# Temper Risk Management (TRM) — Detailed Project Plan

## LLM-Driven Development with Design Memory

This project plan is structured for execution by LLM agents (Claude Code CLI, multi-agent workflows) with a design memory system that ensures full context continuity across sessions. Every design decision, schema definition, API contract, and convention is captured in tracked files so that any agent session can resume work without loss of context. Temper Risk Management (TRM) is a product of Subnet.

---

## 1. Design Memory System

The design memory system is a set of living documents stored in the repository root under `/docs/`. These files are the single source of truth for all architectural decisions, conventions, and current state. Every LLM session must read the relevant memory files before beginning work, and must update them before completing a session.

### 1.1 Memory File Structure

```
/docs/
├── ARCHITECTURE.md            # System architecture, component relationships, data flow
├── DESIGN_DECISIONS.md         # Numbered log of every architectural decision with rationale
├── SCHEMA.md                   # Current database schema (tables, columns, types, RLS policies)
├── API_CONTRACTS.md            # Every API endpoint: method, path, request/response schemas
├── CONVENTIONS.md              # Code style, naming, file structure, commit message format
├── TASK_TRACKER.md             # Current phase, active tasks, blocked items, completed work
├── INTEGRATION_NOTES.md        # ConnectWise, Entra ID, Graph API configs, auth flows, scopes
├── TESTING_STRATEGY.md         # Test patterns, fixtures, coverage requirements
├── ENVIRONMENT.md              # Docker Compose config, env vars, local dev setup instructions
├── DATA_RESIDENCY.md           # Region constraints, Terraform policies, future Govt/Defence notes
└── CHANGELOG.md                # Chronological log of what changed and when
```

### 1.2 Memory File Rules

These rules are non-negotiable for every LLM session:

1. **Read before work.** Every session begins by reading `TASK_TRACKER.md` and the memory files relevant to the current task. No code is written until context is loaded.
2. **Write before closing.** Every session ends by updating the memory files that were affected. If a schema changed, `SCHEMA.md` is updated. If a design decision was made, it is appended to `DESIGN_DECISIONS.md` with a number, date, rationale, and alternatives considered.
3. **Single source of truth.** If a memory file and the code disagree, the code is wrong. Memory files are updated first, then code is brought into alignment.
4. **Atomic updates.** Each memory file update is committed separately from code changes with a commit message prefixed `docs:` (e.g., `docs: update SCHEMA.md with audit_logs table`).
5. **No orphaned decisions.** Every non-trivial choice (library selection, schema design, auth flow, error handling pattern) gets a `DESIGN_DECISIONS.md` entry. "Non-trivial" means anything another developer or LLM session would need to understand the "why" behind the code.

### 1.3 DESIGN_DECISIONS.md Format

```markdown
## DD-001: Row-Level Security over Application-Layer Filtering
- **Date:** 2026-04-01
- **Status:** Accepted
- **Context:** Multi-tenant data isolation strategy
- **Decision:** Use PostgreSQL RLS policies on every tenant-scoped table
- **Rationale:** RLS is enforced at the database engine level. Even a bug in
  application code cannot leak data across tenants. This is a compliance
  requirement for ISO 27001 access control (A.8.3).
- **Alternatives Considered:**
  - Application-layer WHERE clause injection — rejected (bypass risk)
  - Schema-per-tenant — rejected (operational overhead at 50+ tenants)
- **Consequences:** All migrations must include RLS policy definitions.
  Superadmin/cross-tenant queries require explicit policy bypass via
  SET ROLE or separate connection.
```

### 1.4 TASK_TRACKER.md Format

```markdown
## Current Phase: Phase 1 — Infrastructure & Scaffolding

### Active Tasks
- [ ] TASK-1.03: Implement RLS policies on tenants, users tables
  - **Assigned:** Session
  - **Blocked by:** None
  - **Acceptance Criteria:** See task detail below
  - **Notes:** Draft policy in SCHEMA.md first, then implement

### Completed Tasks
- [x] TASK-1.01: Docker Compose stack definition — completed 2026-04-01
- [x] TASK-1.02: PostgreSQL provisioning and initial migration — completed 2026-04-02

### Blocked Tasks
- [ ] TASK-1.08: Entra ID OAuth2 flow — blocked by Azure app registration (manual step)
```

---

## 2. Repository Structure

