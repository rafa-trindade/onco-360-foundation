"""PNS 2013 - Diagnóstico e Tipo de Câncer (process).

Respondentes com diagnóstico médico de câncer (Q120 = Sim), com tipo
(categórico, 1 por pessoa; a PNS 2019 usa flags binárias), idade no
diagnóstico e grau de limitação. Posições confirmadas contra o dicionário
oficial PNS 2013.
"""
import sys

from scripts.process.ibge.common.pns_base import (
    PNS_MANUAL_DIR, decodificar, ler_microdados, finalizar_e_publicar, logger,
)

ARQUIVO_ENTRADA = PNS_MANUAL_DIR / "PNS_2013.txt"
NOME_ARQUIVO_FINAL = "pns_2013_diagnostico_cancer.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_TIPO_CANCER = {
    "1": "Pulmão", "2": "Intestino", "3": "Estômago", "4": "Mama",
    "5": "Colo de útero", "6": "Próstata", "7": "Pele", "8": "Outro",
}
MAPA_LIMITACAO = {
    "1": "Não limita", "2": "Um pouco", "3": "Moderadamente",
    "4": "Intensamente", "5": "Muito intensamente",
}

CAMPOS = [
    ("UF", 1, 2),
    ("ESTRATO", 3, 7),
    ("UPA_PNS", 10, 7),
    ("V0006_PNS", 17, 4),
    ("NUM_ORDEM_MORADOR", 102, 2),
    ("SEXO", 106, 1),
    ("IDADE", 115, 3),
    ("COR_RACA", 118, 1),
    ("DIAGNOSTICO_CANCER", 1018, 1),
    ("TIPO_CANCER", 1019, 1),
    ("IDADE_DIAGNOSTICO", 1020, 2),
    ("LIMITACAO_ATIVIDADES", 1022, 1),
]

ORDEM = [
    "DIAGNOSTICO_CANCER", "TIPO_CANCER", "IDADE_DIAGNOSTICO", "LIMITACAO_ATIVIDADES",
    "SEXO", "IDADE", "COR_RACA", "COD_UF",
    "ESTRATO_AMOSTRAL", "UNIDADE_PRIMARIA_AMOSTRAGEM", "NUM_ORDEM_DOMICILIO",
    "NUM_ORDEM_MORADOR",
]


def main() -> int:
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        from scripts.common import exit_codes
        return exit_codes.ERRO

    logger.info("Lendo microdados PNS 2013 (diagnóstico de câncer)...")
    df = ler_microdados(ARQUIVO_ENTRADA, CAMPOS, filtro_pos=(1018, 1), filtro_valor="1")

    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["TIPO_CANCER"] = df["TIPO_CANCER"].apply(lambda v: decodificar(v, MAPA_TIPO_CANCER))
    df["LIMITACAO_ATIVIDADES"] = df["LIMITACAO_ATIVIDADES"].apply(lambda v: decodificar(v, MAPA_LIMITACAO))
    df["DIAGNOSTICO_CANCER"] = "Sim"

    return finalizar_e_publicar(df, NOME_ARQUIVO_FINAL, ORDEM)


if __name__ == "__main__":
    sys.exit(main())
