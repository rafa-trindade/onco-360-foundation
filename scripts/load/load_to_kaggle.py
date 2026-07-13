"""
Publica data/raw/ (inteiro, plano -- sem subpastas por fonte) no dataset
Kaggle rafatrindade/onco-360.

Diferente do flor-de-aco-foundation (que organiza por subpasta por
fonte), este projeto publica tudo direto na raiz do dataset -- mesma
estrutura que já estava publicada antes desta reestruturação
(raw_cnes_estabelecimentos.parquet, raw_painel_de_oncologia.parquet
etc., todos soltos).
"""
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from kaggle.api.kaggle_api_extended import KaggleApi
from dotenv import load_dotenv

from scripts.common.paths import BASE_DIR, RAW_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(BASE_DIR / ".env")

KAGGLE_JSON_PATH = BASE_DIR / ".kaggle" / "kaggle.json"
DATASET_NAME = "onco-360"


def preparar_pasta_dataset(raw_dir: Path) -> Path:
    """Copia todos os arquivos de data/raw/ (plano) pra uma pasta
    temporária de upload."""
    temp_folder = raw_dir.parent / "upload_tmp"
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
    temp_folder.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        logger.warning(f"Pasta '{raw_dir}' não encontrada. Nada para publicar.")
        return temp_folder

    arquivos = sorted(f for f in raw_dir.glob("*") if f.is_file() and f.name != ".gitkeep")

    logger.info(f"Copiando {len(arquivos)} arquivo(s) de {raw_dir}...")
    for src in arquivos:
        try:
            shutil.copy2(src, temp_folder / src.name)
        except Exception as e:
            logger.error(f"❌ Falha ao copiar '{src}': {e}")

    return temp_folder


def obter_metadata_existente(api: KaggleApi, dataset_id: str, temp_folder: Path) -> dict | None:
    """
    Se o dataset já existe, baixa o dataset-metadata.json ATUAL do
    Kaggle (título, descrição, tags/keywords etc.) -- sem isso,
    dataset_create_version() trata o metadata.json que a gente manda
    como a descrição COMPLETA e autoritativa do dataset, e qualquer
    campo omitido (como "keywords", onde ficam as tags) é APAGADO no
    Kaggle a cada publicação.

    Validação defensiva: só retorna se o conteúdo baixado for de fato
    um dict -- na prática, dataset_metadata() já devolveu formato
    inesperado (uma string) em vez do JSON de metadata esperado. Nesse
    caso, cai pro fallback (metadata mínimo, sem preservar tags desta
    vez) em vez de travar o load inteiro.
    """
    try:
        api.dataset_metadata(dataset_id, path=str(temp_folder))
        caminho = temp_folder / "dataset-metadata.json"
        if not caminho.exists():
            logger.warning("dataset_metadata() não gerou o arquivo esperado -- seguindo sem preservar metadata.")
            return None

        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)

        if isinstance(dados, str):
            # A API do Kaggle devolveu JSON duplamente codificado --
            # o arquivo continha uma STRING cujo conteúdo é o dict de
            # verdade (ex: '"{\\"datasetId\\": ...}"' em vez de
            # '{"datasetId": ...}'). Tenta decodificar mais uma vez
            # antes de desistir.
            try:
                dados = json.loads(dados)
            except (json.JSONDecodeError, TypeError):
                pass

        if not isinstance(dados, dict):
            logger.warning(
                f"Metadata existente veio num formato inesperado ({type(dados).__name__}, "
                f"não dict, mesmo após tentar decodificar 2x) -- seguindo sem preservar "
                f"tags/título/descrição desta vez. Conteúdo (primeiros 200 chars): {str(dados)[:200]!r}"
            )
            return None

        return dados

    except Exception as e:
        logger.warning(f"Não foi possível baixar o metadata existente do Kaggle: {e}")
        return None


def gerar_metadata(temp_folder: Path, dataset_id: str, metadata_existente: dict | None = None) -> Path:
    """Gera o dataset-metadata.json exigido pela API do Kaggle.

    Se houver metadata_existente (dataset já publicado antes), preserva
    TODOS os campos que já estavam lá (título, descrição, tags, licença
    etc.) -- só força o "id" (pra nunca publicar no dataset errado por
    engano) e reseta "resources" (deixa a API redetectar a partir dos
    arquivos realmente presentes na pasta de upload, evita referenciar
    arquivo antigo que não existe mais)."""
    metadata_path = temp_folder / "dataset-metadata.json"

    if metadata_existente:
        metadata = dict(metadata_existente)
        metadata["id"] = dataset_id
        metadata["resources"] = []
    else:
        metadata = {
            "id": dataset_id,
            "licenses": [{"name": "CC0-1.0"}],
            "resources": [],
        }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"Metadata criado em: {metadata_path} (preservando tags existentes: {bool(metadata_existente)})")
    return metadata_path


def load_raw_to_kaggle():
    with open(KAGGLE_JSON_PATH) as f:
        kaggle_creds = json.load(f)
    dataset_id = f"{kaggle_creds['username']}/{DATASET_NAME}"

    logger.info(f"Iniciando o carregamento para o Kaggle: {dataset_id}")

    api = KaggleApi()
    api.authenticate()

    temp_folder = preparar_pasta_dataset(RAW_DIR)

    try:
        try:
            api.dataset_list_files(dataset_id)
            dataset_existe = True
            logger.info(f"Dataset {dataset_id} já existe. Atualizando...")
        except Exception as e:
            if "404 - Not Found" in str(e):
                dataset_existe = False
                logger.info(f"Dataset {dataset_id} não existe. Criando...")
            else:
                raise

        metadata_existente = obter_metadata_existente(api, dataset_id, temp_folder) if dataset_existe else None
        gerar_metadata(temp_folder, dataset_id, metadata_existente)

        if dataset_existe:
            api.dataset_create_version(
                folder=str(temp_folder),
                version_notes=f"Update {datetime.now().strftime('%Y-%m-%d')}",
                delete_old_versions=True,
                quiet=False,
            )
            logger.info(f"✅ Dataset {dataset_id} atualizado com sucesso!")
        else:
            api.dataset_create_new(
                folder=str(temp_folder),
                public=True,
                quiet=False,
            )
            logger.info(f"✅ Dataset {dataset_id} criado com sucesso!")

    except Exception as e:
        logger.error(f"❌ Erro ao interagir com o Kaggle: {e}")
        raise
    finally:
        if temp_folder.exists():
            shutil.rmtree(temp_folder)
            logger.info(f"Pasta temporária '{temp_folder}' removida.")


if __name__ == "__main__":
    load_raw_to_kaggle()