"""
CNES - Instituições com Habilitação em Oncologia (process)

Uma linha por INSTITUIÇÃO (não por habilitação) -- uma mesma
instituição pode ter mais de uma habilitação em oncologia (ex: UNACON
adulto + UNACON pediátrica), e um desenho anterior (uma linha por
habilitação) duplicava a instituição em qualquer cruzamento posterior
(ex: convênios, onde cada convênio aparecia 2x pra instituição com 2
habilitações).

Traz o máximo de informação não nula do CNES de Estabelecimentos:
endereço completo, lat/long, telefone, e-mail, classificação
administrativa/jurídica, capacidades assistenciais -- não só
nome/CNPJ como antes.

Normaliza o código CNES (remove espaço, preenche zero à esquerda até 7
dígitos) nos DOIS lados antes de cruzar -- corrigido um bug real: o
CNES do IMIP (Recife/PE, hospital ativo e atualizado) aparecia como
órfão porque uma das fontes devolvia "434" e a outra "0000434".

Instituições cuja habilitação não encontrou correspondência no CNES de
Estabelecimentos (mesmo após normalizar) NÃO são descartadas -- ficam
com ENCONTRADO_NO_CNES=False e os demais campos vazios, pra nunca
perder dado silenciosamente. Confira esses casos manualmente.

Contagem de leitos: NÃO vem mais do campo NULEITOS de dentro do
Habilitação (HB) -- provado não confiável (vinha 0 pra quase tudo,
inclusive centros de referência nacional). Vem do dataset CNES-Leitos
(LT, separado), como TOTAL_LEITOS_CNES -- é o total de leitos do
estabelecimento inteiro, não um recorte só de oncologia (o LT não tem
essa granularidade disponível ainda neste projeto).

Saída: data/raw/raw_cnes_oncologia_instituicoes.parquet
"""
import pandas as pd
from scripts.common.paths import LANDING_DIR, RAW_DIR
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc_filtrado, processar_diretorio_dbc
from scripts.process.datasus.common.habilitacoes_oncologia import eh_habilitacao_oncologia, eh_pediatrico, HABILITACOES_ONCOLOGIA

CNES_ESTABELECIMENTOS_CSV = LANDING_DIR / "cnes" / "cnes_estabelecimentos_raw.csv"

COLUNA_HABILITACAO_CANDIDATAS = ["SGRUPHAB", "CO_HABILITACAO", "CO_HAB", "HABILITACAO", "TP_HABILITACAO"]
COLUNA_CNES_CANDIDATAS = ["CNES", "CO_CNES", "CO_UNIDADE"]
COLUNA_PORTARIA_CANDIDATAS = ["PORTARIA"]
COLUNA_DATA_PORTARIA_CANDIDATAS = ["DTPORTAR"]

# CNES - Leitos (LT): dataset separado do de Habilitações, com a
# contagem de leitos de verdade por estabelecimento (não filtrada por
# oncologia -- é o total de leitos do estabelecimento inteiro).
# Nomes candidatos cobrem tanto o padrão "moderno" documentado
# publicamente (QT_EXIST) quanto o padrão antigo truncado de campo DBF
# que já vimos se confirmar reservado no Habilitação (SGRUPHAB em vez
# de CO_HABILITACAO) -- não temos certeza de qual vai aparecer aqui até
# rodar contra dado real.
COLUNA_QTD_LEITOS_LT_CANDIDATAS = ["QT_EXIST", "QTDE_EXIST", "QT_EXIST_", "NULEITOS", "QTLEITOS"]

