"""Portal da Transparência - Convênios Oncológicos (process).

Filtra os convênios federais cujo objeto menciona câncer/oncologia e cruza cada
convenente (por CNPJ) com as instituições habilitadas em oncologia no CNES,
para marcar quais convênios foram firmados com unidades efetivamente
habilitadas.
"""
import re
import sys
import hashlib

import pandas as pd

from scripts.common.paths import LANDING_DIR
from scripts.common.publish import dataframe_para_parquet, bucket_para_dataframe
from scripts.common.bucket_sync import carregar_assinaturas, salvar_assinaturas
from scripts.common import exit_codes

LANDING_PORTAL = LANDING_DIR / "portal_transparencia"
ARQUIVO_CONVENIOS = LANDING_PORTAL / "Convenios.csv"

CNES_PASTA_BUCKET = "cnes"
CNES_ARQUIVO = "cnes_instituicoes_oncologia.parquet"

PASTA_BUCKET = "transparencia"
NOME_ARQUIVO_FINAL = "convenios_cancer.parquet"
CHAVE_FONTE = "convenios_csv"

COLUNA_OBJETO = "OBJETO DO CONVÊNIO"
COLUNA_CNPJ_CONVENENTE = "CÓDIGO CONVENENTE"

PALAVRAS_CHAVE = [
    "cancer", "câncer", "oncologic", "oncológic", "oncologia",
    "quimioterapia", "radioterapia", "mastologia", "mastectomia",
    "hemato-oncologico", "hemato-oncológico", "tumor maligno",
    "carcinoma", "neoplasia", "inca ",
]


def filtrar_por_palavra_chave(df: pd.DataFrame) -> pd.DataFrame:
    objeto = df[COLUNA_OBJETO].astype(str).str.lower()
    padrao = "|".join(re.escape(p) for p in PALAVRAS_CHAVE)
    return df[objeto.str.contains(padrao, case=False, na=False, regex=True)]


def _vazio(serie: pd.Series) -> pd.Series:
    return serie.isna() | (serie.astype(str).str.strip() == "")


def _preparar_cnes() -> pd.DataFrame | None:
    """Carrega o CNES publicado e agrupa por CNPJ efetivo (próprio ou, se
    vazio, da mantenedora), pronto para cruzar sem duplicar convênios."""
    try:
        df_cnes = bucket_para_dataframe(CNES_PASTA_BUCKET, CNES_ARQUIVO)
    except Exception as e:
        print(f"[AVISO] Não foi possível ler o CNES do bucket ({e}). Salvando sem cruzamento.")
        return None

    if "CNPJ_MANTENEDORA" in df_cnes.columns:
        cnpj_proprio_vazio = _vazio(df_cnes["CNPJ"])
        df_cnes["_CNPJ_EFETIVO"] = df_cnes["CNPJ"].where(~cnpj_proprio_vazio, df_cnes["CNPJ_MANTENEDORA"])
        df_cnes["_VIA_MANTENEDORA"] = cnpj_proprio_vazio & ~_vazio(df_cnes["CNPJ_MANTENEDORA"])
    else:
        df_cnes["_CNPJ_EFETIVO"] = df_cnes["CNPJ"]
        df_cnes["_VIA_MANTENEDORA"] = False

    qtd_via_mantenedora = int(df_cnes["_VIA_MANTENEDORA"].sum())
    if qtd_via_mantenedora:
        print(f"  {qtd_via_mantenedora} instituição(ões) sem CNPJ próprio -- cruzando pela mantenedora.")

    df_cnes = df_cnes[~_vazio(df_cnes["_CNPJ_EFETIVO"])]

    return df_cnes.groupby("_CNPJ_EFETIVO", as_index=False).agg(
        CNES_TEM_ONCOLOGIA_PEDIATRICA=("TEM_ONCOLOGIA_PEDIATRICA", "any"),
        CNES_NOME_FANTASIA=("NOME_FANTASIA", "first"),
        CNES_RAZAO_SOCIAL=("RAZAO_SOCIAL", "first"),
        CNES_HABILITACOES=("HABILITACOES_ONCOLOGIA", lambda s: "; ".join(sorted(set(s.dropna())))),
        CNES_QTD_UNIDADES_VINCULADAS=("_CNPJ_EFETIVO", "size"),
        CNES_TOTAL_LEITOS=("TOTAL_LEITOS_CNES", lambda s: s.sum(min_count=1)),
        CNES_COD_UF=("COD_UF", "first"),
        CNES_COD_MUNICIPIO=("COD_MUNICIPIO", "first"),
        CNES_LOGRADOURO=("LOGRADOURO", "first"),
        CNES_LATITUDE=("LATITUDE", "first"),
        CNES_LONGITUDE=("LONGITUDE", "first"),
        CNES_VIA_CNPJ_MANTENEDORA=("_VIA_MANTENEDORA", "any"),
    )


