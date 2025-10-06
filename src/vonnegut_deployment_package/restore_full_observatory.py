#!/usr/bin/env python3
"""
Restore Full Observatory Stack
=============================

Restore the complete Observatory Docker Compose stack with all services
and recovered data to get back to full functionality.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def restore_full_observatory():
    """Restore the complete Observatory stack."""
    print("🚀 Restoring Full Observatory Stack")
    print("=" * 50)
    
    # Step 1: Navigate to deployment directory
    deployment_dir = Path("deployment/observatory")
    if not deployment_dir.exists():
        print(f"❌ Deployment directory not found: {deployment_dir}")
        return False
    
    os.chdir(deployment_dir)
    print(f"📁 Working in: {deployment_dir.absolute()}")
    
    # Step 2: Update config for Linux networking
    print("🔧 Configuring for Linux networking...")
    
    # Set Linux-specific environment variables
    env = os.environ.copy()
    env.update({
        'DOCKER_DESKTOP': 'false',  # We're on Linux, not Docker Desktop
        'REDIS_HOST': 'observatory-redis',  # Use container name, not host.docker.internal
    })
    
    # Step 3: Start the full stack
    print("🐳 Starting full Observatory Docker Compose stack...")
    
    try:
        result = subprocess.run([
            "docker-compose", "up", "-d"
        ], capture_output=True, text=True, timeout=300, env=env)
        
        if result.returncode == 0:
            print("✅ Docker Compose stack started successfully")
        else:
            print(f"❌ Docker Compose failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker Compose startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error starting Docker Compose: {e}")
        return False
    
    # Step 3: Wait for services to be healthy
    print("⏳ Waiting for services to become healthy...")
    time.sleep(30)
    
    # Step 4: Check service health
    services = [
        "beast-mode-observatory",
        "observatory-redis", 
        "observatory-prometheus",
        "observatory-grafana"
    ]
    
    for service in services:
        try:
            result = subprocess.run([
                "docker", "ps", "--filter", f"name={service}", "--format", "{{.Status}}"
            ], capture_output=True, text=True)
            
            if "healthy" in result.stdout or "Up" in result.stdout:
                print(f"✅ {service} is running")
            else:
                print(f"⚠️  {service} status: {result.stdout.strip()}")
                
        except Exception as e:
            print(f"❌ Error checking {service}: {e}")
    
    # Step 5: Test Observatory endpoint
    print("🔍 Testing Observatory endpoint...")
    time.sleep(10)
    
    try:
        import requests
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Observatory health check passed: {health}")
            return True
        else:
            print(f"⚠️  Observatory returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Observatory health check failed: {e}")
        return False

if __name__ == "__main__":
    success = restore_full_observatory()
    if success:
        print("\n🎉 Full Observatory stack restored successfully!")
        print("🌐 Observatory should be available at http://localhost:8888")
        print("📊 Grafana should be available at http://localhost:3000")
        print("📈 Prometheus should be available at http://localhost:9090")
    else:
        print("\n❌ Observatory restoration failed")
    
    sys.exit(0 if success else 1)