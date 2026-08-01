"""Extração FTP DATASUS: SIM / Declaração de Óbito CID-10 (Desde 1996).

Regra de negócio: Extrai os arquivos nacionais consolidados anualmente (prefixo 'DOBR').
Marco temporal: 1996 define o início da série histórica restrita à codificação CID-10 no SIM.
"""
from datetime import datetime
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIM/CID10/DORES"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sim_declaracao_obito_cid10")
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
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)