import os
import re
import logging
from pathlib import Path

import datasus_dbc
from dbfread import DBF
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def processar_diretorio_dbc(dbc_dir: Path, parquet_final_path: Path, batch_size: int = 50_000):
    """
    Converte todos os .dbc de um diretório em um único Parquet final,
    escrevendo em lotes (batch_size registros por vez) para controlar o
    uso de memória em arquivos grandes.
    """
    if not dbc_dir.exists():
        logger.warning(f"Diretório não encontrado: {dbc_dir}.")
        return

    arquivos_dbc = [f for f in os.listdir(dbc_dir) if f.lower().endswith(".dbc")]
    arquivos_dbc.sort()

    if not arquivos_dbc:
        logger.warning(f"Nenhum arquivo .dbc encontrado em {dbc_dir}.")
        return

    parquet_final_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Arquivos encontrados: {len(arquivos_dbc)}")

    writer = None
    total_geral = 0

    try:
        for arquivo in arquivos_dbc:
            caminho_dbc = dbc_dir / arquivo
            nome_base = os.path.splitext(arquivo)[0]
            caminho_dbf = dbc_dir / f"{nome_base}.dbf"

            logger.info(f"=== Arquivo: {arquivo} ===")
            logger.info(f"Descompactando {arquivo}...")

            try:
                datasus_dbc.decompress(str(caminho_dbc), str(caminho_dbf))
            except Exception as e:
                logger.error(f"Falha ao descompactar {arquivo}: {e}")
                continue

            tabela = DBF(str(caminho_dbf), encoding="latin-1")

            batch_registros = []
            count_total = 0

            for registro in tabela:
                count_total += 1
                total_geral += 1
                batch_registros.append(registro)

                if len(batch_registros) >= batch_size:
                    df_batch = pd.DataFrame(batch_registros)
                    table = pa.Table.from_pandas(df_batch, preserve_index=False)

                    if writer is None:
                        writer = pq.ParquetWriter(str(parquet_final_path), table.schema)

                    writer.write_table(table)
                    batch_registros = []

            if batch_registros:
                df_batch = pd.DataFrame(batch_registros)
                table = pa.Table.from_pandas(df_batch, preserve_index=False)

                if writer is None:
                    writer = pq.ParquetWriter(str(parquet_final_path), table.schema)

                writer.write_table(table)

            logger.info(f"Registros totais em {arquivo}: {count_total}")

            if caminho_dbf.exists():
                caminho_dbf.unlink()
                logger.info(f"Arquivo temporário {caminho_dbf.name} removido.")

    finally:
        if writer is not None:
            writer.close()
            logger.info(f"Parquet final salvo em: {parquet_final_path}")

    logger.info("Processamento concluído!")
    logger.info(f"Total de registros em todos os arquivos: {total_geral}")


def _processar_arquivos_para_parquet(
    dbc_dir: Path, arquivos: list[str], colunas_fixas: list[str], saida_path: Path, batch_size: int = 50_000
) -> bool:
    """
    Converte uma lista de .dbc para um único Parquet de saída, com schema
    fixo
    (todas as colunas como string, na ordem de colunas_fixas -- colunas
    ausentes no .dbc viram string vazia). Escreve em lotes de `batch_size`
    registros por vez (mesma disciplina de processar_diretorio_dbc) --
    nunca materializa um arquivo .dbc inteiro em memória de uma vez.

    Retorna True se algum registro foi escrito, False caso contrário.
    """
    schema_pa = pa.schema([(nome, pa.string()) for nome in colunas_fixas])
    writer = None
    total = 0

    try:
        for arquivo in arquivos:
            caminho_dbc = dbc_dir / arquivo
            nome_base = os.path.splitext(arquivo)[0]
            caminho_dbf = dbc_dir / f"{nome_base}.dbf"

            logger.info(f"--- Processando: {arquivo} ---")
            try:
                datasus_dbc.decompress(str(caminho_dbc), str(caminho_dbf))
                dbf_data = DBF(str(caminho_dbf), encoding="latin1")

                batch = []
                count_arquivo = 0
                for record in dbf_data:
                    batch.append({col: str(record.get(col, "")).strip() for col in colunas_fixas})
                    if len(batch) >= batch_size:
                        table = pa.Table.from_pylist(batch, schema=schema_pa)
                        if writer is None:
                            saida_path.parent.mkdir(parents=True, exist_ok=True)
                            writer = pq.ParquetWriter(str(saida_path), schema_pa)
                        writer.write_table(table)
                        total += len(batch)
                        count_arquivo += len(batch)
                        batch = []

                if batch:
                    table = pa.Table.from_pylist(batch, schema=schema_pa)
                    if writer is None:
                        saida_path.parent.mkdir(parents=True, exist_ok=True)
                        writer = pq.ParquetWriter(str(saida_path), schema_pa)
                    writer.write_table(table)
                    total += len(batch)
                    count_arquivo += len(batch)

                logger.info(f"{arquivo}: {count_arquivo} registros.")

            except Exception as e:
                logger.error(f"Falha CRÍTICA ao processar {arquivo}, pulando. Erro: {e}")
            finally:
                if caminho_dbf.exists():
                    caminho_dbf.unlink()
    finally:
        if writer is not None:
            writer.close()

    return total > 0


