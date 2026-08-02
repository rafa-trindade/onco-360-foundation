"""Geração do manifesto/índice (CSV) do bucket, publicado na raiz.
"""
import csv
import logging
import sys
from collections import defaultdict

import pyarrow.fs as pafs
import pyarrow.parquet as pq

from zoneinfo import ZoneInfo

from scripts.common import env, exit_codes
from scripts.common.bucket_sync import get_s3_client
from scripts.common.paths import BASE_DIR
from scripts.config.fontes import FONTES

logger = logging.getLogger(__name__)

NOME_ARQUIVO_SAIDA = "onco360-metadados.csv"
CAMINHO_DOCS = BASE_DIR / "docs" / NOME_ARQUIVO_SAIDA

COLUNAS = [
    "ARQUIVO",
    "DIRETORIO",
    "FONTE_RELACIONADA",
    "DESCRICAO",
    "NUM_REGISTROS",
    "NUM_COLUNAS",
    "TAMANHO_BYTES",
    "ULTIMA_ATUALIZACAO",
]

NOMES_POR_ARQUIVO: dict[str, str] = {
    "obitos_cancer_cid9.parquet": "SIM - Óbitos por Câncer, CID-9 (1979-1995)",
    "obitos_cancer_cid10.parquet": "SIM - Óbitos por Câncer, CID-10 (1996-atual_consolidado)",
    "obitos_cancer_prelim.parquet": "SIM - Óbitos por Câncer, atual_preliminar",
    "obitos_cancer_resumo_anual.parquet": "SIM - Óbitos por Câncer (Resumo Anual)",
    "geo_macroregiao.parquet": "Macrorregião de Saúde (geolocalização)",
    "sinonimos_municipio.parquet": "Códigos Municipais antigos -> Códigos Vigentes",
    "cnes_instituicoes_oncologia.parquet": "CNES - Instituições habilitadas em Oncologia",
    "convenios_cancer.parquet": "Convênios Federais em Oncologia (Portal da Transparência)",
    "painel_oncologia.parquet": "Painel de Oncologia (DATASUS)",
    "siasus_quimioterapia.parquet": "SIASUS - APAC de Quimioterapia",
    "siasus_radioterapia.parquet": "SIASUS - APAC de Radioterapia",
    "siasus_medicamentos_oncologicos.parquet": "SIASUS - APAC de Medicamentos Oncológicos",
    "cancer_relacionado_ao_trabalho.parquet": "SINAN - Câncer Relacionado ao Trabalho",
    "cito_colo_residencia.parquet": "SISCAN - Citopatológico do Colo do Útero (Residência)",
    "cito_colo_atendimento.parquet": "SISCAN - Citopatológico do Colo do Útero (Atendimento)",
    "histo_colo_residencia.parquet": "SISCAN - Histopatológico do Colo do Útero (Residência)",
    "histo_colo_atendimento.parquet": "SISCAN - Histopatológico do Colo do Útero (Atendimento)",
    "mamografia_residencia.parquet": "SISCAN - Mamografia (Residência)",
    "mamografia_atendimento.parquet": "SISCAN - Mamografia (Atendimento)",
    "cito_mama_residencia.parquet": "SISCAN - Citopatológico da Mama (Residência)",
    "cito_mama_atendimento.parquet": "SISCAN - Citopatológico da Mama (Atendimento)",
    "histo_mama_residencia.parquet": "SISCAN - Histopatológico da Mama (Residência)",
    "histo_mama_atendimento.parquet": "SISCAN - Histopatológico da Mama (Atendimento)",
    "pns_2013_diagnostico_cancer.parquet": "PNS 2013 - Diagnóstico e Tipo de Câncer",
    "pns_2019_diagnostico_cancer.parquet": "PNS 2019 - Diagnóstico e Tipo de Câncer",
    "pns_2013_rastreamento_colo_utero.parquet": "PNS 2013 - Rastreamento de Colo do Útero",
    "pns_2019_rastreamento_colo_utero.parquet": "PNS 2019 - Rastreamento de Colo do Útero",
    "pns_2013_rastreamento_mama.parquet": "PNS 2013 - Rastreamento de Mama",
    "pns_2019_rastreamento_mama.parquet": "PNS 2019 - Rastreamento de Mama",
    "cancer_populacional.parquet": "INCA - Registro de Câncer de Base Populacional (RCBP)",
    "registro_hospitalar.parquet": "INCA - Registro Hospitalar de Câncer (RHC)",
}