# Colunas do CNES de Estabelecimentos que valem a pena trazer --
# identificação, endereço/geo, contato, classificação, capacidades
# assistenciais. Só entram as que existirem de fato no arquivo (ver
# checagem defensiva em main()).
COLUNAS_ESTABELECIMENTOS = [
    "CO_CNES", "NU_CNPJ", "NU_CNPJ_MANTENEDORA", "NO_RAZAO_SOCIAL", "NO_FANTASIA",
    "CO_UF", "CO_IBGE", "CO_CEP", "NO_LOGRADOURO", "NU_ENDERECO", "NO_BAIRRO",
    "NU_LATITUDE", "NU_LONGITUDE", "NU_TELEFONE", "NO_EMAIL",
    "CO_NATUREZA_JUR", "CO_NATUREZA_ORGANIZACAO", "DS_NATUREZA_ORGANIZACAO",
    "CO_ESFERA_ADMINISTRATIVA", "DS_ESFERA_ADMINISTRATIVA",
    "CO_NIVEL_HIERARQUIA", "DS_NIVEL_HIERARQUIA", "TP_UNIDADE",
    "ST_CENTRO_CIRURGICO", "ST_CENTRO_OBSTETRICO", "ST_CENTRO_NEONATAL",
    "ST_ATEND_HOSPITALAR", "ST_SERVICO_APOIO", "ST_ATEND_AMBULATORIAL",
]


