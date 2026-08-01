"""Extração FTP DATASUS: SIASUS / APAC de Medicamentos (desde 2008).

Arquivos AMuf aamm.dbc (AM = APAC de Medicamentos). Base genérica de alto
custo; o recorte oncológico é feito no process, filtrando o CID principal
(capítulo II da CID-10: neoplasias, C00-D48).
"""
from datetime import datetime
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIASUS/200801_/Dados"
OUTPUT_DIR = str(LANDING_DIR / "dbc_siasus_medicamentos")
PASTA_BUCKET = "datasus_siasus"

ANO_MINIMO = 2008

def regra_am(nome_arquivo: str) -> bool:
    nome = nome_arquivo.upper()
    if not (nome.startswith("AM") and nome.endswith(".DBC")):
        return False
    ano_str = nome[4:6]
    if not ano_str.isdigit():
        return False
    return 2000 + int(ano_str) >= ANO_MINIMO

if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_am, pasta_bucket=PASTA_BUCKET)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)
