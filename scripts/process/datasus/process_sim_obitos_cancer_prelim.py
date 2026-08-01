"""SIM - Óbitos por Câncer, CID-10 Preliminar (process).

Mesmo filtro do consolidado (CAUSABAS C00-C97), aplicado aos dados ainda
não homologados. Publica datasus_sim/obitos_cancer_prelim.parquet. Pode
legitimamente ficar sem .dbc entre ciclos de publicação do DATASUS --
nesse caso não há nada a processar e o resumo não é tocado.
"""
import sys

import pandas as pd

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.common.bucket_sync import already_in_bucket
from scripts.common.publish import dataframe_para_parquet
from scripts.process.datasus.common.base_process_dbc_stream import (
    processar_fonte_ftp_incremental, listar_dbc_deduplicados,
)
from scripts.process.datasus.common.sim.filtros_cancer import filtro_chunk_cancer_cid10
from scripts.process.datasus.common.sim.decodificar_sim import (
    montar_query_sim_cid10, baixar_sinonimos_municipio,
)
from scripts.process.datasus.common.sim.colunas_sim import COLUNAS_DECLARACAO_OBITO
from scripts.process.datasus.common.sim.ordenar_colunas_sim import ordenar_colunas
from scripts.process.datasus.common.sim.renomear_colunas_sim import nome_final
from scripts.process.datasus.common.sim.resumo_sim_stream import atualizar_resumo_anual
from scripts.process.datasus.common.sim.resumo_cancer import extrair_ano_cid10

PASTA_BUCKET = "datasus_sim"
NOME_ARQUIVO_FINAL = "obitos_cancer_prelim.parquet"
FONTE_RESUMO = "PRELIM"
COLUNA_MUNICIPIO = "CODMUNRES"

DBC_DIR = LANDING_DIR / "dbc_sim_declaracao_obito_prelim"


def _publicar_vazio_se_ausente() -> int:
    """Preliminar pode ficar sem .dbc entre ciclos do DATASUS. Se o arquivo
    ainda não existe no bucket, publica um Parquet vazio (schema padrão)
    para o consumidor distinguir 'sem dado novo agora' de 'nunca publicado'."""
    if already_in_bucket(f"{PASTA_BUCKET}/{NOME_ARQUIVO_FINAL}"):
        print("[INFO] Preliminar sem .dbc novos -- arquivo já existe no bucket, mantido.")
        return exit_codes.SEM_NOVIDADE
    colunas_brutas = (COLUNAS_DECLARACAO_OBITO
                      + ["IDADE_ANOS", "ARQUIVO_ORIGEM", "CO_IBGE_RESIDENCIA", "COD_MUNICIPIO_ATUAL"])
    ordenadas = ordenar_colunas([c.upper() if c != "ARQUIVO_ORIGEM" else c for c in colunas_brutas])
    colunas = [nome_final(c) for c in ordenadas]
    if "CAUSA_BASICA" in colunas:
        colunas.insert(colunas.index("CAUSA_BASICA") + 1, "CAUSA_BASICA_DESCRICAO")
    df_vazio = pd.DataFrame({c: pd.Series(dtype="string") for c in colunas})
    ok = dataframe_para_parquet(df_vazio, PASTA_BUCKET, NOME_ARQUIVO_FINAL)
    return exit_codes.SUCESSO if ok else exit_codes.ERRO


def main() -> int:
    sem_dbc = (not DBC_DIR.exists()) or (not listar_dbc_deduplicados(DBC_DIR))
    if sem_dbc:
        return _publicar_vazio_se_ausente()

    totais = {}
    sinonimos = baixar_sinonimos_municipio()

    def transformacao(cols):
        tem_idade = "IDADE" in cols
        return montar_query_sim_cid10(cols, COLUNA_MUNICIPIO, tem_idade, sinonimos)

    codigo = processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        filtro_chunk=filtro_chunk_cancer_cid10,
        query_transformacao=transformacao,
        contador_totais=totais,
    )

    if codigo == exit_codes.SUCESSO and totais:
        atualizar_resumo_anual(totais, FONTE_RESUMO, extrair_ano_cid10, NOME_ARQUIVO_FINAL)

    return codigo


if __name__ == "__main__":
    sys.exit(main())
