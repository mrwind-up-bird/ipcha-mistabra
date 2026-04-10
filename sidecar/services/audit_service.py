from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from ipcha.audit.models import Finding, RejectionLog, RejectionReason

class AuditServiceError(Exception):
    """Custom exception for audit service failures."""
    pass

def log_rejection(
    db_session: Session,
    *,
    finding_id: int,
    tenant_id: str,
    rejection_source: str,
    reason_code: RejectionReason,
    justification: str | None = None,
) -> RejectionLog:
    """
    Logs a rejection event and updates the finding status atomically.

    This function ensures that creating the rejection log and updating the
    associated finding's status to 'REJECTED' either both succeed or both
    fail.

    Args:
        db_session: The SQLAlchemy session for database operations.
        finding_id: The ID of the finding being rejected.
        tenant_id: The tenant ID for data isolation.
        rejection_source: The module or service that triggered the rejection.
        reason_code: The structured reason for the rejection.
        justification: Optional free-text explanation for the rejection.

    Returns:
        The created RejectionLog instance.

    Raises:
        AuditServiceError: If the finding is not found or if a database
                           error occurs.
    """
    try:
        # Use a nested transaction to ensure atomicity. The session should
        # be managed by a context manager at the application's entry point.
        with db_session.begin_nested():
            # 1. Fetch the finding and lock the row for update
            finding_to_reject = (
                db_session.query(Finding)
                .filter_by(id=finding_id, tenant_id=tenant_id)
                .with_for_update()
                .one_or_none()
            )

            if not finding_to_reject:
                raise AuditServiceError(f"Finding with ID {finding_id} not found for tenant {tenant_id}.")

            # 2. Update the finding's status
            finding_to_reject.status = "REJECTED"

            # 3. Create the new rejection log entry
            new_log_entry = RejectionLog(
                finding_id=finding_id,
                tenant_id=tenant_id,
                rejection_source=rejection_source,
                reason_code=reason_code,
                justification=justification,
            )
            db_session.add(new_log_entry)

        # The transaction is committed here upon exiting the 'with' block
        # successfully. We need to refresh the object to get relationships.
        db_session.refresh(new_log_entry)
        return new_log_entry

    except SQLAlchemyError as e:
        # The transaction is automatically rolled back by the context manager
        # on exception.
        raise AuditServiceError(f"Database error during rejection logging: {e}") from e
