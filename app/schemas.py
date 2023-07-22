from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils import camelize_dict_keys


class RecordStateBase(BaseModel):
    data: dict
    tags: Optional[list[str]] = None
    meta: Optional[dict] = None


class RecordStateCreate(RecordStateBase):
    pass


class RecordStateUpdate(RecordStateBase):
    pass


class RecordState(RecordStateBase):
    id: UUID
    created: datetime
    last_updated: datetime = Field(serialization_alias="lastUpdated")

    class Config:
        from_attributes = True


class RecordStateDiff(RecordState):
    diff_to_previous: dict = Field(serialization_alias="diffToPrevious")

    @field_serializer("diff_to_previous")
    def serialize_diff_to_previous(self, diff_to_previous: dict):
        return camelize_dict_keys(diff_to_previous)


class LogbookBase(BaseModel):
    key: str


class LogbookCreate(LogbookBase):
    pass


class Logbook(LogbookBase):
    class Config:
        from_attributes = True