def normalizar_codigo(valor, largura: int) -> str:
    """Remove espaços e preenche com zero à esquerda até a largura
    esperada -- normaliza diferenças de formatação entre fontes antes
    de cruzar (ex: uma fonte devolve '434' onde a outra tem '0000434')."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    return str(valor).strip().zfill(largura)


def criar_filtro_oncologia():
    estado = {"coluna_hab": None, "detectado": False}

    def filtro(registro: dict) -> bool:
        if not estado["detectado"]:
            estado["coluna_hab"] = next((c for c in COLUNA_HABILITACAO_CANDIDATAS if c in registro), None)
            estado["detectado"] = True
            if estado["coluna_hab"] is None:
                print(f"[AVISO] Nenhuma coluna candidata a código de habilitação encontrada. "
                      f"Colunas disponíveis: {list(registro.keys())}")
                print("        Ajuste COLUNA_HABILITACAO_CANDIDATAS neste script com o nome correto.")
            else:
                print(f"[INFO] Usando '{estado['coluna_hab']}' como coluna de código de habilitação.")

        if estado["coluna_hab"] is None:
            return False

        return eh_habilitacao_oncologia(registro.get(estado["coluna_hab"], ""))

    return filtro


def _descricao_habilitacao(codigo: str) -> str:
    info = HABILITACOES_ONCOLOGIA.get(str(codigo).strip().replace(".", ""))
    return info["descricao"] if info else f"Código {codigo} (não catalogado)"


def carregar_leitos_por_cnes() -> pd.DataFrame | None:
    """Lê o CNES-Leitos (LT), agrega o total de leitos por CNES
    (normalizado, 7 dígitos). Retorna None se o diretório não existir
    ou não tiver arquivo -- tratado como fonte opcional, não trava o
    resto do processamento se ainda não foi baixado."""
    dbc_dir = LANDING_DIR / "dbc_cnes_leitos"
    parquet_temp = RAW_DIR / "_tmp_cnes_leitos.parquet"

    if not dbc_dir.exists() or not any(dbc_dir.glob("*.dbc")):
        print(f"[AVISO] {dbc_dir} não encontrado ou vazio -- rode o extract do CNES Leitos "
              f"(scripts.extract.datasus.fetch_cnes_leitos) pra ter essa informação. Seguindo sem leitos reais.")
        return None

    processar_diretorio_dbc(dbc_dir, parquet_temp)

    if not parquet_temp.exists():
        print("[AVISO] Processamento do CNES Leitos não gerou saída -- seguindo sem leitos reais.")
        return None

    df_lt = pd.read_parquet(parquet_temp)
    parquet_temp.unlink()

    coluna_cnes_lt = next((c for c in COLUNA_CNES_CANDIDATAS if c in df_lt.columns), None)
    coluna_qtd_lt = next((c for c in COLUNA_QTD_LEITOS_LT_CANDIDATAS if c in df_lt.columns), None)

    if coluna_cnes_lt is None or coluna_qtd_lt is None:
        print(f"[AVISO] Não achei as colunas esperadas no CNES Leitos (CNES: {coluna_cnes_lt}, "
              f"quantidade: {coluna_qtd_lt}). Colunas disponíveis: {list(df_lt.columns)}")
        print("        Ajuste COLUNA_QTD_LEITOS_LT_CANDIDATAS neste script com o nome correto. Seguindo sem leitos reais.")
        return None

    print(f"[INFO] CNES Leitos: usando '{coluna_cnes_lt}' como CNES e '{coluna_qtd_lt}' como quantidade.")
    amostra_bruta = df_lt[coluna_qtd_lt].head(10).tolist()
    print(f"[DIAGNÓSTICO] Amostra bruta de '{coluna_qtd_lt}' (10 primeiros valores): {amostra_bruta}")

    df_lt["_CNES_NORM"] = df_lt[coluna_cnes_lt].apply(lambda v: normalizar_codigo(v, 7))
    df_lt["_QTD"] = pd.to_numeric(df_lt[coluna_qtd_lt], errors="coerce")

    df_leitos_agrupado = (
        df_lt.groupby("_CNES_NORM")
        .agg(TOTAL_LEITOS_CNES=("_QTD", lambda s: s.sum(min_count=1)))
        .reset_index()
        .rename(columns={"_CNES_NORM": "CNES"})
    )
    print(f"[INFO] CNES Leitos: {len(df_leitos_agrupado)} estabelecimento(s) com contagem de leitos.")
    return df_leitos_agrupado


def main():
    dbc_dir = LANDING_DIR / "dbc_cnes_habilitacao"
    parquet_temp = RAW_DIR / "_tmp_cnes_habilitacao_oncologia.parquet"
    parquet_final = RAW_DIR / "raw_cnes_oncologia_instituicoes.parquet"

    houve_dado, _ = processar_diretorio_dbc_filtrado(dbc_dir, parquet_temp, criar_filtro_oncologia())

    if not houve_dado:
        print("[AVISO] Nenhuma habilitação de oncologia encontrada/processada.")
        return

    df_hab = pd.read_parquet(parquet_temp)
    parquet_temp.unlink()

    coluna_hab = next((c for c in COLUNA_HABILITACAO_CANDIDATAS if c in df_hab.columns), None)
    coluna_cnes = next((c for c in COLUNA_CNES_CANDIDATAS if c in df_hab.columns), None)
    coluna_portaria = next((c for c in COLUNA_PORTARIA_CANDIDATAS if c in df_hab.columns), None)
    coluna_data_portaria = next((c for c in COLUNA_DATA_PORTARIA_CANDIDATAS if c in df_hab.columns), None)

    if coluna_cnes is None:
        print(f"[AVISO] Nenhuma coluna candidata a código CNES encontrada em df_hab. "
              f"Colunas disponíveis: {list(df_hab.columns)}")
        print("        Ajuste COLUNA_CNES_CANDIDATAS neste script.")
        return

    df_hab["_CNES_NORM"] = df_hab[coluna_cnes].apply(lambda v: normalizar_codigo(v, 7))
    df_hab["_DESCRICAO_HAB"] = df_hab[coluna_hab].apply(_descricao_habilitacao)
    df_hab["_PEDIATRICO_HAB"] = df_hab[coluna_hab].apply(eh_pediatrico)

    print(f"Agrupando {len(df_hab)} habilitação(ões) em instituições únicas...")

    agregados = {
        "PEDIATRICO": ("_PEDIATRICO_HAB", "any"),
        "QTD_HABILITACOES_ONCOLOGIA": ("_DESCRICAO_HAB", "count"),
        "HABILITACOES_ONCOLOGIA": ("_DESCRICAO_HAB", lambda s: "; ".join(sorted(set(s)))),
    }
    if coluna_portaria:
        agregados["PORTARIAS"] = (
            coluna_portaria,
            lambda s: "; ".join(sorted(set(str(x) for x in s if pd.notna(x) and str(x).strip()))),
        )
    if coluna_data_portaria:
        agregados["DATA_PORTARIA_MAIS_ANTIGA"] = (coluna_data_portaria, "min")

    df_inst = (
        df_hab.groupby("_CNES_NORM")
        .agg(**agregados)
        .reset_index()
        .rename(columns={"_CNES_NORM": "CNES"})
    )

    if CNES_ESTABELECIMENTOS_CSV.exists():
        print(f"Lendo {CNES_ESTABELECIMENTOS_CSV.name} (Landing) e juntando (CNES normalizado, 7 dígitos)...")
        df_estab_completo = pd.read_csv(CNES_ESTABELECIMENTOS_CSV, sep=";", encoding="latin1", dtype=str)

        colunas_disponiveis = [c for c in COLUNAS_ESTABELECIMENTOS if c in df_estab_completo.columns]
        faltando = [c for c in COLUNAS_ESTABELECIMENTOS if c not in df_estab_completo.columns]
        if faltando:
            print(f"[AVISO] Colunas esperadas do CNES de Estabelecimentos não encontradas (ignoradas): {faltando}")

        df_estab = df_estab_completo[colunas_disponiveis].copy()
        df_estab["CO_CNES"] = df_estab["CO_CNES"].apply(lambda v: normalizar_codigo(v, 7))

        # Um mesmo CO_CNES não deveria se repetir no cadastro de
        # estabelecimentos -- se repetir, o merge duplicaria instituições.
        duplicados = df_estab[df_estab.duplicated("CO_CNES", keep=False)]
        if not duplicados.empty:
            print(f"[AVISO] {duplicados['CO_CNES'].nunique()} código(s) CNES duplicado(s) no cadastro de "
                  f"Estabelecimentos -- mantendo só o primeiro registro de cada.")
            df_estab = df_estab.drop_duplicates("CO_CNES", keep="first")

        total_antes = len(df_inst)
        df_final = df_inst.merge(df_estab, left_on="CNES", right_on="CO_CNES", how="left")
        assert len(df_final) == total_antes, (
            f"Merge duplicou linhas ({total_antes} -> {len(df_final)}) -- investigar duplicata de CO_CNES."
        )

        df_final["ENCONTRADO_NO_CNES"] = df_final["CO_CNES"].notna()
        nao_encontrados = int((~df_final["ENCONTRADO_NO_CNES"]).sum())
        if nao_encontrados:
            codigos_orfaos = sorted(df_final.loc[~df_final["ENCONTRADO_NO_CNES"], "CNES"].tolist())
            print(f"[AVISO] {nao_encontrados} instituição(ões) com habilitação em oncologia, mas SEM "
                  f"correspondência no CNES de Estabelecimentos (mesmo após normalizar zero à esquerda). "
                  f"Mantidas na saída com ENCONTRADO_NO_CNES=False. Códigos: {codigos_orfaos}")
    else:
        print(f"[AVISO] {CNES_ESTABELECIMENTOS_CSV} não encontrado -- salvando sem dados do cadastro geral. "
              f"Rode o extract do CNES Estabelecimentos primeiro.")
        df_final = df_inst
        df_final["ENCONTRADO_NO_CNES"] = False

    parquet_final.parent.mkdir(parents=True, exist_ok=True)

    df_leitos = carregar_leitos_por_cnes()
    if df_leitos is not None:
        total_antes = len(df_final)
        df_final = df_final.merge(df_leitos, on="CNES", how="left")
        assert len(df_final) == total_antes, (
            f"Merge com CNES Leitos duplicou linhas ({total_antes} -> {len(df_final)})."
        )
        qtd_com_leito = int(df_final["TOTAL_LEITOS_CNES"].notna().sum())
        print(f"[INFO] {qtd_com_leito}/{len(df_final)} instituição(ões) com contagem de leitos real (CNES Leitos).")

    df_final.to_parquet(parquet_final, index=False)

    total_pediatrico = int(df_final["PEDIATRICO"].sum())
    print(f"✔ {len(df_final)} instituição(ões) com habilitação em oncologia salvas em {parquet_final.name} "
          f"({total_pediatrico} com habilitação pediátrica, {len(df_final) - total_pediatrico} só adulto).")

if __name__ == "__main__":
    main()