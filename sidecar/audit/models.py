import enum
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Placeholder model to demonstrate transactional updates.
# Assumes this model is defined elsewhere in the project.
class Finding(Base):
    __tablename__ = 'findings'
    id = Column(Integer, primary_key=True)
    status = Column(String(50), nullable=False, default='PENDING')
    tenant_id = Column(String(36), nullable=False)
    rejection_logs = relationship("RejectionLog", back_populates="finding")


class RejectionReason(enum.Enum):
    """Structured reason codes for why a finding was rejected."""
    INSUFFICIENT_CONFIDENCE = "INSUFFICIENT_CONFIDENCE"
    INPUT_SANITIZE_FAILURE = "INPUT_SANITIZE_FAILURE"
    COHERENCE_VALIDATION_FAIL = "COHERENCE_VALIDATION_FAIL"
    MALFORMED_INPUT = "MALFORMED_INPUT"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    UNKNOWN = "UNKNOWN"


class RejectionLog(Base):
    """Represents an audit trail entry for a rejected finding."""
    __tablename__ = 'rejection_logs'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finding_id = Column(Integer, ForeignKey('findings.id'), nullable=False)
    rejection_source = Column(String(100), nullable=False)
    reason_code = Column(Enum(RejectionReason), nullable=False)
    justification = Column(String(500), nullable=True)
    tenant_id = Column(String(36), nullable=False)

    finding = relationship("Finding", back_populates="rejection_logs")

    __table_args__ = (
        Index('ix_rejection_logs_tenant_id_created_at', 'tenant_id', 'created_at'),
    )

    def __repr__(self):
        return (
            f"<RejectionLog(id={self.id}, finding_id={self.finding_id}, "
            f"reason='{self.reason_code.value}')>"
        )
