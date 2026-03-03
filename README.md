# SRAG — Semantic Retrieval-Augmented Generation

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SRAG is a full-stack Retrieval-Augmented Generation (RAG) application for building document-grounded question-answering systems.**

It combines semantic search, vector retrieval, and large language models to generate accurate, context-aware responses based on your own documents.

---

## ✨ Features

* 📄 Document ingestion (PDF, TXT, Markdown)
* 🧠 Semantic embeddings (SentenceTransformers)
* 🔎 Vector search (ChromaDB)
* 🤖 LLM integration (Google Gemini)
* 🔍 Source attribution with similarity scores
* ⚡ FastAPI REST API backend
* 💻 React web interface
* 🐳 Docker-ready deployment

---

## 🏗️ Architecture

```
Query → Embedding → Vector Search → Top-K Retrieval → LLM Generation → Answer + Sources
```

**Tech Stack:**
- **Backend:** FastAPI, SQLAlchemy, ChromaDB
- **Frontend:** React 18, Vite, TailwindCSS  
- **Deployment:** Docker, Docker Compose, Nginx
- **LLM:** Google Gemini
- **Embeddings:** SentenceTransformers

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/SxxAq/srag.git
cd srag

# Set API key
export GEMINI_API_KEY="your-api-key"

# Start all services
docker-compose up -d
```

**Access:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Local Development

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -e .
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --reload  # Port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev  # Port 3000
```

---

## 🧠 Core Python Library

Use the RAG engine directly in Python:

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

# Retrieve & generate
retriever = RAGRetriever(vector_store, embedding_mgr)
results = retriever.retrieve("What is RAG?", top_k=5)

llm = get_llm_backend("gemini")
context = "\n\n".join([doc["content"] for doc in results])
answer = llm.generate_with_context("What is RAG?", context)

print(answer)
```

---

## 📁 Project Structure

```
SRAG/
├── srag/                   # Core RAG library
│   ├── core/              # Chunking, embeddings, vector store, retrieval
│   ├── loaders/           # Document ingestion
│   ├── llm/               # LLM backends
│   ├── config.py
│   └── exceptions.py
│
├── backend/               # FastAPI REST API
│   ├── app.py            # Routes & application logic
│   ├── models.py         # Pydantic schemas
│   ├── database.py       # SQLAlchemy models
│   ├── crud.py           # Database operations
│   └── requirements.txt
│
├── frontend/              # React web UI
│   ├── src/components/   # Chat, Upload, Documents, Sidebar
│   ├── src/pages/        # Chat, Documents, Settings
│   ├── src/services/     # API client
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml     # Multi-container orchestration
├── Dockerfile.backend     # Backend container
├── Dockerfile.frontend    # Frontend container
├── nginx.conf            # Reverse proxy
├── DEPLOYMENT.md         # Deployment guide
└── data/                 # Documents & vector store
```

---

## ⚙️ Configuration

Set environment variables in `.env`:

```bash
GEMINI_API_KEY=your-api-key
SRAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
SRAG_LLM_BACKEND=gemini
SRAG_VECTOR_DB_PATH=./data/vector_store
SRAG_TOP_K=5
```

For full configuration options, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 📚 API Endpoints

### Chat
- `POST /api/chat` - Send query with semantic retrieval
- `GET /api/chat/history` - Chat history
- `DELETE /api/chat/history` - Clear history

### Documents
- `POST /api/documents/upload` - Upload PDF/TXT/Markdown
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### System
- `GET /api/health` - Health check
- `GET /api/status` - System status

📖 Full API docs: http://localhost:8000/api/docs (Swagger UI)

---

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Local, Docker, and cloud deployment (GCP, AWS, Heroku, DigitalOcean), scaling, troubleshooting

---

## 📄 License

MIT License

---

Made with ❤️ by [Saalim Aqueel](https://github.com/SxxAq)