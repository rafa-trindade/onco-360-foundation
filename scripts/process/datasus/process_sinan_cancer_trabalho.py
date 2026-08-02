"""SINAN - Câncer Relacionado ao Trabalho (process).

Notificações de câncer relacionado ao trabalho (agravo C80), com ocupação,
situação no mercado de trabalho, exposição ocupacional a agentes cancerígenos
(asbesto, sílica, benzeno, radiações, antineoplásicos, etc.) e evolução do
caso.
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.sinan.transformar_sinan import montar_query_sinan

PASTA_BUCKET = "datasus_sinan"
NOME_ARQUIVO_FINAL = "cancer_relacionado_ao_trabalho.parquet"
DBC_DIR = LANDING_DIR / "dbc_sinan_cancer_trabalho"


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        query_transformacao=montar_query_sinan,
    )


if __name__ == "__main__":
    sys.exit(main())
