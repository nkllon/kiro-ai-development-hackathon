#!/usr/bin/env python3
"""
🚨 EMERGENCY OBSERVATORY RECOVERY SCRIPT
Observer Mode - Debug, Patch, and Restore Production Observatory

This script diagnoses and fixes the production Observatory deployment.
"""

import subprocess
import sys
import time
import os
from pathlib import Path


def run_command(cmd, description="", check=True, capture_output=True):
    """Run a command with proper logging."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=check)
        if result.stdout and result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        if result.stderr and result.stderr.strip():
            print(f"⚠️  {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False, "", str(e)


def check_production_status():
    """Check current production Observatory status."""
    print("🔍 CHECKING PRODUCTION OBSERVATORY STATUS")
    print("=" * 50)
    
    # Test external endpoints
    success, stdout, stderr = run_command(
        "curl -s -w '%{http_code}' https://observatory.nkllon.com/health", 
        "Testing Observatory health endpoint"
    )
    
    success2, stdout2, stderr2 = run_command(
        "curl -s -w '%{http_code}' https://observatory.nkllon.com/api/observatory/status", 
        "Testing Observatory status endpoint"
    )
    
    # Check if containers are running locally (if this is the production server)
    success3, stdout3, stderr3 = run_command(
        "docker ps | grep observatory", 
        "Checking Observatory containers", 
        check=False
    )
    
    return {
        "health_endpoint": "502" not in stdout if stdout else False,
        "status_endpoint": "502" not in stdout2 if stdout2 else False,
        "containers_running": "observatory" in stdout3 if stdout3 else False
    }


def diagnose_issues():
    """Diagnose specific issues with the Observatory deployment."""
    print("🔍 DIAGNOSING OBSERVATORY ISSUES")
    print("=" * 40)
    
    issues = []
    
    # Check if we're on the production server
    success, stdout, stderr = run_command("hostname", "Checking hostname")
    if "vonnegut" not in stdout.lower():
        issues.append("NOT_ON_PRODUCTION_SERVER")
        print("⚠️  Not running on production server (vonnegut)")
    
    # Check Docker status
    success, stdout, stderr = run_command("docker --version", "Checking Docker", check=False)
    if not success:
        issues.append("DOCKER_NOT_AVAILABLE")
    
    # Check if containers exist
    success, stdout, stderr = run_command("docker ps -a | grep observatory", "Checking Observatory containers", check=False)
    if not success or not stdout:
        issues.append("NO_OBSERVATORY_CONTAINERS")
    else:
        # Check container health
        if "unhealthy" in stdout:
            issues.append("UNHEALTHY_CONTAINERS")
        if "exited" in stdout.lower():
            issues.append("STOPPED_CONTAINERS")
    
    # Check if deployment directory exists
    if not Path("deployment/observatory").exists():
        issues.append("NO_DEPLOYMENT_CONFIG")
    
    # Check if requirements.txt is up to date
    if Path("pyproject.toml").exists() and Path("requirements.txt").exists():
        success, stdout, stderr = run_command(
            "python scripts/generate_requirements.py --validate-only", 
            "Checking dependency sync", 
            check=False
        )
        if not success:
            issues.append("DEPENDENCIES_OUT_OF_SYNC")
    
    return issues


def fix_dependencies():
    """Fix dependency synchronization issues."""
    print("🔧 FIXING DEPENDENCY SYNCHRONIZATION")
    print("=" * 40)
    
    if not Path("scripts/generate_requirements.py").exists():
        print("❌ Dependency management script not found")
        return False
    
    # Regenerate requirements.txt
    success, stdout, stderr = run_command(
        "python scripts/generate_requirements.py", 
        "Regenerating requirements.txt"
    )
    
    return success


def rebuild_containers():
    """Rebuild Observatory containers with updated dependencies."""
    print("🔧 REBUILDING OBSERVATORY CONTAINERS")
    print("=" * 40)
    
    deployment_dir = Path("deployment/observatory")
    if not deployment_dir.exists():
        print("❌ Observatory deployment directory not found")
        return False
    
    # Change to deployment directory
    original_dir = os.getcwd()
    os.chdir(deployment_dir)
    
    try:
        # Stop existing containers
        run_command("docker-compose down", "Stopping existing containers", check=False)
        
        # Build new containers
        success, stdout, stderr = run_command(
            "docker-compose build --no-cache observatory", 
            "Building Observatory container"
        )
        
        if not success:
            print("❌ Failed to build Observatory container")
            return False
        
        # Start containers
        success, stdout, stderr = run_command(
            "docker-compose up -d", 
            "Starting Observatory containers"
        )
        
        return success
        
    finally:
        os.chdir(original_dir)


def verify_recovery():
    """Verify that Observatory has been recovered."""
    print("🔍 VERIFYING OBSERVATORY RECOVERY")
    print("=" * 40)
    
    # Wait for containers to start
    print("⏳ Waiting for containers to start...")
    time.sleep(30)
    
    # Check container status
    success, stdout, stderr = run_command(
        "docker ps | grep observatory", 
        "Checking container status"
    )
    
    if not success or not stdout:
        print("❌ No Observatory containers running")
        return False
    
    # Wait a bit more for health checks
    print("⏳ Waiting for health checks...")
    time.sleep(30)
    
    # Test local endpoints first
    success, stdout, stderr = run_command(
        "curl -f http://localhost:8888/health", 
        "Testing local Observatory health", 
        check=False
    )
    
    if success:
        print("✅ Local Observatory health check passed")
    else:
        print("❌ Local Observatory health check failed")
        # Check container logs
        run_command(
            "docker logs beast-mode-observatory --tail 20", 
            "Observatory container logs", 
            check=False
        )
    
    # Test external endpoints
    time.sleep(10)  # Give Cloudflare tunnel time to update
    
    success2, stdout2, stderr2 = run_command(
        "curl -s -w '%{http_code}' https://observatory.nkllon.com/health", 
        "Testing external Observatory health", 
        check=False
    )
    
    if "200" in stdout2:
        print("✅ External Observatory health check passed")
        return True
    else:
        print("❌ External Observatory health check failed")
        print(f"Response: {stdout2}")
        return False


def emergency_recovery():
    """Execute emergency recovery procedure."""
    print("🚨 EMERGENCY OBSERVATORY RECOVERY")
    print("=" * 50)
    print("Observer Mode: Diagnose → Patch → Restore")
    print()
    
    # Step 1: Check current status
    status = check_production_status()
    print(f"Current status: {status}")
    
    if status["health_endpoint"] and status["status_endpoint"]:
        print("✅ Observatory appears to be working!")
        return True
    
    # Step 2: Diagnose issues
    issues = diagnose_issues()
    print(f"Issues found: {issues}")
    
    if not issues:
        print("🤔 No obvious issues found, but Observatory is still down")
        print("Proceeding with container restart...")
    
    # Step 3: Apply fixes
    if "DEPENDENCIES_OUT_OF_SYNC" in issues:
        if not fix_dependencies():
            print("❌ Failed to fix dependencies")
            return False
    
    # Step 4: Rebuild and restart containers
    if not rebuild_containers():
        print("❌ Failed to rebuild containers")
        return False
    
    # Step 5: Verify recovery
    if verify_recovery():
        print("🎉 OBSERVATORY RECOVERY SUCCESSFUL!")
        print("📊 Services should be available at:")
        print("  - Observatory: https://observatory.nkllon.com")
        print("  - Prometheus: https://prometheus.observatory.nkllon.com")
        print("  - Grafana: https://grafana.observatory.nkllon.com")
        return True
    else:
        print("❌ OBSERVATORY RECOVERY FAILED")
        print("Manual intervention may be required")
        return False


if __name__ == "__main__":
    success = emergency_recovery()
    sys.exit(0 if success else 1)