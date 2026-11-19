"""
Agent 4 — Supply Decision Agent

For each predicted part, this agent:
1. Checks stock availability, warehouse location, and unit cost from
   parts_inventory.json.
2. Identifies substitute parts when the primary part is out of stock.
3. Estimates delivery time.
4. Makes an ordering decision based on confidence thresholds:
   - ≥ HIGH_CONFIDENCE_THRESHOLD  → AUTO_ORDER
   - ≥ MEDIUM_CONFIDENCE_THRESHOLD → RESERVE
   - Below                         → ESCALATE_TO_HUMAN
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD
from utils.helpers import load_json, format_confidence, format_decision

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_INVENTORY_PATH = os.path.join(_PROJECT_ROOT, "data", "parts_inventory.json")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_part_in_inventory(part_name: str, inventory: list[dict]) -> dict | None:
    """Case-insensitive lookup of a part in the inventory list."""
    name_lower = part_name.lower()
    for item in inventory:
        if item.get("part_name", "").lower() == name_lower:
            return item
    # Fuzzy fallback — substring match
    for item in inventory:
        if name_lower in item.get("part_name", "").lower() or \
           item.get("part_name", "").lower() in name_lower:
            return item
    return None


def _find_substitute(part_name: str, inventory: list[dict]) -> dict | None:
    """Attempt to find a substitute part that is in stock.

    Looks for inventory items tagged with a 'substitute_for' field, or items
    in the same category with stock > 0.
    """
    name_lower = part_name.lower()
    # Explicit substitute_for field
    for item in inventory:
        subs = item.get("substitute_for", [])
        if isinstance(subs, str):
            subs = [subs]
        for s in subs:
            if s.lower() == name_lower and item.get("stock_quantity", item.get("quantity", 0)) > 0:
                return item

    # Same category fallback
    original = _find_part_in_inventory(part_name, inventory)
    if original:
        category = original.get("category", "")
        if category:
            for item in inventory:
                if (item.get("category", "").lower() == category.lower()
                        and item.get("stock_quantity", item.get("quantity", 0)) > 0
                        and item.get("part_name", "").lower() != name_lower):
                    return item
    return None


def _estimate_delivery(in_stock: bool, warehouse: str) -> str:
    """Return a rough delivery estimate based on stock and location."""
    if in_stock:
        return "1-2 business days (in-stock)"
    return "5-7 business days (backordered / substitute sourcing)"


def _make_decision(confidence: float) -> str:
    """Map a confidence score to an ordering decision."""
    if confidence >= HIGH_CONFIDENCE_THRESHOLD:
        return "AUTO_ORDER"
    elif confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "RESERVE"
    else:
        return "ESCALATE_TO_HUMAN"


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def run_supply_decision(state: dict) -> dict:
    """Evaluate supply availability and make ordering decisions.

    **Expected state keys (input):**
    - ``predicted_parts`` (list[dict]): Each dict must have ``part_name``
      and ``confidence_percent``.

    **Added state keys (output):**
    - ``supply_decisions`` (list[dict]): One entry per predicted part with
      keys: ``part_name``, ``confidence``, ``in_stock``, ``quantity``,
      ``warehouse``, ``unit_cost``, ``substitute``, ``decision``,
      ``decision_label``, ``delivery_estimate``.

    Returns:
        Updated state dict.
    """
    print("\n📦 Agent 4: Supply Decision running …")

    predicted_parts = state.get("predicted_parts", [])
    if not predicted_parts:
        print("  [supply_decision] WARNING: No predicted parts to evaluate.")
        state["supply_decisions"] = []
        return state

    try:
        inventory = load_json(_INVENTORY_PATH)
    except FileNotFoundError:
        print("  [supply_decision] ERROR: parts_inventory.json not found.")
        state["supply_decisions"] = []
        return state

    decisions: list[dict] = []

    for part in predicted_parts:
        part_name = part.get("part_name", "Unknown")
        confidence = part.get("confidence_percent", 0)

        inv_entry = _find_part_in_inventory(part_name, inventory)

        in_stock = False
        quantity = 0
        warehouse = "N/A"
        unit_cost = 0.0
        substitute_info = None

        if inv_entry:
            quantity = inv_entry.get("stock_quantity", inv_entry.get("quantity", 0))
            in_stock = quantity > 0
            warehouse = inv_entry.get("warehouse_location", inv_entry.get("warehouse", inv_entry.get("location", "N/A")))
            unit_cost = inv_entry.get("unit_cost_inr", inv_entry.get("unit_cost", inv_entry.get("price", 0.0)))

        part_id = inv_entry.get("part_id", "N/A") if inv_entry else "N/A"
        part_description = inv_entry.get("part_description", "") if inv_entry else ""

        # If out of stock, look for a substitute
        if not in_stock:
            sub = _find_substitute(part_name, inventory)
            if sub:
                substitute_info = {
                    "part_name": sub.get("part_name", sub.get("substitute_part_name")),
                    "quantity": sub.get("stock_quantity", sub.get("quantity", 0)),
                    "warehouse": sub.get("warehouse_location", sub.get("warehouse", sub.get("location", "N/A"))),
                    "unit_cost": sub.get("unit_cost_inr", sub.get("unit_cost", sub.get("price", 0.0))),
                }

        decision = _make_decision(confidence)
        delivery = _estimate_delivery(in_stock or (substitute_info is not None), warehouse)

        entry = {
            "part_name": part_name,
            "part_id": part_id,
            "part_description": part_description,
            "confidence": confidence,
            "confidence_label": format_confidence(confidence),
            "in_stock": in_stock,
            "quantity": quantity,
            "warehouse": warehouse,
            "unit_cost": unit_cost,
            "substitute": substitute_info,
            "decision": decision,
            "decision_label": format_decision(decision),
            "delivery_estimate": delivery,
        }
        decisions.append(entry)

        stock_tag = f"✅ {quantity} in stock" if in_stock else "❌ Out of stock"
        sub_tag = f" → Sub: {substitute_info['part_name']}" if substitute_info else ""
        print(f"  • {part_name}: {stock_tag}{sub_tag} | {decision}")

    state["supply_decisions"] = decisions
    print(f"  ✅ Supply decisions made for {len(decisions)} parts.")
    return state
