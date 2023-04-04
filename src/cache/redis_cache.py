import json
import logging
import uuid
from functools import wraps

from core.config import REDIS_CACHE_EXPIRE as EXPIRE
from .abstract_cache import AbstractBaseCache
from services.cache import get_cache_service


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


def cache(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs['request']
        redis: AbstractBaseCache = get_cache_service()
        key = str(request.url.path)
        if request.query_params:
            key = '?'.join([key, str(request.query_params)])
        value = await redis.get(key)
        if value:
            logging.info('CACHE HIT')
            value_json = value.decode('utf-8')
            value_dict = json.loads(value_json)
            return value_dict
        value = await func(*args, **kwargs)
        try:
            await redis.set(key, value.json(), EXPIRE)
        except:
            serialized_value = json.dumps(
                [dict(v) for v in value if not isinstance(v, uuid.UUID)],
                cls=UUIDEncoder,
            )
            await redis.set(key, serialized_value.encode('utf-8'), EXPIRE)
        logging.info('CACHE MISS')
        return value

    return wrapper
