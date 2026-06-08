from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..models.schemas import ChatRequest
from ..services.claude_client import get_claude_client
from ..services.data_store import get_store


log = logging.getLogger("vla.chat")
router = APIRouter(prefix="/api/chat", tags=["chat"])


def _sse(event: str, data: dict[str, object]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


@router.post("")
async def chat(request: ChatRequest) -> StreamingResponse:
    store = get_store()

    session = None
    dataset = None
    episode = None

    if request.session_id:
        candidate = store.active_session()
        if candidate is not None and candidate.id == request.session_id:
            session = candidate
            dataset = store.dataset(session.dataset_id)
    if request.dataset_id:
        dataset = store.dataset(request.dataset_id) or dataset
    if request.dataset_id and request.episode_id:
        episode = store.episode(request.dataset_id, request.episode_id)

    client = get_claude_client()

    async def event_stream() -> AsyncIterator[bytes]:
        try:
            yield _sse(
                "meta",
                {
                    "session_id": session.id if session else None,
                    "dataset_id": dataset.id if dataset else None,
                    "episode_id": episode.id if episode else None,
                },
            )
            async for chunk in client.stream_chat(
                session=session,
                dataset=dataset,
                episode=episode,
                messages=request.messages,
            ):
                yield _sse("token", {"text": chunk})
            yield _sse("done", {})
        except RuntimeError as exc:
            yield _sse("error", {"message": str(exc)})
        except Exception as exc:  # noqa: BLE001
            log.exception("chat stream failed")
            yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
