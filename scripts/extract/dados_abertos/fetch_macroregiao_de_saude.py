"""
Macrorregião e Região de Saúde

Baixa a lista de municípios com informações de macrorregião e região de
saúde, publicada pelo Ministério da Saúde no Portal de Dados Abertos.
"""
from scripts.extract.dados_abertos.base_dados_abertos import LANDING_DIR, baixar_e_extrair_csv
from scripts.common import exit_codes

CSV_DIR = LANDING_DIR / "macroregiao"

def main() -> bool:
    url = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbgeral/macroregiao_de_saude_csv.zip"
    landing_file = CSV_DIR / "macroregiao_de_saude_raw.csv"

    novidade = baixar_e_extrair_csv(url, landing_file)
    print("Lembre-se de garantir que o arquivo 'macro_geolocalizacao.xls' está na pasta Landing (data/landing/macroregiao/).")
    return novidade

if __name__ == "__main__":
    novidade = main()
    exit(exit_codes.SUCESSO if novidade else exit_codes.SEM_NOVIDADE)