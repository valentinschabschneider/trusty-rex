from datetime import datetime

from deepdiff import DeepDiff
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends
from sqlalchemy.orm import Session

import app.database.crud as crud
from app import dependencies
from app.schemas import Logbook as LogbookSchema
from app.schemas import LogbookCreate as LogbookCreateSchema
from app.schemas import Record as RecordSchema
from app.schemas import RecordCreate as RecordCreateSchema
from app.schemas import RecordHistory as RecordHistorySchema

router = APIRouter()


@router.get("/logbooks", response_model=list[LogbookSchema])
async def get_locations(db: Session = Depends(dependencies.get_db)):
    return crud.find_all_logbooks(db)


@router.post("/logbooks", response_model=LogbookSchema)
async def create_logbook(
    logbook: LogbookCreateSchema, db: Session = Depends(dependencies.get_db)
):
    return crud.create_logbook(db, logbook)


@router.post("/logbooks/{logbook_key}/records", response_model=RecordSchema)
async def create_record(
    logbook_key: str,
    record: RecordCreateSchema,
    db: Session = Depends(dependencies.get_db),
):
    return crud.create_record(db, logbook_key, record)


@router.get("/logbooks/{logbook_key}/records", response_model=list[RecordSchema])
async def get_records(
    logbook_key: str, record_key: str = None, db: Session = Depends(dependencies.get_db)
):
    return crud.find_records(db, logbook_key, record_key)


@router.get(
    "/logbooks/{logbook_key}/records/{record_key}/diff",
    response_model=list[RecordHistorySchema],
)
async def get_records(
    logbook_key: str, record_key: str, db: Session = Depends(dependencies.get_db)
):
    records = crud.find_records(db, logbook_key, record_key)

    diff_pairs = [
        (records[0], {}),
        *[
            (records[i], DeepDiff(records[i - 1].data, records[i].data))
            for i in range(1, len(records))
        ],
    ]

    return jsonable_encoder([Aaaaah(*pair) for pair in diff_pairs])


class Aaaaah:
    key: str
    data: dict = None
    tags: list[str] = None
    meta: dict = None
    created: datetime = None
    last_updated: datetime = None
    diff: dict

    def __init__(
        self,
        record: RecordSchema,
        diff: dict,
    ):
        self.key = record.key
        self.data = record.data
        self.tags = record.tags
        self.meta = record.meta
        self.created = record.created
        self.last_updated = record.last_updated
        self.diff = diff
