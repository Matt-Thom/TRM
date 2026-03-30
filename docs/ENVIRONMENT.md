# Environment

## Local Development

Docker Compose stack with 5 services: backend, frontend, db, redis, worker.

### Services

| Service | Image | Port | Notes |
| :--- | :--- | :--- | :--- |
| backend | FastAPI (uvicorn) | 8000 | Swagger UI at /docs |
| frontend | Next.js | 3000 | Hot reload enabled |
| db | PostgreSQL 16 | 5432 | RLS enabled |
| redis | Redis 7 | 6379 | Celery broker + result backend |
| worker | Celery | — | Same image as backend, different entrypoint |

### Environment Variables

See `.env.example` for all required variables. Prefixes:
- `DB_` — Database connection
- `REDIS_` — Redis connection
- `CW_` — ConnectWise API
- `ENTRA_` — Microsoft Entra ID
- `GRAPH_` — Microsoft Graph API
- `SMTP_` — Email configuration

## Production

Azure Kubernetes Service (AKS) in Australia East region. See DATA_RESIDENCY.md.
