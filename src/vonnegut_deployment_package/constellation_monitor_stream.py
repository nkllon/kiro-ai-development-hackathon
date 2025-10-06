#!/usr/bin/env python3
"""
Real-time Streaming Monitor for Constellation Execution

Connects to WebSocket server for real-time updates (no polling).
"""

import json
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Try to import websockets
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets library not available. Install with: pip install websockets")
    sys.exit(1)


def clear_screen():
    """Clear terminal screen"""
    print("\033[2J\033[H", end="")


def draw_progress_bar(progress, width=50):
    """Draw a progress bar"""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress:.1f}%"


class StreamingMonitor:
    """Real-time streaming monitor using WebSocket"""

    def __init__(self, websocket_url: str = "ws://localhost:8765"):
        self.websocket_url = websocket_url
        self.current_status = None
        self.recent_events = []
        self.max_events = 10

    async def connect_and_monitor(self):
        """Connect to WebSocket server and display real-time updates"""
        print(f"📡 Connecting to {self.websocket_url}...")

        try:
            async with websockets.connect(self.websocket_url) as websocket:
                print("✅ Connected! Receiving real-time updates...\n")

                # Request initial status
                await websocket.send(json.dumps({"type": "get_status"}))

                # Listen for updates
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.handle_message(data)
                    except json.JSONDecodeError:
                        pass

        except ConnectionRefusedError:
            print("❌ Connection refused. Is the WebSocket server running?")
            print("\n🚀 Start server with:")
            print("   python3 -m src.constellation_streaming.websocket_server")
        except Exception as e:
            print(f"❌ Connection error: {e}")

    async def handle_message(self, data: dict):
        """Handle incoming WebSocket message"""
        msg_type = data.get("type")

        if msg_type == "status_update":
            self.current_status = data.get("data")
            self.display_dashboard()

        elif msg_type == "prompt_update":
            # Add to recent events
            prompt_name = data.get("prompt_name")
            status = data.get("status")
            self.recent_events.append({
                "timestamp": data.get("timestamp"),
                "message": f"📝 {prompt_name}: {status}",
            })
            if len(self.recent_events) > self.max_events:
                self.recent_events.pop(0)

            # Refresh display if we have status
            if self.current_status:
                self.display_dashboard()

        elif msg_type in ["prompt_started", "prompt_completed", "prompt_failed", "execution_started"]:
            # Add event to recent events
            self.recent_events.append({
                "timestamp": data.get("timestamp"),
                "message": f"🔔 {data.get('message')}",
            })
            if len(self.recent_events) > self.max_events:
                self.recent_events.pop(0)

        elif msg_type == "heartbeat":
            # Update stats without full refresh
            pass

    def display_dashboard(self):
        """Display dashboard with current status"""
        if not self.current_status:
            return

        clear_screen()

        status = self.current_status
        prompts = status.get("prompts", {})

        # Header
        print("=" * 100)
        print("CONSTELLATION ELABORATION - REAL-TIME DASHBOARD (STREAMING)")
        print("=" * 100)
        print(f"🆔 Execution ID: {status.get('execution_id', 'N/A')}")
        print(f"📊 Status: {status.get('status', 'unknown').upper()}")
        print(f"🕐 Started: {status.get('started_at', 'N/A')}")

        # Calculate stats
        total = len(prompts)
        pending = sum(1 for p in prompts.values() if p.get("status") == "pending")
        running = sum(1 for p in prompts.values() if p.get("status") == "running")
        completed = sum(1 for p in prompts.values() if p.get("status") == "completed")
        failed = sum(1 for p in prompts.values() if p.get("status") == "failed")

        progress = (completed + failed) / total * 100 if total > 0 else 0

        # Progress bar
        print("\n" + "=" * 100)
        print(f"Progress: {draw_progress_bar(progress)}")
        print(
            f"Total: {total} | Pending: {pending} | Running: {running} | Completed: {completed} | Failed: {failed}"
        )
        print("=" * 100)

        # Currently running prompts
        if running > 0:
            print("\n🔄 CURRENTLY RUNNING:")
            for name, info in prompts.items():
                if info.get("status") == "running":
                    started_str = info.get("started_at")
                    if started_str:
                        started = datetime.fromisoformat(started_str)
                        elapsed = (datetime.now() - started).total_seconds() / 60
                        agent = info.get("agent_id", "N/A")
                        print(f"  [{agent}] {name} ({elapsed:.1f} min elapsed)")

        # Recently completed
        recently_completed = [
            (name, info)
            for name, info in prompts.items()
            if info.get("status") == "completed" and info.get("completed_at")
        ]
        recently_completed.sort(key=lambda x: x[1].get("completed_at", ""), reverse=True)

        if recently_completed:
            print("\n✅ RECENTLY COMPLETED (last 5):")
            for name, info in recently_completed[:5]:
                agent = info.get("agent_id", "N/A")
                duration = info.get("duration_min", 0)
                print(f"  [{agent}] {name} ({duration:.1f} min)")

        # Failed prompts
        if failed > 0:
            print("\n❌ FAILED:")
            for name, info in prompts.items():
                if info.get("status") == "failed":
                    error = info.get("error", "Unknown error")[:80]
                    print(f"  {name}: {error}")

        # Recent events
        if self.recent_events:
            print("\n📰 RECENT EVENTS:")
            for event in self.recent_events[-5:]:
                timestamp = event["timestamp"][:19] if event["timestamp"] else "N/A"
                print(f"  [{timestamp}] {event['message']}")

        # ETA calculation
        if completed > 0:
            avg_duration = sum(
                p.get("duration_min", 0) for p in prompts.values() if p.get("duration_min")
            ) / completed

            remaining = pending + running
            concurrent_agents = min(running if running > 0 else status.get("max_agents", 10), remaining)
            eta_min = (remaining * avg_duration) / concurrent_agents if concurrent_agents > 0 else 0
            eta = datetime.now() + timedelta(minutes=eta_min)

            print(
                f"\n⏰ ESTIMATED COMPLETION: {eta.strftime('%Y-%m-%d %H:%M:%S')} ({eta_min:.0f} min remaining)"
            )

        print("\n" + "=" * 100)
        print(f"🌐 Streaming from: {self.websocket_url}")
        print(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to exit")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Real-time Constellation Streaming Monitor")
    parser.add_argument(
        "--websocket",
        default="ws://localhost:8765",
        help="WebSocket server URL (default: ws://localhost:8765)",
    )

    args = parser.parse_args()

    monitor = StreamingMonitor(websocket_url=args.websocket)

    try:
        await monitor.connect_and_monitor()
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
