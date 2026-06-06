from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .routes import captions, chat, datasets, lerobot, robot_ws, sessions
from .services.data_store import get_store
from .services.robot_proxy import get_robot_proxy


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_store()
    get_robot_proxy().start()
    yield
    await get_robot_proxy().stop()


app = FastAPI(title="VLA-DataEngine Backend", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(sessions.router)
app.include_router(captions.router)
app.include_router(chat.router)
app.include_router(lerobot.router)
app.include_router(robot_ws.router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
