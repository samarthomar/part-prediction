import streamlit as st
import json
import time
import os
import pandas as pd
from datetime import datetime
import plotly.express as px
from PIL import Image
import base64

# Load GE logo as base64 for embedding in HTML
_GE_LOGO_WHITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "ge_logo_white.svg")
_GE_LOGO_BLUE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "ge_logo.svg")

def _load_logo_b64(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        return base64.b64encode(svg_data.encode()).decode()
    except:
        return ""

_GE_LOGO_WHITE_B64 = _load_logo_b64(_GE_LOGO_WHITE_PATH)
_GE_LOGO_BLUE_B64 = _load_logo_b64(_GE_LOGO_BLUE_PATH)

from config import APP_TITLE, APP_SUBTITLE, MAX_PARTS_TO_PREDICT
from graph.workflow import run_recommendation_streaming

# ============================================================
# PART IMAGE & INVENTORY LOOKUP HELPERS
# ============================================================
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_PARTS_IMAGE_DIR = os.path.join(_PROJECT_ROOT, "static", "parts")
_INVENTORY_PATH = os.path.join(_PROJECT_ROOT, "data", "parts_inventory.json")

_PART_IMAGE_MAP = {
    "compressor": "compressor.png",
    "compressor_v2": "compressor.png",
    "thermostat": "thermostat.png",
    "evaporator_coil": "evaporator_coil.png",
    "evaporator_coil_v2": "evaporator_coil.png",
    "condenser_fan": "condenser_fan.png",
    "drain_pump": "drain_pump.png",
    "drain_pump_v2": "drain_pump.png",
    "inlet_valve": "inlet_valve.png",
    "motor": "motor.png",
    "blower_motor": "motor.png",
    "starter_motor": "motor.png",
    "control_board": "control_board.png",
    "main_bearing": "bearing.png",
    "drum_bearing": "bearing.png",
    "yaw_motor": "motor.png",
    "pitch_actuator": "motor.png",
    "fuel_injector": "inlet_valve.png",
    "coolant_pump": "drain_pump.png",
    "vibration_sensor": "thermostat.png",
}

def _get_part_image_path(part_name: str) -> str:
    """Resolve the image file path for a part name."""
    name_lower = part_name.lower().strip()
    filename = _PART_IMAGE_MAP.get(name_lower)
    if filename:
        path = os.path.join(_PARTS_IMAGE_DIR, filename)
        if os.path.exists(path):
            return path
    # Partial match fallback
    for key, fname in _PART_IMAGE_MAP.items():
        if key in name_lower or name_lower in key:
            path = os.path.join(_PARTS_IMAGE_DIR, fname)
            if os.path.exists(path):
                return path
    # Generic fallback
    generic = os.path.join(_PARTS_IMAGE_DIR, "generic_part.png")
    return generic if os.path.exists(generic) else None


def _lookup_inventory(part_name: str) -> dict:
    """Look up a part in parts_inventory.json by name."""
    try:
        with open(_INVENTORY_PATH, "r") as f:
            inventory = json.load(f)
    except:
        return {}
    name_lower = part_name.lower().strip()
    for item in inventory:
        if item.get("part_name", "").lower() == name_lower:
            return item
    for item in inventory:
        if name_lower in item.get("part_name", "").lower() or item.get("part_name", "").lower() in name_lower:
            return item
    return {}

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="GE Appliances | AI Parts Recommendation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PERSISTENT DATABASE LOGIC
# ============================================================
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "app_database.json")

def load_db():
    if not os.path.exists(DB_FILE):
        return {"complaint_history": [], "feedback_data": {}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"complaint_history": [], "feedback_data": {}}

def save_db(data):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "results" not in st.session_state:
    st.session_state.results = None
