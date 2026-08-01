"""PNS 2019 - Rastreamento de Câncer de Mama (process).

Comportamento de rastreamento de câncer de mama (exame clínico das mamas e
mamografia) das mulheres entrevistadas na PNS 2019 (IBGE). Uma linha por
mulher com resposta no bloco. Posições confirmadas contra o dicionário oficial
PNS 2019.
"""
import sys

import pandas as pd

from scripts.process.ibge.common.pns_base import (
    PNS_MANUAL_DIR, extrair, decodificar, finalizar_e_publicar, logger,
)
from scripts.common import exit_codes

ARQUIVO_ENTRADA = PNS_MANUAL_DIR / "PNS_2019.txt"
NOME_ARQUIVO_FINAL = "pns_2019_rastreamento_mama.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_QUANDO = {
    "1": "Há menos de 1 ano", "2": "De 1 a menos de 2 anos",
    "3": "De 2 a menos de 3 anos", "4": "Há 3 anos ou mais",
    "5": "Nunca fez", "9": "Ignorado",
}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não", "9": "Ignorado"}
MAPA_SIM_NAO_NSABE = {"1": "Sim", "2": "Não", "3": "Não sabe/Não lembra"}
MAPA_RESULTADO = {
    "1": "Menos de 1 mês depois", "2": "De 1 a menos de 3 meses depois",
    "3": "De 3 a menos de 6 meses depois", "4": "6 meses ou mais depois",
    "5": "Ainda não recebi", "6": "Nunca recebi", "7": "Nunca fui buscar", "9": "Ignorado",
}
MAPA_ENCAMINHAMENTO = {
    "1": "Sim", "2": "Não",
    "3": "Não houve encaminhamento, consultas já eram com especialista", "9": "Ignorado",
}

CAMPOS = [
    ("UF", 1, 2),
    ("ESTRATO", 3, 7),
    ("UPA_PNS", 10, 9),
    ("V0006_PNS", 19, 4),
    ("NUM_ORDEM_MORADOR", 104, 2),
    ("SEXO", 108, 1),
    ("IDADE", 117, 3),
    ("COR_RACA", 120, 1),
    ("ULTIMO_EXAME_CLINICO_MAMAS", 1078, 1),
    ("MAMOGRAFIA_SOLICITADA", 1079, 1),
    ("FEZ_MAMOGRAFIA", 1080, 1),
    ("ULTIMA_MAMOGRAFIA", 1081, 1),
    ("PAGOU_MAMOGRAFIA", 1082, 1),
    ("MAMOGRAFIA_PELO_SUS", 1083, 1),
    ("TEMPO_ATE_RESULTADO", 1084, 1),
    ("ENCAMINHAMENTO_APOS_RESULTADO", 1085, 1),
    ("FOI_A_CONSULTA_ESPECIALISTA", 1086, 1),
]

ORDEM = [
    "ULTIMO_EXAME_CLINICO_MAMAS", "MAMOGRAFIA_SOLICITADA", "FEZ_MAMOGRAFIA",
    "ULTIMA_MAMOGRAFIA", "MAMOGRAFIA_PELO_SUS", "PAGOU_MAMOGRAFIA",
    "TEMPO_ATE_RESULTADO", "ENCAMINHAMENTO_APOS_RESULTADO", "FOI_A_CONSULTA_ESPECIALISTA",
    "SEXO", "IDADE", "COR_RACA", "COD_UF",
    "ESTRATO_AMOSTRAL", "UNIDADE_PRIMARIA_AMOSTRAGEM", "NUM_ORDEM_DOMICILIO",
    "NUM_ORDEM_MORADOR",
]


def main() -> int:
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return exit_codes.ERRO

    logger.info("Lendo microdados PNS 2019 (rastreamento de mama)...")
    registros = []
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")
            if extrair(linha, 108, 1) != "2":  # só mulheres
                continue
            if not extrair(linha, 1078, 1):  # sem resposta no bloco de mama
                continue
            registros.append({nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS})

    df = pd.DataFrame(registros)
    logger.info(f"{len(df)} mulher(es) no recorte de rastreamento de mama.")

    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["ULTIMO_EXAME_CLINICO_MAMAS"] = df["ULTIMO_EXAME_CLINICO_MAMAS"].apply(lambda v: decodificar(v, MAPA_QUANDO))
    df["MAMOGRAFIA_SOLICITADA"] = df["MAMOGRAFIA_SOLICITADA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["FEZ_MAMOGRAFIA"] = df["FEZ_MAMOGRAFIA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["ULTIMA_MAMOGRAFIA"] = df["ULTIMA_MAMOGRAFIA"].apply(lambda v: decodificar(v, MAPA_QUANDO))
    df["PAGOU_MAMOGRAFIA"] = df["PAGOU_MAMOGRAFIA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["MAMOGRAFIA_PELO_SUS"] = df["MAMOGRAFIA_PELO_SUS"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_NSABE))
    df["TEMPO_ATE_RESULTADO"] = df["TEMPO_ATE_RESULTADO"].apply(lambda v: decodificar(v, MAPA_RESULTADO))
    df["ENCAMINHAMENTO_APOS_RESULTADO"] = df["ENCAMINHAMENTO_APOS_RESULTADO"].apply(lambda v: decodificar(v, MAPA_ENCAMINHAMENTO))
    df["FOI_A_CONSULTA_ESPECIALISTA"] = df["FOI_A_CONSULTA_ESPECIALISTA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))

    return finalizar_e_publicar(df, NOME_ARQUIVO_FINAL, ORDEM)


if __name__ == "__main__":
    sys.exit(main())
