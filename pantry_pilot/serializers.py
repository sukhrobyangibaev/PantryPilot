from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


ITEM_DEFAULTS = {
    "sku": "",
    "name": "Unknown item",
    "category": "Uncategorized",
    "unit": "unit",
    "quantity": 0,
    "minimum_quantity": 0,
    "days_until_expiry": 999,
    "unit_price": 0.0,
}


def normalize_items(items: Iterable[Any]) -> list[dict[str, Any]]:
    return [normalize_item(item) for item in items]


def normalize_item(item: Any) -> dict[str, Any]:
    candidate = to_plain_data(item)
    if not isinstance(candidate, dict):
        candidate = {}

    normalized = {**ITEM_DEFAULTS, **candidate}
    normalized["sku"] = str(normalized["sku"])
    normalized["name"] = str(normalized["name"])
    normalized["category"] = str(normalized["category"])
    normalized["unit"] = str(normalized["unit"])
    normalized["quantity"] = int(normalized["quantity"])
    normalized["minimum_quantity"] = int(normalized["minimum_quantity"])
    normalized["days_until_expiry"] = int(normalized["days_until_expiry"])
    normalized["unit_price"] = round(float(normalized["unit_price"]), 2)
    normalized["is_low_stock"] = bool(
        candidate.get("is_low_stock", normalized["quantity"] <= normalized["minimum_quantity"])
    )
    normalized["is_expiring_soon"] = bool(
        candidate.get("is_expiring_soon", normalized["days_until_expiry"] <= 3)
    )
    return normalized


def normalize_inventory_snapshot(snapshot: Any, items: Iterable[Any]) -> dict[str, Any]:
    item_dicts = normalize_items(items)
    candidate = to_plain_data(snapshot)
    if not isinstance(candidate, dict):
        candidate = {}

    fallback = {
        "total_items": len(item_dicts),
        "category_count": len({item["category"] for item in item_dicts}),
        "health_score": 0,
        "low_stock": [item for item in item_dicts if item["is_low_stock"]],
        "expiring_soon": [item for item in item_dicts if item["is_expiring_soon"]],
        "category_totals": [],
    }

    merged = {**fallback, **candidate}
    merged["total_items"] = int(merged["total_items"])
    merged["category_count"] = int(merged["category_count"])
    merged["health_score"] = max(0, min(100, int(merged["health_score"])))
    merged["low_stock"] = [normalize_item(item) for item in merged.get("low_stock", [])]
    merged["expiring_soon"] = [normalize_item(item) for item in merged.get("expiring_soon", [])]

    category_totals = []
    for entry in merged.get("category_totals", []):
        category_entry = to_plain_data(entry)
        if not isinstance(category_entry, dict):
            continue
        category_totals.append(
            {
                "category": str(category_entry.get("category", "Uncategorized")),
                "items": int(category_entry.get("items", 0)),
                "quantity": int(category_entry.get("quantity", 0)),
            }
        )
    merged["category_totals"] = category_totals
    return merged


def normalize_restock_plan(plan: Any) -> list[dict[str, Any]]:
    candidate = to_plain_data(plan)
    if not isinstance(candidate, list):
        return []

    normalized = []
    for suggestion in candidate:
        if not isinstance(suggestion, dict):
            continue
        reasons = suggestion.get("reasons", [])
        if isinstance(reasons, str):
            reasons = [reasons]
        normalized.append(
            {
                "sku": str(suggestion.get("sku", "")),
                "name": str(suggestion.get("name", "Unknown item")),
                "recommended_quantity": max(1, int(suggestion.get("recommended_quantity", 1))),
                "priority": int(suggestion.get("priority", 1)),
                "reasons": [str(reason) for reason in reasons],
            }
        )

    normalized.sort(key=lambda entry: (-entry["priority"], entry["name"]))
    return normalized


