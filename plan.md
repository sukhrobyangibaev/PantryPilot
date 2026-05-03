# PantryPilot Plan

## App Scenario

PantryPilot is a smart pantry dashboard for busy households who want to waste less food and shop more efficiently. The app starts with a small pantry snapshot, a grocery catalog, and a few household preferences, then turns that data into a living dashboard: low-stock warnings, expiring-item alerts, savings opportunities, and a guided shopping trip. Students never touch the web layer. They only write Python classes and functions, and the browser immediately reflects their work, so every OOP design decision feels tied to a real product instead of an isolated exercise.

## File & Folder Structure

```text
pantry-pilot/
├── app.py
├── README.md
├── plan.md
├── requirements.txt
├── data/
│   ├── aisle_map.json
│   ├── catalog.json
│   ├── pantry.json
│   ├── preferences.json
│   └── generated/
│       └── .gitkeep
├── pantry_pilot/
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── data_access.py
│   ├── fallbacks.py
│   ├── serializers.py
│   ├── inventory.py          # student file, starts blank
│   ├── restock.py            # student file, starts blank
│   ├── models.py             # student file, starts blank
│   ├── offers.py             # student file, starts blank
│   ├── planner.py            # student file, starts blank
│   └── reports.py            # student file, starts blank
├── templates/
│   ├── dashboard.html
│   ├── insights.html
│   └── partials/
│       ├── hero.html
│       ├── inventory_panel.html
│       ├── offers_panel.html
│       ├── report_panel.html
│       ├── restock_panel.html
│       └── trip_panel.html
└── static/
    ├── css/
    │   └── app.css
    └── js/
        └── dashboard.js
```

### Structure Notes

- `app.py` contains the Flask routes and imports student code safely.
- `data/` holds realistic seed data so the UI can render immediately.
- `pantry_pilot/` contains the Python backend. The six blank student files are real application modules, not artificial exercise files.
- `bootstrap.py`, `data_access.py`, `fallbacks.py`, and `serializers.py` are scaffolding files that keep Flask, file loading, safe defaults, and UI formatting out of student code.
- `templates/` and `static/` provide the complete frontend so students never need to edit HTML, CSS, or JavaScript.
- `data/generated/` stores the report snapshot created in the final task.
