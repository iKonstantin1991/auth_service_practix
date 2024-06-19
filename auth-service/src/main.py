from contextlib import asynccontextmanager
import logging

import uvicorn
import aiohttp
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

import http_client
from core.config import settings
from core.logger import LOGGING
from db import redis
from api.v1 import auth, roles, users


logger = logging.getLogger(__name__)


def configure_tracer() -> None:
    provider = TracerProvider(resource=Resource(attributes={"service.name": settings.project_name}))
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f'http://{settings.jaeger_host}:{settings.jaeger_port}',
                                                    insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    http_client.session = aiohttp.ClientSession()
    await FastAPILimiter.init(redis.redis)
    yield
    await FastAPILimiter.close()
    await http_client.session.close()


configure_tracer()
app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
add_pagination(app)
FastAPIInstrumentor.instrument_app(app)

app.include_router(
    auth.router, prefix='/api/v1/auth',
    tags=['auth'],
    dependencies=[Depends(RateLimiter(times=5, seconds=1))]
)
app.include_router(
    roles.router,
    prefix='/api/v1/roles',
    tags=['roles'],
    dependencies=[Depends(RateLimiter(times=5, seconds=1))]
)
app.include_router(
    users.router,
    prefix='/api/v1/users',
    tags=['users'],
    dependencies=[Depends(RateLimiter(times=5, seconds=1))]
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                              content={'detail': 'X-Request-Id is required'})
    return await call_next(request)


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
