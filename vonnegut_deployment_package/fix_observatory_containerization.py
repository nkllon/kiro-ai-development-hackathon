#!/usr/bin/env python3
"""
Observatory Containerization Fix
Root Cause: Observatory service running as bare Python process instead of Docker container
Fix: Implement proper containerized deployment with Docker Compose integration
"""

import os
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, Any


def create_observatory_dockerfile():
    """Create Dockerfile for Observatory service."""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY start_observatory.py .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Expose ports
EXPOSE 8888 8889 8890

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost:8888/health || exit 1

# Run Observatory service
CMD ["python", "start_observatory.py"]
"""
    
    with open("deployment/observatory/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Created Observatory Dockerfile")


def create_observatory_docker_compose():
    """Create Docker Compose configuration for Observatory."""
    compose_config = {
        'version': '3.8',
        'services': {
            'observatory': {
                'build': {
                    'context': '../../',
                    'dockerfile': 'deployment/observatory/Dockerfile'
                },
                'image': 'beast-mode-observatory:latest',
                'container_name': 'beast-mode-observatory',
                'restart': 'unless-stopped',
                'ports': [
                    '8888:8888',  # Main Observatory service
                    '8889:8889',  # WebSocket service
                    '8890:8890'   # Health monitor
                ],
                'environment': [
                    'OBSERVATORY_HOST=0.0.0.0',
                    'OBSERVATORY_PORT=8888',
                    'WEBSOCKET_PORT=8889',
                    'HEALTH_MONITOR_PORT=8890',
                    'LOG_LEVEL=INFO'
                ],
                'volumes': [
                    'observatory_data:/app/data',
                    'observatory_logs:/app/logs',
                    '/etc/localtime:/etc/localtime:ro'
                ],
                'networks': ['observatory-network'],
                'healthcheck': {
                    'test': ['CMD', 'curl', '-f', 'http://localhost:8888/health'],
                    'interval': '30s',
                    'timeout': '10s',
                    'retries': 3,
                    'start_period': '60s'
                },
                'deploy': {
                    'resources': {
                        'limits': {
                            'memory': '512M',
                            'cpus': '1.0'
                        },
                        'reservations': {
                            'memory': '256M',
                            'cpus': '0.5'
                        }
                    }
                }
            },
            'prometheus': {
                'image': 'prom/prometheus:latest',
                'container_name': 'observatory-prometheus',
                'restart': 'unless-stopped',
                'ports': ['9090:9090'],
                'volumes': [
                    './prometheus.yml:/etc/prometheus/prometheus.yml:ro',
                    'prometheus_data:/prometheus'
                ],
                'networks': ['observatory-network'],
                'command': [
                    '--config.file=/etc/prometheus/prometheus.yml',
                    '--storage.tsdb.path=/prometheus',
                    '--web.console.libraries=/etc/prometheus/console_libraries',
                    '--web.console.templates=/etc/prometheus/consoles',
                    '--storage.tsdb.retention.time=30d',
                    '--web.enable-lifecycle'
                ]
            },
            'grafana': {
                'image': 'grafana/grafana:latest',
                'container_name': 'observatory-grafana',
                'restart': 'unless-stopped',
                'ports': ['3000:3000'],
                'environment': [
                    'GF_SECURITY_ADMIN_PASSWORD=admin',
                    'GF_USERS_ALLOW_SIGN_UP=false'
                ],
                'volumes': [
                    'grafana_data:/var/lib/grafana'
                ],
                'networks': ['observatory-network'],
                'depends_on': ['prometheus']
            }
        },
        'volumes': {
            'observatory_data': {'driver': 'local'},
            'observatory_logs': {'driver': 'local'},
            'prometheus_data': {'driver': 'local'},
            'grafana_data': {'driver': 'local'}
        },
        'networks': {
            'observatory-network': {
                'driver': 'bridge'
            }
        }
    }
    
    os.makedirs("deployment/observatory", exist_ok=True)
    
    with open("deployment/observatory/docker-compose.yml", "w") as f:
        yaml.dump(compose_config, f, default_flow_style=False, indent=2)
    
    print("✅ Created Observatory Docker Compose configuration")


def create_observatory_prometheus_config():
    """Create Prometheus configuration for Observatory."""
    prometheus_config = {
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
                'static_configs': [{'targets': ['observatory:8888']}],
                'metrics_path': '/metrics',
                'scrape_interval': '5s'
            }
        ]
    }
    
    with open("deployment/observatory/prometheus.yml", "w") as f:
        yaml.dump(prometheus_config, f, default_flow_style=False, indent=2)
    
    print("✅ Created Observatory Prometheus configuration")


def fix_deploy_observatory_script():
    """Fix the deploy_observatory.py script to use Docker containers."""
    script_content = '''#!/usr/bin/env python3
"""
Deploy Observatory using Docker containers.
Fixed to use proper containerization instead of bare Python processes.
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, description="", check=True):
    """Run a command with proper logging."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False


def stop_existing_containers():
    """Stop any existing Observatory containers."""
    print("🛑 Stopping existing Observatory containers...")
    
    containers = [
        "beast-mode-observatory",
        "observatory-prometheus", 
        "observatory-grafana"
    ]
    
    for container in containers:
        run_command(f"docker stop {container}", f"Stopping {container}", check=False)
        run_command(f"docker rm {container}", f"Removing {container}", check=False)


def deploy_observatory_containers():
    """Deploy Observatory using Docker Compose."""
    print("🚀 Deploying Observatory containers...")
    
    # Change to deployment directory
    deployment_dir = Path("deployment/observatory")
    if not deployment_dir.exists():
        print("❌ Observatory deployment directory not found")
        return False
    
    os.chdir(deployment_dir)
    
    # Build and start containers
    if not run_command("docker-compose build", "Building Observatory containers"):
        return False
    
    if not run_command("docker-compose up -d", "Starting Observatory containers"):
        return False
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(30)
    
    # Verify containers are running
    if not run_command("docker-compose ps", "Checking container status"):
        return False
    
    return True


def verify_deployment():
    """Verify Observatory deployment is working."""
    print("🔍 Verifying Observatory deployment...")
    
    # Test Observatory health endpoint
    if run_command("curl -f http://localhost:8888/health", "Testing Observatory health", check=False):
        print("✅ Observatory service is healthy")
    else:
        print("❌ Observatory service health check failed")
        return False
    
    # Test Prometheus
    if run_command("curl -f http://localhost:9090/-/healthy", "Testing Prometheus health", check=False):
        print("✅ Prometheus service is healthy")
    else:
        print("❌ Prometheus service health check failed")
        return False
    
    # Test Grafana
    if run_command("curl -f http://localhost:3000/api/health", "Testing Grafana health", check=False):
        print("✅ Grafana service is healthy")
    else:
        print("❌ Grafana service health check failed")
        return False
    
    return True


def main():
    """Main deployment function."""
    print("🔭 Observatory Container Deployment")
    print("=" * 50)
    
    # Stop existing containers
    stop_existing_containers()
    
    # Deploy new containers
    if not deploy_observatory_containers():
        print("❌ Observatory deployment failed")
        return 1
    
    # Verify deployment
    if not verify_deployment():
        print("❌ Observatory verification failed")
        return 1
    
    print("🎉 Observatory deployment completed successfully!")
    print("📊 Services available at:")
    print("  - Observatory: http://localhost:8888")
    print("  - Prometheus: http://localhost:9090") 
    print("  - Grafana: http://localhost:3000")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open("scripts/deploy_observatory.py", "w") as f:
        f.write(script_content)
    
    os.chmod("scripts/deploy_observatory.py", 0o755)
    print("✅ Fixed deploy_observatory.py script")


def update_makefile_targets():
    """Update Makefile targets to use proper containerization."""
    makefile_updates = """
