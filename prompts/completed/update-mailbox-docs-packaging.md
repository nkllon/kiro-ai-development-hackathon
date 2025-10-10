## Task: Document and Package Mailbox Ack/Trim Workflow

### Goal
Update documentation and packaging assets so the new mailbox acknowledgement/trim functionality is discoverable for both repo users and external package consumers.

### Context & Preconditions
- Work on host **herbert** within this repository.
- **Begin only after** the ack/trim implementation task (`prompts/implement-mailbox-ack-trim.md`) is complete and merged locally, so the documentation reflects actual behaviour.
- Relevant files: `docs/operational-workflows/beast-mailbox-network.md`, package README under `packages/beast-mailbox-core/README.md` (create if missing), and `packages/beast-mailbox-core/pyproject.toml` for metadata/versioning.

### Steps
1. Review the updated specs (`.kiro/specs/beast-mailbox-service/requirements.md`) to ensure documentation aligns with the requirements.
2. Update the operational workflow doc to include:
   - Example commands using `--latest --ack` / `--trim`.
   - Warnings about destructive operations and best practices (e.g., dry runs, backups).
3. Ensure the packaged README (create or expand) documents the same CLI options and usage examples.
4. Bump the package version in `packages/beast-mailbox-core/pyproject.toml` to reflect the new feature, noting the change in the README or an existing changelog if present.
5. If applicable, add release notes or entry to `docs/recent-updates` summarising the change.
6. Provide a brief verification section demonstrating commands run to validate docs (e.g., `pip install -e .` if necessary).

### Deliverables
- Updated documentation files referencing the new ack/trim workflow.
- Revised package metadata/version.
- Summary note of commands used to verify the documentation (no need for screenshots).

### Notes
- Maintain consistent tone/style with existing docs.
- Coordinate versioning with any pending code changes from the ack/trim task.
- After completing the documentation and packaging updates, move this prompt to `prompts/completed/`.
