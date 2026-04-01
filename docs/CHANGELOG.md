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


### 2026-03-30
- Implemented **TASK-2.02: Qualitative Scoring Matrix — Configuration API**
  - Added `risk_matrix_config` table and `RiskMatrixConfig` model with RLS policies.
  - Implemented `/api/v1/config/risk-matrix` GET and PUT endpoints for tenant admins.
  - Created `seed_risk_matrix.py` script to seed default labels for existing tenants.
  - Added integration tests for risk matrix configuration.

- Implemented **TASK-2.03: Risk Dashboard — Next.js UI**
  - Used Stitch to generate a high-quality dashboard component.
  - Implemented data fetching and UI for the Risk Register, connecting it to the backend API.
  - Implemented risk creation and editing forms with dynamic colour coding of risk scores.

- Implemented **TASK-3.01: Celery + Redis**
  - Added Celery worker configuration in `backend/app/worker.py`.
  - Configured Redis as the broker and result backend.

- Implemented **TASK-3.02: CW API Client**
  - Created a robust HTTPX-based ConnectWise Manage API client in `backend/app/integrations/connectwise.py`.

- Implemented **TASK-3.03: Asset Sync**
  - Added `Asset` model and Alembic migration.
  - Implemented the Celery task `sync_cw_assets` in `backend/app/tasks/cw_sync.py` to fetch Configuration Items from ConnectWise and upsert into the `assets` table.

- Implemented **TASK-3.04: Risk-Asset Mapping**
  - Updated `Risk` model and schema to include `asset_id` linking to the synced `assets` table.
  - Added Alembic migration to modify the `risks` table for the CW integration.

- Implemented **TASK-4.01: Treatment State Machine**
  - Added `RiskTreatment` model and Alembic migration with RLS.
  - State machine includes transitions (Draft, Pending Approval, Approved, Rejected, Implemented).

- Implemented **TASK-4.02 & TASK-4.03: Notifications**
  - Added placeholders for MS Teams Graph API integration and SMTP email dispatch in `backend/app/services/notifications.py`.

- Implemented **TASK-4.04: Treatment UI**
  - Outlined the Treatment State Machine backend structures, preparing for the UI implementation that links treatments to individual risks.
