#!/usr/bin/env python3
"""
Fix Observatory Linux Networking
===============================

Remove macOS Docker Desktop cruft and configure for proper Linux networking.
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path

def fix_docker_compose_config():
    """Fix Docker Compose configuration for Linux."""
    print("🔧 Fixing Docker Compose configuration for Linux...")
    
    compose_file = Path("deployment/observatory/docker-compose.yml")
    if not compose_file.exists():
        print(f"❌ Docker Compose file not found: {compose_file}")
        return False
    
    # Read current config
    with open(compose_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Fix Observatory service environment
    if 'services' in config and 'observatory' in config['services']:
        env = config['services']['observatory'].get('environment', [])
        
        # Convert to dict if it's a list
        if isinstance(env, list):
            env_dict = {}
            for item in env:
                if '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
            env = env_dict
        
        # Fix macOS-specific settings
        env['DOCKER_DESKTOP'] = 'false'
        env['REDIS_HOST'] = 'observatory-redis'  # Use container name
        
        # Remove any host.docker.internal references
        for key, value in env.items():
            if isinstance(value, str) and 'host.docker.internal' in value:
                # Replace with proper container networking
                if 'redis' in value.lower():
                    env[key] = value.replace('host.docker.internal', 'observatory-redis')
                elif 'prometheus' in value.lower():
                    env[key] = value.replace('host.docker.internal', 'observatory-prometheus')
                elif 'grafana' in value.lower():
                    env[key] = value.replace('host.docker.internal', 'observatory-grafana')
        
        config['services']['observatory']['environment'] = env
        print("✅ Fixed Observatory environment variables")
    
    # Fix Grafana Redis session config
    if 'services' in config and 'grafana' in config['services']:
        env = config['services']['grafana'].get('environment', [])
        
        if isinstance(env, list):
            env_dict = {}
            for item in env:
                if '=' in item:
                    key, value = item.split('=', 1)
                    env_dict[key] = value
            env = env_dict
        
        # Fix Grafana Redis session provider
        if 'GF_SESSION_PROVIDER_CONFIG' in env:
            redis_config = env['GF_SESSION_PROVIDER_CONFIG']
            if 'host.docker.internal' in redis_config:
                env['GF_SESSION_PROVIDER_CONFIG'] = redis_config.replace('host.docker.internal', 'observatory-redis')
        
        config['services']['grafana']['environment'] = env
        print("✅ Fixed Grafana Redis configuration")
    
    # Write updated config
    with open(compose_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Updated Docker Compose configuration: {compose_file}")
    return True

def create_linux_override():
    """Create Linux-specific Docker Compose override."""
    print("📝 Creating Linux-specific Docker Compose override...")
    
    override_content = {
        'version': '3.8',
        'services': {
            'observatory': {
                'environment': {
                    'DOCKER_DESKTOP': 'false',
                    'REDIS_HOST': 'observatory-redis',
                    'PROMETHEUS_URL': 'http://observatory-prometheus:9090',
                    'GRAFANA_URL': 'http://observatory-grafana:3000',
                    'JAEGER_ENDPOINT': 'http://observatory-jaeger:14268/api/traces'
                }
            },
            'grafana': {
                'environment': {
                    'GF_SESSION_PROVIDER_CONFIG': 'addr=observatory-redis:6379,pool_size=100,db=1'
                }
            }
        }
    }
    
    override_file = Path("deployment/observatory/docker-compose.linux.yml")
    with open(override_file, 'w') as f:
        yaml.dump(override_content, f, default_flow_style=False)
    
    print(f"✅ Created Linux override: {override_file}")
    return True

def restore_with_linux_config():
    """Restore Observatory with Linux networking configuration."""
    print("🚀 Restoring Observatory with Linux networking...")
    
    deployment_dir = Path("deployment/observatory")
    if not deployment_dir.exists():
        print(f"❌ Deployment directory not found: {deployment_dir}")
        return False
    
    os.chdir(deployment_dir)
    
    # Stop any existing containers
    print("🛑 Stopping existing containers...")
    subprocess.run(["docker-compose", "down"], capture_output=True)
    
    # Start with Linux configuration
    print("🐳 Starting Observatory with Linux networking...")
    
    env = os.environ.copy()
    env.update({
        'DOCKER_DESKTOP': 'false',
        'COMPOSE_FILE': 'docker-compose.yml:docker-compose.linux.yml'
    })
    
    try:
        result = subprocess.run([
            "docker-compose", "up", "-d"
        ], capture_output=True, text=True, timeout=300, env=env)
        
        if result.returncode == 0:
            print("✅ Observatory stack started with Linux networking")
            return True
        else:
            print(f"❌ Failed to start stack: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def validate_linux_deployment():
    """Validate that Observatory is working with Linux networking."""
    print("🔍 Validating Linux deployment...")
    
    import time
    time.sleep(30)  # Wait for services to start
    
    try:
        import requests
        
        # Test Observatory
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Observatory health: {health}")
            
            # Check if it's no longer in emergency mode
            if health.get('mode') != 'emergency':
                print("🎉 Observatory is running in full mode!")
                return True
            else:
                print("⚠️  Observatory still in emergency mode")
                return False
        else:
            print(f"❌ Observatory returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def main():
    """Main execution."""
    print("🚀 Observatory Linux Networking Fix")
    print("=" * 50)
    
    # Step 1: Fix Docker Compose config
    if not fix_docker_compose_config():
        return False
    
    # Step 2: Create Linux override
    if not create_linux_override():
        return False
    
    # Step 3: Restore with Linux config
    if not restore_with_linux_config():
        return False
    
    # Step 4: Validate deployment
    if not validate_linux_deployment():
        print("⚠️  Deployment started but validation failed")
        return False
    
    print("\n🎉 Observatory Linux networking fix completed!")
    print("🌐 Observatory: http://localhost:8888")
    print("📊 Grafana: http://localhost:3000") 
    print("📈 Prometheus: http://localhost:9090")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)