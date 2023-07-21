from sqlalchemy import (
    ARRAY,
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Logbook(Base):
    __tablename__ = "logbook"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)

    records = relationship("Record", back_populates="logbook")


class Record(Base):
    __tablename__ = "record"

    id = Column(Integer, primary_key=True, index=True)
    logbook_id = Column(Integer, ForeignKey("logbook.id"))
    key = Column(String, index=True, nullable=False)
    data = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    meta = Column(JSON, nullable=True)
    created = Column(DateTime, default=func.now())
    last_updated = Column(
        "last_updated", DateTime, default=func.now(), onupdate=func.now()
    )

    logbook = relationship("Logbook", back_populates="records")

    __table_args__ = (UniqueConstraint("logbook_id", "key", created, name="uq_record"),)
