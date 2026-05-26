# TranscribeOP

> **AI-Powered SOP Intelligence Platform**
> Transform transcripts, KT sessions, and operational discussions into structured enterprise-grade Standard Operating Procedures using Azure OpenAI GPT-5.

![python](https://img.shields.io/badge/python-3.12-blue) ![next.js](https://img.shields.io/badge/next.js-15-black) ![fastapi](https://img.shields.io/badge/fastapi-0.115-009688) ![license](https://img.shields.io/badge/license-Proprietary-lightgrey)

---

## ✨ Overview

**TranscribeOP** converts unstructured knowledge — meeting transcripts, KT recordings, walk-throughs, and operational documents — into polished, audit-ready **Standard Operating Procedures (SOPs)**.

- **Frontend** — Next.js 15, React 19, TypeScript, Tailwind, shadcn/ui, Framer Motion (Claude-inspired design language).
- **Backend** — FastAPI (async), SQLAlchemy 2, Pydantic v2, Clean Architecture.
- **AI** — Azure OpenAI GPT-5 with LangChain orchestration, tiktoken-aware chunking, streaming SSE.
- **Storage** — Pluggable: local filesystem (dev) / Azure Blob Storage (prod).
- **DB** — Pluggable: SQLite (dev) / PostgreSQL (prod) via SQLAlchemy URL.
- **Async** — FastAPI BackgroundTasks (dev) / Celery+Redis (prod, optional).

---

## 🚀 Quick Start (no Docker)

### Prerequisites

- Node.js 20+
- Python 3.12+
- (optional) PostgreSQL 16, Redis 7

### Backend

```cmd
cd apps\api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
:: edit .env and set AZURE_OPENAI_* values
alembic upgrade head
uvicorn app.main:app --reload --port 4000
```

API docs → **http://localhost:4000/docs**

### Frontend

```cmd
cd apps\web
npm install
copy .env.example .env.local
npm run dev
```

App → **http://localhost:3000**

---

## 🧠 AI Pipeline

```
Upload  →  Extract (PDF / DOCX / TXT)  →  Sanitize  →  Chunk (tiktoken)
   →  Summarize per chunk  →  Prompt Orchestrator  →  Azure OpenAI GPT-5
   →  SOP Formatter (Pydantic)  →  Persist  →  Stream (SSE)
```

## 🔐 Security

- JWT access + refresh tokens, RBAC scaffolding (USER / EDITOR / ADMIN)
- CORS, throttling (slowapi), security headers
- Pydantic v2 validation, prompt sanitization
- File MIME + magic-byte validation
- Structured audit logging

## 📁 Monorepo

```
TranscribeOP/
├── apps/
│   ├── web/    # Next.js 15 frontend
│   └── api/    # FastAPI backend
└── docs/       # Architecture & deployment
```

## 📝 License
Proprietary — © 2026 TranscribeOP.
