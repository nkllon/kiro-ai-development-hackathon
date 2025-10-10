## Task: Bootstrap Beast Mode Stack on Poe Host

### Goal
Run the enhanced `make install` workflow on the Poe server, bring up the Docker-based Observatory stack, and report verification results.

### Steps
1. SSH into the Poe host (use the standard deployment credentials).
2. Ensure any prior repository checkout is either updated or freshly cloned:
   ```bash
   cd ~/poe
   if [ -d beast-mode-ai-development-hackathon ]; then
       cd beast-mode-ai-development-hackathon && git pull
   else
       git clone https://github.com/your-org/beast-mode-ai-framework.git beast-mode-ai-development-hackathon
       cd beast-mode-ai-development-hackathon
   fi
   ```
3. Run the installer with Docker bootstrap and dev dependencies:
   ```bash
   make INSTALL_ARGS="--bootstrap-stack --dev" install
   ```
   - Capture the full console output to `~/poe/install-log-$(date +%Y%m%d%H%M%S).txt`.
   - Note any warnings or failures.
4. Validate services:
   ```bash
   source .venv/bin/activate
   redis-cli -a "$REDIS_PASSWORD" ping
   docker ps
   curl -sf http://localhost:8080/health
   ```
   Record the outputs.
5. If Directus is part of the stack, confirm port 8055 is listening:
   ```bash
   lsof -i:8055 || docker ps --filter "publish=8055"
   ```

### Deliverables
- Installation log path.
- Summary of validation commands (include Redis ping result, Docker container list, health check status).
- Any follow-up actions required (missing services, errors, manual steps).

### Constraints
- Read/execute only; do not modify application code during this run.
- Use existing credentials; do not rotate secrets.
