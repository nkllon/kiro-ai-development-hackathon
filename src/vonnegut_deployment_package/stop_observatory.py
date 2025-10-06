#!/usr/bin/env python3
"""
Stop Observatory services - both Docker containers and Python processes.
Comprehensive shutdown script for Beast Mode Observatory system.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description="", ignore_errors=False):
    """Run a command with proper logging."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 or ignore_errors:
            if result.stdout.strip():
                print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def stop_python_processes():
    """Stop all Observatory-related Python processes."""
    print("\n🐍 Stopping Python Observatory processes...")
    
    # Find and kill Observatory processes
    observatory_patterns = [
        "src.beast_mode.observatory.main",
        "start_observatory",
        "observatory_server",
        "scripts/start_observatory_production.py"
    ]
    
    for pattern in observatory_patterns:
        cmd = f"pkill -f '{pattern}'"
        run_command(cmd, f"Killing processes matching: {pattern}", ignore_errors=True)
    
    # Give processes time to shut down gracefully
    time.sleep(2)
    
    # Force kill if still running
    for pattern in observatory_patterns:
        cmd = f"pkill -9 -f '{pattern}'"
        run_command(cmd, f"Force killing processes matching: {pattern}", ignore_errors=True)


def stop_docker_containers():
    """Stop Observatory-related Docker containers."""
    print("\n🐳 Stopping Docker Observatory containers...")
    
    # Observatory-related containers (both old and new naming)
    containers = [
        # New containerized Observatory containers
        "beast-mode-observatory",
        "observatory-prometheus",
        "observatory-grafana",
        "observatory-jaeger",
        "observatory-engagement-manager",
        "observatory-redis",
        "observatory-cloudflare-tunnel",
        # Legacy containers
        "local-grafana-1",
        "local-prometheus-1", 
        "local-beast-mode-metrics-1",
        "local-nginx-1",
        "local-directus-1",
        "local-systematic-pdca-orchestrator-1"
    ]
    
    for container in containers:
        run_command(f"docker stop {container}", f"Stopping container: {container}", ignore_errors=True)
    
    # Stop using Docker Compose if in Observatory deployment directory
    observatory_compose = "deployment/observatory/docker-compose.yml"
    if os.path.exists(observatory_compose):
        print("\n🐳 Stopping Observatory Docker Compose stack...")
        run_command(f"cd deployment/observatory && docker-compose down", "Stopping Observatory stack", ignore_errors=True)


def stop_cloudflare_tunnel():
    """Stop Cloudflare tunnel if running."""
    print("\n☁️ Stopping Cloudflare tunnel...")
    run_command("pkill -f 'cloudflared tunnel'", "Stopping Cloudflare tunnel", ignore_errors=True)


def check_remaining_processes():
    """Check if any Observatory processes are still running."""
    print("\n🔍 Checking for remaining Observatory processes...")
    
    cmd = "ps aux | grep -E '(observatory|prometheus|grafana)' | grep -v grep | grep -v 'stop_observatory.py'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        # Filter out the current script and make processes
        lines = result.stdout.strip().split('\n')
        filtered_lines = []
        for line in lines:
            if 'stop_observatory.py' not in line and 'make observatory-stop' not in line:
                filtered_lines.append(line)
        
        if filtered_lines:
            print("⚠️ Some processes may still be running:")
            for line in filtered_lines:
                print(line)
            return False
        else:
            print("✅ No Observatory processes found running")
            return True
    else:
        print("✅ No Observatory processes found running")
        return True


def check_docker_status():
    """Check Docker container status."""
    print("\n🐳 Checking Docker container status...")
    
    cmd = "docker ps | grep -E '(grafana|prometheus|beast-mode|nginx|pdca)'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        print("⚠️ Some Observatory containers may still be running:")
        print(result.stdout)
        return False
    else:
        print("✅ No Observatory containers found running")
        
    # Check if database is still running (this is often intentional)
    db_cmd = "docker ps | grep -E '(directus.*db|postgres)'"
    db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True)
    
    if db_result.stdout.strip():
        print("ℹ️ Database containers still running (this may be intentional):")
        print(db_result.stdout)
        
    return True


def main():
    """Main function to stop all Observatory services."""
    print("🛑 Stopping Beast Mode Observatory System")
    print("=" * 50)
    
    # Stop Python processes first
    stop_python_processes()
    
    # Stop Docker containers
    stop_docker_containers()
    
    # Stop Cloudflare tunnel
    stop_cloudflare_tunnel()
    
    # Wait a moment for everything to shut down
    print("\n⏳ Waiting for services to shut down...")
    time.sleep(3)
    
    # Check status
    print("\n📊 Final Status Check")
    print("=" * 30)
    
    processes_clean = check_remaining_processes()
    containers_clean = check_docker_status()
    
    if processes_clean and containers_clean:
        print("\n🎉 Observatory system stopped successfully!")
        print("✅ All services have been shut down cleanly")
        return 0
    else:
        print("\n⚠️ Some services may still be running")
        print("💡 You may need to manually stop remaining processes")
        return 1


if __name__ == "__main__":
    sys.exit(main())