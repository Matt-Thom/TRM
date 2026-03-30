## Current Phase: Phase 1 — Infrastructure & Scaffolding

### Active Tasks
- [ ] TASK-1.01: Docker Compose stack definition
  - **Assigned:** Agent
  - **Blocked by:** None
  - **Acceptance Criteria:** `docker compose up` brings up backend, frontend, db, redis, worker without errors
  - **Notes:** Foundation for all other tasks

- [ ] TASK-1.02: PostgreSQL provisioning and base schema
  - **Assigned:** Agent
  - **Blocked by:** TASK-1.01
  - **Acceptance Criteria:** Alembic migrations create tenants, users, user_tenant_roles tables
  - **Notes:** Must include TenantBase mixin with tenant_id FK

- [ ] TASK-1.03: Row-Level Security implementation
  - **Assigned:** Pending
  - **Blocked by:** TASK-1.02
  - **Acceptance Criteria:** RLS ENABLED and FORCED on all tenant-scoped tables; test_rls.py passes
  - **Notes:** Hardest to change retroactively — get this right

- [ ] TASK-1.04: Audit trail implementation
  - **Assigned:** Pending
  - **Blocked by:** TASK-1.03
  - **Acceptance Criteria:** All CRUD operations auto-create audit_logs entries with field-level diffs

- [ ] TASK-1.05: Authentication — Local (Argon2 + JWT)
  - **Assigned:** Pending
  - **Blocked by:** TASK-1.04
  - **Acceptance Criteria:** Register/login endpoints, JWT with tenant_id/role claims, token refresh

- [ ] TASK-1.06: Authentication — Microsoft Entra ID SSO
  - **Assigned:** Pending
  - **Blocked by:** TASK-1.05 + manual Azure step
  - **Acceptance Criteria:** SSO flow with auto-provisioning, tenant mapping

- [ ] TASK-1.07: Backend scaffolding — error handling, middleware, logging
  - **Assigned:** Agent
  - **Blocked by:** None (structural — can parallel with 1.01)
  - **Acceptance Criteria:** Standard error envelope, request ID middleware, structured logging, health check

- [ ] TASK-1.08: Frontend scaffolding — Next.js app shell
  - **Assigned:** Agent
  - **Blocked by:** None (structural — can parallel with 1.01)
  - **Acceptance Criteria:** Next.js App Router, Zustand store, login page shell, API client module

### Completed Tasks
(none yet)

### Blocked Tasks
- [ ] TASK-1.06: Entra ID OAuth2 flow — blocked by Azure app registration (manual step)
