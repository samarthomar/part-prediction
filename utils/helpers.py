"""
Utility helper functions for the Parts Recommendation AI system.

Provides common operations used across all agents including JSON file loading,
confidence formatting, decision formatting, timestamp generation, and LLM
response parsing.
"""

import json
import os
import time
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import HIGH_CONFIDENCE_THRESHOLD, MEDIUM_CONFIDENCE_THRESHOLD, MAX_RETRIES, RETRY_DELAY_SECONDS


def load_json(filepath: str) -> dict | list:
    """Load and parse a JSON file.

    Args:
        filepath: Absolute or relative path to the JSON file.

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  [helpers] ERROR: File not found → {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"  [helpers] ERROR: Invalid JSON in {filepath} → {e}")
        raise


def format_confidence(score: float) -> str:
    """Return an emoji + label string for a confidence score.

    Args:
        score: Numeric confidence value (0-100).

    Returns:
        Formatted string like '🟢 High (92%)'.
    """
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return f"🟢 High ({score}%)"
    elif score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return f"🟡 Medium ({score}%)"
    else:
        return f"🔴 Low ({score}%)"


def format_decision(decision: str) -> str:
    """Return a styled text representation for a supply-chain decision.

    Args:
        decision: One of 'AUTO_ORDER', 'RESERVE', or 'ESCALATE_TO_HUMAN'.

    Returns:
        Emoji-prefixed decision string.
    """
    styles = {
        "AUTO_ORDER": "✅ AUTO ORDER — Part will be dispatched automatically",
        "RESERVE": "🔶 RESERVE — Part reserved pending technician confirmation",
        "ESCALATE_TO_HUMAN": "🚨 ESCALATE — Requires human review before ordering",
    }
    return styles.get(decision, f"❓ UNKNOWN — {decision}")


def get_timestamp() -> str:
    """Return the current UTC timestamp as an ISO-8601 string.

    Returns:
        Timestamp string, e.g. '2026-06-29T09:30:52Z'.
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_llm_json(response_text: str) -> dict | list:
    """Parse a JSON payload from an LLM response.

    Handles both raw JSON strings and responses wrapped in markdown
    code fences (```json ... ``` or ``` ... ```).

    Args:
        response_text: Raw text returned by the LLM.

    Returns:
        Parsed Python object (dict or list).

    Raises:
        json.JSONDecodeError: If the extracted text is not valid JSON.
    """
    text = response_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def retry_llm_call(llm, messages, agent_name="Agent"):
    """Call an LLM with automatic retry on rate-limit errors.

    Retries up to MAX_RETRIES times, waiting RETRY_DELAY_SECONDS between
    each attempt. This handles 429 RESOURCE_EXHAUSTED errors from the
    Gemini API gracefully.

    Args:
        llm: The LangChain LLM instance (ChatGoogleGenerativeAI).
        messages: The messages/prompt to send to the LLM.
        agent_name: Name of the calling agent (for logging).

    Returns:
        The LLM response object.

    Raises:
        Exception: If all retries are exhausted.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(messages)
            return response
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                if attempt < MAX_RETRIES:
                    print(f"  [{agent_name}] ⚠️ Rate limit hit. Waiting {RETRY_DELAY_SECONDS}s before retry {attempt + 1}/{MAX_RETRIES}...")
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    print(f"  [{agent_name}] ❌ Rate limit: All {MAX_RETRIES} retries exhausted.")
                    raise
            else:
                raise

