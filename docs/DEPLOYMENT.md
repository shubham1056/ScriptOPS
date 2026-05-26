# Deployment Guide

## Local development (no Docker)

See [README](../README.md) Quick Start.

## Production (recommended)

1. **Database** — provision PostgreSQL 16, set `DATABASE_URL=postgresql+asyncpg://...`
2. **Storage** — provision Azure Blob, set `STORAGE_BACKEND=azure_blob` and `AZURE_STORAGE_*`.
3. **Queue** — provision Redis, set `QUEUE_BACKEND=celery` and `REDIS_URL`, run `celery -A app.workers.celery_app worker`.
4. **Backend** — `gunicorn -k uvicorn.workers.UvicornWorker app.main:app -w 4 -b 0.0.0.0:4000`
5. **Frontend** — `npm run build && npm start` (Next.js 15 standalone).
6. **Reverse proxy** — NGINX terminating TLS, forwarding `/api` to backend, `/` to frontend.

## Migrations

```cmd
cd apps\api
alembic revision --autogenerate -m "your message"
alembic upgrade head
```
