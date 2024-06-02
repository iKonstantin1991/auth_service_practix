from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse, PlainTextResponse
from redis.asyncio import Redis

from core.config import settings
from db import redis
from api.v1 import auth


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

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return ORJSONResponse(status_code=500, content={'detail': 'internal server error'})


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
