# 🤖 Agentic RAG - Intelligent Query Router

A production-ready Retrieval-Augmented Generation (RAG) system with intelligent query routing using LangGraph and Ollama LLM.

## ✨ Features

- **🧠 Intelligent Query Routing**: Automatically routes queries to the best handler:
  - Math questions → Direct LLM
  - General knowledge → Direct LLM  
  - Document questions → RAG with vector search
  
- **⚡ Low Latency**: Optimized with phi model (~5s per query)
- **📊 Real-time Latency Tracking**: See exactly where time is spent
- **🎨 Beautiful UI**: Glassmorphic design with smooth animations
- **📱 Fully Responsive**: Works on all screen sizes

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                  │
│           Glassmorphic UI + Animations              │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTP (Axios)
                     ↓
┌─────────────────────────────────────────────────────┐
│              Backend (FastAPI)                      │
│   ┌──────────────────────────────────────────┐     │
│   │      LangGraph State Machine              │     │
│   │  [Query] → Route → [Retrieve] → [Generate]    │
│   └──────────────────────────────────────────┘     │
└────────────────────┬────────────────────────────────┘
           ┌─────────┴──────────┐
           ↓                    ↓
    ┌────────────────┐  ┌──────────────────┐
    │ Ollama LLM     │  │ Qdrant Vector DB │
    │ (phi model)    │  │ (embeddings)     │
    │ 1.6GB fast     │  │ (1,513 vectors)  │
    └────────────────┘  └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 16+
- Ollama (for LLM)

### Installation

```bash
# Clone repo
git clone https://github.com/sakshimishra/agentic-rag.git
cd agentic-rag

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running

**Terminal 1: Start Ollama**
```bash
ollama serve
```

**Terminal 2: Start Backend**
```bash
cd backend
source .venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

**Terminal 3: Start Frontend**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` in your browser.

## 📊 Performance

| Metric | Value |
|--------|-------|
| Query Routing | <0.001s |
| Vector Search | <0.2s |
| LLM Inference | ~4.96s (phi) |
| **Total** | ~5s |

## 📁 Project Structure

```
agentic-rag/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── langgraph_rag.py       # LangGraph routing & state management
│   ├── vector_store.py         # Qdrant embeddings & search
│   ├── chunking.py             # Document chunking
│   ├── load_docs.py            # Document loading
│   ├── embeddings.py           # Embedding model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ChatBox.jsx     # Main chat UI
│   │   │   └── Message.jsx     # Message rendering with latency display
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── research_papers/
│       ├── *.pdf               # Research papers (7 papers, 176 docs)
│       └── custom/
│           └── company_policy.txt
└── README.md
```

## 🤖 Models & Tech Stack

**Backend:**
- **LLM**: Ollama with phi (2.7B params, 1.6GB)
- **Embeddings**: SentenceTransformer (BAAI/bge-small-en-v1.5)
- **Vector DB**: Qdrant (in-memory)
- **State Management**: LangGraph
- **Framework**: FastAPI

**Frontend:**
- **Framework**: React + Vite
- **Styling**: CSS with glassmorphic design
- **Animations**: Custom keyframes
- **HTTP Client**: Axios

## 🔄 Query Flow

1. **User Input** → Query sent to `/chat` endpoint
2. **Analysis** → Detect query type (math/knowledge/document)
3. **Routing Decision**:
   - Math? → Direct LLM
   - General? → Direct LLM
   - Document? → Vector search + RAG
4. **Generation** → LLM generates response
5. **Response** → JSON with summary/details/key_points + timing data
6. **Display** → Beautiful UI with latency breakdown button

## 📈 Latency Tracking

Every response includes detailed timing breakdown:
```json
{
  "timings": {
    "analyze": 0.000002,
    "retrieve": 0.0,
    "llm_invoke": 4.957028,
    "total": 4.963505
  }
}
```

Click **"⏱️ Show Latency"** button on any response to see breakdown.

## 🛠️ Development

### Adding new models
Edit `backend/langgraph_rag.py`:
```python
llm = OllamaLLM(
    model="neural-chat",  # Change model here
    temperature=0.3,
    top_p=0.9,
)
```

### Adding custom documents
Place files in `data/research_papers/custom/` and restart backend.

## 📝 API Endpoints

- `POST /chat` - Send query
- `POST /debug/route` - See routing decision
- `GET /health` - Health check

## 🚨 Troubleshooting

**Q: API returning 404 for model**
- Run `ollama pull phi` to download model

**Q: Slow responses**
- Check latency with "⏱️ Show Latency" button
- If LLM > 80%, need faster model or GPU

**Q: Vector search not finding documents**
- Restart backend to reload vector store
- Check `data/research_papers/` folder exists

## 📄 License

MIT

## 🙋 Support

For issues or questions, open a GitHub issue.

---

**Built with ❤️ for intelligent RAG**
