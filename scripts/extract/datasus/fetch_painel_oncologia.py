"""Extração FTP DATASUS: Painel de Oncologia (Desde 2013).

Sincronização incremental de arquivos .DBC contendo registros de diagnóstico e tratamento oncológico no SUS.
"""
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/PAINEL_ONCOLOGIA/DADOS"
OUTPUT_DIR = str(LANDING_DIR / "dbc_painel_oncologia")
PASTA_BUCKET = "datasus_po"

def regra_dbc_geral(nome_arquivo: str) -> bool:
    return nome_arquivo.upper().endswith(".DBC")

if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dbc_geral, pasta_bucket=PASTA_BUCKET)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)