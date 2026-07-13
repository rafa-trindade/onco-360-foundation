"""
PNS 2019 - Diagnóstico e Tipo de Câncer (process)

Filtra os respondentes que relataram diagnóstico médico de câncer
(Q120 = Sim). Diferente da PNS 2013 (1 variável categórica), o tipo de
câncer em 2019 é registrado como 16 flags binárias independentes
(permite mais de um tipo por pessoa). NÃO existe variável de idade no
diagnóstico nesta edição (removida em relação a 2013 -- confirmado
conferindo o dicionário posição a posição).

Posições confirmadas contra dicionario_PNS_microdados_2019.xls.

Saída: data/raw/raw_pns_2019_diagnostico_cancer.parquet
"""
import pandas as pd
from scripts.common.paths import RAW_DIR
from scripts.process.ibge.pns_base import PNS_LANDING_DIR, extrair, decodificar, logger

ARQUIVO_ENTRADA = PNS_LANDING_DIR / "PNS_2019.txt"
ARQUIVO_SAIDA = RAW_DIR / "raw_pns_2019_diagnostico_cancer.parquet"

MAPA_SEXO = {"1": "Homem", "2": "Mulher"}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não", "9": "Ignorado"}
MAPA_LIMITACAO = {
    "1": "Não limita", "2": "Um pouco", "3": "Moderadamente",
    "4": "Intensamente", "5": "Muito intensamente", "9": "Ignorado",
}

# Cada tipo de câncer é uma flag Sim/Não própria
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


def main():
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return

    logger.info("Iniciando leitura dos microdados PNS 2019...")
    registros = []

    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")

            diagnostico = extrair(linha, 1031, 1)
            if diagnostico != "1":  # só quem respondeu Sim a Q120
                continue

            registro = {nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS_CONTEXTO}
            for nome, (pos, tam) in TIPOS_CANCER.items():
                registro[nome] = extrair(linha, pos, tam)
            registro["LIMITACAO_ATIVIDADES"] = extrair(linha, 1049, 1)
            registros.append(registro)

    logger.info("Convertendo para DataFrame...")
    df = pd.DataFrame(registros)

    logger.info("Decodificando categorias...")
    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    for nome in TIPOS_CANCER:
        df[nome] = df[nome].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["LIMITACAO_ATIVIDADES"] = df["LIMITACAO_ATIVIDADES"].apply(lambda v: decodificar(v, MAPA_LIMITACAO))
    df["DIAGNOSTICO_CANCER"] = "Sim"

    logger.info(f"Total de registros com diagnóstico de câncer: {len(df)}")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ARQUIVO_SAIDA, index=False)
    logger.info(f"✔ Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()