from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any


def fallback_pantry_items() -> list[dict[str, Any]]:
    return [
        {
            "sku": "MILK-2L",
            "name": "Whole Milk",
            "category": "Dairy",
            "unit": "carton",
            "quantity": 1,
            "minimum_quantity": 2,
            "days_until_expiry": 2,
            "unit_price": 3.79,
        },
        {
            "sku": "EGGS-12",
            "name": "Free-Range Eggs",
            "category": "Dairy",
            "unit": "dozen",
            "quantity": 1,
            "minimum_quantity": 1,
            "days_until_expiry": 6,
            "unit_price": 4.99,
        },
        {
            "sku": "RICE-1KG",
            "name": "Jasmine Rice",
            "category": "Grains",
            "unit": "bag",
            "quantity": 0,
            "minimum_quantity": 1,
            "days_until_expiry": 180,
            "unit_price": 5.49,
        },
        {
            "sku": "PASTA-500",
            "name": "Penne Pasta",
            "category": "Grains",
            "unit": "box",
            "quantity": 1,
            "minimum_quantity": 2,
            "days_until_expiry": 240,
            "unit_price": 2.39,
        },
        {
            "sku": "BEANS-BLK",
            "name": "Black Beans",
            "category": "Canned Goods",
            "unit": "can",
            "quantity": 2,
            "minimum_quantity": 3,
            "days_until_expiry": 120,
            "unit_price": 1.69,
        },
        {
            "sku": "SPINACH-BX",
            "name": "Baby Spinach",
            "category": "Produce",
            "unit": "box",
            "quantity": 1,
            "minimum_quantity": 1,
            "days_until_expiry": 1,
            "unit_price": 3.29,
        },
    ]


def fallback_catalog() -> list[dict[str, Any]]:
    return [
        {
            "sku": "MILK-2L",
            "name": "Whole Milk",
            "category": "Dairy",
            "unit": "carton",
            "unit_price": 3.79,
        },
        {
            "sku": "EGGS-12",
            "name": "Free-Range Eggs",
            "category": "Dairy",
            "unit": "dozen",
            "unit_price": 4.99,
        },
        {
            "sku": "RICE-1KG",
            "name": "Jasmine Rice",
            "category": "Grains",
            "unit": "bag",
            "unit_price": 5.49,
        },
        {
            "sku": "PASTA-500",
            "name": "Penne Pasta",
            "category": "Grains",
            "unit": "box",
            "unit_price": 2.39,
        },
        {
            "sku": "BEANS-BLK",
            "name": "Black Beans",
            "category": "Canned Goods",
            "unit": "can",
            "unit_price": 1.69,
        },
        {
            "sku": "SPINACH-BX",
            "name": "Baby Spinach",
            "category": "Produce",
            "unit": "box",
            "unit_price": 3.29,
        },
        {
            "sku": "TOMATO-6",
            "name": "Roma Tomatoes",
            "category": "Produce",
            "unit": "pack",
            "unit_price": 2.89,
        },
    ]


def fallback_preferences() -> dict[str, Any]:
    return {
        "shopping_day_in_days": 2,
        "weekend_cooking": True,
        "household_size": 4,
        "budget_focus": "balanced",
    }


def fallback_aisle_map() -> dict[str, Any]:
    return {
        "section_order": [
            "Produce Market",
            "Dairy Aisle",
            "Grains & Pasta",
            "Canned Goods",
            "Household Staples",
        ],
        "sku_sections": {
            "MILK-2L": "Dairy Aisle",
            "EGGS-12": "Dairy Aisle",
            "RICE-1KG": "Grains & Pasta",
            "PASTA-500": "Grains & Pasta",
            "BEANS-BLK": "Canned Goods",
            "SPINACH-BX": "Produce Market",
            "TOMATO-6": "Produce Market",
        },
        "category_sections": {
            "Produce": "Produce Market",
            "Dairy": "Dairy Aisle",
            "Grains": "Grains & Pasta",
            "Canned Goods": "Canned Goods",
        },
    }


