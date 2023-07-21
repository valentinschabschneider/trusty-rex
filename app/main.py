import contextlib
import logging
from os import environ

from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import routes  # make better
from app import database, dependencies
from app.database.crud import create_logbook, find_logbook
from app.database.models import Base
from app.schemas import LogbookCreate as LogbookCreateSchema

logger = logging.getLogger(__name__)


def start_application():
    Base.metadata.create_all(bind=database.engine)

    app = FastAPI(dependencies=[Depends(dependencies.get_db)])

    app.include_router(routes.router)

    return app


app = start_application()


get_db_wrapper = contextlib.contextmanager(dependencies.get_db)  # bruh


@app.on_event("startup")
async def create_default_logbooks():  # doesn't work: "db: Session = Depends(dependencies.get_db)""
    with get_db_wrapper() as db:
        logbook_keys = [
            key.strip()
            for key in environ.get("DEFAULT_LOGBOOKS", "").split(",")
            if key.strip() != ""
        ]

        for key in logbook_keys:
            if find_logbook(db, key) is None:
                logger.info(f"Creating default logbook for key: {key}")
                create_logbook(db, LogbookCreateSchema(key=key))
