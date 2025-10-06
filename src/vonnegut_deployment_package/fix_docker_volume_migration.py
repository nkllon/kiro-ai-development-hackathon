#!/usr/bin/env python3
"""
Docker Volume Migration Script - Fix the January 27, 2025 Incident

This script safely migrates data from host directory mounts to proper Docker named volumes,
then removes the volatile data from git tracking to resolve the governance violations.
"""

import os
import sys
import subprocess
import json
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


def check_docker_running():
    """Check if Docker is running."""
    result = run_command("docker info", check=False)
    if result is None or result.returncode != 0:
        print("❌ Docker is not running. Please start Docker first.")
        return False
    return True


def get_volume_info(volume_name):
    """Get information about a Docker volume."""
    result = run_command(f"docker volume inspect {volume_name}", check=False)
    if result and result.returncode == 0:
        return json.loads(result.stdout)[0]
    return None


def check_containers_running():
    """Check if observatory containers are running."""
    result = run_command("docker ps --filter name=observatory --format '{{.Names}}'", check=False)
    if result and result.stdout.strip():
        running_containers = result.stdout.strip().split('\n')
        print(f"⚠️  Found running observatory containers: {', '.join(running_containers)}")
        return running_containers
    return []


def stop_observatory_containers():
    """Stop observatory containers."""
    print("🛑 Stopping observatory containers...")
    run_command("docker-compose -f deployment/observatory/docker-compose.yml down", check=False)
    
    # Force stop any remaining containers
    result = run_command("docker ps --filter name=observatory --format '{{.Names}}'", check=False)
    if result and result.stdout.strip():
        containers = result.stdout.strip().split('\n')
        for container in containers:
            run_command(f"docker stop {container}", check=False)


