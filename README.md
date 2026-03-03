# SRAG — Semantic Retrieval-Augmented Generation

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SRAG is a full-stack Retrieval-Augmented Generation (RAG) application for building document-grounded question-answering systems.**

It combines semantic search, vector retrieval, and large language models to generate accurate, context-aware responses based on your own documents.

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
```

Set environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
export SRAG_LLM_BACKEND="gemini"
export SRAG_EMBEDDING_MODEL="all-MiniLM-L6-v2"
```

Run the API server:

```bash
uvicorn backend.main:app --reload
```

Backend runs at: `http://localhost:8000`

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## 🧠 Core Usage (Python Engine)

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

## 📁 Project Structure

```
SRAG/
├── srag/            # Core RAG engine
│   ├── core/        # Chunking, embeddings, vector store, retriever
│   ├── loaders/     # Document ingestion
│   ├── llm/         # LLM backends
│   ├── config.py
│   └── exceptions.py
│
├── backend/         # FastAPI REST API
├── frontend/        # React application
├── data/            # Sample documents & vector store
├── pyproject.toml
└── README.md
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
pytest tests/
pytest --cov=srag tests/
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

Application will be available at:

* Backend: `localhost:8000`
* Frontend: `localhost:3000`

---

## 📄 License

MIT License
