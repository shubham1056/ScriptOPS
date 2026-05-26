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
- Git
- (optional) PostgreSQL 16, Redis 7

### 1. Clone

```bash
git clone https://github.com/shubham1056/ScriptOPS.git
cd ScriptOPS
```

### 2. Backend (FastAPI)

**Windows:**
```cmd
cd apps\api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**macOS / Linux:**
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then **edit `apps/api/.env`** and set the required values:

```dotenv
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
JWT_SECRET_KEY=<paste-generated-secret>

# Single-account portal credentials (the API auto-seeds this user on startup)
PORTAL_USER_EMAIL=userc2i@ust.com
PORTAL_USER_PASSWORD=Userc2i@qwertyuiop
PORTAL_USER_NAME=C2I Portal

# Azure OpenAI — get these from the team lead
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=
```

Run the API:
```bash
uvicorn app.main:app --reload --port 4000
```

API → **http://localhost:4000** · Docs → **http://localhost:4000/docs**

### 3. Frontend (Next.js) — in a new terminal

**Windows:**
```cmd
cd apps\web
npm install
copy .env.example .env.local
npm run dev
```

**macOS / Linux:**
```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

App → **http://localhost:3000**

### 4. Sign in

Open http://localhost:3000/login and use the portal credentials from your `.env`:

- **Email:** `userc2i@ust.com`
- **Password:** `Userc2i@qwertyuiop`

> The portal is locked to a single provisioned account by design. There is no self-service registration. On every API startup, the user from `PORTAL_USER_EMAIL` / `PORTAL_USER_PASSWORD` is upserted as `ADMIN` and any other accounts in the `users` table are purged. To rotate the credential, change `.env` and restart the API.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `Port 3000 / 4000 already in use` | Kill the existing process (`taskkill /F /IM node.exe` on Windows, `lsof -ti:4000 \| xargs kill` on macOS/Linux) and retry. |
| Startup error: `PORTAL_USER_EMAIL and PORTAL_USER_PASSWORD must be set` | Fill those values in `apps/api/.env`. |
| Login returns `401 Invalid email or password` | Your `.env` values don't match what you typed. Update `.env` and restart the API so the seeder re-runs. |
| `pydantic_settings ValidationError: JWT_SECRET_KEY` | The secret must be at least 32 chars — regenerate with the `secrets.token_urlsafe(48)` command above. |

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
