"""
Painel de Oncologia (DATASUS) - desde 2013

Baixa os arquivos .dbc do FTP público do DATASUS.
"""
from scripts.extract.datasus.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/PAINEL_ONCOLOGIA/DADOS"
OUTPUT_DIR = str(LANDING_DIR / "dbc_painel_oncologia")

def regra_dbc_geral(nome_arquivo: str) -> bool:
    return nome_arquivo.upper().endswith(".DBC")

if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dbc_geral)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)