def main() -> int:
    if not ARQUIVO_CONVENIOS.exists():
        print(f"[AVISO] {ARQUIVO_CONVENIOS} não encontrado. Rode o extract primeiro.")
        return exit_codes.SEM_NOVIDADE

    assinatura = hashlib.sha256(ARQUIVO_CONVENIOS.read_bytes()).hexdigest()
    assinaturas = carregar_assinaturas(PASTA_BUCKET)
    if assinaturas.get(CHAVE_FONTE) == assinatura:
        print("[INFO] Convênios inalterados desde a última publicação -- nada a fazer.")
        return exit_codes.SEM_NOVIDADE

    print(f"Lendo {ARQUIVO_CONVENIOS.name}...")
    df = pd.read_csv(ARQUIVO_CONVENIOS, sep=";", encoding="iso-8859-1", dtype=str, quotechar='"')

    if COLUNA_OBJETO not in df.columns:
        print(f"[ERRO] Coluna '{COLUNA_OBJETO}' não encontrada. Disponíveis: {list(df.columns)}")
        return exit_codes.ERRO

    print(f"Total de convênios no arquivo: {len(df)}")
    df_filtrado = filtrar_por_palavra_chave(df).copy()
    print(f"Convênios com menção a câncer/oncologia: {len(df_filtrado)}")

    if df_filtrado.empty:
        print("[AVISO] Nenhum convênio com as palavras-chave -- nada publicado.")
        return exit_codes.SEM_NOVIDADE

    if COLUNA_CNPJ_CONVENENTE not in df_filtrado.columns:
        print(f"[AVISO] Coluna '{COLUNA_CNPJ_CONVENENTE}' não encontrada -- publicando sem cruzamento com CNES.")
    else:
        df_cnes_agrupado = _preparar_cnes()
        if df_cnes_agrupado is not None:
            print("Cruzando convênios com instituições habilitadas em oncologia (por CNPJ)...")
            total_antes = len(df_filtrado)
            df_filtrado = df_filtrado.merge(
                df_cnes_agrupado, left_on=COLUNA_CNPJ_CONVENENTE, right_on="_CNPJ_EFETIVO", how="left"
            )
            assert len(df_filtrado) == total_antes, (
                f"Merge duplicou linhas ({total_antes} -> {len(df_filtrado)})."
            )
            df_filtrado["HABILITADO_CNES_ONCOLOGIA"] = df_filtrado["_CNPJ_EFETIVO"].notna()
            df_filtrado = df_filtrado.drop(columns=["_CNPJ_EFETIVO"])

            total_cruzados = int(df_filtrado["HABILITADO_CNES_ONCOLOGIA"].sum())
            total_via_mant = int((df_filtrado["CNES_VIA_CNPJ_MANTENEDORA"] == True).sum())
            print(f"  {total_cruzados} convênio(s) com convenente habilitado em oncologia "
                  f"({total_via_mant} via CNPJ da mantenedora).")

    ok = dataframe_para_parquet(df_filtrado, PASTA_BUCKET, NOME_ARQUIVO_FINAL)
    if not ok:
        return exit_codes.ERRO

    assinaturas[CHAVE_FONTE] = assinatura
    salvar_assinaturas(PASTA_BUCKET, assinaturas)

    print(f"✔ {len(df_filtrado)} convênio(s) publicado(s) em {NOME_ARQUIVO_FINAL}.")
    return exit_codes.SUCESSO


if __name__ == "__main__":
    sys.exit(main())
