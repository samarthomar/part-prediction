"""
Agent 1 — Case Intelligence Agent

Parses a free-text complaint using Google Gemini to extract structured fields:
symptoms, product type, model, urgency, error codes, and an issue summary.
This is the entry point of the LangGraph pipeline.
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
You are an expert field-service engineer AI. Analyse the customer complaint
below and extract structured information.

Return ONLY valid JSON with these keys (no extra text):
{{
  "symptoms": ["<symptom1>", "<symptom2>", ...],
  "product_type": "<product category, e.g. HVAC, Refrigerator, Washing Machine>",
  "model": "<model identifier if mentioned, else 'Unknown'>",
  "urgency": "<critical | high | medium | low>",
  "error_codes": ["<code1>", ...],
  "issue_summary": "<one-sentence summary of the problem>"
}}

Guidelines:
- Infer urgency from language cues (safety risk → critical, business impact → high, etc.)
- If the complaint mentions specific error codes or blink patterns, capture them.
- If product_type or model are supplied separately, prefer those over inferred values.
"""


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def run_case_intelligence(state: dict) -> dict:
    """Parse a raw complaint into structured case data.

    **Expected state keys (input):**
    - ``complaint_text`` (str): Raw customer complaint.
    - ``product_type`` (str, optional): Pre-supplied product type override.
    - ``model`` (str, optional): Pre-supplied model override.
    - ``error_codes`` (list[str], optional): Pre-supplied error codes.

    **Added state keys (output):**
    - ``symptoms``, ``product_type``, ``model``, ``urgency``,
      ``error_codes``, ``issue_summary``

    Returns:
        Updated state dict.
    """
    print("\n🔍 Agent 1: Case Intelligence running …")
    complaint = state.get("complaint_text", "")

    if not complaint:
        print("  [case_intelligence] WARNING: No complaint_text in state.")
        state["symptoms"] = []
        state["issue_summary"] = "No complaint provided."
        state["urgency"] = "low"
        return state

    try:
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )

        # Build user message — include overrides if present
        user_parts = [f"Customer Complaint:\n{complaint}"]
        if state.get("product_type"):
            user_parts.append(f"Product type (override): {state['product_type']}")
        if state.get("model"):
            user_parts.append(f"Model (override): {state['model']}")
        if state.get("error_codes"):
            user_parts.append(f"Error codes (override): {', '.join(state['error_codes'])}")

        user_message = "\n\n".join(user_parts)

        response = retry_llm_call(llm, [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ], agent_name="case_intelligence")

        parsed = parse_llm_json(response.content)

        # Merge into state (overrides take priority where already supplied)
        state["symptoms"] = parsed.get("symptoms", [])
        state["product_type"] = state.get("product_type") or parsed.get("product_type", "Unknown")
        state["model"] = state.get("model") or parsed.get("model", "Unknown")
        state["urgency"] = parsed.get("urgency", "medium")
        state["error_codes"] = state.get("error_codes") or parsed.get("error_codes", [])
        state["issue_summary"] = parsed.get("issue_summary", "")

        print(f"  ✅ Extracted {len(state['symptoms'])} symptoms | "
              f"Urgency: {state['urgency']} | Product: {state['product_type']}")

    except json.JSONDecodeError as e:
        print(f"  [case_intelligence] ERROR parsing LLM JSON: {e}")
        state.setdefault("symptoms", [])
        state.setdefault("issue_summary", "Failed to parse complaint.")
        state.setdefault("urgency", "medium")

    except Exception as e:
        print(f"  [case_intelligence] ERROR: {e}")
        state.setdefault("symptoms", [])
        state.setdefault("issue_summary", f"Agent error: {e}")
        state.setdefault("urgency", "medium")

    return state
