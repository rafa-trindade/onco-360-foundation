"""SIASUS - APAC de Medicamentos oncológicos (process).

A base de medicamentos de alto custo (AM) é genérica; este recorte mantém
apenas os registros cujo CID principal é uma neoplasia (capítulo II da CID-10,
C00-D48).
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.siasus.transformar_siasus import montar_query_medicamentos

PASTA_BUCKET = "datasus_siasus"
NOME_ARQUIVO_FINAL = "siasus_medicamentos_oncologicos.parquet"
DBC_DIR = LANDING_DIR / "dbc_siasus_medicamentos"

COLUNA_CID_CANDIDATAS = ["AP_CIDPRI", "AP_CIDSEC", "AP_CIDCAS"]


def _eh_neoplasia(cid: str) -> bool:
    """CID-10 do capítulo II (neoplasias): C00-C97 e D00-D48."""
    if not cid:
        return False
    c = str(cid).strip().upper()
    if not c:
        return False
    letra, resto = c[0], c[1:3]
    if letra == "C":
        return True
    if letra == "D" and resto.isdigit():
        return 0 <= int(resto) <= 48
    return False


def _filtro_oncologico(df):
    coluna = next((c for c in COLUNA_CID_CANDIDATAS if c in df.columns), None)
    if coluna is None:
        return df.iloc[0:0]
    return df[df[coluna].apply(_eh_neoplasia)]


def main() -> int:
    return processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        filtro_chunk=_filtro_oncologico,
        query_transformacao=montar_query_medicamentos,
    )


if __name__ == "__main__":
    sys.exit(main())
