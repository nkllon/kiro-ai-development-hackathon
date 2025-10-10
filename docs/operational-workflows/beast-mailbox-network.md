# Beast Mode Mailbox Network

This guide explains how to run the Redis-backed mailbox service across nodes (e.g. local dev machine, Herbert, Poe) so agents can exchange messages reliably.

## Components
- `scripts/run_mailbox_service.py` — starts a long-running listener for an agent ID.
- `scripts/send_mailbox_message.py` — sends a single message to another agent's mailbox.
- `src/beast_mode/messaging/redis_mailbox.py` — reusable library built on `RedisFoundation` (streams + consumer groups).
- `scripts/run_mailbox_service.py --latest` — one-shot fetch of the newest mailbox entries (no long-running loop).

## 1. Start the mailbox service on each machine
```bash
# Example: run on Poe
python scripts/run_mailbox_service.py poe --redis-host 192.168.1.119 --redis-password beastmode2025

# Example: run on Herbert
python scripts/run_mailbox_service.py herbert --redis-host 192.168.1.119 --redis-password beastmode2025
```
The service logs inbound messages (`📬` entries) and keeps its consumer group active. Use systemd/pm2/launchd to run it persistently.

## 2. Send a message
```bash
python scripts/send_mailbox_message.py devbox poe --message "Hello from devbox" \
  --redis-host 192.168.1.119 --redis-password beastmode2025
```
On Poe's service you'll see:
```
📬 poe <- devbox (direct_message): {'message': 'Hello from devbox'}
```

## 3. Custom payloads
Use `--json` to send structured data:
```bash
python scripts/send_mailbox_message.py herbert poe --json '{"task": "sync", "priority": "high"}' \
  --message-type task_update --redis-host 192.168.1.119 --redis-password beastmode2025
```

## 4. Installation hints
- Ensure Redis is reachable and contains the shared password (`REDIS_PASSWORD=beastmode2025`).
- `make install` already seeds `.env`; re-run with `INSTALL_ARGS="--bootstrap-stack"` if Redis needs to be provisioned.
- Place service invocation into a supervisor (systemd service, launchd plist, etc.) so it restarts automatically on each machine.

## 5. Inspect the latest messages without streaming
Use the one-shot mode to read and print the most recent entries, then exit immediately:
```bash
python scripts/run_mailbox_service.py devbox --latest --count 1 \
  --redis-host vonnegut --redis-password beastmode2025 --verbose
```
- Increase `--count` to view several recent messages.
- The command initialises the same Redis foundation and consumer metadata, ensuring parity with the streaming service while remaining non-blocking.

### 5.1. Acknowledge and trim messages (destructive operations)

⚠️ **Warning:** The `--ack` and `--trim` flags perform destructive operations on your mailbox. Use with caution in production environments.

**Acknowledge messages after viewing:**
```bash
python scripts/run_mailbox_service.py devbox --latest --count 5 --ack \
  --redis-host vonnegut --redis-password beastmode2025
```
This marks the messages as acknowledged in the consumer group, preventing redelivery.

**Delete messages after viewing:**
```bash
python scripts/run_mailbox_service.py devbox --latest --count 5 --trim \
  --redis-host vonnegut --redis-password beastmode2025
```
This permanently deletes the messages from the stream. Cannot be undone.

**Acknowledge AND delete (common cleanup pattern):**
```bash
python scripts/run_mailbox_service.py devbox --latest --count 10 --ack --trim \
  --redis-host vonnegut --redis-password beastmode2025 --verbose
```

**Best practices:**
- Start with `--latest` (read-only) to inspect messages before performing destructive operations
- Use `--count` to limit the scope of operations (don't accidentally delete hundreds of messages)
- Enable `--verbose` to see detailed logging of what was acknowledged/deleted
- Back up important messages before trimming (use `redis-cli DUMP` if needed)
- In production, consider implementing a `--dry-run` flag (see enhancement tasks)
- The `--ack` flag is safer than `--trim` as it only marks messages as processed

**Output indicators:**
- `✓ Acknowledged N message(s)` - Messages were marked as acknowledged
- `🗑️  Deleted N message(s)` - Messages were permanently removed from the stream
- Error messages will clearly indicate if operations failed partially or completely

**Error handling:**
- Partial failures (e.g., Redis connection lost mid-operation) are reported without leaving inconsistent state
- If acknowledgement fails, trimming is skipped to prevent data loss
- Check the exit code: `0` for success, non-zero for failures

## 6. Next steps
- Integrate mailbox handlers with agent workflows (conversion to `BeastModeMessage` etc.).
- Add monitoring via `redis-cli xlen beast:mailbox:<agent>:in` to verify queue size stays manageable.
- Extend `send_mailbox_message.py` to broadcast or fan out to multiple recipients if needed.
