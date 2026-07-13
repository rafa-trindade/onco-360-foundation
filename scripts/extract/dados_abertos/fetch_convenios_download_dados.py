"""
Portal da Transparência - Convênios (via Dados Abertos / download-de-dados)

Baixa o arquivo acumulado de Convênios via o mecanismo de "Dados
Abertos" do Portal da Transparência -- diferente da API
(api.portaldatransparencia.gov.br, que exige chave/2FA), este caminho é
público: sem autenticação, sem chave, sem login.

URL: https://portaldatransparencia.gov.br/download-de-dados/convenios/{AAAAMMDD}

A data no final do endereço é a "data de referência" da extração (o
portal atualiza semanalmente) -- NÃO representa um período específico
de convênios. Confirmado na página oficial de perguntas frequentes do
Portal ("Convênios e Outros Acordos"): "Os dados apresentados são o
acumulado desde 1996." Cada data é um retrato de TUDO desde 1996 até
aquele momento -- não precisamos baixar várias datas e somar, só a
mais recente já é o histórico completo.

Como a página só mostra a data mais recente via JavaScript, o script
tenta a data de hoje e vai voltando dia a dia até achar a mais recente
que responder com um arquivo de verdade.

O .zip baixado contém 2 CSVs (Convenios e Convenios_OrdensBancarias) --
igual ao resto do projeto, o extract descompacta e entrega o formato
final (CSV) direto na Landing; nunca deixa um .zip cru salvo.
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
    """
    Remove o prefixo de data (ex: '20260703_') do nome do arquivo de
    dentro do zip. O nome final salvo na Landing precisa ser ESTÁVEL
    entre execuções -- sempre "Convenios.csv", nunca
    "20260710_Convenios.csv" -- senão cada atualização semanal cria um
    arquivo NOVO em vez de substituir o anterior (o conteúdo já é o
    acumulado inteiro desde 1996, não um recorte da semana -- guardar
    um snapshot por semana seria só duplicação sem propósito).
    """
    nome_base = Path(nome_interno).name
    return re.sub(r"^\d{8}_", "", nome_base)


def _parece_arquivo_valido(resp: requests.Response) -> bool:
    """Distingue uma resposta com arquivo de verdade de uma página de
    erro/vazia -- checa tamanho mínimo e que não é HTML."""
    if resp.status_code != 200:
        return False
    if len(resp.content) < 10_000:  # arquivo real tem 1996-hoje, não cabe em poucos KB
        return False
    content_type = resp.headers.get("Content-Type", "").lower()
    if "text/html" in content_type:
        return False
    return True


def achar_e_baixar_mais_recente() -> tuple[str, bytes] | None:
    """Tenta a partir de hoje, voltando dia a dia, até achar uma data
    cuja extração exista de verdade. Retorna (data_str, conteudo_zip) ou None."""
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
    """Compara hash do conteúdo contra o já salvo em Landing -- só
    sobrescreve e reporta novidade se for de fato diferente."""
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
    """Retorna True se pelo menos um dos CSVs teve conteúdo novo."""
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