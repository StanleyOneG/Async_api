from redis import Redis
from functional.settings import test_settings

redis = Redis(host=test_settings.redis_host, port=6379, decode_responses=True)
redis.set('mykey', 'thevalueofmykey')
print(redis.get('mykey'))
