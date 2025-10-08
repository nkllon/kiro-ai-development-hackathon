#!/usr/bin/env python3
"""
Directus Health Check Fix Script
Root Cause: Docker health check using IPv6 localhost ([::1]) but service only listening on IPv4
Fix: Update health check to use IPv4 localhost (127.0.0.1) or 0.0.0.0
"""

import subprocess
import json
import time
from typing import Dict, Any

def get_container_info(container_name: str) -> Dict[str, Any]:
    """Get detailed container information."""
    try:
        result = subprocess.run([
            'docker', 'inspect', container_name
        ], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)[0]
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to inspect container: {e}"}

def test_health_endpoints() -> Dict[str, Any]:
    """Test various health check approaches."""
    tests = {}
    
    # Test external access
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:8055/server/health'
        ], capture_output=True, text=True, timeout=5)
        tests['external_curl'] = {
            'status': 'success' if result.returncode == 0 else 'failed',
            'response': result.stdout.strip(),
            'error': result.stderr.strip() if result.stderr else None
        }
    except Exception as e:
        tests['external_curl'] = {'status': 'error', 'error': str(e)}
    
    # Test internal IPv4
    try:
        result = subprocess.run([
            'docker', 'exec', 'directus_cms_fixed', 
            'wget', '--no-verbose', '--tries=1', '--spider', 
            'http://127.0.0.1:8055/server/health'
        ], capture_output=True, text=True, timeout=10)
        tests['internal_ipv4'] = {
            'status': 'success' if result.returncode == 0 else 'failed',
            'output': result.stdout.strip(),
            'error': result.stderr.strip() if result.stderr else None
        }
    except Exception as e:
        tests['internal_ipv4'] = {'status': 'error', 'error': str(e)}
    
    # Test internal with curl (if available)
    try:
        result = subprocess.run([
            'docker', 'exec', 'directus_cms_fixed', 
            'curl', '-s', 'http://127.0.0.1:8055/server/health'
        ], capture_output=True, text=True, timeout=10)
        tests['internal_curl'] = {
            'status': 'success' if result.returncode == 0 else 'failed',
            'response': result.stdout.strip(),
            'error': result.stderr.strip() if result.stderr else None
        }
    except Exception as e:
        tests['internal_curl'] = {'status': 'error', 'error': str(e)}
    
    return tests

def create_fixed_docker_compose() -> str:
    """Create a fixed docker-compose configuration."""
    compose_content = """version: '3.8'

services:
  directus_cms_fixed:
    image: directus/directus:10.8
    container_name: directus_cms_fixed
    restart: unless-stopped
    ports:
      - "8055:8055"
    environment:
      KEY: "replace-with-random-value"
      SECRET: "replace-with-random-value"
      DB_CLIENT: "pg"
      DB_HOST: "directus_postgres_fixed"
      DB_PORT: "5432"
      DB_DATABASE: "directus"
      DB_USER: "directus"
      DB_PASSWORD: "directus"
      CACHE_ENABLED: "true"
      CACHE_STORE: "redis"
      REDIS: "redis://directus_redis_fixed:6379"
      ADMIN_EMAIL: "admin@example.com"
      ADMIN_PASSWORD: "d1r3ctu5"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://127.0.0.1:8055/server/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    depends_on:
      - directus_postgres_fixed
      - directus_redis_fixed
    networks:
      - directus_network

  directus_postgres_fixed:
    image: postgres:15-alpine
    container_name: directus_postgres_fixed
    restart: unless-stopped
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: "directus"
      POSTGRES_USER: "directus"
      POSTGRES_PASSWORD: "directus"
    volumes:
      - directus_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U directus"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - directus_network

  directus_redis_fixed:
    image: redis:7-alpine
    container_name: directus_redis_fixed
    restart: unless-stopped
    ports:
      - "6380:6379"
    volumes:
      - directus_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - directus_network

volumes:
  directus_postgres_data:
  directus_redis_data:

networks:
  directus_network:
    driver: bridge
"""
    return compose_content

def apply_immediate_fix() -> Dict[str, Any]:
    """Apply immediate fix by recreating container with proper health check."""
    results = {}
    
    print("🔧 Applying immediate fix for Directus health check...")
    
    # Step 1: Stop the unhealthy container
    try:
        subprocess.run(['docker', 'stop', 'directus_cms_fixed'], 
                      capture_output=True, check=True)
        results['stop_container'] = 'success'
        print("✅ Stopped unhealthy container")
    except subprocess.CalledProcessError as e:
        results['stop_container'] = f'failed: {e}'
        print(f"❌ Failed to stop container: {e}")
        return results
    
    # Step 2: Remove the container
    try:
        subprocess.run(['docker', 'rm', 'directus_cms_fixed'], 
                      capture_output=True, check=True)
        results['remove_container'] = 'success'
        print("✅ Removed old container")
    except subprocess.CalledProcessError as e:
        results['remove_container'] = f'failed: {e}'
        print(f"❌ Failed to remove container: {e}")
    
    # Step 3: Create fixed docker-compose file
    compose_content = create_fixed_docker_compose()
    with open('docker-compose.directus-fixed.yml', 'w') as f:
        f.write(compose_content)
    results['create_compose'] = 'success'
    print("✅ Created fixed docker-compose configuration")
    
    # Step 4: Start with new configuration
    try:
        subprocess.run([
            'docker-compose', '-f', 'docker-compose.directus-fixed.yml', 
            'up', '-d', 'directus_cms_fixed'
        ], capture_output=True, check=True)
        results['start_container'] = 'success'
        print("✅ Started container with fixed health check")
    except subprocess.CalledProcessError as e:
        results['start_container'] = f'failed: {e}'
        print(f"❌ Failed to start container: {e}")
        return results
    
    # Step 5: Wait for startup
    print("⏳ Waiting for Directus to start...")
    time.sleep(30)
    
    # Step 6: Validate fix
    validation = validate_fix()
    results['validation'] = validation
    
    return results

