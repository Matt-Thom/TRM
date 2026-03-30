import pytest
"""Tests for risk management."""

import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import Risk, RiskStatus, RiskCategory
from app.models.audit_log import AuditLog

@pytest.fixture
def risk_payload():
    return {
        "title": "Test Risk",
        "description": "A test risk description",
        "threat_source": "External Hacker",
        "vulnerability": "Outdated Software",
        "asset_at_risk": "Web Server",
        "category": "Technological",
        "likelihood": 3,
        "impact": 4,
    }

@pytest.mark.asyncio
async def test_create_risk(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    risk_payload: dict,
):
    response = await client.post("/api/v1/risks", json=risk_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["title"] == risk_payload["title"]
    assert data["inherent_risk_score"] == 12  # 3 * 4

    # Verify in DB
    risk = await db_session.get(Risk, uuid.UUID(data["id"]))
    assert risk is not None

@pytest.mark.asyncio
async def test_get_risk(
    client: AsyncClient,
    auth_headers: dict,
    risk_payload: dict,
):
    # Create
    response = await client.post("/api/v1/risks", json=risk_payload, headers=auth_headers)
    risk_id = response.json()["data"]["id"]

    # Get
    response = await client.get(f"/api/v1/risks/{risk_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == risk_id

@pytest.mark.asyncio
async def test_update_risk(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    risk_payload: dict,
):
    # Create
    response = await client.post("/api/v1/risks", json=risk_payload, headers=auth_headers)
    risk_id = response.json()["data"]["id"]

    # Update
    update_payload = {"title": "Updated Risk", "likelihood": 4}
    response = await client.put(f"/api/v1/risks/{risk_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Updated Risk"
    assert data["inherent_risk_score"] == 16  # 4 * 4

    # Verify in DB
    await db_session.refresh(await db_session.get(Risk, uuid.UUID(risk_id)))
    risk = await db_session.get(Risk, uuid.UUID(risk_id))
    assert risk.title == "Updated Risk"

@pytest.mark.asyncio
async def test_delete_risk(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    risk_payload: dict,
):
    # Create
    response = await client.post("/api/v1/risks", json=risk_payload, headers=auth_headers)
    risk_id = response.json()["data"]["id"]

    # Delete
    response = await client.delete(f"/api/v1/risks/{risk_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify in DB
    risk = await db_session.get(Risk, uuid.UUID(risk_id))
    assert risk is None

@pytest.mark.asyncio
async def test_list_risks_pagination(
    client: AsyncClient,
    auth_headers: dict,
    risk_payload: dict,
):
    # Create 3 risks
    for i in range(3):
        payload = {**risk_payload, "title": f"Risk {i}"}
        await client.post("/api/v1/risks", json=payload, headers=auth_headers)

    # List with limit=2
    response = await client.get("/api/v1/risks?limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 2
    assert data["has_more"] is True
    assert data["next_cursor"] is not None

@pytest.mark.asyncio
async def test_risk_audit_logging(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    risk_payload: dict,
):
    # Create risk
    response = await client.post("/api/v1/risks", json=risk_payload, headers=auth_headers)
    risk_id = response.json()["data"]["id"]

    # Check audit log
    query = select(AuditLog).where(AuditLog.table_name == "risks", AuditLog.record_id == risk_id)
    result = await db_session.execute(query)
    logs = result.scalars().all()

    assert len(logs) == 1
    assert logs[0].action == "INSERT"
