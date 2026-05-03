from __future__ import annotations

from datetime import datetime
import importlib
import inspect
import logging
from typing import Any, Callable, Iterable

from pantry_pilot import data_access, fallbacks, serializers


class PantryPilotBootstrap:
    FEATURE_STATUS_META = {
        "models": {
            "label": "Pantry item model",
            "title": "Pantry item model not implemented",
            "message": "Add `PantryItem.from_dict` in `pantry_pilot/models.py` to replace raw pantry dictionaries.",
            "error_message": "Your `PantryItem` implementation raised an error. Check the Flask console and fix it before the app can trust live model data.",
        },
        "inventory": {
            "label": "Inventory overview",
            "title": "Inventory snapshot not implemented",
            "message": "Add `InventorySnapshotBuilder.build` in `pantry_pilot/inventory.py` to replace scaffold inventory metrics.",
            "error_message": "Your inventory snapshot code raised an error. Check the Flask console and fix it before this panel can show live results.",
        },
        "restock": {
            "label": "Restock advisor",
            "title": "Restock advisor not implemented",
            "message": "Implement `RestockAdvisor` plus concrete `RestockRule` classes in `pantry_pilot/restock.py` to unlock this panel.",
            "error_message": "Your restock advisor raised an error. Check the Flask console and fix it before this panel can show live suggestions.",
        },
        "offers": {
            "label": "Savings opportunities",
            "title": "Savings engine not implemented",
            "message": "Implement `OfferEngine` plus concrete `Offer` classes in `pantry_pilot/offers.py` to replace scaffold savings cards.",
            "error_message": "Your savings engine raised an error. Check the Flask console and fix it before this panel can show live offers.",
        },
        "trip": {
            "label": "Shopping trip",
            "title": "Shopping planner not implemented",
            "message": "Add `ShoppingPlanner.build_trip` in `pantry_pilot/planner.py` to replace the scaffold trip plan.",
            "error_message": "Your shopping planner raised an error. Check the Flask console and fix it before this panel can show a live trip.",
        },
        "report": {
            "label": "Insights report",
            "title": "Insights report not implemented",
            "message": "Implement `PantryReportBuilder` plus concrete `ReportSection` classes in `pantry_pilot/reports.py` to unlock the insights page.",
            "error_message": "Your report builder raised an error. Check the Flask console and fix it before the insights page can show live results.",
        },
    }

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("pantry_pilot")
        self._reported_messages: set[str] = set()

    def build_dashboard_context(self) -> dict[str, Any]:
        state = self.build_state()
        return {
            "page_title": "PantryPilot Dashboard",
            "inventory": state["inventory"],
            "restock_plan": state["restock_plan"],
            "offers": state["offers"],
            "trip": state["trip"],
            "feature_statuses": state["feature_statuses"],
        }

    def build_insights_context(self) -> dict[str, Any]:
        state = self.build_state()
        return {
            "page_title": "PantryPilot Insights",
            "report": state["report"],
            "latest_report_preview": state["latest_report_preview"],
            "feature_statuses": state["feature_statuses"],
        }

    def build_state(self) -> dict[str, Any]:
        raw_items = data_access.load_pantry_items(self.logger)
        catalog = data_access.load_catalog(self.logger)
        preferences = data_access.load_preferences(self.logger)
        aisle_map = data_access.load_aisle_map(self.logger)

        pantry_items, models_status = self._build_pantry_items(raw_items)
        inventory, inventory_status = self._build_inventory_snapshot(raw_items)
        inventory.setdefault("generated_at", datetime.now().isoformat(timespec="seconds"))
        restock_plan, restock_status = self._build_restock_plan(raw_items, catalog, preferences)
        offer_items, offers_status = self._build_offers(pantry_items)
        offers = {
            "items": offer_items,
            "total_estimated_savings": round(
                sum(float(offer.get("estimated_savings", 0)) for offer in offer_items),
                2,
            ),
        }
        trip, trip_status = self._build_trip(pantry_items, restock_plan, offer_items, aisle_map)

        report_context = {
            "inventory": inventory,
            "restock_plan": restock_plan,
            "offers": offers,
            "trip": trip,
        }
        report, report_status = self._build_report(report_context)

        latest_report_preview = ""
        if report_status["implemented"]:
            latest_report_preview = data_access.read_latest_report_preview(self.logger) or fallbacks.build_report_preview(report)

        return {
            "inventory": inventory,
            "restock_plan": restock_plan,
            "offers": offers,
            "trip": trip,
            "report": report,
            "latest_report_preview": latest_report_preview,
            "feature_statuses": {
                "models": models_status,
                "inventory": inventory_status,
                "restock": restock_status,
                "offers": offers_status,
                "trip": trip_status,
                "report": report_status,
            },
        }

    def _build_inventory_snapshot(self, raw_items: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        fallback_value = fallbacks.build_inventory_snapshot(raw_items)
        module = self._import_student_module("pantry_pilot.inventory")
        if module is None:
            return fallback_value, self._not_implemented_status("inventory")

        builder_class = self._get_attribute(module, "InventorySnapshotBuilder", "pantry_pilot.inventory")
        if builder_class is None:
            return fallback_value, self._not_implemented_status("inventory")

        builder = self._instantiate(builder_class, "pantry_pilot.inventory.InventorySnapshotBuilder")
        if builder is None:
            return fallback_value, self._not_implemented_status("inventory")

        build_method = getattr(builder, "build", None)
        if not callable(build_method):
            self._warn_once(
                "inventory-build-missing",
                "InventorySnapshotBuilder.build is missing; using fallback inventory snapshot.",
            )
            return fallback_value, self._not_implemented_status("inventory")

        try:
            return (
                serializers.normalize_inventory_snapshot(build_method(raw_items), raw_items),
                self._implemented_status("inventory"),
            )
        except Exception:
            self.logger.exception("InventorySnapshotBuilder.build failed. Using fallback inventory snapshot.")
            return fallback_value, self._error_status("inventory")

    def _build_restock_plan(
        self,
        raw_items: list[dict[str, Any]],
        catalog: list[dict[str, Any]],
        preferences: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        fallback_value = fallbacks.build_restock_plan(raw_items, catalog, preferences)
        module = self._import_student_module("pantry_pilot.restock")
        if module is None:
            return fallback_value, self._not_implemented_status("restock")

        advisor_class = self._get_attribute(module, "RestockAdvisor", "pantry_pilot.restock")
        rule_base = self._get_attribute(module, "RestockRule", "pantry_pilot.restock")
        if advisor_class is None or rule_base is None:
            return fallback_value, self._not_implemented_status("restock")

        rules = self._instantiate_concrete_subclasses(module, rule_base)
        if not rules:
            self._warn_once(
                "restock-rules-missing",
                "No concrete RestockRule classes are ready yet. Using fallback restock suggestions.",
            )
            return fallback_value, self._not_implemented_status("restock")
        advisor = self._instantiate_with_dependency(advisor_class, rules, "rules", "pantry_pilot.restock.RestockAdvisor")
        if advisor is None:
            return fallback_value, self._not_implemented_status("restock")

        build_method = getattr(advisor, "build_plan", None)
        if not callable(build_method):
            self._warn_once(
                "restock-build-missing",
                "RestockAdvisor.build_plan is missing; using fallback restock suggestions.",
            )
            return fallback_value, self._not_implemented_status("restock")

        try:
            return (
                serializers.normalize_restock_plan(build_method(raw_items, catalog, preferences)),
                self._implemented_status("restock"),
            )
        except Exception:
            self.logger.exception("RestockAdvisor.build_plan failed. Using fallback restock suggestions.")
            return fallback_value, self._error_status("restock")

    def _build_pantry_items(self, raw_items: list[dict[str, Any]]) -> tuple[list[Any], dict[str, Any]]:
        fallback_items = serializers.normalize_items(raw_items)
        module = self._import_student_module("pantry_pilot.models")
        if module is None:
            return fallback_items, self._not_implemented_status("models")

        model_class = self._get_attribute(module, "PantryItem", "pantry_pilot.models")
        if model_class is None:
            return fallback_items, self._not_implemented_status("models")

        from_dict = getattr(model_class, "from_dict", None)
        if not callable(from_dict):
            self._warn_once(
                "pantry-item-from-dict-missing",
                "PantryItem.from_dict is missing; using raw pantry data.",
            )
            return fallback_items, self._not_implemented_status("models")

        converted_items: list[Any] = []
        for item in raw_items:
            try:
                converted_items.append(from_dict(item))
            except Exception:
                self.logger.exception(
                    "PantryItem.from_dict failed for %s. Skipping that item and continuing.",
                    item.get("name", "unknown item"),
                )

        if converted_items:
            return converted_items, self._implemented_status("models")

        return fallback_items, self._error_status("models")

    def _build_offers(self, pantry_items: list[Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        fallback_value = fallbacks.build_offers(pantry_items)
        module = self._import_student_module("pantry_pilot.offers")
        if module is None:
            return fallback_value, self._not_implemented_status("offers")

        engine_class = self._get_attribute(module, "OfferEngine", "pantry_pilot.offers")
        offer_base = self._get_attribute(module, "Offer", "pantry_pilot.offers")
        if engine_class is None or offer_base is None:
            return fallback_value, self._not_implemented_status("offers")

        offers = self._instantiate_concrete_subclasses(module, offer_base)
        if not offers:
            self._warn_once(
                "offer-classes-missing",
                "No concrete Offer classes are ready yet. Using fallback savings offers.",
            )
            return fallback_value, self._not_implemented_status("offers")
        engine = self._instantiate_with_dependency(engine_class, offers, "offers", "pantry_pilot.offers.OfferEngine")
        if engine is None:
            return fallback_value, self._not_implemented_status("offers")

        build_method = self._pick_callable(engine, ["build_offers", "build", "generate", "create_offers"])
        if build_method is None:
            self._warn_once(
                "offer-engine-method-missing",
                "OfferEngine has no supported public method for building offers; using fallback savings offers.",
            )
            return fallback_value, self._not_implemented_status("offers")

        try:
            return serializers.normalize_offers(build_method(pantry_items)), self._implemented_status("offers")
        except Exception:
            self.logger.exception("OfferEngine failed. Using fallback savings offers.")
            return fallback_value, self._error_status("offers")

    def _build_trip(
        self,
        pantry_items: list[Any],
        restock_plan: list[dict[str, Any]],
        offers: list[dict[str, Any]],
        aisle_map: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        fallback_value = fallbacks.build_trip(pantry_items, restock_plan, offers, aisle_map)
        module = self._import_student_module("pantry_pilot.planner")
        if module is None:
            return fallback_value, self._not_implemented_status("trip")

        planner_class = self._get_attribute(module, "ShoppingPlanner", "pantry_pilot.planner")
        if planner_class is None:
            return fallback_value, self._not_implemented_status("trip")

        orderer = None
        orderer_base = getattr(module, "StepOrderer", None)
        if inspect.isclass(orderer_base):
            orderers = self._instantiate_concrete_subclasses(module, orderer_base)
            if orderers:
                orderer = orderers[0]

        planner = self._instantiate_with_dependency(planner_class, orderer, "orderer", "pantry_pilot.planner.ShoppingPlanner")
        if planner is None:
            return fallback_value, self._not_implemented_status("trip")

        build_method = getattr(planner, "build_trip", None)
        if not callable(build_method):
            self._warn_once(
                "shopping-planner-method-missing",
                "ShoppingPlanner.build_trip is missing; using fallback shopping trip.",
            )
            return fallback_value, self._not_implemented_status("trip")

        try:
            return (
                serializers.normalize_trip(build_method(pantry_items, restock_plan, offers, aisle_map)),
                self._implemented_status("trip"),
            )
        except Exception:
            self.logger.exception("ShoppingPlanner.build_trip failed. Using fallback shopping trip.")
            return fallback_value, self._error_status("trip")

    def _build_report(self, context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        fallback_value = fallbacks.build_report(context)
        module = self._import_student_module("pantry_pilot.reports")
        if module is None:
            return fallback_value, self._not_implemented_status("report")

        builder_class = self._get_attribute(module, "PantryReportBuilder", "pantry_pilot.reports")
        section_base = self._get_attribute(module, "ReportSection", "pantry_pilot.reports")
        if builder_class is None or section_base is None:
            return fallback_value, self._not_implemented_status("report")

        sections = self._instantiate_concrete_subclasses(module, section_base)
        if not sections:
            self._warn_once(
                "report-sections-missing",
                "No concrete ReportSection classes are ready yet. Using fallback insights report.",
            )
            return fallback_value, self._not_implemented_status("report")
        builder = self._instantiate_with_dependency(
            builder_class,
            sections,
            "sections",
            "pantry_pilot.reports.PantryReportBuilder",
        )
        if builder is None:
            return fallback_value, self._not_implemented_status("report")

        build_method = self._pick_callable(builder, ["build", "build_report", "compose", "create"])
        if build_method is None:
            self._warn_once(
                "report-builder-method-missing",
                "PantryReportBuilder has no supported public method for composing reports; using fallback insights report.",
            )
            return fallback_value, self._not_implemented_status("report")

        try:
            return serializers.normalize_report(build_method(context)), self._implemented_status("report")
        except Exception:
            self.logger.exception("PantryReportBuilder failed. Using fallback insights report.")
            return fallback_value, self._error_status("report")

    def _import_student_module(self, module_name: str):
        try:
            return importlib.import_module(module_name)
        except ImportError as exc:
            self._warn_once(module_name, f"Could not import {module_name}: {exc}. Using scaffold fallback data.")
            return None
        except Exception:
            self.logger.exception("Could not load %s. Using scaffold fallback data.", module_name)
            return None

    def _get_attribute(self, module: Any, attribute: str, module_name: str):
        try:
            return getattr(module, attribute)
        except AttributeError:
            self._warn_once(
                f"{module_name}.{attribute}",
                f"{module_name} does not define {attribute} yet. Using scaffold fallback data.",
            )
            return None

    def _instantiate(self, class_object: type[Any], label: str):
        try:
            return class_object()
        except TypeError as exc:
            self._warn_once(f"{label}-init", f"Could not instantiate {label}: {exc}. Using scaffold fallback data.")
            return None

    def _instantiate_with_dependency(
        self,
        class_object: type[Any],
        dependency: Any,
        dependency_name: str,
        label: str,
    ):
        if dependency is None:
            return self._instantiate(class_object, label)

        try:
            return class_object(dependency)
        except TypeError:
            pass

        try:
            return class_object(**{dependency_name: dependency})
        except TypeError:
            pass

        return self._instantiate(class_object, label)

    def _instantiate_concrete_subclasses(self, module: Any, base_class: type[Any]) -> list[Any]:
        instances: list[Any] = []
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate is base_class or candidate.__module__ != module.__name__:
                continue
            if not issubclass(candidate, base_class) or inspect.isabstract(candidate):
                continue
            instance = self._instantiate(candidate, f"{module.__name__}.{candidate.__name__}")
            if instance is not None:
                instances.append(instance)
        return instances

    def _pick_callable(self, target: Any, method_names: Iterable[str]) -> Callable[..., Any] | None:
        for name in method_names:
            candidate = getattr(target, name, None)
            if callable(candidate):
                return candidate
        return None

    def _warn_once(self, key: str, message: str) -> None:
        if key in self._reported_messages:
            return
        self._reported_messages.add(key)
        self.logger.warning(message)

    def _implemented_status(self, feature: str) -> dict[str, Any]:
        meta = self.FEATURE_STATUS_META[feature]
        return {
            "implemented": True,
            "state": "implemented",
            "badge": "Implemented",
            "label": meta["label"],
            "title": f"{meta['label']} ready",
            "message": "Using your implementation.",
        }

    def _not_implemented_status(self, feature: str) -> dict[str, Any]:
        meta = self.FEATURE_STATUS_META[feature]
        return {
            "implemented": False,
            "state": "not-implemented",
            "badge": "Not implemented",
            "label": meta["label"],
            "title": meta["title"],
            "message": meta["message"],
        }

    def _error_status(self, feature: str) -> dict[str, Any]:
        meta = self.FEATURE_STATUS_META[feature]
        return {
            "implemented": False,
            "state": "implementation-error",
            "badge": "Implementation error",
            "label": meta["label"],
            "title": meta["title"],
            "message": meta["error_message"],
        }