# Updated Observatory targets for proper containerization

observatory-start: ## Start Observatory services in Docker containers
	@echo '🔭 Starting Observatory services in containers...'
	python scripts/deploy_observatory.py
	@echo '✅ Observatory services started'

observatory-stop: ## Stop Observatory services and containers
	@echo '🔭 Stopping Observatory services and containers...'
	python scripts/stop_observatory.py
	@echo '✅ Observatory services stopped'

observatory-restart: ## Restart Observatory services
	@echo '🔭 Restarting Observatory services...'
	$(MAKE) observatory-stop
	sleep 5
	$(MAKE) observatory-start
	@echo '✅ Observatory services restarted'

observatory-logs: ## View Observatory container logs
	@echo '🔭 Observatory Container Logs:'
	@echo '============================'
	@docker logs beast-mode-observatory --tail=50 2>/dev/null || echo 'Observatory container not running'
	@docker logs observatory-prometheus --tail=20 2>/dev/null || echo 'Prometheus container not running'
	@docker logs observatory-grafana --tail=20 2>/dev/null || echo 'Grafana container not running'

observatory-shell: ## Access Observatory container shell
	@echo '🔭 Accessing Observatory container shell...'
	docker exec -it beast-mode-observatory /bin/bash

observatory-build: ## Build Observatory Docker images
	@echo '🔭 Building Observatory Docker images...'
	cd deployment/observatory && docker-compose build
	@echo '✅ Observatory images built'
