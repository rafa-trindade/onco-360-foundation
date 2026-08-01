"""PNS 2019 - Diagnóstico e Tipo de Câncer (process).

Respondentes com diagnóstico médico de câncer (Q120 = Sim). Diferente da PNS
2013 (uma variável categórica), o tipo de câncer em 2019 é registrado como 15
flags binárias independentes (permite mais de um tipo por pessoa). NÃO há idade
no diagnóstico nesta edição (confirmado no dicionário). Posições confirmadas
contra o dicionário oficial PNS 2019.
"""
import sys

from scripts.process.ibge.common.pns_base import (
    PNS_MANUAL_DIR, extrair, decodificar, finalizar_e_publicar, logger,
)
from scripts.common import exit_codes

ARQUIVO_ENTRADA = PNS_MANUAL_DIR / "PNS_2019.txt"
NOME_ARQUIVO_FINAL = "pns_2019_diagnostico_cancer.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não", "3": "Não sei", "9": "Ignorado"}
MAPA_LIMITACAO = {
    "1": "Não limita", "2": "Um pouco", "3": "Moderadamente",
    "4": "Intensamente", "5": "Muito intensamente", "9": "Ignorado",
}

TIPOS_CANCER = {
    "TIPO_PELE": (1032, 1),
    "TIPO_PELE_MELANOMA": (1033, 1),
    "TIPO_PULMAO": (1034, 1),
    "TIPO_COLON_RETO": (1035, 1),
    "TIPO_ESTOMAGO": (1036, 1),
    "TIPO_MAMA": (1037, 1),
    "TIPO_COLO_UTERO": (1038, 1),
    "TIPO_PROSTATA": (1039, 1),
    "TIPO_BOCA_OROFARINGE_LARINGE": (1040, 1),
    "TIPO_BEXIGA": (1041, 1),
    "TIPO_LINFOMA_LEUCEMIA": (1042, 1),
    "TIPO_CEREBRO": (1043, 1),
    "TIPO_OVARIO": (1044, 1),
    "TIPO_TIREOIDE": (1045, 1),
    "TIPO_OUTRO": (1046, 1),
}

CAMPOS_CONTEXTO = [
    ("UF", 1, 2),
    ("ESTRATO", 3, 7),
    ("UPA_PNS", 10, 9),
    ("V0006_PNS", 19, 4),
    ("NUM_ORDEM_MORADOR", 104, 2),
    ("SEXO", 108, 1),
    ("IDADE", 117, 3),
    ("COR_RACA", 120, 1),
]

ORDEM = (
    ["DIAGNOSTICO_CANCER"]
    + list(TIPOS_CANCER.keys())
    + ["LIMITACAO_ATIVIDADES", "SEXO", "IDADE", "COR_RACA", "COD_UF",
       "ESTRATO_AMOSTRAL", "UNIDADE_PRIMARIA_AMOSTRAGEM", "NUM_ORDEM_DOMICILIO",
       "NUM_ORDEM_MORADOR"]
)


def main() -> int:
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return exit_codes.ERRO

    logger.info("Lendo microdados PNS 2019 (diagnóstico de câncer)...")
    registros = []
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")
            if extrair(linha, 1031, 1) != "1":
                continue
            registro = {nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS_CONTEXTO}
            for nome, (pos, tam) in TIPOS_CANCER.items():
                registro[nome] = extrair(linha, pos, tam)
            registro["LIMITACAO_ATIVIDADES"] = extrair(linha, 1049, 1)
            registros.append(registro)

    import pandas as pd
    df = pd.DataFrame(registros)
    logger.info(f"{len(df)} registro(s) com diagnóstico de câncer.")

    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    for nome in TIPOS_CANCER:
        df[nome] = df[nome].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["LIMITACAO_ATIVIDADES"] = df["LIMITACAO_ATIVIDADES"].apply(lambda v: decodificar(v, MAPA_LIMITACAO))
    df["DIAGNOSTICO_CANCER"] = "Sim"

    return finalizar_e_publicar(df, NOME_ARQUIVO_FINAL, ORDEM)


if __name__ == "__main__":
    sys.exit(main())
