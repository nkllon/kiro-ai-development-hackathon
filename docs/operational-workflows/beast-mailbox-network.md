# Beast Mode Mailbox Network

This guide explains how to run the Redis-backed mailbox service across nodes (e.g. local dev machine, Herbert, Poe) so agents can exchange messages reliably.

## Components
- `scripts/run_mailbox_service.py` — starts a long-running listener for an agent ID.
- `scripts/send_mailbox_message.py` — sends a single message to another agent's mailbox.
- `src/beast_mode/messaging/redis_mailbox.py` — reusable library built on `RedisFoundation` (streams + consumer groups).

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

## 5. Next steps
- Integrate mailbox handlers with agent workflows (conversion to `BeastModeMessage` etc.).
- Add monitoring via `redis-cli xlen beast:mailbox:<agent>:in` to verify queue size stays manageable.
- Extend `send_mailbox_message.py` to broadcast or fan out to multiple recipients if needed.
