# 实现连接大模型api：httpx
import httpx
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI,Request
from pydantic import BaseModel
from src.backend.setting import config

class Chat_data(BaseModel):
    prompt : str

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.client = httpx.AsyncClient(timeout=20.0)
    yield 
    await app.state.client.aclose()
    pass

app = FastAPI(lifespan=lifespan)

async def get_client(req : Request):
    return req.app.state.client

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

msg = []

@app.post("/chat")
async def chat(cd : Chat_data ,client : httpx.AsyncClient = Depends(get_client)):
    user_msg = {"role" : "user" , "content" : cd.prompt}
    msg.append(user_msg)
    reply = await chat_with_llm(msg,client)
    return reply
    

