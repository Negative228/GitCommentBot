import os
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.webhook import router as webhook_router
from database import engine, Model

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
    
    print("База данных готова к работе")
    
    yield  
    
    print("Выключение сервера")


app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router)

@app.get("/")
async def ok():
    return {"message": "ok"}
