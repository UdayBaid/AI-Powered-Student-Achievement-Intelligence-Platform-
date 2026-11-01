from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.api.config import FRONTEND_ORIGINS
from modules.api.database import init_db
from modules.api.routes import router
from modules.api.services.prediction import load_artifacts


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    load_artifacts()
    yield


app = FastAPI(
    title="Student Achievement Intelligence API",
    description="Predicts an estimated final student grade using a trained ML model.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(FRONTEND_ORIGINS),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)