```
temper/
├── docker-compose.yml
├── docker-compose.override.yml      # Local dev overrides (volumes, debug ports)
├── .env.example                     # Template environment variables
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Lint, test, type-check on PR
│       └── deploy.yml               # Production deployment pipeline
├── docs/                            # Design memory system (see Section 1)
├── backend/
│   ├── Dockerfile
│   ├── Dockerfile.worker            # Celery worker image
│   ├── pyproject.toml
│   ├── alembic/
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   └── versions/               # Migration files
│   ├── app/
│   │   ├── main.py                 # FastAPI application factory
│   │   ├── config.py               # Settings via pydantic-settings
│   │   ├── dependencies.py         # Dependency injection (DB sessions, auth, tenant context)
│   │   ├── middleware/
│   │   │   ├── tenant.py           # Tenant context extraction and RLS session config
│   │   │   └── audit.py            # Request-level audit context
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── base.py             # Base model with tenant_id, timestamps
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── risk.py
│   │   │   ├── asset.py
│   │   │   ├── treatment.py
│   │   │   ├── control.py          # ISO 27001 Annex A controls
│   │   │   ├── soa.py              # Statement of Applicability
│   │   │   └── audit_log.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── routers/                # FastAPI route handlers
│   │   ├── services/               # Business logic layer
│   │   ├── integrations/
│   │   │   ├── connectwise/        # CW Manage API client
│   │   │   ├── entra/              # Microsoft Entra ID / MSAL
│   │   │   └── graph/              # Microsoft Graph API (Teams, Email)
│   │   ├── tasks/                  # Celery task definitions
│   │   └── utils/
│   └── tests/
│       ├── conftest.py             # Fixtures: test DB, tenant factory, auth tokens
│       ├── test_rls.py             # Tenant isolation verification
│       ├── test_audit.py           # Audit trail coverage
│       └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/                    # API client, auth helpers
│   │   ├── stores/                 # Zustand state management
│   │   └── types/
│   └── tests/
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── policies/               # Azure Policy definitions (region lock, encryption)
│   │   └── modules/
│   └── k8s/
│       ├── base/                   # Kustomize base manifests
│       └── overlays/
│           ├── staging/
│           └── production/
└── scripts/
    ├── seed_annex_a.py             # Seed ISO 27001:2022 Annex A controls
    ├── seed_risk_matrix.py         # Seed default 5x5 scoring matrix
    └── generate_rtp.py             # Risk Treatment Plan PDF generation
```

---

## 3. Conventions

These are codified in `docs/CONVENTIONS.md` and enforced by CI.

### 3.1 Code Conventions

| Area | Convention |
| :--- | :--- |
| **Python** | `ruff` for linting and formatting. Type hints on all function signatures. Docstrings on all public functions and classes. |
| **TypeScript** | `eslint` + `prettier`. Strict TypeScript (`strict: true`). No `any` types without a comment explaining why. |
| **SQL/Migrations** | Every migration file includes a descriptive docstring. RLS policies are defined in the same migration as the table they protect. Down migrations must remove RLS policies before dropping tables. |
| **API Endpoints** | RESTful. Plural nouns. Versioned (`/api/v1/`). All responses wrapped in a standard envelope: `{ data, meta, errors }`. |
| **Environment Variables** | Prefixed by component: `DB_`, `REDIS_`, `CW_` (ConnectWise), `ENTRA_`, `GRAPH_`, `SMTP_`. |

### 3.2 Git Conventions

| Rule | Detail |
| :--- | :--- |
| **Branch naming** | `feature/TASK-X.XX-short-description`, `fix/TASK-X.XX-short-description` |
| **Commit messages** | Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:` |
| **Commit frequency** | Commit and push after every meaningful unit of work. Never end a session with uncommitted changes. |
| **PR scope** | One task per PR. PRs include updated memory files where applicable. |

### 3.3 Comment Conventions

```python
# All public functions and classes require docstrings.
# Inline comments explain "why", not "what".
# TODO comments reference a task ID: # TODO(TASK-2.03): Add pagination support

def calculate_inherent_risk(likelihood: int, impact: int) -> int:
    """
    Calculate inherent risk score from likelihood and impact ratings.

    Uses multiplicative scoring against the tenant's configured 5x5 matrix.
    See DD-005 for rationale on multiplicative vs additive scoring.

    Args:
        likelihood: Rating from 1 (Rare) to 5 (Almost Certain).
        impact: Rating from 1 (Negligible) to 5 (Severe).

    Returns:
        Inherent risk score (1-25).
    """
    return likelihood * impact
```

---

## 4. Detailed Task Breakdown

Each task includes acceptance criteria specific enough for an LLM agent to verify its own output. Tasks are numbered by phase (`X.XX`).

---

### Phase 1: Infrastructure, Containerization, and Core Scaffolding

#### TASK-1.01: Docker Compose Stack Definition

**Objective:** Define the complete local development environment.

**Deliverables:**
- `docker-compose.yml` with services: `backend`, `frontend`, `db`, `redis`, `worker`
- `docker-compose.override.yml` with volume mounts for hot-reload, debug ports
- `.env.example` with all required environment variables documented

**Acceptance Criteria:**
- `docker compose up` brings up all 5 services without errors
- Backend is accessible at `http://localhost:8000/docs` (Swagger UI)
- Frontend is accessible at `http://localhost:3000`
- PostgreSQL is accessible at `localhost:5432` with credentials from `.env`
- Redis is accessible at `localhost:6379`
- Hot-reload works: changing a `.py` file restarts the backend; changing a `.tsx` file triggers Next.js rebuild

**Memory Updates:** `ENVIRONMENT.md`, `CHANGELOG.md`

---

#### TASK-1.02: PostgreSQL Provisioning and Base Schema

**Objective:** Create the foundational database schema with multi-tenancy support.

**Deliverables:**
- Alembic configuration (`alembic.ini`, `env.py`)
- Initial migration creating: `tenants`, `users`, `user_tenant_roles` tables
- `TenantBase` SQLAlchemy mixin with `tenant_id` FK, `created_at`, `updated_at`

