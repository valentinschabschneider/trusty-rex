from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.config import API_KEY

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
