"""Extração HTTP/ZIP: Macrorregião e Região de Saúde (Dados Abertos).

Idempotência: Validação de novidade baseada em hash de conteúdo contra o manifesto persistido no bucket.
"""
from scripts.extract.dados_abertos.common.base_dados_abertos import LANDING_DIR, sincronizar_csv_zip
from scripts.common import exit_codes

URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbgeral/macroregiao_de_saude_csv.zip"
PASTA_BUCKET = "macroregiao"
CHAVE_FONTE = "macroregiao_de_saude_csv.zip"
CSV_LANDING = LANDING_DIR / "macroregiao" / "macroregiao_de_saude_raw.csv"


def main() -> bool:
    novidade, _ = sincronizar_csv_zip(URL, CSV_LANDING, PASTA_BUCKET, CHAVE_FONTE)
    print("Lembre-se: 'macro_geolocalizacao.xls' precisa estar em MANUAL_DIR/macroregiao/.")
    return novidade


if __name__ == "__main__":
    novidade = main()
    exit(exit_codes.SUCESSO if novidade else exit_codes.SEM_NOVIDADE)
