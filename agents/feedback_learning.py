"""
Agent 5 — Feedback & Learning Agent

Generates a feedback report for the current prediction pipeline run.
In production this would compare predictions against actual repair outcomes;
here it simulates the feedback loop with realistic metrics.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.helpers import get_timestamp


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def run_feedback_learning(state: dict) -> dict:
    """Create a feedback report summarising the prediction pipeline run.

    **Expected state keys (input):**
    - ``predicted_parts`` (list[dict])
    - ``supply_decisions`` (list[dict])
    - ``issue_summary`` (str)
    - ``urgency`` (str)

    **Added state keys (output):**
    - ``feedback_report`` (dict): Contains prediction metadata, confidence
      summary, simulated accuracy, and status.

    Returns:
        Updated state dict.
    """
    print("\n📝 Agent 5: Feedback & Learning running …")

    try:
        predicted_parts = state.get("predicted_parts", [])
        supply_decisions = state.get("supply_decisions", [])

        # --- Confidence summary -------------------------------------------
        confidences = [p.get("confidence_percent", 0) for p in predicted_parts]
        avg_confidence = round(sum(confidences) / len(confidences), 1) if confidences else 0.0
        max_confidence = max(confidences) if confidences else 0
        min_confidence = min(confidences) if confidences else 0

        # --- Decision breakdown -------------------------------------------
        decision_counts = {}
        for d in supply_decisions:
            dec = d.get("decision", "UNKNOWN")
            decision_counts[dec] = decision_counts.get(dec, 0) + 1

        # --- Simulated accuracy (80–95%) ----------------------------------
        simulated_accuracy = round(random.uniform(80.0, 95.0), 1)

        feedback_report = {
            "prediction_logged": True,
            "timestamp": get_timestamp(),
            "issue_summary": state.get("issue_summary", ""),
            "urgency": state.get("urgency", "unknown"),
            "predicted_parts_count": len(predicted_parts),
            "confidence_summary": {
                "average": avg_confidence,
                "max": max_confidence,
                "min": min_confidence,
            },
            "decision_breakdown": decision_counts,
            "recommendation_status": "logged_for_review",
            "simulated_accuracy": simulated_accuracy,
            "notes": (
                "This is a simulated feedback entry. In production, accuracy "
                "would be computed by comparing predicted parts against actual "
                "parts used during the repair."
            ),
        }

        state["feedback_report"] = feedback_report

        print(f"  ✅ Feedback report generated:")
        print(f"     • Parts predicted   : {len(predicted_parts)}")
        print(f"     • Avg confidence    : {avg_confidence}%")
        print(f"     • Simulated accuracy: {simulated_accuracy}%")
        print(f"     • Status            : logged_for_review")

    except Exception as e:
        print(f"  [feedback_learning] ERROR: {e}")
        state["feedback_report"] = {
            "prediction_logged": False,
            "timestamp": get_timestamp(),
            "error": str(e),
            "recommendation_status": "error",
        }

    return state
