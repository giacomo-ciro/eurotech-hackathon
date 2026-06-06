from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from ..models.schemas import Session
from ..services.data_store import get_store
from ..services.robot_proxy import get_robot_proxy


log = logging.getLogger("vla.sessions")
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/active", response_model=Session)
def get_active() -> Session:
    session = get_store().active_session()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session configured")
    return session


@router.post("/{session_id}/start", response_model=Session)
async def start(session_id: str) -> Session:
    store = get_store()
    session = store.active_session()
    if session is None or session.id != session_id:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not active")

    payload = {
        "session_id": session.id,
        "task": session.task,
        "robot": session.robot,
    }
    try:
        await get_robot_proxy().trigger_record(payload)
    except httpx.HTTPError as exc:
        store.set_session_state("error")
        log.warning("robot-bridge record failed: %s", exc)
        raise HTTPException(status_code=503, detail=f"robot-bridge unreachable: {exc}") from exc

    updated = store.set_session_state("recording")
    return updated or session


@router.post("/{session_id}/stop", response_model=Session)
async def stop(session_id: str) -> Session:
    store = get_store()
    session = store.active_session()
    if session is None or session.id != session_id:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not active")
    updated = store.set_session_state(
        "saved",
        episode_count=session.episode_count + 1,
    )
    _ = datetime.now(timezone.utc).isoformat()
    return updated or session
