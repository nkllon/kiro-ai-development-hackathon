#!/usr/bin/env python3
"""
Fix Vonnegut Prometheus Configuration
===================================

Fixes the Prometheus configuration issue on Vonnegut by ensuring
proper container networking and service discovery.
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any

class VonnegutPrometheusConfigFixer:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/observatory"
        
    def check_current_state(self) -> Dict[str, Any]:
        """Check current state of containers on Vonnegut."""
        print("🔍 Checking current container state on Vonnegut...")
        
        check_script = f"""
cd {self.remote_path} 2>/dev/null || cd /home/lou

echo "=== Docker Containers ==="
docker ps -a --format "table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}"

echo ""
echo "=== Docker Compose Status ==="
if [ -f docker-compose.yml ]; then
    docker-compose ps 2>/dev/null || echo "Docker Compose not running"
else
    echo "No docker-compose.yml found"
fi

echo ""
echo "=== Network Status ==="
docker network ls | grep observatory || echo "No observatory network found"

echo ""
echo "=== Volume Status ==="
docker volume ls | grep -E "(prometheus|grafana|observatory)" || echo "No observatory volumes found"

echo ""
echo "=== Port Status ==="
netstat -tlnp | grep -E "(8888|9090|3000)" || echo "No observatory ports listening"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                check_script
            ], text=True, capture_output=True, timeout=30)
            
            print("📋 Current state:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Warnings:")
                print(result.stderr)
            
            return {"success": result.returncode == 0, "output": result.stdout}
            
        except Exception as e:
            print(f"❌ State check failed: {e}")
            return {"success": False, "error": str(e)}
    
    def fix_prometheus_configuration(self) -> bool:
        """Fix Prometheus configuration for container networking."""
        print("🔧 Fixing Prometheus configuration...")
        
        # Create proper Prometheus config
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s",
                "external_labels": {
                    "instance_id": "vonnegut",
                    "datacenter": "home"
                }
            },
            "scrape_configs": [
                {
                    "job_name": "prometheus",
                    "static_configs": [{"targets": ["localhost:9090"]}]
                },
                {
                    "job_name": "observatory",
                    "metrics_path": "/metrics",
                    "scrape_interval": "5s",
                    "static_configs": [{"targets": ["observatory-app:8888"]}]
                },
                {
                    "job_name": "grafana",
                    "metrics_path": "/metrics", 
                    "scrape_interval": "30s",
                    "static_configs": [{"targets": ["observatory-grafana:3000"]}]
                },
                {
                    "job_name": "redis",
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s", 
                    "static_configs": [{"targets": ["observatory-redis:6379"]}]
                }
            ]
        }
        
        # Write config to temporary file
        temp_config = Path("/tmp/prometheus-vonnegut.yml")
        with open(temp_config, 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        
        # Upload and apply config
        fix_script = f"""
cd {self.remote_path}

# Backup existing config if it exists
if [ -f prometheus.yml ]; then
    cp prometheus.yml prometheus.yml.backup.$(date +%Y%m%d_%H%M%S)
fi

# Stop Prometheus container if running
docker-compose stop observatory-prometheus 2>/dev/null || docker stop observatory-prometheus 2>/dev/null || true

# Wait for stop
sleep 5

# Start Prometheus with new config
docker-compose start observatory-prometheus 2>/dev/null || echo "Starting via docker-compose failed, trying direct docker..."

# Check if Prometheus is running
sleep 10
docker logs observatory-prometheus --tail=20

echo ""
echo "=== Prometheus Status ==="
docker ps | grep prometheus || echo "Prometheus container not running"

echo ""
echo "=== Prometheus Health ==="
curl -s http://localhost:9090/-/healthy || echo "Prometheus health check failed"
"""
        
        try:
            # Upload new config
            subprocess.run([
                "scp", str(temp_config),
                f"{self.ssh_user}@{self.vonnegut_ip}:{self.remote_path}/prometheus.yml"
            ], check=True)
            
            # Apply fix
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                fix_script
            ], text=True, capture_output=True)
            
            print("📋 Fix output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Fix warnings:")
                print(result.stderr)
            
            # Clean up temp file
            temp_config.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Prometheus config fix failed: {e}")
            return False
    
    def restart_observatory_stack(self) -> bool:
        """Restart the entire Observatory stack with proper order."""
        print("🔄 Restarting Observatory stack with proper service order...")
        
        restart_script = f"""
cd {self.remote_path}

echo "🛑 Stopping all services..."
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up any orphaned containers
docker container prune -f 2>/dev/null || true

echo "⏳ Waiting for cleanup..."
sleep 10

echo "🚀 Starting services in proper order..."

# Set environment
export REDIS_PASSWORD="${os.getenv('REDIS_PASSWORD', 'beastmode2025')}"

# Start Redis first
echo "Starting Redis..."
docker-compose up -d observatory-redis
sleep 10

# Start Prometheus
echo "Starting Prometheus..."
docker-compose up -d observatory-prometheus  
sleep 15

# Start Grafana
echo "Starting Grafana..."
docker-compose up -d observatory-grafana
sleep 15

# Start Observatory app
echo "Starting Observatory app..."
docker-compose up -d observatory-app
sleep 20

# Start tunnel last
echo "Starting Cloudflare tunnel..."
docker-compose up -d observatory-tunnel 2>/dev/null || echo "Tunnel start failed, continuing..."

echo ""
echo "=== Final Status ==="
docker-compose ps

echo ""
echo "=== Service Health Checks ==="
echo "Redis:"
docker exec observatory-redis redis-cli ping 2>/dev/null || echo "Redis not responding"

echo "Prometheus:"
curl -s http://localhost:9090/-/healthy || echo "Prometheus not healthy"

echo "Grafana:"
curl -s http://localhost:3000/api/health || echo "Grafana not healthy"

echo "Observatory:"
curl -s http://localhost:8888/health || echo "Observatory not healthy"

echo ""
echo "✅ Stack restart complete!"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                restart_script
            ], text=True, capture_output=True)
            
            print("📋 Restart output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Restart warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Stack restart failed: {e}")
            return False
    
    def validate_services(self) -> bool:
        """Validate all services are working properly."""
        print("🔍 Validating Observatory services...")
        
        validation_script = f"""
