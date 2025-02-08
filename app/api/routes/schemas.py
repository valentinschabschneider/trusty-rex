import uuid
from datetime import datetime

from pydantic import BaseModel


class DiffDict(BaseModel):
    values_changed: list = []
    iterable_item_added: list = []
    iterable_item_removed: list = []
    dictionary_item_added: list = []
    dictionary_item_removed: list = []


class RecordStateAmount(BaseModel):
    key: str
    amount_of_states: int


class RecordStateDiff(BaseModel):
    id: uuid.UUID
    key: str
    data: dict | list
    meta: dict
    created_at: datetime
    diff_to_previous: DiffDict | None
    hash: str

    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {
        #     DeepDiff: lambda v: v.to_json(),
        # }

    # @field_serializer("diff_to_previous")
    # def serialize_diff(self, diff: dict):
    #     if diff is None:
    #         return None

    #     return json.loads(diff.to_json())


class PreviewDiff(BaseModel):
    data: dict | list
