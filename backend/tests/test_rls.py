"""
Tests for Row-Level Security tenant isolation.

Verifies that RLS policies correctly isolate data between tenants
and that superadmin bypass works.
"""

import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


# These tests require a running PostgreSQL with the migrations applied.
# Mark as integration tests.
pytestmark = pytest.mark.asyncio


TEST_DATABASE_URL = "postgresql+asyncpg://temper:temper@localhost:5432/temper"


@pytest.fixture
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tenant_session(session_factory, tenant_id: str) -> AsyncSession:
    """Create a session scoped to a specific tenant."""
    session = session_factory()
    await session.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'"))
    return session


async def test_user_tenant_roles_isolation(session_factory):
    """Verify user_tenant_roles RLS isolates data between tenants."""
    tenant_a_id = str(uuid.uuid4())
    tenant_b_id = str(uuid.uuid4())
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())

    # Setup: create tenants and users using superadmin session
    async with session_factory() as setup_session:
        await setup_session.execute(text("SET LOCAL app.is_superadmin = true"))

        # Create tenants
        await setup_session.execute(text(
            f"INSERT INTO tenants (id, name, slug) VALUES ('{tenant_a_id}', 'Tenant A', 'tenant-a')"
        ))
        await setup_session.execute(text(
            f"INSERT INTO tenants (id, name, slug) VALUES ('{tenant_b_id}', 'Tenant B', 'tenant-b')"
        ))

        # Create users
        await setup_session.execute(text(
            f"INSERT INTO users (id, email, display_name) VALUES ('{user_a_id}', 'a@test.com', 'User A')"
        ))
        await setup_session.execute(text(
            f"INSERT INTO users (id, email, display_name) VALUES ('{user_b_id}', 'b@test.com', 'User B')"
        ))

        # Assign users to tenants
        await setup_session.execute(text(
            f"INSERT INTO user_tenant_roles (user_id, tenant_id, role) VALUES ('{user_a_id}', '{tenant_a_id}', 'admin')"
        ))
        await setup_session.execute(text(
            f"INSERT INTO user_tenant_roles (user_id, tenant_id, role) VALUES ('{user_b_id}', '{tenant_b_id}', 'admin')"
        ))
        await setup_session.commit()

    # Test: Tenant A session sees only Tenant A's roles
    async with session_factory() as session_a:
        await session_a.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_a_id}'"))
        result = await session_a.execute(text("SELECT * FROM user_tenant_roles"))
        rows = result.fetchall()
        assert len(rows) == 1
        assert str(rows[0].tenant_id) == tenant_a_id

    # Test: Tenant B session sees only Tenant B's roles
    async with session_factory() as session_b:
        await session_b.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_b_id}'"))
        result = await session_b.execute(text("SELECT * FROM user_tenant_roles"))
        rows = result.fetchall()
        assert len(rows) == 1
        assert str(rows[0].tenant_id) == tenant_b_id


async def test_superadmin_sees_all(session_factory):
    """Verify superadmin bypass sees data from all tenants."""
    async with session_factory() as session:
        await session.execute(text("SET LOCAL app.is_superadmin = true"))
        result = await session.execute(text("SELECT * FROM user_tenant_roles"))
        rows = result.fetchall()
        # Should see roles from multiple tenants
        assert len(rows) >= 2
