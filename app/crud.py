from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session, func, select

from app.models import LogbookBase, RecordStateCreate

from .models import Logbook, RecordState, RecordStateBase


def create_logbook(db: Session, new_logbook: LogbookBase):
    existing_logbook = find_logbook(db, new_logbook.key)

    if existing_logbook:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Logbook already exists"
        )

    logbook = Logbook.model_validate(new_logbook)

    db.add(logbook)
    db.commit()
    db.refresh(logbook)

    return logbook


def find_logbook(db: Session, key: str):
    statement = select(Logbook).where(Logbook.key == key)
    return db.exec(statement).first()


def get_logbook(db: Session, key: str):
    logbook = find_logbook(db, key)

    if not logbook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Logbook not found"
        )

    return logbook


def delete_logbook(db: Session, key: str):
    logbook = get_logbook(db, key)

    statement = select(RecordState).where(RecordState.logbook_id == logbook.id)
    states = db.exec(statement).all()

    for state in states:
        db.delete(state)

    db.delete(logbook)

    db.commit()


def find_all_logbooks(db: Session):
    statement = select(Logbook)
    return db.exec(statement).all()


def find_all_record_keys(db: Session, logbook_key: str):
    logbook = get_logbook(db, logbook_key)

    statement = (
        select(RecordState.key, func.count(RecordState.id))
        .where(RecordState.logbook_id == logbook.id)
        .group_by(RecordState.key)
    )
    states = db.exec(statement).all()

    return [{"key": key, "amount_of_states": count} for key, count in states]


def delete_record(db: Session, logbook_key: str, record_key: str):
    logbook = get_logbook(db, logbook_key)

    statement = (
        select(RecordState)
        .where(RecordState.logbook_id == logbook.id)
        .where(RecordState.key == record_key)
    )
    states = db.exec(statement).all()

    if not states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    for state in states:
        db.delete(state)

    db.commit()


def create_record_state(
    db: Session,
    logbook_key: str,
    record_key: str,
    new_record_state: RecordStateCreate,
):
    logbook = get_logbook(db, logbook_key)

    record_state = RecordState.model_validate(
        new_record_state,
        update={
            "logbook_id": logbook.id,
            "key": record_key,
            "created_at": datetime.now(),
        },
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
    updated_record_state: RecordStateBase,
):
    record_state = get_record_state(db, logbook_key, record_key, record_state_id)

    record_state = record_state.model_validate(updated_record_state)

    db.refresh(record_state)
    db.commit()

    return record_state


def delete_record_state(
    db: Session, logbook_key: str, record_key: str, record_state_id: UUID
):
    record_state = get_record_state(db, logbook_key, record_key, record_state_id)

    if not record_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record state not found"
        )

    db.delete(record_state)
    db.commit()


def get_record_state(
    db: Session, logbook_key: str, record_key: str, record_state_id: UUID
):
    logbook = get_logbook(db, logbook_key)

    statement = (
        select(RecordState)
        .where(RecordState.logbook_id == logbook.id)
        .where(RecordState.key == record_key)
        .where(RecordState.id == record_state_id)
    )
    state = db.exec(statement).first()

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record state not found"
        )

    return state


def get_latest_record_state(db: Session, logbook_key: str, record_key: str):
    logbook = get_logbook(db, logbook_key)

    statement = (
        select(RecordState)
        .where(RecordState.logbook_id == logbook.id)
        .where(RecordState.key == record_key)
        .order_by(RecordState.created_at.desc())
    )
    state = db.exec(statement).first()

    return state


def get_latest_record_state_or_raise(db: Session, logbook_key: str, record_key: str):
    state = get_latest_record_state(db, logbook_key, record_key)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record state not found"
        )

    return state


def find_record_states(db: Session, logbook_key: str, record_key: str):
    logbook = get_logbook(db, logbook_key)

    record_states = (
        db.query(RecordState)
        .filter(RecordState.logbook_id == logbook.id)
        .filter(RecordState.key == record_key)
        .order_by(RecordState.key, RecordState.created_at)
        .all()
    )

    if not record_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Record not found"
        )

    return record_states
