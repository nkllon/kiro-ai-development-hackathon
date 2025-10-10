## Task: provide system info from poe

### Context & Preconditions
- Execute all steps on the **Poe host** (SSH in first if you are remote).
- Ensure the `beast-mailbox-core` CLI tools are installed and available on Poe.
- Confirm access to Redis at `192.168.1.119` with password `beastmode2025`.

### instruction for poe agent
- ssh into poe if not already there
- run `uname -a` and `uptime`
- send the combined output back to devbox via the mailbox using:
  ```bash
  beast-mailbox-send poe devbox --json '{"uname": "<output>", "uptime": "<output>"}' \
    --redis-host 192.168.1.119 --redis-password beastmode2025
  ```

### note
- This message was initiated by `devbox`.
- Use the existing mailbox service running on poe.
- After completing the task, move this prompt to `prompts/completed/`.
