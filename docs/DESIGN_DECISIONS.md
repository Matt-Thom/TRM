# Design Decisions

## DD-001: Row-Level Security over Application-Layer Filtering
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** Multi-tenant data isolation strategy
- **Decision:** Use PostgreSQL RLS policies on every tenant-scoped table
- **Rationale:** RLS is enforced at the database engine level. Even a bug in application code cannot leak data across tenants. This is a compliance requirement for ISO 27001 access control (A.8.3).
- **Alternatives Considered:**
  - Application-layer WHERE clause injection — rejected (bypass risk)
  - Schema-per-tenant — rejected (operational overhead at 50+ tenants)
- **Consequences:** All migrations must include RLS policy definitions. Superadmin/cross-tenant queries require explicit `SET LOCAL app.is_superadmin = true`.

---

## DD-002: UUID Primary Keys over Integer Auto-increment
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** Primary key strategy for all tables
- **Decision:** Use UUID v4 for all primary keys
- **Rationale:** UUIDs prevent enumeration attacks, support distributed ID generation, and are required for cross-tenant operations where integer sequences could collide.
- **Alternatives Considered:**
  - Auto-increment integers — rejected (enumerable, problematic for multi-tenant)
  - ULIDs — considered but UUID is sufficient and has native PostgreSQL support

---

## DD-003: Superadmin Bypass via Session Variable
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** How should superadmin/cross-tenant queries bypass RLS?
- **Decision:** Use `SET LOCAL app.is_superadmin = true` session variable checked by a separate RLS policy
- **Rationale:** `SET LOCAL` is transaction-scoped, automatically reset on commit/rollback. No risk of leaking elevated privileges across requests.
- **Alternatives Considered:**
  - SET ROLE to a superadmin PostgreSQL role — more complex setup
  - Separate connection pool — resource overhead

---

## DD-004: Append-Only Audit Logs via DB Rules
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** How to enforce append-only semantics on audit_logs
- **Decision:** PostgreSQL RULE-based protection (`DO INSTEAD NOTHING` on UPDATE/DELETE)
- **Rationale:** Enforced at the database level, cannot be bypassed by application code. Simpler than trigger-based approaches for a "silently ignore" semantic.
- **Alternatives Considered:**
  - Application guard only — rejected (bypassable)
  - Trigger that raises exception — considered but silent ignore is preferable for robustness

---

## DD-005: Argon2 for Password Hashing
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** Password hashing algorithm selection
- **Decision:** Use Argon2id via argon2-cffi
- **Rationale:** Argon2 is the winner of the Password Hashing Competition, recommended by OWASP. Memory-hard algorithm resists GPU/ASIC attacks.
- **Alternatives Considered:**
  - bcrypt — acceptable but Argon2 is the modern recommendation
  - scrypt — less widely adopted tooling in Python

---

## DD-006: JWT Access + Refresh Token Pattern
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** Session management strategy
- **Decision:** Short-lived access tokens (15min) + long-lived refresh tokens (7 days)
- **Rationale:** Short access token TTL limits exposure window. Refresh tokens allow seamless session extension without re-authentication. Stateless verification scales with multi-instance deployment.
- **Alternatives Considered:**
  - Server-side sessions with Redis — rejected (adds state management complexity)
  - Single long-lived token — rejected (larger exposure window)

## DD-007: Multiplicative Risk Scoring Model
- **Date:** 2026-03-30
- **Status:** Accepted
- **Context:** Quantitative representation of qualitative risk labels
- **Decision:** Use a multiplicative scoring model (`inherent_risk_score` = `likelihood` × `impact`) on a 5x5 matrix
- **Rationale:** A multiplicative approach provides greater separation between critical risks (5x5=25) and low risks (1x1=1) compared to an additive model (5+5=10 vs 1+1=2). It ensures high-likelihood/high-impact risks are mathematically distinct from moderate combinations.
- **Alternatives Considered:**
  - Additive scoring — rejected (insufficient spread, e.g., 1+5 = 5+1 = 3+3 = 6)
  - Custom weighting (e.g., impact weighted higher than likelihood) — rejected (adds unnecessary complexity for MVP; 31000 standard allows equal weighting)
- **Consequences:** The scoring thresholds must cover the range 1-25. The front-end must dynamically calculate and colour-code based on the configured thresholds.
