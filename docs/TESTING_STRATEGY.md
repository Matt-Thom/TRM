# Testing Strategy

## Test Categories

| Category | Tool | When | Coverage Target |
| :--- | :--- | :--- | :--- |
| **Unit** | `pytest` | Every session | All services, utility functions — 80%+ |
| **Integration** | `pytest` + test DB | Every session | API endpoints, DB operations — 70%+ |
| **RLS Isolation** | `pytest` + multi-session | Phase 1, then on schema changes | Every tenant-scoped table — 100% |
| **Audit Trail** | `pytest` | Phase 1, then on new audited tables | Every audited operation — 100% |
| **E2E** | Playwright | Phase 2+, before deployment | Critical user journeys — top 10 flows |
| **API Contract** | Schema validation | CI | All endpoints match API_CONTRACTS.md |

## Test Fixtures (tests/conftest.py)

- `test_db` — isolated PostgreSQL database per test session
- `tenant_factory` — creates a tenant with default config
- `user_factory(tenant)` — creates a user within a tenant
- `auth_headers(user)` — returns JWT auth headers for a user
- `risk_factory(tenant)` — creates a risk with default values
- `cw_mock` — mock ConnectWise API responses

## RLS Test Pattern

Every tenant-scoped table must have a test that:
1. Creates Tenant A and Tenant B
2. Creates data for both tenants
3. Queries as Tenant A — verifies only Tenant A data returned
4. Queries as Tenant B — verifies only Tenant B data returned
5. Attempts direct SQL without tenant context — verifies zero rows (RLS default deny)
