# Conversa AI | by AiwithDhruv — Production Deployment Project

> Intelligent conversational AI with full AWS production infrastructure.
> Live class project for Euron's Future-Proof AI Automation Bootcamp.

---

## Quick Reference

```
┌────────────────────┬──────────────────────────────────────────────┐
│ Field              │ Value                                        │
├────────────────────┼──────────────────────────────────────────────┤
│ What               │ Conversa AI — multi-modal chat + files        │
│ Frontend           │ Next.js 14 + TypeScript + Tailwind CSS       │
│ Backend            │ Python 3.11 + FastAPI                        │
│ AI                 │ OpenAI GPT-4o (text + vision + streaming)    │
│ Database           │ MongoDB Atlas                                │
│ Cache              │ Redis (ElastiCache)                          │
│ Deployment         │ AWS ECS Fargate + ALB + ECR                  │
│ CI/CD              │ GitHub Actions → ECR → ECS                   │
│ Monitoring         │ CloudWatch + Grafana                         │
│ Origin             │ Sudhanshi's live class spec at Euron          │
│ Reusable Skill     │ aws-production-deploy (claude-skills)        │
│ Status             │ BUILT — Ready to deploy                      │
└────────────────────┴──────────────────────────────────────────────┘
```

---

## What This App Does

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    User sends:  "Summarize this quarterly report"               │
│                 + attaches  Q4-Report.pdf (3.2 MB)              │
│                                                                 │
│                          │                                      │
│                          ▼                                      │
│                                                                 │
│    ┌──────────────────────────────────────────────┐             │
│    │  1. PDF text extracted (pdfplumber)          │             │
│    │  2. Text sent as context to GPT-4o           │             │
│    │  3. Response streams back word-by-word (SSE) │             │
│    │  4. Conversation saved to MongoDB            │             │
│    └──────────────────────────────────────────────┘             │
│                                                                 │
│    AI responds: "The Q4 report shows revenue growth of 23%      │
│                  driven primarily by the APAC region..."         │
│                                                                 │
│    Supports: PDF  |  DOCX  |  XLSX  |  PNG/JPG/WEBP            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                                │
│                                                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│   │  Chat UI     │  │  File Upload │  │  Conversation Sidebar    │  │
│   │  (Streaming) │  │  (Drag+Drop) │  │  (History + Delete)      │  │
│   └──────┬───────┘  └──────┬───────┘  └──────────┬───────────────┘  │
│          └─────────────────┴─────────────────────┘                   │
│                             │                                        │
└─────────────────────────────┼────────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOAD BALANCER                          │
│                      (SSL Termination via ACM)                       │
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
└──────────┼───────────────────────────────────────────────────────────┘
           │
           │  API Calls
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                 │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  OpenAI API     │  │  ElastiCache    │  │  MongoDB Atlas      │ │
│  │                 │  │  (Redis)        │  │                     │ │
│  │  GPT-4o         │  │                 │  │  - conversations    │ │
│  │  + Vision API   │  │  - Rate limits  │  │  - messages         │ │
│  │  + Streaming    │  │  - Sessions     │  │  - files            │ │
│  │                 │  │  - Cache        │  │  - GridFS (binary)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        MONITORING STACK                               │
│                                                                      │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐ │
│  │  CloudWatch              │  │  Grafana Dashboards              │ │
│  │                          │  │                                  │ │
│  │  - /ecs/backend logs     │  │  - API response times (p50/p95) │ │
│  │  - /ecs/frontend logs    │  │  - Request count                │ │
│  │  - CPU/Memory metrics    │  │  - Error rate (5xx)             │ │
│  │  - Custom alarms         │  │  - CPU + Memory utilization     │ │
│  └──────────────────────────┘  └──────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## CI/CD Pipeline

