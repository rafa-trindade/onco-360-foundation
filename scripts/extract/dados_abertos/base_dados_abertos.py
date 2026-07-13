import hashlib
import requests
import zipfile
from io import BytesIO
from pathlib import Path

from scripts.common.paths import BASE_DIR, LANDING_DIR, RAW_DIR  # noqa: F401

# -----------------------------------------
# Funções Utilitárias Reutilizáveis
# -----------------------------------------
def baixar_e_extrair_csv(url: str, caminho_destino: Path) -> bool:
    """
    Baixa um arquivo ZIP da URL, extrai o primeiro arquivo .csv encontrado
    e salva no caminho de destino (Landing Zone).

    Compara o hash do conteúdo baixado contra o que já está salvo em
    caminho_destino -- só sobrescreve e reporta novidade se o conteúdo
    for de fato diferente. Sem isso, esta fonte (HTTP simples, sem o
    SKIP-por-tamanho que o FTP tem) sempre reportava "novidade" mesmo
    quando o conteúdo era idêntico ao de uma execução anterior,
    disparando publicação (bucket/Kaggle) desnecessária a cada run.

    Retorna True se houve novidade (conteúdo novo ou diferente do
    anterior), False se o conteúdo é idêntico ao já salvo.
    """
    caminho_destino.parent.mkdir(parents=True, exist_ok=True)

    print(f"Baixando: {url}")
    response = requests.get(url, timeout=120)
    response.raise_for_status()

    print("Descompactando o arquivo ZIP...")
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(csv_name) as csvfile:
            conteudo_novo = csvfile.read()

    hash_novo = hashlib.sha256(conteudo_novo).hexdigest()

    if caminho_destino.exists():
        hash_antigo = hashlib.sha256(caminho_destino.read_bytes()).hexdigest()
        if hash_novo == hash_antigo:
            print(f"[SKIP] {caminho_destino.name} -- conteúdo idêntico ao já baixado.")
            return False

    with open(caminho_destino, "wb") as f_out:
        f_out.write(conteudo_novo)

    print(f"✔ Arquivo salvo em Landing: {caminho_destino.name} (conteúdo novo)")
    return True