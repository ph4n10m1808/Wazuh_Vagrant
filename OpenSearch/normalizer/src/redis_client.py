# src/python/redis_client.py

import redis
from config import REDIS_CONF

def connect_redis():
    return redis.StrictRedis(
        host=REDIS_CONF["host"],
        port=REDIS_CONF["port"],
        db=REDIS_CONF["db"],
        password=REDIS_CONF["password"],
        decode_responses=True
    )
