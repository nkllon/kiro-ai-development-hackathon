## Task: Build Poe Mailbox Instance

### Context & Preconditions
- You are running directly on the **Poe host**.
- `beast-mailbox-core` is already installed (`pip install beast-mailbox-core`).
- You have network access to the shared Redis (`vonnegut`, password `beastmode2025`).
- This task focuses on setting up Poe’s workspace from the GitHub repository and wiring it into the existing mailbox infrastructure.

### Goals
1. Pull the latest `beast-mailbox-core` repository from GitHub.
2. Configure the local workspace for Poe’s agent code/workflows.
3. Ensure the installed CLI matches the repository state (optional verification).
4. Prepare a clean environment so Poe can develop and run mailbox-based tasks.

### Steps
1. **Clone the repository** (if not already present):
   ```bash
   git clone https://github.com/nkllon/beast-mailbox-core.git ~/beast-mailbox-core
   cd ~/beast-mailbox-core
   ```

2. **Check the repository status**:
   ```bash
   git status
   git log -1
   ```
   Ensure you are on the latest main branch (or the branch that matches your workflow).

3. **Verify the installed package version** (optional sanity check):
   ```bash
   beast-mailbox-service --version
   ```
   Confirm it reports `0.2.0` (or whichever version is currently published).

4. **Concrete setup steps for Poe’s instance**:
   - Create or update a workspace directory for Poe’s agent tasks (e.g., `~/poe-agent`).
   - If you maintain notebooks/scripts, pull or copy them into this workspace.
   - Set environment variables in Poe’s shell profile (if not already set):
     ```bash
     export REDIS_HOST=vonnegut
     export REDIS_PASSWORD=beastmode2025
     export BEAST_MODE_PROMETHEUS_ENABLED=false
     ```
   - Optionally create helper scripts (e.g., `start-poe-mailbox.sh`) that wrap the CLI command:
     ```bash
     #!/usr/bin/env bash
     beast-mailbox-service poe --redis-host "$REDIS_HOST" --redis-password "$REDIS_PASSWORD" --verbose
     ```

5. **Run a quick validation** (optional but recommended):
   ```bash
   beast-mailbox-service poe --latest --count 1 --verbose
   ```
   Ensure the CLI can reach Vonnegut and display recent messages.

6. **Document the setup**:
   - Update any local README or notes with installation steps.
   - Record any custom scripts or cron jobs you set up for Poe.

### Deliverables
- Cloned repository on Poe (`~/beast-mailbox-core`).
- Configured workspace/environment ready for development.
- Optional log/output from validation commands.

### Completion
- When all steps are complete, move this file to `prompts/completed/poe/` (or remove it if that directory doesn’t exist).
