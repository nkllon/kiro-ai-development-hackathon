#!/usr/bin/env python3
"""
Create Clean Linux Observatory Deployment
========================================

Create a proper Linux container deployment following the vonnegut pattern.
Clean, simple, no macOS cruft.
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path

def create_clean_docker_compose():
    """Create a clean Docker Compose file for Linux."""
    print("📝 Creating clean Linux Docker Compose configuration...")
    
    # Clean, simple configuration
    config = {
        'version': '3.8',
        'networks': {
            'observatory': {
                'driver': 'bridge'
            }
        },
        'volumes': {
            'prometheus_data': {},
            'grafana_data': {},
            'redis_data': {}
        },
        'services': {
            'redis': {
                'image': 'redis:7-alpine',
                'container_name': 'observatory-redis',
                'restart': 'unless-stopped',
                'networks': ['observatory'],
                'volumes': ['redis_data:/data'],
                'command': 'redis-server --appendonly yes'
            },
            'prometheus': {
                'image': 'prom/prometheus:latest',
                'container_name': 'observatory-prometheus',
                'restart': 'unless-stopped',
                'networks': ['observatory'],
                'ports': ['9090:9090'],
                'volumes': [
                    'prometheus_data:/prometheus',
                    './prometheus.yml:/etc/prometheus/prometheus.yml:ro'
                ],
                'command': [
                    '--config.file=/etc/prometheus/prometheus.yml',
                    '--storage.tsdb.path=/prometheus',
                    '--web.console.libraries=/etc/prometheus/console_libraries',
                    '--web.console.templates=/etc/prometheus/consoles',
                    '--storage.tsdb.retention.time=7d',
                    '--web.enable-lifecycle'
                ]
            },
            'grafana': {
                'image': 'grafana/grafana:latest',
                'container_name': 'observatory-grafana',
                'restart': 'unless-stopped',
                'networks': ['observatory'],
                'ports': ['3000:3000'],
                'volumes': ['grafana_data:/var/lib/grafana'],
                'environment': [
                    'GF_SECURITY_ADMIN_PASSWORD=admin',
                    'GF_USERS_ALLOW_SIGN_UP=false',
                    'GF_AUTH_ANONYMOUS_ENABLED=true',
                    'GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer'
                ],
                'depends_on': ['prometheus']
            },
            'observatory': {
                'build': {
                    'context': '../../',
                    'dockerfile': 'deployment/observatory/Dockerfile'
                },
                'image': 'beast-mode-observatory:latest',
                'container_name': 'beast-mode-observatory',
                'restart': 'unless-stopped',
                'networks': ['observatory'],
                'ports': ['8888:8888'],
                'environment': [
                    'OBSERVATORY_HOST=0.0.0.0',
                    'OBSERVATORY_PORT=8888',
                    'LOG_LEVEL=INFO',
                    'REDIS_HOST=redis',
                    'REDIS_PORT=6379',
                    'PROMETHEUS_URL=http://prometheus:9090',
                    'GRAFANA_URL=http://grafana:3000',
                    'DOCKER_DESKTOP=false'
                ],
                'depends_on': ['redis', 'prometheus', 'grafana'],
                'healthcheck': {
                    'test': ['CMD', 'curl', '-f', 'http://localhost:8888/health'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3,
                    'start_period': '60s'
                }
            }
        }
    }
    
    # Write clean config
    compose_file = Path("deployment/observatory/docker-compose.clean.yml")
    compose_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(compose_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Created clean Docker Compose: {compose_file}")
    return compose_file

def create_prometheus_config():
    """Create a simple Prometheus configuration."""
    print("📊 Creating Prometheus configuration...")
    
    prometheus_config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s'
        },
        'scrape_configs': [
            {
                'job_name': 'observatory',
                'static_configs': [
                    {'targets': ['observatory:8888']}
                ],
                'metrics_path': '/metrics',
                'scrape_interval': '10s'
            },
            {
                'job_name': 'prometheus',
                'static_configs': [
                    {'targets': ['localhost:9090']}
                ]
            }
        ]
    }
    
    config_file = Path("deployment/observatory/prometheus.yml")
    with open(config_file, 'w') as f:
        yaml.dump(prometheus_config, f, default_flow_style=False)
    
    print(f"✅ Created Prometheus config: {config_file}")
    return config_file

def stop_existing_containers():
    """Stop any existing Observatory containers."""
    print("🛑 Stopping existing containers...")
    
    # Stop the complex stack
    deployment_dir = Path("deployment/observatory")
    if deployment_dir.exists():
        os.chdir(deployment_dir)
        subprocess.run(["docker-compose", "down"], capture_output=True)
    
    # Stop any remaining Observatory containers
    containers = [
        "beast-mode-observatory",
        "observatory-redis", 
        "observatory-prometheus",
        "observatory-grafana",
        "observatory-jaeger",
        "observatory-engagement-manager",
        "observatory-cloudflare-tunnel"
    ]
    
    for container in containers:
        subprocess.run(["docker", "stop", container], capture_output=True)
        subprocess.run(["docker", "rm", container], capture_output=True)
    
    print("✅ Existing containers stopped")

def start_clean_deployment(compose_file):
    """Start the clean deployment."""
    print("🚀 Starting clean Observatory deployment...")
    
    deployment_dir = Path("deployment/observatory")
    os.chdir(deployment_dir)
    
    try:
        result = subprocess.run([
            "docker-compose", "-f", compose_file.name, "up", "-d"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Clean deployment started successfully")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def validate_clean_deployment():
    """Validate the clean deployment."""
    print("🔍 Validating clean deployment...")
    
    import time
    time.sleep(45)  # Give services time to start
    
    # Check container status
    containers = ["observatory-redis", "observatory-prometheus", "observatory-grafana", "beast-mode-observatory"]
    
    for container in containers:
        try:
            result = subprocess.run([
                "docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"
            ], capture_output=True, text=True)
            
            if "Up" in result.stdout:
                print(f"✅ {container} is running")
            else:
                print(f"❌ {container} status: {result.stdout.strip()}")
                
        except Exception as e:
            print(f"❌ Error checking {container}: {e}")
    
    # Test Observatory endpoint
    try:
        import requests
        response = requests.get("http://localhost:8888/health", timeout=15)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Observatory health: {health}")
            
            # Check if it's out of emergency mode
            if health.get('mode') not in ['emergency', 'minimal']:
                print("🎉 Observatory is running in full mode!")
                return True
            else:
                print(f"⚠️  Observatory in {health.get('mode', 'unknown')} mode")
                return False
        else:
            print(f"❌ Observatory returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Observatory validation failed: {e}")
        return False

def main():
    """Main execution."""
    print("🚀 Clean Linux Observatory Deployment")
    print("=" * 50)
    
    # Step 1: Stop existing containers
    stop_existing_containers()
    
    # Step 2: Create clean Docker Compose
    compose_file = create_clean_docker_compose()
    
    # Step 3: Create Prometheus config
    create_prometheus_config()
    
    # Step 4: Start clean deployment
    if not start_clean_deployment(compose_file):
        return False
    
    # Step 5: Validate deployment
    if not validate_clean_deployment():
        print("⚠️  Deployment started but validation failed")
        return False
    
    print("\n🎉 Clean Linux Observatory deployment completed!")
    print("🌐 Observatory: http://localhost:8888")
    print("📊 Grafana: http://localhost:3000")
    print("📈 Prometheus: http://localhost:9090")
    print("🔧 Management: docker-compose -f docker-compose.clean.yml")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)