"""
PNS 2019 - Rastreamento de Câncer de Colo do Útero (process)

Bloco mais rico que 2013: além de quando foi o último exame, traz o
motivo de NÃO ter feito, quanto tempo até receber o resultado, e se
houve encaminhamento após o resultado -- acompanha o desfecho, não só
a realização do exame.

Posições confirmadas contra dicionario_PNS_microdados_2019.xls.

Saída: data/raw/raw_pns_2019_rastreamento_colo_utero.parquet
"""
import pandas as pd
from scripts.common.paths import RAW_DIR
from scripts.process.ibge.pns_base import PNS_LANDING_DIR, extrair, decodificar, logger

ARQUIVO_ENTRADA = PNS_LANDING_DIR / "PNS_2019.txt"
ARQUIVO_SAIDA = RAW_DIR / "raw_pns_2019_rastreamento_colo_utero.parquet"

MAPA_SEXO = {"1": "Homem", "2": "Mulher"}
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
    "3": "Não houve encaminhamento -- consultas já eram com especialista",
    "9": "Ignorado",
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
    ("ULTIMO_EXAME_PREVENTIVO", 1064, 1),
    ("MOTIVO_NAO_FEZ", 1065, 2),
    ("PAGOU_EXAME", 1067, 1),
    ("FEITO_PELO_SUS", 1068, 1),
    ("TEMPO_ATE_RESULTADO", 1069, 1),
    ("ENCAMINHAMENTO_APOS_RESULTADO", 1070, 1),
]


def main():
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return

    logger.info("Iniciando leitura dos microdados PNS 2019 (rastreamento colo do útero)...")
    registros = []

    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")

            sexo = extrair(linha, 108, 1)
            if sexo != "2":
                continue

            resposta_exame = extrair(linha, 1064, 1)
            if not resposta_exame:
                continue

            registro = {nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS}
            registros.append(registro)

    logger.info("Convertendo para DataFrame...")
    df = pd.DataFrame(registros)

    logger.info("Decodificando categorias...")
    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["ULTIMO_EXAME_PREVENTIVO"] = df["ULTIMO_EXAME_PREVENTIVO"].apply(lambda v: decodificar(v, MAPA_ULTIMO_EXAME))
    df["MOTIVO_NAO_FEZ"] = df["MOTIVO_NAO_FEZ"].apply(lambda v: decodificar(v, MAPA_MOTIVO_NAO_FEZ))
    df["PAGOU_EXAME"] = df["PAGOU_EXAME"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["FEITO_PELO_SUS"] = df["FEITO_PELO_SUS"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_NSABE))
    df["TEMPO_ATE_RESULTADO"] = df["TEMPO_ATE_RESULTADO"].apply(lambda v: decodificar(v, MAPA_TEMPO_RESULTADO))
    df["ENCAMINHAMENTO_APOS_RESULTADO"] = df["ENCAMINHAMENTO_APOS_RESULTADO"].apply(lambda v: decodificar(v, MAPA_ENCAMINHAMENTO))

    logger.info(f"Total de mulheres no recorte de rastreamento: {len(df)}")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ARQUIVO_SAIDA, index=False)
    logger.info(f"✔ Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()