"""
    
    print("📋 Makefile updates prepared (manual integration needed)")
    print("Add these targets to the Observatory section of the Makefile:")
    print(makefile_updates)


def update_requirements():
    """Update requirements to reflect containerization needs."""
    requirements_update = """
## Updated Requirements for Observatory Containerization

### Requirement 32: Observatory Container Architecture
**User Story**: As a system administrator, I need the Observatory service to run in Docker containers for consistent deployment and isolation.

**Acceptance Criteria**:
- Observatory service runs in dedicated Docker container
- Container includes all necessary dependencies and configurations
- Health checks verify container and service status
- Container integrates with existing Prometheus and Grafana containers
- Makefile targets manage containerized deployment lifecycle

**Technical Requirements**:
- Dockerfile for Observatory service in `deployment/observatory/`
- Docker Compose configuration for full Observatory stack
- Container health checks on ports 8888, 8889, 8890
- Volume mounts for persistent data and logs
- Network configuration for inter-container communication

### Requirement 33: Containerized Service Management
**User Story**: As a developer, I need Makefile targets that properly manage containerized Observatory services.

**Acceptance Criteria**:
- `make observatory-start` deploys containers using Docker Compose
- `make observatory-stop` stops and removes Observatory containers
- `make observatory-restart` performs clean restart of containerized services
- `make observatory-logs` shows container logs for debugging
- `make observatory-shell` provides container shell access

**Technical Requirements**:
- Updated `scripts/deploy_observatory.py` for container deployment
- Container lifecycle management in stop script
- Proper error handling for container operations
- Integration with existing Cloudflare tunnel configuration

### Requirement 34: Container Health Monitoring
**User Story**: As a system operator, I need comprehensive health monitoring for containerized Observatory services.

**Acceptance Criteria**:
- Docker health checks verify service availability
- Health endpoints accessible through container networking
- Monitoring integrates with existing Prometheus metrics
- Container status visible in `make observatory-status`
- Automatic restart on container health failures

**Technical Requirements**:
- Health check configuration in Dockerfile and Docker Compose
- Container networking allows health endpoint access
- Integration with existing monitoring infrastructure
- Status reporting includes container state information
"""
    
    # Find and update requirements file
    req_files = [
        ".kiro/specs/beast-mode-deployment-architecture/requirements.md",
        ".kiro/specs/observatory-deployment/requirements.md"
    ]
    
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, "a") as f:
                f.write(requirements_update)
            print(f"✅ Updated requirements in {req_file}")
            break
    else:
        # Create new requirements file
        os.makedirs(".kiro/specs/observatory-containerization", exist_ok=True)
        with open(".kiro/specs/observatory-containerization/requirements.md", "w") as f:
            f.write(requirements_update)
        print("✅ Created new requirements file for Observatory containerization")


def main():
    """Main function to apply Observatory containerization fix."""
    print("🔧 Observatory Containerization Fix")
    print("=" * 50)
    
    print("\n📦 Creating Docker configurations...")
    create_observatory_dockerfile()
    create_observatory_docker_compose()
    create_observatory_prometheus_config()
    
    print("\n🔧 Fixing deployment scripts...")
    fix_deploy_observatory_script()
    
    print("\n📋 Updating Makefile targets...")
    update_makefile_targets()
    
    print("\n📝 Updating requirements...")
    update_requirements()
    
    print("\n🎉 Observatory containerization fix completed!")
    print("\n📋 Next Steps:")
    print("1. Review and integrate Makefile target updates")
    print("2. Test container deployment: make observatory-start")
    print("3. Verify services: make observatory-status")
    print("4. Update Cloudflare tunnel to connect to containerized service")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())