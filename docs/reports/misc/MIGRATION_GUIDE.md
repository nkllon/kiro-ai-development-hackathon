# Observatory Migration to Poe - Step by Step Guide

**Migration Package**: observatory-poe-deployment-20251004_152642.tar.gz
**Created**: 2025-10-04T15:31:48.176657
**Vonnegut IP**: 192.168.1.119
**Poe IP**: POE_SERVER_IP

## 🎯 Migration Overview

This migration moves Observatory from Vonnegut to Poe with zero downtime using Cloudflare tunnel switchover.

## 📋 Pre-Migration Checklist

- [ ] Poe server accessible and ready
- [ ] Deployment package transferred to Poe
- [ ] Docker installed on Poe
- [ ] Python environment ready on Poe
- [ ] Cloudflare tunnel credentials available

## 🚀 Migration Steps

### Step 1: Deploy on Poe (Parallel)

1. **Transfer files to Poe**:
   ```bash
   scp observatory-poe-deployment-20251004_152642.tar.gz user@poe-server:/path/to/deployment/
   scp deploy_on_poe.sh user@poe-server:/path/to/deployment/
   ```

2. **SSH to Poe and deploy**:
   ```bash
   ssh user@poe-server
   cd /path/to/deployment/
   ./deploy_on_poe.sh
   ```

3. **Verify Poe deployment**:
   ```bash
   curl http://poe-ip:8888/health
   curl http://poe-ip:3000/
   curl http://poe-ip:9090/
   ```

### Step 2: Test Poe Services

- **Observatory**: http://poe-ip:8888
- **Grafana**: http://poe-ip:3000  
- **Prometheus**: http://poe-ip:9090
- **WebSocket endpoints**: Test all 3 endpoints
- **Data persistence**: Verify data directories

### Step 3: Tunnel Switchover

1. **Execute switchover** (on Vonnegut):
   ```bash
   ./switchover_to_poe.sh
   ```

2. **Verify external access**:
   - https://observatory.nkllon.com
   - https://grafana.observatory.nkllon.com
   - https://prometheus.observatory.nkllon.com

### Step 4: Validation

1. **Test all functionality**:
   ```bash
   python validate_observatory_deployment.py
   ```

2. **Test WebSocket endpoints**:
   ```bash
   python test_websocket.py
   ```

3. **Monitor for issues**:
   ```bash
   python scripts/monitor_observatory_health.py status
   ```

## 🔙 Rollback Procedure

If issues occur, rollback immediately:

```bash
./rollback_to_vonnegut.sh
```

This restores the tunnel to point back to Vonnegut.

## 🔧 Post-Migration

1. **Monitor Poe deployment** for 24 hours
2. **Verify all features working** 
3. **Update documentation** with new Poe details
4. **Decommission Vonnegut** when confident

## 📞 Emergency Contacts

- **Migration Lead**: [Your contact]
- **Poe Server Admin**: [Poe admin contact]
- **Cloudflare Admin**: [Tunnel admin contact]

## 🚨 Troubleshooting

### Common Issues

1. **Poe deployment fails**: Check Docker, Python, dependencies
2. **Tunnel switchover fails**: Verify Poe IP, check tunnel config
3. **External access broken**: Run rollback script immediately
4. **WebSocket issues**: Check Poe firewall, container networking

### Emergency Commands

```bash
# Check Poe services
ssh user@poe-server "docker ps && curl localhost:8888/health"

# Rollback immediately
./rollback_to_vonnegut.sh

# Check tunnel status
python scripts/manage_tunnel.py status
```

---

**Ready for Migration! 🚀**
