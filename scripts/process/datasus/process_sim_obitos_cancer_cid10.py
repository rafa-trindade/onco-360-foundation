"""SIM - Óbitos por Câncer, CID-10 Consolidado (1996-atual) (process).

Filtra os óbitos por neoplasia maligna (CAUSABAS C00-C97) direto dos .dbc
da landing, publica em datasus_sim/obitos_cancer_cid10.parquet (com
CO_IBGE_RESIDENCIA normalizado) e atualiza o resumo anual compartilhado.

Idempotência: o parquet publicado é mesclado por ARQUIVO_ORIGEM (ano
revisado substitui a versão anterior) e o manifesto da pasta registra os
.dbc já incorporados. Um ano que antes existia como preliminar tem sua
linha de resumo substituída pela do consolidado.
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.sim.filtros_cancer import filtro_chunk_cancer_cid10
from scripts.process.datasus.common.sim.decodificar_sim import (
    montar_query_sim_cid10, baixar_sinonimos_municipio,
)
from scripts.process.datasus.common.sim.resumo_sim_stream import atualizar_resumo_anual
from scripts.process.datasus.common.sim.resumo_cancer import extrair_ano_cid10

PASTA_BUCKET = "datasus_sim"
NOME_ARQUIVO_FINAL = "obitos_cancer_cid10.parquet"
FONTE_RESUMO = "CID10"
COLUNA_MUNICIPIO = "CODMUNRES"

DBC_DIR = LANDING_DIR / "dbc_sim_declaracao_obito_cid10"


def main() -> int:
    totais = {}
    sinonimos = baixar_sinonimos_municipio()
    if sinonimos is None:
        print("[AVISO] geo_sinonimos_municipio ausente -- publicando sem COD_MUNICIPIO_ATUAL. "
              "Processe a fonte macroregiao antes para resolver códigos municipais extintos.")

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
