from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.api import api_router
from app.common.logging import setup_logging
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Startup complete")
    yield
    logger.info("Shutdown complete")

app = FastAPI(
    title="Slowburn App",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
