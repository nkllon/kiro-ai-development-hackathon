## Task: Publish beast-mailbox-core Package

### Goal
Extract the mailbox package from this repo into a dedicated GitHub repository and prepare it for release on PyPI.

### Steps
1. Create a new GitHub repo `nkllon/beast-mailbox-core` with no starter files.
2. From this repo:
   - Copy `packages/beast-mailbox-core/` to a clean directory.
   - Ensure pyproject, README, and CLI entry points match the scaffolding.
3. Initialize git in the new directory, commit, and push to the new GitHub repo.
4. Run `python -m build` and (optionally) `twine upload dist/*` to publish.
5. Update any documentation or README badges in the new repo.

### Notes
- Shared Redis password is `beastmode2025` (documented in README).
- Disable Prometheus instrumentation with `BEAST_MODE_PROMETHEUS_ENABLED=false` when running mailbox scripts in isolation.
