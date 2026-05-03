from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_ROOT = PROJECT_ROOT / "pantry_pilot"
DATA_ROOT = PROJECT_ROOT / "data"
GENERATED_DATA_ROOT = DATA_ROOT / "generated"

__all__ = [
    "DATA_ROOT",
    "GENERATED_DATA_ROOT",
    "PACKAGE_ROOT",
    "PROJECT_ROOT",
]
