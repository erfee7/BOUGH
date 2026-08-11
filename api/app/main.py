import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.connection import init_pool, close_pool
from app.routers import conversations, messages, prompts, generation_presets
# Configure root logger for radical transparency
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs before the server starts accepting requests
    logger.info("Application starting up...")
    await init_pool()
    yield
    # Runs after the server stops accepting requests
    logger.info("Application shutting down...")
    await close_pool()

app = FastAPI(lifespan=lifespan)

# Register the router
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(prompts.router)
app.include_router(generation_presets.router)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}