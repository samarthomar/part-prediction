"""
Embedding utilities for the Parts Recommendation AI system.

Manages Google Gemini embeddings via LangChain, FAISS vector store creation /
loading, and similarity search over historical fix records.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import GEMINI_API_KEY, EMBEDDING_MODEL, TOP_K_SIMILAR_CASES
from utils.helpers import load_json

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
_VECTORSTORE_DIR = os.path.join(_PROJECT_ROOT, "vectorstore", "faiss_index")
_HISTORICAL_FIXES_PATH = os.path.join(_DATA_DIR, "historical_fixes.json")

# ---------------------------------------------------------------------------
# Embeddings model (lazy-initialised singleton)
# ---------------------------------------------------------------------------
_embeddings_model = None


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a cached GoogleGenerativeAIEmbeddings instance."""
    global _embeddings_model
    if _embeddings_model is None:
        _embeddings_model = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GEMINI_API_KEY,
        )
        print("  [embeddings] Gemini embeddings model initialised.")
    return _embeddings_model


# ---------------------------------------------------------------------------
# Text representation
# ---------------------------------------------------------------------------

def _record_to_text(record: dict) -> str:
    """Convert a historical-fix record into a single text string for embedding.

    Combines symptoms, parts used, product info, and technician notes into a
    searchable passage.
    """
    parts = []
    parts.append(f"Product: {record.get('product_type', 'N/A')} {record.get('model', 'N/A')}")

    symptoms = record.get("symptoms", [])
    if symptoms:
        parts.append(f"Symptoms: {', '.join(symptoms)}")

    error_codes = record.get("error_codes", [])
    if error_codes:
        parts.append(f"Error codes: {', '.join(error_codes)}")

    used_parts = record.get("parts_used", [])
    if used_parts:
        parts.append(f"Parts used: {', '.join(used_parts)}")

    notes = record.get("technician_notes", "")
    if notes:
        parts.append(f"Notes: {notes}")

    resolution = record.get("resolution", "")
    if resolution:
        parts.append(f"Resolution: {resolution}")

    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_vector_store() -> FAISS:
    """Read historical_fixes.json, embed every record, and persist a FAISS index.

    Returns:
        The newly-created FAISS vector store.

    Raises:
        FileNotFoundError: If historical_fixes.json does not exist.
    """
    print("  [embeddings] Building FAISS vector store from historical fixes …")
    records = load_json(_HISTORICAL_FIXES_PATH)

    texts = [_record_to_text(r) for r in records]
    metadatas = [
        {
            "case_id": r.get("case_id", f"case_{i}"),
            "fix_id": r.get("fix_id", ""),
            "product_type": r.get("product_type", ""),
            "model": r.get("model", ""),
            "issue_category": r.get("issue_category", ""),
            "parts_used": ", ".join(r.get("parts_replaced", r.get("parts_used", []))),
            "primary_part": r.get("primary_part", ""),
            "fix_successful": str(r.get("fix_successful", "")),
            "resolution_time_hours": str(r.get("resolution_time_hours", "")),
            "first_time_fix": str(r.get("first_time_fix", "")),
            "technician_notes": r.get("technician_notes", ""),
            "root_cause": r.get("root_cause", ""),
        }
        for i, r in enumerate(records)
    ]

    embeddings = _get_embeddings()
    vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    # Persist to disk
    os.makedirs(os.path.dirname(_VECTORSTORE_DIR), exist_ok=True)
    vectorstore.save_local(_VECTORSTORE_DIR)
    print(f"  [embeddings] FAISS index saved → {_VECTORSTORE_DIR}  ({len(texts)} records)")
    return vectorstore


def load_vector_store() -> FAISS:
    """Load an existing FAISS index from disk.

    If the index does not exist yet, it is built automatically via
    :func:`build_vector_store`.

    Returns:
        The loaded (or freshly-built) FAISS vector store.
    """
    if not os.path.exists(_VECTORSTORE_DIR):
        print("  [embeddings] FAISS index not found — building now …")
        return build_vector_store()

    embeddings = _get_embeddings()
    print(f"  [embeddings] Loading FAISS index from {_VECTORSTORE_DIR}")
    return FAISS.load_local(
        _VECTORSTORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def search_similar_cases(query: str, k: int = TOP_K_SIMILAR_CASES) -> list[dict]:
    """Search the FAISS vector store for the *k* most similar historical cases.

    Args:
        query: Natural-language search string (e.g. symptoms description).
        k: Number of results to return (default from config.TOP_K_SIMILAR_CASES).

    Returns:
        List of dicts, each containing 'text', 'metadata', and 'score'.
    """
    try:
        vs = load_vector_store()
        results = vs.similarity_search_with_score(query, k=k)

        similar_cases = []
        for doc, score in results:
            similar_cases.append(
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": round(float(score), 4),
                }
            )

        print(f"  [embeddings] Found {len(similar_cases)} similar cases for query.")
        return similar_cases

    except Exception as e:
        print(f"  [embeddings] ERROR during similarity search: {e}")
        return []
