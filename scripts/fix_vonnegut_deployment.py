#!/usr/bin/env python3
"""
Fix Vonnegut Containerized Observatory Deployment
================================================

Creates a complete containerized deployment for Vonnegut Linux server
with proper Prometheus configuration and Grafana integration.
"""

import os
import sys
import subprocess
import yaml
import json
from pathlib import Path
from typing import Dict, Any

class VonnegutContainerFix:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/observatory"
        
    def create_prometheus_config(self) -> str:
        """Create proper Prometheus configuration."""
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {'targets': ['localhost:9090']}
                    ]
                },
                {
                    'job_name': 'observatory',
                    'static_configs': [
                        {'targets': ['observatory-app:8888']}
                    ],
                    'metrics_path': '/metrics',
                    'scrape_interval': '5s'
                },
                {
                    'job_name': 'redis',
                    'static_configs': [
                        {'targets': ['observatory-redis:6379']}
                    ]
                },
                {
                    'job_name': 'node-exporter',
                    'static_configs': [
                        {'targets': ['node-exporter:9100']}
                    ]
                }
            ]
        }
        
        return yaml.dump(prometheus_config, default_flow_style=False)
    
    def create_docker_compose(self) -> str:
        """Create complete Docker Compose configuration."""
        compose_config = {
            'version': '3.8',
            'services': {
                'observatory-redis': {
                    'image': 'redis:7-alpine',
                    'container_name': 'observatory-redis',
                    'ports': ['6379:6379'],
                    'volumes': ['redis-data:/data'],
                    'restart': 'unless-stopped',
                    'command': ['redis-server', '--requirepass', '${REDIS_PASSWORD:-beastmode2025}'],
                    'healthcheck': {
                        'test': ['CMD', 'redis-cli', '--raw', 'incr', 'ping'],
                        'interval': '10s',
                        'timeout': '3s',
                        'retries': 5
                    }
                },
                'observatory-prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': 'observatory-prometheus',
                    'ports': ['9090:9090'],
                    'volumes': [
                        './prometheus.yml:/etc/prometheus/prometheus.yml:ro',
                        'prometheus-data:/prometheus'
                    ],
                    'restart': 'unless-stopped',
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/etc/prometheus/console_libraries',
                        '--web.console.templates=/etc/prometheus/consoles',
                        '--storage.tsdb.retention.time=200h',
                        '--web.enable-lifecycle'
                    ],
                    'healthcheck': {
                        'test': ['CMD', 'wget', '--no-verbose', '--tries=1', '--spider', 'http://localhost:9090/-/healthy'],
                        'interval': '10s',
                        'timeout': '3s',
                        'retries': 5
                    }
                },
                'observatory-grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': 'observatory-grafana',
                    'ports': ['3000:3000'],
                    'volumes': [
                        'grafana-storage:/var/lib/grafana',
                        './grafana-provisioning:/etc/grafana/provisioning:ro'
                    ],
                    'environment': {
                        'GF_SECURITY_ADMIN_PASSWORD': '${GRAFANA_PASSWORD:-admin}',
                        'GF_USERS_ALLOW_SIGN_UP': 'false',
                        'GF_SERVER_DOMAIN': 'grafana.vonnegut.poe.com',
                        'GF_SERVER_ROOT_URL': 'https://grafana.vonnegut.poe.com'
                    },
                    'restart': 'unless-stopped',
                    'depends_on': ['observatory-prometheus'],
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1'],
                        'interval': '10s',
                        'timeout': '3s',
                        'retries': 5
                    }
                },
                'node-exporter': {
                    'image': 'prom/node-exporter:latest',
                    'container_name': 'node-exporter',
                    'ports': ['9100:9100'],
                    'volumes': [
                        '/proc:/host/proc:ro',
                        '/sys:/host/sys:ro',
                        '/:/rootfs:ro'
                    ],
                    'command': [
                        '--path.procfs=/host/proc',
                        '--path.rootfs=/rootfs',
                        '--path.sysfs=/host/sys',
                        '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
                    ],
                    'restart': 'unless-stopped'
                },
                'observatory-app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'observatory-app',
                    'ports': ['8888:8888'],
                    'volumes': [
                        './observatory_data:/app/observatory_data',
                        './logs:/app/logs'
                    ],
                    'environment': {
                        'REDIS_HOST': 'observatory-redis',
                        'REDIS_PASSWORD': '${REDIS_PASSWORD:-beastmode2025}',
                        'PROMETHEUS_URL': 'http://observatory-prometheus:9090',
                        'ENVIRONMENT': 'production'
                    },
                    'depends_on': {
                        'observatory-redis': {'condition': 'service_healthy'},
                        'observatory-prometheus': {'condition': 'service_healthy'}
                    },
                    'restart': 'unless-stopped',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8888/health'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 3
                    }
                },
                'cloudflare-tunnel': {
                    'image': 'cloudflare/cloudflared:latest',
                    'container_name': 'cloudflare-tunnel',
                    'volumes': [
                        './cloudflared-config.yml:/etc/cloudflared/config.yml:ro',
                        './tunnel-credentials.json:/etc/cloudflared/credentials.json:ro'
                    ],
                    'command': ['tunnel', '--config', '/etc/cloudflared/config.yml', 'run'],
                    'restart': 'unless-stopped',
                    'depends_on': {
                        'observatory-app': {'condition': 'service_healthy'},
                        'observatory-grafana': {'condition': 'service_healthy'}
                    }
                }
            },
            'volumes': {
                'redis-data': {},
                'prometheus-data': {},
                'grafana-storage': {}
            },
            'networks': {
                'default': {
                    'driver': 'bridge'
                }
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False)
    
    def create_dockerfile(self) -> str:
        """Create Dockerfile for Observatory."""
        return """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config logs

# Expose port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8888/health || exit 1

# Start Observatory
CMD ["python", "start_observatory.py"]
"""
    
    def create_cloudflared_config(self) -> str:
        """Create Cloudflare tunnel configuration."""
        config = {
            'tunnel': 'd1e53e43-033f-4994-8f46-c83962ae3785',
            'credentials-file': '/etc/cloudflared/credentials.json',
            'ingress': [
                {
                    'hostname': 'observatory.niclon.com',
                    'service': 'http://observatory-app:8888'
                },
                {
                    'hostname': 'grafana.vonnegut.poe.com', 
                    'service': 'http://observatory-grafana:3000'
                },
                {
                    'hostname': 'prometheus.vonnegut.poe.com',
                    'service': 'http://observatory-prometheus:9090'
                },
                {
                    'service': 'http_status:404'
                }
            ]
        }
        
        return yaml.dump(config, default_flow_style=False)
    
    def create_grafana_datasource(self) -> str:
        """Create Grafana datasource configuration."""
        datasource = {
            'apiVersion': 1,
            'datasources': [
                {
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'access': 'proxy',
                    'url': 'http://observatory-prometheus:9090',
                    'isDefault': True,
                    'editable': True
                }
            ]
        }
        
        return yaml.dump(datasource, default_flow_style=False)
    
    def create_deployment_package(self) -> Path:
        """Create complete deployment package."""
        print("📦 Creating containerized deployment package...")
        
        package_dir = Path("vonnegut_containerized_deployment")
        package_dir.mkdir(exist_ok=True)
        
        # Copy source files
        files_to_copy = [
            "start_observatory.py",
            "src/",
            "requirements.txt"
        ]
        
        for item in files_to_copy:
            if Path(item).exists():
                if Path(item).is_dir():
                    subprocess.run(["cp", "-r", item, str(package_dir)], check=True)
                else:
                    subprocess.run(["cp", item, str(package_dir)], check=True)
        
        # Create configuration files
        with open(package_dir / "docker-compose.yml", 'w') as f:
            f.write(self.create_docker_compose())
        
        with open(package_dir / "Dockerfile", 'w') as f:
            f.write(self.create_dockerfile())
        
        with open(package_dir / "prometheus.yml", 'w') as f:
            f.write(self.create_prometheus_config())
        
        with open(package_dir / "cloudflared-config.yml", 'w') as f:
            f.write(self.create_cloudflared_config())
        
        # Create Grafana provisioning
        grafana_dir = package_dir / "grafana-provisioning" / "datasources"
        grafana_dir.mkdir(parents=True, exist_ok=True)
        
        with open(grafana_dir / "prometheus.yml", 'w') as f:
            f.write(self.create_grafana_datasource())
        
        # Create environment file
        with open(package_dir / ".env", 'w') as f:
            f.write("""REDIS_PASSWORD=beastmode2025
GRAFANA_PASSWORD=admin
COMPOSE_PROJECT_NAME=observatory
""")
        
        # Copy tunnel credentials if available
        tunnel_creds = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
        if tunnel_creds.exists():
            subprocess.run(["cp", str(tunnel_creds), str(package_dir / "tunnel-credentials.json")])
            print("✅ Tunnel credentials copied")
        else:
            print("⚠️ Tunnel credentials not found - manual copy needed")
        
        print(f"✅ Deployment package created: {package_dir}")
        return package_dir
    
    def deploy_to_vonnegut(self, package_dir: Path) -> bool:
        """Deploy to Vonnegut server."""
        print(f"🚀 Deploying to Vonnegut ({self.vonnegut_ip})...")
        
        try:
            # Upload package
            subprocess.run([
                "rsync", "-avz", "--delete",
                f"{package_dir}/",
                f"{self.ssh_user}@{self.vonnegut_ip}:{self.remote_path}/"
            ], check=True)
            
            # Deploy on remote
            deploy_script = f"""
cd {self.remote_path}

# Stop existing containers
docker-compose down --remove-orphans 2>/dev/null || true

# Clean up old containers and volumes if needed
docker system prune -f

# Build and start services
docker-compose up -d --build

# Wait for services
sleep 60

# Check status
echo "=== Container Status ==="
docker-compose ps

echo "=== Observatory Logs ==="
docker logs observatory-app --tail=20

echo "=== Prometheus Logs ==="
docker logs observatory-prometheus --tail=10

echo "=== Grafana Logs ==="
docker logs observatory-grafana --tail=10

echo "=== Tunnel Logs ==="
docker logs cloudflare-tunnel --tail=10

echo "✅ Deployment complete!"
"""
            
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                deploy_script
            ], text=True, capture_output=True)
            
            print("📋 Deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Deployment stderr:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    def validate_deployment(self) -> bool:
        """Validate the deployment."""
        print("🔍 Validating deployment...")
        
        validation_script = f"""
cd {self.remote_path}

echo "=== Health Checks ==="
docker-compose exec -T observatory-app curl -f http://localhost:8888/health || echo "Observatory health check failed"
docker-compose exec -T observatory-prometheus wget -q --spider http://localhost:9090/-/healthy || echo "Prometheus health check failed"
docker-compose exec -T observatory-grafana curl -f http://localhost:3000/api/health || echo "Grafana health check failed"

echo "=== Service Status ==="
docker-compose ps

echo "=== Network Test ==="
docker-compose exec -T observatory-app curl -f http://observatory-prometheus:9090/api/v1/targets || echo "Prometheus connection failed"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                validation_script
            ], text=True, capture_output=True)
            
            print("📋 Validation output:")
            print(result.stdout)
            
            return "health check failed" not in result.stdout.lower()
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False

def main():
    """Main execution."""
    print("🐳 Vonnegut Containerized Observatory Deployment Fix")
    print("=" * 60)
    
    fixer = VonnegutContainerFix()
    
    # Create deployment package
    package_dir = fixer.create_deployment_package()
    
    # Deploy to Vonnegut
    if not fixer.deploy_to_vonnegut(package_dir):
        print("❌ Deployment failed")
        return False
    
    # Validate deployment
    if not fixer.validate_deployment():
        print("⚠️ Deployment completed but validation failed")
        return False
    
    print("\n🎉 Observatory containerized deployment successful!")
    print("🌐 Observatory: https://observatory.niclon.com")
    print("📊 Prometheus: https://prometheus.vonnegut.poe.com") 
    print("📈 Grafana: https://grafana.vonnegut.poe.com")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)