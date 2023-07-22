import contextlib
import logging

from fastapi import FastAPI
from fastapi.params import Depends

from app import database, dependencies, routes
from app.config import DEFAULT_LOGBOOKS
from app.database.crud import create_logbook, find_logbook
from app.database.models import Base
from app.schemas import LogbookCreate as LogbookCreateSchema

logger = logging.getLogger(__name__)


Base.metadata.create_all(bind=database.engine)

app = FastAPI(dependencies=[Depends(dependencies.get_db)])
app.include_router(routes.router)


@app.on_event("startup")
async def create_default_logbooks():  # doesn't work: "db: Session = Depends(dependencies.get_db)""
    with contextlib.contextmanager(dependencies.get_db)() as db:
        for key in DEFAULT_LOGBOOKS:
            if find_logbook(db, key) is None:
                logger.info(f"Creating default logbook for key: {key}")
                create_logbook(db, LogbookCreateSchema(key=key))
