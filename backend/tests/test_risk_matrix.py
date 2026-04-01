import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.risk_matrix import RiskMatrixConfig

pytestmark = pytest.mark.asyncio

async def test_get_risk_matrix(client: AsyncClient, test_db: AsyncSession, tenant_factory, user_factory, auth_headers):
    tenant = await tenant_factory()
    user = await user_factory(tenant)
    headers = await auth_headers(user)

    matrix = RiskMatrixConfig(
        tenant_id=tenant.id,
        likelihood_labels=["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"],
        impact_labels=["Negligible", "Minor", "Moderate", "Major", "Severe"],
        thresholds={
            "Low": {"min": 1, "max": 4},
            "Medium": {"min": 5, "max": 9},
            "High": {"min": 10, "max": 16},
            "Critical": {"min": 17, "max": 25}
        }
    )
    test_db.add(matrix)
    await test_db.commit()

    response = await client.get("/api/v1/config/risk-matrix", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["likelihood_labels"]) == 5
    assert data["thresholds"]["Critical"]["min"] == 17

async def test_update_risk_matrix(client: AsyncClient, test_db: AsyncSession, tenant_factory, user_factory, auth_headers):
    tenant = await tenant_factory()
    user = await user_factory(tenant, role="admin")
    headers = await auth_headers(user)

    matrix = RiskMatrixConfig(
        tenant_id=tenant.id,
        likelihood_labels=["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"],
        impact_labels=["Negligible", "Minor", "Moderate", "Major", "Severe"],
        thresholds={
            "Low": {"min": 1, "max": 4},
            "Medium": {"min": 5, "max": 9},
            "High": {"min": 10, "max": 16},
            "Critical": {"min": 17, "max": 25}
        }
    )
    test_db.add(matrix)
    await test_db.commit()

    payload = {
        "likelihood_labels": ["Very Rare", "Unlikely", "Possible", "Likely", "Certain"],
        "impact_labels": ["None", "Low", "Medium", "High", "Critical"],
        "thresholds": {
            "Low": {"min": 1, "max": 5},
            "Medium": {"min": 6, "max": 10},
            "High": {"min": 11, "max": 15},
            "Critical": {"min": 16, "max": 25}
        }
    }

    response = await client.put("/api/v1/config/risk-matrix", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["likelihood_labels"][0] == "Very Rare"
    assert data["impact_labels"][0] == "None"
    assert data["thresholds"]["Low"]["max"] == 5

async def test_update_risk_matrix_invalid(client: AsyncClient, test_db: AsyncSession, tenant_factory, user_factory, auth_headers):
    tenant = await tenant_factory()
    user = await user_factory(tenant, role="admin")
    headers = await auth_headers(user)

    payload = {
        "likelihood_labels": ["Rare", "Unlikely", "Possible", "Likely"], # Only 4
        "impact_labels": ["Negligible", "Minor", "Moderate", "Major", "Severe"],
        "thresholds": {
            "Low": {"min": 1, "max": 4},
            "Medium": {"min": 5, "max": 9},
            "High": {"min": 10, "max": 16},
            "Critical": {"min": 17, "max": 25}
        }
    }

    response = await client.put("/api/v1/config/risk-matrix", json=payload, headers=headers)
    assert response.status_code == 422