def _copiar_parquet_em_lotes(origem_path: Path, writer: pq.ParquetWriter):
    """Copia um Parquet inteiro pra dentro de um ParquetWriter já aberto,
    row-group por row-group -- nunca lê o arquivo inteiro em memória de
    uma vez só, independente do tamanho do arquivo de origem."""
    pf = pq.ParquetFile(origem_path)
    for i in range(pf.num_row_groups):
        writer.write_table(pf.read_row_group(i))


def processar_incremental_seguro(
    dbc_dir: Path,
    parquet_final_path: Path,
    colunas_fixas: list[str],
    coluna_data_referencia: str = "DTOBITO",
    batch_size: int = 50_000,
) -> bool:
    """
    Processa só os .dbc de anos ainda não presentes no Parquet final
    (identificados pelos 4 últimos dígitos de `coluna_data_referencia`),
    e faz a concatenação de forma SEGURA -- preservando o histórico já
    existente, em vez de sobrescrevê-lo (ParquetWriter sempre
    cria/sobrescreve o arquivo no caminho dado; não existe modo "append"
    nativo no PyArrow para Parquet).

    Memória: tanto o processamento dos arquivos novos quanto a cópia do
    histórico existente são feitos em lotes (linhas por vez / row-group
    por vez) -- nunca é necessário ter o Parquet antigo inteiro E o novo
    inteiro carregados ao mesmo tempo, mesmo em datasets de dezenas de
    milhões de linhas.

    Retorna True se algum dado novo foi escrito, False se não havia
    nada novo para processar.
    """
    if not dbc_dir.exists():
        logger.warning(f"Diretório não encontrado: {dbc_dir}.")
        return False

    arquivos_dbc = [f for f in os.listdir(dbc_dir) if f.lower().endswith(".dbc")]
    arquivos_dbc.sort()

    if not arquivos_dbc:
        logger.warning(f"Nenhum arquivo .dbc encontrado em {dbc_dir}.")
        return False

    ultimo_ano = None
    if parquet_final_path.exists():
        logger.info(f"Parquet existente encontrado: {parquet_final_path}. Verificando último ano...")
        # Lê só a coluna de referência (leve), não o arquivo inteiro.
        col_referencia = pq.read_table(
            parquet_final_path, columns=[coluna_data_referencia]
        ).column(coluna_data_referencia).to_pandas()

        anos = col_referencia.astype(str).str[-4:]
        anos_validos = anos[anos.str.isnumeric() & (anos.str.len() == 4)]

        if not anos_validos.empty:
            ultimo_ano = anos_validos.astype(int).max()
            logger.info(f"Último ano já presente no Parquet: {ultimo_ano}")

    if ultimo_ano is not None:
        arquivos_dbc = [
            f for f in arquivos_dbc
            if (m := re.search(r"(\d{4})", f)) and int(m.group(1)) > ultimo_ano
        ]

    if not arquivos_dbc:
        logger.info("Nenhum arquivo novo para processar (todos os anos já estão no Parquet).")
        return False

    logger.info(f"Arquivos a processar: {arquivos_dbc}")

    caminho_temp_novo = parquet_final_path.with_suffix(".novo.tmp.parquet")
    houve_dado = _processar_arquivos_para_parquet(dbc_dir, arquivos_dbc, colunas_fixas, caminho_temp_novo, batch_size)

    if not houve_dado:
        logger.warning("Nenhum registro novo foi extraído dos arquivos filtrados.")
        return False

    schema_pa = pa.schema([(nome, pa.string()) for nome in colunas_fixas])
    caminho_temp_final = parquet_final_path.with_suffix(".parquet.tmp")

    writer = pq.ParquetWriter(str(caminho_temp_final), schema_pa)
    try:
        if parquet_final_path.exists():
            logger.info("Copiando histórico existente para o novo arquivo (em lotes)...")
            _copiar_parquet_em_lotes(parquet_final_path, writer)
        logger.info("Copiando dados novos para o arquivo final (em lotes)...")
        _copiar_parquet_em_lotes(caminho_temp_novo, writer)
    finally:
        writer.close()

    caminho_temp_final.replace(parquet_final_path)  # troca atômica
    caminho_temp_novo.unlink()

    total_final = pq.ParquetFile(parquet_final_path).metadata.num_rows
    logger.info(f"✔ Parquet final atualizado: {parquet_final_path} ({total_final} registros totais)")
    return True


