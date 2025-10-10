# Docker Bridge Network Troubleshooting

The `beast-mode-network` Docker bridge occasionally fails to attach on macOS hosts with the error:

```
creating network beast-mode-network: driver failed programming external connectivity on endpoint ...: operation not supported
```

When this happens, work through the steps below until connectivity is restored.

1. **Confirm Docker daemon health**
   ```bash
   docker info
   docker network ls
   ```
   If these commands fail, restart the Docker Desktop app.

2. **Reload the bridge kernel module (Linux hosts only)**
   ```bash
   sudo modprobe bridge
   sudo modprobe br_netfilter
   ```

3. **Reset Docker’s network stack**
   ```bash
   docker network prune
   docker system prune --volumes
   ```
   > This removes unused networks, containers, and volumes. Back up any data you need first.

4. **Restart the Docker daemon**
   - **macOS:** `open /Applications/Docker.app` → Preferences → Restart
   - **Linux:** `sudo systemctl restart docker`

5. **Fall back to host networking**
   Temporarily switch services to `network_mode: host` if bridge mode keeps failing.

Document the outcome and any additional remediation in `docs/operational-workflows/` so the next responder has a clear starting point.
