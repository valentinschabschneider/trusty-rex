from fastapi import APIRouter

from app.api.routes import logbook

api_router = APIRouter()
api_router.include_router(logbook.router)
