"""Transformação do Painel de Oncologia (DATASUS).
"""

RENOMEAR = {
    "ANO_DIAGN": "ANO_DIAGNOSTICO",
    "ANOMES_DIA": "ANO_MES_DIAGNOSTICO",
    "ANO_TRATAM": "ANO_TRATAMENTO",
    "ANOMES_TRA": "ANO_MES_TRATAMENTO",
    "UF_RESID": "COD_UF_RESIDENCIA",
    "MUN_RESID": "COD_MUNICIPIO_RESIDENCIA",
    "UF_TRATAM": "COD_UF_TRATAMENTO",
    "MUN_TRATAM": "COD_MUNICIPIO_TRATAMENTO",
    "UF_DIAGN": "COD_UF_DIAGNOSTICO",
    "MUN_DIAG": "COD_MUNICIPIO_DIAGNOSTICO",
    "TRATAMENTO": "COD_TRATAMENTO",
    "DIAGNOSTIC": "COD_CATEGORIA_DIAGNOSTICO",
    "IDADE": "IDADE_DIAGNOSTICO",
    "SEXO": "SEXO",
    "ESTADIAM": "COD_ESTADIAMENTO",
    "CNES_DIAG": "COD_CNES_DIAGNOSTICO",
    "CNES_TRAT": "COD_CNES_TRATAMENTO",
    "TEMPO_TRAT": "DIAS_ATE_TRATAMENTO",
    "DIAG_DETH": "TOPOGRAFIA_CID10",
    "DT_DIAG": "DATA_DIAGNOSTICO",
    "DT_TRAT": "DATA_TRATAMENTO",
    "DT_NASC": "DATA_NASCIMENTO",
}

_DESCARTAR = {"CNS_PAC"}

TRATAMENTO = {
    "1": "Cirurgia",
    "2": "Quimioterapia",
    "3": "Radioterapia",
    "4": "Quimioterapia + Radioterapia",
    "5": "Sem informação de tratamento",
}

CATEGORIA_DIAGNOSTICO = {
    "1": "Neoplasias malignas (Lei 12.732/12)",
    "2": "Neoplasias in situ",
    "3": "Neoplasias de comportamento incerto ou desconhecido",
    "4": "C44 e C73",
}

ESTADIAMENTO = {
    "0": "0",
    "1": "I",
    "2": "II",
    "3": "III",
    "4": "IV",
    "5": "Não se aplica",
    "9": "Ignorado",
}

SEXO = {"F": "Feminino", "M": "Masculino"}

_ORDEM = [
    "TOPOGRAFIA_CID10", "TOPOGRAFIA_CID10_DESCRICAO",
    "COD_CATEGORIA_DIAGNOSTICO", "CATEGORIA_DIAGNOSTICO",
    "COD_ESTADIAMENTO", "ESTADIAMENTO",
    "COD_TRATAMENTO", "TRATAMENTO",
    "ANO_DIAGNOSTICO", "ANO_MES_DIAGNOSTICO", "DATA_DIAGNOSTICO",
    "ANO_TRATAMENTO", "ANO_MES_TRATAMENTO", "DATA_TRATAMENTO",
    "DIAS_ATE_TRATAMENTO",
    "IDADE_DIAGNOSTICO", "SEXO", "DATA_NASCIMENTO",
    "COD_MUNICIPIO_RESIDENCIA", "COD_UF_RESIDENCIA",
    "COD_MUNICIPIO_DIAGNOSTICO", "COD_UF_DIAGNOSTICO", "COD_CNES_DIAGNOSTICO",
    "COD_MUNICIPIO_TRATAMENTO", "COD_UF_TRATAMENTO", "COD_CNES_TRATAMENTO",
    "ARQUIVO_ORIGEM",
]

from pathlib import Path
from scripts.common.paths import MANUAL_DATASUS_REF_DIR

REF_CID10 = MANUAL_DATASUS_REF_DIR / "ref_causa_cid10.parquet"