def _escrever_parquet_vazio(saida_path: Path, colunas: list[str]):
    schema = pa.schema([(c, pa.string()) for c in colunas])
    saida_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist([], schema=schema), saida_path)
    logger.info(f"Parquet vazio (0 linhas, schema padrão) escrito em: {saida_path}")


def _consolidar_parquets_temp_streaming(parquets_temp: list[Path], saida_path: Path):
    """
    Consolida os parquets temporários (um por arquivo/ano) num único
    arquivo final, unindo colunas entre eles -- SEM carregar todos na
    memória de uma vez. `pd.concat([pd.read_parquet(p) for p in ...])`
    já estourou memória em produção (CID-10: 29 anos, 5M+ linhas,
    colunas mudando de ano pra ano) -- lê o schema de cada arquivo
    primeiro (barato, não carrega dados), monta a união de colunas, e
    escreve incrementalmente com pyarrow.parquet.ParquetWriter, um
    arquivo de cada vez.
    """
    saida_path.parent.mkdir(parents=True, exist_ok=True)

    # 1ª passada: só o schema de cada arquivo (não carrega os dados)
    todas_colunas = []
    vistas = set()
    for p in parquets_temp:
        schema = pq.ParquetFile(p).schema_arrow
        for nome in schema.names:
            if nome not in vistas:
                vistas.add(nome)
                todas_colunas.append(nome)

    schema_unificado = pa.schema([(c, pa.string()) for c in todas_colunas])

    writer = pq.ParquetWriter(str(saida_path), schema_unificado)
    try:
        for p in parquets_temp:
            tabela = pq.read_table(p)
            colunas_alinhadas = {}
            for nome in todas_colunas:
                if nome in tabela.column_names:
                    coluna = tabela.column(nome)
                    if not pa.types.is_string(coluna.type) and not pa.types.is_large_string(coluna.type):
                        coluna = coluna.cast(pa.string())
                    colunas_alinhadas[nome] = coluna
                else:
                    colunas_alinhadas[nome] = pa.nulls(tabela.num_rows, type=pa.string())
            tabela_alinhada = pa.table(colunas_alinhadas, schema=schema_unificado)
            writer.write_table(tabela_alinhada)
            del tabela, tabela_alinhada  # libera a memória do arquivo atual antes do próximo
    finally:
        writer.close()