if "run_triggered" not in st.session_state:
    st.session_state.run_triggered = False

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .stApp { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #FFFFFF; color: #333333; }
    
    .main-header {
        background-color: #02193C;
        padding: 2.5rem; border-radius: 8px; margin-bottom: 2rem;
        color: white;
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .main-header h1 { color: #ffffff; font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px;}
    .main-header p { color: #4A90D9; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 300; }
    
    .metric-card {
        background: white; border-radius: 8px; padding: 1.5rem;
        border: 1px solid #E0E0E0; transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 140px; display: flex; flex-direction: column; justify-content: center;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); }
    .metric-value { font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 0.2rem; }
    .metric-label { font-size: 0.9rem; color: rgba(255,255,255,0.9); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;}
    
    .metric-gradient {
        border-radius: 8px; padding: 1.5rem 1.2rem; text-align: center; color: white;
        height: 120px; display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .flow-step { display: inline-block; background: #F5F5F5; border-radius: 4px; padding: 0.5rem 1rem; margin: 0.2rem; font-size: 0.85rem; color: #02193C; font-weight: 600; border: 1px solid #E0E0E0; }
    .flow-arrow { display: inline-block; color: #666666; margin: 0 0.3rem; font-size: 1.2rem; }

    .part-row { background: white; border-radius: 8px; padding: 1.2rem; margin: 0.8rem 0; border: 1px solid #E0E0E0; }
    .confidence-high { background: #dcfce7; color: #166534; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #bbf7d0;}
    .confidence-medium { background: #fef9c3; color: #854d0e; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #fef08a;}
    .confidence-low { background: #fee2e2; color: #991b1b; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; border: 1px solid #fecaca;}
    
    .custom-divider { height: 1px; background: #E0E0E0; margin: 2rem 0; border: none; }
    
    .result-card { background: white; border-radius: 8px; padding: 2rem; border: 1px solid #E0E0E0; border-left: 3px solid #0056B3; margin-bottom: 1.5rem; }
    .result-card h3 { color: #02193C; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; border-bottom: 1px solid #E0E0E0; padding-bottom: 0.5rem;}
    
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { height: 3.5rem; font-size: 1.1rem; font-weight: 500; color: #666666; }
    .stTabs [aria-selected="true"] { color: #0056B3 !important; border-bottom-color: #0056B3 !important; }
    
    /* Override primary button to be orange */
    button[kind="primary"] {
        background-color: #FF6600 !important;
        border-color: #FF6600 !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #e65c00 !important;
        border-color: #e65c00 !important;
    }
    
    @keyframes spin { 100% { transform:rotate(360deg); } }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(f'''
<div class="main-header">
    <img src="data:image/svg+xml;base64,{_GE_LOGO_WHITE_B64}" alt="GE Appliances" style="height:56px; flex-shrink:0;" />
    <div style="margin-left:0.5rem;">
        <h1>AI Parts Recommendation</h1>
        <p>Predictive Service Intelligence for GE Field Operations</p>
    </div>
</div>
''', unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2 = st.tabs(["AI Recommendation", "Operations Dashboard"])

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f'''
    <div style="background:#02193C; margin:-1rem -1rem 1.5rem -1rem; padding:1.5rem 1rem; text-align:center;">
        <img src="data:image/svg+xml;base64,{_GE_LOGO_WHITE_B64}" alt="GE Appliances" style="height:42px;" />
        <div style="color:#4A90D9;font-size:0.8rem;margin-top:0.5rem;">Service Intelligence</div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("### New Service Request")
    st.markdown("---")
    
    complaint_text = st.text_area(
        "Customer Complaint",
        placeholder="e.g., Refrigerator not cooling properly, making loud humming noise...",
        height=120, key="complaint_input"
    )
    
    st.markdown("---")
    st.markdown("##### Optional Details")
    
    product_type = st.selectbox(
        "Product Type",
        ["Auto-Detect", "Refrigerator", "Washing Machine", "HVAC/Air Conditioner", "Wind Turbine", "Industrial Generator"]
    )
    
    model_options = {
        "Auto-Detect": ["Auto-Detect"],
        "Refrigerator": ["Auto-Detect", "RF-28X", "RF-22S", "RF-35P"],
        "Washing Machine": ["Auto-Detect", "WM-12A", "WM-18B", "WM-20C"],
        "HVAC/Air Conditioner": ["Auto-Detect", "AC-15T", "AC-22R", "AC-30S"],
        "Wind Turbine": ["Auto-Detect", "WT-500", "WT-300", "WT-700"],
        "Industrial Generator": ["Auto-Detect", "GN-100", "GN-250"]
    }
    model = st.selectbox("Model Number", model_options.get(product_type, ["Auto-Detect"]))
    
    st.markdown("---")
    st.markdown("##### Try Sample Complaints")
    
    samples = {
        "Fridge Not Cooling": "Refrigerator not cooling properly. Ice buildup on back panel and loud humming noise. Model RF-28X, 5 years old.",
        "Washer Leaking": "Washing machine leaking water from bottom during spin cycle. Also vibrating excessively. Model WM-12A.",
        "AC Grinding Noise": "AC unit making grinding noise and not cooling. Thermostat shows error code E205. Unit is 3 years old, model AC-22R.",
        "Turbine Vibration": "High vibration and overheating detected in wind turbine WT-500. Error codes E102 and E215. Priority urgent.",
        "Generator Shutdown": "Industrial generator GN-250 experienced complete shutdown during operation. Temperature spike before failure."
    }
    
    for label, sample in samples.items():
        if st.button(label, use_container_width=True, key=f"s_{label}"):
            st.session_state["use_sample"] = sample
            st.rerun()
    
    if "use_sample" in st.session_state:
        complaint_text = st.session_state.pop("use_sample")
    
    st.markdown("---")
    
    if st.button("Run AI Recommendation", type="primary", use_container_width=True, disabled=not complaint_text):
        st.session_state.run_triggered = True
        st.session_state.current_complaint = complaint_text
        st.session_state.current_product = product_type if product_type != "Auto-Detect" else None
        st.session_state.current_model = model if model != "Auto-Detect" else None


    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Database Management")
    if st.button("Clear Database (Reset All)", type="secondary", use_container_width=True):
        st.session_state.db = {"complaint_history": [], "feedback_data": {}}
        save_db(st.session_state.db)
        st.session_state.results = None
        st.success("Database cleared successfully.")
        time.sleep(1)
        st.rerun()

# ============================================================
# TAB 1 — AI RECOMMENDATION
# ============================================================
with tab1:
    if not st.session_state.run_triggered and st.session_state.results is None:
        # Landing state
        st.markdown("### Welcome! Enter a service complaint to get started.")
        st.markdown("""
        <div class="result-card">
            <h3>How It Works — 5 AI Agents powered by LangGraph</h3>
            <br>
            <span class="flow-step">Parse Complaint</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">Find Similar Cases</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">Predict Parts</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">Check Inventory</span>
            <span class="flow-arrow">→</span>
            <span class="flow-step">Learn & Improve</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-gradient" style="background:linear-gradient(135deg,#02193C,#0056B3);"><div style="font-weight:600;font-size:1.2rem;">Google Gemini</div><div style="font-size:0.85rem;opacity:0.9;margin-top:0.4rem;">2.5 Flash LLM</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-gradient" style="background:linear-gradient(135deg,#0056B3,#4A90D9);"><div style="font-weight:600;font-size:1.2rem;">LangGraph</div><div style="font-size:0.85rem;opacity:0.9;margin-top:0.4rem;">Agent Orchestration</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-gradient" style="background:linear-gradient(135deg,#FF6600,#FF8533);"><div style="font-weight:600;font-size:1.2rem;">FAISS</div><div style="font-size:0.85rem;opacity:0.9;margin-top:0.4rem;">Vector Search (RAG)</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="metric-gradient" style="background:linear-gradient(135deg,#10b981,#059669);"><div style="font-weight:600;font-size:1.2rem;">5 AI Agents</div><div style="font-size:0.85rem;opacity:0.9;margin-top:0.4rem;">Multi-Agent System</div></div>', unsafe_allow_html=True)
        
    elif st.session_state.run_triggered:
        # Run the pipeline
        st.session_state.run_triggered = False
        
        complaint = st.session_state.current_complaint
        prod = st.session_state.current_product
        mod = st.session_state.current_model
        
        st.markdown(f"""
        <div class="result-card">
            <h3>Service Request</h3>
            <p><b>Complaint:</b> {complaint}</p>
            <p><b>Product:</b> {prod or 'Auto-Detect'} | <b>Model:</b> {mod or 'Auto-Detect'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        agent_info = {
            "case_intelligence": {"name": "Case Intelligence", "desc": "Extract product, model & symptoms from complaint"},
            "context_enrichment": {"name": "Context Enrichment", "desc": "Retrieve similar past cases to identify resolution patterns"},
            "parts_prediction": {"name": "Parts Prediction", "desc": "Predict required parts using LLM and historical context"},
            "supply_decision": {"name": "Supply Decision", "desc": "Check inventory & determine supply action"},
            "feedback_learning": {"name": "Feedback & Learning", "desc": "Evaluate confidence and update system learning"},
        }
        
        tracker = st.empty()
        completed = []
        full_state = {}
        
        # We will re-render the agent panel on every step
        try:
            for agent_name, agent_output in run_recommendation_streaming(
                complaint_text=complaint, product_type=prod, model=mod, error_codes=[]
            ):
                if agent_name == "error":
                    st.error(f"Pipeline Error: {agent_output.get('error_message', 'Unknown')}")
                    break
                
                completed.append(agent_name)
                full_state.update(agent_output)
                
                # Render the sequential dark panel using individual markdown calls
                with tracker.container():
                    # Panel header
                    st.markdown('<div style="background:#0A1628; border-radius:16px 16px 0 0; padding:1.5rem; border:1px solid rgba(255,255,255,0.08); border-bottom:1px solid rgba(255,255,255,0.08);"><div style="color:white;font-weight:700;font-size:1.2rem;">Agent Orchestration Pipeline</div><div style="color:#64748b;font-size:0.85rem;margin-top:4px;">LangGraph sequential pipeline — each node checkpoints its state</div></div>', unsafe_allow_html=True)
                    
                    for idx, (key, info) in enumerate(agent_info.items()):
                        is_last = idx == len(agent_info) - 1
                        border_radius = "0 0 16px 16px" if is_last else "0"
                        
                        if key in completed:
                            summary_text = ""
                            if key == "case_intelligence":
                                summary_text = f"Product: {full_state.get('product_type', 'Unknown')} | Model: {full_state.get('model', 'Unknown')} | Urgency: {full_state.get('urgency', 'medium').capitalize()}"
                            elif key == "context_enrichment":
                                n_cases = len(full_state.get('similar_cases', []))
                                summary_text = f"Found {n_cases} similar cases in vector database"
                            elif key == "parts_prediction":
                                n_parts = len(full_state.get('predicted_parts', []))
                                summary_text = f"Predicted {n_parts} potential parts needed"
                            elif key == "supply_decision":
                                n_dec = len(full_state.get('supply_decisions', []))
                                summary_text = f"Generated {n_dec} supply decisions"
                            elif key == "feedback_learning":
                                acc = full_state.get('feedback_report', {}).get('simulated_accuracy', 'N/A')
                                summary_text = f"System updated with predicted accuracy: {acc}%"
                            
                            agent_name_str = info['name']
                            agent_desc_str = info['desc']
                            row_html = (
                                f'<div style="background:#0A1628; display:flex; align-items:flex-start; gap:1rem; padding:1.2rem 1.5rem; border-left:1px solid rgba(255,255,255,0.08); border-right:1px solid rgba(255,255,255,0.08); border-bottom:1px solid rgba(255,255,255,0.06); border-radius:{border_radius};">'
                                f'<div style="width:36px;height:36px;border-radius:50%;background:#10b981;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">'
                                f'<span style="color:white;font-weight:700;font-size:1rem;">&#10003;</span></div>'
                                f'<div><div><span style="color:white;font-weight:700;font-size:1.05rem;">{agent_name_str}</span>'
                                f' <span style="background:rgba(255,255,255,0.1);color:#94a3b8;font-size:0.7rem;padding:2px 8px;border-radius:4px;margin-left:8px;text-transform:uppercase;letter-spacing:1px;">AGENT</span></div>'
                                f'<div style="color:#64748b;font-size:0.85rem;margin-top:2px;">{agent_desc_str}</div>'
                                f'<div style="color:#94a3b8;font-size:0.9rem;margin-top:6px;">{summary_text}</div>'
                                f'</div></div>'
                            )
                            st.markdown(row_html, unsafe_allow_html=True)
                        else:
                            agent_name_str = info['name']
                            agent_desc_str = info['desc']
                            row_html = (
                                f'<div style="background:#0A1628; display:flex; align-items:flex-start; gap:1rem; padding:1.2rem 1.5rem; border-left:1px solid rgba(255,255,255,0.08); border-right:1px solid rgba(255,255,255,0.08); border-bottom:1px solid rgba(255,255,255,0.06); opacity:0.4; border-radius:{border_radius};">'
                                f'<div style="width:36px;height:36px;border-radius:50%;background:#334155;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">'
                                f'<span style="color:#64748b;font-size:0.8rem;">&#9675;</span></div>'
                                f'<div><div><span style="color:#94a3b8;font-weight:600;font-size:1.05rem;">{agent_name_str}</span>'
                                f' <span style="background:rgba(255,255,255,0.05);color:#475569;font-size:0.7rem;padding:2px 8px;border-radius:4px;margin-left:8px;text-transform:uppercase;letter-spacing:1px;">AGENT</span></div>'
                                f'<div style="color:#475569;font-size:0.85rem;margin-top:2px;">{agent_desc_str}</div>'
                                f'</div></div>'
                            )
                            st.markdown(row_html, unsafe_allow_html=True)
                
                time.sleep(0.3)
            
            # Save results
            st.session_state.results = full_state
            
            # Save to persistent database
            history_entry = {
                "id": f"CR-{len(st.session_state.db['complaint_history']) + 1001}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "complaint": complaint,
                "product_type": full_state.get("product_type", prod or "Unknown"),
                "model": full_state.get("model", mod or "Unknown"),
                "urgency": full_state.get("urgency", "medium"),
                "predicted_parts": full_state.get("predicted_parts", [])[:3],
                "supply_decisions": full_state.get("supply_decisions", []),
                "feedback_report": full_state.get("feedback_report", {})
            }
            st.session_state.db["complaint_history"].append(history_entry)
            save_db(st.session_state.db)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)

    elif st.session_state.results is not None:
        # Display stored results
        full_state = st.session_state.results
        
        # ─── Agent 1: Case Intelligence ───
        st.markdown('<div class="result-card"><h3>Agent 1: Case Intelligence</h3>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Product Type", full_state.get("product_type", "Unknown"))
        with col2:
            st.metric("Model", full_state.get("model", "Unknown"))
        with col3:
            urgency = full_state.get("urgency", "medium")
            st.metric("Urgency", f"{urgency.title()}")
        with col4:
            symptoms = full_state.get("symptoms", [])
            st.metric("Symptoms Found", len(symptoms))
        
        if symptoms:
            st.markdown("**Extracted Symptoms:** " + " | ".join([f"`{s}`" for s in symptoms]))
        if full_state.get("issue_summary"):
            st.info(f"**AI Summary:** {full_state['issue_summary']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── Agent 2: Context Enrichment ───
        st.markdown('<div class="result-card"><h3>Agent 2: Context Enrichment</h3>', unsafe_allow_html=True)
        similar_cases = full_state.get("similar_cases", [])
        
        if similar_cases:
            st.markdown(f"**Found {len(similar_cases)} similar past cases from historical database:**")
            for i, case in enumerate(similar_cases[:3], 1):
                meta = case.get("metadata", {})
                case_title = f"{meta.get('issue_category', 'Repair Case')} — {meta.get('product_type', '')} {meta.get('model', '')}"
                with st.expander(f"Similar Case {i}: {case_title} (Match Score: {case.get('score', 'N/A')})"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f"**Parts Replaced:** `{meta.get('parts_used', 'N/A')}`")
                        st.markdown(f"**Primary Part:** `{meta.get('primary_part', 'N/A')}`")
                    with c2:
                        success = meta.get('fix_successful', 'N/A')
                        st.markdown(f"**Fix Successful:** {'Yes' if success == 'True' else 'No' if success == 'False' else 'N/A'}")
                        ftf = meta.get('first_time_fix', 'N/A')
                        st.markdown(f"**First-Time Fix:** {'Yes' if ftf == 'True' else 'No' if ftf == 'False' else 'N/A'}")
                    with c3:
                        st.markdown(f"**Resolution Time:** {meta.get('resolution_time_hours', 'N/A')} hours")
                        st.markdown(f"**Root Cause:** `{meta.get('root_cause', 'N/A')}`")
                    if meta.get("technician_notes"):
                        st.markdown(f"**Technician Notes:** {meta['technician_notes']}")
        else:
            st.warning("No similar cases found. The FAISS index may still be building.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── Agent 3: Parts Prediction (TOP 3 ONLY) ───
        st.markdown('<div class="result-card"><h3>Agent 3: Parts Prediction — Top Recommendations</h3>', unsafe_allow_html=True)
        predicted_parts = full_state.get("predicted_parts", [])[:3]  # TOP 3 ONLY
        
        if predicted_parts:
            for i, part in enumerate(predicted_parts, 1):
                confidence = part.get("confidence_percent", 0)
                if isinstance(confidence, str):
                    try: confidence = int(confidence)
                    except: confidence = 50
                
                if confidence >= 75: conf_class = "confidence-high"
                elif confidence >= 50: conf_class = "confidence-medium"
                else: conf_class = "confidence-low"
                
                # Look up part specification from inventory
                inv_info = _lookup_inventory(part.get("part_name", ""))
                part_id = inv_info.get("part_id", "—")
                part_desc = inv_info.get("part_description", "")
                
                p3_left, p3_right = st.columns([3, 2])
                with p3_left:
                    st.markdown(f"""
                    <div class="part-row">
                        <div style="flex:1;">
                            <span style="font-weight:700; font-size:1.1rem; color:#02193C;">Option {i}: {part.get('part_name', 'Unknown').replace('_', ' ').title()}</span>
                            <br><span style="font-size:0.9rem; color:#666666;">{part.get('reasoning', 'Based on historical data analysis')}</span>
                        </div>
                        <div style="margin-top:0.5rem;">
                            <span class="{conf_class}">{confidence}% confidence</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(confidence / 100)
                with p3_right:
                    st.markdown(f"""
                    <div style="background:#F5F5F5; border-radius:8px; padding:1rem; margin:0.8rem 0; border-left: 4px solid #0056B3; border: 1px solid #E0E0E0; border-left-width: 4px;">
                        <div style="font-size:0.8rem; color:#666666; text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Part Specification</div>
                        <div style="font-size:1rem; font-weight:600; color:#333333; margin-top:0.4rem;">{part_id}</div>
                        <div style="font-size:0.9rem; color:#666666; margin-top:0.2rem;">{part_desc if part_desc else 'Specification not available in inventory'}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No parts predicted. Please try with more detail in the complaint.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── Agent 4: Supply Decision ───
        st.markdown('<div class="result-card"><h3>Agent 4: Supply Decision & Inventory Check</h3>', unsafe_allow_html=True)
        supply_decisions = full_state.get("supply_decisions", [])
        
        if supply_decisions:
            for sd_idx, sd in enumerate(supply_decisions):
                part_name_raw = sd.get("part_name", "N/A")
                decision = sd.get("decision", "N/A")
                if "AUTO" in str(decision).upper(): decision_display, dec_color = "AUTO ORDER", "#dcfce7"
                elif "RESERVE" in str(decision).upper(): decision_display, dec_color = "RESERVE", "#fef9c3"
                else: decision_display, dec_color = "ESCALATE", "#fee2e2"
                
                part_id = sd.get("part_id", "N/A")
                part_desc = sd.get("part_description", "")
                
                # If agent didn't return these, look them up
                if part_id == "N/A" or not part_desc:
                    inv_info = _lookup_inventory(part_name_raw)
                    if part_id == "N/A":
                        part_id = inv_info.get("part_id", "N/A")
                    if not part_desc:
                        part_desc = inv_info.get("part_description", "")
                
                img_col, info_col, spec_col, stock_col, dec_col = st.columns([1, 2, 2, 2, 1.5])
                
                with img_col:
                    img_path = _get_part_image_path(part_name_raw)
                    if img_path:
                        st.image(img_path, width=90)
                    else:
                        st.markdown("_No image_")
                
                with info_col:
                    st.markdown(f"**{part_name_raw.replace('_', ' ').title()}**")
                    st.markdown(f"Part No: `{part_id}`")
                
                with spec_col:
                    st.markdown(f"**Specification**")
                    st.caption(part_desc if part_desc else "N/A")
                
                with stock_col:
                    qty = sd.get("stock_quantity", sd.get("stock", sd.get("quantity", 0)))
                    loc = sd.get("warehouse_location", sd.get("warehouse", sd.get("location", "N/A")))
                    cost = sd.get("unit_cost_inr", sd.get("unit_cost", 0))
                    st.markdown(f"**Stock:** {qty} units")
                    st.markdown(f"**Location:** {loc}")
                    st.markdown(f"**Cost:** INR {cost:,}")
                
                with dec_col:
                    st.markdown(f'<div style="background:{dec_color}; border-radius:4px; border: 1px solid #E0E0E0; padding:0.6rem; text-align:center; font-weight:600; font-size:0.9rem; margin-top:0.5rem; color: #333333;">{decision_display}</div>', unsafe_allow_html=True)
                
                if sd_idx < len(supply_decisions) - 1:
                    st.markdown("---")
        else:
            st.warning("No supply decisions generated.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── Agent 5: Feedback & Learning ───
        st.markdown('<div class="result-card"><h3>Agent 5: Feedback & Learning</h3>', unsafe_allow_html=True)
        feedback = full_state.get("feedback_report", {})
        
        if feedback:
            conf_summary = feedback.get("confidence_summary", {})
            avg_conf = conf_summary.get("average", 0) if isinstance(conf_summary, dict) else 0
            
            _box = 'text-align:center; padding:1.5rem; border-radius:8px; height:120px; display:flex; flex-direction:column; justify-content:center; align-items:center;'
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div style="{_box} background:#02193C;"><div class="metric-value">{feedback.get("simulated_accuracy", "N/A")}%</div><div class="metric-label">Accuracy</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div style="{_box} background:#0056B3;"><div class="metric-value">{feedback.get("predicted_parts_count", 0)}</div><div class="metric-label">Parts Predicted</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="{_box} background:#4A90D9;"><div class="metric-value">{avg_conf}%</div><div class="metric-label">Avg Confidence</div></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div style="{_box} background:#FF6600;"><div class="metric-value">Logged</div><div class="metric-label">To VectorStore</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ─── Technician Feedback (Persistent) ───
        st.markdown('<div class="result-card" style="background: #F5F5F5; border: 1px dashed #0056B3;"><h3>Technician Feedback</h3><p style="color:#666666">After repair, submit feedback to continuously improve the AI model.</p>', unsafe_allow_html=True)
        
        current_case_id = st.session_state.db["complaint_history"][-1]["id"] if st.session_state.db["complaint_history"] else "N/A"
        
        # Only show form if feedback hasn't been submitted yet for this case
        if current_case_id in st.session_state.db.get("feedback_data", {}):
            st.success(f"Feedback already submitted for Case {current_case_id}. Data successfully logged to database.")
        else:
            with st.form(key="feedback_form"):
                fb_col1, fb_col2 = st.columns(2)
                with fb_col1:
                    accuracy = st.selectbox(
                        "Was the prediction accurate?",
                        ["Yes — exact parts were needed", "Partially — some parts were correct", "No — different parts were needed"],
                        key="fb_accuracy"
                    )
                with fb_col2:
                    actual_parts = st.text_input(
                        "Actual parts used (if different)",
                        placeholder="e.g., compressor, thermostat",
                        key="fb_actual"
                    )
                
                fb_notes = st.text_area("Additional Notes", placeholder="Any observations from the repair...", height=80, key="fb_notes")
                
                submitted = st.form_submit_button("Submit Feedback & Retrain Model", use_container_width=True, type="primary")
                
                if submitted:
                    feedback_entry = {
                        "case_id": current_case_id,
                        "accuracy": accuracy,
                        "actual_parts": actual_parts,
                        "notes": fb_notes,
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.db["feedback_data"][current_case_id] = feedback_entry
                    save_db(st.session_state.db)
                    
                    st.success(f"Feedback submitted. Database updated. This data will be used to enrich the vector store.")
                    time.sleep(1)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Button to run new complaint
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start New Service Request", use_container_width=True, type="secondary"):
            st.session_state.results = None
            st.rerun()


# ============================================================
# TAB 2 — PREMIUM DASHBOARD
# ============================================================
with tab2:
    history = st.session_state.db.get("complaint_history", [])
    feedback_data = st.session_state.db.get("feedback_data", {})
    
    if not history:
        st.info("Database is empty. Go to the AI Recommendation tab to submit your first complaint.")
    else:
        st.markdown("### Live Operations Dashboard")
        st.markdown("Real-time monitoring of AI prediction accuracy, operational metrics, and technician feedback loops.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ─── Summary Metrics ───
        total_complaints = len(history)
        total_feedback = len(feedback_data)
        
        feedbacks_accurate = sum(1 for f in feedback_data.values() if "Yes" in f.get("accuracy", ""))
        feedbacks_partial = sum(1 for f in feedback_data.values() if "Partial" in f.get("accuracy", ""))
        avg_accuracy = round((feedbacks_accurate * 100 + feedbacks_partial * 50) / total_feedback, 1) if total_feedback > 0 else 0
        
        auto_order_count = sum(1 for h in history for sd in h.get("supply_decisions", []) if "AUTO" in str(sd.get("decision", "")).upper())
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg, #02193C, #0056B3);"><div class="metric-label">Total Requests</div><div class="metric-value">{total_complaints}</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg, #0056B3, #4A90D9);"><div class="metric-label">Auto-Orders Triggered</div><div class="metric-value">{auto_order_count}</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg, #FF6600, #FF8533);"><div class="metric-label">Feedback Submissions</div><div class="metric-value">{total_feedback}</div></div>', unsafe_allow_html=True)
        with m_col4:
            st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg, #10b981, #059669);"><div class="metric-label">Confirmed Accuracy</div><div class="metric-value">{avg_accuracy}%</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ─── Plotly Interactive Charts ───
        c_col1, c_col2, c_col3 = st.columns([1, 2, 1])
        with c_col2:
            # Donut Chart for Urgency (Centered, taking up middle column)
            urgency_counts = {}
            for h in history:
                u = h.get("urgency", "unknown").capitalize()
                urgency_counts[u] = urgency_counts.get(u, 0) + 1
                
            fig1 = px.pie(
                names=list(urgency_counts.keys()), 
                values=list(urgency_counts.values()), 
                hole=0.6,
                title="Service Request Urgency",
                color_discrete_sequence=["#02193C", "#0056B3", "#4A90D9", "#FF6600"]
            )
            fig1.update_layout(margin=dict(t=40, b=0, l=0, r=0), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
            
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # ─── Database View (Recent Activity) ───
        st.markdown("#### Master Database Log")
        
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
            
            # Get overall decision
            decisions = h.get("supply_decisions", [])
            decision_display = "N/A"
            if decisions:
                top_decision = decisions[0].get("decision", "N/A")
                if "AUTO" in str(top_decision).upper(): decision_display = "Auto Order"
                elif "RESERVE" in str(top_decision).upper(): decision_display = "Reserve"
                else: decision_display = "Escalate"
            
            table_data.append({
                "Case ID": h["id"],
                "Timestamp": h["timestamp"],
                "Product & Model": f"{h.get('product_type', 'N/A')} ({h.get('model', 'N/A')})",
                "Top Parts Predicted": ", ".join(parts_predicted) if parts_predicted else "None",
                "Action Taken": decision_display,
                "Tech Feedback": fb_status
            })
        
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
        
        st.markdown("#### Manage Records")
        del_col1, del_col2, del_col3 = st.columns([2, 1, 3])
        with del_col1:
            case_to_delete = st.selectbox("Select Case ID to delete:", [h["id"] for h in reversed(history)])
        with del_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Delete Record", type="primary"):
                st.session_state.db["complaint_history"] = [h for h in st.session_state.db["complaint_history"] if h["id"] != case_to_delete]
                if case_to_delete in st.session_state.db.get("feedback_data", {}):
                    del st.session_state.db["feedback_data"][case_to_delete]
                save_db(st.session_state.db)
                st.success(f"Case {case_to_delete} deleted.")
                time.sleep(0.5)
                st.rerun()
