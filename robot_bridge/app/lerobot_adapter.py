from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator

import yaml


log = logging.getLogger("dispensr.lerobot_adapter")

WAYPOINTS_PATH = Path(__file__).resolve().parent.parent / "motions" / "waypoints.yaml"


def _load_waypoints() -> dict[str, Any]:
    if not WAYPOINTS_PATH.exists():
        return {}
    with WAYPOINTS_PATH.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


async def run_dispense(payload: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
    """Yield state events as the dispense motion runs.

    For the hackathon demo this is a scripted mock — it follows the stages in
    waypoints.yaml so the UI animates end-to-end without the arm being
    plugged in. Swap in real LeRobot calls below once the SO-101 is
    calibrated.
    """
    config = _load_waypoints()
    stages = config.get("default", {}).get("stages", [])
    if not stages:
        stages = [
            {"name": "scanning", "detail": "(no waypoints.yaml)", "duration_s": 1.0},
            {"name": "done", "detail": "mock dispense complete", "duration_s": 0.5},
        ]

    total = sum(float(stage.get("duration_s", 1.0)) for stage in stages) or 1.0
    elapsed = 0.0
    for stage in stages:
        duration = float(stage.get("duration_s", 1.0))
        yield {
            "stage": stage["name"],
            "detail": stage.get("detail", ""),
            "progress": round(elapsed / total, 3),
            "drug_id": payload.get("drug_id"),
            "drug_name": payload.get("drug_name"),
            "tray": payload.get("tray"),
        }
        await asyncio.sleep(duration)
        elapsed += duration

    yield {
        "stage": "idle",
        "detail": "ready for next prescription",
        "progress": 1.0,
        "drug_id": payload.get("drug_id"),
        "drug_name": payload.get("drug_name"),
        "tray": payload.get("tray"),
    }
