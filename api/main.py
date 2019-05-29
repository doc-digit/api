import os

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from api.exceptions import NotFoundException
from core import config
from api.routes.storage import router as storage_router
from api.routes.user import router as user_router
from api.database import SessionLocal

app = FastAPI(title="docdigit-api", version="0.1")
app.include_router(storage_router, prefix="/storage", tags=["storage"])
app.include_router(user_router, prefix="/user", tags=["user"])


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(status_code=404, content={"message": "Not found"})
