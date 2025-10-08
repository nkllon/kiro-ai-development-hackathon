#!/usr/bin/env python3
"""
Docker Volume Migration Rollback Script

This script provides a complete rollback mechanism for the Docker volume migration,
restoring the system to its pre-migration state if anything goes wrong.
"""

import os
import sys
import subprocess
import json
import glob
from datetime import datetime
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        return None
    
    return result


def find_backup_directories():
    """Find available backup directories."""
    backup_dirs = glob.glob("docker-migration-backup-*")
    backup_dirs.sort(reverse=True)  # Most recent first
    
    print(f"🔍 Found {len(backup_dirs)} backup directories:")
    for i, backup_dir in enumerate(backup_dirs):
        print(f"   {i+1}. {backup_dir}")
    
    return backup_dirs


def select_backup_directory(backup_dirs):
    """Let user select which backup to restore from."""
    if not backup_dirs:
        print("❌ No backup directories found!")
        return None
    
    if len(backup_dirs) == 1:
        print(f"📁 Using backup: {backup_dirs[0]}")
        return backup_dirs[0]
    
    while True:
        try:
            choice = input(f"\nSelect backup to restore from (1-{len(backup_dirs)}, or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(backup_dirs):
                selected = backup_dirs[index]
                print(f"📁 Selected backup: {selected}")
                return selected
            else:
                print(f"❌ Invalid choice. Please enter 1-{len(backup_dirs)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")


def verify_backup_contents(backup_dir):
    """Verify that the backup contains the expected files."""
    print(f"🔍 Verifying backup contents in {backup_dir}...")
    
    expected_files = [
        "host-grafana-data",
        "host-prometheus-data",
        "docker-grafana-data.tar.gz",
        "docker-prometheus-data.tar.gz"
    ]
    
    missing_files = []
    for expected_file in expected_files:
        file_path = os.path.join(backup_dir, expected_file)
        if not os.path.exists(file_path):
            missing_files.append(expected_file)
    
    if missing_files:
        print(f"⚠️  Warning: Missing backup files: {', '.join(missing_files)}")
        response = input("Continue with incomplete backup? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Show backup contents
    print("📋 Backup contents:")
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.isdir(item_path):
            file_count = len(list(Path(item_path).rglob("*")))
            print(f"   📁 {item}/ ({file_count} files)")
        else:
            size = os.path.getsize(item_path)
            print(f"   📄 {item} ({size} bytes)")
    
    return True


def stop_containers():
    """Stop observatory containers."""
    print("🛑 Stopping observatory containers...")
    
    # Stop using docker-compose
    result = run_command("docker-compose -f deployment/observatory/docker-compose.yml down", check=False)
    
    # Force stop any remaining containers
    result = run_command("docker ps --filter name=observatory --format '{{.Names}}'", check=False)
    if result and result.stdout.strip():
        containers = result.stdout.strip().split('\n')
        for container in containers:
            print(f"🛑 Force stopping {container}")
            run_command(f"docker stop {container}", check=False)
    
    print("✅ Containers stopped")


def restore_host_directories(backup_dir):
    """Restore host directories from backup."""
    print("📁 Restoring host directories...")
    
    # Remove current directories if they exist
    if os.path.exists("deployment/observatory/grafana-data"):
        print("🗑️  Removing current grafana-data directory")
        run_command("rm -rf deployment/observatory/grafana-data")
    
    if os.path.exists("deployment/observatory/prometheus-data"):
        print("🗑️  Removing current prometheus-data directory")
        run_command("rm -rf deployment/observatory/prometheus-data")
    
    # Restore from backup
    grafana_backup = os.path.join(backup_dir, "host-grafana-data")
    if os.path.exists(grafana_backup):
        print("📦 Restoring Grafana data...")
        run_command(f"cp -r {grafana_backup} deployment/observatory/grafana-data")
    
    prometheus_backup = os.path.join(backup_dir, "host-prometheus-data")
    if os.path.exists(prometheus_backup):
        print("📦 Restoring Prometheus data...")
        run_command(f"cp -r {prometheus_backup} deployment/observatory/prometheus-data")
    
    print("✅ Host directories restored")


def restore_docker_volumes(backup_dir):
    """Restore Docker volumes from backup."""
    print("🐳 Restoring Docker volumes...")
    
    # Restore Grafana volume
    grafana_backup = os.path.join(backup_dir, "docker-grafana-data.tar.gz")
    if os.path.exists(grafana_backup):
        print("📦 Restoring Grafana Docker volume...")
        
        # Remove existing volume
        run_command("docker volume rm observatory_grafana_data", check=False)
        
        # Create new volume
        run_command("docker volume create observatory_grafana_data")
        
        # Restore data
        run_command(f"docker run --rm -v observatory_grafana_data:/data -v $(pwd)/{backup_dir}:/backup alpine tar xzf /backup/docker-grafana-data.tar.gz -C /data")
    
    # Restore Prometheus volume
    prometheus_backup = os.path.join(backup_dir, "docker-prometheus-data.tar.gz")
    if os.path.exists(prometheus_backup):
        print("📦 Restoring Prometheus Docker volume...")
        
        # Remove existing volume
        run_command("docker volume rm observatory_prometheus_data", check=False)
        
        # Create new volume
        run_command("docker volume create observatory_prometheus_data")
        
        # Restore data
        run_command(f"docker run --rm -v observatory_prometheus_data:/data -v $(pwd)/{backup_dir}:/backup alpine tar xzf /backup/docker-prometheus-data.tar.gz -C /data")
    
    print("✅ Docker volumes restored")


def restore_configuration_files():
    """Restore original configuration files."""
    print("⚙️  Restoring configuration files...")
    
    # Restore docker-compose.yml from git
    result = run_command("git checkout deployment/observatory/docker-compose.yml", check=False)
    if result and result.returncode == 0:
        print("✅ docker-compose.yml restored from git")
    else:
        print("⚠️  Could not restore docker-compose.yml from git")
        print("   You may need to manually restore the original configuration")
    
    # Restore .gitignore from git (remove migration additions)
    result = run_command("git checkout .gitignore", check=False)
    if result and result.returncode == 0:
        print("✅ .gitignore restored from git")
    else:
        print("⚠️  Could not restore .gitignore from git")
        print("   You may need to manually remove the migration additions")


def restore_git_tracking():
    """Restore git tracking of the directories."""
    print("📝 Restoring git tracking...")
    
    # Add directories back to git tracking
    if os.path.exists("deployment/observatory/grafana-data"):
        run_command("git add deployment/observatory/grafana-data/", check=False)
    
    if os.path.exists("deployment/observatory/prometheus-data"):
        run_command("git add deployment/observatory/prometheus-data/", check=False)
    
    print("✅ Git tracking restored")


def verify_rollback():
    """Verify that the rollback was successful."""
    print("🔍 Verifying rollback...")
    
    checks = []
    
    # Check host directories exist
    grafana_exists = os.path.exists("deployment/observatory/grafana-data/grafana.db")
    prometheus_exists = os.path.exists("deployment/observatory/prometheus-data")
    checks.append(("Host directories restored", grafana_exists and prometheus_exists))
    
    # Check docker-compose.yml has original format
    if os.path.exists("deployment/observatory/docker-compose.yml"):
        with open("deployment/observatory/docker-compose.yml", 'r') as f:
            compose_content = f.read()
        
        original_format = "${GRAFANA_DATA_PATH:-./grafana-data}" in compose_content
        checks.append(("docker-compose.yml restored", original_format))
    
    # Check containers can start
    print("🧪 Testing container startup...")
    result = run_command("docker-compose -f deployment/observatory/docker-compose.yml up -d", check=False)
    container_start = result and result.returncode == 0
    checks.append(("Containers start successfully", container_start))
    
    if container_start:
        # Stop containers after test
        run_command("docker-compose -f deployment/observatory/docker-compose.yml down", check=False)
    
    # Print verification results
    print("\n📊 Rollback Verification:")
    print("-" * 40)
    
    all_good = True
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
        if not passed:
            all_good = False
    
    return all_good


def main():
    """Main rollback function."""
    print("🔄 Docker Volume Migration Rollback")
    print("=" * 40)
    
    # Find available backups
    backup_dirs = find_backup_directories()
    if not backup_dirs:
        print("❌ No backup directories found!")
        print("   Backup directories should be named: docker-migration-backup-YYYYMMDD_HHMMSS")
        sys.exit(1)
    
    # Select backup
    selected_backup = select_backup_directory(backup_dirs)
    if not selected_backup:
        print("👋 Rollback cancelled")
        sys.exit(0)
    
    # Verify backup
    if not verify_backup_contents(selected_backup):
        print("❌ Backup verification failed")
        sys.exit(1)
    
    # Confirm rollback
    print(f"\n⚠️  This will rollback the migration using backup: {selected_backup}")
    print("   This will:")
    print("   • Stop all observatory containers")
    print("   • Restore host directories from backup")
    print("   • Restore Docker volumes from backup")
    print("   • Restore original docker-compose.yml")
    print("   • Restore original .gitignore")
    print("   • Re-add directories to git tracking")
    
    response = input("\nProceed with rollback? (y/N): ")
    if response.lower() != 'y':
        print("👋 Rollback cancelled")
        sys.exit(0)
    
    try:
        # Execute rollback steps
        stop_containers()
        restore_host_directories(selected_backup)
        restore_docker_volumes(selected_backup)
        restore_configuration_files()
        restore_git_tracking()
        
        # Verify rollback
        if verify_rollback():
            print("\n🎉 Rollback completed successfully!")
            print("\n📋 Next steps:")
            print("1. Verify your data is intact")
            print("2. Start containers: docker-compose -f deployment/observatory/docker-compose.yml up -d")
            print("3. Check Grafana and Prometheus are working")
            print(f"4. Keep backup safe: {selected_backup}")
        else:
            print("\n⚠️  Rollback completed but verification failed")
            print("   Please manually check your system state")
    
    except Exception as e:
        print(f"\n❌ Rollback failed with error: {e}")
        print("   System may be in an inconsistent state")
        print("   Please check manually and restore from backup if needed")
        sys.exit(1)


if __name__ == "__main__":
    main()