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

## How This Works

- You ONLY modify Python files listed in the tasks below.
- Do NOT touch any other files.
- After making changes, restart the app (`Ctrl+C`, then `python app.py` again) and refresh the browser.
- The app is designed to keep running even when later tasks are unfinished, so some panels may stay empty until your code is ready.
- Complete the tasks in order. Later tasks build on the earlier ones.

## Tasks

### Task 1 (Easy): Inventory Health Snapshot
**File:** `pantry_pilot/inventory.py`

Create a class named `InventorySnapshotBuilder` whose job is to analyze the raw pantry data and build a single summary dictionary for the dashboard. This class should have one clear responsibility: inventory analysis. Give it a public method `build(items)` that accepts a list of item dictionaries from the seed data and returns a dictionary with these keys: `total_items`, `category_count`, `health_score`, `low_stock`, `expiring_soon`, and `category_totals`.

Treat an item as low stock when `quantity <= minimum_quantity`. Treat an item as expiring soon when `days_until_expiry <= 3`. `health_score` should be an integer from 0 to 100 that drops as the number of low-stock and expiring items increases. `low_stock` and `expiring_soon` should be lists of dictionaries that include at least the item name, category, current quantity, and minimum quantity. `category_totals` should be sorted from largest category to smallest so the UI can render the busiest sections first. Keep this class focused: no HTML, no printing, no shopping-plan logic.

**Verify:** The overview cards at the top of the dashboard show real counts, the low-stock list fills in, and the category summary is no longer empty.

---

### Task 2 (Easy): Extensible Restock Advisor
**File:** `pantry_pilot/restock.py`

Build a restock system that follows Open/Closed and Dependency Inversion. Create an abstract `RestockRule` type with a method that receives pantry items, the grocery catalog, and household preferences, then returns suggestion dictionaries. Then create at least three concrete rule classes: one for low-stock items, one for items that will expire before the next shopping day, and one that reacts to the `weekend_cooking` preference in the seed data.

Also create a `RestockAdvisor` class that receives rule objects in its constructor and exposes `build_plan(items, catalog, preferences)`. The advisor should work with the shared rule interface rather than checking concrete class names with a long `if` or `elif` chain. Each suggestion should contain `sku`, `name`, `recommended_quantity`, `priority`, and `reasons`. If two rules suggest the same item, merge them into one suggestion, keep the highest priority, and combine the reasons into a list. Sort the final plan by priority descending and then by item name.

**Verify:** The restock panel shows suggested items, each card explains why it was suggested, and higher-priority items appear first.

---

### Task 3 (Medium): Robust Pantry Domain Model
**File:** `pantry_pilot/models.py`

Replace loose dictionaries with a proper domain object. Implement a custom exception named `InvalidPantryItemError` and a `PantryItem` dataclass with type hints for `sku`, `name`, `category`, `unit`, `quantity`, `minimum_quantity`, `days_until_expiry`, and `unit_price`. Validate that numeric values are never negative and that text fields are not blank. Normalize category and unit text so the app does not show inconsistent labels.

Your class must include computed properties named `is_low_stock`, `is_expiring_soon`, `restock_amount`, and `estimated_restock_cost`. Add a `from_dict` classmethod for turning raw JSON data into a `PantryItem`, plus a `to_dict` method for converting the object back into a UI-friendly dictionary. Give the class a readable `__str__` implementation that would make sense in logs or debugging output. This task should make the rest of the app easier to extend, not harder.

**Verify:** Inventory labels become cleaner and more consistent, restock quantities become more accurate, and invalid pantry data is handled gracefully instead of breaking the page.

---

### Task 4 (Medium): Pluggable Savings Engine
**File:** `pantry_pilot/offers.py`

Create a savings system that can grow without rewriting the engine. Define an abstract base class named `Offer` with methods such as `is_applicable(item: PantryItem)` and `build_offer(item: PantryItem)`. Then implement at least three concrete offer types: a category sale for staple items, a bulk refill offer for items far below their minimum level, and a rescue offer for items that expire soon and should be used before buying more.

Implement an `OfferEngine` that receives any iterable of `Offer` objects and produces a list of offer dictionaries for a list of `PantryItem` objects. The engine should depend on the shared offer interface, not on concrete class names. Every returned offer must include the item SKU, a short title, a description, an estimated savings amount, and a visual tag such as `sale`, `bundle`, or `use-first`. Design the code so adding a fourth offer class later would not require editing the engine itself.

**Verify:** The savings section fills with offer cards, the total estimated savings number appears, and different offer tags are visible in the browser.

---

### Task 5 (Hard): Iterable Shopping Trip Planner
**File:** `pantry_pilot/planner.py`

Turn the restock plan into a structured shopping trip. Create a `ShoppingStep` dataclass, an abstract `StepOrderer` with an `order(steps)` method, and a concrete `PriorityStepOrderer` that can be used by default. Then implement a `ShoppingTrip` class that stores steps, implements `__iter__`, exposes a `total_estimated_cost` property, and provides a `summary()` method.

Finally, implement `ShoppingPlanner` with a public method `build_trip(items, restock_plan, offers, aisle_map)`. The planner should match restock suggestions to aisle or store-section data, attach helpful notes from matching offers, calculate per-step estimated costs, and produce an ordered trip using the injected `StepOrderer` dependency instead of hard-coding one large sort directly inside the planner. A generator method such as `yield_priority_items()` or `yield_store_sections()` is a good fit here if it improves the design. The final trip object should be easy for the Flask app to loop over naturally.

**Verify:** The trip panel shows store sections in order, each step includes useful notes, and the running total updates with realistic values.

---

### Task 6 (Hard): Insight Report Composer
**File:** `pantry_pilot/reports.py`

Finish the application with a modular report builder rather than one giant function. Create an abstract `ReportSection` with a method like `build(context)` that returns one section of the final report. Implement at least three concrete sections: `WasteRiskSection`, `SavingsSection`, and `RestockCoverageSection`. Then implement `PantryReportBuilder`, which receives section objects and composes a final report dictionary containing `headline_metrics`, `sections`, and `generated_at`.

Also add a context manager named `ReportArchive` that writes a human-readable text snapshot of the newest report to `data/generated/latest_report.txt` when a report is built. If the target folder does not exist, create it safely. The builder should depend on the `ReportSection` abstraction so new report sections can be added later without changing the builder. Use the outputs from your earlier tasks as report context so this final feature feels like the top layer of the whole system rather than a separate mini-project.

**Verify:** The insights page becomes populated, headline metrics appear at the top, and the latest report preview shows meaningful text generated from your Python code.
