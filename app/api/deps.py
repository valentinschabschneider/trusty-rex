from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine

_api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


DBSessionDep = Annotated[Session, Depends(get_db)]


def check_api_key(x_api_key: str = Security(_api_key_header)):
    if settings.API_KEY is not None and x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid api key"
        )
    return True


AuthDep = Depends(check_api_key)