```
┌──────────┐     ┌──────────────────────────────────────┐     ┌───────────────────┐
│          │     │         GitHub Actions                 │     │                   │
│  git     │     │                                        │     │    AWS Cloud      │
│  push    ├────►│  1. Checkout code                      ├────►│                   │
│  (main)  │     │  2. Configure AWS credentials          │     │  ┌─────────────┐ │
│          │     │  3. Login to ECR                       │     │  │     ECR     │ │
└──────────┘     │  4. Build backend Docker image         │     │  │   (Images)  │ │
                 │  5. Build frontend Docker image        │     │  └──────┬──────┘ │
                 │  6. Push both to ECR                   │     │         │        │
                 │  7. Render new task definition          │     │         ▼        │
                 │  8. Deploy to ECS                      │     │  ┌─────────────┐ │
                 │  9. Wait for service stability         │     │  │     ECS     │ │
                 └────────────────────────────────────────┘     │  │  (Fargate)  │ │
                                                                │  └──────┬──────┘ │
                 ┌────────────────────────────────────────┐     │         │        │
                 │   Rolling Deployment                    │     │         ▼        │
                 │                                         │     │  ┌─────────────┐ │
                 │   Old containers keep serving traffic   │     │  │     ALB     │ │
                 │   while new ones start up. Zero         │     │  │  (Live URL) │ │
                 │   downtime deployment.                  │     │  └─────────────┘ │
                 └────────────────────────────────────────┘     └───────────────────┘
```

---

## Request Flow — What Happens When User Sends a Message

```
  User types: "What are the key findings?"  +  attaches Report.pdf
         │
         ▼
┌─ Frontend (Next.js) ──────────────────────────────────────────┐
│                                                                │
│  1. Show user message immediately (optimistic UI)             │
│  2. POST /api/chat/send  (FormData: message + files)          │
│  3. Open SSE stream                                            │
│  4. Render each token as it arrives (like ChatGPT)            │
│  5. On "done" event → reload conversation list                │
│                                                                │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌─ Backend (FastAPI) ───────────────────────────────────────────┐
│                                                                │
│  STEP 1:  Rate limit check (Redis)                            │
│           └─ 429 if exceeded                                   │
│                                                                │
│  STEP 2:  Create or fetch conversation (MongoDB)              │
│                                                                │
│  STEP 3:  Process uploaded files                               │
│           ┌──────────┬──────────┬──────────┬──────────┐       │
│           │   PDF    │   DOCX   │   XLSX   │  IMAGE   │       │
│           │pdfplumber│python-doc│ openpyxl │  base64  │       │
│           │ → text   │ → text   │ → text   │ → b64    │       │
│           └──────────┴──────────┴──────────┴──────────┘       │
│                                                                │
│  STEP 4:  Store user message + file metadata (MongoDB)        │
│                                                                │
│  STEP 5:  Build OpenAI messages array                          │
│           - System prompt                                      │
│           - Last 20 conversation messages (sliding window)    │
│           - File text as context                               │
│           - Images as base64 (Vision API)                     │
│                                                                │
│  STEP 6:  Stream GPT-4o response via SSE                      │
│           - Each token → SSE "token" event                    │
│           - Complete  → SSE "done" event                      │
│                                                                │
│  STEP 7:  Store assistant response (MongoDB)                  │
│                                                                │
│  STEP 8:  Auto-generate conversation title (first message)    │
│           Uses GPT-4o-mini for speed                          │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

## Tech Stack (Layered View)

```
┌──────────────────────────────────────────────────────────────┐
│  FRONTEND                                                     │
│  ├── Next.js 14 (App Router, standalone output)              │
│  ├── TypeScript (strict mode)                                │
│  ├── Tailwind CSS (dark ChatGPT theme)                       │
│  ├── react-markdown + Prism syntax highlighting              │
│  ├── lucide-react (icons)                                    │
│  └── SSE client (fetch + ReadableStream)                     │
├──────────────────────────────────────────────────────────────┤
│  BACKEND                                                      │
│  ├── FastAPI (Python 3.11, async everywhere)                 │
│  ├── OpenAI SDK (GPT-4o + Vision + stream=True)              │
│  ├── Motor (async MongoDB driver)                            │
│  ├── redis-py (async rate limiting + caching)                │
│  ├── pdfplumber / python-docx / openpyxl (file extraction)   │
│  ├── SSE-Starlette (Server-Sent Events)                      │
│  └── Pydantic v2 (models + settings)                        │
├──────────────────────────────────────────────────────────────┤
│  DATA                                                         │
│  ├── MongoDB Atlas (conversations, messages, files, GridFS)  │
│  └── Redis / ElastiCache (rate limits, sessions, cache)      │
├──────────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE                                               │
│  ├── Docker (multi-stage builds, both services)              │
│  ├── Docker Compose (local dev: 4 containers)                │
│  ├── AWS ECS Fargate (serverless containers)                 │
│  ├── AWS ALB (HTTPS, path-based routing, SSL via ACM)        │
│  ├── AWS ECR (container image registry)                      │
│  ├── AWS VPC (public + private subnets, security groups)     │
│  ├── AWS CloudWatch (logs + metrics + alarms)                │
│  └── Grafana OSS (dashboards)                                │
├──────────────────────────────────────────────────────────────┤
│  CI/CD                                                        │
│  └── GitHub Actions → ECR push → ECS deploy (rolling)        │
└──────────────────────────────────────────────────────────────┘
```

---

## MongoDB Collections

```
┌─────────────────────────────────────────────────────────┐
│  DATABASE: conversa_ai                                    │
│                                                          │
│  ┌─ conversations ────────────────────────────────────┐ │
│  │  _id            ObjectId                            │ │
│  │  title          string      "Quarterly Report Q4"   │ │
│  │  message_count  int         12                      │ │
│  │  created_at     datetime    2026-02-28T10:00:00Z    │ │
│  │  updated_at     datetime    2026-02-28T10:30:00Z    │ │
│  │                                                     │ │
│  │  Indexes: created_at                                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ messages ─────────────────────────────────────────┐ │
│  │  _id              ObjectId                          │ │
│  │  conversation_id  string                            │ │
│  │  role             "user" | "assistant"               │ │
│  │  content          string      "Summarize this..."   │ │
│  │  files            [FileMetadata]                     │ │
│  │  token_count      int         342                   │ │
│  │  created_at       datetime                          │ │
│  │                                                     │ │
│  │  Indexes: (conversation_id, created_at)             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌─ files ────────────────────────────────────────────┐ │
│  │  _id              ObjectId                          │ │
│  │  conversation_id  string                            │ │
│  │  filename         string      "report.pdf"          │ │
│  │  content_type     string      "application/pdf"     │ │
│  │  size             int         3200000               │ │
│  │  file_type        "pdf"|"docx"|"xlsx"|"image"       │ │
│  │  extracted_text   string | null                      │ │
│  │  file_data        binary      (GridFS for >5MB)     │ │
│  │  created_at       datetime                          │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## API Endpoints

