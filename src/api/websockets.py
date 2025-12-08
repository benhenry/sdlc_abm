"""WebSocket support for real-time simulation updates

Provides WebSocket connections for clients to receive live progress updates.
"""

import asyncio
import json
import os
from typing import Dict, Set
from uuid import UUID

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Store active WebSocket connections per simulation
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for simulations"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_client = None

    async def connect(self, websocket: WebSocket, simulation_id: str):
        """Accept WebSocket connection and subscribe to simulation updates"""
        await websocket.accept()

        if simulation_id not in self.active_connections:
            self.active_connections[simulation_id] = set()

        self.active_connections[simulation_id].add(websocket)

    def disconnect(self, websocket: WebSocket, simulation_id: str):
        """Remove WebSocket connection"""
        if simulation_id in self.active_connections:
            self.active_connections[simulation_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[simulation_id]:
                del self.active_connections[simulation_id]

    async def send_message(self, message: dict, simulation_id: str):
        """Send message to all connected clients for a simulation"""
        if simulation_id not in self.active_connections:
            return

        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections[simulation_id]:
            try:
                await connection.send_json(message)
            except Exception:
                # Mark for removal if send fails
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, simulation_id)

    async def get_redis_client(self):
        """Get or create Redis client"""
        if self.redis_client is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = await aioredis.from_url(redis_url, decode_responses=True)
        return self.redis_client

    async def listen_to_redis(self, simulation_id: str):
        """Listen to Redis pub/sub for simulation updates

        This allows Celery workers to publish updates that get forwarded to WebSocket clients.
        """
        redis_client = await self.get_redis_client()
        pubsub = redis_client.pubsub()

        channel = f"simulation:{simulation_id}:progress"
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    # Parse and forward to WebSocket clients
                    try:
                        data = json.loads(message["data"])
                        await self.send_message(data, simulation_id)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from Redis: {message['data']}")
        except Exception as e:
            print(f"Redis listener error for {simulation_id}: {e}")
        finally:
            await pubsub.unsubscribe(channel)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/api/simulations/{simulation_id}/progress")
async def simulation_progress_websocket(
    websocket: WebSocket,
    simulation_id: str
):
    """WebSocket endpoint for real-time simulation progress updates

    Clients connect to this endpoint to receive live updates as the simulation runs.

    Message format:
        {
            "type": "progress",
            "simulation_id": "uuid",
            "progress": 0.5,
            "current_step": 130,
            "total_steps": 260,
            "current_metrics": {...}
        }
    """
    await manager.connect(websocket, simulation_id)

    try:
        # Start Redis listener in background
        redis_task = asyncio.create_task(manager.listen_to_redis(simulation_id))

        # Keep connection alive and handle client messages
        while True:
            # Wait for messages from client (ping/pong to keep alive)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                # Echo back ping messages
                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": asyncio.get_event_loop().time()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, simulation_id)
        print(f"Client disconnected from simulation {simulation_id}")

    except Exception as e:
        print(f"WebSocket error for simulation {simulation_id}: {e}")
        manager.disconnect(websocket, simulation_id)

    finally:
        # Cancel Redis listener
        if 'redis_task' in locals():
            redis_task.cancel()
            try:
                await redis_task
            except asyncio.CancelledError:
                pass
