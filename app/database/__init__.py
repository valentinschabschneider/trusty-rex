from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from app.config import (
    DATABASE_DRIVER,
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PORT,
    DATABASE_USER_NAME,
    DATABASE_USER_PASSWORD,
)

database_url = URL.create(
    drivername=DATABASE_DRIVER,
    username=DATABASE_USER_NAME,
    password=DATABASE_USER_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
