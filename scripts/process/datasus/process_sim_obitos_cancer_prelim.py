"""
SIM - Óbitos por Câncer, CID-10 Preliminar (process)

Mesmo filtro do consolidado. Pode legitimamente ficar vazio entre
ciclos de publicação do DATASUS -- nesse caso escreve só o Parquet
vazio (schema padrão); o resumo anual não é tocado (não tem ano pra
registrar quando não há nenhum arquivo).

Saídas:
  data/raw/raw_sim_obitos_cancer_prelim.parquet
  data/raw/raw_sim_obitos_cancer_resumo_anual.csv (upsert -- só quando há dado)
"""
from scripts.common.paths import LANDING_DIR, RAW_DIR
from scripts.process.datasus.base_process_dbc import processar_diretorio_dbc_filtrado
from scripts.process.datasus.common.filtros_cancer import filtro_cancer_cid10
from scripts.process.datasus.common.colunas_sim import COLUNAS_DECLARACAO_OBITO
from scripts.process.datasus.common.resumo_cancer import atualizar_resumo_anual, extrair_ano_cid10

def main():
    dbc_dir = LANDING_DIR / "dbc_sim_declaracao_obito_prelim"
    parquet_final = RAW_DIR / "raw_sim_obitos_cancer_prelim.parquet"
    resumo_csv = RAW_DIR / "raw_sim_obitos_cancer_resumo_anual.csv"

    def callback(detalhe):
        atualizar_resumo_anual([detalhe], "PRELIM", extrair_ano_cid10, resumo_csv)

    _, detalhes = processar_diretorio_dbc_filtrado(
        dbc_dir, parquet_final, filtro_cancer_cid10,
        colunas_padrao=COLUNAS_DECLARACAO_OBITO, callback_arquivo=callback
    )

    if not detalhes:
        print("[INFO] Nenhum .dbc no preliminar agora -- resumo anual não alterado.")

if __name__ == "__main__":
    main()