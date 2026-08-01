"""Processamento de referência geográfica e municipal (`macroregiao`).

Regras arquiteturais e de engenharia:
- Consolidação de três fontes: CSV de saúde (extract), planilha de geolocalização e base CADMUN (manuais).
- Padronização rigorosa: Aplicação mandatório de zero-fill à esquerda (`zfill=6`) antes de cada join para evitar perdas cadastrais.
- Geração de subprodutos: Produz simultaneamente a malha unificada (`geo_macroregiao.parquet`) e o mapa de sinônimos históricos (`geo_sinonimos_municipio.parquet`).
"""
import hashlib
import sys

import pandas as pd

from scripts.common.paths import LANDING_DIR, MANUAL_MACROREGIAO_DIR
from scripts.common import exit_codes
from scripts.common.publish import dataframe_para_parquet, conectar_duckdb
from scripts.common.bucket_sync import carregar_assinaturas, salvar_assinaturas
from scripts.process.dados_abertos.common.macroregiao.cadmun import montar_mapa_sinonimos

PASTA_BUCKET = "macroregiao"
NOME_ARQUIVO_FINAL = "geo_macroregiao.parquet"
NOME_SINONIMOS = "sinonimos_municipio.parquet"
CHAVE_FONTE = "macroregiao_de_saude_csv.zip"

CSV_LANDING = LANDING_DIR / "macroregiao" / "macroregiao_de_saude_raw.csv"
XLS_GEO = MANUAL_MACROREGIAO_DIR / "macro_geolocalizacao.xls"
CADMUN_PARQUET = MANUAL_MACROREGIAO_DIR / "cadmun.parquet"

_RENOMEAR_GEO = {
    "cod_municipio": "COD_MUNICIPIO",
    "NO_MUNICIPIO": "NOME_MUNICIPIO",
    "AREA": "AREA_KM2",
    "SITUACAO": "SITUACAO_MUNICIPIO",
    "CAPITAL": "EH_CAPITAL",
    "MESOCOD": "COD_MESORREGIAO",
    "MICROCOD": "COD_MICRORREGIAO",
}


def _normalizar_chave(nome: str) -> str:
    """Normaliza um nome de coluna para comparação robusta: remove BOM e
    espaços, tira acentos e passa a maiúsculo. Assim 'NO_MUNICÍPIO',
    ' no_municipio ' e 'NO_MUNICIPIO' viram a mesma chave."""
    import unicodedata
    limpo = nome.replace("\ufeff", "").strip()
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", limpo) if not unicodedata.combining(c)
    )
    return sem_acento.upper()


# Mapa por chave normalizada -> nome legível final.
_RENOMEAR_GEO_NORM = {_normalizar_chave(k): v for k, v in _RENOMEAR_GEO.items()}


def _renomear_geo(df):
    novos = {}
    for c in df.columns:
        chave = _normalizar_chave(c)
        novos[c] = _RENOMEAR_GEO_NORM.get(chave, chave)
    return df.rename(columns=novos)


# Ordem harmônica: hierarquia do país ao município, com as duas divisões
# territoriais (saúde do SUS e estatística do IBGE) agrupadas, depois a
# identificação do município, seus atributos e por fim a geolocalização.
_ORDEM_GEO = [
    # Hierarquia político-administrativa (IBGE)
    "CO_REGIAO_PAIS", "REGIAO_PAIS", "CO_UF", "SG_UF", "UF",
    # Divisão de saúde (SUS)
    "COD_MACRORREGIAO_DE_SAUDE", "MACRORREGIAO_DE_SAUDE",
    "COD_REGIAO_DE_SAUDE", "REGIAO_DE_SAUDE",
    # Divisão estatística (IBGE)
    "COD_MESORREGIAO", "COD_MICRORREGIAO",
    # Município: identificação e atributos
    "COD_MUNICIPIO", "MUNCODDV", "NOME_MUNICIPIO", "EH_CAPITAL",
    "SITUACAO_MUNICIPIO", "POPULACAO_IBGE_2022",
    # Geolocalização
    "LATITUDE", "LONGITUDE", "ALTITUDE", "AREA_KM2",
]


def _ordenar_geo(df):
    """Ordena as colunas na sequência harmônica. Colunas fora da lista (novas
    ou inesperadas) vão para o fim, preservando a informação."""
    presentes = [c for c in _ORDEM_GEO if c in df.columns]
    resto = [c for c in df.columns if c not in _ORDEM_GEO]
    return df[presentes + resto]


