"""
Caminhos centrais do projeto, usados por todos os módulos de extract/process/load.

Mesma convenção do flor-de-aco-foundation: um único lugar define
BASE_DIR/DATA_DIR/LANDING_DIR/RAW_DIR, em vez de cada fonte redefinir
isso do zero no seu próprio base_*.py.

Diferente do flor-de-aco-foundation, este projeto publica em formato
"flat": os arquivos finais ficam direto em data/raw/<nome>.parquet
(sem subpastas por fonte), pra bater com a estrutura já publicada em
kaggle.com/datasets/rafatrindade/onco-360.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"

_landing_override = os.environ.get("LANDING_DIR")
_raw_override = os.environ.get("RAW_DIR")

LANDING_DIR = Path(_landing_override) if _landing_override else DATA_DIR / "landing"
RAW_DIR = Path(_raw_override) if _raw_override else DATA_DIR / "raw"

LANDING_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)