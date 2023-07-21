from os import environ

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

database_url = URL.create(
    environ.get("DATABASE_DRIVER", "postgresql"),
    username=environ.get("DATABASE_USER_NAME"),
    password=environ.get("DATABASE_USER_PASSWORD"),
    host=environ.get("DATABASE_HOST", "localhost"),
    port=environ.get("DATABASE_PORT", 5432),
    database=environ.get("DATABASE_NAME"),
)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
