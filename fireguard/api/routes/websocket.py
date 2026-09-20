from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from fireguard.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
