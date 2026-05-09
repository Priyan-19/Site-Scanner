"""
SiteScanner Core - WebSocket Route
Real-time scan progress streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import ws_manager
from app.core.store import scan_store
from app.core.logging import get_logger
import json

logger = get_logger("routes.ws")
ws_router = APIRouter()


@ws_router.websocket("/ws/scan/{scan_id}")
async def websocket_scan(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for real-time scan updates.
    Connects to scan_id and receives progress/complete/error events.
    """
    await ws_manager.connect(scan_id, websocket)
    logger.info(f"WS client connected: {scan_id[:8]}")

    try:
        # Send current state immediately on connect
        result = await scan_store.get(scan_id)
        if result:
            await websocket.send_text(json.dumps({
                "type": "state",
                "scan_id": scan_id,
                "status": result.status.value,
                "progress": result.progress,
                "stage": result.current_stage,
            }))

        # Keep alive until disconnect
        while True:
            try:
                data = await websocket.receive_text()
                # Handle ping
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        ws_manager.disconnect(scan_id, websocket)
        logger.info(f"WS client disconnected: {scan_id[:8]}")
