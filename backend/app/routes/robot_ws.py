from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..services.robot_proxy import get_robot_proxy


log = logging.getLogger("dispensr.robot_ws")
router = APIRouter()


@router.websocket("/ws/robot")
async def robot_ws(socket: WebSocket) -> None:
    await socket.accept()
    proxy = get_robot_proxy()
    try:
        async for event in proxy.subscribe():
            await socket.send_json(event)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        raise
    except Exception:  # noqa: BLE001
        log.exception("robot_ws fan-out error")
        await socket.close(code=1011)