def _publicar_sinonimos(df_cadmun) -> bool:
    mapa = montar_mapa_sinonimos(df_cadmun)
    df_sin = pd.DataFrame(
        [{"COD_MUNICIPIO_ANTIGO": a, "COD_MUNICIPIO_ATUAL": b} for a, b in sorted(mapa.items())]
    )
    return dataframe_para_parquet(df_sin, PASTA_BUCKET, NOME_SINONIMOS)


def main() -> int:
    if not CSV_LANDING.exists():
        print(f"[INFO] {CSV_LANDING.name} não está na landing -- nada a processar.")
        return exit_codes.SEM_NOVIDADE

    if not XLS_GEO.exists():
        print(f"[ERRO] '{XLS_GEO.name}' não encontrado. Coloque em {MANUAL_MACROREGIAO_DIR}.")
        return exit_codes.ERRO

    if not CADMUN_PARQUET.exists():
        print(f"[ERRO] '{CADMUN_PARQUET.name}' não encontrado. Coloque em {MANUAL_MACROREGIAO_DIR}.")
        return exit_codes.ERRO

    print("Lendo CSV, XLS e CADMUN para ajuste de zeros à esquerda...")
    df = pd.read_csv(CSV_LANDING, sep=";", encoding="utf-8-sig", dtype=str)
    df_geo = pd.read_excel(XLS_GEO, dtype=str)
    df_cadmun = pd.read_parquet(CADMUN_PARQUET)

    df["cod_municipio"] = df["cod_municipio"].str.zfill(6)
    df_geo["MUNCOD"] = df_geo["MUNCOD"].str.zfill(6)
    df_cadmun["MUNCOD"] = df_cadmun["MUNCOD"].astype(str).str.zfill(6)

    # MS (CSV) + planilha de geolocalização (XLS) são a base: já trazem
    # macrorregião, região de saúde, UF, nome, população e coordenadas. Do
    # CADMUN aproveitamos só o que essas fontes não têm: situação, capital e
    # os códigos de meso/microrregião. Evita colunas duplicadas (lat/long/área).
    colunas_cadmun_complemento = ["MUNCOD", "SITUACAO", "CAPITAL", "MESOCOD", "MICROCOD"]
    colunas_cadmun_presentes = [c for c in colunas_cadmun_complemento if c in df_cadmun.columns]
    df_cad = df_cadmun[colunas_cadmun_presentes].drop_duplicates(subset=["MUNCOD"])

    con = conectar_duckdb()
    con.register("macro", df)
    con.register("geo", df_geo)
    con.register("cad", df_cad)

    query = """
        SELECT m.*, g.* EXCLUDE (MUNCOD), c.* EXCLUDE (MUNCOD)
        FROM macro m
        LEFT JOIN geo g ON m.cod_municipio = g.MUNCOD
        LEFT JOIN cad c ON m.cod_municipio = c.MUNCOD
    """

    try:
        df_final = con.execute(query).fetchdf()
    finally:
        con.close()

    df_final = _renomear_geo(df_final)
    df_final = _ordenar_geo(df_final)

    esperadas = {"NOME_MUNICIPIO", "COD_MUNICIPIO", "AREA_KM2"}
    faltando = esperadas - set(df_final.columns)
    if faltando:
        print(f"[AVISO] colunas esperadas ausentes após renomeação: {sorted(faltando)}. "
              "Verifique se os nomes na origem (CSV/XLS/CADMUN) mudaram.")

    sucesso = dataframe_para_parquet(df_final, PASTA_BUCKET, NOME_ARQUIVO_FINAL)

    if not sucesso:
        return exit_codes.ERRO

    if not _publicar_sinonimos(df_cadmun):
        return exit_codes.ERRO

    assinatura = hashlib.sha256(CSV_LANDING.read_bytes()).hexdigest()
    assinaturas = carregar_assinaturas(PASTA_BUCKET)
    assinaturas[CHAVE_FONTE] = assinatura
    salvar_assinaturas(PASTA_BUCKET, assinaturas)

    CSV_LANDING.unlink(missing_ok=True)
    return exit_codes.SUCESSO


if __name__ == "__main__":
    sys.exit(main())