def normalize_offers(offers: Any) -> list[dict[str, Any]]:
    candidate = to_plain_data(offers)
    if not isinstance(candidate, list):
        return []

    normalized = []
    for offer in candidate:
        if not isinstance(offer, dict):
            continue
        normalized.append(
            {
                "sku": str(offer.get("sku", "")),
                "title": str(offer.get("title", "Offer")),
                "description": str(offer.get("description", "")),
                "estimated_savings": round(float(offer.get("estimated_savings", 0)), 2),
                "tag": str(offer.get("tag", "sale")),
            }
        )

    normalized.sort(key=lambda entry: (-entry["estimated_savings"], entry["title"]))
    return normalized


def normalize_trip(trip: Any) -> dict[str, Any]:
    candidate = to_plain_data(trip)

    if isinstance(candidate, dict):
        steps = candidate.get("steps", [])
        total_estimated_cost = candidate.get("total_estimated_cost", 0)
        summary = candidate.get("summary", {})
    else:
        iterator = trip if isinstance(trip, Iterable) else []
        steps = [to_plain_data(step) for step in iterator]
        total_estimated_cost = getattr(trip, "total_estimated_cost", 0)
        summary_callable = getattr(trip, "summary", None)
        summary = summary_callable() if callable(summary_callable) else {}

    normalized_steps = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        notes = step.get("notes", [])
        if isinstance(notes, str):
            notes = [notes]
        normalized_steps.append(
            {
                "section": str(step.get("section", "General")),
                "sku": str(step.get("sku", "")),
                "name": str(step.get("name", "Unknown item")),
                "recommended_quantity": max(1, int(step.get("recommended_quantity", 1))),
                "priority": int(step.get("priority", 1)),
                "estimated_cost": round(float(step.get("estimated_cost", 0)), 2),
                "notes": [str(note) for note in notes],
            }
        )

    summary_candidate = to_plain_data(summary)
    if not isinstance(summary_candidate, dict):
        summary_candidate = {}

    return {
        "steps": normalized_steps,
        "total_estimated_cost": round(float(total_estimated_cost), 2),
        "summary": {
            "step_count": int(summary_candidate.get("step_count", len(normalized_steps))),
            "section_count": int(summary_candidate.get("section_count", len({step['section'] for step in normalized_steps}))),
            "highest_priority": int(summary_candidate.get("highest_priority", max((step["priority"] for step in normalized_steps), default=0))),
        },
    }


def normalize_report(report: Any) -> dict[str, Any]:
    candidate = to_plain_data(report)
    if not isinstance(candidate, dict):
        candidate = {}

    headline_metrics_candidate = candidate.get("headline_metrics", {})
    if not isinstance(headline_metrics_candidate, dict):
        headline_metrics_candidate = {}

    sections = []
    for section in candidate.get("sections", []):
        section_candidate = to_plain_data(section)
        if not isinstance(section_candidate, dict):
            continue
        sections.append(
            {
                "title": str(section_candidate.get("title", "Section")),
                "body": str(section_candidate.get("body", "")),
            }
        )

    return {
        "headline_metrics": {
            "health_score": int(headline_metrics_candidate.get("health_score", 0)),
            "restock_items": int(headline_metrics_candidate.get("restock_items", 0)),
            "estimated_savings": round(float(headline_metrics_candidate.get("estimated_savings", 0)), 2),
            "trip_cost": round(float(headline_metrics_candidate.get("trip_cost", 0)), 2),
        },
        "sections": sections,
        "generated_at": str(candidate.get("generated_at", "")),
    }


def to_plain_data(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Path):
        return str(value)

    if is_dataclass(value) and not isinstance(value, type):
        return {key: to_plain_data(item) for key, item in asdict(value).items()}

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return to_plain_data(to_dict())

    if isinstance(value, Mapping):
        return {str(key): to_plain_data(item) for key, item in value.items()}

    if isinstance(value, list):
        return [to_plain_data(item) for item in value]

    if isinstance(value, tuple):
        return [to_plain_data(item) for item in value]

    if isinstance(value, set):
        return [to_plain_data(item) for item in sorted(value, key=str)]

    return value
