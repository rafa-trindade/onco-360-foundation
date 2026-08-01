"""Caminhos base com override via .env.

Ciclo de vida estrutural:
- Efêmeros (scratch, expurgados pós-publicação): LANDING_DIR, PROCESSED_DIR.
- Persistentes: MANUAL_DIR, PUBLISH_CACHE_DIR.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# load_dotenv mandatório neste escopo (além do env.py) para contornar o cache de 
# importação do Python e garantir injeção dos overrides.
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"


def _dir_com_override(env_var: str, padrao: Path) -> Path:
    override = os.environ.get(env_var)
    return Path(override) if override else padrao


LANDING_DIR = _dir_com_override("LANDING_DIR", DATA_DIR / "landing")
PROCESSED_DIR = _dir_com_override("PROCESSED_DIR", DATA_DIR / "processed")
MANUAL_DIR = _dir_com_override("MANUAL_DIR", DATA_DIR / "manual")
PUBLISH_CACHE_DIR = _dir_com_override("PUBLISH_CACHE_DIR", DATA_DIR / "kaggle_publish_cache")
DUCKDB_TEMP_DIR = _dir_com_override("DUCKDB_TEMP_DIR", DATA_DIR / ".duckdb_temp")

MANUAL_MACROREGIAO_DIR = MANUAL_DIR / "macroregiao"
MANUAL_INCA_DIR = MANUAL_DIR / "inca"
MANUAL_PNS_DIR = MANUAL_DIR / "ibge" / "pns"
MANUAL_DATASUS_REF_DIR = MANUAL_DIR / "datasus_referencias"

for _dir in (LANDING_DIR, PROCESSED_DIR, MANUAL_DIR, PUBLISH_CACHE_DIR, DUCKDB_TEMP_DIR,
             MANUAL_MACROREGIAO_DIR, MANUAL_INCA_DIR, MANUAL_PNS_DIR, MANUAL_DATASUS_REF_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
