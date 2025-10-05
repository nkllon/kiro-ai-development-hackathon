#!/usr/bin/env python3
"""
Poe Observatory Deployment Script
================================

Automated deployment of Observatory to Poe platform.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def deploy_to_poe():
    """Deploy Observatory to Poe platform."""
    print("🚀 Deploying Observatory to Poe...")
    
    # Load manifest
    with open('poe_manifest.json', 'r') as f:
        manifest = json.load(f)
    
    print(f"📦 Deploying {manifest['name']} v{manifest['version']}")
    
    # Step 1: Setup Docker containers
    print("🐳 Starting Docker containers...")
    subprocess.run([
        "docker-compose", "-f", "deployment/observatory/docker-compose.yml", 
        "up", "-d", "redis", "prometheus", "grafana"
    ])
    
    # Step 2: Setup data persistence
    print("💾 Setting up data persistence...")
    subprocess.run(["python", "setup_data_persistence.py"])
    
    # Step 3: Start Observatory
    print("🌟 Starting Observatory core...")
    subprocess.Popen(["python", "start_observatory.py"])
    
    # Step 4: Validate deployment
    print("✅ Validating deployment...")
    result = subprocess.run(["python", "validate_observatory_deployment.py"])
    
    if result.returncode == 0:
        print("🎉 Observatory deployed successfully to Poe!")
        print("🌐 Access at: https://observatory.nkllon.com")
        return True
    else:
        print("❌ Deployment validation failed")
        return False

if __name__ == "__main__":
    success = deploy_to_poe()
    sys.exit(0 if success else 1)
