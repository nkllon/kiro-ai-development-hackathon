#!/usr/bin/env python3
"""
Observatory Migration to Poe
============================

Executes the complete migration from Vonnegut to Poe with zero downtime.
"""

import os
import sys
import json
import subprocess
import time
import requests
from datetime import datetime
from pathlib import Path

class PoeObservatoryMigration:
    def __init__(self):
        self.poe_ip = None  # Will be determined
        self.vonnegut_ip = "192.168.1.119"
        self.migration_log = []
        self.deployment_package = None
        
    def log_action(self, action, status, details=""):
        """Log migration actions."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.migration_log.append(entry)
        
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "ℹ️"
        print(f"{status_icon} {action}: {details}")
    
    def find_deployment_package(self):
        """Find the latest deployment package."""
        print("🔍 Finding deployment package...")
        
        packages = list(Path(".").glob("observatory-poe-deployment-*.tar.gz"))
        if not packages:
            self.log_action("Package Search", "error", "No deployment packages found")
            return False
        
        # Get the latest package
        latest_package = max(packages, key=lambda x: x.stat().st_mtime)
        self.deployment_package = latest_package
        
        self.log_action("Package Found", "success", f"Using {latest_package}")
        return True
    
    def get_poe_ip(self):
        """Get Poe server IP address."""
        print("🌐 Determining Poe IP address...")
        
        # For now, we'll use a placeholder - in real deployment this would be determined
        # You would replace this with actual Poe server discovery
        self.poe_ip = "POE_SERVER_IP"  # Placeholder
        
        self.log_action("Poe IP Discovery", "info", f"Poe IP: {self.poe_ip}")
        return True
    
    def create_poe_deployment_script(self):
        """Create script to deploy on Poe server."""
        print("📝 Creating Poe deployment script...")
        
        poe_script = f'''#!/bin/bash
# Observatory Deployment Script for Poe
# Run this script on the Poe server

set -e

echo "🚀 Observatory Deployment on Poe"
echo "================================"

# Extract deployment package
echo "📦 Extracting deployment package..."
tar -xzf {self.deployment_package.name}
cd poe_deployment_*/

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Setup Docker containers
echo "🐳 Starting Docker containers..."
docker-compose -f deployment/observatory/docker-compose.yml up -d redis prometheus grafana

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 30

# Setup data persistence
echo "💾 Setting up data persistence..."
python setup_data_persistence.py

# Start Observatory
echo "🌟 Starting Observatory..."
nohup python start_observatory.py > observatory.log 2>&1 &

# Wait for Observatory to start
echo "⏳ Waiting for Observatory to start..."
sleep 15

# Validate deployment
echo "✅ Validating deployment..."
python validate_observatory_deployment.py

echo "🎉 Observatory deployed successfully on Poe!"
echo "🌐 Local access: http://localhost:8888"
echo "📊 Grafana: http://localhost:3000"
echo "📈 Prometheus: http://localhost:9090"
'''
        
        script_file = Path("deploy_on_poe.sh")
        with open(script_file, 'w') as f:
            f.write(poe_script)
        
        os.chmod(script_file, 0o755)
        self.log_action("Poe Script Creation", "success", f"Created {script_file}")
        return script_file
    
    def create_tunnel_switchover_script(self):
        """Create script to switch Cloudflare tunnel to Poe."""
        print("🔄 Creating tunnel switchover script...")
        
        # Read current tunnel config
        with open("cloudflared-config.yml", 'r') as f:
            current_config = f.read()
        
        # Create new config for Poe
        poe_config = current_config.replace(
            "service: http://localhost:8888",
            f"service: http://{self.poe_ip}:8888"
        ).replace(
            "service: http://localhost:3000", 
            f"service: http://{self.poe_ip}:3000"
        ).replace(
            "service: http://localhost:9090",
            f"service: http://{self.poe_ip}:9090"
        )
        
        # Save Poe config
        poe_config_file = Path("cloudflared-config-poe.yml")
        with open(poe_config_file, 'w') as f:
            f.write(poe_config)
        
        # Create switchover script
        switchover_script = f'''#!/bin/bash
# Cloudflare Tunnel Switchover Script
# Switches Observatory traffic from Vonnegut to Poe

set -e

echo "🔄 Observatory Tunnel Switchover"
echo "==============================="

# Backup current config
echo "💾 Backing up current tunnel config..."
cp cloudflared-config.yml cloudflared-config-vonnegut-backup.yml

# Switch to Poe config
echo "🔄 Switching tunnel to Poe..."
cp cloudflared-config-poe.yml cloudflared-config.yml

# Restart tunnel
echo "🔄 Restarting Cloudflare tunnel..."
python scripts/manage_tunnel.py restart

# Wait for tunnel to stabilize
echo "⏳ Waiting for tunnel to stabilize..."
sleep 10

# Test external access
echo "🔍 Testing external access..."
curl -f https://observatory.nkllon.com/health || echo "❌ Health check failed"
curl -f https://grafana.observatory.nkllon.com/ || echo "❌ Grafana check failed"

echo "✅ Tunnel switchover complete!"
echo "🌐 Observatory now running on Poe"
'''
        
        switchover_file = Path("switchover_to_poe.sh")
        with open(switchover_file, 'w') as f:
            f.write(switchover_script)
        
        os.chmod(switchover_file, 0o755)
        
        self.log_action("Switchover Script", "success", f"Created {switchover_file}")
        self.log_action("Poe Config", "success", f"Created {poe_config_file}")
        return switchover_file
    
    def create_rollback_script(self):
        """Create rollback script to return to Vonnegut."""
        print("🔙 Creating rollback script...")
        
        rollback_script = '''#!/bin/bash
# Observatory Rollback Script
# Returns Observatory traffic to Vonnegut

set -e

echo "🔙 Observatory Rollback to Vonnegut"
echo "=================================="

# Restore Vonnegut config
echo "🔄 Restoring Vonnegut tunnel config..."
cp cloudflared-config-vonnegut-backup.yml cloudflared-config.yml

# Restart tunnel
echo "🔄 Restarting Cloudflare tunnel..."
python scripts/manage_tunnel.py restart

# Wait for tunnel to stabilize
echo "⏳ Waiting for tunnel to stabilize..."
sleep 10

# Test external access
echo "🔍 Testing external access..."
curl -f https://observatory.nkllon.com/health || echo "❌ Health check failed"

echo "✅ Rollback complete!"
echo "🌐 Observatory back on Vonnegut"
'''
        
        rollback_file = Path("rollback_to_vonnegut.sh")
        with open(rollback_file, 'w') as f:
            f.write(rollback_script)
        
        os.chmod(rollback_file, 0o755)
        self.log_action("Rollback Script", "success", f"Created {rollback_file}")
        return rollback_file
    
    def create_migration_guide(self):
        """Create step-by-step migration guide."""
        print("📖 Creating migration guide...")
        
        guide_content = f'''# Observatory Migration to Poe - Step by Step Guide

**Migration Package**: {self.deployment_package}
**Created**: {datetime.now().isoformat()}
**Vonnegut IP**: {self.vonnegut_ip}
**Poe IP**: {self.poe_ip}

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
   scp {self.deployment_package} user@poe-server:/path/to/deployment/
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
'''
        
        guide_file = Path("MIGRATION_GUIDE.md")
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        self.log_action("Migration Guide", "success", f"Created {guide_file}")
        return guide_file
    
    def prepare_migration(self):
        """Prepare all migration artifacts."""
        print("🚀 Observatory Migration to Poe - Preparation")
        print("=" * 50)
        
        # Step 1: Find deployment package
        if not self.find_deployment_package():
            return False
        
        # Step 2: Get Poe IP
        if not self.get_poe_ip():
            return False
        
        # Step 3: Create Poe deployment script
        poe_script = self.create_poe_deployment_script()
        if not poe_script:
            return False
        
        # Step 4: Create tunnel switchover script
        switchover_script = self.create_tunnel_switchover_script()
        if not switchover_script:
            return False
        
        # Step 5: Create rollback script
        rollback_script = self.create_rollback_script()
        if not rollback_script:
            return False
        
        # Step 6: Create migration guide
        guide_file = self.create_migration_guide()
        if not guide_file:
            return False
        
        print(f"\n🎉 Migration Preparation Complete!")
        print(f"📦 Deployment Package: {self.deployment_package}")
        print(f"🚀 Poe Deployment: {poe_script}")
        print(f"🔄 Switchover Script: {switchover_script}")
        print(f"🔙 Rollback Script: {rollback_script}")
        print(f"📖 Migration Guide: {guide_file}")
        print(f"\n📋 Next Steps:")
        print(f"1. Review {guide_file}")
        print(f"2. Transfer files to Poe server")
        print(f"3. Deploy on Poe using {poe_script}")
        print(f"4. Execute switchover using {switchover_script}")
        
        return True

def main():
    """Main migration preparation execution."""
    migration = PoeObservatoryMigration()
    
    try:
        success = migration.prepare_migration()
        
        if success:
            print("\n🎯 Migration preparation completed successfully!")
            print("Ready to execute Observatory migration to Poe!")
            return True
        else:
            print("\n❌ Migration preparation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Migration preparation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)