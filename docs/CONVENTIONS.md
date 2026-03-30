# Conventions

## Code Conventions

| Area | Convention |
| :--- | :--- |
| **Python** | `ruff` for linting and formatting. Type hints on all function signatures. Docstrings on all public functions and classes. |
| **TypeScript** | `eslint` + `prettier`. Strict TypeScript (`strict: true`). No `any` types without a comment explaining why. |
| **SQL/Migrations** | Every migration file includes a descriptive docstring. RLS policies are defined in the same migration as the table they protect. Down migrations must remove RLS policies before dropping tables. |
| **API Endpoints** | RESTful. Plural nouns. Versioned (`/api/v1/`). All responses wrapped in standard envelope: `{ data, meta, errors }`. |
| **Environment Variables** | Prefixed by component: `DB_`, `REDIS_`, `CW_` (ConnectWise), `ENTRA_`, `GRAPH_`, `SMTP_`. |

## Git Conventions

| Rule | Detail |
| :--- | :--- |
| **Branch naming** | `feature/TASK-X.XX-short-description`, `fix/TASK-X.XX-short-description` |
| **Commit messages** | Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:` |
| **Commit frequency** | Commit and push after every meaningful unit of work. |
| **PR scope** | One task per PR. PRs include updated memory files where applicable. |

## Comment Conventions

- All public functions and classes require docstrings
- Inline comments explain "why", not "what"
- TODO comments reference a task ID: `# TODO(TASK-2.03): Add pagination support`

## RLS Migration Template

```python
"""
Migration: Add <table_name> with RLS policies.
"""

def upgrade():
    # Create table
    op.create_table(...)

    # Enable RLS
    op.execute("ALTER TABLE <table_name> ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE <table_name> FORCE ROW LEVEL SECURITY")

    # Create tenant isolation policy
    op.execute("""
        CREATE POLICY tenant_isolation ON <table_name>
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

def downgrade():
    # Remove RLS policies before dropping table
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON <table_name>")
    op.execute("ALTER TABLE <table_name> DISABLE ROW LEVEL SECURITY")
    op.drop_table('<table_name>')
```
