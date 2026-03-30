## Current Phase: Phase 1 — Infrastructure & Scaffolding

### Active Tasks
- [ ] TASK-1.06: Authentication — Microsoft Entra ID SSO
  - **Assigned:** Pending
  - **Blocked by:** TASK-1.05 (done) + manual Azure app registration step
  - **Acceptance Criteria:** SSO flow with auto-provisioning, tenant mapping
  - **Notes:** Requires manual Azure portal step before implementation

### Completed Tasks
- [x] TASK-1.01: Docker Compose stack definition — completed 2026-03-30
  - docker-compose.yml with 5 services (backend, frontend, db, redis, worker)
  - docker-compose.override.yml with hot-reload volume mounts
  - .env.example with all documented env vars
  - backend/Dockerfile and frontend/Dockerfile (dev mode)

- [x] TASK-1.02: PostgreSQL provisioning and base schema — completed 2026-03-30
  - Alembic configuration (alembic.ini, env.py with async support)
  - Initial migration: tenants, users, user_tenant_roles tables
  - TenantBase mixin with tenant_id FK, timestamps
  - UUID primary keys, PostgreSQL role enum type

- [x] TASK-1.03: Row-Level Security implementation — completed 2026-03-30
  - Migration 002: RLS policies on users and user_tenant_roles
  - Tenant isolation via current_setting('app.current_tenant_id')
  - Superadmin bypass via current_setting('app.is_superadmin')
  - Tenant middleware sets request.state.tenant_id
  - db.py with async engine and session factory
  - Dependencies: get_db_session (tenant-scoped), get_superadmin_session
  - tests/test_rls.py for isolation verification

- [x] TASK-1.04: Audit trail implementation — completed 2026-03-30
  - Migration 003: audit_logs table with RLS and append-only rules
  - AuditLog model with JSONB old/new values
  - SQLAlchemy before_flush event listeners (middleware/audit.py)
  - Context variables for request-scoped audit metadata
  - DB rules prevent UPDATE/DELETE on audit_logs
  - tests/test_audit.py

- [x] TASK-1.05: Authentication — Local (Argon2 + JWT) — completed 2026-03-30
  - services/auth.py: Argon2 hashing, JWT creation/decode, user authentication
  - schemas/auth.py: Register, Login, Refresh, Token response schemas
  - routers/auth.py: /register, /login, /refresh endpoints
  - Updated dependencies.py: get_current_user extracts JWT claims
  - Updated main.py: auth router registered
  - Constant-time comparison prevents enumeration attacks

- [x] TASK-1.07: Backend scaffolding — completed 2026-03-30
  - config.py: Pydantic Settings with all env vars
  - main.py: FastAPI app with CORS, exception handlers
  - middleware/request_id.py: UUID per request, X-Request-ID header
  - middleware/tenant.py: Tenant context extraction
  - schemas/responses.py: APIResponse envelope
  - routers/health.py: /api/v1/health with DB/Redis checks
  - Empty package dirs: services, integrations, tasks, utils

- [x] TASK-1.08: Frontend scaffolding — completed 2026-03-30
  - Next.js 15 + React 19 + Tailwind CSS v4 + Zustand 5
  - App Router: layout, login page, dashboard shell
  - stores/auth.ts: Zustand auth state
  - lib/api.ts: Axios client with JWT interceptors
  - types/index.ts: APIResponse envelope, Risk entity types

### Blocked Tasks
- [ ] TASK-1.06: Entra ID OAuth2 flow — blocked by Azure app registration (manual step)

### Next Up: Phase 2
- [x] TASK-2.01: Risk Register — Data Model and API
- [ ] TASK-2.02: Qualitative Scoring Matrix — Configuration API
- [ ] TASK-2.03: Risk Dashboard — Next.js UI