```
┌────────┬─────────────────────────────────┬────────────────────────────┐
│ Method │ Path                            │ Description                │
├────────┼─────────────────────────────────┼────────────────────────────┤
│ POST   │ /api/chat/send                  │ Chat + files (SSE stream)  │
│ POST   │ /api/chat/send-simple           │ Chat (non-streaming)       │
├────────┼─────────────────────────────────┼────────────────────────────┤
│ GET    │ /api/conversations              │ List all conversations     │
│ GET    │ /api/conversations/:id          │ Get one conversation       │
│ GET    │ /api/conversations/:id/messages │ Get messages               │
│ PATCH  │ /api/conversations/:id          │ Update title               │
│ DELETE │ /api/conversations/:id          │ Delete conversation        │
├────────┼─────────────────────────────────┼────────────────────────────┤
│ GET    │ /api/files/:id                  │ File metadata              │
│ GET    │ /api/files/:id/download         │ Download file binary       │
│ GET    │ /api/files/:id/text             │ Extracted text             │
├────────┼─────────────────────────────────┼────────────────────────────┤
│ GET    │ /health                         │ Health check (DB + Redis)  │
│ GET    │ /                               │ API info + docs link       │
└────────┴─────────────────────────────────┴────────────────────────────┘
```

---

## AWS Network Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│  VPC: 10.0.0.0/16                                                    │
│                                                                      │
│  ┌─ Public Subnets ────────────────────────────────────────────────┐│
│  │                                                                  ││
│  │  10.0.1.0/24 (ap-south-1a)    10.0.2.0/24 (ap-south-1b)       ││
│  │                                                                  ││
│  │  ┌──────────────────────────────────────────────────────────┐   ││
│  │  │              Application Load Balancer                    │   ││
│  │  │              (Internet-facing, HTTPS)                     │   ││
│  │  └──────────────────────────────────────────────────────────┘   ││
│  │                                                                  ││
│  │  Security Group: Allow 80, 443 from 0.0.0.0/0                  ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  ┌─ Private Subnets ──────────────────────────────────────────────┐│
│  │                                                                  ││
│  │  10.0.10.0/24 (ap-south-1a)   10.0.11.0/24 (ap-south-1b)      ││
│  │                                                                  ││
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    ││
│  │  │  ECS Backend   │  │  ECS Frontend  │  │  ElastiCache   │    ││
│  │  │  (Fargate)     │  │  (Fargate)     │  │  (Redis)       │    ││
│  │  └────────────────┘  └────────────────┘  └────────────────┘    ││
│  │                                                                  ││
│  │  Security Groups:                                                ││
│  │   - ECS: Allow 3000,8000 from ALB SG only                      ││
│  │   - Redis: Allow 6379 from ECS SG only                          ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                      │
│  Internet Gateway ──→ ALB (public)                                   │
│  NAT Gateway ──→ ECS tasks can reach OpenAI API + MongoDB Atlas     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Production Additions (Beyond Original Spec)

