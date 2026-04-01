"""Notification services for TRM."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def send_teams_notification(channel_id: str, card_payload: Dict[str, Any]) -> bool:
    """
    Dispatch an actionable adaptive card to a Microsoft Teams channel via Graph API.
    Placeholder for TASK-4.02 implementation.
    """
    logger.info(f"Sending Teams notification to {channel_id}...")
    # Requires MS Graph API Client with ChannelMessage.Send scope
    logger.debug(f"Payload: {card_payload}")
    return True

async def send_email_notification(to_email: str, subject: str, body_html: str) -> bool:
    """
    Dispatch an email notification via SMTP.
    Placeholder for TASK-4.03 implementation.
    """
    logger.info(f"Sending Email notification to {to_email}...")
    # Requires SMTP client implementation
    return True
