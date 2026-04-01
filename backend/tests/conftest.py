import asyncio
import os
import uuid
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:////app/trm_dev.db")

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)

    from app.models.tenant import Tenant
    from app.models.user import User
    from app.models.user_tenant_role import UserTenantRole
    from app.models.audit_log import AuditLog
    from app.models.risk import Risk
    from app.models.risk_matrix import RiskMatrixConfig
    from app.models.base import Base

    # We do not use Base.metadata.create_all because it errors out
    # Instead we assume tests are using standard integration mode
    # SQLite does not support JSONB and ENUM properly on generation via create_all

    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def test_db(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def db_session(test_db):
    yield test_db

@pytest.fixture
def client(test_db: AsyncSession):
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from app.main import app
    from app.dependencies import get_db_session

    app.dependency_overrides[get_db_session] = lambda: test_db

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    yield client

@pytest_asyncio.fixture
async def tenant_factory(test_db: AsyncSession):
    from app.models.tenant import Tenant
    async def create_tenant(name="Test Tenant", slug="test-tenant"):
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"
        tenant = Tenant(name=name, slug=slug)
        test_db.add(tenant)
        await test_db.commit()
        await test_db.refresh(tenant)
        return tenant
    return create_tenant

@pytest_asyncio.fixture
async def user_factory(test_db: AsyncSession):
    from app.models.user import User
    from app.models.user_tenant_role import UserTenantRole
    async def create_user(tenant, email="test@example.com", display_name="Test User", role="admin"):
        email = f"{uuid.uuid4().hex[:8]}-{email}"
        user = User(email=email, display_name=display_name)
        test_db.add(user)
        await test_db.flush()
        user_role = UserTenantRole(user_id=user.id, tenant_id=tenant.id, role=role)
        test_db.add(user_role)
        await test_db.commit()
        await test_db.refresh(user)
        return user
    return create_user

@pytest_asyncio.fixture
async def auth_headers():
    async def _get_headers(user) -> Dict[str, str]:
        from app.services.auth import create_access_token
        from app.models.user_tenant_role import UserTenantRole
        from sqlalchemy.future import select
        from app.dependencies import get_db_session

        engine = create_async_engine(TEST_DATABASE_URL)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as db:
            result = await db.execute(select(UserTenantRole).where(UserTenantRole.user_id == user.id))
            role = result.scalars().first()

        token = create_access_token(user_id=user.id, tenant_id=role.tenant_id, role=role.role)
        return {"Authorization": f"Bearer {token}"}
    return _get_headers
