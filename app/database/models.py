import uuid

from sqlalchemy import (
    ARRAY,
    JSON,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Logbook(Base):
    __tablename__ = "logbook"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, index=True)

    record_states = relationship("RecordState", back_populates="logbook")


class RecordState(Base):
    __tablename__ = "record_state"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    logbook_id = Column(UUID(as_uuid=True), ForeignKey("logbook.id"))
    key = Column(String, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    meta = Column(JSON, nullable=True)
    created = Column(DateTime, default=func.now())
    last_updated = Column(
        "last_updated", DateTime, default=func.now(), onupdate=func.now()
    )

    logbook = relationship("Logbook", back_populates="record_states")

    __table_args__ = (
        UniqueConstraint("logbook_id", "key", created, name="uq_record_state"),
        CheckConstraint(
            created <= last_updated, name="ch_record_state_created_before_updated"
        ),
    )
