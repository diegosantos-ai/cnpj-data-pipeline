# src/pipeline_config.py
from __future__ import annotations
import os
from dataclasses import dataclass

def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return default if v is None or v == "" else int(v)

def _get_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return default if v is None or v == "" else v

@dataclass(frozen=True)
class PipelineConfig:
    mode: str
    sample_files_per_type: int
    sample_rows: int
    sample_seed: int
    sample_output_dir: str
    sample_force: bool
    sample_strategy: str

def load_config() -> PipelineConfig:
    mode = _get_str("PIPELINE_MODE", "full").lower()
    if mode not in ("full", "sample"):
        mode = "full"

    return PipelineConfig(
        mode=mode,
        sample_files_per_type=_get_int("SAMPLE_FILES_PER_TYPE", 1),
        sample_rows=_get_int("SAMPLE_ROWS", 50_000),
        sample_seed=_get_int("SAMPLE_SEED", 42),
        sample_output_dir=_get_str("SAMPLE_OUTPUT_DIR", "processed_sample"),
        sample_force=_get_str("SAMPLE_FORCE", "0") in ("1", "true", "True"),
        sample_strategy=_get_str("SAMPLE_STRATEGY", "head").lower(),
    )
