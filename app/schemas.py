from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.utils import camelize_diff


class RecordBase(BaseModel):
    key: str
    data: Optional[dict] = None
    tags: Optional[list[str]] = None
    meta: Optional[dict] = None


class RecordCreate(RecordBase):
    pass


class Record(RecordBase):
    created: datetime
    last_updated: datetime = Field(serialization_alias="lastUpdated")

    class Config:
        from_attributes = True


class RecordHistory(Record):
    diff: dict

    @field_serializer("diff")
    def serialize_diff(self, diff: dict):
        return camelize_diff(diff)


class LogbookBase(BaseModel):
    key: str


class LogbookCreate(LogbookBase):
    pass


class Logbook(LogbookBase):
    class Config:
        from_attributes = True
