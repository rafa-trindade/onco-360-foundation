"""PNS 2013 - Rastreamento de Câncer de Colo do Útero (process).

Diferente do recorte de diagnóstico, não filtra por ter tido câncer: é sobre
comportamento preventivo de todas as mulheres entrevistadas (exame preventivo
/ Papanicolau). Filtra mulheres com resposta no bloco R. Posições confirmadas
contra o dicionário oficial PNS 2013.
"""
import sys

import pandas as pd

from scripts.process.ibge.common.pns_base import (
    PNS_MANUAL_DIR, extrair, decodificar, finalizar_e_publicar, logger,
)
from scripts.common import exit_codes

ARQUIVO_ENTRADA = PNS_MANUAL_DIR / "PNS_2013.txt"
NOME_ARQUIVO_FINAL = "pns_2013_rastreamento_colo_utero.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_ULTIMO_EXAME = {
    "1": "Menos de 1 ano atrás", "2": "De 1 a menos de 2 anos",
    "3": "De 2 a menos de 3 anos", "4": "3 anos ou mais atrás", "5": "Nunca fez",
}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não"}
MAPA_SIM_NAO_NSABE = {"1": "Sim", "2": "Não", "3": "Não sabe"}
MAPA_RESULTADO = {
    "1": "Menos de 1 mês depois", "2": "De 1 a menos de 3 meses depois",
    "3": "De 3 a menos de 6 meses depois", "4": "6 meses ou mais depois",
    "5": "Ainda não recebi", "6": "Nunca recebi", "7": "Nunca fui buscar",
}
MAPA_MOTIVO_HISTERECTOMIA = {
    "1": "Mioma uterino", "2": "Prolapso do útero", "3": "Endometriose",
    "4": "Câncer ginecológico", "5": "Complicações da gravidez ou parto",
    "6": "Sangramento vaginal anormal", "7": "Outro",
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
    ("ULTIMO_EXAME_PREVENTIVO", 1044, 1),
    ("COBERTO_PLANO_SAUDE", 1047, 1),
    ("PAGOU_EXAME", 1048, 1),
    ("FEITO_PELO_SUS", 1049, 1),
    ("TEMPO_ATE_RESULTADO", 1050, 1),
    ("FEZ_HISTERECTOMIA", 1055, 1),
    ("MOTIVO_HISTERECTOMIA", 1056, 1),
    ("IDADE_HISTERECTOMIA", 1057, 2),
]

ORDEM = [
    "ULTIMO_EXAME_PREVENTIVO", "FEITO_PELO_SUS", "PAGOU_EXAME", "COBERTO_PLANO_SAUDE",
    "TEMPO_ATE_RESULTADO",
    "FEZ_HISTERECTOMIA", "MOTIVO_HISTERECTOMIA", "IDADE_HISTERECTOMIA",
    "SEXO", "IDADE", "COR_RACA", "COD_UF",
    "ESTRATO_AMOSTRAL", "UNIDADE_PRIMARIA_AMOSTRAGEM", "NUM_ORDEM_DOMICILIO",
    "NUM_ORDEM_MORADOR",
]


def main() -> int:
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return exit_codes.ERRO

    logger.info("Lendo microdados PNS 2013 (rastreamento colo do útero)...")
    registros = []
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")
            if extrair(linha, 106, 1) != "2":  # só mulheres
                continue
            if not extrair(linha, 1044, 1):  # sem resposta no bloco R
                continue
            registros.append({nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS})

    df = pd.DataFrame(registros)
    logger.info(f"{len(df)} mulher(es) no recorte de rastreamento.")

    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["ULTIMO_EXAME_PREVENTIVO"] = df["ULTIMO_EXAME_PREVENTIVO"].apply(lambda v: decodificar(v, MAPA_ULTIMO_EXAME))
    df["COBERTO_PLANO_SAUDE"] = df["COBERTO_PLANO_SAUDE"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["PAGOU_EXAME"] = df["PAGOU_EXAME"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["FEITO_PELO_SUS"] = df["FEITO_PELO_SUS"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_NSABE))
    df["TEMPO_ATE_RESULTADO"] = df["TEMPO_ATE_RESULTADO"].apply(lambda v: decodificar(v, MAPA_RESULTADO))
    df["FEZ_HISTERECTOMIA"] = df["FEZ_HISTERECTOMIA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["MOTIVO_HISTERECTOMIA"] = df["MOTIVO_HISTERECTOMIA"].apply(lambda v: decodificar(v, MAPA_MOTIVO_HISTERECTOMIA))

    return finalizar_e_publicar(df, NOME_ARQUIVO_FINAL, ORDEM)


if __name__ == "__main__":
    sys.exit(main())
