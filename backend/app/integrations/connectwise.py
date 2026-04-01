"""ConnectWise Manage API Client."""

import httpx
import base64
import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

class ConnectWiseClient:
    """Client for interacting with the ConnectWise Manage API."""

    def __init__(self):
        self.base_url = settings.CW_BASE_URL.rstrip('/') if settings.CW_BASE_URL else ""
        self.company_id = settings.CW_COMPANY_ID
        self.client_id = settings.CW_CLIENT_ID

        # Build Basic Auth header: CompanyId+PublicKey:PrivateKey
        auth_string = f"{self.company_id}+{settings.CW_PUBLIC_KEY}:{settings.CW_PRIVATE_KEY}"
        b64_auth = base64.b64encode(auth_string.encode()).decode()

        self.headers = {
            "Authorization": f"Basic {b64_auth}",
            "clientId": self.client_id,
            "Accept": "application/vnd.connectwise.com+json; version=2023.1"
        }

    async def get_configurations(self, conditions: str = "", page: int = 1, page_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch Configuration Items (assets) from ConnectWise."""
        if not self.base_url:
            logger.warning("CW_BASE_URL not set. ConnectWise integration is disabled.")
            return []

        url = f"{self.base_url}/v4_6_release/apis/3.0/company/configurations"

        params = {
            "pageSize": page_size,
            "page": page
        }
        if conditions:
            params["conditions"] = conditions

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"ConnectWise API error: {e}")
                return []

    # Synchronous version for Celery tasks
    def get_configurations_sync(self, conditions: str = "", page: int = 1, page_size: int = 100) -> List[Dict[str, Any]]:
        """Synchronous fetch Configuration Items (assets) from ConnectWise."""
        if not self.base_url:
            logger.warning("CW_BASE_URL not set. ConnectWise integration is disabled.")
            return []

        url = f"{self.base_url}/v4_6_release/apis/3.0/company/configurations"

        params = {
            "pageSize": page_size,
            "page": page
        }
        if conditions:
            params["conditions"] = conditions

        with httpx.Client() as client:
            try:
                response = client.get(url, headers=self.headers, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"ConnectWise API error: {e}")
                return []
