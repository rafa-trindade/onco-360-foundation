"""Extração FTP DATASUS: SINAN / Câncer Relacionado ao Trabalho (CANC).

Arquivos CANCBRaa.dbc nas pastas FINAIS (consolidado) e PRELIM (preliminar).
Base única: registra exposição ocupacional a agentes cancerígenos.
"""
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR_FINAIS = "/dissemin/publicos/SINAN/DADOS/FINAIS"
FTP_DIR_PRELIM = "/dissemin/publicos/SINAN/DADOS/PRELIM"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sinan_cancer_trabalho")
PASTA_BUCKET = "datasus_sinan"


def regra_cancn(nome_arquivo: str) -> bool:
    nome = nome_arquivo.upper()
    return nome.startswith("CANC") and nome.endswith(".DBC")


if __name__ == "__main__":
    sucesso_f, novidade_f = sincronizar_ftp(
        FTP_DIR_FINAIS, OUTPUT_DIR, regra_cancn, pasta_bucket=PASTA_BUCKET
    )
    sucesso_p, novidade_p = sincronizar_ftp(
        FTP_DIR_PRELIM, OUTPUT_DIR, regra_cancn, pasta_bucket=PASTA_BUCKET
    )

    if not (sucesso_f and sucesso_p):
        exit(exit_codes.ERRO)
    elif not (novidade_f or novidade_p):
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)
