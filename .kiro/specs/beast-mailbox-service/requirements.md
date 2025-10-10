# Beast Mailbox Service Requirements

## Overview

The Beast Mailbox Service provides durable, Redis-backed message delivery between Beast Mode agents (e.g. Devbox, Poe, Herbert). It covers the Python package (`beast-mailbox-core`), console entry points, and operational scripts that ship with this repository.

**Single Responsibility:** Deliver and inspect agent-to-agent messages over the shared Redis mailbox network.

**Relevant Components:**
- `src/beast_mode/messaging/redis_mailbox.py`
- `src/beast_mode/messaging/redis_foundation.py`
- `scripts/run_mailbox_service.py`
- `scripts/send_mailbox_message.py`
- `packages/beast-mailbox-core`

## Functional Requirements

### R1: Streaming Mailbox Consumer
**User Story:** As an operator, I need to run a long-lived mailbox listener for a specific agent so incoming messages are processed continuously.

**Acceptance Criteria:**
- [ ] CLI exposes `python scripts/run_mailbox_service.py <agent>` (and packaged console script) that connects to Redis, creates a consumer group, and logs each message as it arrives.
- [ ] Service supports graceful shutdown (Ctrl-C) and reconnects to Redis when needed.
- [ ] Handlers can be registered to process messages asynchronously.

### R2: One-Shot Latest Message Retrieval
**User Story:** As an operator, I want to quickly inspect the latest messages in an agent’s mailbox without leaving a blocking process running.

**Acceptance Criteria:**
- [ ] CLI flag `--latest` queries the agent’s `beast:mailbox:<agent>:in` stream and exits immediately.
- [ ] Optional `--count` parameter controls the number of most recent messages returned.
- [ ] Output includes sender, recipient, message type, message ID, and decoded payload.
- [ ] Works with the same Redis configuration flow as the streaming consumer (environment variables, CLI overrides).

### R2.1: Optional Acknowledge & Trim
**User Story:** As an operator, after reviewing the most recent messages via the one-shot mode, I want to optionally acknowledge and/or trim them so the mailbox stays tidy.

**Acceptance Criteria:**
- [ ] One-shot CLI exposes flags (e.g., `--ack`, `--trim`) that acknowledge or remove the viewed entries when explicitly requested.
- [ ] Defaults remain non-destructive; acknowledgement/trim must be opt-in.
- [ ] Command outputs clearly indicate when messages were acknowledged or trimmed, including counts.
- [ ] Error handling covers partial ack/delete failures without leaving the CLI in an inconsistent state.

### R3: Message Sending Utility
**User Story:** As an operator, I need to send ad hoc messages between agents for testing or orchestration.

**Acceptance Criteria:**
- [ ] `scripts/send_mailbox_message.py` (and packaged console script) publishes to `beast:mailbox:<recipient>:in`.
- [ ] Supports plain text (`--message`) and JSON payloads (`--json`).
- [ ] Allows setting `--message-type` and reuses the shared Redis host/port/password conventions.

### R4: Packaging & Distribution
**User Story:** As a developer, I want to install the mailbox tooling with `pip install` and gain the same functionality as the scripts in this repository.

**Acceptance Criteria:**
- [ ] `packages/beast-mailbox-core` builds successfully (editable and wheel) with console entry points for streaming consumer and send utility.
- [ ] Installation registers the scripts in `pyproject.toml` so `beast-mailbox-service` and `beast-mailbox-send` are available after `pip install -e .`.
- [ ] Package declares Redis dependencies (`redis>=5`), Prometheus optional metrics, and development extras for tests/linting.

### R5: Configuration Handling
**User Story:** As an operator, I must be able to target the shared Vonnegut Redis cluster without code changes.

**Acceptance Criteria:**
- [ ] Services respect `REDIS_HOST`, `REDIS_PORT`, and `REDIS_PASSWORD` environment variables, with CLI overrides.
- [ ] Reflective module auto-registration resolves hostnames correctly for host and container contexts.
- [ ] Graceful degradation paths exist when Redis is unreachable (logged warnings, non-zero exit).

### R6: Reflective Module Compliance
**User Story:** As a platform engineer, I need mailbox modules to participate in the unified reflective-module ecosystem for governance and monitoring.

**Acceptance Criteria:**
- [ ] `RedisMailboxService` and `RedisFoundation` expose `get_module_info`, `get_capabilities`, `get_health_status`, and `graceful_degradation` per the unified interface.
- [ ] Modules register themselves with Redis (auto-registration heartbeat) unless explicitly disabled.
- [ ] Health reporting distinguishes connected vs degraded states and surfaces issues in logs/metadata.

## Non-Functional Requirements

### N1: Reliability
- Mailbox consumer must acknowledge messages only after handlers run successfully.
- Redis connection failures trigger retries/backoff without crashing immediately.

### N2: Observability
- Prometheus metrics hooks remain optional but detectable; lack of `prometheus-client` should not block execution (warning only).
- Logging includes agent ID, message IDs, and payload highlights for auditing.

### N3: Compatibility
- Python 3.9–3.12 supported (per `pyproject.toml`).
- Works with Redis 6+ and Vonnegut cluster default configuration.

## Open Questions
- Do we need a CLI wrapper for bulk message export/import?

## References
- `docs/operational-workflows/beast-mailbox-network.md` (operational guide).
- `packages/beast-mailbox-core/pyproject.toml`.
