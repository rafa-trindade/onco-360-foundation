"""Painel de Oncologia (DATASUS) - process.

Procedimentos oncológicos do SUS desde 2013 (diagnóstico, estadiamento,
tratamento). Uma linha por registro. Converte os .dbc da landing, decodifica
os códigos (tratamento, categoria de diagnóstico, estadiamento, sexo, e a
topografia CID-10 com descrição), e publica no bucket (painel_oncologia/),
padrão do projeto. Sem filtro: o painel já é inteiramente oncológico.
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.po.transformar_painel import montar_query_painel

PASTA_BUCKET = "datasus_po"
NOME_ARQUIVO_FINAL = "painel_oncologia.parquet"
DBC_DIR = LANDING_DIR / "dbc_painel_oncologia"


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        query_transformacao=lambda cols: montar_query_painel(cols),
    )


if __name__ == "__main__":
    sys.exit(main())
