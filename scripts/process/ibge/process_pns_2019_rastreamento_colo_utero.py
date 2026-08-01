"""PNS 2019 - Rastreamento de Câncer de Colo do Útero (process).

Comportamento preventivo (exame preventivo / Papanicolau) das mulheres
entrevistadas. Em 2019 há campos adicionais: motivo de não ter feito, tempo
até o resultado e encaminhamento. Filtra mulheres com resposta no bloco.
Posições confirmadas contra o dicionário oficial PNS 2019.
"""
import sys

import pandas as pd

from scripts.process.ibge.common.pns_base import (
    PNS_MANUAL_DIR, extrair, decodificar, finalizar_e_publicar, logger,
)
from scripts.common import exit_codes

ARQUIVO_ENTRADA = PNS_MANUAL_DIR / "PNS_2019.txt"
NOME_ARQUIVO_FINAL = "pns_2019_rastreamento_colo_utero.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_ULTIMO_EXAME = {
    "1": "Há menos de 1 ano", "2": "De 1 a menos de 2 anos",
    "3": "De 2 a menos de 3 anos", "4": "Há 3 anos ou mais",
    "5": "Nunca fez", "9": "Ignorado",
}
MAPA_MOTIVO_NAO_FEZ = {
    "01": "Nunca teve relações sexuais", "02": "Não acha necessário",
    "03": "Tem vergonha", "04": "Não foi orientada para fazer o exame",
    "05": "Não sabe quem procurar ou aonde ir", "06": "Tem dificuldades financeiras",
    "07": "Tempo de espera no serviço de saúde era muito grande",
    "08": "Serviço de saúde distante ou dificuldade de transporte",
    "09": "Horário de funcionamento incompatível com trabalho/atividades domésticas",
    "10": "Não conseguiu marcar consulta pelo plano de saúde",
    "11": "Está marcado, mas ainda não realizou",
    "12": "Fez histerectomia (retirada do útero)",
    "13": "Outro", "99": "Ignorado",
}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não", "9": "Ignorado"}
MAPA_SIM_NAO_NSABE = {"1": "Sim", "2": "Não", "3": "Não sabe/Não lembra"}
MAPA_TEMPO_RESULTADO = {
    "1": "Menos de 1 mês depois", "2": "De 1 a menos de 3 meses depois",
    "3": "De 3 a menos de 6 meses depois", "4": "6 meses ou mais depois",
    "5": "Ainda não recebi", "6": "Nunca recebi", "7": "Nunca fui buscar", "9": "Ignorado",
}
MAPA_ENCAMINHAMENTO = {
    "1": "Sim", "2": "Não",
    "3": "Não houve encaminhamento, consultas já eram com especialista",
    "9": "Ignorado",
}

MAPA_MOTIVO_HISTERECTOMIA = {
    "1": "Mioma uterino", "2": "Prolapso do útero", "3": "Endometriose",
    "4": "Câncer ginecológico", "5": "Complicações da gravidez ou parto",
    "6": "Sangramento vaginal anormal", "7": "Outro", "9": "Ignorado",
}
MAPA_SIM_NAO_SIMPLES = {"1": "Sim", "2": "Não", "9": "Ignorado"}

CAMPOS = [
    ("UF", 1, 2),
    ("ESTRATO", 3, 7),
    ("UPA_PNS", 10, 9),
    ("V0006_PNS", 19, 4),
    ("NUM_ORDEM_MORADOR", 104, 2),
    ("SEXO", 108, 1),
    ("IDADE", 117, 3),
    ("COR_RACA", 120, 1),
    ("ULTIMO_EXAME_PREVENTIVO", 1064, 1),
    ("MOTIVO_NAO_FEZ", 1065, 2),
    ("PAGOU_EXAME", 1067, 1),
    ("FEITO_PELO_SUS", 1068, 1),
    ("TEMPO_ATE_RESULTADO", 1069, 1),
    ("ENCAMINHAMENTO_APOS_RESULTADO", 1070, 1),
    ("FEZ_HISTERECTOMIA", 1074, 1),
    ("MOTIVO_HISTERECTOMIA", 1075, 1),
    ("IDADE_HISTERECTOMIA", 1076, 2),
]

ORDEM = [
    "ULTIMO_EXAME_PREVENTIVO", "MOTIVO_NAO_FEZ", "FEITO_PELO_SUS", "PAGOU_EXAME",
    "TEMPO_ATE_RESULTADO", "ENCAMINHAMENTO_APOS_RESULTADO",
    "FEZ_HISTERECTOMIA", "MOTIVO_HISTERECTOMIA", "IDADE_HISTERECTOMIA",
    "SEXO", "IDADE", "COR_RACA", "COD_UF",
    "ESTRATO_AMOSTRAL", "UNIDADE_PRIMARIA_AMOSTRAGEM", "NUM_ORDEM_DOMICILIO",
    "NUM_ORDEM_MORADOR",
]


def main() -> int:
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return exit_codes.ERRO

    logger.info("Lendo microdados PNS 2019 (rastreamento colo do útero)...")
    registros = []
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")
            if extrair(linha, 108, 1) != "2":  # só mulheres
                continue
            if not extrair(linha, 1064, 1):  # sem resposta no bloco
                continue
            registros.append({nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS})

    df = pd.DataFrame(registros)
    logger.info(f"{len(df)} mulher(es) no recorte de rastreamento.")

    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["ULTIMO_EXAME_PREVENTIVO"] = df["ULTIMO_EXAME_PREVENTIVO"].apply(lambda v: decodificar(v, MAPA_ULTIMO_EXAME))
    df["MOTIVO_NAO_FEZ"] = df["MOTIVO_NAO_FEZ"].apply(lambda v: decodificar(v, MAPA_MOTIVO_NAO_FEZ))
    df["PAGOU_EXAME"] = df["PAGOU_EXAME"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["FEITO_PELO_SUS"] = df["FEITO_PELO_SUS"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_NSABE))
    df["TEMPO_ATE_RESULTADO"] = df["TEMPO_ATE_RESULTADO"].apply(lambda v: decodificar(v, MAPA_TEMPO_RESULTADO))
    df["ENCAMINHAMENTO_APOS_RESULTADO"] = df["ENCAMINHAMENTO_APOS_RESULTADO"].apply(lambda v: decodificar(v, MAPA_ENCAMINHAMENTO))
    df["FEZ_HISTERECTOMIA"] = df["FEZ_HISTERECTOMIA"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_SIMPLES))
    df["MOTIVO_HISTERECTOMIA"] = df["MOTIVO_HISTERECTOMIA"].apply(lambda v: decodificar(v, MAPA_MOTIVO_HISTERECTOMIA))

    return finalizar_e_publicar(df, NOME_ARQUIVO_FINAL, ORDEM)


if __name__ == "__main__":
    sys.exit(main())
