import uuid
from datetime import datetime

from sqlmodel import JSON, Field, SQLModel, UniqueConstraint


class LogbookBase(SQLModel):
    key: str = Field(max_length=255, unique=True, index=True)


class Logbook(LogbookBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # record_states: list["RecordState"] = Relationship(
    #     back_populates="logbook", cascade_delete=True
    # )


class RecordStateBase(SQLModel):
    # logbook_id = Column(UUID(as_uuid=True), ForeignKey("logbook.id"))
    data: dict | list = Field(sa_type=JSON)
    meta: dict = Field(default={}, sa_type=JSON)

    class Config:
        arbitrary_types_allowed = True


class RecordStateCreate(RecordStateBase):
    created_at: datetime | None = Field(default=None)


class RecordState(RecordStateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(max_length=255)
    logbook_id: uuid.UUID = Field(foreign_key="logbook.id")
    created_at: datetime = Field(
        default_factory=datetime.now,
    )

    # logbook: Logbook = Relationship(back_populates="record_states")

    __table_args__ = (
        UniqueConstraint("logbook_id", "key", "created_at", name="uq_record_state"),
    )
