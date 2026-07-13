"""
Portal da Transparência - Convênios com foco em câncer (process)

Filtra os convênios cujo OBJETO (finalidade) menciona câncer/oncologia,
e cruza com as instituições habilitadas em oncologia do CNES para
confirmar quando o convenente é uma instituição de saúde habilitada e
trazer o sinalizador adulto/pediátrico nesses casos.

Cruzamento por CNPJ com fallback pra mantenedora: tenta primeiro o
CNPJ do próprio estabelecimento (NU_CNPJ); se vazio, cai pro CNPJ da
entidade mantenedora (NU_CNPJ_MANTENEDORA) -- comum em unidades de
redes/hospitais universitários (ex: EBSERH) que só têm CNPJ próprio
registrado na mantenedora, não na unidade. Sem isso, instituições como
a Fundação HEMOPE (CNES 0000809, CNPJ próprio vazio) nunca cruzariam
com convênio nenhum. Fica marcado em CNES_VIA_CNPJ_MANTENEDORA quando
o cruzamento usou esse fallback (o convênio foi pra mantenedora, não
necessariamente exclusivo dessa unidade -- vale conferir manualmente
se `CNES_QTD_UNIDADES_VINCULADAS` > 1).

Encoding: os CSVs do Portal da Transparência vêm em ISO-8859-1
(Latin-1), não UTF-8 -- confirmado contra um arquivo real.

Saída: data/raw/raw_convenios_cancer.parquet
"""
import re
import pandas as pd
from pathlib import Path
from scripts.common.paths import LANDING_DIR, RAW_DIR

LANDING_PORTAL = LANDING_DIR / "portal_transparencia"
CNES_ONCOLOGIA_PATH = RAW_DIR / "raw_cnes_oncologia_instituicoes.parquet"
ARQUIVO_SAIDA = RAW_DIR / "raw_convenios_cancer.parquet"

COLUNA_OBJETO = "OBJETO DO CONVÊNIO"
COLUNA_CNPJ_CONVENENTE = "CÓDIGO CONVENENTE"

PALAVRAS_CHAVE = [
    "cancer", "câncer", "oncologic", "oncológic", "oncologia",
    "quimioterapia", "radioterapia", "mastologia", "mastectomia",
    "hemato-oncologico", "hemato-oncológico", "tumor maligno",
    "carcinoma", "neoplasia", "inca ",
]


def _achar_arquivo_convenios() -> Path | None:
    """Nome fixo na Landing (Convenios.csv, sem prefixo de data --
    ver _nome_padronizado em fetch_convenios_download_dados.py)."""
    caminho = LANDING_PORTAL / "Convenios.csv"
    return caminho if caminho.exists() else None


def filtrar_por_palavra_chave(df: pd.DataFrame) -> pd.DataFrame:
    objeto = df[COLUNA_OBJETO].astype(str).str.lower()
    padrao = "|".join(re.escape(p) for p in PALAVRAS_CHAVE)
    mascara = objeto.str.contains(padrao, case=False, na=False, regex=True)
    return df[mascara]


