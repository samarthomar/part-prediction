# AI Parts Recommendation App

Predictive Service Intelligence for GE Appliances Field Operations.
This project consists of a FastAPI Python backend (LangGraph + FAISS + Gemini) and a modern React/Vite frontend.

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js installed (v18+)
- Python installed (3.10+)
- Google Gemini API key

### 1. Environment Configuration
Copy `.env.example` to `.env` and provide your Google Gemini API key:
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

### 2. Start the Backend (FastAPI)
```bash
pip install -r requirements.txt
python server.py
```
Backend runs at `http://localhost:8000`.

### 3. Start the Frontend (React + Vite)
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000`.

---

## 🌐 Deployment to Vercel

### Deploying the Frontend to Vercel
1. Import your GitHub repository (`part-prediction`) into **Vercel**.
2. **Framework Preset**: Vite
3. **Root Directory**: Select `frontend` (or leave default root with the included `vercel.json`).
4. **Environment Variables**:
   - `VITE_API_URL`: URL to your hosted backend (e.g. `https://your-backend.onrender.com`)
   - `VITE_WS_URL`: WebSocket URL to your hosted backend (e.g. `wss://your-backend.onrender.com/ws/recommend`)
5. Click **Deploy**.

> **Note on Backend Hosting:**
> Vercel hosts the frontend static build. The Python backend (which uses persistent WebSockets and LangGraph) can be hosted on platforms that support long-running Python processes such as **Render**, **Railway**, **Fly.io**, or **Google Cloud Run**.

---

## 📂 Project Architecture
```
parts-recommendation-ai/
├── agents/             # Multi-agent intelligence pipeline (Case, Context, Parts, Supply)
├── graph/              # LangGraph workflow orchestration
├── data/               # Parts catalog, historical fixes, asset inventory
├── utils/              # FAISS embeddings, vector search helpers
├── server.py           # FastAPI streaming WebSocket & REST backend
├── config.py           # Configuration and model settings
├── vercel.json         # Vercel deployment configuration
└── frontend/           # Modern React dashboard & real-time streaming UI
```
