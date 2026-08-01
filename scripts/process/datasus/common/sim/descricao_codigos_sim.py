"""Descrição de códigos do SIM a partir das tabelas de referência do DATASUS.

Regra do projeto: sempre que houver tabela de-para para um código, agregar a
descrição legível. Aqui:
  - CAUSA_BASICA: coluna de código + coluna separada CAUSA_BASICA_DESCRICAO
    (o código CID é chave de agrupamento; a descrição é para leitura).
  - OCUPACAO: uma coluna no formato "codigo - texto".
  - NATURALIDADE: resolvida para texto (UF de nascimento se brasileiro -
    código inicia em 8 seguido do código da UF; senão, país). O código bruto
    condicional não tem uso analítico e não é mantido.

As tabelas de referência (parquets) são insumos manuais em
MANUAL_DATASUS_REF_DIR, gerados das DBFs oficiais (CID10, CID9, TABOCUP,
TABPAIS, TABUF). Os JOINs são montados como camada SQL externa sobre a
query já transformada, lendo os parquets via read_parquet.

Cada referência tem colunas CODIGO e DESCRICAO (UF também tem SIGLA_UF).
"""
from scripts.common.paths import MANUAL_DATASUS_REF_DIR

REF_CID10 = MANUAL_DATASUS_REF_DIR / "ref_causa_cid10.parquet"
REF_CID9 = MANUAL_DATASUS_REF_DIR / "ref_causa_cid9.parquet"
REF_OCUPACAO = MANUAL_DATASUS_REF_DIR / "ref_ocupacao.parquet"
REF_PAIS = MANUAL_DATASUS_REF_DIR / "ref_pais.parquet"
REF_UF = MANUAL_DATASUS_REF_DIR / "ref_uf.parquet"


def _existe(caminho) -> bool:
    return caminho.exists()


def montar_descricoes(query_base: str, colunas_ordem: list[str], coluna_causa_ref,
                      tem_ocupacao: bool, tem_naturalidade: bool,
                      causa_por_prefixo3: bool = False) -> str:
    """Embrulha query_base (que já expõe os nomes finais legíveis, na ordem
    colunas_ordem) com JOINs de descrição.

    CAUSA_BASICA ganha uma coluna irmã CAUSA_BASICA_DESCRICAO logo ao lado.
    OCUPACAO e NATURALIDADE são SUBSTITUÍDAS pelo texto. Referências ausentes
    são toleradas (mantém só o código).

    causa_por_prefixo3: no CID-9 a causa gravada tem 4 dígitos (categoria de
    3 + subcategoria), mas a tabela de referência é por categoria de 3. Nesse
    caso o JOIN casa os 3 primeiros dígitos da causa."""
    joins = []
    # expr por nome de coluna de saída (quando difere do simples base."COL")
    expr_saida = {}
    novas_apos = {}  # coluna_ancora -> lista de (nome_novo, expr)

    if coluna_causa_ref and _existe(coluna_causa_ref) and "CAUSA_BASICA" in colunas_ordem:
        if causa_por_prefixo3:
            chave_causa = 'substr(base."CAUSA_BASICA", 1, 3)'
        else:
            # remove eventual ponto (C50.9 -> C509) para casar com a referência
            chave_causa = 'replace(base."CAUSA_BASICA", \'.\', \'\')'
        joins.append(
            f'LEFT JOIN read_parquet(\'{coluna_causa_ref.as_posix()}\') rcausa '
            f'ON {chave_causa} = rcausa.CODIGO'
        )
        novas_apos.setdefault("CAUSA_BASICA", []).append(
            ('CAUSA_BASICA_DESCRICAO', 'rcausa.DESCRICAO AS "CAUSA_BASICA_DESCRICAO"'))

    if tem_ocupacao and _existe(REF_OCUPACAO) and "OCUPACAO" in colunas_ordem:
        joins.append(
            f'LEFT JOIN read_parquet(\'{REF_OCUPACAO.as_posix()}\') rocup '
            f'ON base."OCUPACAO" = rocup.CODIGO'
        )
        expr_saida["OCUPACAO"] = (
            'CASE WHEN rocup.DESCRICAO IS NOT NULL '
            'THEN base."OCUPACAO" || \' - \' || rocup.DESCRICAO '
            'ELSE base."OCUPACAO" END AS "OCUPACAO"'
        )

    if tem_naturalidade and _existe(REF_PAIS) and _existe(REF_UF) and "NATURALIDADE" in colunas_ordem:
        joins.append(
            f'LEFT JOIN read_parquet(\'{REF_UF.as_posix()}\') ruf '
            f'ON substr(base."NATURALIDADE", 2, 2) = ruf.CODIGO'
        )
        joins.append(
            f'LEFT JOIN read_parquet(\'{REF_PAIS.as_posix()}\') rpais '
            f'ON base."NATURALIDADE" = rpais.CODIGO'
        )
        expr_saida["NATURALIDADE"] = (
            'CASE WHEN substr(base."NATURALIDADE", 1, 1) = \'8\' THEN ruf.DESCRICAO '
            'ELSE rpais.DESCRICAO END AS "NATURALIDADE"'
        )

    if not joins:
        return query_base

    seletores = []
    for col in colunas_ordem:
        seletores.append(expr_saida.get(col, f'base."{col}"'))
        for nome_novo, expr in novas_apos.get(col, []):
            seletores.append(expr)

    return (
        f"SELECT {', '.join(seletores)} "
        f"FROM ({query_base}) base "
        + " ".join(joins)
    )
