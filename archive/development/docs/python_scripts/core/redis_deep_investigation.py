#!/usr/bin/env python3
"""
Deep investigation of Redis to find where the agents actually are
"""

import redis
import json
import time
from datetime import datetime


def investigate_redis_thoroughly():
    """Thoroughly investigate Redis to find the agents"""
    print("🔍 **DEEP REDIS INVESTIGATION**")
    print("=" * 50)

    r = redis.Redis(host="localhost", port=6379, decode_responses=False)

    # 1. Check all Redis databases (0-15 by default)
    print("🗄️  **CHECKING ALL REDIS DATABASES**")
    for db_num in range(16):
        try:
            db_redis = redis.Redis(
                host="localhost", port=6379, db=db_num, decode_responses=False
            )
            db_redis.ping()

            # Get database info
            info = db_redis.info("keyspace")
            if f"db{db_num}" in info:
                db_info = info[f"db{db_num}"]
                keys_count = db_info["keys"]
                print(f"  📊 Database {db_num}: {keys_count} keys")

                # Sample some keys
                keys = db_redis.keys("*")[:10]  # First 10 keys
                for key in keys:
                    try:
                        key_type = db_redis.type(key).decode("utf-8")
                        key_name = key.decode("utf-8")
                        print(f"    └─ {key_name} ({key_type})")
                    except:
                        pass
            else:
                print(f"  ⚪ Database {db_num}: empty")

        except Exception as e:
            print(f"  ❌ Database {db_num}: error - {e}")

    print()

    # 2. Check what the connected clients are actually subscribed to
    print("🎧 **ANALYZING CLIENT SUBSCRIPTIONS**")
    try:
        clients = r.client_list()
        for i, client in enumerate(clients):
            client_id = client.get("id", "unknown")
            client_name = client.get("name", "unnamed")
            last_cmd = client.get("cmd", "none")

            print(f"  Client {i+1} (ID: {client_id}):")
            print(f"    Name: {client_name}")
            print(f"    Last command: {last_cmd}")

            # If it's a subscription client, try to get more info
            if "subscribe" in last_cmd.lower():
                print(f"    🎧 This client is subscribed to channels")
    except Exception as e:
        print(f"❌ Error analyzing clients: {e}")

    print()

    # 3. Check for any pattern-based subscriptions
    print("📡 **CHECKING FOR PATTERN SUBSCRIPTIONS**")
    try:
        # Try to find what patterns might be subscribed
        patterns_to_check = [
            "beast*",
            "agent*",
            "collaboration*",
            "spore*",
            "tidb*",
            "network*",
        ]

        for pattern in patterns_to_check:
            try:
                # This is tricky - we can't directly query pattern subscriptions
                # But we can try publishing to see if anyone is listening
                test_channels = [
                    f"{pattern.replace('*', '_test')}",
                    f"{pattern.replace('*', '_network')}",
                    f"{pattern.replace('*', '_messages')}",
                ]

                for channel in test_channels:
                    result = r.publish(channel, json.dumps({"test": "pattern_check"}))
                    if result > 0:
                        print(
                            f"  📡 Found subscribers on: {channel} ({result} subscribers)"
                        )

            except Exception as e:
                print(f"  ❌ Error checking pattern {pattern}: {e}")

    except Exception as e:
        print(f"❌ Error checking patterns: {e}")

    print()

    # 4. Look for any keys that might indicate agent presence
    print("🔍 **SEARCHING FOR AGENT-RELATED KEYS**")
    try:
        # Search for keys that might indicate agents
        search_patterns = [
            "*agent*",
            "*beast*",
            "*tidb*",
            "*spore*",
            "*collaboration*",
            "*status*",
            "*heartbeat*",
        ]

        for pattern in search_patterns:
            keys = r.keys(pattern)
            if keys:
                print(f"  📋 Pattern '{pattern}': {len(keys)} keys found")
                for key in keys[:5]:  # Show first 5
                    try:
                        key_name = key.decode("utf-8")
                        key_type = r.type(key).decode("utf-8")

                        if key_type == "string":
                            value = r.get(key)
                            if value:
                                try:
                                    decoded = json.loads(value.decode("utf-8"))
                                    print(f"    └─ {key_name}: {decoded}")
                                except:
                                    print(
                                        f"    └─ {key_name}: {value.decode('utf-8')[:100]}..."
                                    )
                        else:
                            print(f"    └─ {key_name} ({key_type})")

                    except Exception as e:
                        print(f"    └─ Error reading key: {e}")
            else:
                print(f"  ⚪ Pattern '{pattern}': no keys found")

    except Exception as e:
        print(f"❌ Error searching keys: {e}")

    print()

    # 5. Monitor Redis for a few seconds to see live activity
    print("👀 **MONITORING LIVE REDIS ACTIVITY**")
    print("Watching for 5 seconds...")

    try:
        # Use Redis MONITOR command to see live activity
        # Note: This is resource intensive, only for debugging
        monitor = r.monitor()
        start_time = time.time()

        activity_count = 0
        while time.time() - start_time < 5:
            try:
                command = next(monitor)
                activity_count += 1

                # Parse the monitor output
                if isinstance(command, dict):
                    cmd_str = command.get("command", "")
                else:
                    cmd_str = str(command)

                # Only show interesting commands
                if any(
                    keyword in cmd_str.lower()
                    for keyword in ["publish", "subscribe", "lpush", "rpop"]
                ):
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"  [{timestamp}] {cmd_str}")

            except StopIteration:
                break
            except Exception as e:
                print(f"  Monitor error: {e}")
                break

        print(f"  📊 Observed {activity_count} Redis operations in 5 seconds")

    except Exception as e:
        print(f"❌ Error monitoring Redis: {e}")


if __name__ == "__main__":
    investigate_redis_thoroughly()
