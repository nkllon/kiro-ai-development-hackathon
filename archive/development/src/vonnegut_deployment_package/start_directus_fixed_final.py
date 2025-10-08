#!/usr/bin/env python3
"""
Final Directus Fix - Start with correct network and health check
"""

import subprocess
import time

def start_directus_with_correct_network():
    """Start Directus with the correct network and fixed health check."""
    
    # Build docker run command with correct network
    docker_cmd = [
        'docker', 'run', '-d',
        '--name', 'directus_cms_fixed',
        '--restart', 'unless-stopped',
        '-p', '8055:8055',
        '--network', 'beast_mode_directus_network',  # Correct network
        
        # Environment variables
        '-e', 'KEY=replace-with-random-value',
        '-e', 'SECRET=replace-with-random-value',
        '-e', 'DB_CLIENT=pg',
        '-e', 'DB_HOST=directus_postgres_fixed',
        '-e', 'DB_PORT=5432',
        '-e', 'DB_DATABASE=directus',
        '-e', 'DB_USER=directus',
        '-e', 'DB_PASSWORD=directus',
        '-e', 'CACHE_ENABLED=true',
        '-e', 'CACHE_STORE=redis',
        '-e', 'REDIS=redis://directus_redis_fixed:6379',
        '-e', 'ADMIN_EMAIL=admin@example.com',
        '-e', 'ADMIN_PASSWORD=d1r3ctu5',
        
        # Fixed health check using curl with IPv4
        '--health-cmd', 'curl -f http://127.0.0.1:8055/server/health || exit 1',
        '--health-interval', '30s',
        '--health-timeout', '10s',
        '--health-retries', '3',
        '--health-start-period', '60s',
        
        # Image
        'directus/directus:10.8'
    ]
    
    print("🚀 Starting Directus with correct network and fixed health check...")
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        print(f"✅ Container started: {container_id[:12]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start: {e}")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    if start_directus_with_correct_network():
        print("⏳ Waiting 60 seconds for startup...")
        time.sleep(60)
        
        # Check status
        subprocess.run(['docker', 'ps', '--filter', 'name=directus_cms_fixed'])
        
        print("\n🏥 Health Check:")
        subprocess.run(['docker', 'inspect', 'directus_cms_fixed', '--format', '{{.State.Health.Status}}'])
        
        print("\n🌐 Testing endpoint:")
        subprocess.run(['curl', '-s', 'http://localhost:8055/server/health'])
        print()  # newline