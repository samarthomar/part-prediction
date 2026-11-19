"""
Configuration file for the Parts Recommendation AI System.
Contains API keys, model settings, and system parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# ============================================================
# GOOGLE GEMINI API CONFIGURATION
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
GEMINI_API_KEY_BACKUP = os.environ.get("GOOGLE_API_KEY_BACKUP", "")  # Optional backup key

# LLM Model Settings
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
TEMPERATURE = 0.0  # Fully deterministic — same input always gives same output
MAX_OUTPUT_TOKENS = 2048

# Retry Settings (for handling API rate limits)
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 30  # Wait 30s between retries

# ============================================================
# FAISS VECTOR STORE SETTINGS
# ============================================================
VECTOR_STORE_PATH = "vectorstore/faiss_index"
EMBEDDING_DIMENSION = 768
TOP_K_SIMILAR_CASES = 5  # Number of similar cases to retrieve

# ============================================================
# AGENT DECISION THRESHOLDS
# ============================================================
HIGH_CONFIDENCE_THRESHOLD = 75  # Above this → Auto Order
MEDIUM_CONFIDENCE_THRESHOLD = 50  # Above this → Reserve Part
# Below MEDIUM → Escalate to Human

# ============================================================
# DATA FILE PATHS
# ============================================================
DATA_DIR = "data"
COMPLAINTS_FILE = os.path.join(DATA_DIR, "service_complaints.json")
HISTORICAL_FIXES_FILE = os.path.join(DATA_DIR, "historical_fixes.json")
PARTS_INVENTORY_FILE = os.path.join(DATA_DIR, "parts_inventory.json")
ASSET_CATALOG_FILE = os.path.join(DATA_DIR, "asset_catalog.json")
FALLBACK_RESPONSES_FILE = os.path.join(DATA_DIR, "fallback_responses.json")

# ============================================================
# APPLICATION SETTINGS
# ============================================================
APP_TITLE = "GE Appliances | AI Parts Recommendation"
APP_SUBTITLE = "Predictive Service Intelligence for GE Field Operations"
MAX_PARTS_TO_PREDICT = 5
