#!/usr/bin/env python3
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


def load_env_vars():
    """Load environment variables from ~/.env if it exists."""
    home_env = Path.home() / ".env"
    if home_env.exists():
        print(f"🔧 Loading environment variables from {home_env}")
        with open(home_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        return True
    else:
        print("⚠️ No ~/.env file found - using default configurations")
        return False


def deploy_observatory_containers():
    """Deploy Observatory using Docker Compose."""
    print("🚀 Deploying Observatory containers...")
    
    # Load environment variables
    load_env_vars()
    
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
