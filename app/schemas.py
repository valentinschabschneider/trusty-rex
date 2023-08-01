from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer
from pydantic.alias_generators import to_camel

from app.utils import camelize_dict_keys


class RecordStateBase(BaseModel):
    data: dict
    tags: Optional[list[str]] = None
    meta: Optional[dict] = None

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class RecordStateCreate(RecordStateBase):
    created: Optional[datetime] = None


class RecordStateUpdate(RecordStateBase):
    last_updated: Optional[datetime] = Field(
        default=None,
        alias="updated",
    )


class RecordState(RecordStateBase):
    id: UUID
    created: datetime
    last_updated: datetime

    class Config:
        from_attributes = True


class RecordStateDiff(RecordState):
    diff_to_previous: dict

    @field_serializer("diff_to_previous")
    def serialize_diff_to_previous(self, diff_to_previous: dict):
        return camelize_dict_keys(diff_to_previous)


class RecordStateAmount(BaseModel):
    key: str
    amount_of_states: int

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class LogbookBase(BaseModel):
    key: str

    class Config:
        alias_generator = to_camel
        populate_by_name = True


class LogbookCreate(LogbookBase):
    pass


class Logbook(LogbookBase):
    class Config:
        from_attributes = True
