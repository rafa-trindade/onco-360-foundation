"""Base compartilhada para os microdados de largura fixa da PNS (IBGE).

As posições (pos_inicial, tamanho) usadas nos process scripts foram extraídas
dos dicionários oficiais (dicionario_PNS_microdados_2013.xls e _2019.xls),
conferidas variável a variável.

Centraliza a leitura de largura fixa, a decodificação, a renomeação para nomes
legíveis (padrão do projeto) e a publicação no bucket.
"""
import logging

import pandas as pd

from scripts.common.paths import MANUAL_PNS_DIR
from scripts.common.publish import dataframe_para_parquet
from scripts.common import exit_codes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PNS_MANUAL_DIR = MANUAL_PNS_DIR
PASTA_BUCKET = "ibge"

MAPA_COR_RACA = {
    "1": "Branca", "2": "Preta", "3": "Amarela", "4": "Parda", "5": "Indígena",
    "9": "Ignorado",
}

# Renomeação dos campos técnicos/amostrais para nomes legíveis.
RENOMEAR = {
    "UF": "COD_UF",
    "ESTRATO": "ESTRATO_AMOSTRAL",
    "UPA_PNS": "UNIDADE_PRIMARIA_AMOSTRAGEM",
    "V0006_PNS": "NUM_ORDEM_DOMICILIO",
}


def extrair(linha: str, pos_inicial: int, tamanho: int) -> str:
    """Extrai um campo de largura fixa. pos_inicial é 1-indexado (convenção do
    dicionário do IBGE)."""
    inicio = pos_inicial - 1
    return linha[inicio:inicio + tamanho].strip()


def decodificar(valor: str, mapa: dict, vazio: str = "") -> str:
    """Troca o código pela descrição; mantém o código original se não achar no
    mapa (não perde informação silenciosamente)."""
    if not valor:
        return vazio
    return mapa.get(valor, valor)


def idade_para_inteiro(serie: pd.Series) -> pd.Series:
    """Idade textual (com zeros à esquerda) para inteiro nullable."""
    return pd.to_numeric(serie, errors="coerce").astype("Int64")


def ler_microdados(arquivo, campos, filtro_pos, filtro_valor) -> pd.DataFrame:
    """Lê o arquivo de largura fixa, aplicando um filtro por posição
    (pos, tamanho) -> valor exigido. Devolve um DataFrame com os campos
    extraídos como texto."""
    registros = []
    pos, tam = filtro_pos
    with open(arquivo, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")
            if extrair(linha, pos, tam) != filtro_valor:
                continue
            registros.append({nome: extrair(linha, p, t) for nome, p, t in campos})
    logger.info(f"{len(registros)} registro(s) após o filtro.")
    return pd.DataFrame(registros)


def finalizar_e_publicar(df: pd.DataFrame, nome_arquivo: str, ordem: list[str]) -> int:
    """Renomeia para nomes legíveis, decodifica cor/raça, converte idades para
    inteiro, ordena por importância e publica no bucket."""
    df = df.rename(columns={c: RENOMEAR.get(c, c) for c in df.columns})

    if "COR_RACA" in df.columns:
        df["COR_RACA"] = df["COR_RACA"].apply(lambda v: decodificar(v, MAPA_COR_RACA))
    for coluna in ("IDADE", "IDADE_DIAGNOSTICO", "IDADE_HISTERECTOMIA"):
        if coluna in df.columns:
            df[coluna] = idade_para_inteiro(df[coluna])

    presentes = [c for c in ordem if c in df.columns]
    resto = [c for c in df.columns if c not in ordem]
    df = df[presentes + resto]

    ok = dataframe_para_parquet(df, PASTA_BUCKET, nome_arquivo)
    if not ok:
        return exit_codes.ERRO
    logger.info(f"✔ {len(df)} registro(s) publicados em {nome_arquivo}.")
    return exit_codes.SUCESSO
