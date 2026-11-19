"""
Agent 3 — Parts Prediction Agent

Uses Google Gemini to predict the top 3-5 replacement parts needed for a
repair, along with confidence scores and reasoning.  The prediction is
grounded in:
- The parsed complaint summary (from Agent 1)
- Similar historical cases (from Agent 2)
- Asset BOM and known failure patterns (from Agent 2)
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import GEMINI_API_KEY, LLM_MODEL, TEMPERATURE
from utils.helpers import parse_llm_json, retry_llm_call

from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are a senior parts-forecasting AI for field-service operations.
Given the complaint summary, similar past repair cases, and the asset's bill
of materials, predict the top 1-3 parts most likely needed for this repair.

Return ONLY valid JSON — an array of objects with these keys:
[
  {{
    "part_name": "<exact part name>",
    "confidence_percent": <integer 0-100, do not include % symbol>,
    "reasoning": "<one-sentence justification>"
  }},
  ...
]

Rules:
- Strictly limit to a maximum of 3 parts.
- Order by confidence descending.
- Base confidence on how often the part appeared in similar cases and how
  well the symptoms match known failure modes.
- If the BOM lists a part that matches a known issue, boost its confidence.
- Do NOT invent part names that don't exist in the BOM or past cases unless
  the symptoms strongly suggest a novel failure.
"""


def _build_user_prompt(state: dict) -> str:
    """Assemble the user prompt from state data."""
    sections = []

    # Complaint summary
    summary = state.get("issue_summary", "No summary available.")
    symptoms = state.get("symptoms", [])
    sections.append(f"## Complaint Summary\n{summary}")
    if symptoms:
        sections.append(f"Symptoms: {', '.join(symptoms)}")

    # Similar historical cases
    similar = state.get("similar_cases", [])
    if similar:
        lines = ["## Similar Past Cases"]
        for i, case in enumerate(similar, 1):
            meta = case.get("metadata", {})
            lines.append(
                f"{i}. Parts used: {meta.get('parts_used', 'N/A')} | "
                f"Resolution: {meta.get('resolution', 'N/A')} | "
                f"Score: {case.get('score', 'N/A')}"
            )
        sections.append("\n".join(lines))
    else:
        sections.append("## Similar Past Cases\nNone found.")

    # Asset info
    asset = state.get("asset_info", {})
    if asset:
        bom = asset.get("bom", asset.get("bill_of_materials", []))
        known = asset.get("known_issues", [])
        sections.append(f"## Asset BOM\n{json.dumps(bom, indent=2)}")
        if known:
            sections.append(f"## Known Issues\n{json.dumps(known, indent=2)}")
    else:
        sections.append("## Asset Info\nNo asset catalog data available.")

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def run_parts_prediction(state: dict) -> dict:
    """Predict replacement parts using Gemini, grounded in case context.

    **Expected state keys (input):**
    - ``issue_summary`` (str)
    - ``symptoms`` (list[str])
    - ``similar_cases`` (list[dict])
    - ``asset_info`` (dict)

    **Added state keys (output):**
    - ``predicted_parts`` (list[dict]): Each dict has ``part_name``,
      ``confidence_percent``, and ``reasoning``.

    Returns:
        Updated state dict.
    """
    print("\n🔧 Agent 3: Parts Prediction running …")

    try:
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )

        user_prompt = _build_user_prompt(state)

        response = retry_llm_call(llm, [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ], agent_name="parts_prediction")

        predicted_parts = parse_llm_json(response.content)

        # Normalise — ensure it's always a list of dicts
        if isinstance(predicted_parts, dict):
            # Some models wrap in {"parts": [...]}
            predicted_parts = predicted_parts.get("parts", [predicted_parts])

        # Enforce max 3 parts and ensure confidence is an integer
        predicted_parts = predicted_parts[:3]
        for p in predicted_parts:
            try:
                p["confidence_percent"] = int(str(p.get("confidence_percent", 0)).replace("%", "").strip())
            except:
                p["confidence_percent"] = 50

        # Sort by confidence descending
        predicted_parts.sort(
            key=lambda p: p.get("confidence_percent", 0), reverse=True
        )

        state["predicted_parts"] = predicted_parts

        print(f"  ✅ Predicted {len(predicted_parts)} parts:")
        for p in predicted_parts:
            print(f"     • {p.get('part_name', '?')} — {p.get('confidence_percent', '?')}% "
                  f"({p.get('reasoning', '')[:60]})")

    except json.JSONDecodeError as e:
        print(f"  [parts_prediction] ERROR parsing LLM JSON: {e}")
        state["predicted_parts"] = []

    except Exception as e:
        print(f"  [parts_prediction] ERROR: {e}")
        state["predicted_parts"] = []

    return state