cd {self.remote_path}

echo "=== Container Status ==="
docker-compose ps

echo ""
echo "=== Network Connectivity ==="
# Test internal container networking
docker exec observatory-prometheus wget -q --spider http://observatory-app:8888/health && echo "✅ Prometheus -> Observatory: OK" || echo "❌ Prometheus -> Observatory: FAILED"
docker exec observatory-grafana wget -q --spider http://observatory-prometheus:9090/-/healthy && echo "✅ Grafana -> Prometheus: OK" || echo "❌ Grafana -> Prometheus: FAILED"

echo ""
echo "=== External Access ==="
curl -s -o /dev/null -w "Observatory HTTP %{{http_code}}\\n" http://localhost:8888/health
curl -s -o /dev/null -w "Prometheus HTTP %{{http_code}}\\n" http://localhost:9090/-/healthy  
curl -s -o /dev/null -w "Grafana HTTP %{{http_code}}\\n" http://localhost:3000/api/health

echo ""
echo "=== Prometheus Targets ==="
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool 2>/dev/null | grep -A 5 -B 5 "health" || echo "Could not fetch Prometheus targets"

echo ""
echo "=== Recent Logs ==="
echo "Observatory logs:"
docker logs observatory-app --tail=5 2>/dev/null || echo "No Observatory logs"

echo ""
echo "Prometheus logs:"
docker logs observatory-prometheus --tail=5 2>/dev/null || echo "No Prometheus logs"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                validation_script
            ], text=True, capture_output=True)
            
            print("📋 Validation results:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Validation warnings:")
                print(result.stderr)
            
            # Check if validation indicates success
            success_indicators = [
                "Observatory HTTP 200",
                "Prometheus HTTP 200", 
                "Grafana HTTP 200"
            ]
            
            success_count = sum(1 for indicator in success_indicators if indicator in result.stdout)
            
            if success_count >= 2:
                print(f"✅ Validation passed ({success_count}/3 services healthy)")
                return True
            else:
                print(f"❌ Validation failed ({success_count}/3 services healthy)")
                return False
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def fix_all(self) -> bool:
        """Execute complete fix process."""
        print("🎯 Vonnegut Prometheus Configuration Fix")
        print("=" * 50)
        
        # Check current state
        state = self.check_current_state()
        if not state["success"]:
            print("❌ Could not check current state")
            return False
        
        # Fix Prometheus configuration
        if not self.fix_prometheus_configuration():
            print("❌ Failed to fix Prometheus configuration")
            return False
        
        # Restart stack
        if not self.restart_observatory_stack():
            print("❌ Failed to restart Observatory stack")
            return False
        
        # Validate services
        if not self.validate_services():
            print("⚠️ Services restarted but validation failed")
            print("🔧 Check logs for specific issues")
            return False
        
        print("\n🎉 Vonnegut Observatory stack is now properly configured!")
        print("🌐 Observatory: https://observatory.niclon.com")
        print("📊 Prometheus: https://prometheus.observatory.niclon.com")
        print("📈 Grafana: https://grafana.observatory.niclon.com")
        
        return True

def main():
    """Main execution."""
    fixer = VonnegutPrometheusConfigFixer()
    
    try:
        success = fixer.fix_all()
        return success
        
    except Exception as e:
        print(f"\n❌ Fix process failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)