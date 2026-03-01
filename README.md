<div align="center">

# Conversa AI | by AiwithDhruv

### ChatGPT-like app with multi-modal file support — built and deployed from scratch.

![Next.js](https://img.shields.io/badge/Next.js_14-black?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![AWS](https://img.shields.io/badge/AWS_ECS-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Upload PDFs, images, Word docs, Excel sheets — ask questions about them.
Stream AI responses in real-time. Full conversation history. Deployed on AWS with CI/CD.

**Built and deployed in one session with Claude Code.**

<br />

![Conversa AI](assets/chat-interface.jpeg)

<br />

[Live Demo](#live-demo) · [Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Deployment](#deployment)

</div>

---

## Live Demo

| | |
|---|---|
| **GitHub** | [github.com/aiagentwithdhruv/conversa-ai](https://github.com/aiagentwithdhruv/conversa-ai) |
| **Live App** | Deployed on AWS ECS Fargate (ALB + auto-deploy on push) |
| **API Docs** | `/docs` — interactive Swagger UI |

---

## Features

| Feature | What It Does |
|:---|:---|
| **AI Chat** | GPT-4o powered conversations with streaming responses (SSE) |
| **PDF Analysis** | Upload a PDF → AI reads and answers questions about it |
| **Image Understanding** | Upload an image → GPT-4o Vision describes and analyzes it |
| **Word & Excel** | Upload DOCX/XLSX → extracted text becomes AI context |
| **Conversation History** | Auto-titled conversations saved in MongoDB, searchable sidebar |
| **Code Highlighting** | AI code responses with syntax highlighting + copy button |
| **Rate Limiting** | Redis-backed per-IP rate limiting (configurable) |
| **Production Infra** | AWS ECS Fargate + ALB + ECR + CloudWatch + GitHub Actions CI/CD |

---

## Screenshots

### Chat Interface — Code Generation with Syntax Highlighting

![Chat Interface](assets/chat-interface.jpeg)

> Real-time token streaming via Server-Sent Events. Markdown rendering with syntax-highlighted code blocks. Conversation history in sidebar.

### Image Analysis — GPT-4o Vision

![Image Analysis](assets/file-upload.png)

> Upload any image — GPT-4o Vision analyzes it and extracts structured data. Full multi-modal support.

---

## Quick Start

```bash
# Clone
git clone https://github.com/aiagentwithdhruv/conversa-ai.git
cd conversa-ai

# Configure
cp .env.example .env
# Add your OPENAI_API_KEY

# Run
docker-compose up --build
```

```
Frontend  →  http://localhost:3000
API Docs  →  http://localhost:8000/docs
Health    →  http://localhost:8000/health
```

**3 commands. Full-stack AI chat running locally.**

---

## Architecture

```mermaid
graph TB
    subgraph Client["CLIENT"]
        BR["Browser"]
    end

    subgraph AWS["AWS CLOUD"]
        ALB["ALB<br/>Path Routing"]
        subgraph ECS["ECS Fargate"]
            FE["Frontend<br/>Next.js 14<br/>Port 3000"]
            BE["Backend<br/>FastAPI<br/>Port 8000"]
        end
    end

    subgraph Services["SERVICES"]
        AI["OpenAI GPT-4o<br/>Chat + Vision + Streaming"]
        DB["MongoDB Atlas<br/>Conversations + Files"]
        RD["Redis<br/>Rate Limiting + Cache"]
        CW["CloudWatch<br/>Logs + Metrics"]
    end

    BR --> ALB
    ALB -->|"/*"| FE
    ALB -->|"/api/*"| BE
    FE -->|"SSE Stream"| BE
    BE --> AI
    BE --> DB
    BE --> RD
    BE --> CW

    style Client fill:#1e3a5f,stroke:#4a9eed,color:#e5e5e5
    style AWS fill:#1a4d2e,stroke:#22c55e,color:#e5e5e5
    style ECS fill:#1a4d2e,stroke:#22c55e,color:#e5e5e5
    style Services fill:#2d1b69,stroke:#8b5cf6,color:#e5e5e5
```

### Request Flow

```mermaid
graph LR
    subgraph Input["USER INPUT"]
        MSG["Message + File"]
    end

    subgraph Frontend["NEXT.JS"]
        UI["Optimistic UI Update"]
        POST["POST /api/chat/send"]
        SSE["SSE Stream<br/>Render tokens live"]
    end

    subgraph Backend["FASTAPI"]
        RL["Rate Limit Check<br/>Redis"]
        FP["File Processor<br/>PDF · DOCX · XLSX · Image"]
        CTX["Build Context<br/>History + File Content"]
        GPT["Stream GPT-4o<br/>via SSE"]
        SAVE["Store in MongoDB<br/>Auto-title"]
    end

    MSG --> UI --> POST --> RL --> FP --> CTX --> GPT --> SSE
    GPT --> SAVE

    style Input fill:#1e3a5f,stroke:#4a9eed,color:#e5e5e5
    style Frontend fill:#1a4d2e,stroke:#22c55e,color:#e5e5e5
    style Backend fill:#2d1b69,stroke:#8b5cf6,color:#e5e5e5
```

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, react-markdown |
| **Backend** | FastAPI (Python 3.11), OpenAI SDK, Motor (async MongoDB), SSE-Starlette |
| **Database** | MongoDB Atlas (conversations + messages + file metadata) |
| **Cache** | Redis (rate limiting + session cache) |
| **File Processing** | pdfplumber, python-docx, openpyxl, Pillow (base64 for Vision) |
| **AI** | OpenAI GPT-4o (text + vision + streaming) |
| **Infrastructure** | Docker, AWS ECS Fargate, ALB, ECR, ElastiCache, CloudWatch |
| **CI/CD** | GitHub Actions — push to main → build → ECR → ECS (zero-downtime) |
| **Monitoring** | Grafana dashboards, CloudWatch logs + metrics |

---

## API Endpoints

| Method | Path | Description |
|:---|:---|:---|
| `POST` | `/api/chat/send` | Chat + file upload (SSE streaming) |
| `POST` | `/api/chat/send-simple` | Chat without streaming |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/:id` | Get conversation details |
| `GET` | `/api/conversations/:id/messages` | Get messages |
| `PATCH` | `/api/conversations/:id` | Update title |
| `DELETE` | `/api/conversations/:id` | Delete conversation |
| `GET` | `/api/files/:id` | File metadata |
| `GET` | `/api/files/:id/download` | Download file |
| `GET` | `/api/files/:id/text` | Get extracted text |
| `GET` | `/health` | Health check (DB + Redis) |

---

## Deployment

### CI/CD Pipeline

```mermaid
graph LR
    A["git push main"] --> B["GitHub Actions"] --> C["Build Docker"] --> D["Push to ECR"] --> E["Deploy to ECS"] --> F["Live"]

    style A fill:#1e3a5f,stroke:#4a9eed,color:#e5e5e5
    style B fill:#2d1b69,stroke:#8b5cf6,color:#e5e5e5
    style C fill:#2d1b69,stroke:#8b5cf6,color:#e5e5e5
    style D fill:#2d1b69,stroke:#8b5cf6,color:#e5e5e5
    style E fill:#1a4d2e,stroke:#22c55e,color:#e5e5e5
    style F fill:#1a4d2e,stroke:#22c55e,color:#e5e5e5
```

Every push to `main` triggers automatic deployment with zero downtime.

### GitHub Actions Secrets Required

| Secret | Description |
|:---|:---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |

### AWS Infrastructure

| Service | Purpose |
|:---|:---|
| **ECS Fargate** | Serverless container hosting (frontend + backend) |
| **ALB** | Load balancer with path-based routing (`/api/*` → backend, `/*` → frontend) |
| **ECR** | Container image registry |
| **CloudWatch** | Application logs and metrics |
| **ElastiCache** | Managed Redis for rate limiting |
| **MongoDB Atlas** | Managed database (external) |

### Manual Deployment

```bash
# Setup entire AWS infrastructure
chmod +x infrastructure/setup-aws.sh
./infrastructure/setup-aws.sh
```

---

## Project Structure

```
conversa-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + health check
│   │   ├── config.py            # Pydantic settings
│   │   ├── api/
│   │   │   ├── chat.py          # SSE streaming chat endpoint
│   │   │   ├── conversations.py # Conversation CRUD
│   │   │   └── files.py         # File operations
│   │   ├── services/
│   │   │   ├── openai_service.py   # GPT-4o + Vision
│   │   │   ├── file_processor.py   # PDF/DOCX/XLSX/Image
│   │   │   ├── mongo_service.py    # Async MongoDB
│   │   │   └── redis_service.py    # Rate limiting
│   │   └── models/
│   │       └── schemas.py       # Request/response models
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/
│   │   │   ├── Sidebar.tsx      # Conversation list
│   │   │   ├── ChatArea.tsx     # Message display
│   │   │   ├── ChatMessage.tsx  # Markdown + code blocks
│   │   │   ├── ChatInput.tsx    # Auto-resize input
│   │   │   └── FileUpload.tsx   # Drag-and-drop upload
│   │   ├── lib/
│   │   │   └── api.ts           # API client + SSE parser
│   │   └── types/
│   │       └── index.ts         # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
│
├── infrastructure/
│   ├── task-definition.json     # ECS task (2 containers)
│   └── setup-aws.sh            # AWS setup script
│
├── grafana/
│   └── dashboard.json          # Monitoring dashboards
│
├── .github/workflows/
│   └── deploy.yml              # CI/CD pipeline
│
├── docker-compose.yml          # Local dev (4 containers)
└── README.md
```

---

## Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=conversa_ai

# Redis
REDIS_URL=redis://localhost:6379

# App Config
CORS_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_PER_MINUTE=20
MAX_FILE_SIZE_MB=10

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## How This Was Built — The Raw AI Prompts

This entire project — frontend, backend, infrastructure, CI/CD, monitoring — was built in **one session** using [Claude Code](https://claude.ai/code). No boilerplate generators. No tutorials. Just natural language prompts.

Here are the exact prompts used:

### Prompt 1: Build the App

> *"I'm trying to build a particular product where it should behave like ChatGPT. We are going to configure a ChatGPT API key. If my user is going to ask any kind of question, just like ChatGPT, it should try to give an answer out of all the textual conversation, or maybe an image-based conversation, maybe a PDF file-based conversation, word-based conversation, Excel sheet conversation. It should be able to do all kinds of things. It should give me an option to attach a particular file, and then I can go and try to ask any kind of question. I can even download that particular file. My file must be visible inside a chat interface, like a word, PDF, or maybe an image if I'm going to pass, so it should be visible.*
>
> *Now you have to create this particular application by using: Next.js and TypeScript and Tailwind CSS for frontend. Python and FastAPI for backend.*
>
> *You have to store each and every user conversation and whatever file a user is going to upload inside a database, MongoDB. For MongoDB, I am going to use a MongoDB Atlas.*
>
> *I wanted to ship this application to a production environment, so there I wanted to automate each and everything. From a local system, my code should go to a GitHub repository; then GitHub Action is supposed to call AWS. Inside AWS, you have to configure ECR and ECS: ECR for a Docker registry, and then ECS for deployment. Around that you have to implement ElastiCache (Redis) and an Application Load Balancer. In ECR, you are supposed to use ECS Fargate so that I will be able to host my entire backend on serverless.*
>
> *With the help of AWS CLI from my local system, I would like to configure each and everything in a step-by-step manner. Just try to do this configuration for me so that I will be able to build the project, do CI/CD, and eventually by the time I push my codebase, it should build and my feature should be live inside a production environment.*
>
> *I also wanted to implement logging and monitoring. Log each and everything inside CloudWatch. On top of that, I want a Grafana dashboard where I will be able to see all the metrics with respect to application and server."*

**Result:** Claude Code generated the entire codebase — 30+ files, frontend + backend + Docker + CI/CD + Grafana.

### Prompt 2: Set Up AWS & Deploy

> *"Now configure AWS. Create ECR repositories, VPC, subnets, security groups, ECS cluster, ElastiCache. Give me the step-by-step AWS CLI commands."*

**Result:** Generated `infrastructure/setup-aws.sh` — complete AWS setup script (190 lines). Then:

> *"Now push to GitHub and set up the CI/CD."*

**Result:** Created `.github/workflows/deploy.yml`, pushed to GitHub, configured secrets, triggered first deploy. App was live on AWS within minutes.

### Prompt 3: README & Documentation

> *"Create a proper README with Mermaid diagrams, Excalidraw architecture file, and push to GitHub."*

**Result:** This README, 3 Mermaid diagrams, architecture Excalidraw file — all generated and pushed.

### What You Can Learn From This

1. **Describe WHAT you want, not HOW to build it** — Let AI figure out the architecture
2. **Include deployment in the initial prompt** — Don't treat it as an afterthought
3. **Be specific about tech stack** — AI makes better decisions with constraints
4. **Ask for infrastructure as code** — Scripts > clicking through AWS console
5. **One session, full production** — With the right prompt, AI ships complete systems

---

## Euron Bootcamp

This project is a reference implementation for the **Future-Proof AI Automation Bootcamp** at [Euron](https://euron.one).

| Phase | Topic | Conversa AI Coverage |
|:---|:---|:---|
| Phase 4 (Week 9) | RAG + Chatbot | Chat + file processing + context building |
| Phase 5 (Week 11-12) | Docker + Deployment | Docker Compose, ECS Fargate, CI/CD |
| Phase 7 (Week 15-17) | Full-Stack AI Capstone | Complete production app |

---

<div align="center">

### Built by [Dhruv Tomar](https://linkedin.com/in/aiwithdhruv) — @AIwithDhruv

Applied AI Engineer & Solutions Architect | Euron Instructor

**Built and deployed in one session. No tutorials. No copy-paste.**

MIT License

</div>
