#!/usr/bin/env python3
"""
Send Workloads to Vonnegut Containers
====================================
"""

import asyncio
import json
import redis
import sys
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from src.security.secure_credentials import get_redis_password


async def send_workload(task_description: str, task_data: dict = None):
    """Send a workload to Vonnegut containers."""
    
    # Connect to Redis
    redis_client = redis.Redis(
        host="192.168.1.119",
        port=6379,
        password=get_redis_password(),
        decode_responses=True
    )
    
    workload_id = str(uuid.uuid4())[:8]
    
    workload_request = {
        "type": "workload_request",
        "workload_id": workload_id,
        "sender": "workload-dispatcher",
        "timestamp": datetime.now().isoformat(),
        "task": {
            "description": task_description,
            "data": task_data or {},
            "priority": "normal"
        }
    }
    
    print(f"📤 Sending workload {workload_id}: {task_description}")
    redis_client.publish("docker_workloads", json.dumps(workload_request))
    
    # Listen for completion
    pubsub = redis_client.pubsub()
    pubsub.subscribe("beast_mode_network")
    
    print(f"👂 Waiting for workload completion...")
    
    for i in range(30):  # 30 second timeout
        message = pubsub.get_message(timeout=1.0)
        if message and message['type'] == 'message':
            data = json.loads(message['data'])
            if (data.get('type') == 'workload_complete' and 
                data.get('workload_id') == workload_id):
                print(f"✅ Workload completed: {data.get('message')}")
                break
        await asyncio.sleep(1)
    else:
        print("⏰ Workload completion timeout")
    
    pubsub.close()
    redis_client.close()


if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Test workload execution"
    asyncio.run(send_workload(task))
