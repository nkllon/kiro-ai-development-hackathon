#!/usr/bin/env python3
"""
Deploy Observatory to Vonnegut Server
====================================

Deploys the complete Observatory stack to the remote Vonnegut Linux server
with containerized Cloudflare tunnel for proper external access.
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class VonnegutDeployer:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"  # Adjust if different
        self.remote_path = "/home/lou/observatory"
        self.tunnel_credentials = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
        
    def check_vonnegut_connectivity(self) -> bool:
        """Check if we can connect to Vonnegut server."""
        print(f"🔍 Testing connectivity to Vonnegut ({self.vonnegut_ip})...")
        
        try:
            result = subprocess.run(
                ["ping", "-c", "2", self.vonnegut_ip],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Vonnegut server is reachable")
                return True
            else:
                print(f"❌ Cannot ping Vonnegut server")
                return False
                
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False
    
    def check_ssh_access(self) -> bool:
        """Check SSH access to Vonnegut."""
        print(f"🔐 Testing SSH access to {self.ssh_user}@{self.vonnegut_ip}...")
        
        try:
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                f"{self.ssh_user}@{self.vonnegut_ip}", "echo 'SSH OK'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ SSH access confirmed")
                return True
            else:
                print(f"❌ SSH access failed: {result.stderr}")
                print(f"💡 Try: ssh-copy-id {self.ssh_user}@{self.vonnegut_ip}")
                return False
                
        except Exception as e:
            print(f"❌ SSH test failed: {e}")
            return False
    
    def prepare_deployment_package(self) -> Path:
        """Create deployment package for Vonnegut."""
        print("📦 Preparing deployment package...")
        
        package_dir = Path("vonnegut_deployment_package")
        package_dir.mkdir(exist_ok=True)
        
        # Copy essential files
        files_to_copy = [
            "start_observatory.py",
            "start_observatory_minimal.py", 
            "src/",
            "requirements.txt",
            "cloudflared-config.yml",
            "scripts/",
            "docs/",
            ".kiro/"
        ]
        
        for item in files_to_copy:
            if Path(item).exists():
                if Path(item).is_dir():
                    subprocess.run(["cp", "-r", item, str(package_dir)], check=True)
                else:
                    subprocess.run(["cp", item, str(package_dir)], check=True)
        
        # Create Docker Compose for Vonnegut
        docker_compose = {
            "version": "3.8",
            "services": {
                "observatory-redis": {
                    "image": "redis:7-alpine",
                    "container_name": "observatory-redis",
                    "ports": ["6379:6379"],
                    "volumes": ["redis-data:/data"],
                    "restart": "unless-stopped",
                    "command": ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]
                },
                "observatory-prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "observatory-prometheus", 
                    "ports": ["9090:9090"],
                    "volumes": [
                        "./prometheus.yml:/etc/prometheus/prometheus.yml:ro",
                        "prometheus-data:/prometheus"
                    ],
                    "restart": "unless-stopped"
                },
                "observatory-grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "observatory-grafana",
                    "ports": ["3000:3000"],
                    "volumes": ["grafana-storage:/var/lib/grafana"],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "admin"
                    },
                    "restart": "unless-stopped"
                },
                "cloudflare-tunnel": {
                    "image": "cloudflare/cloudflared:latest",
                    "container_name": "cloudflare-tunnel",
                    "volumes": [
                        "./cloudflared-config.yml:/etc/cloudflared/config.yml:ro",
                        "./tunnel-credentials.json:/etc/cloudflared/credentials.json:ro"
                    ],
                    "command": ["tunnel", "--config", "/etc/cloudflared/config.yml", "run"],
                    "restart": "unless-stopped",
                    "depends_on": ["observatory-app"]
                },
                "observatory-app": {
                    "build": ".",
                    "container_name": "observatory-app",
                    "ports": ["8888:8888"],
                    "volumes": [
                        "./observatory_data:/app/observatory_data",
                        "./logs:/app/logs"
                    ],
                    "environment": {
                        "REDIS_HOST": "observatory-redis",
                        "REDIS_PASSWORD": "${REDIS_PASSWORD}",
                        "PROMETHEUS_URL": "http://observatory-prometheus:9090"
                    },
                    "depends_on": ["observatory-redis", "observatory-prometheus"],
                    "restart": "unless-stopped"
                }
            },
            "volumes": {
                "redis-data": {},
                "prometheus-data": {},
                "grafana-storage": {}
            }
        }
        
        with open(package_dir / "docker-compose.yml", 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
        
        # Create Dockerfile for Observatory
        dockerfile = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config

# Expose port
EXPOSE 8888

# Start Observatory
CMD ["python", "start_observatory.py"]
"""
        
        with open(package_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile)
        
        # Copy tunnel credentials if they exist
        if self.tunnel_credentials.exists():
            try:
                with open(self.tunnel_credentials, 'r') as src:
                    with open(package_dir / "tunnel-credentials.json", 'w') as dst:
                        dst.write(src.read())
                print(f"✅ Tunnel credentials copied")
            except Exception as e:
                print(f"⚠️ Could not copy tunnel credentials: {e}")
                print(f"💡 You may need to manually copy: {self.tunnel_credentials}")
        else:
            print(f"❌ Tunnel credentials not found: {self.tunnel_credentials}")
            return None
        
        print(f"✅ Deployment package created: {package_dir}")
        return package_dir
    
    def upload_to_vonnegut(self, package_dir: Path) -> bool:
        """Upload deployment package to Vonnegut."""
        print(f"📤 Uploading deployment package to Vonnegut...")
        
        try:
            # Create remote directory
            subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                f"mkdir -p {self.remote_path}"
            ], check=True)
            
            # Upload package
            subprocess.run([
                "rsync", "-avz", "--delete",
                f"{package_dir}/",
                f"{self.ssh_user}@{self.vonnegut_ip}:{self.remote_path}/"
            ], check=True)
            
            print(f"✅ Package uploaded to {self.remote_path}")
            return True
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    def deploy_on_vonnegut(self) -> bool:
        """Deploy Observatory on Vonnegut server."""
        print(f"🚀 Deploying Observatory on Vonnegut...")
        
        deployment_script = f"""
cd {self.remote_path}

# Stop any existing services
docker-compose down 2>/dev/null || true

# Set environment variables
export REDIS_PASSWORD="${os.getenv('REDIS_PASSWORD', 'beastmode2025')}"

# Build and start services
docker-compose up -d --build

# Wait for services to start
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose ps
docker logs observatory-app --tail=20
docker logs cloudflare-tunnel --tail=10

echo "✅ Deployment complete!"
echo "🌐 Observatory should be available at: https://observatory.nkllon.com"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                deployment_script
            ], text=True, capture_output=True)
            
            print("📋 Deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Deployment warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    def validate_deployment(self) -> bool:
        """Validate the Vonnegut deployment."""
        print("🔍 Validating Vonnegut deployment...")
        
        # Test external access
        try:
            import requests
            response = requests.get("https://observatory.nkllon.com/health", timeout=30)
            
            if response.status_code == 200:
                print("✅ External access working")
                health_data = response.json()
                print(f"📊 Health status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ External access failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ External access test failed: {e}")
            return False
    
    def stop_local_services(self):
        """Stop local Observatory services."""
        print("🛑 Stopping local Observatory services...")
        
        # Stop local Observatory process
        try:
            subprocess.run(["pkill", "-f", "start_observatory"], check=False)
            print("✅ Local Observatory process stopped")
        except:
            pass
        
        # Stop local Docker containers
        try:
            subprocess.run(["docker", "stop", "observatory-redis", "observatory-prometheus", "observatory-grafana"], check=False)
            subprocess.run(["docker", "rm", "observatory-redis", "observatory-prometheus", "observatory-grafana"], check=False)
            print("✅ Local Docker containers stopped")
        except:
            pass
        
        # Stop local tunnel
        try:
            subprocess.run(["pkill", "-f", "cloudflared"], check=False)
            print("✅ Local Cloudflare tunnel stopped")
        except:
            pass
    
    async def deploy(self) -> bool:
        """Execute complete deployment to Vonnegut."""
        print("🎯 Observatory Vonnegut Deployment")
        print("=" * 50)
        
        # Pre-deployment checks
        if not self.check_vonnegut_connectivity():
            return False
        
        if not self.check_ssh_access():
            return False
        
        # Stop local services first
        self.stop_local_services()
        
        # Prepare and upload deployment
        package_dir = self.prepare_deployment_package()
        
        if not self.upload_to_vonnegut(package_dir):
            return False
        
        # Deploy on Vonnegut
        if not self.deploy_on_vonnegut():
            return False
        
        # Validate deployment
        if not self.validate_deployment():
            print("⚠️ Deployment completed but validation failed")
            print("🔧 Check Vonnegut logs for issues")
            return False
        
        print("\n🎉 Observatory successfully deployed to Vonnegut!")
        print("🌐 Access: https://observatory.nkllon.com")
        print("📊 Prometheus: https://prometheus.observatory.nkllon.com")
        print("📈 Grafana: https://grafana.observatory.nkllon.com")
        
        return True

async def main():
    """Main deployment execution."""
    deployer = VonnegutDeployer()
    
    try:
        success = await deployer.deploy()
        return success
        
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)