def processar_diretorio_dbc_filtrado(
    dbc_dir: Path,
    saida_path: Path,
    filtro_registro,
    colunas_padrao: list[str] | None = None,
    callback_arquivo=None,
) -> tuple[bool, list[dict]]:
    """
    Como processar_diretorio_dbc, mas aplica filtro_registro(dict) -> bool
    a CADA registro, ANTES de acumular no lote -- só o que passa no
    filtro chega a ser escrito no Parquet. Usado quando a base completa
    não tem propósito próprio (não vai ser publicada como produto à
    parte) e só o recorte filtrado interessa -- evita materializar em
    disco (e depois reler) dados que seriam descartados de qualquer jeito.

    filtro_registro recebe o dict cru retornado pelo dbfread para cada
    linha e decide se ela deve ser mantida.

    IMPORTANTE -- schema pode mudar entre anos: o layout de colunas do
    DATASUS às vezes muda mesmo dentro da mesma era de codificação (ex:
    SIM CID-9 ganhou as colunas RACACOR/ETNIA só a partir de 1995, não
    tinha nos anos anteriores). Por isso cada arquivo é escrito num
    Parquet temporário PRÓPRIO (schema livre, sem exigir bater com os
    outros anos), e a consolidação final usa pandas.concat, que une as
    colunas automaticamente (anos sem uma coluna que outros têm recebem
    NaN nela, em vez de quebrar o processamento inteiro daquele ano).

    colunas_padrao: se informado, e não houver nenhum .dbc pra processar
    OU nenhum registro passar no filtro, escreve um Parquet VAZIO (0
    linhas, mas com essas colunas) em vez de simplesmente não escrever
    nada. Isso importa pra fontes como SIM/PRELIM, que podem
    legitimamente ficar vazias entre ciclos de publicação do DATASUS --
    sem isso, um consumidor do dataset veria o arquivo de uma execução
    anterior parado no tempo, sem saber que "não tem nada novo agora" é
    diferente de "esqueceram de atualizar isso".

    Retorna (escreveu, detalhes) -- escreveu é True se algo foi escrito
    (mesmo vazio, quando colunas_padrao é informado); detalhes é uma
    lista de {"arquivo": str, "mantidos": int, "total": int} por .dbc
    processado, útil pra quem chama montar um resumo (ex: proporção de
    câncer sobre total de óbitos por ano) sem precisar reprocessar tudo
    de novo. O nome do arquivo já basta pra quem chama extrair o ano
    (a convenção de nome varia entre CID-9/CID-10, então isso fica a
    cargo de quem chama, não desta função).

    callback_arquivo: se informado, é chamado com o dict de detalhe de
    CADA arquivo logo depois dele terminar (sucesso ou falha) -- não só
    no final de tudo. Útil pra ir salvando progresso incrementalmente
    (ex: resumo anual ano a ano) em processamentos longos, sem perder
    tudo se o processo for interrompido no meio.
    """
    arquivos_dbc = []
    if dbc_dir.exists():
        arquivos_dbc = sorted(f for f in os.listdir(dbc_dir) if f.lower().endswith(".dbc"))

    if not arquivos_dbc:
        logger.warning(f"Nenhum arquivo .dbc encontrado em {dbc_dir}.")
        if colunas_padrao:
            _escrever_parquet_vazio(saida_path, colunas_padrao)
            return True, []
        return False, []

    temp_dir = saida_path.parent / f"_tmp_{saida_path.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    parquets_temp = []
    detalhes = []

    for arquivo in arquivos_dbc:
        caminho_dbc = dbc_dir / arquivo
        nome_base = os.path.splitext(arquivo)[0]
        caminho_dbf = dbc_dir / f"{nome_base}.dbf"
        temp_path = temp_dir / f"{nome_base}.parquet"

        if temp_path.exists():
            logger.info(f"--- {arquivo}: temporário já existe (de uma execução anterior) -- pulando reprocessamento. ---")
            parquets_temp.append(temp_path)
            continue

        logger.info(f"--- Processando (com filtro): {arquivo} ---")
        try:
            datasus_dbc.decompress(str(caminho_dbc), str(caminho_dbf))
            dbf_data = DBF(str(caminho_dbf), encoding="latin1")

            registros_filtrados = []
            count_arquivo = 0

            for record in dbf_data:
                count_arquivo += 1
                reg = dict(record)
                if filtro_registro(reg):
                    registros_filtrados.append({k: str(v).strip() for k, v in reg.items()})

            mantidos_arquivo = len(registros_filtrados)

            if registros_filtrados:
                pd.DataFrame(registros_filtrados).to_parquet(temp_path, index=False)
                parquets_temp.append(temp_path)

            detalhe = {"arquivo": arquivo, "mantidos": mantidos_arquivo, "total": count_arquivo}
            detalhes.append(detalhe)
            logger.info(f"{arquivo}: {mantidos_arquivo}/{count_arquivo} registros mantidos pelo filtro.")

            if callback_arquivo:
                callback_arquivo(detalhe)

        except Exception as e:
            logger.error(f"Falha CRÍTICA ao processar {arquivo}, pulando. Erro: {e}")
            detalhe = {"arquivo": arquivo, "mantidos": None, "total": None, "erro": str(e)}
            detalhes.append(detalhe)
            if callback_arquivo:
                callback_arquivo(detalhe)
        finally:
            if caminho_dbf.exists():
                caminho_dbf.unlink()

    total_mantidos = sum(d["mantidos"] for d in detalhes if d.get("mantidos") is not None)
    total_lidos = sum(d["total"] for d in detalhes if d.get("total") is not None)
    logger.info(f"Total: {total_mantidos}/{total_lidos} registros mantidos.")

    if parquets_temp:
        logger.info(f"Consolidando {len(parquets_temp)} arquivo(s) temporário(s) (unindo colunas entre anos)...")
        _consolidar_parquets_temp_streaming(parquets_temp, saida_path)
        for p in parquets_temp:
            p.unlink()
        temp_dir.rmdir()
        return True, detalhes

    temp_dir.rmdir()

    if colunas_padrao:
        _escrever_parquet_vazio(saida_path, colunas_padrao)
        return True, detalhes

    return total_mantidos > 0, detalhes