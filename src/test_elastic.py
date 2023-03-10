import asyncio
from elasticsearch import AsyncElasticsearch
from core import config

es = AsyncElasticsearch(
    [{'host': config.ELASTIC_HOST, 'port': config.ELASTIC_PORT}],
    http_auth=(config.ELASTIC_USERNAME, config.ELASTIC_PASSWORD),
)


async def main():
    resp = await es.search(
        index="persons",
        body={"query": {"match_all": {}}},
        # size=20,
    )
    print(resp)


# loop = asyncio.get_event_loop()
asyncio.run(main())
