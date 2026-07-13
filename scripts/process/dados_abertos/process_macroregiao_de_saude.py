"""
Macrorregião e Região de Saúde (process)

Junta o CSV de macrorregião/região de saúde (baixado pelo extract) com a
planilha de geolocalização de municípios (data/landing/macroregiao/
macro_geolocalizacao.xls, fornecida manualmente -- não tem fonte de
download automatizada conhecida) e gera o Parquet final, plano, em
data/raw/raw_macroregiao_de_saude.parquet.
"""
import pandas as pd
from scripts.common.paths import LANDING_DIR, RAW_DIR

def main():
    landing_csv = LANDING_DIR / "macroregiao" / "macroregiao_de_saude_raw.csv"
    geo_path = LANDING_DIR / "macroregiao" / "macro_geolocalizacao.xls"
    parquet_final = RAW_DIR / "raw_macroregiao_de_saude.parquet"

    if not landing_csv.exists():
        print(f"Erro: CSV não encontrado ({landing_csv}). Rode o extract primeiro.")
        return
    if not geo_path.exists():
        print(f"Erro: Planilha de geolocalização não encontrada ({geo_path}). "
              "Ela precisa ser colocada manualmente em data/landing/macroregiao/.")
        return

    print("Lendo CSV e XLS...")
    df = pd.read_csv(landing_csv, sep=";", encoding="utf-8-sig", dtype=str)
    df_geo = pd.read_excel(geo_path, dtype=str)

    print("Ajustando zeros à esquerda no código do município...")
    df["cod_municipio"] = df["cod_municipio"].str.zfill(6)
    df_geo["MUNCOD"] = df_geo["MUNCOD"].str.zfill(6)

    print("Fazendo merge (LEFT JOIN macro -> geo, por código do município)...")
    df_final = df.merge(df_geo, left_on="cod_municipio", right_on="MUNCOD", how="left")

    print(f"Salvando em {parquet_final}...")
    df_final.to_parquet(parquet_final, index=False)
    print(f"✔ Concluído! {len(df_final)} registros.")

if __name__ == "__main__":
    main()