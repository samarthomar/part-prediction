"""
Agent 2 — Context Enrichment Agent

Enriches the parsed case data by:
1. Searching the FAISS vector store for similar historical repair cases.
2. Looking up the asset catalog for BOM, known issues, and warranty info.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import TOP_K_SIMILAR_CASES
from utils.embeddings import search_similar_cases
from utils.helpers import load_json

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_ASSET_CATALOG_PATH = os.path.join(_PROJECT_ROOT, "data", "asset_catalog.json")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_search_query(state: dict) -> str:
    """Combine symptoms, product type, and model into a single search query."""
    parts = []
    symptoms = state.get("symptoms", [])
    if symptoms:
        parts.append("Symptoms: " + ", ".join(symptoms))
    if state.get("product_type"):
        parts.append(f"Product: {state['product_type']}")
    if state.get("model"):
        parts.append(f"Model: {state['model']}")
    if state.get("error_codes"):
        parts.append("Errors: " + ", ".join(state["error_codes"]))
    return " | ".join(parts) if parts else "general repair query"


def _lookup_asset(product_type: str, model: str) -> dict:
    """Look up asset catalog for BOM, known issues, and warranty info.

    Returns an empty dict if the catalog file is missing or the model is not
    found.
    """
    try:
        catalog = load_json(_ASSET_CATALOG_PATH)
    except FileNotFoundError:
        print("  [context_enrichment] WARNING: asset_catalog.json not found.")
        return {}

    # Support both list-of-dicts and dict-keyed-by-model formats
    if isinstance(catalog, list):
        for entry in catalog:
            entry_model = entry.get("model", "").lower()
            entry_product = entry.get("product_type", "").lower()
            if entry_model == model.lower() or entry_product == product_type.lower():
                return entry
        # Partial match fallback
        for entry in catalog:
            if product_type.lower() in entry.get("product_type", "").lower():
                return entry
    elif isinstance(catalog, dict):
        # Keyed by model name
        if model in catalog:
            return catalog[model]
        # Case-insensitive fallback
        for key, value in catalog.items():
            if key.lower() == model.lower():
                return value

    print(f"  [context_enrichment] No catalog entry for {product_type}/{model}.")
    return {}


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def run_context_enrichment(state: dict) -> dict:
    """Enrich case state with similar historical cases and asset information.

    **Expected state keys (input):**
    - ``symptoms`` (list[str])
    - ``product_type`` (str)
    - ``model`` (str)

    **Added state keys (output):**
    - ``similar_cases`` (list[dict]): Top-k similar historical fix records.
    - ``asset_info`` (dict): BOM, known issues, warranty for the model.
    - ``enriched_context`` (str): Human-readable summary of enrichment data.

    Returns:
        Updated state dict.
    """
    print("\n📚 Agent 2: Context Enrichment running …")

    try:
        # --- 1. Similarity search ----------------------------------------
        query = _build_search_query(state)
        print(f"  Search query: {query[:100]}{'…' if len(query) > 100 else ''}")
        similar_cases = search_similar_cases(query, k=TOP_K_SIMILAR_CASES)
        state["similar_cases"] = similar_cases
        print(f"  ✅ Retrieved {len(similar_cases)} similar historical cases.")

        # --- 2. Asset catalog lookup -------------------------------------
        product_type = state.get("product_type", "Unknown")
        model = state.get("model", "Unknown")
        asset_info = _lookup_asset(product_type, model)
        state["asset_info"] = asset_info

        if asset_info:
            print(f"  ✅ Asset info found for {model}.")
        else:
            print(f"  ⚠️  No asset info for {product_type} / {model}.")

        # --- 3. Build enriched context summary ---------------------------
        context_parts = []
        if similar_cases:
            context_parts.append(
                f"Found {len(similar_cases)} similar past cases. "
                f"Top match score: {similar_cases[0]['score']}"
            )
            for i, case in enumerate(similar_cases[:3], 1):
                parts_used = case["metadata"].get("parts_used", "N/A")
                context_parts.append(f"  Case {i}: Parts → {parts_used}")

        if asset_info:
            bom = asset_info.get("bom", asset_info.get("bill_of_materials", []))
            known = asset_info.get("known_issues", [])
            warranty = asset_info.get("warranty_status", asset_info.get("warranty", "N/A"))
            context_parts.append(f"Asset BOM items: {len(bom) if isinstance(bom, list) else 'N/A'}")
            context_parts.append(f"Known issues: {len(known) if isinstance(known, list) else 'N/A'}")
            context_parts.append(f"Warranty: {warranty}")

        state["enriched_context"] = "\n".join(context_parts) if context_parts else "No enrichment data available."

    except Exception as e:
        print(f"  [context_enrichment] ERROR: {e}")
        state.setdefault("similar_cases", [])
        state.setdefault("asset_info", {})
        state.setdefault("enriched_context", f"Enrichment failed: {e}")

    return state
