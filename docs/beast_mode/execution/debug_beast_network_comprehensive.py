#!/usr/bin/env python3
"""
Comprehensive Beast Mode Network Diagnostics
Checks all possible communication channels and agent states
"""

import redis
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


def check_redis_clients(r: redis.Redis) -> Dict[str, Any]:
    """Check all connected Redis clients"""
    try:
        clients = r.client_list()
        print(f"\n🔍 **REDIS CLIENT ANALYSIS** ({len(clients)} total clients)")

        client_info = []
        for i, client in enumerate(clients):
            info = {
                "id": client.get("id", "unknown"),
                "name": client.get("name", "unnamed"),
                "addr": client.get("addr", "unknown"),
                "age": client.get("age", 0),
                "idle": client.get("idle", 0),
                "cmd": client.get("cmd", "none"),
            }
            client_info.append(info)

            # Calculate human-readable times
            age_mins = int(info["age"]) // 60 if info["age"] else 0
            idle_secs = int(info["idle"]) if info["idle"] else 0

            print(
                f"  Client {i+1}: {info['name'] or 'unnamed'} | "
                f"Age: {age_mins}m | Idle: {idle_secs}s | "
                f"Last: {info['cmd']} | {info['addr']}"
            )

        return {"count": len(clients), "clients": client_info}
    except Exception as e:
        print(f"❌ Error checking clients: {e}")
        return {"count": 0, "clients": [], "error": str(e)}


def check_all_queues(r: redis.Redis) -> Dict[str, Any]:
    """Check all possible message queues"""
    possible_queues = [
        "beast_mode_messages",
        "beast_mode_queue",
        "agent_messages",
        "collaboration_queue",
        "tidb_messages",
        "spore_messages",
        "system_messages",
    ]

    print(f"\n📬 **QUEUE ANALYSIS**")
    queue_status = {}

    for queue_name in possible_queues:
        try:
            length = r.llen(queue_name)
            if length > 0:
                # Get recent messages
                messages = r.lrange(queue_name, -5, -1)  # Last 5 messages
                decoded_messages = []
                for msg in messages:
                    try:
                        decoded = json.loads(msg.decode("utf-8"))
                        decoded_messages.append(decoded)
                    except:
                        decoded_messages.append(msg.decode("utf-8"))

                queue_status[queue_name] = {
                    "length": length,
                    "recent_messages": decoded_messages,
                }
                print(f"  ✅ {queue_name}: {length} messages")

                # Show recent message summary
                for msg in decoded_messages[-2:]:  # Last 2 messages
                    if isinstance(msg, dict):
                        sender = msg.get("sender", "unknown")
                        msg_type = msg.get("type", "unknown")
                        timestamp = msg.get("timestamp", "unknown")
                        print(f"    └─ {sender} → {msg_type} @ {timestamp}")
            else:
                print(f"  ⚪ {queue_name}: empty")
                queue_status[queue_name] = {"length": 0, "recent_messages": []}

        except Exception as e:
            print(f"  ❌ {queue_name}: error - {e}")
            queue_status[queue_name] = {"error": str(e)}

    return queue_status


def check_agent_heartbeats(r: redis.Redis) -> Dict[str, Any]:
    """Check for agent heartbeat/status keys"""
    print(f"\n💓 **AGENT HEARTBEAT ANALYSIS**")

    # Look for common agent status patterns
    patterns = [
        "agent:*:status",
        "agent:*:heartbeat",
        "beast_mode:*:status",
        "tidb:*",
        "spore:*:status",
        "*:last_seen",
    ]

    agent_status = {}
    for pattern in patterns:
        try:
            keys = r.keys(pattern)
            if keys:
                print(f"  📡 Pattern '{pattern}': {len(keys)} keys found")
                for key in keys[:5]:  # Show first 5
                    try:
                        value = r.get(key)
                        if value:
                            decoded = value.decode("utf-8")
                            try:
                                parsed = json.loads(decoded)
                                agent_status[key.decode("utf-8")] = parsed
                                print(f"    └─ {key.decode('utf-8')}: {parsed}")
                            except:
                                agent_status[key.decode("utf-8")] = decoded
                                print(f"    └─ {key.decode('utf-8')}: {decoded}")
                    except Exception as e:
                        print(f"    └─ {key.decode('utf-8')}: error reading - {e}")
            else:
                print(f"  ⚪ Pattern '{pattern}': no keys found")
        except Exception as e:
            print(f"  ❌ Pattern '{pattern}': error - {e}")

    return agent_status


