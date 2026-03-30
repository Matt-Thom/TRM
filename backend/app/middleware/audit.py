"""
Audit trail middleware using SQLAlchemy event listeners.

Automatically captures INSERT, UPDATE, and DELETE operations on all
audited models and writes entries to the audit_logs table.
"""

import enum
import json
import uuid
import logging
import sqlalchemy as sa
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Context variables for request-scoped audit metadata
audit_user_id: ContextVar[str | None] = ContextVar("audit_user_id", default=None)
audit_tenant_id: ContextVar[str | None] = ContextVar("audit_tenant_id", default=None)
audit_request_id: ContextVar[str | None] = ContextVar("audit_request_id", default=None)
audit_ip_address: ContextVar[str | None] = ContextVar("audit_ip_address", default=None)


# Tables to skip auditing
SKIP_TABLES = {"audit_logs"}


def get_model_changes(instance) -> dict[str, tuple[Any, Any]]:
    """
    Get changed fields for an instance as {field: (old_value, new_value)}.

    Only returns fields that actually changed.
    """
    changes = {}
    insp = inspect(instance)

    for attr in insp.attrs:
        hist = attr.history
        if hist.has_changes():
            old = hist.deleted[0] if hist.deleted else None
            new = hist.added[0] if hist.added else None
            # Convert UUIDs and datetimes to strings for JSON serialization
            if isinstance(old, uuid.UUID):
                old = str(old)
            if isinstance(new, uuid.UUID):
                new = str(new)
            if isinstance(old, datetime):
                old = old.isoformat()
            if isinstance(new, datetime):
                new = new.isoformat()
            changes[attr.key] = (old, new)

    return changes


def instance_to_dict(instance) -> dict[str, Any]:
    """Convert a model instance to a serializable dict."""
    result = {}
    insp = inspect(instance)
    for attr in insp.attrs:
        value = attr.loaded_value
        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        result[attr.key] = value
    return result


def _create_audit_entry(session: Session, table_name: str, record_id: str,
                        action: str, old_values: dict | None, new_values: dict | None):
    """Insert an audit log entry using raw SQL to avoid recursive triggers."""
    tenant_id = audit_tenant_id.get()
    if not tenant_id:
        logger.warning(f"No tenant_id in audit context for {action} on {table_name}")
        return

    session.execute(
        sa.text("""
            INSERT INTO audit_logs (id, tenant_id, user_id, table_name, record_id, action, old_values, new_values, timestamp, request_id, ip_address)
            VALUES (:id, :tenant_id, :user_id, :table_name, :record_id, :action, :old_values, :new_values, :timestamp, :request_id, :ip_address)
        """),
        {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "user_id": audit_user_id.get(),
            "table_name": table_name,
            "record_id": record_id,
            "action": action,
            "old_values": json.dumps(old_values) if old_values else None,
            "new_values": json.dumps(new_values) if new_values else None,
            "timestamp": datetime.now(timezone.utc),
            "request_id": audit_request_id.get(),
            "ip_address": audit_ip_address.get(),
        },
    )


def setup_audit_listeners(session_class):
    """
    Register SQLAlchemy event listeners for audit logging.

    Call this once at application startup with the Session class.
    """

    @event.listens_for(session_class, "before_flush")
    def before_flush(session, flush_context, instances):
        # Process new objects (INSERT)
        for instance in session.new:
            table_name = instance.__class__.__tablename__
            if table_name in SKIP_TABLES:
                continue

            new_values = instance_to_dict(instance)
            record_id = str(getattr(instance, "id", "unknown"))
            _create_audit_entry(session, table_name, record_id, "INSERT", None, new_values)

        # Process modified objects (UPDATE)
        for instance in session.dirty:
            if not session.is_modified(instance):
                continue
            table_name = instance.__class__.__tablename__
            if table_name in SKIP_TABLES:
                continue

            changes = get_model_changes(instance)
            if not changes:
                continue

            old_values = {k: v[0] for k, v in changes.items()}
            new_values = {k: v[1] for k, v in changes.items()}
            record_id = str(getattr(instance, "id", "unknown"))
            _create_audit_entry(session, table_name, record_id, "UPDATE", old_values, new_values)

        # Process deleted objects (DELETE)
        for instance in session.deleted:
            table_name = instance.__class__.__tablename__
            if table_name in SKIP_TABLES:
                continue

            old_values = instance_to_dict(instance)
            record_id = str(getattr(instance, "id", "unknown"))
            _create_audit_entry(session, table_name, record_id, "DELETE", old_values, None)