DESCRICOES_POR_ARQUIVO: dict[str, str] = {
    "obitos_cancer_cid9.parquet":
        "Óbitos por neoplasia maligna (CAUSABAS 140-208), era CID-9 (1979-1995). ",
    "obitos_cancer_cid10.parquet":
        "Óbitos por neoplasia maligna (CAUSABAS C00-C97), CID-10 consolidado (1996-atual). ",
    "obitos_cancer_prelim.parquet":
        "Óbitos por câncer (CID-10) dos dados ainda não homologados do ano corrente. ",
    "obitos_cancer_resumo_anual.parquet":
        "Resumo anual por fonte (CID9/CID10/PRELIM) ",
    "geo_macroregiao.parquet":
        "Referência geográfica por município. ",
    "sinonimos_municipio.parquet":
        "De-para de código municipal antigo -> código vigente (derivado do MUNSINON/CADMUN). ",
    "cnes_instituicoes_oncologia.parquet":
        "Instituições de saúde habilitadas em alta complexidade em oncologia no SUS, uma linha por instituição, com habilitações, tipo, esfera, leitos e localização. ",
    "convenios_cancer.parquet":
        "Convênios federais cujo objeto menciona câncer/oncologia (Portal da Transparência), cruzados por CNPJ com as instituições habilitadas no CNES. ",
    "painel_oncologia.parquet":
        "Painel de Oncologia (DATASUS): casos oncológicos do SUS desde 2013, com diagnóstico, estadiamento e primeiro tratamento. ",
    "siasus_quimioterapia.parquet":
        "SIASUS: APAC de quimioterapia do SUS desde 2008, com topografia, estadiamento, linfonodos, grau histopatológico e esquema terapêutico. ",
    "siasus_radioterapia.parquet":
        "SIASUS: APAC de radioterapia do SUS desde 2008, com topografia, estadiamento e finalidade (radical/adjuvante/paliativa). ",
    "siasus_medicamentos_oncologicos.parquet":
        "SIASUS: APAC de medicamentos de alto custo com CID principal de neoplasia (C00-D48), desde 2008. ",
    "cancer_relacionado_ao_trabalho.parquet":
        "SINAN: notificações de câncer relacionado ao trabalho (agravo C80), com ocupação, situação no mercado de trabalho, exposição ocupacional a agentes cancerígenos (asbesto, sílica, benzeno, radiações, antineoplásicos, etc.) e evolução do caso. ",
    "cito_colo_residencia.parquet":
        "SISCAN: exames citopatológicos do colo do útero agregados por local de residência, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "cito_colo_atendimento.parquet":
        "SISCAN: exames citopatológicos do colo do útero agregados por local de atendimento, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "histo_colo_residencia.parquet":
        "SISCAN: exames histopatológicos do colo do útero agregados por local de residência, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "histo_colo_atendimento.parquet":
        "SISCAN: exames histopatológicos do colo do útero agregados por local de atendimento, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "mamografia_residencia.parquet":
        "SISCAN: exames de mamografia agregados por local de residência, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "mamografia_atendimento.parquet":
        "SISCAN: exames de mamografia agregados por local de atendimento, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "cito_mama_residencia.parquet":
        "SISCAN: exames citopatológicos da mama agregados por local de residência, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "cito_mama_atendimento.parquet":
        "SISCAN: exames citopatológicos da mama agregados por local de atendimento, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "histo_mama_residencia.parquet":
        "SISCAN: exames histopatológicos da mama agregados por local de residência, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "histo_mama_atendimento.parquet":
        "SISCAN: exames histopatológicos da mama agregados por local de atendimento, com medidas e resultados do exame. Dados do TABNET desde 2013.",
    "pns_2013_diagnostico_cancer.parquet":
        "PNS 2013 (IBGE): pessoas com diagnóstico de câncer autorreferido, tipo (categórico), idade no diagnóstico e limitação. ",
    "pns_2019_diagnostico_cancer.parquet":
        "PNS 2019 (IBGE): pessoas com diagnóstico de câncer autorreferido, tipo em flags binárias (múltiplos) e limitação. ",
    "pns_2013_rastreamento_colo_utero.parquet":
        "PNS 2013 (IBGE): rastreamento de colo do útero (exame preventivo) nas mulheres entrevistadas, com resultado e histerectomia. ",
    "pns_2019_rastreamento_colo_utero.parquet":
        "PNS 2019 (IBGE): rastreamento de colo do útero, com motivo, tempo até resultado, encaminhamento e histerectomia. ",
    "pns_2013_rastreamento_mama.parquet":
        "PNS 2013 (IBGE): rastreamento de mama (exame clínico das mamas e mamografia) nas mulheres entrevistadas. ",
    "pns_2019_rastreamento_mama.parquet":
        "PNS 2019 (IBGE): rastreamento de mama (exame clínico das mamas e mamografia), com resultado e encaminhamento. ",
    "cancer_populacional.parquet":
        "INCA - Registro de Câncer de Base Populacional (RCBP): estimativas de incidência por população.",
    "registro_hospitalar.parquet":
        "INCA - Registro Hospitalar de Câncer (RHC): perfil de atendimento hospitalar por unidade.",
}


def _e_arquivo_de_controle(nome: str) -> bool:
    return (
        nome == NOME_ARQUIVO_SAIDA
        or nome == "_manifest.json"
        or nome.startswith("_checkpoint_")
    )


