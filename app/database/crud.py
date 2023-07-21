from sqlalchemy.orm import Session

from app.schemas import LogbookCreate as LogbookCreateSchema
from app.schemas import RecordCreate as RecordCreateSchema

from .models import Logbook as LogbookModel
from .models import Record as RecordModel


def create_logbook(db: Session, new_logbook: LogbookCreateSchema):
    logbook = LogbookModel(key=new_logbook.key)

    db.add(logbook)
    db.commit()
    db.refresh(logbook)

    return logbook


def find_logbook(db: Session, key: str):
    return db.query(LogbookModel).filter(LogbookModel.key == key).first()


def find_all_logbooks(db: Session):
    return db.query(LogbookModel).all()


def create_record(db: Session, logbook_key: str, new_record: RecordCreateSchema):
    logbook = find_logbook(db, logbook_key)

    record = RecordModel(
        logbook_id=logbook.id,
        key=new_record.key,
        data=new_record.data,
        tags=new_record.tags,
        meta=new_record.meta,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def find_records(db: Session, logbook_key: str, record_key: str = None):
    logbook = find_logbook(db, logbook_key)

    query = db.query(RecordModel).filter(RecordModel.logbook_id == logbook.id)

    if record_key is not None:
        query = query.filter(RecordModel.key == record_key)

    return query.order_by(RecordModel.key, RecordModel.created).all()
