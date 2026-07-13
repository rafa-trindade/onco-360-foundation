"""
SIM - Óbitos por Câncer (Neoplasia Maligna), série histórica 1979-atual (process)

Recorte derivado, específico do onco-360: filtra os óbitos cuja causa
básica (CAUSABAS) é neoplasia MALIGNA, combinando as duas eras de
codificação do SIM -- CID-9 (1979-1995) e CID-10 (1996-atual).

Os DOIS lados são processados DIRETO dos .dbc na Landing, registro a
registro, via processar_diretorio_dbc_filtrado -- nenhuma base geral de
mortalidade (nem CID-9, nem CID-10) é materializada por inteiro em
disco. Não faz sentido reprocessar/armazenar ~29 anos de óbitos gerais
(todas as causas) só para descartar quase tudo em seguida -- o filtro é
aplicado ANTES da escrita, não depois.

Faixas de CAUSABAS confirmadas linha a linha contra as tabelas oficiais
do DATASUS (CIDCAP.DBF / CIDCAP10.DBF e CID9.DBF / CID10.DBF, capítulo
II - Neoplasias):

  CID-9  (1979-1995): CAUSABAS entre 140 e 208 (neoplasmas malignos)
  CID-10 (1996-atual): CAUSABAS entre C00 e C97 (neoplasias malignas)

Faixas adjacentes foram deliberadamente EXCLUÍDAS por não serem "câncer"
no sentido clínico/epidemiológico padrão (mesma definição usada por
INCA e OMS/IARC para estatística de mortalidade por câncer):

  CID-10  D00-D09  Carcinoma in situ            -- excluído
  CID-10  D10-D36  Neoplasias benignas          -- excluído
  CID-10  D37-D48  Comportamento incerto/desc.  -- excluído
  CID-9   210-229  Neoplasmas benignos          -- excluído
  CID-9   230-234  Carcinoma in situ            -- excluído
  CID-9   235-239  Incerto/não especificado     -- excluído

*** ATENÇÃO -- VALIDAÇÃO PENDENTE (só no CID-9) ***
O CID-10 usa a coluna 'CAUSABAS', já confirmada (mesmo layout usado em
process_sim_declaracao_obito_prelim.py). O nome exato da coluna de causa
básica na era CID-9 ainda NÃO foi confirmado contra um arquivo real --
o filtro detecta a coluna no primeiro registro lido e avisa claramente
no log qual encontrou (ou se não achou nenhuma candidata). Confira essa
linha do log antes de considerar o resultado do CID-9 confiável.
"""
from scripts.common.paths import LANDING_DIR, RAW_DIR
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc_filtrado
import pandas as pd

COLUNA_CAUSABAS_CID9_CANDIDATAS = ["CAUSABAS", "CAUSAMORT", "CAUSAM", "CAUSABAS_O"]


def filtro_cancer_cid10(registro: dict) -> bool:
    """CAUSABAS entre C00 e C97 (neoplasia maligna). Coluna já confirmada."""
    valor = str(registro.get("CAUSABAS", "")).strip().upper()
    if len(valor) < 3 or valor[0] != "C":
        return False
    try:
        numero = int(valor[1:3])
    except ValueError:
        return False
    return numero <= 97


def criar_filtro_cancer_cid9():
    """
    Cria a função de filtro pro CID-9. Detecta a coluna de causa básica
    só no primeiro registro (evita refazer a busca a cada linha) e
    avisa uma única vez no log qual coluna encontrou.
    """
    estado = {"coluna": None, "detectada": False}

    def filtro(registro: dict) -> bool:
        if not estado["detectada"]:
            estado["coluna"] = next((c for c in COLUNA_CAUSABAS_CID9_CANDIDATAS if c in registro), None)
            estado["detectada"] = True
            if estado["coluna"] is None:
                print(f"[AVISO] Nenhuma coluna candidata a CAUSABAS encontrada no CID-9. "
                      f"Colunas disponíveis: {list(registro.keys())}")
                print("        Ajuste COLUNA_CAUSABAS_CID9_CANDIDATAS neste script com o nome correto.")
            else:
                print(f"[INFO] Usando '{estado['coluna']}' como coluna de causa básica no CID-9.")

        if estado["coluna"] is None:
            return False

        valor = str(registro.get(estado["coluna"], "")).strip()
        try:
            numero = int(valor[:3])
        except ValueError:
            return False
        return 140 <= numero <= 208

    return filtro


def main():
    cid10_dbc_dir = LANDING_DIR / "dbc_sim_declaracao_obito"
    cid9_dbc_dir = LANDING_DIR / "dbc_sim_declaracao_obito_cid9"

    cid10_tmp = RAW_DIR / "_tmp_sim_obitos_cancer_cid10.parquet"
    cid9_tmp = RAW_DIR / "_tmp_sim_obitos_cancer_cid9.parquet"
    parquet_final = RAW_DIR / "raw_sim_obitos_cancer.parquet"

    partes = []

    print("=== CID-10 (1996-atual) -- filtrando direto da Landing ===")
    houve_cid10 = processar_diretorio_dbc_filtrado(cid10_dbc_dir, cid10_tmp, filtro_cancer_cid10)
    if houve_cid10:
        df10 = pd.read_parquet(cid10_tmp)
        df10["FONTE_CID"] = "CID10"
        print(f"CID-10: {len(df10)} óbitos por câncer mantidos.")
        partes.append(df10)
        cid10_tmp.unlink()
    else:
        print("[AVISO] Nenhum registro de câncer encontrado/processado no CID-10 "
              "(confira se o extract já baixou os .dbc em data/landing/dbc_sim_declaracao_obito).")

    print("\n=== CID-9 (1979-1995) -- filtrando direto da Landing ===")
    houve_cid9 = processar_diretorio_dbc_filtrado(cid9_dbc_dir, cid9_tmp, criar_filtro_cancer_cid9())
    if houve_cid9:
        df9 = pd.read_parquet(cid9_tmp)
        df9["FONTE_CID"] = "CID9"
        print(f"CID-9: {len(df9)} óbitos por câncer mantidos.")
        partes.append(df9)
        cid9_tmp.unlink()
    else:
        print("[AVISO] Nenhum registro de câncer encontrado/processado no CID-9 "
              "(confira se o extract já baixou os .dbc em data/landing/dbc_sim_declaracao_obito_cid9).")

    if not partes:
        print("\nNenhuma fonte disponível para filtrar. Nada foi gerado.")
        return

    df_final = pd.concat(partes, ignore_index=True)
    parquet_final.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(parquet_final, index=False)
    print(f"\n✔ {len(df_final)} óbitos por câncer (1979-atual) salvos em {parquet_final.name}")

if __name__ == "__main__":
    main()