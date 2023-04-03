import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core import config
from db import storage, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    description=config.PROJECT_DESCRIPTION,
    version=config.PROJECT_VERSION,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = Redis(
        host=config.REDIS_CACHE_HOST, port=config.REDIS_CACHE_PORT
    )
    storage.storage = AsyncElasticsearch(
        [{'host': config.ELASTIC_HOST, 'port': config.ELASTIC_PORT}],
        http_auth=(config.ELASTIC_USERNAME, config.ELASTIC_PASSWORD),
    )


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await storage.storage.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
# app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
