"""SISCAN - Rastreamento de Câncer de Colo e Mama (process).

Tabula, via TABNET, os exames de citopatológico, mamografia e histopatológico.
"""
import sys
import time
import re
from datetime import datetime

import pandas as pd
import requests

from scripts.common import exit_codes
from scripts.common.publish import dataframe_para_parquet, bucket_para_dataframe
from scripts.common.bucket_sync import carregar_assinaturas, salvar_assinaturas
from scripts.process.datasus.common.siscan import tabnet
from scripts.process.datasus.common.siscan.visoes import VISOES, ANOS

PASTA_BUCKET = "datasus_siscan"
HOST = "http://tabnet.datasus.gov.br"
PAUSA_SEGUNDOS = 3


def _anos_recentes():
    atual = datetime.now().year
    return [str(atual), str(atual - 1)]


def _mesclar_incremental(visao_id, df_novo, anos_reprocessados):

    anos_set = {str(a) for a in anos_reprocessados}
    try:
        df_antigo = bucket_para_dataframe(PASTA_BUCKET, f"{visao_id}.parquet")
    except Exception:
        df_antigo = None

    if df_antigo is None or df_antigo.empty:
        return df_novo

    df_antigo = df_antigo[~df_antigo["ANO"].astype(str).isin(anos_set)]
    return pd.concat([df_antigo, df_novo], ignore_index=True)


DATA_INDISPONIVEL = "Desconhecida"


def _obter_data_atualizacao(session, def_rel, tentativas=3):
    """Raspa a data de atualização do rodapé do HTML da visão no DATASUS.
    """
    url = f"{HOST}/cgi/dhdat.exe?{def_rel}"
    for tentativa in range(1, tentativas + 1):
        try:
            r = session.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            r.encoding = "utf-8"
            match = re.search(r"atualiza[^<]*dados.*?(\d{2}/\d{2}/\d{4})", r.text, re.I | re.S)
            if match:
                return match.group(1)
        except Exception:
            pass
        if tentativa < tentativas:
            time.sleep(PAUSA_SEGUNDOS)
    return DATA_INDISPONIVEL

def _baixar_def(session, def_rel):
    r = session.get(f"{HOST}/cgi/{def_rel}", timeout=90,
                    headers={"User-Agent": "Mozilla/5.0"})
    r.encoding = "iso-8859-1"
    return r.text

def _tabular_visao(session, visao_id, cfg, anos):
    dims, medidas = tabnet.parsear_def(_baixar_def(session, cfg["def_rel"]))

    override = cfg.get("submissao", {})
    dims = {**dims, **override.get("dimensoes", {})}
    medidas = {**medidas, **override.get("medidas", {})}

    partes = []

    for dim_linha, dim_coluna in cfg["cruzamentos"]:
        if dim_linha not in dims or dim_coluna not in dims:
            continue

        for medida in cfg["medidas"]:
            if medida not in medidas:
                continue

            for ano in anos:
                print(f"    -> Tabulando {dim_linha} x {dim_coluna} | Medida: {medida} | Ano: {ano}")

                tipo, conteudo = tabnet.tabular(
                    cfg["def_rel"],
                    dims[dim_linha],
                    dims[dim_coluna],
                    medidas[medida],
                    list(dims),
                    [ano],
                    session=session,
                )

                longo = tabnet.resultado_para_longo(
                    tipo, conteudo, visao_id, cfg["exame"], cfg["perfil"],
                    dim_linha, dim_coluna, medida,
                )

                if not longo.empty:
                    longo["ANO"] = ano
                    partes.append(longo)

                time.sleep(PAUSA_SEGUNDOS)

    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()

def main() -> int:
    session = requests.Session()
    assinaturas = carregar_assinaturas(PASTA_BUCKET)
    falhas = 0
    processadas = 0

    for visao_id, cfg in VISOES.items():
        print(f"\n[{visao_id}] Iniciando verificação...")

        data_site = _obter_data_atualizacao(session, cfg["def_rel"])
        print(f"  Última atualização no DATASUS: {data_site}")

        ja_registrada = visao_id in assinaturas
        if ja_registrada and assinaturas.get(visao_id) == data_site and data_site != DATA_INDISPONIVEL:
            print(f"  >> SEM NOVIDADE: '{visao_id}' já está atualizado ({data_site}).")
            continue

        if ja_registrada:
            anos_processar = _anos_recentes()
            print(f"  Atualização detectada. Reprocessando anos recentes: {anos_processar}")
        else:
            anos_processar = list(ANOS)
            print(f"  Primeira carga. Processando série completa ({ANOS[0]}–{ANOS[-1]}).")

        try:
            df_novo = _tabular_visao(session, visao_id, cfg, anos_processar)
        except Exception as e:
            print(f"  [AVISO] falha na visão {visao_id}: {e}")
            falhas += 1
            continue

        print(f"  {len(df_novo)} registros processados.")
        if df_novo.empty:
            print(f"  [AVISO] visão {visao_id} não retornou dados; assinatura não atualizada.")
            falhas += 1
            continue

        if ja_registrada:
            df_final = _mesclar_incremental(visao_id, df_novo, anos_processar)
            print(f"  Após mesclar com o histórico: {len(df_final)} registros.")
        else:
            df_final = df_novo

        nome_arquivo = f"{visao_id}.parquet"
        if not dataframe_para_parquet(df_final, PASTA_BUCKET, nome_arquivo):
            falhas += 1
            continue
        print(f"✔ Publicado com sucesso em: {nome_arquivo}")
        processadas += 1

        if data_site != DATA_INDISPONIVEL:
            assinaturas[visao_id] = data_site
            salvar_assinaturas(PASTA_BUCKET, assinaturas)
        else:
            print(f"  [NOTA] data indisponível; '{visao_id}' será reverificado na próxima execução.")

    if processadas == 0 and falhas > 0:
        print("\n[ERRO] Nenhuma visão foi processada com sucesso.")
        return exit_codes.ERRO
    if processadas == 0:
        print("\nNenhuma novidade: todas as visões já estavam atualizadas.")
        return exit_codes.SEM_NOVIDADE

    print(f"\nProcessamento do SISCAN concluído! {processadas} visão(ões) atualizada(s).")
    return exit_codes.SUCESSO


if __name__ == "__main__":
    sys.exit(main())