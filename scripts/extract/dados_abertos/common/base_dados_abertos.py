"""Utilitários de extração HTTP/ZIP (Dados Abertos).

Idempotência: Como HTTP não provê metadados de tamanho consistentes como o FTP, e a landing zone é efêmera, a detecção de mudança baseia-se em hash de conteúdo (assinatura) persistido no `_manifest.json` do bucket.
"""
import hashlib
import zipfile
from io import BytesIO
from pathlib import Path

import requests

from scripts.common.paths import BASE_DIR, LANDING_DIR  # noqa: F401
from scripts.common.bucket_sync import carregar_assinaturas


def _hash_conteudo(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def _baixar_csv_de_zip(url: str) -> bytes:
    print(f"Baixando: {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    print("Descompactando o arquivo ZIP...")
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(csv_name) as csvfile:
            return csvfile.read()


def sincronizar_csv_zip(url: str, caminho_destino: Path, pasta_bucket: str,
                        chave_fonte: str) -> tuple[bool, str | None]:
    """Orquestra download, extração de CSV e validação de hash contra o manifesto remoto.
    
    Retorna `(houve_novidade, nova_assinatura)`. O arquivo é persistido na landing exclusivamente em caso de novidade (divergência de hash).
    """
    conteudo = _baixar_csv_de_zip(url)
    assinatura = _hash_conteudo(conteudo)

    assinaturas = carregar_assinaturas(pasta_bucket)
    if assinaturas.get(chave_fonte) == assinatura:
        print(f"[SKIP-MANIFESTO] {chave_fonte} sem alteração na origem desde a última publicação.")
        return False, None

    caminho_destino.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_destino, "wb") as f_out:
        f_out.write(conteudo)
    print(f"✔ Conteúdo novo salvo na landing: {caminho_destino.name}")
    return True, assinatura
