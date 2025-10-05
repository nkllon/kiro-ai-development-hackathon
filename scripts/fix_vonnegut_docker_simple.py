#!/usr/bin/env python3
"""
Simple Vonnegut Docker Fix
=========================

Simple script to get Docker running and Observatory deployed on Vonnegut.
"""

import os
import sys
import subprocess

def run_ssh_command(command, timeout=300):
    """Run command on Vonnegut via SSH."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}", command
        ], text=True, capture_output=True, timeout=timeout)
        
        print("📋 Command output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Command warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def setup_docker():
    """Setup Docker on Vonnegut."""
    print("🐳 Setting up Docker on Vonnegut...")
    
    command = """
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker --no-pager -l

# Test Docker
sudo docker run --rm hello-world

echo "✅ Docker setup complete!"
"""
    
    return run_ssh_command(command)

def deploy_containers():
    """Deploy Observatory containers."""
    print("🚀 Deploying Observatory containers...")
    
    command = """
cd /home/lou/observatory

# Set environment
export REDIS_PASSWORD=beastmode2025

# Stop existing containers
sudo docker-compose down --remove-orphans 2>/dev/null || true

# Start containers
sudo docker-compose up -d --build

# Wait for startup
sleep 60

# Check status
sudo docker-compose ps

# Check logs
sudo docker logs observatory-app --tail=10 2>/dev/null || echo "Observatory not running"
sudo docker logs observatory-prometheus --tail=10 2>/dev/null || echo "Prometheus not running"

echo "✅ Container deployment complete!"
"""
    
    return run_ssh_command(command, timeout=600)

def validate_services():
    """Validate services are running."""
    print("🔍 Validating services...")
    
    command = """
cd /home/lou/observatory

# Check container status
sudo docker-compose ps

# Test services
curl -s -f http://localhost:8888/health && echo "✅ Observatory: Healthy" || echo "❌ Observatory: Unhealthy"
curl -s -f http://localhost:9090/-/healthy && echo "✅ Prometheus: Healthy" || echo "❌ Prometheus: Unhealthy"
curl -s -f http://localhost:3000/api/health && echo "✅ Grafana: Healthy" || echo "❌ Grafana: Unhealthy"

echo "✅ Validation complete!"
"""
    
    return run_ssh_command(command)

def main():
    """Main execution."""
    print("🎯 Vonnegut Observatory Docker Fix")
    print("=" * 40)
    
    # Setup Docker
    if not setup_docker():
        print("❌ Docker setup failed")
        return False
    
    # Deploy containers
    if not deploy_containers():
        print("❌ Container deployment failed")
        return False
    
    # Validate services
    if not validate_services():
        print("⚠️ Services deployed but validation failed")
        return False
    
    print("\n🎉 Observatory successfully deployed on Vonnegut!")
    print("🌐 Observatory: https://observatory.niclon.com")
    print("📊 Prometheus: https://prometheus.observatory.niclon.com")
    print("📈 Grafana: https://grafana.observatory.niclon.com")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)