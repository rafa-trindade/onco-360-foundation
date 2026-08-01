"""CNES - Instituições com habilitação em oncologia.

Uma linha por INSTITUIÇÃO (não por habilitação): uma mesma instituição pode ter
mais de uma habilitação em oncologia (ex: UNACON adulto + pediátrica), e um
desenho por habilitação duplicaria a instituição em cruzamentos posteriores.

Junta três fontes: habilitação (HB, .dbc do FTP DATASUS, filtrada para os
códigos de oncologia), cadastro de estabelecimentos (CSV, dados abertos) e
leitos (LT, .dbc, opcional). O código CNES é normalizado (7 dígitos, zero à
esquerda) nos dois lados antes de cruzar. Instituições sem correspondência no
cadastro ficam com ENCONTRADO_NO_CNES=False, nunca são descartadas.
"""
import pandas as pd
import hashlib

from scripts.common.paths import LANDING_DIR, PROCESSED_DIR
from scripts.common.publish import dataframe_para_parquet
from scripts.common.bucket_sync import carregar_assinaturas, salvar_assinaturas
from scripts.common import exit_codes
from scripts.process.datasus.common.base_process_dbc_stream import processar_diretorio_dbc
from scripts.process.datasus.common.cnes.habilitacoes_oncologia import (
    eh_habilitacao_oncologia, eh_pediatrico, HABILITACOES_ONCOLOGIA,
)
from scripts.process.datasus.common.cnes.transformar_cnes import aplicar_transformacoes

PASTA_BUCKET = "cnes"
NOME_ARQUIVO_FINAL = "cnes_instituicoes_oncologia.parquet"
CHAVE_FONTE_ESTABELECIMENTOS = "cnes_estabelecimentos_csv.zip"

CNES_ESTABELECIMENTOS_CSV = LANDING_DIR / "cnes" / "cnes_estabelecimentos_raw.csv"
DBC_HABILITACAO_DIR = LANDING_DIR / "dbc_cnes_habilitacao"
DBC_LEITOS_DIR = LANDING_DIR / "dbc_cnes_leitos"

COLUNA_HABILITACAO_CANDIDATAS = ["SGRUPHAB", "CO_HABILITACAO", "CO_HAB", "HABILITACAO", "TP_HABILITACAO"]
COLUNA_CNES_CANDIDATAS = ["CNES", "CO_CNES", "CO_UNIDADE"]
COLUNA_PORTARIA_CANDIDATAS = ["PORTARIA"]
COLUNA_DATA_PORTARIA_CANDIDATAS = ["DTPORTAR"]
COLUNA_QTD_LEITOS_LT_CANDIDATAS = ["QT_EXIST", "QTDE_EXIST", "QT_EXIST_", "NULEITOS", "QTLEITOS"]

COLUNAS_ESTABELECIMENTOS = [
    "CO_CNES", "NU_CNPJ", "NU_CNPJ_MANTENEDORA", "NO_RAZAO_SOCIAL", "NO_FANTASIA",
    "CO_UF", "CO_IBGE", "CO_CEP", "NO_LOGRADOURO", "NU_ENDERECO", "NO_BAIRRO",
    "NU_LATITUDE", "NU_LONGITUDE", "NU_TELEFONE", "NO_EMAIL",
    "CO_NATUREZA_JUR", "CO_ESFERA_ADMINISTRATIVA", "DS_ESFERA_ADMINISTRATIVA",
    "TP_UNIDADE",
    "ST_CENTRO_CIRURGICO", "ST_CENTRO_OBSTETRICO", "ST_CENTRO_NEONATAL",
    "ST_ATEND_HOSPITALAR", "ST_SERVICO_APOIO", "ST_ATEND_AMBULATORIAL",
]


def normalizar_codigo(valor, largura: int) -> str:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    return str(valor).strip().zfill(largura)


def _filtro_chunk_oncologia(df):
    coluna = next((c for c in COLUNA_HABILITACAO_CANDIDATAS if c in df.columns), None)
    if coluna is None:
        return df.iloc[0:0]
    mascara = df[coluna].apply(eh_habilitacao_oncologia)
    return df[mascara]


