# Database Schema

## Tables

### tenants
| Column | Type | Constraints |
| :--- | :--- | :--- |
| id | UUID | PK, default uuid4 |
| name | String | NOT NULL |
| slug | String | UNIQUE, NOT NULL, INDEXED |
| is_active | Boolean | DEFAULT true |
| created_at | DateTime(tz) | DEFAULT now() |
| updated_at | DateTime(tz) | DEFAULT now(), ON UPDATE now() |

**RLS:** None (root entity, not tenant-scoped)

### users
| Column | Type | Constraints |
| :--- | :--- | :--- |
| id | UUID | PK, default uuid4 |
| email | String | UNIQUE, NOT NULL, INDEXED |
| password_hash | String | NULLABLE (SSO users) |
| display_name | String | NOT NULL |
| is_active | Boolean | DEFAULT true |
| created_at | DateTime(tz) | DEFAULT now() |
| updated_at | DateTime(tz) | DEFAULT now(), ON UPDATE now() |

**RLS:** Enabled + Forced. Isolation via subquery into user_tenant_roles.

### user_tenant_roles
| Column | Type | Constraints |
| :--- | :--- | :--- |
| user_id | UUID | FK users.id, PK (composite) |
| tenant_id | UUID | FK tenants.id, PK (composite) |
| role | Enum(admin, manager, viewer) | NOT NULL |

**RLS:** Enabled + Forced. tenant_id = current_setting('app.current_tenant_id')

### audit_logs
| Column | Type | Constraints |
| :--- | :--- | :--- |
| id | UUID | PK, default uuid4 |
| tenant_id | UUID | FK tenants.id, NOT NULL, INDEXED |
| user_id | UUID | FK users.id, NULLABLE |
| table_name | String(255) | NOT NULL, INDEXED |
| record_id | String(255) | NOT NULL |
| action | Enum(INSERT, UPDATE, DELETE) | NOT NULL |
| old_values | JSONB | NULLABLE |
| new_values | JSONB | NULLABLE |
| timestamp | DateTime(tz) | DEFAULT now(), NOT NULL, INDEXED |
| request_id | String(255) | NULLABLE |
| ip_address | String(45) | NULLABLE |

**RLS:** Enabled + Forced. Tenant isolation + superadmin bypass.
**Protection:** Append-only (DB rules block UPDATE and DELETE).

## Enum Types
- `role_enum`: admin, manager, viewer
- `audit_action_enum`: INSERT, UPDATE, DELETE

## RLS Policies (per table)
- `tenant_isolation`: Filters by `current_setting('app.current_tenant_id')::uuid`
- `superadmin_bypass`: Allows access when `current_setting('app.is_superadmin', true)::boolean = true`

## Migrations
1. `001_initial_schema.py` — tenants, users, user_tenant_roles tables
2. `002_add_rls_policies.py` — RLS policies on users, user_tenant_roles
3. `003_add_audit_logs.py` — audit_logs table with RLS and append-only rules

### risks
| Column | Type | Constraints |
| :--- | :--- | :--- |
| id | UUID | PK, default uuid4 |
| tenant_id | UUID | FK tenants.id, NOT NULL, INDEXED |
| title | String(255) | NOT NULL |
| description | Text | NOT NULL |
| threat_source | String(255) | NOT NULL |
| vulnerability | String(255) | NOT NULL |
| asset_at_risk | Text | NOT NULL |
| category | String(50) | NOT NULL |
| status | String(50) | NOT NULL, DEFAULT 'Open' |
| likelihood | Integer | NOT NULL |
| impact | Integer | NOT NULL |
| inherent_risk_score | Integer | NOT NULL |
| risk_owner_id | UUID | FK users.id, NULLABLE |
| created_by | UUID | FK users.id, NOT NULL |
| created_at | DateTime(tz) | DEFAULT now() |
| updated_at | DateTime(tz) | DEFAULT now(), ON UPDATE now() |

**RLS:** Enabled + Forced. Tenant isolation + superadmin bypass.

### risk_matrix_config
| Column | Type | Constraints |
| :--- | :--- | :--- |
| id | UUID | PK, default uuid4 |
| tenant_id | UUID | FK tenants.id, NOT NULL, INDEXED |
| likelihood_labels | JSONB | NOT NULL, DEFAULT '["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"]' |
| impact_labels | JSONB | NOT NULL, DEFAULT '["Negligible", "Minor", "Moderate", "Major", "Severe"]' |
| score_thresholds | JSONB | NOT NULL, DEFAULT '{"Low": 4, "Medium": 9, "High": 16, "Critical": 25}' |
| created_at | DateTime(tz) | DEFAULT now() |
| updated_at | DateTime(tz) | DEFAULT now(), ON UPDATE now() |

**RLS:** Enabled + Forced. Tenant isolation + superadmin bypass.
