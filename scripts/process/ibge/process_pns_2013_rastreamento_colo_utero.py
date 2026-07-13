"""
PNS 2013 - Rastreamento de Câncer de Colo do Útero (process)

Diferente do recorte de diagnóstico, este NÃO filtra por ter tido
câncer -- é sobre comportamento preventivo de TODAS as mulheres
entrevistadas (rastreamento via exame preventivo/Papanicolau).

Posições confirmadas contra dicionario_PNS_microdados_2013.xls.

Saída: data/raw/raw_pns_2013_rastreamento_colo_utero.parquet
"""
import pandas as pd
from scripts.common.paths import RAW_DIR
from scripts.process.ibge.pns_base import PNS_LANDING_DIR, extrair, decodificar, logger

ARQUIVO_ENTRADA = PNS_LANDING_DIR / "PNS_2013.txt"
ARQUIVO_SAIDA = RAW_DIR / "raw_pns_2013_rastreamento_colo_utero.parquet"

MAPA_SEXO = {"1": "Masculino", "2": "Feminino"}
MAPA_ULTIMO_EXAME = {
    "1": "Menos de 1 ano atrás", "2": "De 1 a menos de 2 anos",
    "3": "De 2 a menos de 3 anos", "4": "3 anos ou mais atrás", "5": "Nunca fez",
}
MAPA_SIM_NAO = {"1": "Sim", "2": "Não"}
MAPA_SIM_NAO_NSABE = {"1": "Sim", "2": "Não", "3": "Não sabe"}

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
]


def main():
    if not ARQUIVO_ENTRADA.exists():
        logger.error(f"Arquivo não encontrado: {ARQUIVO_ENTRADA}")
        return

    logger.info("Iniciando leitura dos microdados PNS 2013 (rastreamento colo do útero)...")
    registros = []

    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8", errors="replace") as f:
        for i, linha in enumerate(f, 1):
            if i % 50_000 == 0:
                logger.info(f"{i} linhas lidas...")

            sexo = extrair(linha, 106, 1)
            if sexo != "2":  # só mulheres (bloco R só se aplica a elas)
                continue

            resposta_exame = extrair(linha, 1044, 1)
            if not resposta_exame:  # "Não aplicável" -- não faz parte da população do bloco R
                continue

            registro = {nome: extrair(linha, pos, tam) for nome, pos, tam in CAMPOS}
            registros.append(registro)

    logger.info("Convertendo para DataFrame...")
    df = pd.DataFrame(registros)

    logger.info("Decodificando categorias...")
    df["SEXO"] = df["SEXO"].apply(lambda v: decodificar(v, MAPA_SEXO))
    df["ULTIMO_EXAME_PREVENTIVO"] = df["ULTIMO_EXAME_PREVENTIVO"].apply(lambda v: decodificar(v, MAPA_ULTIMO_EXAME))
    df["COBERTO_PLANO_SAUDE"] = df["COBERTO_PLANO_SAUDE"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["PAGOU_EXAME"] = df["PAGOU_EXAME"].apply(lambda v: decodificar(v, MAPA_SIM_NAO))
    df["FEITO_PELO_SUS"] = df["FEITO_PELO_SUS"].apply(lambda v: decodificar(v, MAPA_SIM_NAO_NSABE))

    logger.info(f"Total de mulheres no recorte de rastreamento: {len(df)}")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(ARQUIVO_SAIDA, index=False)
    logger.info(f"✔ Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()