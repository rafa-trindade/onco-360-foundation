"""
SIM - Declaração de Óbito (DATASUS) - Dados Consolidados, CID-9 (1979-1995)

Baixa os arquivos .dbc do FTP público do DATASUS, prefixo DORBR (ex:
DORBR95.dbc) -- diferente do prefixo DOBR usado na era CID-10 (ex:
DOBR1996.dbc). A era CID-9 do SIM tem nomes de arquivo com ano de 2 OU 4
dígitos dependendo do ano -- a regra abaixo lida com os dois formatos.
"""
from scripts.extract.datasus.base_ftp import sincronizar_ftp
from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

FTP_DIR = "/dissemin/publicos/SIM/CID9/DORES"
OUTPUT_DIR = str(LANDING_DIR / "dbc_sim_declaracao_obito_cid9")

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
    sucesso, novidade = sincronizar_ftp(FTP_DIR, OUTPUT_DIR, regra_dobr_cid9)

    if not sucesso:
        exit(exit_codes.ERRO)
    elif not novidade:
        print("[INFO] Nenhum arquivo novo desde a última execução.")
        exit(exit_codes.SEM_NOVIDADE)
    else:
        exit(exit_codes.SUCESSO)