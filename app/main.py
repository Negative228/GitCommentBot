import os
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.webhook import router as webhook_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(webhook_router)

@app.get("/ok")
async def ok():
    return {"status": "ok"}
