## Task: Read Messages from Beast Mailbox on Poe

### Context & Preconditions
- Execute this prompt **on the Poe host** (the scripts and environment live there).
- `beast-mailbox-core` must already be installed with its CLI scripts available (see `install-mailbox-service-on-poe.md`).
- Ensure network access to Redis at `192.168.1.119` with password `beastmode2025`.

### Your Agent ID
Your agent ID is: **poe**

### Available Tools

You have the `beast-mailbox-core` package installed with two CLI tools:

1. **beast-mailbox-service**: Runs a persistent listener (already running or can be started)
2. **beast-mailbox-send**: Sends messages to other agents

### Task: Read Messages from Your Mailbox

#### Option 1: Check What's in the Stream Directly (Using Redis CLI)

```bash
# View recent messages in your inbox stream
redis-cli -h 192.168.1.119 -a beastmode2025 \
  XREAD COUNT 10 STREAMS beast:mailbox:poe:in 0

# View messages starting from a specific ID
redis-cli -h 192.168.1.119 -a beastmode2025 \
  XREAD COUNT 10 STREAMS beast:mailbox:poe:in <message-id>

# View consumer group info
redis-cli -h 192.168.1.119 -a beastmode2025 \
  XINFO GROUPS beast:mailbox:poe:in

# View pending (unacknowledged) messages
redis-cli -h 192.168.1.119 -a beastmode2025 \
  XPENDING beast:mailbox:poe:in poe:group
```

#### Option 2: Start the Mailbox Service (Recommended)

This will actively listen for messages and print them as they arrive:

```bash
# Set environment variable to disable Prometheus
export BEAST_MODE_PROMETHEUS_ENABLED=false

# Start the mailbox service with echo mode
~/.local/bin/beast-mailbox-service poe \
  --redis-host 192.168.1.119 \
  --redis-password beastmode2025 \
  --echo \
  --verbose
```

**What this does**:
- Connects to Redis at 192.168.1.119
- Creates/joins consumer group `poe:group` for stream `beast:mailbox:poe:in`
- Continuously polls for new messages every 2 seconds
- Prints received messages in format: `📬 poe <- <sender> (<type>): <payload>`
- Press Ctrl+C to stop

#### Option 3: Run Service with Custom Handler (Python)

If you want to process messages programmatically:

```python
import asyncio
import logging
from beast_mailbox_core.redis_mailbox import MailboxConfig, RedisMailboxService

logging.basicConfig(level=logging.INFO)

async def main():
    # Configure connection to Redis
    config = MailboxConfig(
        host="192.168.1.119",
        password="beastmode2025",
        stream_prefix="beast:mailbox",
        poll_interval=2.0
    )

    # Create service for agent "poe"
    service = RedisMailboxService(agent_id="poe", config=config)

    # Define a custom message handler
    async def handle_message(message):
        print(f"📬 Received message:")
        print(f"   From: {message.sender}")
        print(f"   To: {message.recipient}")
        print(f"   Type: {message.message_type}")
        print(f"   Payload: {message.payload}")
        print(f"   Timestamp: {message.timestamp}")
        print()

        # Your custom logic here
        # e.g., respond to the sender:
        if message.payload.get("message") == "ping":
            await service.send_message(
                recipient=message.sender,
                payload={"message": "pong"},
                message_type="response"
            )

    # Register the handler
    service.register_handler(handle_message)

    # Start the service
    if not await service.start():
        print("Failed to start mailbox service")
        return

    print("Mailbox service started. Listening for messages...")
    print("Press Ctrl+C to stop")

    try:
        # Keep running until interrupted
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nStopping service...")
    finally:
        await service.stop()
        print("Service stopped")

# Run the async main function
asyncio.run(main())
```

Save this as `check_mailbox.py` and run:
```bash
python3 check_mailbox.py
```

### Expected Output

When messages arrive, you should see output like:

```
2025-10-10 09:02:10,123 INFO root:📬 poe <- herbert (direct_message): {'message': 'Hello from herbert!'}
2025-10-10 09:02:15,456 INFO root:📬 poe <- devbox (direct_message): {'message': 'test'}
```

### Testing: Send Yourself a Message

To test that your mailbox is working, send yourself a test message:

```bash
~/.local/bin/beast-mailbox-send poe poe \
  --message "Self-test message" \
  --redis-host 192.168.1.119 \
  --redis-password beastmode2025
```

You should see it appear in the listener output immediately.

### Configuration Details

- **Redis Host**: 192.168.1.119
- **Redis Port**: 6379 (default)
- **Redis Password**: beastmode2025
- **Your Inbox Stream**: `beast:mailbox:poe:in`
- **Consumer Group**: `poe:group`
- **Poll Interval**: 2.0 seconds

### Troubleshooting

**If you don't see messages**:

1. Check the service is running:
   ```bash
   ps aux | grep beast-mailbox-service
   ```

2. Check if messages are in the stream:
   ```bash
   redis-cli -h 192.168.1.119 -a beastmode2025 \
     XLEN beast:mailbox:poe:in
   ```

3. Check consumer group status:
   ```bash
   redis-cli -h 192.168.1.119 -a beastmode2025 \
     XINFO GROUPS beast:mailbox:poe:in
   ```

4. Verify Redis connectivity:
   ```bash
   nc -zv 192.168.1.119 6379
   ```

**If service fails to start**:

1. Make sure BEAST_MODE_PROMETHEUS_ENABLED is set to false:
   ```bash
   export BEAST_MODE_PROMETHEUS_ENABLED=false
   ```

2. Check if the package is installed:
   ```bash
   python3 -c "import beast_mailbox_core; print('Installed')"
   ```

3. Use full Python path if needed:
   ```bash
   python3 -m beast_mailbox_core.cli poe \
     --redis-host 192.168.1.119 \
     --redis-password beastmode2025 \
     --echo
   ```

### Running Persistently

To keep the service running in the background:

**Using the startup script**:
```bash
nohup ~/start-mailbox-poe.sh > /tmp/mailbox-poe.log 2>&1 &
```

**Using systemd** (if configured):
```bash
sudo systemctl start beast-mailbox-poe
sudo journalctl -u beast-mailbox-poe -f
```

### Next Steps

Once you can successfully read messages:

1. Consider what types of messages you want to handle
2. Implement handlers for different message types
3. Set up automatic responses or actions based on incoming messages
4. Integrate with your existing workflows or tools

### Security Note

The Redis password (`beastmode2025`) is shared across all agents. Keep your mailbox service running only on trusted hosts within your internal network.

---

**Quick Reference**:
- Read messages: `redis-cli -h 192.168.1.119 -a beastmode2025 XREAD COUNT 10 STREAMS beast:mailbox:poe:in 0`
- Start listener: `BEAST_MODE_PROMETHEUS_ENABLED=false ~/.local/bin/beast-mailbox-service poe --redis-host 192.168.1.119 --redis-password beastmode2025 --echo`
- Send test: `~/.local/bin/beast-mailbox-send poe poe --message "test" --redis-host 192.168.1.119 --redis-password beastmode2025`

### Completion
- After you’ve retrieved and confirmed mailbox messages, move this prompt into `prompts/completed/`.
