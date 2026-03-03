# SRAG — Semantic Retrieval-Augmented Generation

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SRAG is a full-stack Retrieval-Augmented Generation (RAG) application for building document-grounded question-answering systems.**

It combines semantic search, vector retrieval, and large language models to generate accurate, context-aware responses based on your own documents.

### Complete Stack

**Phase 1: Core RAG Library** ✅
- Python 3.11+ with LangChain + SentenceTransformers + ChromaDB
- Modular, extensible architecture

**Phase 2: REST API Backend** ✅
- FastAPI with OpenAPI/Swagger documentation
- Chat API with semantic retrieval
- Document management (upload, list, delete)

**Phase 3: React Web Frontend** ✅
- React 18 + Vite + TailwindCSS
- Beautiful chat interface with source attribution
- Drag-and-drop document upload

**Phase 4: Docker Deployment** ✅
- Docker & Docker Compose for local & production
- Nginx reverse proxy + multi-container orchestration
- Health checks, volumes, networking

---

## ✨ Features

* 📄 Document ingestion (PDF, TXT, Markdown)
* 🧠 Semantic embeddings (SentenceTransformers)
* 🔎 Vector search (ChromaDB / FAISS)
* 🤖 LLM integration (Google Gemini, extensible)
* 🔍 Source attribution with similarity scores
* ⚡ FastAPI backend for document & chat APIs
* 💻 React frontend with chat interface
* 🐳 Docker-ready deployment

---

## 🏗 Architecture

```
User Query
    ↓
Query Embedding
    ↓
Vector Search
    ↓
Top-K Retrieval
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Answer + Sources
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/SxxAq/srag.git
cd srag
```

---

### Backend Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e .
pip install -r backend/requirements.txt  # Install backend API dependencies
```

Set environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
export SRAG_LLM_BACKEND="gemini"
export SRAG_EMBEDDING_MODEL="all-MiniLM-L6-v2"
```

Run the API server:

```bash
python -m uvicorn backend.app:app --reload
```

Backend runs at: `http://localhost:8000`

📖 **Phase 1-4: Complete Documentation**
  - [End-to-End Implementation Plan](END_TO_END_PLAN.md) — 6-day roadmap (all phases completed)
  - [Deployment Guide](DEPLOYMENT.md) — Local, Docker, cloud deployment, scaling, troubleshooting
  - Library source: [`srag/`](srag/) package

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## 🐳 Docker Deployment

### One-Command Deployment

```bash
# Start all services (backend, frontend, database)
docker-compose up -d
```

### Access Points

| Service        | URL                      | Purpose                    |
| -------------- | ------------------------ | -------------------------- |
| **Frontend**   | http://localhost         | Chat interface             |
| **Backend**    | http://localhost:8000    | REST API                   |
| **API Docs**   | http://localhost:8000/api/docs | Interactive API docs |

### Docker Commands

```bash
# View service status
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Rebuild images
docker-compose build --no-cache
```

📖 **Complete Deployment Guide** (local, cloud, scaling, troubleshooting): [`DEPLOYMENT.md`](DEPLOYMENT.md)

---

## 🧠 Core Python Library

```python
from srag import (
    DocumentProcessor,
    split_documents,
    EmbeddingManager,
    VectorStore,
    RAGRetriever,
    get_llm_backend
)

# Load documents
docs = DocumentProcessor().load_text_files("./data")

# Split into chunks
chunks = split_documents(docs)

# Generate embeddings
embedding_mgr = EmbeddingManager()
embeddings = embedding_mgr.generate_embeddings(
    [doc.page_content for doc in chunks]
)

# Store vectors
vector_store = VectorStore()
vector_store.add_documents(chunks, embeddings)

# Retrieve
retriever = RAGRetriever(vector_store, embedding_mgr)
results = retriever.retrieve("What is RAG?", top_k=5)

# Generate answer
llm = get_llm_backend("gemini")
context = "\n\n".join([doc["content"] for doc in results])
answer = llm.generate_with_context("What is RAG?", context)

print(answer)
```

