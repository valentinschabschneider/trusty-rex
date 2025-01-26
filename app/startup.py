import logging
import os
import subprocess
import sys

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import engine
from app.crud import create_logbook, find_logbook
from app.models import LogbookBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_connect_max_tries = 60 * 5  # 5 minutes
db_connect_wait_seconds = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as db:
        check_db(db)

        run_migrations()

        create_logbooks(db)

        yield


@retry(
    stop=stop_after_attempt(db_connect_max_tries),
    wait=wait_fixed(db_connect_wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def check_db(db: Session):
    try:
        # Try to create session to check if DB is awake
        db.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def run_migrations():
    """
    Runs Alembic database migrations using sys.executable and module execution.

    This method is more compatible with environments like Vercel where direct
    command execution might be restricted.
    """
    try:
        # Ensure the current directory is in the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        # Use sys.executable to run the Alembic module
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Print the output if there's any
        if result.stdout:
            logger.info("Migration output:", result.stdout)

        logger.info("Migrations completed successfully!")

    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed. Error: {e}")
        logger.error("Standard output:", e.stdout)
        logger.error("Standard error:", e.stderr)
        raise
    except Exception as e:
        logger.error(f"An error occurred while running migrations: {e}")
        raise


def create_logbooks(db: Session):
    for key in settings.DEFAULT_LOGBOOKS:
        if find_logbook(db, key) is None:
            logger.info(f"Creating default logbook with key: {key}")
            create_logbook(db, LogbookBase(key=key))
