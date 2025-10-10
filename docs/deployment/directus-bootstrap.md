# Directus Bootstrap Guide

This runbook describes how to bring up Directus and its Postgres dependency for a fresh Beast Mode deployment (Poe, etc.).

## 1. Prerequisites
- SSH access (sudo) to the host
- Docker & Docker Compose (or approval to install)
- Internet access for container images

If `make install` is run with `INSTALL_ARGS="--bootstrap-stack"`, the installer will attempt these steps automatically.

## 2. Service Check
```bash
docker ps --format '{{.Names}} {{.Image}}' | grep directus || true
docker ps --format '{{.Names}} {{.Image}}' | grep postgres || true
```

## 3. Bootstrap via `make install`
```bash
make INSTALL_ARGS="--bootstrap-stack" install
```
This ensures Docker is present, seeds `.env` with common passwords, and starts the stack in compose.

## 4. Manual Start (if needed)
```bash
docker compose up -d directus postgres
python scripts/directus/bootstrap_admin.py --email admin@example.com --password beastmode2025  # TODO: replace with actual helper
```

## 5. Verification
```bash
docker inspect -f '{{.State.Health.Status}}' directus
curl -sf http://localhost:8055/health
```

## 6. Next Steps
- Record the Directus admin credentials in the appropriate secrets store.
- Run `make validate-safety` and `make validate-targets` to confirm validators pass with services running.
- Update operational runbooks with host-specific notes if needed.

