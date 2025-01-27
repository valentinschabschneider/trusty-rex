import json
import uuid
from datetime import datetime

from deepdiff import DeepDiff
from pydantic import BaseModel, field_serializer


class RecordStateAmount(BaseModel):
    key: str
    amount_of_states: int


class RecordStateDiff(BaseModel):
    id: uuid.UUID
    key: str
    data: dict | list
    meta: dict
    created_at: datetime
    diff_to_previous: DeepDiff | None
    hash: str

    class Config:
        arbitrary_types_allowed = True
        # json_encoders = {
        #     DeepDiff: lambda v: v.to_json(),
        # }

    @field_serializer("diff_to_previous")
    def serialize_diff(self, diff: DeepDiff):
        if diff is None:
            return None

        return json.loads(diff.to_json())


class PreviewDiff(BaseModel):
    data: dict | list