**Acceptance Criteria:**
- `alembic upgrade head` runs cleanly against a fresh database
- `alembic downgrade base` removes all tables cleanly
- `tenants` table: `id (UUID PK)`, `name`, `slug`, `is_active`, `created_at`, `updated_at`
- `users` table: `id (UUID PK)`, `email (unique)`, `password_hash (nullable for SSO)`, `display_name`, `is_active`, `created_at`, `updated_at`
- `user_tenant_roles` table: `user_id`, `tenant_id`, `role (enum: admin, manager, viewer)`, composite PK

**Memory Updates:** `SCHEMA.md`, `DESIGN_DECISIONS.md` (DD on UUID vs integer PKs), `CHANGELOG.md`

---

#### TASK-1.03: Row-Level Security Implementation

**Objective:** Enforce tenant data isolation at the database level.

**Deliverables:**
- RLS policies on all tenant-scoped tables
- SQLAlchemy middleware that sets `app.current_tenant_id` session variable on every request
- Alembic migration pattern for adding RLS to new tables
- Superadmin bypass mechanism for cross-tenant operations

**Acceptance Criteria:**
- PostgreSQL RLS is `ENABLED` and `FORCED` on all tenant-scoped tables
- Every query automatically filters by the session's `current_tenant_id` — no application WHERE clause needed
- A direct SQL query from a session with `tenant_id = A` returns zero rows from `tenant_id = B`, even without a WHERE clause
- Superadmin queries explicitly use `SET ROLE` or a separate connection pool to bypass RLS
- Alembic migration template is documented in `CONVENTIONS.md` showing the RLS pattern
- Test: `test_rls.py` creates 2 tenants, inserts data for each, and verifies isolation under concurrent sessions

**Memory Updates:** `SCHEMA.md`, `DESIGN_DECISIONS.md` (DD on RLS enforcement strategy, superadmin bypass), `CONVENTIONS.md` (migration template), `CHANGELOG.md`

---

#### TASK-1.04: Audit Trail Implementation

**Objective:** Capture a tamper-evident log of every data change, from day one.

**Deliverables:**
- `audit_logs` table
- SQLAlchemy event listeners (`before_update`, `before_insert`, `before_delete`)
- Audit context middleware capturing user ID and request metadata

**Acceptance Criteria:**
- `audit_logs` table: `id`, `tenant_id`, `user_id`, `table_name`, `record_id`, `action (enum: INSERT, UPDATE, DELETE)`, `old_values (JSONB, nullable)`, `new_values (JSONB, nullable)`, `timestamp`, `request_id`, `ip_address`
- Every INSERT, UPDATE, DELETE on any audited table automatically creates an audit log entry
- UPDATE entries capture field-level diffs: only changed fields appear in `old_values` / `new_values`
- Audit logs are append-only: no UPDATE or DELETE operations are permitted on `audit_logs` (enforced by DB trigger or application guard)
- RLS on `audit_logs` ensures tenant isolation of audit data
- Test: `test_audit.py` performs CRUD on a risk, then queries `audit_logs` to verify all operations were captured with correct diffs

**Memory Updates:** `SCHEMA.md`, `DESIGN_DECISIONS.md` (DD on append-only enforcement), `CHANGELOG.md`

---

#### TASK-1.05: Authentication — Local (Argon2 + JWT)

**Objective:** Implement username/password authentication for local development and non-SSO tenants.

**Deliverables:**
- `/api/v1/auth/register` and `/api/v1/auth/login` endpoints
- Argon2 password hashing via `argon2-cffi`
- JWT issuance with `tenant_id` and `role` in claims
- Token refresh mechanism
- FastAPI dependency that extracts and validates the current user from the JWT

**Acceptance Criteria:**
- Registration creates a user and returns a JWT
- Login validates credentials and returns access + refresh tokens
- Invalid credentials return 401 with no information leakage (same error for wrong email vs wrong password)
- JWT contains: `sub (user_id)`, `tenant_id`, `role`, `exp`, `iat`
- Access token TTL: 15 minutes. Refresh token TTL: 7 days (configurable via env)
- The `get_current_user` dependency is usable on any endpoint and injects the authenticated user context
- Test: full auth lifecycle — register, login, access protected endpoint, token expiry, refresh

**Memory Updates:** `API_CONTRACTS.md`, `DESIGN_DECISIONS.md` (DD on token TTLs), `CHANGELOG.md`

---

#### TASK-1.06: Authentication — Microsoft Entra ID SSO

**Objective:** Integrate Microsoft Entra ID as an external identity provider using a single multi-purpose app registration.

**Deliverables:**
- `msal-python` integration with authorization code flow
- `/api/v1/auth/sso/login` and `/api/v1/auth/sso/callback` endpoints
- Automatic user provisioning on first SSO login
- Tenant mapping from Entra ID tenant to application tenant

**Acceptance Criteria:**
- SSO login redirects to Microsoft and returns to callback with auth code
- Successful callback creates/updates local user record and issues application JWT
- If Entra ID user does not exist locally, they are auto-provisioned with `viewer` role
- Entra ID tenant ID is mapped to application tenant ID via a `tenant_sso_mappings` table
- The Azure app registration is configured with initial SSO scopes only (`openid`, `profile`, `email`, `User.Read`). Graph scopes are NOT requested yet.
- App registration details are documented in `INTEGRATION_NOTES.md`

**Prerequisites:** Manual Azure portal step — register app, configure redirect URIs. Document in `INTEGRATION_NOTES.md`.