def _case(coluna_origem: str, mapa: dict, coluna_saida: str, tirar_zeros: bool = False) -> str:
    """Monta um CASE SQL que decodifica um código para texto, mantendo o
    código original (trim) quando não há correspondência.

    tirar_zeros: normaliza removendo zeros à esquerda antes de comparar, para
    códigos numéricos que aparecem com preenchimento (ex: DIAGNOSTIC vem '01'
    mas a tabela usa '1')."""
    if tirar_zeros:
        chave = f"nullif(ltrim(trim(base.\"{coluna_origem}\"), '0'), '')"
        chave = f"coalesce({chave}, trim(base.\"{coluna_origem}\"))"
    else:
        chave = f"trim(base.\"{coluna_origem}\")"
    ramos = " ".join(f"WHEN {chave} = '{cod}' THEN '{txt}'" for cod, txt in mapa.items())
    return f'CASE {ramos} ELSE trim(base."{coluna_origem}") END AS "{coluna_saida}"'


def montar_query_painel(cols: list[str]) -> str:
    """Monta a query DuckDB que renomeia, decodifica e ordena o painel.
    Recebe as colunas presentes (nomes técnicos do DBC + ARQUIVO_ORIGEM) e
    devolve o SELECT sobre __ORIGEM__ (placeholder do stream)."""
    presentes = {c.upper() for c in cols}
    seletores = []

    def renomeada(origem, destino):
        if origem in presentes:
            seletores.append(f'trim(base."{origem}") AS "{destino}"')

    def decodificada(origem, mapa, cod_saida, txt_saida, tirar_zeros=False):
        if origem in presentes:
            seletores.append(f'trim(base."{origem}") AS "{cod_saida}"')
            seletores.append(_case(origem, mapa, txt_saida, tirar_zeros))

    tem_topografia = "DIAG_DETH" in presentes
    if tem_topografia:
        seletores.append('trim(base."DIAG_DETH") AS "TOPOGRAFIA_CID10"')
        seletores.append('rcid.DESCRICAO AS "TOPOGRAFIA_CID10_DESCRICAO"')

    decodificada("DIAGNOSTIC", CATEGORIA_DIAGNOSTICO,
                 "COD_CATEGORIA_DIAGNOSTICO", "CATEGORIA_DIAGNOSTICO", tirar_zeros=True)
    decodificada("ESTADIAM", ESTADIAMENTO, "COD_ESTADIAMENTO", "ESTADIAMENTO")
    decodificada("TRATAMENTO", TRATAMENTO, "COD_TRATAMENTO", "TRATAMENTO")

    renomeada("ANO_DIAGN", "ANO_DIAGNOSTICO")
    renomeada("ANOMES_DIA", "ANO_MES_DIAGNOSTICO")
    renomeada("DT_DIAG", "DATA_DIAGNOSTICO")
    renomeada("ANO_TRATAM", "ANO_TRATAMENTO")
    renomeada("ANOMES_TRA", "ANO_MES_TRATAMENTO")
    renomeada("DT_TRAT", "DATA_TRATAMENTO")
    renomeada("TEMPO_TRAT", "DIAS_ATE_TRATAMENTO")

    if "IDADE" in presentes:
        seletores.append(
            'CASE WHEN trim(base."IDADE") = \'999\' THEN NULL '
            'ELSE try_cast(trim(base."IDADE") AS INTEGER) END AS "IDADE_DIAGNOSTICO"'
        )

    if "SEXO" in presentes:
        seletores.append(_case("SEXO", SEXO, "SEXO"))

    renomeada("DT_NASC", "DATA_NASCIMENTO")
    renomeada("MUN_RESID", "COD_MUNICIPIO_RESIDENCIA")
    renomeada("UF_RESID", "COD_UF_RESIDENCIA")
    renomeada("MUN_DIAG", "COD_MUNICIPIO_DIAGNOSTICO")
    renomeada("UF_DIAGN", "COD_UF_DIAGNOSTICO")
    renomeada("CNES_DIAG", "COD_CNES_DIAGNOSTICO")
    renomeada("MUN_TRATAM", "COD_MUNICIPIO_TRATAMENTO")
    renomeada("UF_TRATAM", "COD_UF_TRATAMENTO")
    renomeada("CNES_TRAT", "COD_CNES_TRATAMENTO")

    if "ARQUIVO_ORIGEM" in presentes:
        seletores.append('base."ARQUIVO_ORIGEM" AS "ARQUIVO_ORIGEM"')

    join = ""
    if tem_topografia and REF_CID10.exists():
        join = (f'LEFT JOIN read_parquet(\'{REF_CID10.as_posix()}\') rcid '
                f'ON replace(trim(base."DIAG_DETH"), \'.\', \'\') = rcid.CODIGO')

    return f"SELECT {', '.join(seletores)} FROM __ORIGEM__ base {join}"