def build_inventory_snapshot(items: list[dict[str, Any]]) -> dict[str, Any]:
    low_stock = []
    expiring_soon = []
    category_totals: dict[str, dict[str, Any]] = defaultdict(lambda: {"items": 0, "quantity": 0})

    for item in items:
        category = str(item.get("category", "Uncategorized"))
        quantity = int(item.get("quantity", 0))
        minimum_quantity = int(item.get("minimum_quantity", 0))
        days_until_expiry = int(item.get("days_until_expiry", 999))

        category_totals[category]["items"] += 1
        category_totals[category]["quantity"] += quantity

        item_summary = {
            "sku": item.get("sku", ""),
            "name": item.get("name", "Unknown item"),
            "category": category,
            "quantity": quantity,
            "minimum_quantity": minimum_quantity,
            "days_until_expiry": days_until_expiry,
        }

        if quantity <= minimum_quantity:
            low_stock.append(item_summary)
        if days_until_expiry <= 3:
            expiring_soon.append(item_summary)

    health_score = max(0, 100 - (len(low_stock) * 15) - (len(expiring_soon) * 10))
    ordered_categories = sorted(
        (
            {
                "category": category,
                "items": totals["items"],
                "quantity": totals["quantity"],
            }
            for category, totals in category_totals.items()
        ),
        key=lambda entry: (-entry["items"], -entry["quantity"], entry["category"]),
    )

    return {
        "total_items": len(items),
        "category_count": len(category_totals),
        "health_score": health_score,
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
        "category_totals": ordered_categories,
    }


def build_restock_plan(
    items: list[dict[str, Any]],
    catalog: list[dict[str, Any]],
    preferences: dict[str, Any],
) -> list[dict[str, Any]]:
    catalog_by_sku = {entry.get("sku"): entry for entry in catalog}
    plan: dict[str, dict[str, Any]] = {}
    next_shop = int(preferences.get("shopping_day_in_days", 2))
    weekend_cooking = bool(preferences.get("weekend_cooking", False))

    for item in items:
        sku = str(item.get("sku", ""))
        if not sku:
            continue

        quantity = int(item.get("quantity", 0))
        minimum_quantity = int(item.get("minimum_quantity", 0))
        reasons: list[str] = []
        priority = 1

        if quantity <= minimum_quantity:
            reasons.append("Low stock")
            priority = max(priority, 3)

        if int(item.get("days_until_expiry", 999)) <= next_shop:
            reasons.append("May run out before the next shopping day")
            priority = max(priority, 2)

        category = str(item.get("category", ""))
        if weekend_cooking and category in {"Grains", "Canned Goods"}:
            reasons.append("Weekend cooking plan")
            priority = max(priority, 2)

        if not reasons:
            continue

        recommended_quantity = max(1, minimum_quantity - quantity + 1)
        catalog_entry = catalog_by_sku.get(sku, {})
        plan[sku] = {
            "sku": sku,
            "name": item.get("name") or catalog_entry.get("name") or "Unknown item",
            "recommended_quantity": recommended_quantity,
            "priority": priority,
            "reasons": reasons,
        }

    return sorted(plan.values(), key=lambda entry: (-int(entry["priority"]), str(entry["name"])))


def build_offers(items: list[Any]) -> list[dict[str, Any]]:
    offers: list[dict[str, Any]] = []

    for item in items:
        item_dict = _item_to_dict(item)
        sku = str(item_dict.get("sku", ""))
        if not sku:
            continue

        category = str(item_dict.get("category", ""))
        quantity = int(item_dict.get("quantity", 0))
        minimum_quantity = int(item_dict.get("minimum_quantity", 0))
        unit_price = float(item_dict.get("unit_price", 0))
        expiry_days = int(item_dict.get("days_until_expiry", 999))

        if category in {"Grains", "Canned Goods"}:
            offers.append(
                {
                    "sku": sku,
                    "title": f"Staple sale on {item_dict.get('name', 'this item')}",
                    "description": "Save 10% on pantry staples this week.",
                    "estimated_savings": round(unit_price * 0.10, 2),
                    "tag": "sale",
                }
            )

        if quantity < max(1, minimum_quantity - 1):
            offers.append(
                {
                    "sku": sku,
                    "title": f"Bundle refill for {item_dict.get('name', 'this item')}",
                    "description": "Buy a bundle now to rebuild your pantry buffer.",
                    "estimated_savings": round(unit_price * 0.15, 2),
                    "tag": "bundle",
                }
            )

        if expiry_days <= 3:
            offers.append(
                {
                    "sku": sku,
                    "title": f"Use {item_dict.get('name', 'this item')} first",
                    "description": "Plan meals around this item before buying more.",
                    "estimated_savings": round(unit_price, 2),
                    "tag": "use-first",
                }
            )

    return sorted(offers, key=lambda entry: (-float(entry["estimated_savings"]), str(entry["title"])))


