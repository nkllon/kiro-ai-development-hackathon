#!/usr/bin/env python3
"""
Quick peek at the bus to see if there are any messages
"""

import asyncio
import json
import redis.asyncio as redis
from datetime import datetime


async def peek_bus():
    """Peek at the bus for any recent activity"""
    client = redis.from_url("redis://localhost:6379")
    
    try:
        await client.ping()
        print("🧬 Peeking at the bus...")
        
        # Check if there are any subscribers
        channels = await client.pubsub_channels("beast_mode_network")
        numsub = await client.pubsub_numsub("beast_mode_network")
        
        print(f"Active channels: {channels}")
        print(f"Subscribers to beast_mode_network: {numsub}")
        
        # Try to listen for just a moment to see if there's any activity
        pubsub = client.pubsub()
        await pubsub.subscribe("beast_mode_network")
        
        print("Listening for 3 seconds to see if there's any activity...")
        
        try:
            message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=3.0)
            if message:
                print(f"📨 Got message: {message}")
            else:
                print("📭 No messages in the last 3 seconds")
        except asyncio.TimeoutError:
            print("📭 No messages in the last 3 seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(peek_bus())