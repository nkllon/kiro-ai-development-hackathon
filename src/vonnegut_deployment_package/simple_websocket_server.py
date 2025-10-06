#!/usr/bin/env python3
"""
Simple WebSocket Server for Constellation Dashboard

Reads status file and streams to WebSocket clients.
"""

import asyncio
import json
import websockets
from pathlib import Path
from datetime import datetime
import argparse


class SimpleWebSocketServer:
    """Simple WebSocket server that broadcasts status file changes"""

    def __init__(self, status_file: str, host: str = "localhost", port: int = 8765):
        self.status_file = Path(status_file)
        self.host = host
        self.port = port
        self.clients = set()
        self.last_status = None

    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        print(f"✅ Client connected from {websocket.remote_address} (total: {len(self.clients)})")

        # Send current status immediately
        if self.status_file.exists():
            try:
                with open(self.status_file) as f:
                    status = json.load(f)
                    await websocket.send(json.dumps({
                        "type": "status_update",
                        "timestamp": datetime.now().isoformat(),
                        "data": status
                    }))
            except Exception as e:
                print(f"⚠️  Error sending initial status: {e}")

    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.discard(websocket)
        print(f"❌ Client disconnected from {websocket.remote_address} (total: {len(self.clients)})")

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True,
            )

    async def handle_client(self, websocket):
        """Handle a WebSocket client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                # Handle client requests
                try:
                    request = json.loads(message)
                    if request.get("type") == "get_status":
                        if self.status_file.exists():
                            with open(self.status_file) as f:
                                status = json.load(f)
                                await websocket.send(json.dumps({
                                    "type": "status_update",
                                    "timestamp": datetime.now().isoformat(),
                                    "data": status
                                }))
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def file_watcher(self):
        """Watch status file for changes and broadcast"""
        print(f"👁️  Watching {self.status_file} for changes...")

        last_mtime = 0

        while True:
            try:
                if self.status_file.exists():
                    current_mtime = self.status_file.stat().st_mtime

                    if current_mtime != last_mtime:
                        last_mtime = current_mtime

                        # Read and broadcast new status
                        with open(self.status_file) as f:
                            status = json.load(f)

                        message = json.dumps({
                            "type": "status_update",
                            "timestamp": datetime.now().isoformat(),
                            "data": status
                        })

                        await self.broadcast(message)

                        # Calculate stats
                        prompts = status.get("prompts", {})
                        running = sum(1 for p in prompts.values() if p.get("status") == "running")
                        completed = sum(1 for p in prompts.values() if p.get("status") == "completed")
                        print(f"📊 Update: {completed} completed, {running} running")

            except Exception as e:
                print(f"⚠️  Error reading status file: {e}")

            await asyncio.sleep(0.5)  # Check every 500ms

    async def serve(self):
        """Start the WebSocket server"""
        print(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
        print(f"📁 Status file: {self.status_file}")

        # Start file watcher in background
        watcher_task = asyncio.create_task(self.file_watcher())

        # Start WebSocket server
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✅ WebSocket server running on ws://{self.host}:{self.port}")
            print(f"🌐 Dashboard: http://localhost:8080/constellation_dashboard.html")
            print(f"📡 Broadcasting status file changes...")

            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                print("\n⚠️  Shutting down...")
                watcher_task.cancel()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Simple WebSocket Status Server")
    parser.add_argument(
        "--status",
        default=".kiro/execution-status.json",
        help="Status file to watch (default: .kiro/execution-status.json)",
    )
    parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")

    args = parser.parse_args()

    server = SimpleWebSocketServer(
        status_file=args.status, host=args.host, port=args.port
    )
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
