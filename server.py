"""
FastAPI Backend — GE Appliances AI Parts Recommendation
=======================================================
Thin API layer wrapping the existing LangGraph workflow.
Provides REST endpoints + WebSocket for real-time agent streaming.
"""

import os
import sys

# Fix Windows Unicode encoding for emoji characters in agent print() calls
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import run_recommendation_streaming

# ============================================================
# APP SETUP
# ============================================================
app = FastAPI(title="GE Appliances AI Parts Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve part images as static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static", "parts")
if os.path.exists(STATIC_DIR):
    app.mount("/static/parts", StaticFiles(directory=STATIC_DIR), name="parts")

LOGO_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(LOGO_DIR):
    app.mount("/static", StaticFiles(directory=LOGO_DIR), name="static")

# ============================================================
# DATABASE (same JSON file as before)
# ============================================================
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "app_database.json")
INVENTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "parts_inventory.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return {"complaint_history": [], "feedback_data": {}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"complaint_history": [], "feedback_data": {}}

def save_db(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def lookup_inventory(part_name: str) -> dict:
    inventory = load_inventory()
    name_lower = part_name.lower().strip()
    for item in inventory:
        if item.get("part_name", "").lower() == name_lower:
            return item
    for item in inventory:
        if name_lower in item.get("part_name", "").lower() or item.get("part_name", "").lower() in name_lower:
            return item
    return {}

# Part image mapping
PART_IMAGE_MAP = {
    "compressor": "compressor.png", "compressor_v2": "compressor.png",
    "thermostat": "thermostat.png", "evaporator_coil": "evaporator_coil.png",
    "evaporator_coil_v2": "evaporator_coil.png", "condenser_fan": "condenser_fan.png",
    "drain_pump": "drain_pump.png", "drain_pump_v2": "drain_pump.png",
    "inlet_valve": "inlet_valve.png", "motor": "motor.png",
    "blower_motor": "motor.png", "starter_motor": "motor.png",
    "control_board": "control_board.png", "main_bearing": "bearing.png",
    "drum_bearing": "bearing.png", "yaw_motor": "motor.png",
    "pitch_actuator": "motor.png", "fuel_injector": "inlet_valve.png",
    "coolant_pump": "drain_pump.png", "vibration_sensor": "thermostat.png",
}

def get_part_image_url(part_name: str) -> str:
    name_lower = part_name.lower().strip()
    filename = PART_IMAGE_MAP.get(name_lower)
    if filename:
        return f"/static/parts/{filename}"
    for key, fname in PART_IMAGE_MAP.items():
        if key in name_lower or name_lower in key:
            return f"/static/parts/{fname}"
    return "/static/parts/generic_part.png"


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================
class ComplaintRequest(BaseModel):
    complaint_text: str
    product_type: Optional[str] = None
    model: Optional[str] = None

class FeedbackRequest(BaseModel):
    case_id: str
    accuracy: str
    actual_parts: Optional[str] = ""
    notes: Optional[str] = ""


# ============================================================
# WEBSOCKET — Real-time Agent Streaming
# ============================================================
@app.websocket("/ws/recommend")
async def ws_recommend(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive complaint data from frontend
        data = await websocket.receive_json()
        complaint_text = data.get("complaint_text", "")
        product_type = data.get("product_type")
        model = data.get("model")

        if not complaint_text:
            await websocket.send_json({"type": "error", "message": "No complaint text provided"})
            await websocket.close()
            return

        # Agent metadata for descriptions
        agent_meta = {
            "case_intelligence": {"name": "Case Intelligence Agent", "desc": "Extract product, model & symptoms from complaint"},
            "context_enrichment": {"name": "Context Enrichment Agent", "desc": "Retrieve similar past cases from vector database"},
            "parts_prediction": {"name": "Parts Prediction Agent", "desc": "Predict required parts using LLM and historical context"},
            "supply_decision": {"name": "Supply Decision Agent", "desc": "Check inventory & determine supply action"},
            "feedback_learning": {"name": "Feedback & Learning Agent", "desc": "Evaluate confidence and update system learning"},
        }

        # Send "started" signal
        await websocket.send_json({"type": "started", "total_agents": 5})

        full_state = {}

        # Stream through agents
        def run_sync():
            """Run the synchronous streaming generator in a way that yields results."""
            results = []
            for agent_name, agent_output in run_recommendation_streaming(
                complaint_text=complaint_text,
                product_type=product_type if product_type and product_type != "Auto-Detect" else None,
                model=model if model and model != "Auto-Detect" else None,
                error_codes=[]
            ):
                results.append((agent_name, agent_output))
            return results

        # Run the blocking workflow in a thread
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, run_sync)

        for agent_name, agent_output in results:
            if agent_name == "error":
                await websocket.send_json({
                    "type": "error",
                    "message": agent_output.get("error_message", "Unknown error")
                })
                break

            full_state.update(agent_output)

            # Build summary text for this agent
            summary = ""
            if agent_name == "case_intelligence":
                summary = f"Product: {full_state.get('product_type', 'Unknown')} | Model: {full_state.get('model', 'Unknown')} | Urgency: {full_state.get('urgency', 'medium').capitalize()}"
            elif agent_name == "context_enrichment":
                n = len(full_state.get("similar_cases", []))
                summary = f"Found {n} similar cases in vector database"
            elif agent_name == "parts_prediction":
                n = len(full_state.get("predicted_parts", []))
                summary = f"Predicted {n} potential parts needed"
            elif agent_name == "supply_decision":
                n = len(full_state.get("supply_decisions", []))
                summary = f"Generated {n} supply decisions"
            elif agent_name == "feedback_learning":
                acc = full_state.get("feedback_report", {}).get("simulated_accuracy", "N/A")
                summary = f"Predicted accuracy: {acc}%"

            meta = agent_meta.get(agent_name, {"name": agent_name, "desc": ""})

            await websocket.send_json({
                "type": "agent_complete",
                "agent_key": agent_name,
                "agent_name": meta["name"],
                "agent_desc": meta["desc"],
                "summary": summary,
                "data": agent_output
            })

            # Small delay between agents for visual effect
            await asyncio.sleep(0.3)

        # Enrich parts data with inventory info and images
        predicted_parts = full_state.get("predicted_parts", [])[:3]
        for part in predicted_parts:
            inv = lookup_inventory(part.get("part_name", ""))
            part["part_id"] = inv.get("part_id", "—")
            part["part_description"] = inv.get("part_description", "")
            part["image_url"] = get_part_image_url(part.get("part_name", ""))

        supply_decisions = full_state.get("supply_decisions", [])
        for sd in supply_decisions:
            pname = sd.get("part_name", "")
            if not sd.get("part_id") or sd.get("part_id") == "N/A":
                inv = lookup_inventory(pname)
                sd["part_id"] = inv.get("part_id", "N/A")
                sd["part_description"] = inv.get("part_description", "")
            sd["image_url"] = get_part_image_url(pname)

        # Save to database
        db = load_db()
        case_id = f"CR-{len(db['complaint_history']) + 1001}"
        history_entry = {
            "id": case_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "complaint": complaint_text,
            "product_type": full_state.get("product_type", product_type or "Unknown"),
            "model": full_state.get("model", model or "Unknown"),
            "urgency": full_state.get("urgency", "medium"),
            "predicted_parts": predicted_parts,
            "supply_decisions": supply_decisions,
            "feedback_report": full_state.get("feedback_report", {})
        }
        db["complaint_history"].append(history_entry)
        save_db(db)

        # Send complete results
        await websocket.send_json({
            "type": "complete",
            "case_id": case_id,
            "results": {
                "product_type": full_state.get("product_type", "Unknown"),
                "model": full_state.get("model", "Unknown"),
                "urgency": full_state.get("urgency", "medium"),
                "symptoms": full_state.get("symptoms", []),
                "issue_summary": full_state.get("issue_summary", ""),
                "similar_cases": full_state.get("similar_cases", []),
                "predicted_parts": predicted_parts,
                "supply_decisions": supply_decisions,
                "feedback_report": full_state.get("feedback_report", {}),
            }
        })

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


# ============================================================
# REST ENDPOINTS
# ============================================================
@app.get("/api/history")
async def get_history():
    db = load_db()
    return {"history": list(reversed(db.get("complaint_history", [])))}

@app.get("/api/dashboard")
async def get_dashboard():
    db = load_db()
    history = db.get("complaint_history", [])
    feedback_data = db.get("feedback_data", {})

    total_complaints = len(history)
    total_feedback = len(feedback_data)

    feedbacks_accurate = sum(1 for f in feedback_data.values() if "Yes" in f.get("accuracy", ""))
    feedbacks_partial = sum(1 for f in feedback_data.values() if "Partial" in f.get("accuracy", ""))
    avg_accuracy = round((feedbacks_accurate * 100 + feedbacks_partial * 50) / total_feedback, 1) if total_feedback > 0 else 0

    auto_order_count = sum(
        1 for h in history for sd in h.get("supply_decisions", [])
        if "AUTO" in str(sd.get("decision", "")).upper()
    )

    # Urgency distribution
    urgency_counts = {}
    for h in history:
        u = h.get("urgency", "unknown").capitalize()
        urgency_counts[u] = urgency_counts.get(u, 0) + 1

    # Parts frequency
    parts_freq = {}
    for h in history:
        for p in h.get("predicted_parts", []):
            name = p.get("part_name", "").replace("_", " ").title()
            if name:
                parts_freq[name] = parts_freq.get(name, 0) + 1

    # Build table data
    table_data = []
    for h in reversed(history):
        parts_predicted = [p.get("part_name", "").replace("_", " ").title() for p in h.get("predicted_parts", [])[:3]]
        fb = feedback_data.get(h["id"])
        if fb:
            if "Yes" in fb.get("accuracy", ""): fb_status = "Accurate"
            elif "Partial" in fb.get("accuracy", ""): fb_status = "Partial"
            else: fb_status = "Incorrect"
        else:
            fb_status = "Pending"

        decisions = h.get("supply_decisions", [])
        decision_display = "N/A"
        if decisions:
            top = decisions[0].get("decision", "N/A")
            if "AUTO" in str(top).upper(): decision_display = "Auto Order"
            elif "RESERVE" in str(top).upper(): decision_display = "Reserve"
            else: decision_display = "Escalate"

        table_data.append({
            "id": h["id"],
            "date": h["timestamp"].split(" ")[0],  # just the date part
            "product": h.get("product_type", "N/A"),
            "model": h.get("model", "N/A"),
            "urgency": h.get("urgency", "medium").capitalize(),
            "top_parts": ", ".join(parts_predicted) if parts_predicted else "None",
            "action": decision_display,
            "feedback": fb_status
        })

    return {
        "total_complaints": total_complaints,
        "auto_orders": auto_order_count,
        "total_feedback": total_feedback,
        "avg_accuracy": avg_accuracy,
        "urgency_distribution": urgency_counts,
        "parts_frequency": parts_freq,
        "records": table_data
    }

@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    db = load_db()
    db.setdefault("feedback_data", {})[req.case_id] = {
        "case_id": req.case_id,
        "accuracy": req.accuracy,
        "actual_parts": req.actual_parts,
        "notes": req.notes,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_db(db)
    return {"status": "ok", "message": f"Feedback saved for {req.case_id}"}

@app.delete("/api/history/{case_id}")
async def delete_record(case_id: str):
    db = load_db()
    db["complaint_history"] = [h for h in db["complaint_history"] if h["id"] != case_id]
    if case_id in db.get("feedback_data", {}):
        del db["feedback_data"][case_id]
    save_db(db)
    return {"status": "ok", "message": f"Deleted {case_id}"}

@app.delete("/api/history")
async def clear_history():
    save_db({"complaint_history": [], "feedback_data": {}})
    return {"status": "ok", "message": "All records cleared"}

@app.get("/api/samples")
async def get_samples():
    return {
        "samples": [
            {"label": "Fridge Not Cooling", "text": "Refrigerator not cooling properly. Ice buildup on back panel and loud humming noise. Model RF-28X, 5 years old."},
            {"label": "Washer Leaking", "text": "Washing machine leaking water from bottom during spin cycle. Also vibrating excessively. Model WM-12A."},
            {"label": "AC Grinding Noise", "text": "AC unit making grinding noise and not cooling. Thermostat shows error code E205. Unit is 3 years old, model AC-22R."},
            {"label": "Turbine Vibration", "text": "High vibration and overheating detected in wind turbine WT-500. Error codes E102 and E215. Priority urgent."},
            {"label": "Generator Shutdown", "text": "Industrial generator GN-250 experienced complete shutdown during operation. Temperature spike before failure."},
        ]
    }


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
