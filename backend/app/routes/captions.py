from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..services.caption_engine import get_caption_engine
from ..services.data_store import get_store


log = logging.getLogger("vla.captions")
router = APIRouter(prefix="/api/sessions", tags=["captions"])


def _sse(event: str, data: dict[str, object]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


@router.get("/{session_id}/captions/stream")
async def captions_stream(session_id: str) -> StreamingResponse:
    store = get_store()
    session = store.active_session()
    if session is None or session.id != session_id:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not active")

    engine = get_caption_engine()

    async def event_stream() -> AsyncIterator[bytes]:
        yield _sse("meta", {"session_id": session.id, "task": session.task})
        try:
            async for caption in engine.stream(session):
                yield _sse("caption", caption)
        except asyncio.CancelledError:
            return
        except Exception as exc:  # noqa: BLE001
            log.exception("captions stream failed")
            yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
