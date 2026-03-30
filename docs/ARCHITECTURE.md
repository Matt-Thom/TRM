# Architecture

## System Overview

Temper Risk Management (TRM) is a multi-tenant SaaS platform for ISO 31000 / ISO 27001:2022 compliant risk management. It targets MSP client environments with integrations into ConnectWise, Microsoft 365, and CrowdStrike (future).

## Component Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Next.js App   │────▶│  FastAPI Backend │
│   (Frontend)    │     │  (API Server)    │
│   Port 3000     │     │  Port 8000       │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
               ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
               │PostgreSQL│ │  Redis  │ │ Celery  │
               │ (RLS)   │ │ Broker  │ │ Worker  │
               │Port 5432│ │Port 6379│ │         │
               └─────────┘ └─────────┘ └─────────┘
```

## Key Architectural Decisions

- **Multi-tenancy:** PostgreSQL Row-Level Security (RLS) — enforced at DB level, not application
- **Auth:** Local (Argon2 + JWT) + Microsoft Entra ID SSO (single app registration with incremental consent)
- **Task queue:** Celery + Redis for async operations (ConnectWise sync, notifications)
- **Frontend:** Next.js App Router + Zustand for state management + Tailwind CSS
- **Backend:** FastAPI + SQLAlchemy + Alembic + Pydantic
- **Audit:** SQLAlchemy event listeners auto-capture all changes to audit_logs table

## Data Flow

1. All requests carry JWT with `tenant_id` claim
2. Tenant middleware extracts `tenant_id` and sets PostgreSQL session variable
3. RLS policies automatically filter all queries by `tenant_id`
4. SQLAlchemy event listeners capture changes to `audit_logs`
5. Async tasks (ConnectWise sync, notifications) dispatched via Celery/Redis

## Deployment

- **Dev:** Docker Compose (all services local)
- **Production:** Kubernetes on Azure (AKS), Australian data residency enforced via Terraform
