# Beast Mailbox Core

Redis-backed mailbox utilities extracted from Beast Mode.

## Features
- Durable messaging via Redis streams (`XADD`/`XREADGROUP`)
- Consumer groups per agent ID
- Async handler registration for inbound messages
- Simple CLI entry points (`beast-mailbox-service`, `beast-mailbox-send`)
- One-shot message inspection with optional acknowledge/trim operations

## Installation

```bash
pip install beast-mailbox-core
```

## Quickstart

### Start a streaming listener

```bash
# Start a long-running listener for agent "herbert"
BEAST_MODE_PROMETHEUS_ENABLED=false beast-mailbox-service herbert \
  --redis-host 192.168.1.119 --redis-password beastmode2025 --echo
```

### Send messages

```bash
# Send a simple text message from devbox to herbert
beast-mailbox-send devbox herbert --message "ping"

# Send structured JSON payload
beast-mailbox-send devbox herbert --json '{"task": "sync", "priority": "high"}' \
  --message-type task_update
```

## One-Shot Message Inspection

### Read-only inspection (default)

```bash
# View the latest message without consuming it
beast-mailbox-service devbox --latest --count 1 \
  --redis-host vonnegut --redis-password beastmode2025

# View the 5 most recent messages
beast-mailbox-service devbox --latest --count 5 \
  --redis-host vonnegut --redis-password beastmode2025 --verbose
```

### Acknowledge messages (semi-destructive)

⚠️ **Warning:** Marks messages as acknowledged in the consumer group, preventing redelivery.

```bash
# View and acknowledge the latest 5 messages
beast-mailbox-service devbox --latest --count 5 --ack \
  --redis-host vonnegut --redis-password beastmode2025
```

Output:
```
📬 devbox <- alice (direct_message) [1234567890-0]: {'text': 'Hello'}
✓ Acknowledged 5 message(s) in group devbox:group
```

### Trim messages (destructive)

⚠️ **Warning:** Permanently deletes messages from the stream. **Cannot be undone.**

```bash
# View and delete the latest 5 messages
beast-mailbox-service devbox --latest --count 5 --trim \
  --redis-host vonnegut --redis-password beastmode2025
```

Output:
```
📬 devbox <- alice (direct_message) [1234567890-0]: {'text': 'Hello'}
🗑️  Deleted 5 message(s) from stream
```

### Combined acknowledge and trim (common cleanup pattern)

```bash
# View, acknowledge, and delete messages in one operation
beast-mailbox-service devbox --latest --count 10 --ack --trim \
  --redis-host vonnegut --redis-password beastmode2025 --verbose
```

## CLI Options Reference

### `beast-mailbox-service <agent_id> [options]`

**Positional Arguments:**
- `agent_id` - Unique identifier for this mailbox (e.g., `devbox`, `poe`, `herbert`)

**Connection Options:**
- `--redis-host HOST` - Redis server host (default: `localhost`)
- `--redis-port PORT` - Redis server port (default: `6379`)
- `--redis-password PASSWORD` - Redis authentication password
- `--redis-db DB` - Redis database index (default: `0`)

**Operation Modes:**
- `--latest` - One-shot mode: fetch latest messages and exit (default: streaming mode)
- `--count N` - Number of messages to fetch in one-shot mode (default: `1`)

**Destructive Operations (require `--latest`):**
- `--ack` - Acknowledge messages after displaying them
- `--trim` - Delete messages after displaying them (implies acknowledgement)

**Other Options:**
- `--poll-interval SECONDS` - Seconds between stream polls in streaming mode (default: `2.0`)
- `--verbose` - Enable debug logging
- `--echo` - (deprecated, use `--verbose`)

### `beast-mailbox-send <sender> <recipient> [options]`

**Positional Arguments:**
- `sender` - Agent ID sending the message
- `recipient` - Agent ID receiving the message

**Message Options:**
- `--message TEXT` - Plain text message
- `--json JSON` - JSON payload
- `--message-type TYPE` - Message type classification (default: `direct_message`)

**Connection Options:** (same as `beast-mailbox-service`)

## Best Practices

### Safety Guidelines

1. **Always start with read-only inspection:**
   ```bash
   beast-mailbox-service myagent --latest --count 5
   ```

2. **Use `--count` to limit destructive operations:**
   Don't accidentally delete hundreds of messages - specify a reasonable count.

3. **Enable `--verbose` for audit trails:**
   See exactly what was acknowledged/deleted with timestamps and message IDs.

4. **`--ack` is safer than `--trim`:**
   Acknowledgement prevents redelivery but keeps messages in the stream for debugging.

5. **Back up before trimming in production:**
   Use `redis-cli DUMP beast:mailbox:<agent>:in` to export the stream first.

6. **Check exit codes in automation:**
   - Exit code `0` = success
   - Non-zero = failure (check stderr for details)

### Error Handling

- Partial failures (e.g., network interruption) are reported clearly
- Acknowledgement failures prevent trimming to avoid data loss
- Consumer group creation errors are handled gracefully (BUSYGROUP)

## Environment Notes

This package disables the heavy observability hooks by default. You still need a Redis
instance accessible to all nodes. If you run alongside the full Beast Mode
stack, simply point to the same Redis host.

Set `BEAST_MODE_PROMETHEUS_ENABLED=false` to explicitly disable metrics collection.

## Troubleshooting

**Messages not appearing:**
- Verify Redis connection with `redis-cli -h <host> -a <password> ping`
- Check the stream exists: `redis-cli -h <host> XLEN beast:mailbox:<agent>:in`
- Ensure agent IDs match (sender → recipient)

**Consumer group errors:**
- "BUSYGROUP" errors are normal and handled automatically
- Group names are `<agent_id>:group` format

**Blocking in tests:**
- See `.kiro/steering/testing-patterns.md` for guidance on mocking ReflectiveModule

## Version History

### 0.2.0 (2025-10-10)
- Added `--ack` flag for acknowledging messages after inspection
- Added `--trim` flag for deleting messages from the stream
- Comprehensive test suite (21 tests, all passing)
- Enhanced error handling for partial failures
- Clear logging with emoji indicators

### 0.1.0 (Initial release)
- Basic streaming mailbox service
- One-shot message inspection
- Message sending utility

