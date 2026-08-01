"""SIASUS - APAC de Radioterapia (process).

Procedimentos de radioterapia autorizados no SUS (APAC), com topografia
CID-10, estadiamento, finalidade (radical/adjuvante/paliativa) e campos de
tratamento. Base inteiramente oncológica (sem filtro).
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.siasus.transformar_siasus import montar_query_radioterapia

PASTA_BUCKET = "datasus_siasus"
NOME_ARQUIVO_FINAL = "siasus_radioterapia.parquet"
DBC_DIR = LANDING_DIR / "dbc_siasus_radioterapia"


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        query_transformacao=montar_query_radioterapia,
    )


if __name__ == "__main__":
    sys.exit(main())
