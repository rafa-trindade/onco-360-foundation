"""
Base compartilhada para leitura dos microdados de largura fixa da PNS
(Pesquisa Nacional de Saúde, IBGE).

As posições (pos_inicial, tamanho) usadas nos scripts de process deste
módulo foram extraídas diretamente dos dicionários oficiais fornecidos
pelo usuário (dicionario_PNS_microdados_2013.xls e _2019.xls),
conferidas variável a variável antes de escrever os process scripts --
não são um chute baseado em outra fonte.
"""
import logging
from scripts.common.paths import LANDING_DIR, RAW_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PNS_LANDING_DIR = LANDING_DIR / "ibge"


def extrair(linha: str, pos_inicial: int, tamanho: int) -> str:
    """
    Extrai um campo de uma linha de microdados de largura fixa.
    pos_inicial é 1-indexado (convenção do dicionário do IBGE -- a
    primeira posição do arquivo é a posição 1, não 0).
    """
    inicio = pos_inicial - 1
    return linha[inicio:inicio + tamanho].strip()


def decodificar(valor: str, mapa: dict, vazio: str = "") -> str:
    """Troca o código pela descrição; mantém o código original se não
    encontrar no mapa (evita perder informação silenciosamente)."""
    if not valor:
        return vazio
    return mapa.get(valor, valor)