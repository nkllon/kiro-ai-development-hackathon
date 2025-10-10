# Beast Mailbox Service Tasks

## Implemented (no tasks required)
- R1 streaming consumer loop with async handlers and consumer groups.
- R2 one-shot inspection in read-only mode (`--latest` / `--count`).
- R2.1 one-shot acknowledgement & trim (`--ack` / `--trim` flags).
- R3 mailbox sender utility with text/JSON payload support.
- R4 base packaging and console entry points in `beast-mailbox-core`.
- R5 configuration resolution via env vars/CLI overrides and reflective host detection.
- R6 reflective module registration and health reporting.
- T2 automated tests covering read-only and ack/trim flows (`tests/unit/beast_mode/messaging/test_mailbox_cli.py`).
- T3 documentation & packaging updates (docs/operational workflows, README, version 0.2.0).

## Pending Work

### Backlog (tracked in upstream GitHub project)
- **T4: Optional UX Enhancements** – future improvements such as summary output and a `--dry-run` flag are now tracked in the upstream repository (`nkllon/beast-mailbox-core`). Refer to the corresponding GitHub issue/project card when prioritising this work.
