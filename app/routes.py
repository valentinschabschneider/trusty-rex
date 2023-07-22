from datetime import datetime
from uuid import UUID

from deepdiff import DeepDiff
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from fastapi.security.api_key import APIKey
from sqlalchemy.orm import Session

import app.auth as auth
import app.database.crud as crud
from app import dependencies
from app.schemas import Logbook as LogbookSchema
from app.schemas import LogbookCreate as LogbookCreateSchema
from app.schemas import RecordState as RecordSchema
from app.schemas import RecordStateCreate as RecordCreateSchema
from app.schemas import RecordStateDiff as RecordStateDiffSchema
from app.schemas import RecordStateUpdate

router = APIRouter()


@router.post("/logbooks", response_model=LogbookSchema)
async def create_logbook(
    logbook: LogbookCreateSchema,
    db: Session = Depends(dependencies.get_db),
    api_key: APIKey = Depends(auth.get_api_key),
):
    return crud.create_logbook(db, logbook)


@router.get("/logbooks", response_model=list[LogbookSchema])
async def get_logbooks(
    db: Session = Depends(dependencies.get_db),
    api_key: APIKey = Depends(auth.get_api_key),
):
    return crud.find_all_logbooks(db)


@router.post(
    "/logbooks/{logbook_key}/records/{record_key}/states", response_model=RecordSchema
)
async def create_record_state(
    logbook_key: str,
    record_key: str,
    new_record_state: RecordCreateSchema,
    db: Session = Depends(dependencies.get_db),
    api_key: APIKey = Depends(auth.get_api_key),
):
    return crud.create_record_state(db, logbook_key, record_key, new_record_state)


@router.get(
    "/logbooks/{logbook_key}/records/{record_key}/states",
    response_model=list[RecordStateDiffSchema],
)
async def get_record_states(
    logbook_key: str,
    record_key: str,
    db: Session = Depends(dependencies.get_db),
    api_key: APIKey = Depends(auth.get_api_key),
):
    record_states = crud.find_record_states(db, logbook_key, record_key)

    diff_pairs = [
        (
            record_states[i],
            {}
            if i == 0
            else DeepDiff(record_states[i - 1].data, record_states[i].data),
        )
        for i in range(0, len(record_states))
    ]

    return jsonable_encoder(
        [
            {
                "id": pair[0].id,
                "key": pair[0].key,
                "data": pair[0].data,
                "tags": pair[0].tags,
                "meta": pair[0].meta,
                "created": pair[0].created,
                "last_updated": pair[0].last_updated,
                "diff_to_previous": pair[1],
            }
            for pair in diff_pairs
        ]
    )


@router.put(
    "/logbooks/{logbook_key}/records/{record_key}/states/{record_state_id}",
    response_model=RecordSchema,
)
async def update_record_state(
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    updated_record_state: RecordStateUpdate,
    db: Session = Depends(dependencies.get_db),
    api_key: APIKey = Depends(auth.get_api_key),
):
    return crud.update_record_state(
        db, logbook_key, record_key, record_state_id, updated_record_state
    )