**Memory Updates:** `SCHEMA.md` (`tenant_sso_mappings`), `API_CONTRACTS.md`, `INTEGRATION_NOTES.md`, `DESIGN_DECISIONS.md` (DD on single app registration with incremental consent), `CHANGELOG.md`

---

#### TASK-1.07: Backend Scaffolding — Error Handling, Middleware, Logging

**Objective:** Establish the cross-cutting concerns that every endpoint relies on.

**Deliverables:**
- Global exception handler with structured error responses
- Request ID middleware (UUID per request, propagated to logs and audit)
- Structured JSON logging (structlog)
- CORS configuration
- Health check endpoint (`/api/v1/health`)

**Acceptance Criteria:**
- All error responses follow the envelope: `{ data: null, meta: { request_id }, errors: [{ code, message, field? }] }`
- Every log line includes `request_id`, `tenant_id`, `user_id` where available
- Health check returns database and Redis connectivity status
- CORS allows frontend origin in dev, configurable for production

**Memory Updates:** `API_CONTRACTS.md` (error envelope, health check), `CONVENTIONS.md` (logging format), `CHANGELOG.md`

---

#### TASK-1.08: Frontend Scaffolding — Auth, Layout, Tenant Context

**Objective:** Establish the frontend application shell with authentication and tenant-aware routing.

**Deliverables:**
- Next.js App Router setup with layout components
- Zustand store for auth state (user, tokens, current tenant)
- Login page (local + SSO)
- Protected route wrapper
- API client module with automatic JWT attachment and refresh
- Tenant selector (for users with access to multiple tenants)

**Acceptance Criteria:**
- Unauthenticated users are redirected to login
- Login page offers both local and SSO authentication
- After login, user lands on the dashboard with their tenant context set
- API client automatically attaches JWT, handles 401 by attempting token refresh, redirects to login on refresh failure
- Tenant selector is visible only for multi-tenant users
- Switching tenants reloads the dashboard with the new tenant's data

**Memory Updates:** `CHANGELOG.md`

---

### Phase 2: Core Risk Management Engine (ISO 31000)

#### TASK-2.01: Risk Register — Data Model and API

**Objective:** Build the complete risk entity lifecycle.

**Deliverables:**
- `risks` table with Alembic migration (including RLS)
- Pydantic schemas for risk creation, update, and response
- CRUD endpoints: `POST /api/v1/risks`, `GET /api/v1/risks`, `GET /api/v1/risks/{id}`, `PUT /api/v1/risks/{id}`, `DELETE /api/v1/risks/{id}`
- List endpoint with filtering, sorting, and cursor-based pagination

**Acceptance Criteria:**
- Risk entity fields: `id (UUID)`, `tenant_id`, `title`, `description`, `threat_source`, `vulnerability`, `asset_at_risk (text, pre-CW integration)`, `category (enum)`, `status (enum: Open, Under Review, Mitigated, Accepted, Closed)`, `likelihood (1-5)`, `impact (1-5)`, `inherent_risk_score (computed)`, `risk_owner_id (FK users, nullable)`, `created_by`, `created_at`, `updated_at`
- RLS policy enforced; verified by test
- Audit log entries created for all CRUD operations; verified by test
- Filtering supports: `status`, `category`, `risk_owner_id`, `min_score`, `max_score`
- Sorting supports: `inherent_risk_score`, `created_at`, `updated_at`
- Pagination returns `meta.next_cursor` and `meta.has_more`

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-2.02: Qualitative Scoring Matrix — Configuration API

**Objective:** Allow tenant admins to configure their risk scoring labels while maintaining a consistent 5x5 grid.

**Deliverables:**
- `risk_matrix_config` table (tenant-scoped)
- Seed script (`scripts/seed_risk_matrix.py`) with ISO 31000 default labels
- Admin endpoints to view and update matrix labels
- Backend logic to compute `inherent_risk_score` from `likelihood × impact`

**Acceptance Criteria:**
- Default matrix is seeded on tenant creation: Likelihood labels (Rare, Unlikely, Possible, Likely, Almost Certain), Impact labels (Negligible, Minor, Moderate, Major, Severe)
- Admin can rename labels but cannot change the 5x5 grid dimensions
- Score thresholds are configurable per tenant: Low (1-4), Medium (5-9), High (10-16), Critical (17-25)
- Changing threshold labels does not retroactively change stored risk scores — scores are computed values, labels are display-only
- `GET /api/v1/config/risk-matrix` returns current matrix with labels and thresholds
- `PUT /api/v1/config/risk-matrix` updates labels/thresholds (admin only)

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `DESIGN_DECISIONS.md` (DD on multiplicative scoring), `CHANGELOG.md`

---

#### TASK-2.03: Risk Dashboard — Next.js UI

**Objective:** Build the primary interface for viewing and managing risks.

**Deliverables:**
- Risk register data table with sorting, filtering, pagination
- Risk creation form (modal or dedicated page)
- Risk detail/edit view
- Risk score heat map colour coding in the table
- Empty state for new tenants

**Acceptance Criteria:**
- Table displays: title, category, status, likelihood, impact, inherent score (colour-coded), owner, last updated
- Filters: status dropdown, category dropdown, score range slider
- Sort: clickable column headers with asc/desc toggle
- Pagination: infinite scroll or page-based with cursor support
- Create form validates all required fields client-side before submission
- Edit form pre-populates all fields, shows change diff on save
- Score cells are colour-coded: green (Low), amber (Medium), orange (High), red (Critical) matching tenant's threshold config

