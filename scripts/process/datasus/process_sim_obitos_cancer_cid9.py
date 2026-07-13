"""
SIM - Óbitos por Câncer, CID-9 (1979-1995) (process)

Filtra direto do .dbc na Landing (registro a registro) -- nunca
materializa a base geral de mortalidade CID-9 em disco. Ver
scripts/process/datasus/filtros_cancer.py pra detalhes das faixas de
CAUSABAS e o aviso de validação pendente.

Saídas:
  data/raw/raw_sim_obitos_cancer_cid9.parquet    -- óbitos por câncer, registro a registro
  data/raw/raw_sim_obitos_cancer_resumo_anual.csv -- resumo unificado (upsert por ano, compartilhado com CID-10/preliminar)
"""
from scripts.common.paths import LANDING_DIR, RAW_DIR
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc_filtrado
from scripts.process.datasus.common.filtros_cancer import criar_filtro_cancer_cid9
from scripts.process.datasus.common.resumo_cancer import atualizar_resumo_anual, extrair_ano_cid9
from scripts.process.datasus.common.normalizar_municipio import adicionar_municipio_normalizado

def main():
    dbc_dir = LANDING_DIR / "dbc_sim_declaracao_obito_cid9"
    parquet_final = RAW_DIR / "raw_sim_obitos_cancer_cid9.parquet"
    resumo_csv = RAW_DIR / "raw_sim_obitos_cancer_resumo_anual.csv"

    def callback(detalhe):
        atualizar_resumo_anual([detalhe], "CID9", extrair_ano_cid9, resumo_csv)

    houve_dado, _ = processar_diretorio_dbc_filtrado(
        dbc_dir, parquet_final, criar_filtro_cancer_cid9(), callback_arquivo=callback
    )

    if houve_dado:
        adicionar_municipio_normalizado(parquet_final)

if __name__ == "__main__":
    main()