"""
PNS 2013 - Diagnóstico e Tipo de Câncer (process)

Filtra os respondentes que relataram diagnóstico médico de câncer
(Q120 = Sim), com tipo (categórico, 1 tipo por pessoa -- diferente da
PNS 2019, que virou múltiplas flags binárias), idade no diagnóstico e
grau de limitação nas atividades.

Posições confirmadas contra dicionario_PNS_microdados_2013.xls.

Saída: data/raw/raw_pns_2013_diagnostico_cancer.parquet
"""
import pandas as pd
from scripts.common.paths import RAW_DIR
from scripts.process.ibge.pns_base import PNS_LANDING_DIR, extrair, decodificar, logger

ARQUIVO_ENTRADA = PNS_LANDING_DIR / "PNS_2013.txt"
ARQUIVO_SAIDA = RAW_DIR / "raw_pns_2013_diagnostico_cancer.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_TIPO_CANCER = {
    "1": "Pulmão", "2": "Intestino", "3": "Estômago", "4": "Mama",
    "5": "Colo de útero", "6": "Próstata", "7": "Pele", "8": "Outro",
}
MAPA_LIMITACAO = {
    "1": "Não limita", "2": "Um pouco", "3": "Moderadamente",
    "4": "Intensamente", "5": "Muito intensamente",
}

# (nome_coluna, posicao_inicial, tamanho)
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


def main():
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return

    logger.info("Iniciando leitura dos microdados PNS 2013...")
    registros = []

    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")

            diagnostico = extrair(linha, 1018, 1)
            if diagnostico != "1":  # só quem respondeu Sim a Q120
                continue

            registro = {nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS}
            registros.append(registro)

    logger.info("Convertendo para DataFrame...")
    df = pd.DataFrame(registros)

    logger.info("Decodificando categorias...")
    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["TIPO_CANCER"] = df["TIPO_CANCER"].apply(lambda v: decodificar(v, MAPA_TIPO_CANCER))
    df["LIMITACAO_ATIVIDADES"] = df["LIMITACAO_ATIVIDADES"].apply(lambda v: decodificar(v, MAPA_LIMITACAO))
    df["DIAGNOSTICO_CANCER"] = "Sim"  # já filtrado, mas explícito na saída

    logger.info(f"Total de registros com diagnóstico de câncer: {len(df)}")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ARQUIVO_SAIDA, index=False)
    logger.info(f"✔ Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()