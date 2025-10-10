# Vonnegut Docker Network Resolution — 2025-10-09

**Context:** Vonnegut’s Docker deployment intermittently failed to attach the `beast-mode-network` bridge, logging `operation not supported` during `docker-compose up`. This document captures the remediation applied on 2025-10-09 and the checklist to repeat if the failure reappears.

## Observed Symptoms
- `docker-compose up` aborts while creating `beast-mode-network`.
- `docker network ls` shows the network in `pending` or absent.
- Docker Desktop (macOS) remains “Running,” but containers cannot start.

## Immediate Remediation (2025-10-09)
1. **Restarted Docker Desktop** to reset the bridge driver.
2. **Pruned orphaned networks and system artifacts**:
   ```bash
   docker network prune
   docker system prune --volumes
   ```
3. **Reran the stack**:
   ```bash
   docker compose up -d
   ```
   The bridge came up cleanly and all services attached successfully.

## Verification Checklist
- `docker network inspect beast-mode-network` returns the bridge details.
- `docker ps` lists `observatory-redis`, `observatory-app`, etc., in `Up` status.
- `redis-cli -h 127.0.0.1 -p 6380 ping` responds `PONG`.
- Application healthchecks pass (`curl http://localhost:8080/health`).

## Future Playbook
If the issue recurs:
1. Restart Docker Desktop or `systemctl restart docker` (Linux).
2. Run the prune commands above (warning: removes unused containers/networks/volumes).
3. If still failing on Linux, reload bridge kernel modules:
   ```bash
   sudo modprobe bridge
   sudo modprobe br_netfilter
   ```
4. As a last resort, temporarily switch services to `network_mode: host`.

## Related Files
- `docs/operational-workflows/docker-bridge-network-troubleshooting.md`
- `docker-compose.yml`
- `.env`, `.env.template`, `.env.example`