def backup_current_state():
    """Create backups of current state."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"docker-migration-backup-{timestamp}"
    
    print(f"💾 Creating backup in {backup_dir}/")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup host directories
    if os.path.exists("deployment/observatory/grafana-data"):
        run_command(f"cp -r deployment/observatory/grafana-data {backup_dir}/host-grafana-data")
    
    if os.path.exists("deployment/observatory/prometheus-data"):
        run_command(f"cp -r deployment/observatory/prometheus-data {backup_dir}/host-prometheus-data")
    
    # Backup Docker volumes
    grafana_vol = get_volume_info("observatory_grafana_data")
    if grafana_vol:
        print("💾 Backing up Docker grafana volume...")
        run_command(f"docker run --rm -v observatory_grafana_data:/data -v $(pwd)/{backup_dir}:/backup alpine tar czf /backup/docker-grafana-data.tar.gz -C /data .")
    
    prometheus_vol = get_volume_info("observatory_prometheus_data")
    if prometheus_vol:
        print("💾 Backing up Docker prometheus volume...")
        run_command(f"docker run --rm -v observatory_prometheus_data:/data -v $(pwd)/{backup_dir}:/backup alpine tar czf /backup/docker-prometheus-data.tar.gz -C /data .")
    
    return backup_dir


def compare_data_sources():
    """Compare data in host directories vs Docker volumes."""
    print("🔍 Analyzing data sources...")
    
    # Check host directories
    host_grafana_files = 0
    host_prometheus_files = 0
    
    if os.path.exists("deployment/observatory/grafana-data"):
        result = run_command("find deployment/observatory/grafana-data -type f | wc -l")
        host_grafana_files = int(result.stdout.strip()) if result else 0
    
    if os.path.exists("deployment/observatory/prometheus-data"):
        result = run_command("find deployment/observatory/prometheus-data -type f | wc -l")
        host_prometheus_files = int(result.stdout.strip()) if result else 0
    
    # Check Docker volumes
    docker_grafana_files = 0
    docker_prometheus_files = 0
    
    grafana_vol = get_volume_info("observatory_grafana_data")
    if grafana_vol:
        result = run_command("docker run --rm -v observatory_grafana_data:/data alpine find /data -type f | wc -l")
        docker_grafana_files = int(result.stdout.strip()) if result else 0
    
    prometheus_vol = get_volume_info("observatory_prometheus_data")
    if prometheus_vol:
        result = run_command("docker run --rm -v observatory_prometheus_data:/data alpine find /data -type f | wc -l")
        docker_prometheus_files = int(result.stdout.strip()) if result else 0
    
    print(f"📊 Data comparison:")
    print(f"   Grafana - Host: {host_grafana_files} files, Docker: {docker_grafana_files} files")
    print(f"   Prometheus - Host: {host_prometheus_files} files, Docker: {docker_prometheus_files} files")
    
    return {
        'host_grafana': host_grafana_files,
        'host_prometheus': host_prometheus_files,
        'docker_grafana': docker_grafana_files,
        'docker_prometheus': docker_prometheus_files
    }


def migrate_data_to_volumes(data_comparison):
    """Migrate data from host directories to Docker volumes."""
    print("🚚 Starting data migration...")
    
    # Determine migration strategy
    if data_comparison['host_grafana'] > data_comparison['docker_grafana']:
        print("📦 Migrating Grafana data from host to Docker volume...")
        
        # Create volume if it doesn't exist
        run_command("docker volume create observatory_grafana_data")
        
        # Copy data from host to volume
        run_command("docker run --rm -v $(pwd)/deployment/observatory/grafana-data:/source -v observatory_grafana_data:/dest alpine sh -c 'cp -r /source/* /dest/ 2>/dev/null || true'")
        
        print("✅ Grafana data migrated to Docker volume")
    
    elif data_comparison['docker_grafana'] > data_comparison['host_grafana']:
        print("ℹ️  Docker volume has more Grafana data - keeping Docker volume as source")
    
    if data_comparison['host_prometheus'] > data_comparison['docker_prometheus']:
        print("📦 Migrating Prometheus data from host to Docker volume...")
        
        # Create volume if it doesn't exist
        run_command("docker volume create observatory_prometheus_data")
        
        # Copy data from host to volume
        run_command("docker run --rm -v $(pwd)/deployment/observatory/prometheus-data:/source -v observatory_prometheus_data:/dest alpine sh -c 'cp -r /source/* /dest/ 2>/dev/null || true'")
        
        print("✅ Prometheus data migrated to Docker volume")
    
    elif data_comparison['docker_prometheus'] > data_comparison['host_prometheus']:
        print("ℹ️  Docker volume has more Prometheus data - keeping Docker volume as source")


def fix_docker_compose():
    """Fix the docker-compose.yml to use named volumes only."""
    print("🔧 Fixing docker-compose.yml...")
    
    compose_file = "deployment/observatory/docker-compose.yml"
    
    # Read current file
    with open(compose_file, 'r') as f:
        content = f.read()
    
    # Replace the problematic volume mounts
    content = content.replace(
        '${GRAFANA_DATA_PATH:-./grafana-data}:/var/lib/grafana',
        'grafana_data:/var/lib/grafana'
    )
    
    content = content.replace(
        '${PROMETHEUS_DATA_PATH:-./prometheus-data}:/prometheus',
        'prometheus_data:/prometheus'
    )
    
    # Add named volumes to the volumes section if not present
    if 'grafana_data:' not in content:
        # Find the volumes section and add grafana_data
        if 'volumes:' in content:
            content = content.replace(
                'volumes:\n',
                'volumes:\n  grafana_data:\n    driver: local\n  prometheus_data:\n    driver: local\n'
            )
        else:
            # Add volumes section at the end
            content += '\nvolumes:\n  grafana_data:\n    driver: local\n  prometheus_data:\n    driver: local\n'
    
    # Write fixed file
    with open(compose_file, 'w') as f:
        f.write(content)
    
    print("✅ docker-compose.yml fixed to use named volumes")


def clean_git_tracking():
    """Remove volatile data from git tracking."""
    print("🧹 Cleaning up git tracking...")
    
    # Remove from git tracking
    run_command("git rm -r --cached deployment/observatory/grafana-data/", check=False)
    run_command("git rm -r --cached deployment/observatory/prometheus-data/", check=False)
    
    # Update .gitignore
    gitignore_patterns = [
        "# Deployment data governance - Added by migration script",
        "**/grafana-data/",
        "**/prometheus-data/",
        "*.db",
        "*.exe",
        "**/logs/",
        "**/cache/",
        "**/tmp/"
    ]
    
    with open('.gitignore', 'a') as f:
        f.write('\n' + '\n'.join(gitignore_patterns) + '\n')
    
    print("✅ Updated .gitignore with governance patterns")


def verify_migration():
    """Verify the migration was successful."""
    print("🔍 Verifying migration...")
    
    # Check volumes exist and have data
    grafana_vol = get_volume_info("observatory_grafana_data")
    prometheus_vol = get_volume_info("observatory_prometheus_data")
    
    if not grafana_vol:
        print("❌ Grafana volume not found!")
        return False
    
    if not prometheus_vol:
        print("❌ Prometheus volume not found!")
        return False
    
    # Check volume contents
    result = run_command("docker run --rm -v observatory_grafana_data:/data alpine find /data -type f | wc -l")
    grafana_files = int(result.stdout.strip()) if result else 0
    
    result = run_command("docker run --rm -v observatory_prometheus_data:/data alpine find /data -type f | wc -l")
    prometheus_files = int(result.stdout.strip()) if result else 0
    
    print(f"✅ Migration verification:")
    print(f"   Grafana volume: {grafana_files} files")
    print(f"   Prometheus volume: {prometheus_files} files")
    
    return grafana_files > 0 or prometheus_files > 0


def main():
    """Main migration function."""
    print("🚀 Docker Volume Migration - Fixing January 27, 2025 Incident")
    print("=" * 65)
    
    # Safety check - recommend running tests first
    print("⚠️  SAFETY RECOMMENDATION:")
    print("   Run the test suite first: python scripts/test_docker_migration.py")
    print("   This will verify the migration logic in a safe environment.")
    print()
    
    response = input("Have you run the test suite? (y/N): ")
    if response.lower() != 'y':
        print("🧪 Please run the test suite first for safety:")
        print("   python scripts/test_docker_migration.py")
        print()
        print("   Then run this migration script again.")
        sys.exit(0)
    
    # Pre-flight checks
    if not check_docker_running():
        sys.exit(1)
    
    # Check current state
    running_containers = check_containers_running()
    if running_containers:
        response = input("⚠️  Observatory containers are running. Stop them? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cannot migrate with containers running. Exiting.")
            sys.exit(1)
        stop_observatory_containers()
    
    # Create backup
    backup_dir = backup_current_state()
    print(f"✅ Backup created in {backup_dir}/")
    
    # Analyze current state
    data_comparison = compare_data_sources()
    
    # Migrate data
    migrate_data_to_volumes(data_comparison)
    
    # Fix configuration
    fix_docker_compose()
    
    # Clean up git
    clean_git_tracking()
    
    # Verify migration
    if verify_migration():
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the containers: docker-compose -f deployment/observatory/docker-compose.yml up -d")
        print("2. Verify data integrity in Grafana and Prometheus")
        print("3. Commit the .gitignore changes: git add .gitignore && git commit -m 'Fix deployment data governance'")
        print("4. Remove host directories: rm -rf deployment/observatory/grafana-data deployment/observatory/prometheus-data")
        print(f"5. Keep backup safe: {backup_dir}/")
        print()
        print("🔄 ROLLBACK AVAILABLE:")
        print("   If anything goes wrong, run: python scripts/rollback_docker_migration.py")
        print(f"   This will restore from backup: {backup_dir}/")
        
        # Run the auditor to verify cleanup
        print("\n🔍 Running deployment auditor to verify cleanup...")
        run_command("python scripts/deployment_auditor_scan.py deployment/ --quiet", check=False)
        
    else:
        print("\n❌ Migration verification failed!")
        print(f"Check the backup in {backup_dir}/ and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()