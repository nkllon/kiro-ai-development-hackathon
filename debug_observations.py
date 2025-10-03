#!/usr/bin/env python3
"""
Debug script to monitor Observatory observations in real-time
"""
import asyncio
import json
import websockets
from datetime import datetime

async def monitor_observations():
    """Connect to Observatory WebSocket and monitor observations"""
    uri = "ws://localhost:8888/ws/observations"

    print("🔍 Connecting to Observatory observations feed...")
    print(f"URI: {uri}")
    print("=" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Monitoring observations...\n")

            message_count = 0
            garbage_count = 0

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    message_count += 1

                    msg_text = data.get('message', 'NO MESSAGE')
                    msg_type = data.get('type', data.get('event_type', 'unknown'))
                    module = data.get('module', 'unknown')

                    # Check if this looks like garbage
                    is_garbage = False
                    if 'system status' in msg_text.lower() and ('zero' in msg_text.lower() or ' 0' in msg_text):
                        is_garbage = True
                        garbage_count += 1
                        print(f"\n🗑️  GARBAGE MESSAGE #{garbage_count} (total: {message_count})")
                        print(f"   Type: {msg_type}")
                        print(f"   Module: {module}")
                        print(f"   Message: {msg_text}")
                        print(f"   Full data: {json.dumps(data, indent=2)}")
                        print("-" * 60)
                    else:
                        print(f"✓ #{message_count} [{msg_type}] {module}: {msg_text[:80]}")

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to decode JSON: {e}")
                    print(f"   Raw message: {message}")
                except Exception as e:
                    print(f"❌ Error processing message: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("\n❌ Connection closed")
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔭 Observatory Observation Debug Monitor")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(monitor_observations())
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
