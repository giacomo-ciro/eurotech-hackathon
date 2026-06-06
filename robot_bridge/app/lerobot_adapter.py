from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator

import yaml


log = logging.getLogger("vla.lerobot_adapter")

STAGES_PATH = Path(__file__).resolve().parent.parent / "motions" / "recording_stages.yaml"


def _load_stages() -> dict[str, Any]:
    if not STAGES_PATH.exists():
        return {}
    with STAGES_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


async def run_recording(payload: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
    """Yield state events as a recording session progresses.

    For the hackathon demo this is a scripted mock — it follows the stages in
    recording_stages.yaml so the UI animates end-to-end without the arm being
    plugged in. Swap in real LeRobot data-capture calls below once the SO-101
    is calibrated.
    """
    config = _load_stages()
    stages = config.get("default", {}).get("stages", [])
    if not stages:
        stages = [
            {"name": "recording", "detail": "(no recording_stages.yaml)", "duration_s": 1.0},
            {"name": "saved", "detail": "mock save complete", "duration_s": 0.5},
        ]

    total = sum(float(stage.get("duration_s", 1.0)) for stage in stages) or 1.0
    elapsed = 0.0
    for stage in stages:
        duration = float(stage.get("duration_s", 1.0))
        yield {
            "stage": stage["name"],
            "detail": stage.get("detail", ""),
            "progress": round(elapsed / total, 3),
            "session_id": payload.get("session_id"),
            "task": payload.get("task"),
            "robot": payload.get("robot"),
        }
        await asyncio.sleep(duration)
        elapsed += duration

    yield {
        "stage": "idle",
        "detail": "ready for next recording",
        "progress": 1.0,
        "session_id": payload.get("session_id"),
        "task": payload.get("task"),
        "robot": payload.get("robot"),
    }
