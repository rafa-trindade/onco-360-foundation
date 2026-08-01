"""SIM - Óbitos por Câncer, CID-9 (1979-1995) (process).

Filtra os óbitos por neoplasia maligna (CAUSABAS 140-208) direto dos .dbc
da landing e publica em datasus_sim/obitos_cancer_cid9.parquet.

Esquema e domínios confirmados via MORT98.HLP (DATASUS). A era CID-9 tem
nomes de coluna e dicionários próprios (ESTCIVIL, INSTRUCAO, LOCOCOR em
ordem distinta, TIPOPARTO Espontâneo/Operatório), tratados em
decodificar_sim_cid9. A causa básica é CAUSABAS (3-4 caracteres numéricos)
e o município de residência é MUNIRES.
"""
import sys

from scripts.common import exit_codes
from scripts.common.paths import LANDING_DIR
from scripts.process.datasus.common.base_process_dbc_stream import processar_fonte_ftp_incremental
from scripts.process.datasus.common.sim.filtros_cancer import criar_filtro_chunk_cancer_cid9
from scripts.process.datasus.common.sim.decodificar_sim_cid9 import montar_query_sim_cid9
from scripts.process.datasus.common.sim.decodificar_sim import baixar_sinonimos_municipio
from scripts.process.datasus.common.sim.resumo_sim_stream import atualizar_resumo_anual
from scripts.process.datasus.common.sim.resumo_cancer import extrair_ano_cid9

PASTA_BUCKET = "datasus_sim"
NOME_ARQUIVO_FINAL = "obitos_cancer_cid9.parquet"
FONTE_RESUMO = "CID9"

DBC_DIR = LANDING_DIR / "dbc_sim_declaracao_obito_cid9"


def main() -> int:
    totais = {}
    sinonimos = baixar_sinonimos_municipio()

    def transformacao(cols):
        return montar_query_sim_cid9(cols, sinonimos)

    codigo = processar_fonte_ftp_incremental(
        DBC_DIR, PASTA_BUCKET, NOME_ARQUIVO_FINAL,
        filtro_chunk=criar_filtro_chunk_cancer_cid9(),
        query_transformacao=transformacao,
        contador_totais=totais,
    )

    if codigo == exit_codes.SUCESSO and totais:
        atualizar_resumo_anual(totais, FONTE_RESUMO, extrair_ano_cid9, NOME_ARQUIVO_FINAL)

    return codigo


if __name__ == "__main__":
    sys.exit(main())
