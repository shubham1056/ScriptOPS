# TranscribeOP — Architecture

## High-level

```
┌──────────────────────────────────────────────────────────────────┐
│                  Next.js 15 (App Router)                         │
│        Claude-inspired UI · shadcn · Framer Motion               │
│        Zustand · TanStack Query · Axios · RHF + Zod              │
└───────────────────────────┬──────────────────────────────────────┘
                            │  HTTPS · JWT · SSE
┌───────────────────────────▼──────────────────────────────────────┐
│                       FastAPI (async)                            │
│                                                                  │
│  api/v1  →  middleware  →  services  →  repositories  →  DB      │
│                              │                                   │
│                              ▼                                   │
│                    AI Orchestrator (LangChain)                   │
│            chunker · prompts · formatter · streaming             │
│                              │                                   │
│                              ▼                                   │
│                   Azure OpenAI GPT-5                             │
└──────────────────────────────────────────────────────────────────┘
       │                                              │
       ▼                                              ▼
 PostgreSQL / SQLite                       Local FS / Azure Blob
```

## Clean Architecture layers

| Layer        | Responsibility                                                |
|--------------|---------------------------------------------------------------|
| `api/`       | HTTP transport, request/response models, dependency injection |
| `services/`  | Business logic, orchestration, transactions                   |
| `repositories/` | Pure data access (SQLAlchemy)                              |
| `models/`    | ORM entities                                                  |
| `schemas/`   | Pydantic DTOs (input + output)                                |
| `ai/`        | Prompt orchestration, GPT-5 client, formatters                |
| `core/`      | Config, security, logging, DB, exceptions                     |
| `utils/`     | Pure helpers (file validation, text extraction, sanitization) |

## SOP Generation Flow

1. `POST /api/v1/documents` (multipart) — file persisted, row inserted (`PENDING`).
2. `POST /api/v1/sops/generate` queues a BackgroundTask.
3. Task: extract → sanitize → chunk → per-chunk summarize → orchestrate final SOP prompt → GPT-5.
4. Result formatted into structured `SOPSection[]` and persisted.
5. Client subscribes to `GET /api/v1/sops/{id}/stream` (SSE) for live tokens.

## Pluggable adapters

- **DB:** `DATABASE_URL` (SQLite default, swap to PostgreSQL).
- **Storage:** `STORAGE_BACKEND` = `local` | `azure_blob`.
- **Queue:** `QUEUE_BACKEND` = `background` | `celery`.
