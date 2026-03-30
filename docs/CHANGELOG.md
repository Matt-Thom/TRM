# Changelog

## 2026-03-30

### Session: Initial Setup & Phase 1 Scaffolding
- Created design memory system (`/docs/` directory) with all memory files
- TASK-1.01: Docker Compose stack definition (backend, frontend, db, redis, worker)
- TASK-1.02: PostgreSQL provisioning, base schema (tenants, users, user_tenant_roles), Alembic setup
- TASK-1.03: Row-Level Security policies on tenant-scoped tables with superadmin bypass
- TASK-1.04: Audit trail with SQLAlchemy event listeners and append-only DB protection
- TASK-1.05: Local authentication (Argon2 password hashing + JWT issuance)
- TASK-1.07: Backend scaffolding (config, middleware, error handling, health check, structured logging)
- TASK-1.08: Frontend scaffolding (Next.js App Router, Zustand auth store, login page, API client)

### Remaining Phase 1
- TASK-1.06: Entra ID SSO — blocked by manual Azure app registration

### 2026-03-30
- Completed TASK-2.01: Risk Register — Data Model and API. Created `Risk` model with RLS policies, schemas, and router with CRUD endpoints. Added cursor pagination for list endpoint. Update `main.py` to use new router. Included comprehensive tests and `SCHEMA.md` updates.