def _descricao_habilitacao(codigo: str) -> str:
    info = HABILITACOES_ONCOLOGIA.get(str(codigo).strip().replace(".", ""))
    return info["descricao"] if info else f"Código {codigo} (não catalogado)"


def _carregar_leitos_por_cnes() -> pd.DataFrame | None:
    parquet_temp = PROCESSED_DIR / "_tmp_cnes_leitos.parquet"
    if not DBC_LEITOS_DIR.exists() or not any(DBC_LEITOS_DIR.glob("*.dbc")):
        print(f"[AVISO] {DBC_LEITOS_DIR} ausente ou vazio -- seguindo sem leitos reais.")
        return None

    processar_diretorio_dbc(DBC_LEITOS_DIR, parquet_temp, apagar_dbc=False)
    if not parquet_temp.exists():
        return None

    df_lt = pd.read_parquet(parquet_temp)
    parquet_temp.unlink()

    col_cnes = next((c for c in COLUNA_CNES_CANDIDATAS if c in df_lt.columns), None)
    col_qtd = next((c for c in COLUNA_QTD_LEITOS_LT_CANDIDATAS if c in df_lt.columns), None)
    if col_cnes is None or col_qtd is None:
        print(f"[AVISO] Colunas de leitos não encontradas (CNES: {col_cnes}, qtd: {col_qtd}). Seguindo sem leitos.")
        return None

    df_lt["_CNES_NORM"] = df_lt[col_cnes].apply(lambda v: normalizar_codigo(v, 7))
    df_lt["_QTD"] = pd.to_numeric(df_lt[col_qtd], errors="coerce")
    return (
        df_lt.groupby("_CNES_NORM")
        .agg(TOTAL_LEITOS_CNES=("_QTD", lambda s: s.sum(min_count=1)))
        .reset_index()
        .rename(columns={"_CNES_NORM": "CNES"})
    )


def _agregar_instituicoes(df_hab: pd.DataFrame) -> pd.DataFrame:
    coluna_hab = next((c for c in COLUNA_HABILITACAO_CANDIDATAS if c in df_hab.columns), None)
    coluna_cnes = next((c for c in COLUNA_CNES_CANDIDATAS if c in df_hab.columns), None)
    coluna_portaria = next((c for c in COLUNA_PORTARIA_CANDIDATAS if c in df_hab.columns), None)
    coluna_data = next((c for c in COLUNA_DATA_PORTARIA_CANDIDATAS if c in df_hab.columns), None)

    if coluna_cnes is None:
        raise ValueError(f"Coluna CNES não encontrada. Disponíveis: {list(df_hab.columns)}")

    df_hab["_CNES_NORM"] = df_hab[coluna_cnes].apply(lambda v: normalizar_codigo(v, 7))
    df_hab["_DESCRICAO_HAB"] = df_hab[coluna_hab].apply(_descricao_habilitacao)
    df_hab["_PEDIATRICO_HAB"] = df_hab[coluna_hab].apply(eh_pediatrico)

    agregados = {
        "TEM_ONCOLOGIA_PEDIATRICA": ("_PEDIATRICO_HAB", "any"),
        "QTD_HABILITACOES_ONCOLOGIA": ("_DESCRICAO_HAB", "count"),
        "HABILITACOES_ONCOLOGIA": ("_DESCRICAO_HAB", lambda s: "; ".join(sorted(set(s)))),
    }
    if coluna_portaria:
        agregados["PORTARIAS"] = (
            coluna_portaria,
            lambda s: "; ".join(sorted(set(str(x) for x in s if pd.notna(x) and str(x).strip()))),
        )
    if coluna_data:
        agregados["DATA_PORTARIA_MAIS_ANTIGA"] = (coluna_data, "min")

    return (
        df_hab.groupby("_CNES_NORM")
        .agg(**agregados)
        .reset_index()
        .rename(columns={"_CNES_NORM": "CNES"})
    )