def build_trip(
    items: list[Any],
    restock_plan: list[dict[str, Any]],
    offers: list[dict[str, Any]],
    aisle_map: dict[str, Any],
) -> dict[str, Any]:
    items_by_sku = {item.get("sku"): item for item in (_item_to_dict(entry) for entry in items)}
    offer_notes: dict[str, list[str]] = defaultdict(list)
    for offer in offers:
        offer_notes[str(offer.get("sku", ""))].append(str(offer.get("title", "")))

    steps: list[dict[str, Any]] = []
    section_order = list(aisle_map.get("section_order", []))
    category_sections = dict(aisle_map.get("category_sections", {}))
    sku_sections = dict(aisle_map.get("sku_sections", {}))

    for suggestion in restock_plan:
        sku = str(suggestion.get("sku", ""))
        item = items_by_sku.get(sku, {})
        section = sku_sections.get(sku) or category_sections.get(item.get("category"), "General")
        estimated_cost = round(float(item.get("unit_price", 0)) * int(suggestion.get("recommended_quantity", 1)), 2)
        steps.append(
            {
                "section": section,
                "sku": sku,
                "name": suggestion.get("name", item.get("name", "Unknown item")),
                "recommended_quantity": int(suggestion.get("recommended_quantity", 1)),
                "priority": int(suggestion.get("priority", 1)),
                "estimated_cost": estimated_cost,
                "notes": list(dict.fromkeys(list(suggestion.get("reasons", [])) + offer_notes.get(sku, []))),
            }
        )

    order_lookup = {section: index for index, section in enumerate(section_order)}
    steps.sort(key=lambda step: (order_lookup.get(step["section"], len(order_lookup)), -step["priority"], step["name"]))

    total_estimated_cost = round(sum(step["estimated_cost"] for step in steps), 2)
    section_counter = Counter(step["section"] for step in steps)

    return {
        "steps": steps,
        "total_estimated_cost": total_estimated_cost,
        "summary": {
            "step_count": len(steps),
            "section_count": len(section_counter),
            "highest_priority": max((step["priority"] for step in steps), default=0),
        },
    }


def build_report(context: dict[str, Any]) -> dict[str, Any]:
    inventory = context.get("inventory", {})
    offers = context.get("offers", {})
    restock_plan = context.get("restock_plan", [])
    trip = context.get("trip", {})

    headline_metrics = {
        "health_score": int(inventory.get("health_score", 0)),
        "restock_items": len(restock_plan),
        "estimated_savings": round(float(offers.get("total_estimated_savings", 0)), 2),
        "trip_cost": round(float(trip.get("total_estimated_cost", 0)), 2),
    }

    sections = [
        {
            "title": "Waste Risk",
            "body": f"{len(inventory.get('expiring_soon', []))} pantry items need attention in the next few days.",
        },
        {
            "title": "Savings Opportunities",
            "body": f"Current offers could save about ${headline_metrics['estimated_savings']:.2f} on the next trip.",
        },
        {
            "title": "Restock Coverage",
            "body": f"The current plan covers {headline_metrics['restock_items']} items across {trip.get('summary', {}).get('section_count', 0)} store sections.",
        },
    ]

    return {
        "headline_metrics": headline_metrics,
        "sections": sections,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def build_report_preview(report: dict[str, Any]) -> str:
    headline_metrics = report.get("headline_metrics", {})
    lines = [
        "PantryPilot Latest Report",
        "",
        f"Health score: {headline_metrics.get('health_score', 0)}",
        f"Restock items: {headline_metrics.get('restock_items', 0)}",
        f"Estimated savings: ${float(headline_metrics.get('estimated_savings', 0)):.2f}",
        f"Trip cost: ${float(headline_metrics.get('trip_cost', 0)):.2f}",
        "",
    ]

    for section in report.get("sections", []):
        lines.append(str(section.get("title", "Section")))
        lines.append(str(section.get("body", "")))
        lines.append("")

    return "\n".join(lines).strip()


def _item_to_dict(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        return item
    to_dict = getattr(item, "to_dict", None)
    if callable(to_dict):
        value = to_dict()
        if isinstance(value, dict):
            return value
    return {
        "sku": getattr(item, "sku", ""),
        "name": getattr(item, "name", "Unknown item"),
        "category": getattr(item, "category", "Uncategorized"),
        "unit": getattr(item, "unit", "unit"),
        "quantity": getattr(item, "quantity", 0),
        "minimum_quantity": getattr(item, "minimum_quantity", 0),
        "days_until_expiry": getattr(item, "days_until_expiry", 999),
        "unit_price": getattr(item, "unit_price", 0),
    }
