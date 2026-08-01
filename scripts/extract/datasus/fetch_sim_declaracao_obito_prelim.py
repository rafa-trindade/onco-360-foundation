"""Extração FTP DATASUS: SIM / Declaração de Óbito Preliminar (CID-10).

Regra de negócio: Sincroniza arquivos não homologados do diretório PRELIM. Vazio entre ciclos de publicação é um estado esperado e tratado como `SEM_NOVIDADE`.
"""
from datetime import datetime

from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIM/PRELIM/DORES"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sim_declaracao_obito_prelim")
PASTA_BUCKET = "datasus_sim"

ANO_MINIMO = 1996


def regra_dobr(nome_arquivo: str) -> bool:
    nome = nome_arquivo.upper()
    if not (nome.startswith("DOBR") and nome.endswith(".DBC")):
        return False
    ano_str = nome[4:8]
    if not ano_str.isdigit():
        return False
    return ANO_MINIMO <= int(ano_str) <= datetime.now().year


if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dobr, pasta_bucket=PASTA_BUCKET)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo preliminar novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)
