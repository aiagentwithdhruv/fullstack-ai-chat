# Full-Stack AI Chat

> ChatGPT-like application with multi-modal file support.
> Built with Next.js + FastAPI + MongoDB + AWS.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                                │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│   │  Chat UI     │  │  File Upload │  │  Conversation Sidebar    │  │
│   │  (Streaming) │  │  (Drag+Drop) │  │  (History + Search)      │  │
│   └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│          └─────────────────┴─────────────────────┘                   │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LOAD BALANCER                       │
│                        (SSL Termination)                             │
│                                                                      │
│    /api/*    ──→  Backend  (Port 8000)                               │
│    /grafana* ──→  Grafana  (Port 3001)                               │
│    /*        ──→  Frontend (Port 3000)                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      AWS ECS FARGATE CLUSTER                         │
│                    (Container Insights Enabled)                       │
│                                                                      │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐           │
│   │   Backend    │   │   Frontend   │   │   Grafana    │           │
│   │   FastAPI    │   │   Next.js    │   │   OSS        │           │
│   │   Python 3.11│   │   Node 20   │   │   Dashboards │           │
│   │   Port 8000  │   │   Port 3000  │   │   Port 3001  │           │
│   └──────┬───────┘   └──────────────┘   └──────────────┘           │
│          │                                                           │
│          │  Calls                                                    │
│          ▼                                                           │
│   ┌──────────────────────────────────────────────┐                  │
│   │              OpenAI API (GPT-4o)              │                  │
│   │     Text + Vision + Streaming (SSE)           │                  │
│   └──────────────────────────────────────────────┘                  │
└──────────┬────────────────────────────┬──────────────────────────────┘
           │                            │
           ▼                            ▼
┌─────────────────────┐   ┌──────────────────────────┐
│   ElastiCache       │   │   CloudWatch             │
│   (Redis)           │   │                          │
│                     │   │   - Application Logs     │
│   - Rate Limiting   │   │   - ECS Metrics          │
│   - Session Cache   │   │   - Custom Dashboards    │
│   - Response Cache  │   │   - Alerts & Alarms      │
└─────────────────────┘   └──────────────────────────┘
           │
           ▼
┌─────────────────────┐
│   MongoDB Atlas     │
│                     │
│   - Conversations   │
│   - Messages        │
│   - File Metadata   │
│   - GridFS (files)  │
└─────────────────────┘
```

---

## CI/CD Pipeline

```
┌──────────┐     ┌──────────────────────────────────┐     ┌─────────────────┐
│          │     │       GitHub Actions               │     │                 │
│  git     │     │                                    │     │   AWS Cloud     │
│  push    ├────►│  1. Checkout code                  ├────►│                 │
│  (main)  │     │  2. Build Docker images            │     │  ┌───────────┐ │
│          │     │  3. Push to ECR                    │     │  │    ECR    │ │
└──────────┘     │  4. Update ECS task definition     │     │  │  (Images) │ │
                 │  5. Deploy to ECS Fargate          │     │  └─────┬─────┘ │
                 │  6. Wait for service stability     │     │        │       │
                 └────────────────────────────────────┘     │        ▼       │
                                                            │  ┌───────────┐ │
                                                            │  │    ECS    │ │
                                                            │  │ (Fargate) │ │
                                                            │  └───────────┘ │
                                                            └─────────────────┘
```

---

## Request Flow (Chat Message)

```
User types message + attaches files
         │
         ▼
┌─ Frontend (Next.js) ──────────────────────────────┐
│  1. Add user message to UI (optimistic)           │
│  2. POST /api/chat/send (FormData: message+files) │
│  3. Open SSE stream, render tokens as they arrive │
└────────────────────┬──────────────────────────────┘
                     │
                     ▼
┌─ Backend (FastAPI) ───────────────────────────────┐
│  1. Rate limit check (Redis)                      │
│  2. Create/get conversation (MongoDB)             │
│  3. Process files:                                │
│     ┌─────────┬─────────┬─────────┬─────────┐    │
│     │  PDF    │  DOCX   │  XLSX   │  Image  │    │
│     │ extract │ extract │ extract │ base64  │    │
│     │  text   │  text   │  text   │ encode  │    │
│     └─────────┴─────────┴─────────┴─────────┘    │
│  4. Store user message + file metadata (MongoDB)  │
│  5. Build OpenAI messages (history + files)       │
│  6. Stream GPT-4o response via SSE                │
│  7. Store assistant response (MongoDB)            │
│  8. Auto-generate conversation title (first msg)  │
└───────────────────────────────────────────────────┘
```

---

## File Processing Pipeline

```
              ┌─────────────────────────────────┐
              │        File Upload (10MB max)     │
              └───────────────┬─────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌───────────┐  ┌───────────┐  ┌───────────┐
        │   PDF     │  │   DOCX    │  │   XLSX    │
        │ pdfplumber│  │python-docx│  │ openpyxl  │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │               │               │
              ▼               ▼               ▼
        ┌─────────────────────────────────────────┐
        │          Extracted Text                   │
        │   → Sent as context to GPT-4o            │
        └─────────────────────────────────────────┘

        ┌───────────┐
        │   IMAGE   │  (PNG, JPG, WEBP)
        │  base64   │──→ Sent to GPT-4o Vision API
        │  encode   │
        └───────────┘
```

---

## Features

- Text conversations with GPT-4o
- Upload & discuss PDFs, Word docs, Excel sheets, and images
- Streaming responses (Server-Sent Events)
- Conversation history with auto-generated titles
- Inline file preview in chat
- Rate limiting via Redis
- Production-ready AWS deployment (ECS Fargate + ALB)
- Monitoring with CloudWatch + Grafana dashboards
- CI/CD with GitHub Actions (push to deploy)

---

## Tech Stack

```
┌──────────────────────────────────────────────────┐
│  FRONTEND                                         │
│  ├── Next.js 14 (App Router)                     │
│  ├── TypeScript                                   │
│  ├── Tailwind CSS (dark theme)                   │
│  ├── react-markdown + syntax highlighting        │
│  └── lucide-react (icons)                        │
├──────────────────────────────────────────────────┤
│  BACKEND                                          │
│  ├── FastAPI (Python 3.11)                       │
│  ├── OpenAI SDK (GPT-4o + Vision)                │
│  ├── Motor (async MongoDB driver)                │
│  ├── Redis (rate limiting + caching)             │
│  ├── pdfplumber / python-docx / openpyxl         │
│  └── SSE-Starlette (streaming)                   │
├──────────────────────────────────────────────────┤
│  INFRASTRUCTURE                                   │
│  ├── Docker + Docker Compose (local dev)         │
│  ├── AWS ECS Fargate (production)                │
│  ├── AWS ALB (load balancing + SSL)              │
│  ├── AWS ECR (container registry)                │
│  ├── AWS ElastiCache (Redis)                     │
│  ├── MongoDB Atlas (database)                    │
│  ├── CloudWatch (logs + metrics)                 │
│  ├── Grafana (dashboards)                        │
│  └── GitHub Actions (CI/CD)                      │
└──────────────────────────────────────────────────┘
```

---

## Quick Start (Local Dev)

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY
```

### 2. Run with Docker Compose

```bash
cd infra
docker-compose up --build
```

### 3. Access

```
Frontend  →  http://localhost:3000
API Docs  →  http://localhost:8000/docs
Health    →  http://localhost:8000/health
```

---

## Manual Setup (Without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # Edit with your values
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

> Requires MongoDB and Redis running locally.

---

## Project Structure

```
Full-Stack-AI-Chat/
│
├── backend/                      # Python FastAPI
│   ├── app/
│   │   ├── main.py               # App entry + health check
│   │   ├── config.py             # Pydantic settings (env vars)
│   │   ├── api/
│   │   │   ├── chat.py           # POST /api/chat/send (SSE stream)
│   │   │   ├── conversations.py  # CRUD conversations
│   │   │   └── files.py          # File download + metadata
│   │   ├── services/
│   │   │   ├── openai_service.py # GPT-4o streaming + vision
│   │   │   ├── file_processor.py # PDF/DOCX/XLSX/Image extraction
│   │   │   ├── mongo_service.py  # Async MongoDB (Motor)
│   │   │   └── redis_service.py  # Rate limiting + cache
│   │   └── models/
│   │       └── schemas.py        # Pydantic request/response models
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                     # Next.js 14 + TypeScript
│   ├── src/
│   │   ├── app/                  # App Router (layout + page)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx       # Conversation list
│   │   │   ├── ChatArea.tsx      # Message display
│   │   │   ├── ChatMessage.tsx   # Markdown + code + files
│   │   │   ├── ChatInput.tsx     # Auto-resize input
│   │   │   └── FileUpload.tsx    # Drag-and-drop upload
│   │   ├── lib/
│   │   │   ├── api.ts            # API client + SSE parser
│   │   │   └── utils.ts          # Helpers
│   │   └── types/
│   │       └── index.ts          # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
│
├── infra/                        # Infrastructure
│   ├── docker-compose.yml        # Local: backend+frontend+mongo+redis
│   ├── task-definition.json      # ECS Fargate task (2 containers)
│   ├── setup-aws.sh              # Full AWS setup script
│   └── grafana/
│       └── dashboard.json        # Grafana monitoring dashboard
│
├── .github/workflows/
│   └── deploy.yml                # GitHub Actions → ECR → ECS
│
├── .env.example                  # All env vars documented
├── .gitignore
├── LOADOUT.md                    # Project context for AI
└── README.md                     # This file
```

---

## API Endpoints

```
┌────────┬─────────────────────────────────┬───────────────────────────┐
│ Method │ Path                            │ Description               │
├────────┼─────────────────────────────────┼───────────────────────────┤
│ POST   │ /api/chat/send                  │ Chat + files (SSE stream) │
│ POST   │ /api/chat/send-simple           │ Chat (non-streaming)      │
├────────┼─────────────────────────────────┼───────────────────────────┤
│ GET    │ /api/conversations              │ List all conversations    │
│ GET    │ /api/conversations/:id          │ Get one conversation      │
│ GET    │ /api/conversations/:id/messages │ Get messages              │
│ PATCH  │ /api/conversations/:id          │ Update title              │
│ DELETE │ /api/conversations/:id          │ Delete conversation       │
├────────┼─────────────────────────────────┼───────────────────────────┤
│ GET    │ /api/files/:id                  │ File metadata             │
│ GET    │ /api/files/:id/download         │ Download file binary      │
│ GET    │ /api/files/:id/text             │ Get extracted text        │
├────────┼─────────────────────────────────┼───────────────────────────┤
│ GET    │ /health                         │ Health check (DB + Redis) │
└────────┴─────────────────────────────────┴───────────────────────────┘
```

---

## AWS Deployment

### Infrastructure Setup

```bash
chmod +x infra/setup-aws.sh
./infra/setup-aws.sh
```

This creates: VPC, Subnets, Security Groups, ECR repos, ECS cluster, ElastiCache, CloudWatch log groups.

### GitHub Actions Secrets

```
┌──────────────────────────┬────────────────────────────┐
│ Secret                   │ Description                │
├──────────────────────────┼────────────────────────────┤
│ AWS_ACCESS_KEY_ID        │ IAM user access key        │
│ AWS_SECRET_ACCESS_KEY    │ IAM user secret key        │
└──────────────────────────┴────────────────────────────┘
```

### Deploy

```bash
git push origin main
# GitHub Actions automatically: Build → ECR → ECS → Live
```

---

## Monitoring

```
┌─────────────────────────────────────────────────────────────┐
│                    Grafana Dashboard                         │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ API Response     │  │ Request      │  │ Error Rate    │ │
│  │ Time (p50/p95)   │  │ Count        │  │ (5xx)         │ │
│  │ ████████░░ 120ms │  │    1,247     │  │     0.2%      │ │
│  └─────────────────┘  └──────────────┘  └───────────────┘ │
│                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐ │
│  │ ECS CPU Utilization      │  │ ECS Memory Utilization  │ │
│  │ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ 34%    │  │ ▁▂▃▃▃▄▄▅▅▅▄▃▃▂▁ 58%   │ │
│  └─────────────────────────┘  └─────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Backend Logs (Live Stream)                             │ │
│  │ INFO  2026-02-28 POST /api/chat/send 200 1.2s         │ │
│  │ INFO  2026-02-28 GET  /api/conversations 200 45ms     │ │
│  │ WARN  2026-02-28 Rate limit near: 18/20 for 10.0.1.5 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...              # Required

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=fullstack_ai_chat

# Redis
REDIS_URL=redis://localhost:6379

# App
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_PER_MINUTE=20
DAILY_TOKEN_BUDGET=100000
MAX_FILE_SIZE_MB=10

# AWS (production only)
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=your-account-id
```

---

## Euron Bootcamp Mapping

```
Phase 4 (Week 9)      →  RAG + Chatbot
Phase 5 (Week 11-12)  →  Docker, Deployment, Monitoring
Phase 7 (Week 15-17)  →  Full-Stack AI App Capstone
```

This project is a complete reference implementation for the
**Future-Proof AI Automation Bootcamp** at Euron.