def validate_fix() -> Dict[str, Any]:
    """Validate that the fix worked."""
    validation = {}
    
    # Check container status
    try:
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=directus_cms_fixed', 
            '--format', 'table {{.Names}}\t{{.Status}}'
        ], capture_output=True, text=True, check=True)
        validation['container_status'] = result.stdout.strip()
    except Exception as e:
        validation['container_status'] = f'error: {e}'
    
    # Check health status
    try:
        result = subprocess.run([
            'docker', 'inspect', 'directus_cms_fixed', 
            '--format', '{{.State.Health.Status}}'
        ], capture_output=True, text=True, check=True)
        validation['health_status'] = result.stdout.strip()
    except Exception as e:
        validation['health_status'] = f'error: {e}'
    
    # Test health endpoint
    try:
        result = subprocess.run([
            'curl', '-s', 'http://localhost:8055/server/health'
        ], capture_output=True, text=True, timeout=10)
        validation['health_endpoint'] = {
            'status': 'success' if result.returncode == 0 else 'failed',
            'response': result.stdout.strip()
        }
    except Exception as e:
        validation['health_endpoint'] = {'status': 'error', 'error': str(e)}
    
    return validation

def create_monitoring_script() -> str:
    """Create a monitoring script for ongoing health checks."""
    script_content = """#!/bin/bash
# Directus Health Monitoring Script
# Usage: ./monitor_directus_health.sh

echo "🏥 Directus Health Monitor"
echo "========================="

# Check container status
echo "📦 Container Status:"
docker ps --filter name=directus_cms_fixed --format "table {{.Names}}\\t{{.Status}}"

# Check health status
echo ""
echo "🩺 Health Status:"
HEALTH=$(docker inspect directus_cms_fixed --format '{{.State.Health.Status}}' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "✅ Container Health: $HEALTH"
else
    echo "❌ Container Health: $HEALTH"
fi

# Test health endpoint
echo ""
echo "🌐 Health Endpoint Test:"
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:8055/server/health)
HTTP_CODE="${RESPONSE: -3}"
BODY="${RESPONSE%???}"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HTTP Status: $HTTP_CODE"
    echo "📄 Response: $BODY"
else
    echo "❌ HTTP Status: $HTTP_CODE"
    echo "📄 Response: $BODY"
fi

# Check logs for errors
echo ""
echo "📋 Recent Logs (last 10 lines):"
docker logs directus_cms_fixed --tail 10

echo ""
echo "🔍 Health Check Logs:"
docker inspect directus_cms_fixed | jq '.[] | .State.Health.Log[-3:]' 2>/dev/null || echo "No health logs available"
"""
    return script_content

def main():
    """Main execution function."""
    print("🚨 Directus Health Check Diagnostic and Fix")
    print("=" * 50)
    
    # Step 1: Diagnose current state
    print("\n📊 Current State Analysis:")
    container_info = get_container_info('directus_cms_fixed')
    if 'error' in container_info:
        print(f"❌ {container_info['error']}")
        return
    
    health_status = container_info.get('State', {}).get('Health', {}).get('Status', 'unknown')
    print(f"🩺 Current Health Status: {health_status}")
    
    # Step 2: Test health endpoints
    print("\n🧪 Testing Health Endpoints:")
    tests = test_health_endpoints()
    for test_name, result in tests.items():
        status_icon = "✅" if result.get('status') == 'success' else "❌"
        print(f"{status_icon} {test_name}: {result.get('status', 'unknown')}")
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    # Step 3: Apply fix if needed
    if health_status != 'healthy':
        print(f"\n🔧 Health status is '{health_status}' - applying fix...")
        fix_results = apply_immediate_fix()
        
        print("\n📋 Fix Results:")
        for step, result in fix_results.items():
            status_icon = "✅" if result == 'success' or (isinstance(result, dict) and result.get('health_status') == 'healthy') else "❌"
            print(f"{status_icon} {step}: {result}")
    else:
        print("\n✅ Container is already healthy - no fix needed")
    
    # Step 4: Create monitoring tools
    print("\n🛠️ Creating Monitoring Tools:")
    
    # Create monitoring script
    monitor_script = create_monitoring_script()
    with open('scripts/monitor_directus_health.sh', 'w') as f:
        f.write(monitor_script)
    subprocess.run(['chmod', '+x', 'scripts/monitor_directus_health.sh'])
    print("✅ Created monitoring script: scripts/monitor_directus_health.sh")
    
    print("\n🎯 Recommendations for Permanent Elimination:")
    print("1. Use the fixed docker-compose.directus-fixed.yml configuration")
    print("2. Always use IPv4 localhost (127.0.0.1) in health checks")
    print("3. Install curl in Directus containers for more reliable health checks")
    print("4. Monitor health status with scripts/monitor_directus_health.sh")
    print("5. Consider upgrading to Directus 11.x for better health check support")
    
    print("\n✅ Directus health check fix completed!")

if __name__ == "__main__":
    main()