import os
import json
import redis.asyncio as aioredis

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
_client = None
_checked = False
_memory_cache = {}

async def get_client():
    global _client, _checked
    if not _checked:
        _checked = True
        try:
            c = aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=0.1)
            await c.ping()
            _client = c
        except Exception:
            _client = None
    return _client

async def cache_set(key: str, data: dict | list | str, expire: int = 300):
    val = json.dumps(data, default=str) if not isinstance(data, str) else data
    client = await get_client()
    if client:
        try:
            await client.set(key, val, ex=expire)
            return
        except Exception:
            pass
    _memory_cache[key] = val

async def cache_get(key: str):
    client = await get_client()
    if client:
        try:
            val = await client.get(key)
            if val is not None:
                return json.loads(val) if (val.startswith('{') or val.startswith('[')) else val
        except Exception:
            pass
    val = _memory_cache.get(key)
    if val is not None:
        return json.loads(val) if (val.startswith('{') or val.startswith('[')) else val
    return None

async def publish_event(channel: str, message: dict | str):
    val = json.dumps(message, default=str) if not isinstance(message, str) else message
    client = await get_client()
    if client:
        try:
            await client.publish(channel, val)
        except Exception:
            pass
