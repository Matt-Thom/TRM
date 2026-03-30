"""Add Row-Level Security policies to tenant-scoped tables."""

revision = "002"
down_revision = "001"

from alembic import op


def upgrade():
    # Users table - RLS based on user_tenant_roles membership
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE users FORCE ROW LEVEL SECURITY")

    # user_tenant_roles - direct tenant_id column
    op.execute("ALTER TABLE user_tenant_roles ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE user_tenant_roles FORCE ROW LEVEL SECURITY")

    # Tenant isolation policies for user_tenant_roles
    op.execute("""
        CREATE POLICY tenant_isolation ON user_tenant_roles
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
    """)

    # Superadmin bypass for user_tenant_roles
    op.execute("""
        CREATE POLICY superadmin_bypass ON user_tenant_roles
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)

    # Users - RLS policy based on membership in the current tenant
    op.execute("""
        CREATE POLICY tenant_isolation ON users
        USING (
            id IN (
                SELECT user_id FROM user_tenant_roles
                WHERE tenant_id = current_setting('app.current_tenant_id')::uuid
            )
        )
    """)

    # Superadmin bypass for users
    op.execute("""
        CREATE POLICY superadmin_bypass ON users
        USING (current_setting('app.is_superadmin', true)::boolean = true)
    """)


def downgrade():
    for table in ["users", "user_tenant_roles"]:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"DROP POLICY IF EXISTS superadmin_bypass ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