def _fontes_por_pasta() -> dict[str, dict[str, str]]:
    nomes = defaultdict(list)
    descricoes = defaultdict(list)
    for f in FONTES:
        nomes[f.pasta_bucket].append(f.nome)
        descricoes[f.pasta_bucket].append(f.descricao)
    return {
        pasta: {
            "nomes": " | ".join(nomes[pasta]),
            "descricoes": " | ".join(descricoes[pasta]),
        }
        for pasta in nomes
    }


def _montar_s3_filesystem() -> pafs.S3FileSystem:
    endpoint = env.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    esquema = "https" if env.MINIO_ENDPOINT.startswith("https://") else "http"
    return pafs.S3FileSystem(
        endpoint_override=endpoint,
        access_key=env.MINIO_ROOT_USER,
        secret_key=env.MINIO_ROOT_PASSWORD,
        scheme=esquema,
    )


def _metadados_parquet(s3_fs: pafs.S3FileSystem, bucket: str, key: str) -> tuple[int | None, int | None]:
    try:
        pf = pq.ParquetFile(f"{bucket}/{key}", filesystem=s3_fs)
        return pf.metadata.num_rows, pf.metadata.num_columns
    except Exception as e:
        logger.warning(f"Não foi possível ler metadados de {key}: {e}")
        return None, None


def gerar_linhas(s3_client, s3_fs, bucket: str, infos: dict[str, dict[str, str]]) -> list[dict]:
    paginator = s3_client.get_paginator("list_objects_v2")
    linhas = []

    for pagina in paginator.paginate(Bucket=bucket):
        for obj in pagina.get("Contents", []):
            key = obj["Key"]
            nome_arquivo = key.rsplit("/", 1)[-1]
            if _e_arquivo_de_controle(nome_arquivo):
                continue

            pasta = key.split("/")[0] if "/" in key else ""

            num_registros = num_colunas = None
            if key.endswith(".parquet"):
                num_registros, num_colunas = _metadados_parquet(s3_fs, bucket, key)

            info_pasta = infos.get(pasta, {"nomes": "(não mapeado em fontes.py)", "descricoes": ""})

            descricao = DESCRICOES_POR_ARQUIVO.get(nome_arquivo, info_pasta["descricoes"])
            
            # --- NOVA LÓGICA ---
            # Busca no dicionário específico. Se não existir, extrai apenas o 
            # primeiro nome da fonte para não jogar "um monte" de nomes no CSV.
            nome_fonte = NOMES_POR_ARQUIVO.get(nome_arquivo, info_pasta["nomes"].split(" | ")[0])

            linhas.append({
                "ARQUIVO": nome_arquivo,
                "DIRETORIO": pasta,
                "FONTE_RELACIONADA": nome_fonte,
                "DESCRICAO": descricao,
                "NUM_REGISTROS": num_registros,
                "NUM_COLUNAS": num_colunas,
                "TAMANHO_BYTES": obj["Size"],
                "ULTIMA_ATUALIZACAO": obj["LastModified"].astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d-%m-%Y %H:%M:%S"),
            })

    linhas.sort(key=lambda r: r["DIRETORIO"])
    return linhas


def _escrever_csv(caminho, linhas):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS)
        writer.writeheader()
        writer.writerows(linhas)


def main() -> int:
    faltando = env.validar_minio()
    if faltando:
        logger.error(f"Variáveis do MinIO ausentes: {', '.join(faltando)}")
        return exit_codes.ERRO

    nomes = _fontes_por_pasta()
    s3_client = get_s3_client()
    s3_fs = _montar_s3_filesystem()

    logger.info(f"Catalogando {env.MINIO_BUCKET}...")
    linhas = gerar_linhas(s3_client, s3_fs, env.MINIO_BUCKET, nomes)

    if not linhas:
        logger.warning("Nenhum arquivo encontrado no bucket.")
        return exit_codes.SEM_NOVIDADE

    _escrever_csv(CAMINHO_DOCS, linhas)

    s3_client.upload_file(str(CAMINHO_DOCS), env.MINIO_BUCKET, NOME_ARQUIVO_SAIDA)

    nao_mapeadas = sorted({
        l["DIRETORIO"] for l in linhas
        if l["FONTE_RELACIONADA"].startswith("(não mapeado") # <--- Alterado aqui
    })
    if nao_mapeadas:
        logger.warning(f"Pasta(s) sem Fonte em fontes.py: {nao_mapeadas}")

    sem_metadados = [l["ARQUIVO"] for l in linhas
                     if l["ARQUIVO"].endswith(".parquet") and l["NUM_REGISTROS"] is None]
    if sem_metadados:
        logger.warning(f"Parquet(s) sem metadados legíveis: {sem_metadados}")

    total = sum(l["NUM_REGISTROS"] or 0 for l in linhas)
    logger.info(
        f"{NOME_ARQUIVO_SAIDA} publicado na raiz do bucket: "
        f"{len(linhas)} arquivo(s), {total:,} registro(s) no total.".replace(",", ".")
    )
    return exit_codes.SUCESSO


if __name__ == "__main__":
    sys.exit(main())
