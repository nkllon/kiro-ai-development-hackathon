## Task: Enhance Mailbox CLI UX Summary (Optional)

### Goal
Improve the one-shot mailbox inspector’s output with a summary table and optional `--dry-run` support, as outlined in task T4 of `.kiro/specs/beast-mailbox-service/tasks.md`.

### Context & Preconditions
- Execute on host **herbert** within this repository.
- **Start only after** the ack/trim feature from `prompts/implement-mailbox-ack-trim.md` is complete and available locally.
- Preferably run after the test task (`prompts/add-mailbox-cli-tests.md`) so new UX behaviour can be covered by follow-up tests; coordinate with the test owner if simultaneous changes are required.

### Steps
1. Review existing CLI behaviour and logging in `scripts/run_mailbox_service.py` and packaged counterparts.
2. Add a summary section that reports:
   - Number of messages read.
   - Number acknowledged and/or trimmed (when those flags are used).
   - Remaining stream length if easily available (optional but useful).
3. Introduce a `--dry-run` flag that prevents destructive actions while still showing what would happen.
4. Update help text and documentation strings accordingly; ensure flags interact predictably (e.g., `--dry-run` overrides `--ack/--trim`).
5. Validate the behaviour locally by invoking the CLI with combinations of flags, capturing sample output.

### Deliverables
- Updated CLI code reflecting the new UX features.
- Sample terminal output demonstrating summary/dry-run behaviour.
- Notes highlighting any interaction caveats discovered during testing.

### Notes
- If `--dry-run` conflicts with other flags, document the precedence clearly in code comments/log output.
- Coordinate with documentation task owners so the new options are documented once implemented.
- When enhancements are complete and validated, move this prompt to `prompts/completed/`.
