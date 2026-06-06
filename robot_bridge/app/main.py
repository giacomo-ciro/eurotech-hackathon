from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .lerobot_adapter import run_dispense


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("dispensr.robot_bridge")

app = FastAPI(title="Dispensr Robot Bridge", version="0.1.0")


class DispenseRequest(BaseModel):
    prescription_id: str
    drug_id: int
    drug_name: str
    tray: str


class _Hub:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._lock = asyncio.Lock()
        self._last: dict[str, Any] = {"stage": "idle", "detail": "robot-bridge online"}

    async def subscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        async with self._lock:
            self._subscribers.add(queue)
        await queue.put(self._last)

    async def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    async def publish(self, event: dict[str, Any]) -> None:
        self._last = event
        async with self._lock:
            queues = list(self._subscribers)
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass


_hub = _Hub()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def state_socket(socket: WebSocket) -> None:
    await socket.accept()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=32)
    await _hub.subscribe(queue)
    try:
        while True:
            event = await queue.get()
            await socket.send_json(event)
    except WebSocketDisconnect:
        return
    finally:
        await _hub.unsubscribe(queue)


@app.post("/dispense")
async def dispense(request: DispenseRequest) -> dict[str, Any]:
    log.info(
        "dispense requested: rx=%s drug=%s tray=%s",
        request.prescription_id,
        request.drug_name,
        request.tray,
    )

    async def _drive() -> None:
        async for event in run_dispense(request.model_dump()):
            await _hub.publish(event)

    asyncio.create_task(_drive(), name=f"dispense-{request.prescription_id}")
    return {"accepted": True, "prescription_id": request.prescription_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
