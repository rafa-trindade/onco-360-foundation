"""Resumo anual de óbitos por câncer (modelo streaming).

Publica datasus_sim/obitos_cancer_resumo_anual.parquet com upsert por ano,
compartilhado entre CID-9, CID-10 consolidado e CID-10 preliminar. O total
de óbitos por arquivo vem do header do DBF (numrec, sem ler o corpo), e o
total de câncer sai do parquet de câncer já publicado, agrupado por
ARQUIVO_ORIGEM. Upsert por ano: o consolidado substitui o preliminar do
mesmo ano.
"""
import logging
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from botocore.exceptions import ClientError

from scripts.common import env
from scripts.common.paths import PROCESSED_DIR
from scripts.common.bucket_sync import get_s3_client
from scripts.common.publish import conectar_duckdb, dataframe_para_parquet

logger = logging.getLogger(__name__)

PASTA_BUCKET = "datasus_sim"
NOME_RESUMO = "obitos_cancer_resumo_anual.parquet"
COLUNAS_RESUMO = ["ANO", "FONTE", "ARQUIVO", "TOTAL_OBITOS_GERAL", "TOTAL_OBITOS_CANCER", "PROPORCAO_OBITOS_CANCER", "ERRO"]


def _cancer_por_arquivo(parquet_cancer_key: str) -> dict[str, int]:
    """Conta linhas de câncer por ARQUIVO_ORIGEM no parquet já publicado."""
    existente = PROCESSED_DIR / "_resumo_cancer_tmp.parquet"
    existente.parent.mkdir(parents=True, exist_ok=True)
    s3 = get_s3_client()
    try:
        s3.download_file(env.MINIO_BUCKET, parquet_cancer_key, str(existente))
    except ClientError:
        return {}

    con = conectar_duckdb()
    try:
        linhas = con.execute(
            f"SELECT ARQUIVO_ORIGEM AS arq, COUNT(*) AS n "
            f"FROM read_parquet('{existente}') GROUP BY ARQUIVO_ORIGEM"
        ).fetchall()
    finally:
        con.close()
        existente.unlink(missing_ok=True)
    return {arq: n for arq, n in linhas}


def _carregar_resumo_existente() -> pd.DataFrame:
    existente = PROCESSED_DIR / "_resumo_anual_tmp.parquet"
    existente.parent.mkdir(parents=True, exist_ok=True)
    s3 = get_s3_client()
    try:
        s3.download_file(env.MINIO_BUCKET, f"{PASTA_BUCKET}/{NOME_RESUMO}", str(existente))
    except ClientError:
        return pd.DataFrame(columns=COLUNAS_RESUMO)
    df = pq.read_table(existente).to_pandas()
    existente.unlink(missing_ok=True)
    return df


def atualizar_resumo_anual(totais_por_arquivo: dict[str, int | None], fonte: str,
                           extrair_ano_fn, parquet_cancer_nome: str) -> bool:
    """Monta as linhas de resumo desta fonte e faz upsert por ano no
    parquet consolidado, publicando o resultado."""
    cancer = _cancer_por_arquivo(f"{PASTA_BUCKET}/{parquet_cancer_nome}")

    linhas = []
    for arquivo, total in totais_por_arquivo.items():
        ano = extrair_ano_fn(arquivo)
        total_cancer = cancer.get(arquivo)
        proporcao = (total_cancer / total) if (total and total_cancer is not None) else None
        linhas.append({
            "ANO": ano, "FONTE": fonte, "ARQUIVO": arquivo,
            "TOTAL_OBITOS_GERAL": total, "TOTAL_OBITOS_CANCER": total_cancer,
            "PROPORCAO_OBITOS_CANCER": round(proporcao, 4) if proporcao is not None else None,
            "ERRO": None if total is not None else "falha ao contar registros",
        })

    df_novo = pd.DataFrame(linhas, columns=COLUNAS_RESUMO)
    df_existente = _carregar_resumo_existente()
    anos_atualizados = set(df_novo["ANO"].dropna())
    df_existente = df_existente[~df_existente["ANO"].isin(anos_atualizados)]
    # Filtra DataFrames vazios para evitar o FutureWarning do Pandas
    frames_to_concat = [df for df in [df_existente, df_novo] if not df.empty]

    if frames_to_concat:
        df_final = pd.concat(frames_to_concat, ignore_index=True).sort_values(["ANO", "FONTE"])
    else:
        # Alternativa caso ambos estejam vazios
        df_final = pd.DataFrame(columns=df_existente.columns)
    logger.info(f"Resumo anual: {len(df_novo)} ano(s) de '{fonte}' upsertados, {len(df_final)} linha(s) no total.")
    return dataframe_para_parquet(df_final, PASTA_BUCKET, NOME_RESUMO)
