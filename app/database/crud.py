from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas import LogbookCreate as LogbookCreateSchema
from app.schemas import RecordStateCreate as RecordStateCreateSchema
from app.schemas import RecordStateUpdate as RecordStateUpdateSchema

from .models import Logbook as LogbookModel
from .models import RecordState as RecordStateModel


def create_logbook(db: Session, new_logbook: LogbookCreateSchema):
    logbook = LogbookModel(key=new_logbook.key)

    db.add(logbook)
    db.commit()
    db.refresh(logbook)

    return logbook


def find_logbook(db: Session, key: str):
    return db.query(LogbookModel).filter(LogbookModel.key == key).first()


def get_logbook(db: Session, key: str):
    logbook = find_logbook(db, key)

    if not logbook:
        raise HTTPException(status_code=404, detail="Logbook not found")

    return logbook


def find_all_logbooks(db: Session):
    return db.query(LogbookModel).all()


def find_all_record_keys(db: Session, logbook_key: str):
    logbook = find_logbook(db, logbook_key)

    return [
        {"key": key, "amount_of_states": count}
        for key, count in (
            db.query(RecordStateModel.key, func.count(RecordStateModel.id))
            .filter(RecordStateModel.logbook_id == logbook.id)
            .group_by(RecordStateModel.key)
            .all()
        )
    ]


def create_record_state(
    db: Session,
    logbook_key: str,
    record_key: str,
    new_record_state: RecordStateCreateSchema,
):
    logbook = get_logbook(db, logbook_key)

    record_state = RecordStateModel(
        logbook_id=logbook.id,
        key=record_key,
        data=new_record_state.data,
        tags=new_record_state.tags,
        meta=new_record_state.meta,
        created=new_record_state.created,
        last_updated=new_record_state.created,
    )

    db.add(record_state)
    db.commit()
    db.refresh(record_state)

    return record_state


def update_record_state(
    db: Session,
    logbook_key: str,
    record_key: str,
    record_state_id: UUID,
    updated_record_state: RecordStateUpdateSchema,
):
    record_state = get_record_state(db, logbook_key, record_key, record_state_id)

    record_state.data = updated_record_state.data
    record_state.tags = updated_record_state.tags
    record_state.meta = updated_record_state.meta
    record_state.last_updated = updated_record_state.last_updated

    db.commit()
    db.refresh(record_state)

    return record_state


def get_record_state(
    db: Session, logbook_key: str, record_key: str, record_state_id: UUID
):
    logbook = get_logbook(db, logbook_key)

    record_state = (
        db.query(RecordStateModel)
        .filter(RecordStateModel.logbook_id == logbook.id)
        .filter(RecordStateModel.key == record_key)
        .filter(RecordStateModel.id == record_state_id)
        .first()
    )

    if not record_state:
        raise HTTPException(status_code=404, detail="Record state not found")

    return record_state


def find_record_states(db: Session, logbook_key: str, record_key: str):
    logbook = get_logbook(db, logbook_key)

    return (
        db.query(RecordStateModel)
        .filter(RecordStateModel.logbook_id == logbook.id)
        .filter(RecordStateModel.key == record_key)
        .order_by(RecordStateModel.key, RecordStateModel.created)
        .all()
    )
