from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..models.schemas import ChatRequest
from ..services.claude_client import get_claude_client
from ..services.data_store import get_store


log = logging.getLogger("dispensr.chat")
router = APIRouter(prefix="/api/chat", tags=["chat"])


def _sse(event: str, data: dict[str, object]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")


@router.post("")
async def chat(request: ChatRequest) -> StreamingResponse:
    store = get_store()
    medicine = store.medicine(request.drug_id)
    if medicine is None:
        raise HTTPException(status_code=404, detail=f"Drug {request.drug_id} not found")
    interactions = store.interactions_for(request.drug_id)

    active = store.active()
    patient = None
    if active is not None:
        prescription = store.prescription(active.prescription_id)
        if prescription is not None and prescription.drug_id == request.drug_id:
            patient = store.patient(prescription.patient_id)

    client = get_claude_client()

    async def event_stream() -> AsyncIterator[bytes]:
        try:
            yield _sse(
                "meta",
                {"drug_id": medicine.drug_id, "drug_name": medicine.drug_name},
            )
            async for chunk in client.stream_reply(
                medicine=medicine,
                interactions=interactions,
                patient=patient,
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
