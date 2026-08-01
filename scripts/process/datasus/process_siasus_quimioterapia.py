"""SIASUS - APAC de Quimioterapia (process).

Procedimentos de quimioterapia autorizados no SUS (APAC), com topografia
CID-10, estadiamento, linfonodos, grau histopatológico e esquema terapêutico.
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.siasus.transformar_siasus import montar_query_quimioterapia

PASTA_BUCKET = "datasus_siasus"
NOME_ARQUIVO_FINAL = "siasus_quimioterapia.parquet"
DBC_DIR = LANDING_DIR / "dbc_siasus_quimioterapia"


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        query_transformacao=montar_query_quimioterapia,
    )


if __name__ == "__main__":
    sys.exit(main())
