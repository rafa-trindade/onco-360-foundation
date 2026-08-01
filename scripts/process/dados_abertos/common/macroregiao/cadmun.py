"""Tratamento de referência municipal (CADMUN/DATASUS) e mapeamento de sinônimos.

Regra de negócio: Resolve códigos de municípios extintos presentes em óbitos históricos (SIM) mapeando-os para códigos vigentes via campo `MUNSINON`.
Parser de sinônimos: Suporta múltiplos formatos (avulsos, listas e faixas numéricas com limite de segurança contra intervalos administrativos globais).
"""

MAX_SINONIMOS_POR_FAIXA = 200


def expandir_sinonimos(munsinon: str) -> list[str]:
    """Expande o campo `MUNSINON` em códigos de 6 dígitos, aplicando limite de corte (`MAX_SINONIMOS_POR_FAIXA`) para descartar faixas administrativas genéricas."""
    if not munsinon:
        return []

    codigos = []
    for parte in munsinon.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if "-" in parte:
            inicio, fim = parte.split("-", 1)
            inicio, fim = inicio.strip(), fim.strip()
            if inicio.isdigit() and fim.isdigit() and len(inicio) == len(fim):
                tamanho = int(fim) - int(inicio) + 1
                if tamanho > MAX_SINONIMOS_POR_FAIXA:
                    continue
                for n in range(int(inicio), int(fim) + 1):
                    codigos.append(str(n).zfill(len(inicio))[:6])
        elif parte.isdigit():
            codigos.append(parte.zfill(6)[:6])
    return codigos


def _e_municipio_real(codigo: str) -> bool:
    """Filtra códigos nulos ('000000') e ignorados por UF (terminados em '9999')."""
    return codigo != "000000" and not codigo.endswith("9999")


def montar_mapa_sinonimos(df_cadmun) -> dict[str, str]:
    """Constrói dicionário de de-para (`codigo_antigo -> codigo_atual`) restrito a municípios ativos e válidos."""
    mapa = {}
    for _, linha in df_cadmun.iterrows():
        if str(linha.get("SITUACAO") or "").strip().upper() != "ATIVO":
            continue
        atual = str(linha["MUNCOD"]).zfill(6)
        if not _e_municipio_real(atual):
            continue
        for antigo in expandir_sinonimos(str(linha.get("MUNSINON") or "")):
            if antigo != atual and _e_municipio_real(antigo):
                mapa[antigo] = atual
    return mapa
