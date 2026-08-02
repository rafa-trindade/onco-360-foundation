"""Consulta ao TABNET do DATASUS (SISCAN) e download do CSV gerado.
"""
import re

import pandas as pd

BASE_TABNET = "http://tabnet.datasus.gov.br/cgi/webtabx.exe"
BASE_HOST = "http://tabnet.datasus.gov.br"


def parsear_def(texto_def):
    """Extrai dimensões e medidas de um .def do TABNET.
    """
    dimensoes, medidas = {}, {}
    for linha in texto_def.split("\n"):
        linha = linha.rstrip("\r")
        if not linha or linha[0] in ("B", "H", "R", ";", "O", "A", "<", "P", "C", "X", " "):
            continue
        partes = [p.strip() for p in linha[1:].split(",")]
        rotulo = partes[0]
        valor = "|".join(partes) if len(partes) > 1 else rotulo
        if linha[0] == "L":
            dimensoes[rotulo] = valor
        elif linha[0] == "I":
            medidas[rotulo] = valor
    return dimensoes, medidas


def tabular(def_rel, valor_linha, valor_coluna, valor_incremento,
            dimensoes_todas, anos, session=None):
    """Executa uma tabulação e devolve o texto do CSV gerado.
    """
    import requests

    http = session or requests
    url = f"{BASE_TABNET}?{def_rel}"

    dados = [
        ("Linha", valor_linha),
        ("Coluna", valor_coluna),
        ("Incremento", valor_incremento),
    ]
    for ano in anos:
        dados.append(("PAno competencia", f"{ano}|{ano}|4"))
    for rotulo in dimensoes_todas:
        dados.append((f"X{rotulo}", "TODAS_AS_CATEGORIAS__"))
    dados.append(("nomedef", def_rel))
    dados.append(("grafico", ""))

    resposta = http.post(url, data=dados, timeout=180,
                         headers={"User-Agent": "Mozilla/5.0",
                                  "Content-Type": "application/x-www-form-urlencoded"})
    resposta.encoding = "iso-8859-1"

    link_csv = _extrair_link_csv(resposta.text)
    if link_csv:
        csv = http.get(f"{BASE_HOST}{link_csv}", timeout=180,
                       headers={"User-Agent": "Mozilla/5.0"})
        csv.encoding = "iso-8859-1"
        return ("csv", csv.text)
    return ("html", resposta.text)


def _extrair_link_csv(html):
    """Extrai o caminho do CSV gerado. O link vem relativo ('csv/<visao><id>.csv')
    ou absoluto ('/cgi/csv/...'); normaliza para caminho absoluto sob /cgi/."""
    m = re.search(r'((?:/cgi/)?csv/[^"\'\s>]+\.csv)', html, re.I)
    if not m:
        return None
    caminho = m.group(1)
    if not caminho.startswith("/"):
        caminho = "/cgi/" + caminho
    return caminho


def resultado_para_longo(tipo, conteudo, visao, exame, perfil,
                         dimensao_linha, dimensao_coluna, medida):
    """Normaliza o resultado da tabulação (CSV ou HTML) para formato longo.
    """
    if tipo == "csv":
        bruto = _matriz_de_csv(conteudo)
    else:
        bruto = _matriz_de_html(conteudo)
    return _derreter(bruto, visao, exame, perfil, dimensao_linha, dimensao_coluna, medida)


def _matriz_de_csv(csv_texto):
    from io import StringIO

    if not csv_texto or ";" not in csv_texto:
        return pd.DataFrame()
    linhas = [l for l in csv_texto.splitlines() if l.count(";") >= 1]
    if len(linhas) < 2:
        return pd.DataFrame()
    df = pd.read_csv(StringIO("\n".join(linhas)), sep=";", dtype=str)
    df.columns = [str(c).strip().strip('"') for c in df.columns]
    return df


def _matriz_de_html(html):
    from io import StringIO

    try:
        tabelas = pd.read_html(StringIO(html), decimal=",", thousands=".", flavor="lxml")
    except (ValueError, ImportError):
        return pd.DataFrame()
    for t in tabelas:
        if len(t) > 1 and len(t.columns) >= 2:
            t.columns = [str(c).strip() for c in t.columns]
            return t.astype(str)
    return pd.DataFrame()


def _derreter(matriz, visao, exame, perfil, dimensao_linha, dimensao_coluna, medida):
    colunas = ["VISAO", "EXAME", "PERFIL", "DIMENSAO_LINHA", "CATEGORIA_LINHA",
               "DIMENSAO_COLUNA", "CATEGORIA_COLUNA", "MEDIDA", "QTD"]
    if matriz.empty or len(matriz.columns) < 2:
        return pd.DataFrame(columns=colunas)

    id_col = matriz.columns[0]
    valores = [c for c in matriz.columns
               if c != id_col and str(c).strip().lower() != "total"]

    df = matriz[~matriz[id_col].astype(str).str.strip().str.lower().isin(["total", ""])]
    longo = df.melt(id_vars=id_col, value_vars=valores,
                    var_name="CATEGORIA_COLUNA", value_name="QTD")
    longo = longo.rename(columns={id_col: "CATEGORIA_LINHA"})

    longo["QTD"] = (longo["QTD"].astype(str).str.strip()
                    .str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    longo["QTD"] = pd.to_numeric(longo["QTD"], errors="coerce").fillna(0).astype("int64")
    longo = longo[longo["QTD"] > 0]

    longo["CATEGORIA_LINHA"] = longo["CATEGORIA_LINHA"].astype(str).str.strip()
    longo["VISAO"] = visao
    longo["EXAME"] = exame
    longo["PERFIL"] = perfil
    longo["DIMENSAO_LINHA"] = dimensao_linha
    longo["DIMENSAO_COLUNA"] = dimensao_coluna
    longo["MEDIDA"] = medida
    return longo[colunas]