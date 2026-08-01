"""Monta as queries DuckDB de transformação das APAC do SIASUS.
"""
from scripts.process.datasus.common.siasus.comum_siasus import (
    RENOMEAR_COMUM, REF_CID10, MAPA_SEXO, MAPA_RACA_COR, MAPA_SIM_NAO,
    MAPA_LINFONODOS, MAPA_ESTADIAMENTO, MAPA_TIPO_APAC, MAPA_FINALIDADE_RADIO,
)


def _case(coluna_origem: str, mapa: dict, coluna_saida: str) -> str:
    ramos = " ".join(
        f"WHEN trim(base.\"{coluna_origem}\") = '{cod}' THEN '{txt}'"
        for cod, txt in mapa.items()
    )
    return f'CASE {ramos} ELSE trim(base."{coluna_origem}") END AS "{coluna_saida}"'


def _seletores_comuns(presentes: set) -> list[str]:
    """Renomeia o bloco AP_* comum e decodifica sexo, raça/cor e tipos."""
    sel = []

    def renomeada(origem, destino):
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{destino}"')

    for origem, destino in RENOMEAR_COMUM.items():
        if origem in ("AP_SEXO", "AP_RACACOR", "AP_TPAPAC"):
            continue  # decodificados abaixo
        renomeada(origem, destino)

    if "AP_SEXO" in presentes:
        sel.append(_case("AP_SEXO", MAPA_SEXO, "SEXO"))
    if "AP_RACACOR" in presentes:
        sel.append(f'trim(base."AP_RACACOR") AS "COD_RACA_COR"')
        sel.append(_case("AP_RACACOR", MAPA_RACA_COR, "RACA_COR"))
    if "AP_TPAPAC" in presentes:
        sel.append(f'trim(base."AP_TPAPAC") AS "COD_TIPO_APAC"')
        sel.append(_case("AP_TPAPAC", MAPA_TIPO_APAC, "TIPO_APAC"))

    return sel


def _topografia(prefixo: str, presentes: set, sel: list[str]) -> bool:
    """Adiciona a topografia CID-10 (código sempre; descrição só quando a
    tabela de referência existe, pois depende do JOIN). Devolve True se o JOIN
    deve ser montado."""
    coluna = f"{prefixo}_CID10"
    if coluna not in presentes:
        return False
    sel.append(f'trim(base."{coluna}") AS "TOPOGRAFIA_CID10"')
    if REF_CID10.exists():
        sel.append('rcid.DESCRICAO AS "TOPOGRAFIA_CID10_DESCRICAO"')
        return True
    return False


def _bloco_oncologico(prefixo: str, presentes: set, sel: list[str]):
    """Campos clínicos comuns a AQ e AR: estadiamento, linfonodos, grau
    histopatológico, tratamentos anteriores, continuidade."""
    def renomeada(origem, destino):
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{destino}"')

    def decodificada(origem, mapa, cod_saida, txt_saida):
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{cod_saida}"')
            sel.append(_case(origem, mapa, txt_saida))

    decodificada(f"{prefixo}_ESTADI", MAPA_ESTADIAMENTO, "COD_ESTADIAMENTO", "ESTADIAMENTO")
    decodificada(f"{prefixo}_LINFIN", MAPA_LINFONODOS, "COD_LINFONODOS_INVADIDOS", "LINFONODOS_INVADIDOS")
    renomeada(f"{prefixo}_GRAHIS", "GRAU_HISTOPATOLOGICO")
    decodificada(f"{prefixo}_TRANTE", MAPA_SIM_NAO, "COD_TRATAMENTO_ANTERIOR", "TEVE_TRATAMENTO_ANTERIOR")
    renomeada(f"{prefixo}_DTIDEN", "DATA_IDENTIFICACAO_PATOLOGICA")
    decodificada(f"{prefixo}_CONTTR", MAPA_SIM_NAO, "COD_CONTINUIDADE", "CONTINUIDADE_TRATAMENTO")
    renomeada(f"{prefixo}_DTINTR", "DATA_INICIO_TRATAMENTO")


def montar_query_quimioterapia(cols: list[str]) -> str:
    presentes = {c.upper() for c in cols}
    sel = _seletores_comuns(presentes)
    tem_topo = _topografia("AQ", presentes, sel)
    _bloco_oncologico("AQ", presentes, sel)

    def renomeada(origem, destino):
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{destino}"')

    renomeada("AQ_ESQU_P1", "ESQUEMA_TERAPEUTICO_INICIO")
    renomeada("AQ_ESQU_P2", "ESQUEMA_TERAPEUTICO_FIM")
    renomeada("AQ_TOTMPL", "TOTAL_MESES_PLANEJADOS")
    renomeada("AQ_TOTMAU", "TOTAL_MESES_AUTORIZADOS")
    sel.append('base."ARQUIVO_ORIGEM" AS "ARQUIVO_ORIGEM"')

    join = _montar_join_topografia("AQ_CID10", tem_topo)
    return f"SELECT {', '.join(sel)} FROM __ORIGEM__ base {join}"


def montar_query_radioterapia(cols: list[str]) -> str:
    presentes = {c.upper() for c in cols}
    sel = _seletores_comuns(presentes)
    tem_topo = _topografia("AR", presentes, sel)
    _bloco_oncologico("AR", presentes, sel)

    if "AR_FINALI" in presentes:
        sel.append('trim(base."AR_FINALI") AS "COD_FINALIDADE"')
        sel.append(_case("AR_FINALI", MAPA_FINALIDADE_RADIO, "FINALIDADE_RADIOTERAPIA"))
    sel.append('base."ARQUIVO_ORIGEM" AS "ARQUIVO_ORIGEM"')

    join = _montar_join_topografia("AR_CID10", tem_topo)
    return f"SELECT {', '.join(sel)} FROM __ORIGEM__ base {join}"


def montar_query_medicamentos(cols: list[str]) -> str:
    presentes = {c.upper() for c in cols}
    sel = _seletores_comuns(presentes)

    def renomeada(origem, destino):
        if origem in presentes:
            sel.append(f'trim(base."{origem}") AS "{destino}"')

    renomeada("AM_PESO", "PESO_KG")
    renomeada("AM_ALTURA", "ALTURA_CM")
    if "AM_GESTANT" in presentes:
        sel.append(_case("AM_GESTANT", MAPA_SIM_NAO, "GESTANTE"))
    sel.append('base."ARQUIVO_ORIGEM" AS "ARQUIVO_ORIGEM"')

    # AM não tem CID10 topográfico próprio; descreve pelo CID principal.
    tem_join = "AP_CIDPRI" in presentes and REF_CID10.exists()
    if tem_join:
        sel.insert(0, 'rcid.DESCRICAO AS "CID_PRINCIPAL_DESCRICAO"')
    join = _montar_join_topografia("AP_CIDPRI", tem_join)
    return f"SELECT {', '.join(sel)} FROM __ORIGEM__ base {join}"


def _montar_join_topografia(coluna_cid: str, tem: bool) -> str:
    if not tem or not REF_CID10.exists():
        return ""
    return (f'LEFT JOIN read_parquet(\'{REF_CID10.as_posix()}\') rcid '
            f'ON replace(trim(base."{coluna_cid}"), \'.\', \'\') = rcid.CODIGO')
