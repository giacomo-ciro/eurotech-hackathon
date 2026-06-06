from __future__ import annotations

import os
from pathlib import Path


def _resolve_data_dir() -> Path:
    override = os.environ.get("VLA_DATA_DIR") or os.environ.get("DISPENSR_DATA_DIR")
    if override:
        return Path(override).resolve()
    return (Path(__file__).resolve().parents[2] / "data").resolve()


DATA_DIR: Path = _resolve_data_dir()
DATASETS_DIR = DATA_DIR / "datasets"
ACTIVE_SESSION_JSON = DATA_DIR / "active_session.json"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
ROBOT_BRIDGE_URL = os.environ.get("ROBOT_BRIDGE_URL", "ws://localhost:8001/ws")
ROBOT_BRIDGE_HTTP = os.environ.get("ROBOT_BRIDGE_HTTP", "http://localhost:8001")
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
