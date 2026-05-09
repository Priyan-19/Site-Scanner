"""
SiteScanner Core - WebSocket Manager
Real-time scan progress broadcasting.
"""
import asyncio
import json
from typing import Dict, List
from fastapi import WebSocket
from app.core.logging import get_logger

logger = get_logger("websocket")


class ConnectionManager:
    """Manages WebSocket connections per scan ID."""

    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, scan_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if scan_id not in self._connections:
            self._connections[scan_id] = []
        self._connections[scan_id].append(websocket)
        logger.info(f"WS connected: scan={scan_id} total={len(self._connections[scan_id])}")

    def disconnect(self, scan_id: str, websocket: WebSocket) -> None:
        if scan_id in self._connections:
            self._connections[scan_id].discard(websocket) if hasattr(
                self._connections[scan_id], 'discard'
            ) else None
            try:
                self._connections[scan_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[scan_id]:
                del self._connections[scan_id]
        logger.info(f"WS disconnected: scan={scan_id}")

    async def broadcast(self, scan_id: str, data: dict) -> None:
        if scan_id not in self._connections:
            return
        dead = []
        for ws in self._connections[scan_id]:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(scan_id, ws)

    async def send_progress(self, scan_id: str, stage: str, progress: int, detail: str = "") -> None:
        await self.broadcast(scan_id, {
            "type": "progress",
            "scan_id": scan_id,
            "stage": stage,
            "progress": progress,
            "detail": detail,
        })

    async def send_complete(self, scan_id: str, score: int, risk: str) -> None:
        await self.broadcast(scan_id, {
            "type": "complete",
            "scan_id": scan_id,
            "security_score": score,
            "risk_level": risk,
        })

    async def send_error(self, scan_id: str, error: str) -> None:
        await self.broadcast(scan_id, {
            "type": "error",
            "scan_id": scan_id,
            "error": error,
        })


ws_manager = ConnectionManager()
