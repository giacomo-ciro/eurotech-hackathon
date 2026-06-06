from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncIterator

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

from .. import config


log = logging.getLogger("dispensr.robot_proxy")


class RobotProxy:
    """Fan-out hub: one upstream WS to robot-bridge, many downstream browser WS."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._last_event: dict[str, Any] = {"stage": "offline", "detail": "robot-bridge not connected"}

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="robot-proxy-upstream")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def subscribe(self) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=32)
        async with self._lock:
            self._subscribers.add(queue)
        try:
            await queue.put(self._last_event)
            while True:
                event = await queue.get()
                yield event
        finally:
            async with self._lock:
                self._subscribers.discard(queue)

    async def _broadcast(self, event: dict[str, Any]) -> None:
        self._last_event = event
        async with self._lock:
            queues = list(self._subscribers)
        for queue in queues:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass

    async def _run(self) -> None:
        backoff = 1.0
        while True:
            try:
                async with websockets.connect(config.ROBOT_BRIDGE_URL) as ws:
                    log.info("robot-bridge connected: %s", config.ROBOT_BRIDGE_URL)
                    backoff = 1.0
                    await self._broadcast({"stage": "idle", "detail": "robot-bridge online"})
                    async for raw in ws:
                        try:
                            event = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        await self._broadcast(event)
            except (ConnectionClosed, OSError) as exc:
                log.info("robot-bridge unreachable (%s); retrying in %.1fs", exc, backoff)
                await self._broadcast(
                    {"stage": "offline", "detail": "robot-bridge not connected"}
                )
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                log.exception("robot-proxy upstream error")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 10.0)

    async def trigger_dispense(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{config.ROBOT_BRIDGE_HTTP.rstrip('/')}/dispense"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()


_proxy = RobotProxy()


def get_robot_proxy() -> RobotProxy:
    return _proxy
