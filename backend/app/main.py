from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api import chat, conversations, files
from app.services import mongo_service, redis_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await mongo_service.connect_db()
    await redis_service.connect_redis()
    yield
    # Shutdown
    await redis_service.close_redis()
    await mongo_service.close_db()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(files.router)


@app.get("/health")
async def health():
    mongo_ok = await mongo_service.ping_db()
    redis_ok = await redis_service.ping_redis()
    return {
        "status": "ok",
        "version": "1.0.0",
        "mongodb": "connected" if mongo_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
    }


@app.get("/")
async def root():
    return {"message": "Conversa AI API | by AiwithDhruv", "docs": "/docs"}
