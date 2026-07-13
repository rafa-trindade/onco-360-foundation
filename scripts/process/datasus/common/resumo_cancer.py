"""
Resumo anual único de óbitos por câncer, compartilhado entre CID-9,
CID-10 consolidado e CID-10 preliminar -- os três têm exatamente as
mesmas colunas de resumo (ano, total de óbitos, total de câncer,
proporção), então em vez de 3 arquivos separados, mantemos 1 só com
upsert por ano.

Upsert por ano (não por fonte+ano): quando o CID-10 consolidado processa
um ano que antes só existia como preliminar, a linha do preliminar é
SUBSTITUÍDA pela do consolidado -- é o comportamento certo, já que o
dado definitivo deve prevalecer sobre o preliminar pro mesmo ano.
"""
import re
import pandas as pd
from pathlib import Path

COLUNAS_RESUMO = ["ano", "fonte", "arquivo", "total_obitos", "total_cancer", "proporcao_cancer", "erro"]


def extrair_ano_cid9(nome_arquivo: str) -> int | None:
    m = re.search(r"DORBR(\d{2,4})\.dbc", nome_arquivo, re.IGNORECASE)
    if not m:
        return None
    ano_str = m.group(1)
    ano_int = int(ano_str)
    if len(ano_str) == 2:
        return 1900 + ano_int if ano_int >= 79 else 2000 + ano_int
    return ano_int


def extrair_ano_cid10(nome_arquivo: str) -> int | None:
    m = re.search(r"DOBR(\d{4})\.dbc", nome_arquivo, re.IGNORECASE)
    return int(m.group(1)) if m else None


def atualizar_resumo_anual(
    detalhes: list[dict],
    fonte: str,
    extrair_ano_fn,
    caminho_csv: Path,
):
    """
    Constrói as linhas de resumo a partir de `detalhes` (retornado por
    processar_diretorio_dbc_filtrado) e faz upsert por ano no CSV
    consolidado -- remove linhas existentes dos anos que estão sendo
    atualizados agora, e adiciona as novas no lugar.
    """
    linhas_novas = []
    for d in detalhes:
        ano = extrair_ano_fn(d["arquivo"])
        if d.get("mantidos") is None:
            linhas_novas.append({
                "ano": ano, "fonte": fonte, "arquivo": d["arquivo"],
                "total_obitos": None, "total_cancer": None,
                "proporcao_cancer": None, "erro": d.get("erro"),
            })
            continue

        proporcao = d["mantidos"] / d["total"] if d["total"] else None
        linhas_novas.append({
            "ano": ano, "fonte": fonte, "arquivo": d["arquivo"],
            "total_obitos": d["total"], "total_cancer": d["mantidos"],
            "proporcao_cancer": round(proporcao, 4) if proporcao is not None else None,
            "erro": None,
        })

    df_novo = pd.DataFrame(linhas_novas, columns=COLUNAS_RESUMO)

    if caminho_csv.exists():
        df_existente = pd.read_csv(caminho_csv)
        anos_atualizados = set(df_novo["ano"].dropna())
        df_existente = df_existente[~df_existente["ano"].isin(anos_atualizados)]
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    df_final = df_final.sort_values(["ano", "fonte"])
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(caminho_csv, index=False, encoding="utf-8-sig")
    print(f"✔ Resumo anual atualizado: {caminho_csv.name} "
          f"({len(df_novo)} ano(s) de '{fonte}' upsertados, {len(df_final)} linha(s) no total)")

    falhas = df_novo[df_novo["erro"].notna()]
    if not falhas.empty:
        print(f"[AVISO] {len(falhas)} arquivo(s) com falha nesta execução -- confira a coluna 'erro':")
        print(falhas[["ano", "arquivo", "erro"]].to_string(index=False))