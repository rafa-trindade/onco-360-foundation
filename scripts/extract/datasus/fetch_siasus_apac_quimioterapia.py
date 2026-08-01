"""Extração FTP DATASUS: SIASUS / APAC de Quimioterapia (desde 2008).

Arquivos AQuf aamm.dbc (AQ = APAC de Quimioterapia). Base inteiramente
oncológica. Série a partir de 2008 (implantação da tabela SIGTAP).
"""
from datetime import datetime
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIASUS/200801_/Dados"
OUTPUT_DIR = str(LANDING_DIR / "dbc_siasus_quimioterapia")
PASTA_BUCKET = "datasus_siasus"

ANO_MINIMO = 2008

def regra_aq(nome_arquivo: str) -> bool:
    nome = nome_arquivo.upper()
    if not (nome.startswith("AQ") and nome.endswith(".DBC")):
        return False
    ano_str = nome[4:6]
    if not ano_str.isdigit():
        return False
    return 2000 + int(ano_str) >= ANO_MINIMO

if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_aq, pasta_bucket=PASTA_BUCKET)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)
