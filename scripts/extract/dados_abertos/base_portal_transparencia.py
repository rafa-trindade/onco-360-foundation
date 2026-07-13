"""
Base para consultas à API do Portal da Transparência do Governo Federal.

Autenticação: header HTTP `chave-api-dados`, obtido via cadastro em
https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
(login Gov.br, conta nível Prata/Ouro ou CPF+senha com 2FA).

A chave NUNCA fica hardcoded -- vem da variável de ambiente
PORTAL_TRANSPARENCIA_API_KEY, lida do arquivo .env na raiz do projeto.
"""
import os
import time
import requests
from dotenv import load_dotenv

from scripts.common.paths import BASE_DIR

load_dotenv(BASE_DIR / ".env")

BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"

API_KEY = os.environ.get("PORTAL_TRANSPARENCIA_API_KEY")

# Limite documentado varia por horário (até 700 req/min de madrugada,
# bem mais restrito durante o dia) -- delay conservador entre chamadas
# pra não estourar limite em horário comercial.
DELAY_ENTRE_CHAMADAS = 1.0


def _headers() -> dict:
    if not API_KEY:
        raise RuntimeError(
            "PORTAL_TRANSPARENCIA_API_KEY não configurada. "
            "Cadastre-se em https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email "
            "e defina a variável de ambiente antes de rodar este script."
        )
    return {"chave-api-dados": API_KEY}


def consultar_paginado(endpoint: str, params: dict, max_paginas: int | None = None) -> list[dict]:
    """
    Consulta um endpoint da API paginando automaticamente até a última
    página (a API do Portal da Transparência não informa total de
    páginas -- convenção usual é parar quando uma página vier vazia).
    """
    url = f"{BASE_URL}/{endpoint}"
    resultados = []
    pagina = 1

    while True:
        if max_paginas and pagina > max_paginas:
            break

        params_pagina = {**params, "pagina": pagina}
        print(f"[{endpoint}] Consultando página {pagina}...")

        try:
            resp = requests.get(url, params=params_pagina, headers=_headers(), timeout=30)
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"[ERRO] {endpoint} página {pagina}: {e} -- resposta: {resp.text[:500]}")
            break

        dados_pagina = resp.json()
        if not dados_pagina:
            print(f"[{endpoint}] Página {pagina} vazia -- fim da paginação.")
            break

        resultados.extend(dados_pagina)
        print(f"[{endpoint}] Página {pagina}: {len(dados_pagina)} registro(s).")
        pagina += 1
        time.sleep(DELAY_ENTRE_CHAMADAS)

    return resultados