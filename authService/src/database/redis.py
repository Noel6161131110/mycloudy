import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis = None

async def getRedis():
    global _redis
    if not _redis:
        _redis = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis

async def closeRedis():
    if _redis:
        await _redis.close()