**Memory Updates:** `CHANGELOG.md`

---

### Phase 3: ConnectWise Manage Integration

#### TASK-3.01: Celery and Redis Configuration

**Objective:** Set up the asynchronous task infrastructure.

**Deliverables:**
- Celery application configuration
- `Dockerfile.worker` for the Celery worker container
- Beat schedule for periodic tasks
- Task result backend (Redis)
- Admin endpoint to view task status

**Acceptance Criteria:**
- `docker compose up worker` starts Celery worker connected to Redis
- A test task can be dispatched from the API and executes in the worker
- Beat schedule runs periodic tasks on a configurable cron
- Task failures are logged with full traceback in structured logging
- `GET /api/v1/admin/tasks/{task_id}` returns task state and result

**Memory Updates:** `ENVIRONMENT.md` (Redis/Celery config), `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-3.02: ConnectWise Manage API Client

**Objective:** Build a reusable, well-tested client for the ConnectWise Manage API.

**Deliverables:**
- `app/integrations/connectwise/client.py` — HTTP client with auth, pagination, rate limiting
- `app/integrations/connectwise/models.py` — Pydantic models for CW response types
- Per-tenant CW credential storage (encrypted)

**Acceptance Criteria:**
- Client handles ConnectWise API authentication (API keys per tenant)
- Automatic pagination through all results (CW uses `page` + `pageSize`)
- Rate limiting respects CW's API throttle (configurable delay)
- Retry logic with exponential backoff on 429/5xx responses
- API credentials are stored encrypted in `tenant_integrations` table, not in env vars (per-tenant config)
- Test: mock CW API responses, verify pagination assembly, error handling

**Memory Updates:** `SCHEMA.md` (`tenant_integrations`), `INTEGRATION_NOTES.md` (CW API details), `DESIGN_DECISIONS.md` (DD on per-tenant credential storage), `CHANGELOG.md`

---

#### TASK-3.03: Asset Synchronisation

**Objective:** Periodically sync Configuration Items from ConnectWise into the local database.

**Deliverables:**
- `assets` table with Alembic migration
- Celery task: `sync_connectwise_assets` per tenant
- Sync logic: upsert (create or update), soft-delete assets removed from CW
- Beat schedule for periodic sync (configurable interval, default 6 hours)

**Acceptance Criteria:**
- `assets` table: `id (UUID)`, `tenant_id`, `cw_configuration_id (int, unique per tenant)`, `name`, `type`, `status`, `serial_number`, `eol_date`, `last_synced_at`, `is_deleted`, `raw_data (JSONB)`
- Sync creates new assets, updates changed assets, soft-deletes removed assets
- Sync is idempotent — running twice with no CW changes produces no DB writes
- Sync duration and asset counts are logged
- Failed syncs do not leave partial data — transaction per tenant
- Manual trigger: `POST /api/v1/admin/integrations/connectwise/sync`

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-3.04: Risk-to-Asset Mapping

**Objective:** Allow users to link synced ConnectWise assets to risks.

**Deliverables:**
- `risk_assets` junction table
- Asset search endpoint (for the linking UI)
- Risk detail view updated to show linked assets
- UI for searching and linking/unlinking assets

**Acceptance Criteria:**
- `risk_assets` table: `risk_id`, `asset_id`, composite PK, `linked_at`, `linked_by`
- `GET /api/v1/assets?search=` returns matching assets with type-ahead support
- `POST /api/v1/risks/{id}/assets` links one or more assets
- `DELETE /api/v1/risks/{id}/assets/{asset_id}` unlinks an asset
- Risk detail view shows a list of linked assets with name, type, status, EOL date
- Linking/unlinking creates audit log entries

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `CHANGELOG.md`

---

### Phase 4: Treatment Workflows and Notifications

#### TASK-4.01: Treatment State Machine

**Objective:** Implement the risk treatment workflow engine.

**Deliverables:**
- `treatments` table with state transitions
- State machine logic enforcing valid transitions
- Treatment CRUD endpoints
- Residual risk score calculation

**Acceptance Criteria:**
- `treatments` table: `id (UUID)`, `tenant_id`, `risk_id (FK)`, `title`, `description`, `treatment_type (enum: Mitigate, Transfer, Accept, Avoid)`, `status (enum: Draft, Pending Approval, Approved, In Progress, Completed, Rejected)`, `assigned_to (FK users)`, `due_date`, `existing_controls (text)`, `proposed_controls (text)`, `residual_likelihood (1-5, nullable)`, `residual_impact (1-5, nullable)`, `residual_risk_score (computed, nullable)`, `created_by`, `created_at`, `updated_at`
- Valid state transitions enforced (e.g., cannot go from Draft directly to Completed)
- State transition map documented in `DESIGN_DECISIONS.md`
- Invalid transitions return 422 with explanation
- Residual risk score = `residual_likelihood × residual_impact` (only computed when both are set)
- Audit log captures every state transition with old and new status

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `DESIGN_DECISIONS.md` (DD on state transition map), `CHANGELOG.md`

---

#### TASK-4.02: Microsoft Graph API — Teams Notifications

**Objective:** Send adaptive card notifications to Teams when treatments require approval.

**Deliverables:**
- Incremental consent flow for Graph API scopes on existing Entra ID app
- `app/integrations/graph/teams.py` — Teams message sender
- Adaptive card template for treatment approval requests
- Tenant-level configuration for target Teams channel

**Acceptance Criteria:**
- On treatment status change to "Pending Approval", an adaptive card is sent to the configured Teams channel
- Adaptive card includes: risk title, inherent score, treatment summary, assigned owner, approve/reject action buttons
- Action buttons deep-link back to the treatment in the web UI (not Graph-level approve — approval happens in-app)
- Tenants without a configured Teams channel skip notifications gracefully (log, don't error)
- Graph API scopes are requested via incremental consent, not pre-granted
- Test: mock Graph API, verify card payload structure, verify no-channel-configured handling

**Memory Updates:** `INTEGRATION_NOTES.md` (Graph scopes, Teams config), `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-4.03: SMTP Email Notifications

