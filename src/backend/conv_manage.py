from redis.asyncio import Redis
from src.backend.setting import config
import json


async def get_history(r:Redis , conv_id : int):
    key = f"conv{conv_id}"
    res = await r.lrange(key, -config.HISTORY_LIMIT ,-1) # list[str]
    return [json.loads(m) for m in res] # list[dict]

async def add_history(r:Redis , conv_id : int ,  user_msg : dict , assistant_msg : dict):
    key = f"conv{conv_id}"
    cleaned_u = json.dumps(user_msg)
    cleaned_a = json.dumps(assistant_msg)
    await r.rpush(key , cleaned_u , cleaned_a)


