#!/usr/bin/env python3
"""
Deploy Containerized Observatory to Vonnegut
===========================================

Deploys the complete containerized Observatory stack to Vonnegut server
with proper Prometheus configuration and independent service management.
"""

import os
import sys
import subprocess
import json
import yaml
import time
from pathlib import Path
from typing import Dict, Any, List

class VonnegutContainerDeployer:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/observatory"
        self.tunnel_credentials = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
        
    def check_prerequisites(self) -> bool:
        """Check all prerequisites for deployment."""
        print("🔍 Checking deployment prerequisites...")
        
        # Check connectivity
        if not self._check_connectivity():
            return False
            
        # Check SSH access
        if not self._check_ssh_access():
            return False
            
        # Check tunnel credentials
        if not self.tunnel_credentials.exists():
            print(f"❌ Tunnel credentials not found: {self.tunnel_credentials}")
            return False
            
        print("✅ All prerequisites met")
        return True
    
    def _check_connectivity(self) -> bool:
        """Check network connectivity to Vonnegut."""
        try:
            result = subprocess.run(
                ["ping", "-c", "2", self.vonnegut_ip],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Vonnegut ({self.vonnegut_ip}) is reachable")
                return True
            else:
                print(f"❌ Cannot reach Vonnegut server")
                return False
        except Exception as e:
            print(f"❌ Connectivity check failed: {e}")
            return False
    
    def _check_ssh_access(self) -> bool:
        """Check SSH access to Vonnegut."""
        try:
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                f"{self.ssh_user}@{self.vonnegut_ip}", "echo 'SSH OK'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ SSH access confirmed")
                return True
            else:
                print(f"❌ SSH access failed")
                return False
        except Exception as e:
            print(f"❌ SSH test failed: {e}")
            return False
    
    def prepare_deployment_package(self) -> Path:
        """Prepare complete deployment package for Vonnegut."""
        print("📦 Preparing containerized deployment package...")
        
        package_dir = Path("vonnegut_container_deployment")
        if package_dir.exists():
            subprocess.run(["rm", "-rf", str(package_dir)], check=True)
        package_dir.mkdir()
        
        # Copy deployment directory
        subprocess.run(["cp", "-r", "deployment/observatory", str(package_dir)], check=True)
        
        # Copy source code
        subprocess.run(["cp", "-r", "src", str(package_dir)], check=True)
        
        # Copy essential files
        essential_files = [
            "start_observatory.py",
            "requirements.txt",
            "Dockerfile"
        ]
        
        for file in essential_files:
            if Path(file).exists():
                subprocess.run(["cp", file, str(package_dir)], check=True)
        
        # Create Vonnegut-specific docker-compose.yml
        self._create_vonnegut_docker_compose(package_dir)
        
        # Create Vonnegut-specific Prometheus config
        self._create_vonnegut_prometheus_config(package_dir)
        
        # Create Cloudflare tunnel config
        self._create_tunnel_config(package_dir)
        
        # Copy tunnel credentials
        if self.tunnel_credentials.exists():
            subprocess.run([
                "cp", str(self.tunnel_credentials), 
                str(package_dir / "tunnel-credentials.json")
            ], check=True)
        
        print(f"✅ Deployment package created: {package_dir}")
        return package_dir
    
    def _create_vonnegut_docker_compose(self, package_dir: Path):
        """Create Vonnegut-optimized docker-compose.yml."""
        compose_config = {
            "version": "3.8",
            "services": {
                "observatory-redis": {
                    "image": "redis:7-alpine",
                    "container_name": "observatory-redis",
                    "restart": "unless-stopped",
                    "ports": ["6379:6379"],
                    "networks": ["observatory-network"],
                    "command": ["redis-server", "--appendonly", "yes", "--requirepass", "${REDIS_PASSWORD}"],
                    "volumes": ["redis_data:/data"],
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "--raw", "incr", "ping"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "observatory-prometheus": {
                    "image": "prom/prometheus:latest",
                    "container_name": "observatory-prometheus",
                    "restart": "unless-stopped",
                    "ports": ["9090:9090"],
                    "networks": ["observatory-network"],
                    "command": [
                        "--config.file=/etc/prometheus/prometheus.yml",
                        "--storage.tsdb.path=/prometheus",
                        "--web.console.libraries=/etc/prometheus/console_libraries",
                        "--web.console.templates=/etc/prometheus/consoles",
                        "--storage.tsdb.retention.time=7d",
                        "--web.enable-lifecycle",
                        "--web.enable-remote-write-receiver",
                        "--web.external-url=https://prometheus.observatory.niclon.com"
                    ],
                    "volumes": [
                        "./prometheus-vonnegut.yml:/etc/prometheus/prometheus.yml:ro",
                        "prometheus_data:/prometheus"
                    ],
                    "healthcheck": {
                        "test": ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "observatory-grafana": {
                    "image": "grafana/grafana:latest",
                    "container_name": "observatory-grafana",
                    "restart": "unless-stopped",
                    "ports": ["3000:3000"],
                    "networks": ["observatory-network"],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "admin",
                        "GF_USERS_ALLOW_SIGN_UP": "false",
                        "GF_AUTH_ANONYMOUS_ENABLED": "true",
                        "GF_AUTH_ANONYMOUS_ORG_NAME": "Main Org.",
                        "GF_AUTH_ANONYMOUS_ORG_ROLE": "Viewer",
                        "GF_SESSION_PROVIDER": "redis",
                        "GF_SESSION_PROVIDER_CONFIG": "addr=observatory-redis:6379,pool_size=100,db=1,password=${REDIS_PASSWORD}",
                        "GF_DATABASE_TYPE": "sqlite3"
                    },
                    "volumes": [
                        "grafana_data:/var/lib/grafana",
                        "./observatory/grafana-config:/etc/grafana/provisioning"
                    ],
                    "depends_on": ["observatory-redis", "observatory-prometheus"],
                    "healthcheck": {
                        "test": ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                },
                "observatory-app": {
                    "build": {
                        "context": ".",
                        "dockerfile": "observatory/Dockerfile"
                    },
                    "image": "beast-mode-observatory:vonnegut",
                    "container_name": "observatory-app",
                    "restart": "unless-stopped",
                    "ports": ["8888:8888", "8889:8889", "8890:8890"],
                    "networks": ["observatory-network"],
                    "environment": {
                        "OBSERVATORY_HOST": "0.0.0.0",
                        "OBSERVATORY_PORT": "8888",
                        "WEBSOCKET_PORT": "8889",
                        "HEALTH_MONITOR_PORT": "8890",
                        "LOG_LEVEL": "INFO",
                        "REDIS_HOST": "observatory-redis",
                        "REDIS_PORT": "6379",
                        "REDIS_PASSWORD": "${REDIS_PASSWORD}",
                        "REDIS_DB": "0",
                        "PROMETHEUS_URL": "http://observatory-prometheus:9090",
                        "GRAFANA_URL": "http://observatory-grafana:3000",
                        "CACHE_BACKEND": "redis",
                        "SESSION_BACKEND": "redis",
                        "SHARED_STATE_BACKEND": "redis",
                        "DOCKER_DESKTOP": "false",
                        "PROMETHEUS_ENABLED": "true",
                        "METRICS_EXPORT_ENABLED": "true"
                    },
                    "volumes": [
                        "observatory_data:/app/data",
                        "observatory_logs:/app/logs",
                        "/etc/localtime:/etc/localtime:ro"
                    ],
                    "depends_on": ["observatory-redis", "observatory-prometheus"],
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8888/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "60s"
                    }
                },
                "cloudflare-tunnel": {
                    "image": "cloudflare/cloudflared:latest",
                    "container_name": "observatory-tunnel",
                    "restart": "unless-stopped",
                    "networks": ["observatory-network"],
                    "command": ["tunnel", "--config", "/etc/cloudflared/config.yml", "run"],
                    "volumes": [
                        "./cloudflared-config.yml:/etc/cloudflared/config.yml:ro",
                        "./tunnel-credentials.json:/etc/cloudflared/credentials.json:ro"
                    ],
                    "depends_on": ["observatory-app", "observatory-grafana", "observatory-prometheus"],
                    "healthcheck": {
                        "test": ["CMD", "cloudflared", "tunnel", "info"],
                        "interval": "60s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
            },
            "networks": {
                "observatory-network": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "observatory_data": {"driver": "local"},
                "observatory_logs": {"driver": "local"},
                "grafana_data": {"driver": "local"},
                "prometheus_data": {"driver": "local"},
                "redis_data": {"driver": "local"}
            }
        }
        
        with open(package_dir / "docker-compose.yml", 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
    
    def _create_vonnegut_prometheus_config(self, package_dir: Path):
        """Create Vonnegut-specific Prometheus configuration."""
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
                    "job_name": "redis",
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                    "static_configs": [{"targets": ["observatory-redis:6379"]}]
                },
                {
                    "job_name": "grafana",
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                    "static_configs": [{"targets": ["observatory-grafana:3000"]}]
                },
                {
                    "job_name": "node-exporter",
                    "metrics_path": "/metrics",
                    "scrape_interval": "30s",
                    "static_configs": [{"targets": ["host.docker.internal:9100"]}]
                }
            ]
        }
        
        with open(package_dir / "prometheus-vonnegut.yml", 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
    
    def _create_tunnel_config(self, package_dir: Path):
        """Create Cloudflare tunnel configuration."""
        tunnel_config = {
            "tunnel": "d1e53e43-033f-4994-8f46-c83962ae3785",
            "credentials-file": "/etc/cloudflared/credentials.json",
            "ingress": [
                {
                    "hostname": "observatory.niclon.com",
                    "service": "http://observatory-app:8888"
                },
                {
                    "hostname": "grafana.observatory.niclon.com", 
                    "service": "http://observatory-grafana:3000"
                },
                {
                    "hostname": "prometheus.observatory.niclon.com",
                    "service": "http://observatory-prometheus:9090"
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
        
        with open(package_dir / "cloudflared-config.yml", 'w') as f:
            yaml.dump(tunnel_config, f, default_flow_style=False)
    
    def upload_to_vonnegut(self, package_dir: Path) -> bool:
        """Upload deployment package to Vonnegut."""
        print(f"📤 Uploading containerized deployment to Vonnegut...")
        
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
    
    def deploy_containers_on_vonnegut(self) -> bool:
        """Deploy containerized Observatory on Vonnegut."""
        print(f"🚀 Deploying containerized Observatory on Vonnegut...")
        
        deployment_script = f"""
cd {self.remote_path}

# Set environment variables
export REDIS_PASSWORD="${os.getenv('REDIS_PASSWORD', 'beastmode2025')}"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up any orphaned containers
docker container prune -f 2>/dev/null || true
docker network prune -f 2>/dev/null || true

# Build and start services
echo "🏗️ Building and starting containers..."
docker-compose up -d --build

# Wait for services to initialize
echo "⏳ Waiting for services to initialize..."
sleep 60

# Check service health
echo "🏥 Checking service health..."
docker-compose ps
echo ""
echo "📊 Container logs:"
docker logs observatory-app --tail=10
echo ""
docker logs observatory-prometheus --tail=10
echo ""
docker logs observatory-grafana --tail=10
echo ""
docker logs observatory-tunnel --tail=10

echo ""
echo "✅ Containerized deployment complete!"
echo "🌐 Observatory: https://observatory.niclon.com"
echo "📊 Prometheus: https://prometheus.observatory.niclon.com"  
echo "📈 Grafana: https://grafana.observatory.niclon.com"
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
        """Validate the containerized deployment."""
        print("🔍 Validating containerized deployment...")
        
        # Wait a bit more for services to fully start
        print("⏳ Waiting for services to fully initialize...")
        time.sleep(30)
        
        validation_results = []
        
        # Test each service endpoint
        endpoints = [
            ("Observatory", "https://observatory.niclon.com/health"),
            ("Prometheus", "https://prometheus.observatory.niclon.com/-/healthy"),
            ("Grafana", "https://grafana.observatory.niclon.com/api/health")
        ]
        
        for service, url in endpoints:
            try:
                import requests
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    print(f"✅ {service} is accessible")
                    validation_results.append(True)
                else:
                    print(f"❌ {service} returned HTTP {response.status_code}")
                    validation_results.append(False)
            except Exception as e:
                print(f"❌ {service} validation failed: {e}")
                validation_results.append(False)
        
        return all(validation_results)
    
    def manage_individual_services(self, action: str, services: List[str] = None) -> bool:
        """Manage individual containerized services."""
        if services is None:
            services = ["observatory-app", "observatory-prometheus", "observatory-grafana", "observatory-redis", "observatory-tunnel"]
        
        print(f"🔧 {action.title()} services: {', '.join(services)}")
        
        service_commands = {
            "start": "docker-compose start",
            "stop": "docker-compose stop", 
            "restart": "docker-compose restart",
            "logs": "docker-compose logs --tail=50",
            "status": "docker-compose ps"
        }
        
        if action not in service_commands:
            print(f"❌ Unknown action: {action}")
            return False
        
        cmd = f"{service_commands[action]} {' '.join(services)}"
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                f"cd {self.remote_path} && {cmd}"
            ], text=True, capture_output=True)
            
            print("📋 Command output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Command warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Service management failed: {e}")
            return False
    
    async def deploy(self) -> bool:
        """Execute complete containerized deployment."""
        print("🎯 Observatory Containerized Vonnegut Deployment")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Prepare deployment package
        package_dir = self.prepare_deployment_package()
        
        # Upload to Vonnegut
        if not self.upload_to_vonnegut(package_dir):
            return False
        
        # Deploy containers
        if not self.deploy_containers_on_vonnegut():
            return False
        
        # Validate deployment
        if not self.validate_deployment():
            print("⚠️ Deployment completed but validation failed")
            print("🔧 Check container logs for issues")
            return False
        
        print("\n🎉 Containerized Observatory successfully deployed to Vonnegut!")
        print("🌐 Observatory: https://observatory.niclon.com")
        print("📊 Prometheus: https://prometheus.observatory.niclon.com")
        print("📈 Grafana: https://grafana.observatory.niclon.com")
        print("\n🔧 Service Management Commands:")
        print(f"  Start all: python {__file__} start")
        print(f"  Stop all: python {__file__} stop")
        print(f"  Restart all: python {__file__} restart")
        print(f"  Check status: python {__file__} status")
        print(f"  View logs: python {__file__} logs")
        
        return True

async def main():
    """Main deployment execution."""
    deployer = VonnegutContainerDeployer()
    
    # Handle service management commands
    if len(sys.argv) > 1:
        action = sys.argv[1]
        services = sys.argv[2:] if len(sys.argv) > 2 else None
        
        if action in ["start", "stop", "restart", "logs", "status"]:
            success = deployer.manage_individual_services(action, services)
            return success
        elif action == "deploy":
            success = await deployer.deploy()
            return success
        else:
            print(f"❌ Unknown command: {action}")
            print("Available commands: deploy, start, stop, restart, logs, status")
            return False
    
    # Default to full deployment
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