def check_pubsub_channels(r: redis.Redis) -> Dict[str, Any]:
    """Check active pub/sub channels"""
    print(f"\n📻 **PUB/SUB CHANNEL ANALYSIS**")

    try:
        # Get active channels
        channels = r.pubsub_channels()
        if channels:
            print(f"  📡 Active channels: {len(channels)}")
            for channel in channels:
                num_subs = r.pubsub_numsub(channel)[0][1]
                print(f"    └─ {channel.decode('utf-8')}: {num_subs} subscribers")
        else:
            print(f"  ⚪ No active pub/sub channels")

        return {"channels": [ch.decode("utf-8") for ch in channels]}
    except Exception as e:
        print(f"  ❌ Error checking pub/sub: {e}")
        return {"error": str(e)}


def send_network_ping(r: redis.Redis) -> bool:
    """Send a network-wide ping to see who responds"""
    print(f"\n📡 **SENDING NETWORK PING**")

    ping_message = {
        "type": "NETWORK_PING",
        "sender": "NETWORK_DIAGNOSTICS",
        "timestamp": datetime.now().isoformat(),
        "message": "Network diagnostic ping - please respond with PONG",
        "respond_to": "beast_mode_messages",
    }

    try:
        r.lpush("beast_mode_messages", json.dumps(ping_message))
        print(f"  ✅ Ping sent to beast_mode_messages queue")

        # Wait a moment and check for responses
        print(f"  ⏳ Waiting 3 seconds for responses...")
        time.sleep(3)

        # Check for PONG responses
        messages = r.lrange("beast_mode_messages", 0, -1)
        pong_count = 0
        for msg in messages:
            try:
                decoded = json.loads(msg.decode("utf-8"))
                if decoded.get(
                    "type"
                ) == "PONG" and "NETWORK_DIAGNOSTICS" in decoded.get("message", ""):
                    pong_count += 1
                    sender = decoded.get("sender", "unknown")
                    print(f"    🏓 PONG received from: {sender}")
            except:
                continue

        if pong_count == 0:
            print(f"  ⚠️  No PONG responses received")

        return pong_count > 0

    except Exception as e:
        print(f"  ❌ Error sending ping: {e}")
        return False


def main():
    """Run comprehensive network diagnostics"""
    print("🔍 **BEAST MODE NETWORK COMPREHENSIVE DIAGNOSTICS**")
    print("=" * 60)

    try:
        # Connect to Redis
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)

        # Test connection
        r.ping()
        print("✅ Redis connection successful")

        # Run all diagnostic checks
        client_info = check_redis_clients(r)
        queue_status = check_all_queues(r)
        agent_status = check_agent_heartbeats(r)
        pubsub_info = check_pubsub_channels(r)
        ping_success = send_network_ping(r)

        # Summary
        print(f"\n📊 **DIAGNOSTIC SUMMARY**")
        print(f"  Connected Clients: {client_info['count']}")
        print(
            f"  Active Queues: {sum(1 for q, info in queue_status.items() if info.get('length', 0) > 0)}"
        )
        print(f"  Agent Status Keys: {len(agent_status)}")
        print(f"  Pub/Sub Channels: {len(pubsub_info.get('channels', []))}")
        print(
            f"  Network Ping Response: {'✅ Success' if ping_success else '❌ No Response'}"
        )

        # Recommendations
        print(f"\n💡 **RECOMMENDATIONS**")
        if client_info["count"] > 1:
            print(f"  • {client_info['count']} clients connected - agents are online")
        if not ping_success:
            print(
                f"  • No ping responses - agents may not be listening to beast_mode_messages"
            )
            print(f"  • Check if agents are using different queue names")
            print(f"  • Verify agent listener processes are running")

        return True

    except redis.ConnectionError:
        print("❌ Cannot connect to Redis. Is Redis running on localhost:6379?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    main()
