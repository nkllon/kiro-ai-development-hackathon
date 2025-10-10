# Beast Mailbox Service Design

## Overview
The Beast Mailbox Service provides two complementary interfaces around the shared Redis Streams transport used by Beast Mode agents:

- **Streaming consumer** for long-lived inbox processing, built on async Redis consumer groups (`xreadgroup`).
- **One-shot inspector** for on-demand retrieval of the latest mailbox entries without maintaining a running process (`xrevrange`).
- **Sender utility** for publishing structured messages to any agent’s inbox (`xadd`).

This document captures the implemented architecture, data flow, and operational touchpoints delivered in the current revision.

## Architecture

```text
┌──────────────────────┐        ┌────────────────────────┐
│ scripts/send_mail…  │ xadd -->│ beast:mailbox:<agent>:in │
└──────────┬───────────┘        └──────────┬──────────────┘
           │                                │
           │                                ▼
           │                      ┌──────────────────────┐
           │                      │ RedisMailboxService  │
           │                      │   (consumer group)   │
           │                      └──────────┬───────────┘
           │                                │
           ▼                                ▼
┌──────────────────────┐        ┌────────────────────────┐
│ One-shot inspector  │<--xrevrange--│   Stored messages     │
└──────────────────────┘        └────────────────────────┘
```

Core modules:
- `src/beast_mode/messaging/redis_mailbox.py` implements message structures, async consumer loop, handler dispatch, and one-shot retrieval helpers.
- `src/beast_mode/messaging/redis_foundation.py` wraps connection management, health checks, and reflective-module registration.
- `scripts/run_mailbox_service.py` exposes both streaming and `--latest` modes over CLI.
- `scripts/send_mailbox_message.py` provides a command-line publisher (also wired via console entry points in `packages/beast-mailbox-core`).
- `packages/beast-mailbox-core` packages the same functionality for external installation.

## Data Flow

1. **Sending**
   - CLI/script builds a payload (text or JSON) → `MailboxMessage.to_redis_fields()` → `redis.xadd()` into `beast:mailbox:<recipient>:in` (bounded via `MAXLEN`).
2. **Streaming Consumption**
   - `RedisMailboxService.start()` initialises Redis, ensures consumer group exists, and runs `_consume_loop()` with `xreadgroup`.
   - Each entry is decoded via `MailboxMessage.from_redis_fields()` and dispatched to registered async handlers.
   - Messages are acknowledged (`xack`) after handlers succeed.
3. **One-Shot Inspection**
   - `--latest` mode initialises the same Redis foundation, executes `xrevrange` with configurable count, logs decoded payloads, then shuts down without entering the consume loop.

## Deployment & Configuration

- Redis host/port/password resolve via environment (`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`) with CLI overrides. Auto-registration detects host vs container and adjusts defaults.
- Optional Prometheus metrics integrate through the unified reflective-module infrastructure (warnings only if client missing).
- Packaging (`packages/beast-mailbox-core/pyproject.toml`) exports console scripts matching the repo CLI: `beast-mailbox-service` and `beast-mailbox-send`.

## Extensibility

- Handlers registered on `RedisMailboxService` support custom business logic (e.g., parsing into internal event schemas).
- One-shot inspector provides a foundation for future tools (ack/trim, export) without duplicating connection logic.
- Both CLI paths leverage the same async classes, ensuring behavioural parity between packaged and in-repo tooling.

## Decisions & Rationale

- **Redis Streams**: chosen for durability, consumer groups, and compatibility with the Vonnegut cluster.
- **Async foundation**: `redis.asyncio` enables non-blocking loops suited for long-running agents.
- **Reflective module compliance**: required to meet RDI governance; exposes module metadata and health uniformly and hooks into auto-registration.
- **`--latest` design**: uses `xrevrange` to satisfy quick-inspection requirements while reusing authentication/decoding logic and avoiding side effects.

## Known Follow-Ups

- Add optional acknowledgement/trim workflow for one-shot inspection (tracked in requirements R2.1 and tasks).
- Expand packaging docs to highlight the `--latest` mode and upcoming destructive options.
- Introduce automated tests for one-shot retrieval and future ack/trim behaviour once Redis fixtures are available.