def _juntar_estabelecimentos(df_inst: pd.DataFrame) -> pd.DataFrame:
    if not CNES_ESTABELECIMENTOS_CSV.exists():
        print(f"[AVISO] {CNES_ESTABELECIMENTOS_CSV} não encontrado -- sem dados do cadastro geral.")
        df_inst["ENCONTRADO_NO_CNES"] = False
        return df_inst

    df_estab_completo = pd.read_csv(CNES_ESTABELECIMENTOS_CSV, sep=";", encoding="latin1", dtype=str)
    colunas = [c for c in COLUNAS_ESTABELECIMENTOS if c in df_estab_completo.columns]
    faltando = [c for c in COLUNAS_ESTABELECIMENTOS if c not in df_estab_completo.columns]
    if faltando:
        print(f"[AVISO] Colunas do cadastro não encontradas (ignoradas): {faltando}")

    df_estab = df_estab_completo[colunas].copy()
    df_estab["CO_CNES"] = df_estab["CO_CNES"].apply(lambda v: normalizar_codigo(v, 7))
    df_estab = df_estab.drop_duplicates("CO_CNES", keep="first")

    total_antes = len(df_inst)
    df = df_inst.merge(df_estab, left_on="CNES", right_on="CO_CNES", how="left")
    assert len(df) == total_antes, f"Merge duplicou linhas ({total_antes} -> {len(df)})."

    df["ENCONTRADO_NO_CNES"] = df["CO_CNES"].notna()
    df = df.drop(columns=["CO_CNES"])

    nao_encontrados = int((~df["ENCONTRADO_NO_CNES"]).sum())
    if nao_encontrados:
        orfaos = sorted(df.loc[~df["ENCONTRADO_NO_CNES"], "CNES"].tolist())
        print(f"[AVISO] {nao_encontrados} instituição(ões) sem correspondência no cadastro CNES "
              f"(mantidas com ENCONTRADO_NO_CNES=False). Códigos: {orfaos}")
    return df


def main() -> int:
    parquet_temp = PROCESSED_DIR / "_tmp_cnes_habilitacao_oncologia.parquet"

    houve_dado = processar_diretorio_dbc(
        DBC_HABILITACAO_DIR, parquet_temp,
        filtro_chunk=_filtro_chunk_oncologia, apagar_dbc=False,
    )
    if not houve_dado or not parquet_temp.exists():
        print("[AVISO] Nenhuma habilitação de oncologia encontrada/processada.")
        return exit_codes.SEM_NOVIDADE

    df_hab = pd.read_parquet(parquet_temp)
    parquet_temp.unlink()

    df_inst = _agregar_instituicoes(df_hab)
    df_final = _juntar_estabelecimentos(df_inst)

    df_leitos = _carregar_leitos_por_cnes()
    if df_leitos is not None:
        total_antes = len(df_final)
        df_final = df_final.merge(df_leitos, on="CNES", how="left")
        assert len(df_final) == total_antes, "Merge com leitos duplicou linhas."

    df_final = aplicar_transformacoes(df_final)

    ok = dataframe_para_parquet(df_final, PASTA_BUCKET, NOME_ARQUIVO_FINAL)
    if not ok:
        return exit_codes.ERRO

    if CNES_ESTABELECIMENTOS_CSV.exists():
        assinatura = hashlib.sha256(CNES_ESTABELECIMENTOS_CSV.read_bytes()).hexdigest()
        assinaturas = carregar_assinaturas(PASTA_BUCKET)
        assinaturas[CHAVE_FONTE_ESTABELECIMENTOS] = assinatura
        salvar_assinaturas(PASTA_BUCKET, assinaturas)

    total = len(df_final)
    pediatrico = int(df_final["TEM_ONCOLOGIA_PEDIATRICA"].sum()) if "TEM_ONCOLOGIA_PEDIATRICA" in df_final else 0
    print(f"✔ {total} instituição(ões) com habilitação em oncologia publicadas "
          f"({pediatrico} com habilitação pediátrica).")
    return exit_codes.SUCESSO


if __name__ == "__main__":
    import sys
    sys.exit(main())