---

## � Project Status

### Completed Phases

✅ **Phase 1**: Core RAG Library (Complete)
  - Document loading, chunking, embedding generation
  - Vector storage (ChromaDB) & semantic retrieval
  - Gemini LLM integration
  - Configuration management & error handling

✅ **Phase 2**: FastAPI REST Backend (Complete)
  - Chat API with context retrieval
  - Document management endpoints
  - Chat history storage
  - OpenAPI documentation

✅ **Phase 3**: React Web Frontend (Complete)
  - Beautiful chat interface
  - Document upload & management UI
  - Settings page with system status
  - Responsive TailwindCSS design

✅ **Phase 4**: Docker & Deployment (Complete)
  - Docker Compose multi-container orchestration
  - Nginx reverse proxy configuration
  - Production deployment guides
  - Health checks & volume persistence

### Next Steps (Post v0.2)

- [ ] Unit & integration tests
- [ ] Query expansion & response reranking
- [ ] Additional LLM backends (OpenAI, Claude, Ollama)
- [ ] Advanced evaluation metrics
- [ ] Multi-language support
- [ ] Conversation memory & context management

---

## 📁 Project Structure

```
SRAG/
├── srag/                   # Phase 1: Core RAG Library
│   ├── core/              # Chunking, embeddings, vector store, retriever
│   ├── loaders/           # Document ingestion (PDF, TXT, MD)
│   ├── llm/               # LLM backends (Gemini, extensible)
│   ├── config.py          # Configuration management
│   └── exceptions.py      # Custom exceptions
│
├── backend/               # Phase 2: FastAPI REST API
│   ├── app.py            # FastAPI application & routes
│   ├── models.py         # Pydantic request/response schemas
│   ├── database.py       # SQLAlchemy models & session
│   ├── crud.py           # Database operations
│   └── requirements.txt   # Backend dependencies
│
├── frontend/              # Phase 3: React Web UI
│   ├── src/
│   │   ├── components/   # Chat, Upload, DocumentList, Sidebar
│   │   ├── pages/        # Chat, Documents, Settings pages
│   │   ├── services/     # Axios API client
│   │   ├── App.jsx       # Root component with routing
│   │   └── index.css     # TailwindCSS styles
│   ├── package.json
│   └── vite.config.js    # API proxy to backend
│
├── docker-compose.yml     # Phase 4: Multi-container orchestration
├── Dockerfile.backend     # Backend container
├── Dockerfile.frontend    # Frontend container
├── nginx.conf            # Reverse proxy configuration
├── DEPLOYMENT.md         # Complete deployment guide
├── END_TO_END_PLAN.md    # Implementation roadmap
└── data/                 # Documents & vector store
```

---

## 🔧 Configuration

Environment variables:

```bash
SRAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
SRAG_VECTOR_DB_TYPE=chroma
SRAG_VECTOR_DB_PATH=./data/vector_store
SRAG_TOP_K=5
SRAG_SIMILARITY_THRESHOLD=0.0
SRAG_LLM_BACKEND=gemini
SRAG_LLM_MODEL=gemini-2.5-flash
```

Or configure via `SRAGConfig` in Python.

---

## 🧪 Testing

```bash
# Backend tests
pytest tests/

# Backend with coverage
pytest --cov=srag tests/
```

---

## 🌐 API Endpoints

### Chat
- `POST /api/chat` - Send query with semantic retrieval
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### Documents
- `POST /api/documents/upload` - Upload document (PDF/TXT/MD)
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{id}` - Delete document

### System
- `GET /api/health` - Health check
- `GET /api/status` - System status & models info

📖 **Full API documentation**: http://localhost:8000/api/docs (interactive Swagger UI)

---

## 📄 License

MIT License
