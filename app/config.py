from os import environ

API_KEY = environ.get("API_KEY")

DATABASE_DRIVER = environ.get("DATABASE_DRIVER", "postgresql")
DATABASE_USER_NAME = environ.get("DATABASE_USER_NAME")
DATABASE_USER_PASSWORD = environ.get("DATABASE_USER_PASSWORD")
DATABASE_HOST = environ.get("DATABASE_HOST", "localhost")
DATABASE_PORT = environ.get("DATABASE_PORT", 5432)
DATABASE_NAME = environ.get("DATABASE_NAME")

DEFAULT_LOGBOOKS = [
    key.strip()
    for key in environ.get("DEFAULT_LOGBOOKS", "").split(",")
    if key.strip() != ""
]
