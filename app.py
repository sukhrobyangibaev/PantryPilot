from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, jsonify, render_template

from pantry_pilot.bootstrap import PantryPilotBootstrap


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    app = Flask(__name__)
    bootstrap = PantryPilotBootstrap(logging.getLogger("pantry_pilot"))

    @app.route("/")
    def dashboard():
        context = bootstrap.build_dashboard_context()
        return _render_or_json(app, "dashboard.html", context)

    @app.route("/insights")
    def insights():
        context = bootstrap.build_insights_context()
        return _render_or_json(app, "insights.html", context)

    return app


def _render_or_json(app: Flask, template_name: str, context: dict[str, object]):
    template_path = Path(app.root_path) / "templates" / template_name
    if template_path.exists():
        return render_template(template_name, **context)
    return jsonify(context)


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
