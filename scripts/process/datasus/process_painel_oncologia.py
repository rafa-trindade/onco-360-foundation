"""
Painel de Oncologia (DATASUS) (process)

Converte os .dbc baixados pelo extract em um único Parquet final, plano,
em data/raw/raw_painel_de_oncologia.parquet -- mesmo nome já publicado em
kaggle.com/datasets/rafatrindade/onco-360.
"""
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc
from scripts.common.paths import LANDING_DIR, RAW_DIR

def main():
    dbc_dir = LANDING_DIR / "dbc_painel_oncologia"
    parquet_final = RAW_DIR / "raw_painel_de_oncologia.parquet"

    processar_diretorio_dbc(dbc_dir, parquet_final)

if __name__ == "__main__":
    main()