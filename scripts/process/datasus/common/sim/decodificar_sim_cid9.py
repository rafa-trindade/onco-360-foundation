"""Decodificação dos campos categóricos do SIM na era CID-9 (1979-1995).

Os domínios e nomes de coluna do CID-9 diferem do CID-10 (ex: ESTCIVIL vs
ESTCIV; LOCOCOR tem ordem distinta; TIPOPARTO usa Espontâneo/Operatório).
Fonte: MORT98.HLP (estrutura das bases de mortalidade 1979-1998, DATASUS).

Reaproveita o gerador de expressões e o tratamento de idade do módulo
CID-10, mudando apenas o dicionário de domínios e a coluna de idade.
"""
from scripts.process.datasus.common.sim.decodificar_sim import (
    montar_expr_decodificacao, montar_expr_idade_anos, _sql_literal, ROTULO_IGNORADO,
)

DOMINIOS_CID9: dict[str, dict[str, str]] = {
    "TIPOBITO": {"1": "Fetal", "2": "Não fetal"},
    "SEXO": {"1": "Masculino", "2": "Feminino"},
    "ESTCIVIL": {"1": "Solteiro", "2": "Casado", "3": "Viúvo",
                 "4": "Separado judicialmente/divorciado", "5": "União estável"},
    "INSTRUCAO": {"1": "Nenhuma", "2": "Primeiro grau",
                  "3": "Segundo grau", "4": "Superior"},
    "LOCOCOR": {"1": "Hospital", "2": "Via pública",
                "3": "Domicílio", "4": "Outro"},
    "TIPOGRAV": {"1": "Única", "2": "Dupla", "3": "Tríplice", "4": "Mais de 3"},
    "TIPOPARTO": {"1": "Espontâneo", "2": "Operatório", "3": "Fórceps", "4": "Outro"},
    "ASSISTMED": {"1": "Com assistência médica", "2": "Sem assistência médica"},
    "ATESTANTE": {"1": "Sim, atendeu ao falecido", "2": "Substituto",
                  "3": "Instituto Médico Legal", "4": "Serviço de Verificação de Óbitos",
                  "5": "Outro"},
    "EXAME": {"1": "Sim", "2": "Não"},
    "CIRURGIA": {"1": "Sim", "2": "Não"},
    "NECROPSIA": {"1": "Sim", "2": "Não"},
    "ACIDTRAB": {"1": "Sim", "2": "Não"},
    "TIPOVIOL": {"1": "Homicídio", "2": "Suicídio", "3": "Acidente",
                 "4": "Outros tipos de violência"},
    "TIPOACID": {"1": "Atropelamento", "2": "Demais acidentes de trânsito",
                 "3": "Queda", "4": "Afogamento", "5": "Outros tipos de acidente"},
    "FONTINFO": {"1": "Boletim de ocorrência", "2": "Hospital", "3": "Outro"},
    "LOCACID": {"1": "Via pública", "2": "Domicílio", "3": "Outro",
                "4": "Local de trabalho"},
}

COLUNA_MUNICIPIO_CID9 = "MUNIRES"
COLUNA_IDADE_CID9 = "IDADE"

# Campos que existem no layout do CID-9 mas nunca foram coletados nesta era
# (0% preenchido em 1979-1995): raça/cor e etnia só entraram no SIM em 1996.
# DATANASC removida do CID-9: 80% nula e IDADE_ANOS (100%) já cobre a idade.
_DESCARTE_CID9 = {"RACACOR", "ETNIA", "DATANASC"}


def _filtrar_cid9(colunas: list[str]) -> list[str]:
    return [c for c in colunas if c.upper() not in _DESCARTE_CID9]


def montar_query_transformacao_cid9(colunas_presentes: list[str], renomear: bool = True) -> str:
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    expr_por_coluna = {c: montar_expr_decodificacao(c, DOMINIOS_CID9[c])
                       for c in DOMINIOS_CID9 if c in colunas_presentes}

    colunas_finais = list(colunas_presentes)

    if COLUNA_IDADE_CID9 in colunas_presentes:
        expr_por_coluna["IDADE_ANOS"] = montar_expr_idade_anos()
        colunas_finais.append("IDADE_ANOS")

    if "DATAOBITO" in colunas_presentes:
        expr_por_coluna["ANO_OBITO"] = montar_expr_ano_obito_cid9("DATAOBITO")
        colunas_finais.append("ANO_OBITO")

    if COLUNA_MUNICIPIO_CID9 in colunas_presentes:
        col = COLUNA_MUNICIPIO_CID9
        expr_por_coluna["CO_IBGE_RESIDENCIA"] = (
            f"CASE WHEN length(trim(CAST({col} AS VARCHAR))) >= 7 "
            f"THEN substr(trim(CAST({col} AS VARCHAR)), 1, 6) "
            f"ELSE nullif(trim(CAST({col} AS VARCHAR)), '') END AS CO_IBGE_RESIDENCIA"
        )
        colunas_finais.append("CO_IBGE_RESIDENCIA")

    ordem = ordenar_colunas(_filtrar_cid9(colunas_finais))

    def _seletor(c):
        alvo = nome_final(c) if renomear else c.upper()
        expr = expr_por_coluna.get(c)
        if expr is not None:
            base_expr = expr.rsplit(" AS ", 1)[0]
            return f'{base_expr} AS "{alvo}"'
        return f'"{c}" AS "{alvo}"'

    seletores = [_seletor(c) for c in ordem]
    return f"SELECT {', '.join(seletores)} FROM __ORIGEM__"


