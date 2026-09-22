# 实现连接大模型api：httpx
import httpx
import redis.asyncio as asyc_redis
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI,Request
from pydantic import BaseModel
from src.backend.conv_manage import add_history, get_history
from src.backend.setting import config

class Chat_data(BaseModel):
    prompt : str
    conv_id : int

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.client = httpx.AsyncClient(timeout=20.0)
    app.state.redis = asyc_redis.Redis(host="127.0.0.1",port=6379,db=0,decode_responses=True)
    yield 
    await app.state.client.aclose()
    await app.state.redis.aclose()
    pass

app = FastAPI(lifespan=lifespan)

async def get_client(req : Request):
    return req.app.state.client

async def get_redis(req : Request):
    return req.app.state.redis

async def chat_with_llm(message , client : httpx.AsyncClient):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {config.DEEPSEEK_API}"
    }
    payload = {
        "messages" : message,
        "model" : "deepseek-chat"
    }
    response = await client.post(url=url,headers=headers,json=payload)
    print(f"这里是报错：{response.text}")
    res = response.json()["choices"][0]["message"]["content"]
    return res



@app.post("/chat")
async def chat(
    cd : Chat_data ,
    client : httpx.AsyncClient = Depends(get_client),
    r : asyc_redis.Redis = Depends(get_redis)
):
    msg = await get_history(r=r , conv_id=cd.conv_id)
    user_msg = {"role" : "user" , "content" : cd.prompt}
    msg.append(user_msg)
    reply = await chat_with_llm(msg,client)
    assistant_msg = {"role" : "assistant" , "content" : reply}
    await add_history(r=r,user_msg=user_msg,assistant_msg=assistant_msg,conv_id=cd.conv_id)
    return reply
    

