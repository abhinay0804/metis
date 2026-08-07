import json
from typing import Dict, List, Any
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps job_id -> list of active websockets listening to that job
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            if websocket in self.active_connections[job_id]:
                self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast_job_update(self, job_id: str, status: str, message: str, data: Any = None):
        """Send a real-time status update to all connected clients for a specific job"""
        if job_id in self.active_connections:
            payload = {
                "job_id": job_id,
                "status": status,
                "message": message
            }
            if data:
                payload["data"] = data
                
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_text(json.dumps(payload))
                except Exception:
                    # If socket closed unexpectedly, ignore
                    pass

ws_manager = ConnectionManager()
