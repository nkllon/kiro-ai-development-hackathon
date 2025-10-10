# Beast Mailbox Core

Redis-backed mailbox utilities extracted from Beast Mode.

## Features
- Durable messaging via Redis streams (`XADD`/`XREADGROUP`)
- Consumer groups per agent ID
- Async handler registration for inbound messages
- Simple CLI entry points (`beast-mailbox-service`, `beast-mailbox-send`)

## Quickstart
```bash
pip install beast-mailbox-core

# start listener for agent "herbert"
BEAST_MODE_PROMETHEUS_ENABLED=false beast-mailbox-service herbert \
  --redis-host 192.168.1.119 --redis-password beastmode2025 --echo

# send a message from devbox
beast-mailbox-send devbox herbert --message "ping"
```

## Environment Notes
This package disables the heavy observability hooks; you still need a Redis
instance accessible to all nodes. If you run alongside the full Beast Mode
stack, simply point to the same Redis host.

