from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Callable

from pantry_pilot import DATA_ROOT, GENERATED_DATA_ROOT
from pantry_pilot import fallbacks


JsonFactory = Callable[[], Any]


def load_pantry_items(logger: logging.Logger | None = None) -> list[dict[str, Any]]:
    return list(_load_json_data(DATA_ROOT / "pantry.json", fallbacks.fallback_pantry_items, "pantry items", logger))


def load_catalog(logger: logging.Logger | None = None) -> list[dict[str, Any]]:
    return list(_load_json_data(DATA_ROOT / "catalog.json", fallbacks.fallback_catalog, "catalog", logger))


def load_preferences(logger: logging.Logger | None = None) -> dict[str, Any]:
    return dict(_load_json_data(DATA_ROOT / "preferences.json", fallbacks.fallback_preferences, "preferences", logger))


def load_aisle_map(logger: logging.Logger | None = None) -> dict[str, Any]:
    return dict(_load_json_data(DATA_ROOT / "aisle_map.json", fallbacks.fallback_aisle_map, "aisle map", logger))


def read_latest_report_preview(logger: logging.Logger | None = None) -> str | None:
    path = GENERATED_DATA_ROOT / "latest_report.txt"
    if not path.exists():
        return None

    try:
        return path.read_text(encoding="utf-8").strip() or None
    except OSError as exc:
        _get_logger(logger).warning("Could not read latest report preview from %s: %s", path, exc)
        return None


def _load_json_data(
    path: Path,
    fallback_factory: JsonFactory,
    label: str,
    logger: logging.Logger | None,
) -> Any:
    if not path.exists():
        _get_logger(logger).info("Using built-in fallback %s because %s is missing.", label, path)
        return fallback_factory()

    try:
        with path.open("r", encoding="utf-8") as file_handle:
            return json.load(file_handle)
    except (json.JSONDecodeError, OSError) as exc:
        _get_logger(logger).warning("Using built-in fallback %s because %s could not be loaded: %s", label, path, exc)
        return fallback_factory()


def _get_logger(logger: logging.Logger | None) -> logging.Logger:
    return logger or logging.getLogger("pantry_pilot")
