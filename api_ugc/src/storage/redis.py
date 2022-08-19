from redis import StrictRedis
from redis_cache import RedisCache

from core.settings import get_settings

client = StrictRedis(
    host=get_settings().redis_settings.endpoint,
    port=get_settings().redis_settings.port,
    decode_responses=True,
)
cache = RedisCache(redis_client=client)
