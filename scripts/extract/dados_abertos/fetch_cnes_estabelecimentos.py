"""
CNES - Cadastro Nacional de Estabelecimentos de Saúde

Baixa o CSV completo de estabelecimentos de saúde cadastrados no CNES,
publicado no Portal de Dados Abertos do Ministério da Saúde.
"""
from scripts.extract.dados_abertos.base_dados_abertos import LANDING_DIR, baixar_e_extrair_csv
from scripts.common import exit_codes

CSV_DIR = LANDING_DIR / "cnes"

def main() -> bool:
    url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_csv.zip"
    landing_file = CSV_DIR / "cnes_estabelecimentos_raw.csv"

    return baixar_e_extrair_csv(url, landing_file)

if __name__ == "__main__":
    novidade = main()
    exit(exit_codes.SUCESSO if novidade else exit_codes.SEM_NOVIDADE)