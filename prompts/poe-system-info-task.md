## Task: collect system info on Poe

### Context & Preconditions
- Execute this entire prompt on the **Poe host** (SSH in if necessary).
- Ensure the `beast-mailbox-core` CLI is installed on Poe and accessible in the PATH.
- Confirm you can reach Redis at `192.168.1.119` with password `beastmode2025`.

### Instruction Sequence
1. ssh to poe (if not already on the host).
2. Run the following commands:
   ```bash
   uname -a
   uptime
   df -h
   ```
3. Send the combined output back to devbox via the mailbox:
   ```bash
   beast-mailbox-send poe devbox --json '{"uname": "<uname output>", "uptime": "<uptime output>", "df": "<df output>"}' \
     --redis-host 192.168.1.119 --redis-password beastmode2025
   ```

### Notes
- Include the command output as JSON values.
- This message is initiated by devbox (running on Herbert).
- Ignore prior confusion about host identity; the instructions above are self-contained.
- When finished, move this prompt to `prompts/completed/`.
