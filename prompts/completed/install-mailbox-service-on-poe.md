## Task: Install Beast Mailbox Service on Poe

### Goal
Install the new `beast-mailbox-core` package on the Poe host and verify that it can send and receive messages via the shared Redis instance.

### Steps
1. SSH into Poe.
2. Install the package (once published to PyPI):
   ```bash
   pip install beast-mailbox-core
   ```
   *(If not yet on PyPI, install from GitHub: `pip install git+https://github.com/nkllon/beast-mailbox-core.git`)*
3. Start a mailbox listener for Poe:
   ```bash
   export BEAST_MODE_PROMETHEUS_ENABLED=false
   beast-mailbox-service poe --redis-host 192.168.1.119 --redis-password beastmode2025 --echo
   ```
4. From another shell (or host), send a test message:
   ```bash
   beast-mailbox-send devbox poe --message "hello from devbox" \
     --redis-host 192.168.1.119 --redis-password beastmode2025
   ```
5. Confirm the listener logs the incoming message.

### Deliverables
- Terminal log showing the package installation command and success message.
- Terminal log showing the listener receiving at least one test message.

### Notes
- Use the shared Redis password (`beastmode2025`).
- Keep the listener running under a supervisor (systemd, tmux, etc.) after testing.
