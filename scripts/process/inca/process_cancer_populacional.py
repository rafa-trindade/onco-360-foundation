"""INCA - Registro de Câncer de Base Populacional (RCBP) (process).

Fonte estática: o INCA descontinuou o download integral desta base. O
snapshot é trazido manualmente como Parquet pronto em
MANUAL_INCA_DIR/cancer_populacional.parquet
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import MANUAL_INCA_DIR
from scripts.common.publish import publicar_arquivo_pronto

PASTA_BUCKET = "inca"
NOME_ARQUIVO_FINAL = "cancer_populacional.parquet"
ORIGEM = MANUAL_INCA_DIR / "cancer_populacional.parquet"


def main() -> int:
    if not ORIGEM.exists():
        print(f"[ERRO] Snapshot não encontrado: {ORIGEM}. Coloque o arquivo manualmente.")
        return exit_codes.ERRO

    print(f"Publicando arquivo estático {NOME_ARQUIVO_FINAL} no bucket...")
    sucesso = publicar_arquivo_pronto(ORIGEM, PASTA_BUCKET, NOME_ARQUIVO_FINAL)

    if not sucesso:
        return exit_codes.ERRO

    return exit_codes.SUCESSO


if __name__ == "__main__":
    sys.exit(main())