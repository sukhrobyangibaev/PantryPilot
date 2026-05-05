# PantryPilot

PantryPilot is a smart pantry dashboard for people who want to waste less food, avoid surprise grocery runs, and spot savings before they shop. The app already includes the full interface, sample pantry data, and Flask routes. Your job is to write the Python that powers the dashboard so the browser can show inventory health, restock advice, savings opportunities, a guided shopping trip, and a final insights report.

## Setup

```bash
git clone <REPO_URL>
cd pantry-pilot
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 in your browser.

## Tasks

### Task 1 (Easy): Inventory Health Snapshot
**File:** `pantry_pilot/inventory.py`

Analyze raw pantry data and produce a single summary dictionary for the dashboard.

1. Create a class `InventorySnapshotBuilder` with one clear responsibility: inventory analysis.
2. Add a public method `build(items)` that accepts a list of item dictionaries from the seed data and returns a dictionary with these keys: `total_items`, `category_count`, `health_score`, `low_stock`, `expiring_soon`, and `category_totals`.
3. Mark an item as **low stock** when `quantity <= minimum_quantity`.
4. Mark an item as **expiring soon** when `days_until_expiry <= 3`.
5. Compute `health_score` as an integer from 0 to 100 that drops as the number of low-stock and expiring items increases.
   - Example formula: `max(0, 100 - (len(low_stock) * 15) - (len(expiring_soon) * 10))`.
6. Make `low_stock` and `expiring_soon` lists of dictionaries that include at least the item name, category, current quantity, and minimum quantity.
7. Sort `category_totals` from the largest category to the smallest so the UI can render the busiest sections first.

**Expected return shape from `build(items)`:**

```python
{
    "total_items": 6,
    "category_count": 4,
    "health_score": 0,
    "low_stock": [
        {
            "name": "Whole Milk",
            "category": "Dairy",
            "quantity": 1,
            "minimum_quantity": 2,
            "days_until_expiry": 2,
            "unit": "carton",
        }
    ],
    "expiring_soon": [...],
    "category_totals": [
        {"category": "Dairy", "items": 2, "quantity": 2},
        {"category": "Grains", "items": 2, "quantity": 1},
    ],
}
```

**Verify:** The overview cards at the top of the dashboard show real counts, the low-stock list fills in, and the category summary is no longer empty.

---

### Task 2 (Easy): Extensible Restock Advisor
**File:** `pantry_pilot/restock.py`

Build a restock system that follows Open/Closed and Dependency Inversion.

#### Step 1 — Abstract base class

Create an abstract base class named `RestockRule`.

It must define one abstract method called `suggest` that accepts three positional arguments — `items` (a list of pantry item dicts from `data/pantry.json`), `catalog` (a list of catalog entry dicts from `data/catalog.json`), and `preferences` (the household preferences dict from `data/preferences.json`) — and returns a list of **suggestion dictionaries** (see Step 3 for the shape).

#### Step 2 — Three concrete rule classes

Define exactly these three subclasses of `RestockRule`. Each one implements `suggest(...)` and returns a list of suggestion dicts.

**Class `LowStockRule`** — the highest-priority rule (priority three).
- For every item whose `quantity` is equal to or below its `minimum_quantity`, produce one suggestion.
- Reason string: `f"Low stock: only {quantity} left (minimum {minimum_quantity})"`.

**Class `ExpiringSoonRule`** — medium priority (priority two).
- Read the `shopping_day_in_days` value from `preferences`, defaulting to seven if it is missing.
- For every item whose `days_until_expiry` is equal to or less than that threshold, produce one suggestion.
- Reason string: `f"Expires in {days_until_expiry} days (before next shopping trip)"`.

**Class `WeekendCookingRule`** — the lowest-priority rule (priority one).
- If the `weekend_cooking` preference is falsy, return an empty list.
- Otherwise, for every item whose `category` is Produce, Meat, or Dairy, produce one suggestion.
- Reason string: `"Weekend cooking planned — keep this stocked"`.

#### Step 3 — Suggestion dictionary shape

Each suggestion returned by `suggest(...)` must be a dict with exactly these keys:

```python
{
    "sku": item["sku"],
    "name": item["name"],
    "recommended_quantity": max(1, item["minimum_quantity"] - item["quantity"] + 1),
    "priority": <rule priority: 3, 2, or 1>,
    "reasons": [<one reason string>],   # always a list with one string
}
```

#### Step 4 — `RestockAdvisor` class

Create a class `RestockAdvisor` whose constructor accepts a list of `rules` and stores it. It must expose a `build_plan` method that takes `items`, `catalog`, and `preferences` and returns a list of suggestion dicts.

Inside `build_plan`:

1. Create an empty dict `merged` keyed by `sku`.
2. Loop over every rule in `self.rules` and call its `suggest` method with `items`, `catalog`, and `preferences`, then loop over the returned suggestions.
   - Use the shared `suggest` interface — **do not** check rule class names with `isinstance` or `if`/`elif`.
3. For each suggestion, merge by `sku`:
   - If the `sku` is new, add it to `merged`.
   - If the `sku` already exists, update the existing entry:
     - Keep the higher of the two `priority` values.
     - Keep the higher of the two `recommended_quantity` values.
     - Concatenate the new `reasons` onto the existing `reasons` list.
4. Return the merged suggestions sorted by `priority` descending first, then by `name` ascending.

#### Expected return shape from `build_plan(...)`

```python
[
    {
        "sku": "MILK-2L",
        "name": "Whole Milk",
        "recommended_quantity": 2,
        "priority": 3,
        "reasons": [
            "Low stock: only 1 left (minimum 2)",
            "Expires in 2 days (before next shopping trip)",
        ],
    }
]
```

#### Verify

The restock panel shows suggested items, each card explains why it was suggested, and higher-priority items appear first.

---

### Task 3 (Medium): Robust Pantry Domain Model
**File:** `pantry_pilot/models.py`

Replace loose dictionaries with a proper domain object so the rest of the app gets easier to extend, not harder.

1. Implement a custom exception named `InvalidPantryItemError`.
2. Implement a `PantryItem` dataclass with type hints for `sku`, `name`, `category`, `unit`, `quantity`, `minimum_quantity`, `days_until_expiry`, and `unit_price`.
3. Validate inputs and **raise `InvalidPantryItemError`** when validation fails:
   - Numeric values must never be negative.
   - Text fields must not be blank.
4. Normalize text fields so the UI does not show inconsistent labels:
   - `category` → `.strip().title()`
   - `unit` → `.strip().lower()`
5. Add these computed properties:
   - `is_low_stock`: `True` when `quantity <= minimum_quantity`.
   - `is_expiring_soon`: `True` when `days_until_expiry <= 3`.
   - `restock_amount`: `max(1, minimum_quantity - quantity + 1)` (rebuilds the buffer).
   - `estimated_restock_cost`: `restock_amount * unit_price`, rounded to 2 decimals.
6. Add a `from_dict` classmethod that turns raw JSON data into a `PantryItem`.
7. Add a `to_dict` method that converts the object back into a UI-friendly dictionary.
   - Include all 8 base fields plus the 4 computed properties from step 5.
8. Add a readable `__str__` implementation that would make sense in logs or debugging output.

**Expected return shape from `to_dict()`:**

```python
{
    "sku": "MILK-2L",
    "name": "Whole Milk",
    "category": "Dairy",
    "unit": "carton",
    "quantity": 1,
    "minimum_quantity": 2,
    "days_until_expiry": 2,
    "unit_price": 3.79,
    "is_low_stock": True,
    "is_expiring_soon": True,
    "restock_amount": 2,
    "estimated_restock_cost": 7.58,
}
```

**Verify:** Inventory labels become cleaner and more consistent, restock quantities become more accurate, and invalid pantry data is handled gracefully instead of breaking the page.

---

### Task 4 (Medium): Pluggable Savings Engine
**File:** `pantry_pilot/offers.py`

Create a savings system that can grow without rewriting the engine.

1. Define an abstract base class `Offer` with methods such as `is_applicable(item: PantryItem)` and `build_offer(item: PantryItem)`.
2. Implement at least three concrete offer types:
   - **Staple sale** — applies when `category` is `Grains` or `Canned Goods`.
     - Estimated savings = `unit_price * 0.10` (rounded to 2 decimals).
   - **Bulk refill** — applies when `quantity` is at least 2 below `minimum_quantity` (e.g., `quantity < max(1, minimum_quantity - 1)`).
     - Estimated savings = `unit_price * 0.15` (rounded to 2 decimals).
   - **Rescue offer** — applies when `days_until_expiry <= 3` and the item should be used before buying more.
     - Estimated savings = the full `unit_price` (rounded to 2 decimals), representing the money saved by using the item before it spoils.
3. Implement an `OfferEngine` that takes any iterable of `Offer` objects and produces a list of offer dictionaries from a list of `PantryItem` objects.
   - The engine must depend on the shared `Offer` interface, not on concrete class names — adding a fourth offer class later must not require editing the engine.
4. Make every returned offer dictionary include: `sku`, a short `title`, a `description`, an `estimated_savings` amount, and a visual `tag` such as `sale`, `bundle`, or `use-first`.

**Expected return shape from `build_offers(...)`:**

```python
[
    {
        "sku": "MILK-2L",
        "title": "Use Whole Milk first",
        "description": "Plan meals around this item before buying more.",
        "estimated_savings": 3.79,
        "tag": "use-first",
    }
]
```

**Verify:** The savings section fills with offer cards, the total estimated savings number appears, and different offer tags are visible in the browser.

---

### Task 5 (Hard): Iterable Shopping Trip Planner
**File:** `pantry_pilot/planner.py`

Turn the restock plan into a structured shopping trip.

1. Create a `ShoppingStep` dataclass to represent a single stop on the trip.
2. Create an abstract `StepOrderer` with an `order(steps)` method.
3. Create a concrete `PriorityStepOrderer` that can be used by default.
4. Implement a `ShoppingTrip` class that stores steps and:
   - Implements `__iter__` so callers can iterate over its `ShoppingStep`s.
   - Exposes a `total_estimated_cost` property.
   - Provides a `summary()` method.
5. Implement `ShoppingPlanner` with a public method `build_trip(items, restock_plan, offers, aisle_map)`.
   - Match each restock suggestion to its aisle / store-section using `aisle_map` (check `sku_sections` first, then fall back to `category_sections`).
   - Attach helpful notes from any matching offers.
   - Calculate a per-step `estimated_cost`.
   - Produce the final ordered trip by delegating to the injected `StepOrderer` — do not hard-code one large sort inside the planner.
   - **Important:** `build_trip` must return a `ShoppingTrip` instance (not a plain dict), so the Flask app can iterate over it naturally.
   - A generator method such as `yield_priority_items()` or `yield_store_sections()` is a good fit here if it improves the design.

**Expected shapes:**

Each `ShoppingStep` should expose these fields (as a dataclass or plain object):

```python
{
    "section": "Dairy Aisle",
    "sku": "MILK-2L",
    "name": "Whole Milk",
    "recommended_quantity": 2,
    "priority": 3,
    "estimated_cost": 7.58,
    "notes": ["Low stock: only 1 left (minimum 2)", "Use Whole Milk first"],
}
```

The `ShoppingTrip` object must:
1. Be iterable (implement `__iter__` yielding `ShoppingStep`s).
2. Provide a `total_estimated_cost` property (float, sum of all step costs).
3. Provide a `summary()` method returning:
   ```python
   {"step_count": 6, "section_count": 4, "highest_priority": 3}
   ```

**Verify:** The trip panel shows store sections in order, each step includes useful notes, and the running total updates with realistic values.

---

### Task 6 (Hard): Insight Report Composer
**File:** `pantry_pilot/reports.py`

Finish the application with a modular report builder rather than one giant function. Use the outputs from your earlier tasks as report context so this final feature feels like the top layer of the whole system.

1. Create an abstract `ReportSection` with a method like `build(context)` that returns one section of the final report.
2. Implement at least three concrete sections: `WasteRiskSection`, `SavingsSection`, and `RestockCoverageSection`.
3. Implement `PantryReportBuilder` that receives section objects and composes the final report dictionary with `headline_metrics`, `sections`, and `generated_at`.
   - The builder must depend on the `ReportSection` abstraction so new sections can be added later without changing the builder.
4. Add a context manager named `ReportArchive` that writes a human-readable text snapshot of the newest report to `data/generated/latest_report.txt`.
   - If the target folder does not exist, create it safely.
5. Use your `ReportArchive` context manager inside `PantryReportBuilder.build()` (or a dedicated helper method) so the snapshot is written every time a report is generated.

#### Expected Interfaces

Your code will be discovered and wired together automatically, so it must match the following contracts exactly.

**`ReportSection.build(context)`** returns a dictionary with these keys:
```python
{"title": str, "body": str}
```

**`PantryReportBuilder`** constructor must accept a list of section instances (positional or keyword `sections`). Its `build(context)` method must return a dictionary with this shape:
```python
{
    "headline_metrics": {
        "health_score": int,
        "restock_items": int,
        "estimated_savings": float,
        "trip_cost": float,
    },
    "sections": [section_dict, ...],  # one dict per section, in order
    "generated_at": str,  # ISO timestamp (e.g., "2026-05-03T10:46:15")
}
```

**Context dictionary** passed to `build(context)` contains:
- `inventory`: `{"health_score": int, "expiring_soon": [{"name": str}, ...]}`
- `restock_plan`: list of items to restock
- `offers`: `{"total_estimated_savings": float}`
- `trip`: `{"total_estimated_cost": float, "summary": {"section_count": int}}`

**`ReportArchive`** must be a context manager that writes a plain-text snapshot to `data/generated/latest_report.txt`. The snapshot should be human-readable and look like this:

```
PantryPilot Latest Report

Health score: 0
Restock items: 6
Estimated savings: $8.86
Trip cost: $35.00

Restock Coverage
The current plan covers 6 items across 4 store sections.

Savings Opportunities
Current offers could save about $8.86 on the next trip.

Waste Risk
2 pantry items need attention in the next few days. Watch out for: Whole Milk, Baby Spinach.
```

**Verify:** The insights page becomes populated, headline metrics appear at the top, and the latest report preview shows meaningful text generated from your Python code.


