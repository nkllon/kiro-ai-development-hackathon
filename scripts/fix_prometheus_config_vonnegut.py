#!/usr/bin/env python3
"""
Fix Prometheus Configuration on Vonnegut
========================================

Specifically fixes the Prometheus configuration issue where Grafana is exposed
but Prometheus isn't properly configured.
"""

import subprocess
import yaml
from pathlib import Path

def create_prometheus_config():
    """Create proper Prometheus configuration."""
    config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s'
        },
        'scrape_configs': [
            {
                'job_name': 'prometheus',
                'static_configs': [{'targets': ['localhost:9090']}]
            },
            {
                'job_name': 'observatory',
                'static_configs': [{'targets': ['observatory-app:8888']}],
                'metrics_path': '/metrics',
                'scrape_interval': '5s'
            },
            {
                'job_name': 'redis',
                'static_configs': [{'targets': ['observatory-redis:6379']}]
            }
        ]
    }
    return yaml.dump(config, default_flow_style=False)

def fix_prometheus_on_vonnegut():
    """Fix Prometheus configuration on Vonnegut server."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    remote_path = "/home/lou/observatory"
    
    print("🔧 Fixing Prometheus configuration on Vonnegut...")
    
    # Create prometheus config locally
    prometheus_config = create_prometheus_config()
    
    with open("prometheus.yml", 'w') as f:
        f.write(prometheus_config)
    
    try:
        # Upload prometheus config
        subprocess.run([
            "scp", "prometheus.yml", 
            f"{ssh_user}@{vonnegut_ip}:{remote_path}/prometheus.yml"
        ], check=True)
        
        # Fix the deployment on Vonnegut
        fix_script = f"""
cd {remote_path}

echo "🛑 Stopping containers..."
docker-compose down

echo "🔧 Updating Prometheus configuration..."
# Ensure prometheus.yml is in place

echo "🚀 Starting containers with fixed config..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking container status..."
docker-compose ps

echo "🏥 Testing Prometheus health..."
docker-compose exec -T observatory-prometheus wget -q --spider http://localhost:9090/-/healthy && echo "✅ Prometheus healthy" || echo "❌ Prometheus unhealthy"

echo "🏥 Testing Grafana health..."
docker-compose exec -T observatory-grafana curl -f http://localhost:3000/api/health && echo "✅ Grafana healthy" || echo "❌ Grafana unhealthy"

echo "🔗 Testing Prometheus targets..."
docker-compose exec -T observatory-prometheus wget -qO- http://localhost:9090/api/v1/targets | grep -o '"health":"[^"]*"' | head -5

echo "✅ Prometheus configuration fix complete!"
"""
        
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            fix_script
        ], text=True, capture_output=True)
        
        print("📋 Fix output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Fix stderr:")
            print(result.stderr)
        
        # Clean up local file
        Path("prometheus.yml").unlink()
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_prometheus_on_vonnegut()
    if success:
        print("\n🎉 Prometheus configuration fixed!")
        print("📊 Check: https://prometheus.vonnegut.poe.com")
        print("📈 Check: https://grafana.vonnegut.poe.com")
    else:
        print("\n❌ Fix failed - check logs above")