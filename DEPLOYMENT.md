# Deployment Guide

**v0.2.0** | Complete full-stack application

---

## 🚀 Quick Start

### Docker Compose (Recommended)

```bash
git clone https://github.com/SxxAq/srag.git
cd srag

# Set API key
export GEMINI_API_KEY="your-api-key"

# Start all services
docker-compose up -d
```

Access:
- Frontend: http://localhost (or http://localhost:3000)
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

**Useful commands:**
```bash
docker-compose ps              # View status
docker-compose logs -f backend # View backend logs
docker-compose down           # Stop services
docker-compose build --no-cache # Rebuild
```

---

## 💻 Local Development

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
pip install -r backend/requirements.txt

# Configure .env
export GEMINI_API_KEY="your-api-key"

# Start
python -m uvicorn backend.app:app --reload
# Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## ☁️ Cloud Deployment

### Google Cloud Run

```bash
# Setup
gcloud auth login
gcloud config set project PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/srag:latest -f Dockerfile.backend .

# Deploy
gcloud run deploy srag \
  --image gcr.io/PROJECT_ID/srag:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key \
  --cpu=2 \
  --memory=4Gi
```

### AWS ECS

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Push image
docker tag srag:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/srag:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/srag:latest

# Create task definition and service via AWS console
```

### Heroku

```bash
heroku login
heroku create srag-app
heroku config:set -a srag-app GEMINI_API_KEY=your-key
git push heroku main
```

---

## 🔧 Environment Variables

```bash
# Required
GEMINI_API_KEY=your-api-key

# Optional (defaults shown)
SRAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
SRAG_LLM_BACKEND=gemini
SRAG_VECTOR_DB_PATH=./data/vector_store
SRAG_CHUNK_SIZE=1000
SRAG_TOP_K=5

# Database (local development)
DATABASE_URL=sqlite:///./data/chat_history.db

# Production database
# DATABASE_URL=postgresql://user:password@host/dbname
```

---

## 🐛 Troubleshooting

**Backend won't start:**
```bash
docker-compose logs backend
# Check GEMINI_API_KEY is set
echo $GEMINI_API_KEY
```

**Frontend can't connect to backend:**
```bash
# Verify Nginx proxy is configured correctly
docker-compose exec frontend curl http://backend:8000/api/health
```

**High memory usage:**
- Reduce SRAG_CHUNK_SIZE
- Increase container memory limits
- Use managed database instead of SQLite

**Database issues:**
```bash
# Reset database
rm -rf data/chat_history.db
docker-compose restart backend
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│         User / Internet                  │
└────────────────┬─────────────────────────┘
                 │
        ┌────────▼─────────┐
        │  Nginx (Frontend)│
        │  Port 80/3000    │
        └────────┬─────────┘
                 │ API Proxy (/api)
         ┌───────▼──────────┐
         │ FastAPI Backend  │
         │ Port 8000        │
         └───────┬──────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
   ┌──▼──┐           ┌─────▼──────┐
   │SQLite│         │   ChromaDB  │
   │(Chat)│         │  (Vectors)  │
   └──────┘         └─────────────┘
```

---

## 📊 Production Checklist

- [ ] HTTPS enabled (managed certificates via cloud)
- [ ] CORS restricted to your domains
- [ ] API keys in secret manager (not .env)
- [ ] Database backups configured
- [ ] Health checks enabled
- [ ] Logging configured
- [ ] Rate limiting applied
- [ ] Security headers set

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)

---

Made with ❤️ by [Saalim Aqueel](https://github.com/SxxAq)
