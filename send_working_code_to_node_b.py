#!/usr/bin/env python3
"""
Send the actual working code to Node B via Beast Mode network
"""
import asyncio
import json
import uuid
from datetime import datetime
import redis.asyncio as redis

async def send_working_code():
    client = redis.from_url("redis://:beastmode2025@192.168.1.119:6379")

    # Read the fixed code
    with open('simple_node_b_spore.py', 'r') as f:
        working_code = f.read()

    message = {
        "id": str(uuid.uuid4()),
        "type": "prompt_request",
        "source": "claude-code-node-a",
        "target": None,
        "payload": {
            "prompt": f"""🔧 WORKING NODE B CODE - COPY AND PASTE THIS:

Here's the FIXED version of your spore that won't block:

```python
{working_code}
```

KEY FIXES:
1. Line 105: Uses `asyncio.wait_for()` with timeout instead of infinite blocking
2. Added message limits (max 20 messages)
3. Added timeout limits (10 consecutive timeouts = exit)
4. Added collaboration request handler
5. Proper error handling and cleanup

JUST COPY THE CODE ABOVE AND RUN IT - it will work properly and respond to collaboration requests!""",
            "action_required": "copy_and_run_code",
            "priority": 9
        },
        "timestamp": datetime.now().isoformat(),
        "priority": 9
    }

    await client.publish("beast_mode_network", json.dumps(message))
    print("📤 Sent working code directly to Node B")
    print("💾 Node B can now copy/paste the fixed code")
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(send_working_code())