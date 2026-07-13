"""
SIM - Óbitos por Câncer, CID-10 Consolidado (1996-atual) (process)

Filtra direto do .dbc na Landing (registro a registro) -- nunca
materializa a base geral de mortalidade CID-10 em disco.

Saídas:
  data/raw/raw_sim_obitos_cancer_cid10.parquet    -- óbitos por câncer, registro a registro
  data/raw/raw_sim_obitos_cancer_resumo_anual.csv -- resumo unificado (upsert por ano)

Nota: quando um ano aqui processado também existir como preliminar no
resumo (ex: 2026 já veio como PRELIM antes de ser consolidado), a linha
do preliminar é substituída pela do consolidado -- comportamento
intencional (ver resumo_cancer.py).
"""
from scripts.common.paths import LANDING_DIR, RAW_DIR
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc_filtrado
from scripts.process.datasus.common.filtros_cancer import filtro_cancer_cid10
from scripts.process.datasus.common.colunas_sim import COLUNAS_DECLARACAO_OBITO
from scripts.process.datasus.common.resumo_cancer import atualizar_resumo_anual, extrair_ano_cid10
from scripts.process.datasus.common.normalizar_municipio import adicionar_municipio_normalizado

def main():
    dbc_dir = LANDING_DIR / "dbc_sim_declaracao_obito_cid10"
    parquet_final = RAW_DIR / "raw_sim_obitos_cancer_cid10.parquet"
    resumo_csv = RAW_DIR / "raw_sim_obitos_cancer_resumo_anual.csv"

    def callback(detalhe):
        atualizar_resumo_anual([detalhe], "CID10", extrair_ano_cid10, resumo_csv)

    houve_dado, _ = processar_diretorio_dbc_filtrado(
        dbc_dir, parquet_final, filtro_cancer_cid10,
        colunas_padrao=COLUNAS_DECLARACAO_OBITO, callback_arquivo=callback
    )

    if houve_dado:
        adicionar_municipio_normalizado(parquet_final)

if __name__ == "__main__":
    main()