"""Extração Portal da Transparência: Convênios (Dados Abertos).

Mecanismo de busca: Polling reverso (D-0 a D-30) para localizar o dump semanal público mais recente.
Regra de negócio: Cada snapshot contém o histórico integral acumulado (desde 1996), dispensando paginação ou merge temporal. O ZIP é descompactado em memória e os CSVs expostos diretamente na Landing.
"""
import time
import hashlib
import re
import zipfile
from io import BytesIO
from pathlib import Path
import requests
from datetime import datetime, timedelta

from scripts.common.paths import LANDING_DIR
from scripts.common import exit_codes

URL_BASE = "https://portaldatransparencia.gov.br/download-de-dados/convenios"
OUTPUT_DIR = LANDING_DIR / "portal_transparencia"

MAX_DIAS_TENTATIVA = 30  # atualização é semanal; 30 dias dá margem de sobra


def _nome_padronizado(nome_interno: str) -> str:
    """Padronização de saída: Remove prefixo temporal do CSV extraído para garantir estabilidade do nome na Landing e permitir overwrite idempotente."""
    nome_base = Path(nome_interno).name
    return re.sub(r"^\d{8}_", "", nome_base)


def _parece_arquivo_valido(resp: requests.Response) -> bool:
    """Validação de payload: Rejeita soft 404s (páginas HTML de erro) e payloads subdimensionados."""
    if resp.status_code != 200:
        return False
    if len(resp.content) < 10_000: 
        return False
    content_type = resp.headers.get("Content-Type", "").lower()
    if "text/html" in content_type:
        return False
    return True


def achar_e_baixar_mais_recente() -> tuple[str, bytes] | None:

    hoje = datetime.now()

    for i in range(MAX_DIAS_TENTATIVA):
        data = hoje - timedelta(days=i)
        data_str = data.strftime("%Y%m%d")
        url = f"{URL_BASE}/{data_str}"
        print(f"Tentando {data_str}...")

        try:
            resp = requests.get(url, timeout=180)
        except requests.RequestException as e:
            print(f"  [ERRO] Falha de conexão em {data_str}: {e}")
            continue

        if _parece_arquivo_valido(resp):
            print(f"✔ Encontrado: {data_str} ({len(resp.content):,} bytes, Content-Type: {resp.headers.get('Content-Type')})")
            return data_str, resp.content

        print(f"  [SKIP] {data_str} não é um arquivo válido (status {resp.status_code}).")
        time.sleep(0.5)

    return None


def _salvar_se_novidade(nome_arquivo: str, conteudo: bytes) -> bool:
    
    caminho_destino = OUTPUT_DIR / nome_arquivo
    hash_novo = hashlib.sha256(conteudo).hexdigest()

    if caminho_destino.exists():
        hash_antigo = hashlib.sha256(caminho_destino.read_bytes()).hexdigest()
        if hash_novo == hash_antigo:
            print(f"[SKIP] {nome_arquivo} -- conteúdo idêntico ao já salvo.")
            return False

    with open(caminho_destino, "wb") as f:
        f.write(conteudo)

    print(f"✔ Arquivo salvo em Landing: {nome_arquivo} (conteúdo novo)")
    return True


def main() -> bool:
    
    resultado = achar_e_baixar_mais_recente()

    if resultado is None:
        print(f"[ERRO] Nenhuma data válida encontrada nos últimos {MAX_DIAS_TENTATIVA} dias.")
        return False

    data_str, conteudo_zip = resultado
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Descompactando o ZIP...")
    houve_novidade = False

    with zipfile.ZipFile(BytesIO(conteudo_zip)) as z:
        nomes_csv = [n for n in z.namelist() if n.lower().endswith(".csv")]

        if not nomes_csv:
            print(f"[ERRO] Nenhum .csv encontrado dentro do zip. Conteúdo: {z.namelist()}")
            return False

        for nome_interno in nomes_csv:
            with z.open(nome_interno) as f:
                conteudo_csv = f.read()
            nome_destino = _nome_padronizado(nome_interno)
            if _salvar_se_novidade(nome_destino, conteudo_csv):
                houve_novidade = True

    return houve_novidade


if __name__ == "__main__":
    novidade = main()
    exit(exit_codes.SUCESSO if novidade else exit_codes.SEM_NOVIDADE)