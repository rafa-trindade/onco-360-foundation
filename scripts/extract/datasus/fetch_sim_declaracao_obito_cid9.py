"""Extração FTP DATASUS: SIM / Declaração de Óbito CID-9 (1979-1995).

Regra de negócio: Arquivos da era CID-9 usam o prefixo 'DORBR' (divergente do 'DOBR' do CID-10).
Parser tolerante: A regra de extração lida com a inconsistência histórica da nomenclatura, suportando anos com 2 ou 4 dígitos.
"""
from scripts.extract.datasus.common.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIM/CID9/DORES"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sim_declaracao_obito_cid9")
PASTA_BUCKET = "datasus_sim"

ANO_MINIMO = 1979
ANO_MAXIMO = 1995

PREFIXO = "DORBR"

def regra_dobr_cid9(nome_arquivo: str) -> bool:
    nome = nome_arquivo.upper()
    if not (nome.startswith(PREFIXO) and nome.endswith(".DBC")):
        return False

    ano_str = nome[len(PREFIXO):-4]
    if not ano_str.isdigit():
        return False

    ano_int = int(ano_str)
    if len(ano_str) == 2:
        ano_completo = 1900 + ano_int if ano_int >= 79 else 2000 + ano_int
    else:
        ano_completo = ano_int

    return ANO_MINIMO <= ano_completo <= ANO_MAXIMO

if __name__ == "__main__":
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dobr_cid9, pasta_bucket=PASTA_BUCKET)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)