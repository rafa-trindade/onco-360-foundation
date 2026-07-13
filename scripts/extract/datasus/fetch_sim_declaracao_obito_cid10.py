"""
SIM - Declaração de Óbito (DATASUS) - Dados Consolidados, CID-10, desde 1996

Baixa os arquivos .dbc do FTP público do DATASUS (arquivos nacionais
consolidados por ano, prefixo DOBR). 1996 é o início da era CID-10 no
SIM (antes disso, ver fetch_sim_declaracao_obito_cid9.py).
"""
from datetime import datetime
from scripts.extract.datasus.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIM/CID10/DORES"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sim_declaracao_obito_cid10")

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
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dobr)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)