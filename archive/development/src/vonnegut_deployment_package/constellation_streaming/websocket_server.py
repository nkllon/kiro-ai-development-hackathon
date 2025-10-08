#!/usr/bin/env python3
"""
WebSocket Status Server for Constellation Execution

Provides real-time WebSocket streaming of execution status to browser clients.
"""

import asyncio
import json
from typing import Set
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol

from .redis_stream import RedisStatusStream


class WebSocketStatusServer:
    """WebSocket server for real-time status streaming"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        redis_url: str = "redis://localhost:6379",
    ):
        """
        Initialize WebSocket server.

        Args:
            host: WebSocket server host
            port: WebSocket server port
            redis_url: Redis connection URL
        """
        self.host = host
        self.port = port
        self.redis_stream = RedisStatusStream(redis_url)
        self.clients: Set[WebSocketServerProtocol] = set()

    async def register(self, websocket: WebSocketServerProtocol):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        print(f"✅ Client connected: {websocket.remote_address} (total: {len(self.clients)})", flush=True)

        # Send latest cached status immediately
        latest_status = self.redis_stream.get_latest_status()
        if latest_status:
            # Wrap in proper message format
            from datetime import datetime
            response = {
                "type": "status_update",
                "timestamp": datetime.now().isoformat(),
                "data": latest_status
            }
            await websocket.send(json.dumps(response))

    async def unregister(self, websocket: WebSocketServerProtocol):
        """Unregister WebSocket client"""
        self.clients.discard(websocket)
        print(f"❌ Client disconnected: {websocket.remote_address} (total: {len(self.clients)})")

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if self.clients:
            # Create tasks for all sends to avoid blocking
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True,
            )

    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle individual WebSocket client connection"""
        await self.register(websocket)
        try:
            # Keep connection alive and handle incoming messages
            async for message in websocket:
                # Handle client requests (e.g., request full status)
                try:
                    request = json.loads(message)
                    if request.get("type") == "get_status":
                        status = self.redis_stream.get_latest_status()
                        if status:
                            # Wrap in proper message format
                            from datetime import datetime
                            response = {
                                "type": "status_update",
                                "timestamp": datetime.now().isoformat(),
                                "data": status
                            }
                            await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def redis_subscriber(self):
        """Subscribe to Redis and broadcast to WebSocket clients"""
        try:
            print(f"📡 Connecting to Redis...", flush=True)
            import redis.asyncio as aioredis

            # Use the same Redis URL as the stream
            redis_client = await aioredis.from_url(
                "redis://localhost:6379",
                decode_responses=True,
            )
            print(f"✅ Redis connected", flush=True)

            pubsub = redis_client.pubsub()

            # Subscribe to all channels
            print(f"📡 Subscribing to channels...", flush=True)
            await pubsub.subscribe(
                self.redis_stream.status_channel,
                self.redis_stream.prompt_channel,
                self.redis_stream.event_channel,
                self.redis_stream.heartbeat_channel,
            )

            print(f"✅ Subscribed to Redis channels: {self.redis_stream.status_channel}, {self.redis_stream.prompt_channel}, {self.redis_stream.event_channel}, {self.redis_stream.heartbeat_channel}", flush=True)

            async for message in pubsub.listen():
                if message["type"] == "message":
                    # Broadcast to all WebSocket clients
                    await self.broadcast(message["data"])
        except Exception as e:
            print(f"❌ Redis subscriber error: {e}", flush=True)
            import traceback
            traceback.print_exc()
        finally:
            try:
                await pubsub.unsubscribe()
                await redis_client.close()
            except:
                pass

    async def serve(self):
        """Start WebSocket server"""
        print(f"🚀 Starting WebSocket server on {self.host}:{self.port}", flush=True)

        # Start WebSocket server
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                print(f"✅ WebSocket server listening on ws://{self.host}:{self.port}", flush=True)

                # Start Redis subscriber in background
                print(f"📡 Starting Redis subscriber...", flush=True)
                subscriber_task = asyncio.create_task(self.redis_subscriber())

                print(f"✅ WebSocket server fully operational", flush=True)
                print(f"📊 Dashboard: http://localhost:8080/constellation_dashboard.html", flush=True)

                # Run forever
                try:
                    await asyncio.Future()  # Run forever
                except KeyboardInterrupt:
                    print("\n⚠️  Shutting down WebSocket server...", flush=True)
                    subscriber_task.cancel()
        except Exception as e:
            print(f"❌ Server error: {e}", flush=True)
            import traceback
            traceback.print_exc()

    def run(self):
        """Run WebSocket server (blocking)"""
        asyncio.run(self.serve())


async def main():
    """Main entry point for WebSocket server"""
    print("🎬 WebSocket server starting...", flush=True)
    import argparse

    parser = argparse.ArgumentParser(description="Constellation WebSocket Status Server")
    parser.add_argument("--host", default="localhost", help="WebSocket server host")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket server port")
    parser.add_argument(
        "--redis", default="redis://localhost:6379", help="Redis connection URL"
    )

    args = parser.parse_args()
    print(f"📋 Args parsed: host={args.host}, port={args.port}", flush=True)

    server = WebSocketStatusServer(host=args.host, port=args.port, redis_url=args.redis)
    print(f"✅ Server object created", flush=True)
    await server.serve()


if __name__ == "__main__":
    print("🏁 __main__ called", flush=True)
    asyncio.run(main())
