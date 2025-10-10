## Task: Implement One-Shot Mailbox Acknowledge & Trim

### Goal
Extend the Beast Mailbox Service one-shot inspector to optionally acknowledge and/or trim the messages it displays, satisfying requirement R2.1 in `.kiro/specs/beast-mailbox-service/requirements.md`.

### Context
- Work in this repository on host **herbert** (local checkout already present).
- Features touch `scripts/run_mailbox_service.py`, `packages/beast-mailbox-core`, and `src/beast_mode/messaging`.
- Preserve current non-destructive default behaviour; new flags must be opt-in.

### Steps
1. Review the spec (`.kiro/specs/beast-mailbox-service/requirements.md`) and design (`.kiro/specs/beast-mailbox-service/design.md`) to confirm acceptance criteria.
2. Update the one-shot CLI (`scripts/run_mailbox_service.py --latest`) to accept flags such as `--ack` and `--trim` (or an equivalent clear naming). Ensure:
   - Message IDs from `xrevrange` are captured.
   - When `--ack` is set, acknowledge the displayed IDs via `xack`.
   - When `--trim` is set, prune the stream entries (e.g., `xdel` or `xtrim`) after acknowledgement.
   - Logging clearly reports what was acknowledged/trimmed and how many entries were affected.
   - Errors in ack/trim are surfaced without leaving Redis in a confusing state.
3. Mirror the new options in the packaged CLI (`packages/beast-mailbox-core` entry point) so external installs behave the same.
4. Update any shared helpers in `src/beast_mode/messaging` if needed to avoid duplication.
5. Add or update documentation strings/help text for the new flags.
6. Run `python scripts/run_mailbox_service.py devbox --latest --count 1 --ack --redis-host vonnegut --redis-password beastmode2025 --verbose` against Vonnegut (or a local Redis stub if safer) to validate functionality.

### Deliverables
- Code changes implementing the new flags in both repo scripts and packaged CLI.
- Logging output captured in notes showing a successful run with acknowledgements (include message IDs).
- Summary of manual testing commands executed.

### Notes
- Keep all work within this repository; do not push or commit—just deliver diffs/output.
- Downstream tasks (`add-mailbox-cli-tests.md`, `update-mailbox-docs-packaging.md`, `enhance-mailbox-cli-ux.md`) rely on this feature being finished.
- When the task is complete, move this file to `prompts/completed/`.
- Ensure the feature remains non-destructive unless explicit flags are passed.
