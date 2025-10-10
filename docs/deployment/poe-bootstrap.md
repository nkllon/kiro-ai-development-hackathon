# Poe Environment Bootstrap Guide

This runbook describes how to bring up a fresh Beast Mode stack on the **Poe** host using the enhanced installer (`make install`). It assumes the machine is a clean Linux box with no Redis, Docker, or Directus services yet installed.

## 1. Pre-Install Checklist

- SSH access with sudo privileges.
- Python 3.9+ available (installer will verify).
- Optional: ensure system packages are up to date (`sudo apt update && sudo apt upgrade`).

## 2. Clone the Repository

```bash
git clone https://github.com/your-org/beast-mode-ai-framework.git
cd beast-mode-ai-framework
```

## 3. Run the Installer

The installer handles Python environment setup, Redis configuration, and optional Docker bootstrapping.

```bash
# Minimal install (creates .venv, installs dependencies, configures Redis credentials)
make install

# Recommended for a full stack (installs dev tools and brings up Docker services)
make INSTALL_ARGS="--bootstrap-stack --dev" install
```

### Installer Flags

| Flag | Purpose | Notes |
|------|---------|-------|
| `--bootstrap-stack` | Runs `docker compose up -d --build` after install | Requires Docker |
| `--install-docker` | Attempts to install Docker/Compose (Linux) | Needs sudo; restarts Docker daemon |
| `--dev` | Installs `requirements-dev.txt` | Useful for local development |
| `--with-demo` | Executes quick start demo post-install | Runs inside `.venv` |
| `--non-interactive` | Suppresses guidance prompts | Recommended for CI |

## 4. Post-Install Validation

After the script completes:

```bash
source .venv/bin/activate
redis-cli -a "$REDIS_PASSWORD" ping    # Should return PONG (password defaults to beastmode2025)
docker ps                              # Confirm observatory services if stack bootstrapped
curl http://localhost:8080/health      # Observatory health check
```

## 5. Seed Directus (Optional)

If Directus is part of the deployment:

1. Ensure the Docker stack is running (`make INSTALL_ARGS="--bootstrap-stack" install` or `docker compose up -d`).
2. Access Directus at `http://localhost:8055` (default credentials are not created automatically).
3. Run seeding scripts (to be tracked separately) or follow manual provisioning steps:
   ```bash
   python scripts/directus/bootstrap_admin.py  # TODO: script placeholder
   ```
4. Document the admin credentials in the secure secrets store.

## 6. Troubleshooting

- **Docker bridge errors**: follow `docs/operational-workflows/docker-bridge-network-troubleshooting.md`.
- **Redis auth failures**: verify `~/.env` includes `REDIS_PASSWORD=beastmode2025`.
- **Prometheus init warnings**: known issue (pending fix); does not block deployment.

## 7. Next Steps

- Run `make quick-start` to validate the agent demo.
- Execute `make dev-test` (after expanding coverage) for smoke validation.
- Wire Poe into cluster orchestration once services are confirmed healthy.