These aren't in Sudhanshi's original spec but are **critical for production**:

```
┌─────────────────────────────────────────────────────────────────┐
│  IMPLEMENTED                                                     │
│                                                                  │
│  [x] Streaming (SSE)          — word-by-word like ChatGPT       │
│  [x] Rate limiting            — Redis-based, per-IP             │
│  [x] File size limits         — 10MB max, type validation       │
│  [x] CORS middleware          — frontend/backend split          │
│  [x] Context window mgmt     — sliding window (last 20 msgs)   │
│  [x] Auto conversation title  — GPT-4o-mini generates titles    │
│  [x] Health checks           — /health endpoint (DB + Redis)    │
│  [x] Graceful error handling  — errors don't crash the chat     │
├─────────────────────────────────────────────────────────────────┤
│  FUTURE / NICE-TO-HAVE                                           │
│                                                                  │
│  [ ] Authentication           — NextAuth.js or Supabase Auth    │
│  [ ] Token budget tracking    — daily spend per user            │
│  [ ] S3 for large files      — presigned URLs for >5MB          │
│  [ ] Conversation search     — full-text search over history    │
│  [ ] Export conversations     — PDF/Markdown export             │
│  [ ] Websocket option        — bidirectional for typing status  │
│  [ ] Cost tracking dashboard — daily/monthly OpenAI spend       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Bootcamp Phase Mapping

```
┌───────────────────────────────────────────────────────────────────┐
│  Future-Proof AI Automation Bootcamp — Euron                      │
│                                                                   │
│  Phase 4 (Week 9)                                                 │
│  └── RAG + Chatbot                                                │
│      └── This project: file upload → extract → send as context   │
│                                                                   │
│  Phase 5 (Week 11-12)                                             │
│  └── Docker, Deployment, Monitoring                               │
│      ├── Dockerfiles (multi-stage builds)                        │
│      ├── docker-compose.yml (local dev)                          │
│      ├── ECS Fargate (production deploy)                         │
│      ├── GitHub Actions CI/CD                                    │
│      └── CloudWatch + Grafana monitoring                         │
│                                                                   │
│  Phase 7 (Week 15-17)                                             │
│  └── Full-Stack AI App Capstone                                   │
│      └── This entire project IS the capstone                     │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Reusable Deployment Skill

The AWS deployment pattern from this project is extracted into a reusable skill:

```
.context/claude-skills/.claude/skills/aws-production-deploy/SKILL.md
```

Use it for ANY project that needs:
```
Docker → ECR → ECS Fargate → ALB → CloudWatch → Grafana
```

---

*Last updated: 2026-02-28 | Version: 2.0 — Conversa AI by AiwithDhruv — LIVE on AWS*
