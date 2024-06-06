from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis

from core.config import settings
from core.logger import LOGGING
from db import redis
from api.v1 import auth, roles, users


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
add_pagination(app)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    logger.error('Exception has occurred when handled request to %s: %s', request.url , exc)
    return ORJSONResponse(status_code=500, content={'detail': 'internal server error'})


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
