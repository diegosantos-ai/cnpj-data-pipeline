from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def _default_data_root() -> Path:
    # útil só para testes/amostras se DATA_ROOT não estiver setado
    return PROJECT_ROOT / "data"

# Lê DATA_ROOT do ambiente (.env) e evita fallback silencioso quando a var existe
DATA_ROOT = Path(os.getenv("DATA_ROOT", str(_default_data_root()))).expanduser()

RAW_DIR = DATA_ROOT / "raw"
PROCESSED_DIR = DATA_ROOT / "processed"
SAMPLE_DIR = DATA_ROOT / "processed_sample"
TMP_DIR = DATA_ROOT / "tmp"

def validate_data_root() -> None:
    """
    Se DATA_ROOT foi definido, falha explicitamente se o drive externo não existir.
    Evita cair no fallback e lotar o C: por acidente.
    """
    if os.getenv("DATA_ROOT"):
        drive = Path(DATA_ROOT.anchor)  # ex.: "D:\\"
        if not drive.exists():
            raise RuntimeError(
                f"DATA_ROOT aponta para um drive indisponível: {drive}. "
                f"Conecte o HD externo e verifique a letra do drive."
            )

def ensure_dirs() -> None:
    for p in (RAW_DIR, PROCESSED_DIR, TMP_DIR, SAMPLE_DIR):
        p.mkdir(parents=True, exist_ok=True)

SAMPLE_DIR = DATA_ROOT / "processed_sample"


