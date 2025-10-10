## Task: Add Tests for One-Shot Mailbox Inspector

### Goal
Create automated tests covering the Beast Mailbox Service one-shot inspector, including the new acknowledge/trim behaviour, to close tasks T1/T2 in `.kiro/specs/beast-mailbox-service/tasks.md`.

### Context & Preconditions
- Run on host **herbert** with this repository.
- **Do not start** unless the ack/trim flags from `prompts/implement-mailbox-ack-trim.md` have been completed and the code is available locally (verify `scripts/run_mailbox_service.py --latest --ack` exists and works).
- Tests should live under `tests/` (prefer `tests/unit/beast_mode/messaging/` or similar) and mirror the spec’s expectations.
- You may use a lightweight Redis fixture (e.g., `fakeredis` or a local Redis instance); avoid network calls to production if possible.

### Steps
1. Review the design/requirements for expected CLI behaviour (`.kiro/specs/beast-mailbox-service/`).
2. Decide on the testing approach:
   - Preferred: use `redis.asyncio` with `fakeredis` to simulate streams.
   - Alternate: spin up a temporary Redis container via pytest fixtures if sandbox allows.
3. Write tests that cover:
   - Baseline `--latest` read-only mode (ensuring payload decoding works with byte and str fields).
   - `--ack` flag acknowledging the returned message IDs.
   - `--trim` (or chosen destructive flag) removing the entries after acknowledgement.
   - Error handling when ack/trim operations fail (mock or simulate failure to assert logging/exit behaviour).
4. Integrate the tests into the existing suite (pytest). Update `requirements-dev.txt` if new test dependencies are required.
5. Run `make dev-test` (or targeted pytest command) and capture results.

### Deliverables
- New/updated test files under `tests/` exercising the one-shot inspector.
- Any fixture or helper modules added for Redis simulation.
- Command output from the test run proving the suite passes.

### Notes
- Keep dependencies minimal; prefer in-memory solutions.
- Do not commit—return diffs and test logs only.
- Move this prompt to `prompts/completed/` once the tests are implemented and validated.