**Objective:** Email alerts for overdue reviews and critical score changes.

**Deliverables:**
- Email service module with SMTP configuration
- HTML email templates (Jinja2)
- Celery beat task: check for overdue reviews daily
- Event-driven notification on critical risk score change

**Acceptance Criteria:**
- Configurable SMTP settings per tenant (or system-wide fallback)
- Overdue review: if a risk's `updated_at` exceeds the tenant's review period (default 90 days), email the risk owner
- Critical score change: if `inherent_risk_score` crosses into Critical threshold (17+), email tenant admins
- Emails include: risk title, score, owner, direct link to the risk in the web UI
- Failed email sends are logged but do not block other notifications
- Unsubscribe/notification preference support (future — tracked in `TASK_TRACKER.md` as a backlog item)

**Memory Updates:** `ENVIRONMENT.md` (SMTP config), `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-4.04: Treatment UI

**Objective:** Build the frontend for managing risk treatments.

**Deliverables:**
- Treatment list within risk detail view
- Treatment creation form
- Treatment detail/edit view with state transition controls
- Risk owner assignment UI
- Residual risk score display alongside inherent score

**Acceptance Criteria:**
- Risk detail page has a "Treatments" tab showing all treatments for that risk
- Treatment creation form: type, description, existing controls, proposed controls, assigned owner, due date
- State transition buttons only show valid next states (e.g., Draft shows "Submit for Approval")
- Residual likelihood and impact inputs only appear after treatment type is selected
- Side-by-side display of inherent vs residual risk scores with colour coding
- Risk owner is assignable via a user search dropdown (scoped to tenant users)

**Memory Updates:** `CHANGELOG.md`

---

### Phase 5: ISO 27001 Compliance Artifacts and Board Reporting

#### TASK-5.01: Annex A Control Library

**Objective:** Seed the ISO 27001:2022 Annex A controls as reference data.

**Deliverables:**
- `controls` table with Alembic migration
- Seed script (`scripts/seed_annex_a.py`) with all 93 controls
- API endpoint to list controls with filtering by category

**Acceptance Criteria:**
- `controls` table: `id`, `clause_number (e.g., "A.5.1")`, `title`, `description`, `category (enum: Organisational, People, Physical, Technological)`, `is_system_managed (bool, default true)` — system-managed controls are read-only
- All 93 ISO 27001:2022 Annex A controls seeded with correct clause numbers, titles, and categories
- Seed script is idempotent — re-running does not duplicate controls
- `GET /api/v1/controls?category=Technological` returns filtered list

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-5.02: Statement of Applicability (SoA) Builder

**Objective:** Build the interface for evaluating and documenting Annex A control applicability.

**Deliverables:**
- `soa_entries` table linking controls to tenant assessments
- SoA CRUD endpoints
- SoA management UI with bulk actions
- Export to PDF/XLSX

**Acceptance Criteria:**
- `soa_entries` table: `id (UUID)`, `tenant_id`, `control_id (FK)`, `is_applicable (bool)`, `justification (text)`, `implementation_status (enum: Not Started, In Progress, Implemented, Not Applicable)`, `linked_policy_url (text, nullable)`, `linked_risk_ids (UUID[], nullable)`, `assessed_by`, `assessed_at`, `updated_at`
- UI shows all 93 controls grouped by category with applicability toggle, justification text area, and status dropdown
- Bulk action: mark multiple controls as Not Applicable with a shared justification
- Linked risks: ability to search and link risks from the register to each control
- Export: download current SoA as a formatted PDF or XLSX with timestamp and assessed-by metadata
- Progress indicator: "67/93 controls assessed" with per-category breakdown

**Memory Updates:** `SCHEMA.md`, `API_CONTRACTS.md`, `CHANGELOG.md`

---

#### TASK-5.03: Risk Treatment Plan (RTP) Generator

**Objective:** Generate a formal, auditor-ready PDF document from treatment data.

**Deliverables:**
- RTP PDF generation service (ReportLab or headless browser)
- API endpoint to trigger generation and download
- PDF template with Temper/Subnet branding, timestamps, version control

**Acceptance Criteria:**
- RTP PDF includes: cover page (tenant name, generation date, version number), executive summary (total risks, by severity, by status), treatment details table (risk, treatment, owner, due date, status, residual score), appendix (scoring methodology, matrix configuration)
- Timestamped with generation datetime and a monotonically increasing version number per tenant
- PDF stored in tenant-scoped object storage (or local filesystem for dev)
- `POST /api/v1/reports/rtp` generates and returns a download link
- `GET /api/v1/reports/rtp/history` lists previously generated RTPs
- Generated PDFs are audit-logged

**Memory Updates:** `API_CONTRACTS.md`, `DESIGN_DECISIONS.md` (DD on PDF generation approach), `CHANGELOG.md`

---

#### TASK-5.04: Executive Dashboards

**Objective:** Visual reporting for board and management consumption.

**Deliverables:**
- Dashboard page with configurable date ranges
- Risk heat map (5x5 matrix visualisation)
- Risk trend line (score changes over time)
- Status distribution chart
- Top risks table (top 10 by inherent score)

**Acceptance Criteria:**
- Heat map: 5x5 grid with risk counts per cell, colour-coded by severity threshold
- Trend line: line chart showing average inherent risk score over time (weekly data points)
- Status distribution: donut/pie chart showing risk counts by status
- Top risks: table with risk title, score, owner, days since last review
- All charts respond to a global date range filter (default: last 12 months)
- Dashboard data is derived from the risk register and audit logs — no separate analytics tables
- Charts render client-side using Recharts

**Memory Updates:** `CHANGELOG.md`

---

### Phase 6: Production Kubernetes Deployment

#### TASK-6.01: Multi-Stage Dockerfiles

**Objective:** Production-optimised container images.

**Deliverables:**
- `backend/Dockerfile` — multi-stage: builder (install deps) → runtime (slim image)
- `backend/Dockerfile.worker` — same base as backend, different entrypoint
- `frontend/Dockerfile` — multi-stage: builder (npm build) → runtime (nginx or standalone Next.js)
- `.dockerignore` files

**Acceptance Criteria:**
- Backend image < 200MB, frontend image < 150MB
- No dev dependencies, test files, or source maps in production images
- Non-root user in all containers
- Health check instructions in Dockerfiles

**Memory Updates:** `ENVIRONMENT.md`, `CHANGELOG.md`

---

#### TASK-6.02: Terraform — Azure Infrastructure with Data Residency

**Objective:** Codify all Azure infrastructure with enforced Australian data residency.

**Deliverables:**
- Terraform modules for: AKS cluster, Azure Database for PostgreSQL Flexible Server, Azure Cache for Redis, Azure Container Registry, Azure Key Vault, networking (VNet, NSGs)
- Azure Policy: `allowed_locations` restricted to `australiaeast` and `australiasoutheast`
- State backend (Azure Storage Account in `australiaeast`)

**Acceptance Criteria:**
- `terraform plan` shows all resources provisioned in Australian regions only
- Azure Policy assignment prevents any resource creation outside allowed regions — tested by attempting to create a resource in `westus` (should fail)
- PostgreSQL Flexible Server: zone-redundant HA, automated backups, encryption at rest
- AKS: private cluster, managed identity, Azure CNI networking
- Key Vault: stores all secrets (DB credentials, API keys, JWT signing key)
- All modules are parameterised — no hardcoded values

**Memory Updates:** `DATA_RESIDENCY.md`, `ENVIRONMENT.md`, `DESIGN_DECISIONS.md` (DD on region selection, IaC enforcement), `CHANGELOG.md`

---

#### TASK-6.03: Kubernetes Manifests

**Objective:** Define the Kubernetes workloads, networking, and scaling.

**Deliverables:**
- Kustomize base manifests: Deployments (backend, frontend, worker), Services, Ingress, ConfigMaps, Secrets references (External Secrets Operator or Azure Key Vault CSI)
- HPA definitions for backend and frontend
- Staging and production overlays
- cert-manager ClusterIssuer for automated TLS

**Acceptance Criteria:**
- `kustomize build k8s/overlays/production` produces valid manifests
- HPA scales backend pods: min 2, max 10, target 70% CPU
- Ingress routes: `app.domain.com` → frontend, `api.domain.com` → backend
- TLS certificates auto-provisioned via cert-manager + Let's Encrypt
- Secrets pulled from Azure Key Vault, not stored in manifests
- Resource requests and limits defined for all containers
- Pod disruption budgets: at least 1 replica always available

**Memory Updates:** `ENVIRONMENT.md`, `CHANGELOG.md`

---

#### TASK-6.04: CI/CD Pipeline

**Objective:** Automated build, test, and deployment pipeline.

**Deliverables:**
- `.github/workflows/ci.yml` — lint, type-check, test on every PR
- `.github/workflows/deploy.yml` — build images, push to ACR, deploy to AKS on merge to main
- Environment-specific deployment (staging on merge to `develop`, production on merge to `main`)

**Acceptance Criteria:**
- CI runs: `ruff check`, `mypy`, `pytest` (backend); `eslint`, `tsc --noEmit`, `jest` (frontend)
- CI failure blocks merge
- Deploy workflow: build multi-stage images, tag with git SHA, push to ACR, apply Kustomize overlay, rolling update on AKS
- Deployment waits for rollout completion and rolls back on failure
- Slack/Teams notification on deploy success/failure (using existing Graph integration)

**Memory Updates:** `CHANGELOG.md`

---

## 5. LLM Session Protocol

Every LLM development session follows this protocol:

### Session Start

```
1. Read docs/TASK_TRACKER.md — identify the current task
2. Read the memory files listed in the task's "Memory Updates" — load full context
3. Read docs/CONVENTIONS.md — refresh code standards
4. If resuming a partially completed task, read the CHANGELOG.md for the last session's work
```

### During Session

```
1. Write code following CONVENTIONS.md
2. Comment all code per the comment conventions
3. Run tests after every functional change
4. If a design decision is made, draft the DD entry immediately (don't defer to end of session)
```

### Session End

```
1. Run full test suite — ensure nothing is broken
2. Update all affected memory files
3. Update TASK_TRACKER.md — mark completed tasks, note blockers, update active task status
4. Update CHANGELOG.md with a summary of work done
5. Commit all changes with appropriate conventional commit messages
6. Push to GitHub
```

### Session Handoff

If a session cannot complete a task, it must leave a `## Handoff Notes` section in `TASK_TRACKER.md`:

```markdown
## Handoff Notes — TASK-1.03 (Partial)
- **Completed:** RLS policies defined for tenants, users, user_tenant_roles tables
- **Remaining:** RLS policy for audit_logs table, superadmin bypass mechanism
- **Decisions Needed:** Should superadmin bypass use SET ROLE or a separate connection pool? See DD-003 (draft)
- **Files Modified:** backend/alembic/versions/003_rls_policies.py, backend/app/middleware/tenant.py
- **Tests Passing:** Yes (existing tests). New test_rls.py has 2 passing, 1 skipped (pending superadmin bypass)
```

---

## 6. Testing Strategy

### Test Categories

| Category | Tool | When | Coverage Target |
| :--- | :--- | :--- | :--- |
| **Unit** | `pytest` | Every session | All services, utility functions — 80%+ |
| **Integration** | `pytest` + test DB | Every session | API endpoints, DB operations — 70%+ |
| **RLS Isolation** | `pytest` + multi-session | Phase 1, then on schema changes | Every tenant-scoped table — 100% |
| **Audit Trail** | `pytest` | Phase 1, then on new audited tables | Every audited operation — 100% |
| **E2E** | Playwright | Phase 2+, before deployment | Critical user journeys — top 10 flows |
| **API Contract** | Schema validation | CI | All endpoints match `API_CONTRACTS.md` |

### Test Fixtures

Defined in `tests/conftest.py`:

- `test_db` — isolated PostgreSQL database per test session
- `tenant_factory` — creates a tenant with default config (matrix, thresholds)
- `user_factory(tenant)` — creates a user within a tenant
- `auth_headers(user)` — returns JWT auth headers for a user
- `risk_factory(tenant)` — creates a risk with default values within a tenant
- `cw_mock` — mock ConnectWise API responses

### RLS Test Pattern

Every tenant-scoped table must have a test that:

1. Creates Tenant A and Tenant B
2. Creates data for both tenants
3. Queries as Tenant A — verifies only Tenant A data is returned
4. Queries as Tenant B — verifies only Tenant B data is returned
5. Attempts direct SQL without tenant context — verifies zero rows returned (RLS default deny)

---

## 7. Dependency Map

```
TASK-1.01 (Docker Compose)
  └─► TASK-1.02 (PostgreSQL + Base Schema)
       └─► TASK-1.03 (RLS)
            └─► TASK-1.04 (Audit Trail)
                 └─► TASK-1.05 (Auth - Local)
                      ├─► TASK-1.06 (Auth - Entra ID SSO) [+ manual Azure step]
                      └─► TASK-1.07 (Backend Scaffolding)
                           └─► TASK-1.08 (Frontend Scaffolding)
                                └─► TASK-2.01 (Risk Register API + Model)
                                     ├─► TASK-2.02 (Scoring Matrix)
                                     └─► TASK-2.03 (Risk Dashboard UI)
                                          └─► TASK-3.01 (Celery + Redis)
                                               └─► TASK-3.02 (CW API Client)
                                                    └─► TASK-3.03 (Asset Sync)
                                                         └─► TASK-3.04 (Risk-Asset Mapping)
                                                              └─► TASK-4.01 (Treatment State Machine)
                                                                   ├─► TASK-4.02 (Teams Notifications)
                                                                   ├─► TASK-4.03 (Email Notifications)
                                                                   └─► TASK-4.04 (Treatment UI)
                                                                        └─► TASK-5.01 (Annex A Controls)
                                                                             └─► TASK-5.02 (SoA Builder)
                                                                             └─► TASK-5.03 (RTP Generator)
                                                                             └─► TASK-5.04 (Executive Dashboards)

TASK-6.01 through 6.04 can begin in parallel once Phase 2 is stable.
```

---

## 8. Future Considerations (Out of Scope)

These items are tracked for future phases but are explicitly excluded from the current plan:

- **Government / Defence classification support** — ISM PROTECTED data handling, certified Azure regions, additional encryption requirements. The IaC-enforced data residency in Phase 6 is designed to be extensible for this.
- **CrowdStrike integration** — pull vulnerability data from Falcon API into the risk register as threat intelligence.
- **Quantitative risk scoring** — monetary impact modelling alongside the qualitative 5x5 matrix.
- **Multi-language support** — i18n for the frontend (currently English only).
- **Notification preferences** — per-user notification opt-in/opt-out and delivery channel selection.
- **Automated risk identification** — LLM-assisted risk identification from asset and vulnerability data.
