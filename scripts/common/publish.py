"""Interface de consolidação e publicação de arquivos Parquet no S3."""
import logging
from pathlib import Path

import duckdb

from scripts.common.paths import PROCESSED_DIR, DUCKDB_TEMP_DIR
from scripts.common.bucket_sync import upload_and_cleanup

logger = logging.getLogger(__name__)

ROW_GROUP_SIZE = 250_000
MEMORY_LIMIT = "4GB"
THREADS = 4


def conectar_duckdb():
    """Conexão em memória com fallback de diretório temporário obrigatório para disk spill."""
    DUCKDB_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(database=":memory:", config={
        "temp_directory": str(DUCKDB_TEMP_DIR),
        "memory_limit": MEMORY_LIMIT,
    })
    con.execute(f"PRAGMA threads={THREADS};")
    return con


def _caminho_temporario(pasta_bucket: str, nome_arquivo: str) -> Path:
    destino = PROCESSED_DIR / pasta_bucket
    destino.mkdir(parents=True, exist_ok=True)
    return destino / nome_arquivo


def query_para_parquet(query: str, pasta_bucket: str, nome_arquivo: str, con=None) -> bool:
    """Regra de negócio: Resultados vazios são publicados intencionalmente para preservar o contrato de schema."""
    fechar = False
    if con is None:
        con = conectar_duckdb()
        fechar = True

    caminho = _caminho_temporario(pasta_bucket, nome_arquivo)
    s3_key = f"{pasta_bucket}/{nome_arquivo}"

    try:
        logger.info(f"Gerando {nome_arquivo}...")
        con.execute(f"""
            COPY ({query})
            TO '{caminho}' (FORMAT PARQUET, ROW_GROUP_SIZE {ROW_GROUP_SIZE});
        """)
        contagem = con.execute(f"SELECT COUNT(*) FROM read_parquet('{caminho}')").fetchone()[0]
        logger.info(f"{contagem} registros em {nome_arquivo}.")
    except Exception as e:
        logger.error(f"Falha ao gerar {nome_arquivo}: {e}")
        return False
    finally:
        if fechar:
            con.close()

    return upload_and_cleanup(caminho, s3_key)


def publicar_arquivo_pronto(caminho_local: Path, pasta_bucket: str, nome_arquivo: str) -> bool:
    """Publica snapshot persistente (ex: MANUAL_DIR).
    Nota arquitetural: Usa `apagar_local=False` para garantir que a origem não seja expurgada.
    """
    if not caminho_local.exists():
        logger.error(f"Arquivo manual não encontrado: {caminho_local}")
        return False
    s3_key = f"{pasta_bucket}/{nome_arquivo}"
    return upload_and_cleanup(caminho_local, s3_key, apagar_local=False)


def dataframe_para_parquet(df, pasta_bucket: str, nome_arquivo: str) -> bool:
    """Regra de negócio: Resultados vazios são publicados intencionalmente para preservar o contrato de schema."""
    if df is None:
        logger.error(f"DataFrame nulo -- {nome_arquivo} não foi gerado.")
        return False

    if df.empty:
        logger.warning(f"DataFrame vazio -- {nome_arquivo} será publicado só com o schema.")

    caminho = _caminho_temporario(pasta_bucket, nome_arquivo)
    s3_key = f"{pasta_bucket}/{nome_arquivo}"

    try:
        df.to_parquet(caminho, index=False, row_group_size=ROW_GROUP_SIZE)
        logger.info(f"{len(df)} registros em {nome_arquivo}.")
    except Exception as e:
        logger.error(f"Falha ao gerar {nome_arquivo}: {e}")
        return False

    return upload_and_cleanup(caminho, s3_key)

def bucket_para_dataframe(pasta_bucket: str, nome_arquivo: str):
    """Lê um parquet publicado no bucket e devolve como DataFrame.

    Útil para cruzar uma fonte com outra já publicada (ex: convênios x CNES),
    sem depender de arquivos locais no fluxo antigo."""
    import pyarrow.fs as pafs
    import pyarrow.parquet as pq
    from scripts.common import env

    endpoint = env.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    esquema = "https" if env.MINIO_ENDPOINT.startswith("https://") else "http"
    s3_fs = pafs.S3FileSystem(
        endpoint_override=endpoint,
        access_key=env.MINIO_ROOT_USER,
        secret_key=env.MINIO_ROOT_PASSWORD,
        scheme=esquema,
    )
    chave = f"{env.MINIO_BUCKET}/{pasta_bucket}/{nome_arquivo}"
    return pq.read_table(chave, filesystem=s3_fs).to_pandas()