def main():
    caminho_convenios = _achar_arquivo_convenios()
    if caminho_convenios is None:
        print(f"[AVISO] Nenhum arquivo de Convênios encontrado em {LANDING_PORTAL}. Rode o extract primeiro.")
        return

    print(f"Lendo {caminho_convenios.name}...")
    df = pd.read_csv(caminho_convenios, sep=";", encoding="iso-8859-1", dtype=str, quotechar='"')

    if COLUNA_OBJETO not in df.columns:
        print(f"[AVISO] Coluna '{COLUNA_OBJETO}' não encontrada. Colunas disponíveis: {list(df.columns)}")
        print("        Ajuste COLUNA_OBJETO neste script com o nome correto.")
        return

    print(f"Total de convênios no arquivo: {len(df)}")
    df_filtrado = filtrar_por_palavra_chave(df)
    print(f"Convênios com menção a câncer/oncologia no objeto: {len(df_filtrado)}")

    if df_filtrado.empty:
        print("[AVISO] Nenhum convênio encontrado com as palavras-chave atuais -- nada foi salvo.")
        return

    df_filtrado = df_filtrado.copy()

    if COLUNA_CNPJ_CONVENENTE not in df_filtrado.columns:
        print(f"[AVISO] Coluna '{COLUNA_CNPJ_CONVENENTE}' não encontrada -- salvando sem cruzamento com CNES.")
    elif CNES_ONCOLOGIA_PATH.exists():
        print("Cruzando com CNES - Instituições com Habilitação em Oncologia (por CNPJ)...")
        colunas_desejadas = [
            "NU_CNPJ", "NU_CNPJ_MANTENEDORA", "PEDIATRICO", "NO_FANTASIA", "NO_RAZAO_SOCIAL",
            "HABILITACOES_ONCOLOGIA", "QTD_HABILITACOES_ONCOLOGIA",
            "TOTAL_LEITOS_CNES", "CO_UF", "CO_IBGE",
            "NO_LOGRADOURO", "NU_ENDERECO", "NO_BAIRRO", "CO_CEP",
            "NU_LATITUDE", "NU_LONGITUDE", "NU_TELEFONE",
        ]
        df_cnes_completo = pd.read_parquet(CNES_ONCOLOGIA_PATH)
        colunas_disponiveis = [c for c in colunas_desejadas if c in df_cnes_completo.columns]
        df_cnes = df_cnes_completo[colunas_disponiveis].copy()

        def _vazio(serie: pd.Series) -> pd.Series:
            return serie.isna() | (serie.astype(str).str.strip() == "")

        # CNPJ efetivo pro cruzamento: usa o do próprio estabelecimento;
        # se vazio, cai pro da mantenedora (ver docstring do módulo).
        if "NU_CNPJ_MANTENEDORA" in df_cnes.columns:
            cnpj_proprio_vazio = _vazio(df_cnes["NU_CNPJ"])
            df_cnes["_CNPJ_EFETIVO"] = df_cnes["NU_CNPJ"].where(~cnpj_proprio_vazio, df_cnes["NU_CNPJ_MANTENEDORA"])
            df_cnes["_VIA_MANTENEDORA"] = cnpj_proprio_vazio & ~_vazio(df_cnes["NU_CNPJ_MANTENEDORA"])
        else:
            df_cnes["_CNPJ_EFETIVO"] = df_cnes["NU_CNPJ"]
            df_cnes["_VIA_MANTENEDORA"] = False

        qtd_via_mantenedora = int(df_cnes["_VIA_MANTENEDORA"].sum())
        if qtd_via_mantenedora:
            print(f"  {qtd_via_mantenedora} instituição(ões) sem CNPJ próprio -- cruzando pelo CNPJ da mantenedora.")

        df_cnes = df_cnes[~_vazio(df_cnes["_CNPJ_EFETIVO"])]  # sem CNPJ nenhum não tem como cruzar

        # Um mesmo CNPJ efetivo pode ter mais de um CNES vinculado (ex: rede
        # hospitalar com várias unidades sob o mesmo CNPJ, ou várias
        # unidades caindo na mesma mantenedora) -- agrupa ANTES de cruzar,
        # senão o merge duplica o convênio.
        df_cnes_agrupado = df_cnes.groupby("_CNPJ_EFETIVO", as_index=False).agg(
            PEDIATRICO=("PEDIATRICO", "any"),  # True se QUALQUER unidade daquele CNPJ for pediátrica
            CNES_NOME_FANTASIA=("NO_FANTASIA", "first"),
            CNES_RAZAO_SOCIAL=("NO_RAZAO_SOCIAL", "first"),
            CNES_HABILITACOES=("HABILITACOES_ONCOLOGIA", lambda s: "; ".join(sorted(set(s.dropna())))) if "HABILITACOES_ONCOLOGIA" in df_cnes.columns else ("_CNPJ_EFETIVO", "size"),
            CNES_QTD_UNIDADES_VINCULADAS=("_CNPJ_EFETIVO", "size"),
            CNES_TOTAL_LEITOS=("TOTAL_LEITOS_CNES", lambda s: s.sum(min_count=1)) if "TOTAL_LEITOS_CNES" in df_cnes.columns else ("_CNPJ_EFETIVO", "size"),
            CNES_UF=("CO_UF", "first") if "CO_UF" in df_cnes.columns else ("_CNPJ_EFETIVO", "first"),
            CNES_MUNICIPIO_IBGE=("CO_IBGE", "first") if "CO_IBGE" in df_cnes.columns else ("_CNPJ_EFETIVO", "first"),
            CNES_LOGRADOURO=("NO_LOGRADOURO", "first") if "NO_LOGRADOURO" in df_cnes.columns else ("_CNPJ_EFETIVO", "first"),
            CNES_LATITUDE=("NU_LATITUDE", "first") if "NU_LATITUDE" in df_cnes.columns else ("_CNPJ_EFETIVO", "first"),
            CNES_LONGITUDE=("NU_LONGITUDE", "first") if "NU_LONGITUDE" in df_cnes.columns else ("_CNPJ_EFETIVO", "first"),
            CNES_VIA_CNPJ_MANTENEDORA=("_VIA_MANTENEDORA", "any"),
        )

        total_antes = len(df_filtrado)
        df_filtrado = df_filtrado.merge(
            df_cnes_agrupado, left_on=COLUNA_CNPJ_CONVENENTE, right_on="_CNPJ_EFETIVO", how="left"
        )
        assert len(df_filtrado) == total_antes, (
            f"Merge duplicou linhas ({total_antes} -> {len(df_filtrado)}) -- CNES ainda tem CNPJ efetivo repetido."
        )

        df_filtrado["HABILITADO_CNES_ONCOLOGIA"] = df_filtrado["_CNPJ_EFETIVO"].notna()
        total_cruzados = int(df_filtrado["HABILITADO_CNES_ONCOLOGIA"].sum())
        total_via_mantenedora = int((df_filtrado["CNES_VIA_CNPJ_MANTENEDORA"] == True).sum())
        print(f"  {total_cruzados} convênio(s) cujo convenente é uma instituição habilitada em oncologia no CNES "
              f"({total_via_mantenedora} via CNPJ da mantenedora).")
    else:
        print(f"[AVISO] {CNES_ONCOLOGIA_PATH.name} não encontrado -- salvando sem cruzamento com CNES. "
              f"Rode o extract/process do CNES Habilitação primeiro pra ter essa informação.")

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_filtrado.to_parquet(ARQUIVO_SAIDA, index=False)
    print(f"✔ {len(df_filtrado)} convênio(s) salvo(s) em {ARQUIVO_SAIDA.name}")

if __name__ == "__main__":
    main()