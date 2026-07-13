"""
Normaliza o código de município de residência entre as diferentes eras
do SIM pra um formato único de 6 dígitos (código IBGE reduzido, sem
dígito verificador) -- mesmo padrão já usado no resto do projeto
(CNES: CO_IBGE; Macrorregião: cod_municipio).

Achado real (confirmado em análise): CODMUNRES (CID-10/Preliminar) vem
no código IBGE COMPLETO (7 dígitos, com dígito verificador); sem essa
normalização, um cruzamento direto com raw_macroregiao_de_saude.parquet
(ou com o CNES) perde ~24% dos registros -- não por dado faltando, mas
por incompatibilidade de formato entre nossas próprias bases.

CID-9 usa um campo com nome diferente (MUNIRES, não CODMUNRES) --
detecção dinâmica cobre os dois casos.

Lê e escreve em LOTES via pyarrow (não pandas) -- carregar o arquivo
inteiro com pd.read_parquet() já estourou memória em produção
(CID-10: 5M linhas x ~100 colunas, todas texto, pediu 3.8 GiB numa
alocação só). Processando em lotes de ~200 mil linhas, o uso de
memória fica limitado ao tamanho de um lote, não do arquivo inteiro.
"""
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

COLUNA_MUNICIPIO_CANDIDATAS = ["CODMUNRES", "MUNIRES", "MUNI_RES"]
TAMANHO_LOTE = 200_000


def _reduzir_codigo(valor) -> str | None:
    """Corta pro código IBGE reduzido (6 dígitos) se vier com o dígito
    verificador (7 dígitos); mantém como está se já vier com 6."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    return texto[:6] if len(texto) >= 7 else texto


def adicionar_municipio_normalizado(parquet_path: Path) -> bool:
    """Lê o parquet EM LOTES, detecta a coluna de município de
    residência, adiciona CO_IBGE_RESIDENCIA (6 dígitos) e regrava (num
    arquivo temporário, substituindo o original só no final -- se
    crashar no meio, o arquivo original não fica corrompido).

    Retorna True se conseguiu normalizar (ou se o parquet estava vazio
    -- nada a fazer, mas não é erro); False se não achou nenhuma coluna
    candidata (não trava o processamento, só avisa)."""
    if not parquet_path.exists():
        return False

    pf = pq.ParquetFile(parquet_path)
    schema = pf.schema_arrow

    if pf.metadata.num_rows == 0:
        return True

    coluna = next((c for c in COLUNA_MUNICIPIO_CANDIDATAS if c in schema.names), None)
    if coluna is None:
        print(f"[AVISO] Nenhuma coluna de município de residência encontrada em {parquet_path.name} "
              f"(candidatas: {COLUNA_MUNICIPIO_CANDIDATAS}). CO_IBGE_RESIDENCIA não foi adicionado. "
              f"Colunas disponíveis: {schema.names}")
        return False

    novo_schema = schema.append(pa.field("CO_IBGE_RESIDENCIA", pa.string()))
    caminho_temp = parquet_path.with_suffix(".tmp_normalizando.parquet")

    total_linhas = 0
    total_nulo = 0

    writer = pq.ParquetWriter(str(caminho_temp), novo_schema)
    try:
        for batch in pf.iter_batches(batch_size=TAMANHO_LOTE):
            tabela = pa.Table.from_batches([batch])
            valores_originais = tabela.column(coluna).to_pylist()
            valores_normalizados = [_reduzir_codigo(v) for v in valores_originais]

            tabela_nova = tabela.append_column(
                "CO_IBGE_RESIDENCIA", pa.array(valores_normalizados, type=pa.string())
            )
            writer.write_table(tabela_nova)

            total_linhas += len(valores_normalizados)
            total_nulo += sum(1 for v in valores_normalizados if v is None)
    finally:
        writer.close()

    del pf  # libera o handle de leitura do arquivo original -- no Windows,
             # um arquivo com handle aberto não pode ser substituído/renomeado
    caminho_temp.replace(parquet_path)  # só troca o original depois de escrever tudo com sucesso

    print(f"[INFO] CO_IBGE_RESIDENCIA adicionado a {parquet_path.name} (a partir de '{coluna}') -- "
          f"{total_nulo}/{total_linhas} sem código de município.")
    return True