def montar_query_com_sinonimos_cid9(colunas_presentes: list[str], sinonimos_uri: str) -> str:
    """Como montar_query_transformacao_cid9, mas adiciona cod_municipio_atual
    resolvido pelo de-para de sinônimos do CADMUN (preserva CO_IBGE_RESIDENCIA
    original). Só faz efeito se MUNIRES estiver presente."""
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    if COLUNA_MUNICIPIO_CID9 not in colunas_presentes:
        return montar_query_transformacao_cid9(colunas_presentes)

    base = montar_query_transformacao_cid9(colunas_presentes, renomear=False)

    colunas_finais = list(colunas_presentes)
    if COLUNA_IDADE_CID9 in colunas_presentes:
        colunas_finais.append("IDADE_ANOS")
    if "DATAOBITO" in colunas_presentes:
        colunas_finais.append("ANO_OBITO")
    colunas_finais += ["CO_IBGE_RESIDENCIA", "COD_MUNICIPIO_ATUAL"]
    ordem = ordenar_colunas(_filtrar_cid9(colunas_finais))

    seletores = []
    for c in ordem:
        if c == "COD_MUNICIPIO_ATUAL":
            seletores.append(
                f'COALESCE(sin.COD_MUNICIPIO_ATUAL, base."CO_IBGE_RESIDENCIA") AS "{nome_final(c)}"')
        else:
            seletores.append(f'base."{c.upper()}" AS "{nome_final(c)}"')

    return (
        f"SELECT {', '.join(seletores)} "
        f"FROM ({base}) base "
        f"LEFT JOIN read_parquet('{sinonimos_uri}') sin "
        'ON base."CO_IBGE_RESIDENCIA" = sin.COD_MUNICIPIO_ANTIGO'
    )


def ordem_colunas_finais_cid9(colunas_presentes: list[str], com_sinonimos: bool) -> list[str]:
    from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
    from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final

    colunas_finais = list(colunas_presentes)
    if COLUNA_IDADE_CID9 in colunas_presentes:
        colunas_finais.append("IDADE_ANOS")
    if "DATAOBITO" in colunas_presentes:
        colunas_finais.append("ANO_OBITO")
    if COLUNA_MUNICIPIO_CID9 in colunas_presentes:
        colunas_finais.append("CO_IBGE_RESIDENCIA")
        if com_sinonimos:
            colunas_finais.append("COD_MUNICIPIO_ATUAL")
    ordem = ordenar_colunas(_filtrar_cid9(colunas_finais))
    return [nome_final(c) for c in ordem]


def montar_query_sim_cid9(colunas_presentes: list[str], sinonimos_uri: str | None) -> str:
    """Orquestra a query completa do CID-9: transformação, sinônimos e
    descrições de código (causa CID-9, ocupação, naturalidade)."""
    from scripts.process.datasus.common.sim.descricao_codigos_sim import montar_descricoes, REF_CID9

    if sinonimos_uri:
        base = montar_query_com_sinonimos_cid9(colunas_presentes, sinonimos_uri)
    else:
        base = montar_query_transformacao_cid9(colunas_presentes)

    ordem = ordem_colunas_finais_cid9(colunas_presentes, com_sinonimos=bool(sinonimos_uri))
    return montar_descricoes(base, ordem, REF_CID9, tem_ocupacao=True, tem_naturalidade=True,
                             causa_por_prefixo3=True)


def montar_expr_ano_obito_cid9(coluna_data: str = "DATAOBITO") -> str:
    """ANO_OBITO numérico a partir de DATAOBITO no formato AAMMDD (CID-9):
    ano são os 2 primeiros dígitos + 1900 (era 1979-1995). Registros só com
    ano (2 díg) também resolvem; parciais/vazios viram NULL."""
    d = f"trim(CAST({coluna_data} AS VARCHAR))"
    return (
        f"CASE WHEN length({d}) >= 2 AND substr({d}, 1, 2) ~ '^[0-9]{{2}}$' "
        f"THEN TRY_CAST(substr({d}, 1, 2) AS INTEGER) + 1900 "
        f"ELSE NULL END AS ANO_OBITO"
    )
