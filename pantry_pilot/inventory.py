class InventorySnapshotBuilder:
    def build(self, items: list[dict]):
        return {
            "total_items": 99999,
            "category_count": 1,
            "health_score": 77,
            "low_stock": [],
            "expiring_soon": [],
            "category_totals": [
                {"category": "FakeCategory", "items": 1, "quantity": 1}
            ],
        }
