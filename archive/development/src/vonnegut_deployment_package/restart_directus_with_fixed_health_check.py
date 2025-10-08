#!/usr/bin/env python3
"""
Simple Directus Health Check Fix
Recreates just the Directus container with a proper IPv4 health check
"""

import subprocess
import time
import json

def get_container_env(container_name: str) -> dict:
    """Extract environment variables from existing container."""
    try:
        result = subprocess.run([
            'docker', 'inspect', container_name, 
            '--format', '{{json .Config.Env}}'
        ], capture_output=True, text=True, check=True)
        
        env_list = json.loads(result.stdout.strip())
        env_dict = {}
        for env_var in env_list:
            if '=' in env_var:
                key, value = env_var.split('=', 1)
                env_dict[key] = value
        return env_dict
    except Exception as e:
        print(f"Warning: Could not extract environment: {e}")
        return {}

def restart_directus_with_fixed_health_check():
    """Restart Directus with a fixed health check."""
    print("🔧 Restarting Directus with fixed health check...")
    
    # Step 1: Get current environment variables
    print("📋 Extracting current configuration...")
    env_vars = get_container_env('directus_cms_fixed')
    
    # Step 2: Stop and remove current container
    print("🛑 Stopping current container...")
    try:
        subprocess.run(['docker', 'stop', 'directus_cms_fixed'], 
                      capture_output=True, check=True)
        print("✅ Container stopped")
    except subprocess.CalledProcessError:
        print("⚠️ Container was not running")
    
    print("🗑️ Removing current container...")
    try:
        subprocess.run(['docker', 'rm', 'directus_cms_fixed'], 
                      capture_output=True, check=True)
        print("✅ Container removed")
    except subprocess.CalledProcessError:
        print("⚠️ Container was already removed")
    
    # Step 3: Build docker run command with fixed health check
    docker_cmd = [
        'docker', 'run', '-d',
        '--name', 'directus_cms_fixed',
        '--restart', 'unless-stopped',
        '-p', '8055:8055',
        '--network', 'bridge'
    ]
    
    # Add environment variables
    essential_env = {
        'KEY': env_vars.get('KEY', 'replace-with-random-value'),
        'SECRET': env_vars.get('SECRET', 'replace-with-random-value'),
        'DB_CLIENT': env_vars.get('DB_CLIENT', 'pg'),
        'DB_HOST': env_vars.get('DB_HOST', 'directus_postgres_fixed'),
        'DB_PORT': env_vars.get('DB_PORT', '5432'),
        'DB_DATABASE': env_vars.get('DB_DATABASE', 'directus'),
        'DB_USER': env_vars.get('DB_USER', 'directus'),
        'DB_PASSWORD': env_vars.get('DB_PASSWORD', 'directus'),
        'CACHE_ENABLED': env_vars.get('CACHE_ENABLED', 'true'),
        'CACHE_STORE': env_vars.get('CACHE_STORE', 'redis'),
        'REDIS': env_vars.get('REDIS', 'redis://directus_redis_fixed:6379'),
        'ADMIN_EMAIL': env_vars.get('ADMIN_EMAIL', 'admin@example.com'),
        'ADMIN_PASSWORD': env_vars.get('ADMIN_PASSWORD', 'd1r3ctu5')
    }
    
    for key, value in essential_env.items():
        docker_cmd.extend(['-e', f'{key}={value}'])
    
    # Add fixed health check (using curl with IPv4)
    docker_cmd.extend([
        '--health-cmd', 'curl -f http://127.0.0.1:8055/server/health || exit 1',
        '--health-interval', '30s',
        '--health-timeout', '10s',
        '--health-retries', '3',
        '--health-start-period', '60s'
    ])
    
    # Add image
    docker_cmd.append('directus/directus:10.8')
    
    # Step 4: Start new container
    print("🚀 Starting new container with fixed health check...")
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        print("✅ New container started successfully")
        container_id = result.stdout.strip()
        print(f"📦 Container ID: {container_id[:12]}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start container: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Step 5: Wait for startup and validate
    print("⏳ Waiting for Directus to start (60 seconds)...")
    time.sleep(60)
    
    # Check container status
    try:
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=directus_cms_fixed',
            '--format', 'table {{.Names}}\t{{.Status}}'
        ], capture_output=True, text=True, check=True)
        print("📊 Container Status:")
        print(result.stdout)
    except Exception as e:
        print(f"⚠️ Could not check container status: {e}")
    
    # Check health status
    try:
        result = subprocess.run([
            'docker', 'inspect', 'directus_cms_fixed',
            '--format', '{{.State.Health.Status}}'
        ], capture_output=True, text=True, check=True)
        health_status = result.stdout.strip()
        if health_status == 'healthy':
            print(f"✅ Health Status: {health_status}")
        else:
            print(f"⚠️ Health Status: {health_status} (may still be starting)")
    except Exception as e:
        print(f"⚠️ Could not check health status: {e}")
    
    # Test health endpoint
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:8055/server/health'
        ], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Health Endpoint: {result.stdout.strip()}")
        else:
            print(f"⚠️ Health Endpoint: Failed to connect")
    except Exception as e:
        print(f"⚠️ Health Endpoint: {e}")
    
    return True

if __name__ == "__main__":
    print("🏥 Directus Health Check Fix - Simple Restart Method")
    print("=" * 55)
    
    success = restart_directus_with_fixed_health_check()
    
    if success:
        print("\n🎉 Directus restart completed!")
        print("\n📋 Next Steps:")
        print("1. Wait 2-3 minutes for full startup")
        print("2. Monitor with: docker logs directus_cms_fixed -f")
        print("3. Check health: docker inspect directus_cms_fixed --format '{{.State.Health.Status}}'")
        print("4. Test endpoint: curl http://localhost:8055/server/health")
    else:
        print("\n❌ Restart failed - check logs and try manual approach")