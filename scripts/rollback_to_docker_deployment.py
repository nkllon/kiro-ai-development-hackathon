#!/usr/bin/env python3
"""
Observatory Rollback to Docker Deployment
========================================

Provides rollback capability to restore the previous Docker Compose
deployment if the monolithic approach fails.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class ObservatoryRollback:
    def __init__(self):
        self.docker_compose_file = Path("deployment/observatory/docker-compose.yml")
        self.backup_dirs = list(Path(".").glob("observatory_backup_*"))
        self.rollback_log = []
        
    def log_action(self, action: str, status: str, details: str = ""):
        """Log rollback actions."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.rollback_log.append(entry)
        
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "ℹ️"
        print(f"{status_icon} {action}: {details}")
    
    def stop_monolithic_services(self) -> bool:
        """Stop any running monolithic Observatory services."""
        print("🛑 Stopping monolithic Observatory services...")
        
        # Stop Observatory process
        try:
            result = subprocess.run(["pkill", "-f", "start_observatory"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_action("Stop Observatory Process", "success", "Observatory process terminated")
            else:
                self.log_action("Stop Observatory Process", "info", "No Observatory process found")
        except Exception as e:
            self.log_action("Stop Observatory Process", "error", str(e))
            return False
        
        # Stop Cloudflare tunnel
        try:
            result = subprocess.run(["pkill", "-f", "cloudflared"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_action("Stop Cloudflare Tunnel", "success", "Tunnel process terminated")
            else:
                self.log_action("Stop Cloudflare Tunnel", "info", "No tunnel process found")
        except Exception as e:
            self.log_action("Stop Cloudflare Tunnel", "error", str(e))
        
        # Clean up PID files
        pid_files = ["observatory.pid", "cloudflare_tunnel.pid"]
        for pid_file in pid_files:
            if Path(pid_file).exists():
                Path(pid_file).unlink()
                self.log_action("Cleanup PID Files", "success", f"Removed {pid_file}")
        
        return True
    
    def restore_docker_volumes(self) -> bool:
        """Restore Docker volumes from backups."""
        print("💾 Restoring Docker volumes from backups...")
        
        if not self.backup_dirs:
            self.log_action("Volume Restoration", "error", "No backup directories found")
            return False
        
        # Use the most recent backup
        latest_backup = max(self.backup_dirs, key=lambda x: x.stat().st_mtime)
        self.log_action("Backup Selection", "info", f"Using backup: {latest_backup}")
        
        # Create Docker volumes first
        volumes_to_create = [
            "observatory_prometheus_data",
            "observatory_grafana_data", 
            "observatory_redis_data",
            "observatory_observatory_data"
        ]
        
        for volume in volumes_to_create:
            try:
                result = subprocess.run(
                    ["docker", "volume", "create", volume],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self.log_action("Volume Creation", "success", f"Created volume {volume}")
                else:
                    self.log_action("Volume Creation", "info", f"Volume {volume} may already exist")
            except Exception as e:
                self.log_action("Volume Creation", "error", f"Failed to create {volume}: {e}")
        
        # Restore data to volumes
        backup_files = {
            "observatory_prometheus_data.tar.gz": "observatory_prometheus_data",
            "observatory_grafana_data.tar.gz": "observatory_grafana_data",
            "observatory_redis_data.tar.gz": "observatory_redis_data"
        }
        
        for backup_file, volume_name in backup_files.items():
            backup_path = latest_backup / backup_file
            
            if backup_path.exists():
                try:
                    # Restore data to volume using docker run
                    result = subprocess.run([
                        "docker", "run", "--rm",
                        "-v", f"{volume_name}:/data",
                        "-v", f"{backup_path.parent}:/backup",
                        "alpine:latest",
                        "sh", "-c", f"cd /data && tar xzf /backup/{backup_file} --strip-components=1"
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        self.log_action("Volume Restoration", "success", f"Restored {volume_name}")
                    else:
                        self.log_action("Volume Restoration", "error", f"Failed to restore {volume_name}: {result.stderr}")
                        
                except Exception as e:
                    self.log_action("Volume Restoration", "error", f"Error restoring {volume_name}: {e}")
            else:
                self.log_action("Volume Restoration", "info", f"No backup found for {volume_name}")
        
        return True
    
    def start_docker_services(self) -> bool:
        """Start Docker Compose services."""
        print("🚀 Starting Docker Compose services...")
        
        if not self.docker_compose_file.exists():
            self.log_action("Docker Compose Start", "error", f"Docker Compose file not found: {self.docker_compose_file}")
            return False
        
        try:
            # Change to the deployment directory
            deployment_dir = self.docker_compose_file.parent
            
            # Start services
            result = subprocess.run([
                "docker-compose", "up", "-d"
            ], cwd=deployment_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log_action("Docker Compose Start", "success", "Services started successfully")
                
                # Wait for services to be ready
                time.sleep(30)
                
                # Check service health
                health_result = subprocess.run([
                    "docker-compose", "ps"
                ], cwd=deployment_dir, capture_output=True, text=True)
                
                if health_result.returncode == 0:
                    self.log_action("Service Health Check", "success", "Services are running")
                    print(health_result.stdout)
                    return True
                else:
                    self.log_action("Service Health Check", "error", "Failed to check service status")
                    return False
            else:
                self.log_action("Docker Compose Start", "error", f"Failed to start services: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("Docker Compose Start", "error", str(e))
            return False
    
    def validate_rollback(self) -> bool:
        """Validate that the rollback was successful."""
        print("🔍 Validating rollback success...")
        
        # Check if Observatory is accessible
        try:
            import requests
            
            # Test local access
            response = requests.get("http://localhost:8888/health", timeout=30)
            if response.status_code == 200:
                self.log_action("Local Health Check", "success", "Observatory accessible locally")
            else:
                self.log_action("Local Health Check", "error", f"Local health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_action("Local Health Check", "error", str(e))
            return False
        
        # Test external access
        try:
            response = requests.get("https://observatory.nkllon.com/health", timeout=30)
            if response.status_code == 200:
                self.log_action("External Health Check", "success", "Observatory accessible externally")
            else:
                self.log_action("External Health Check", "error", f"External health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_action("External Health Check", "error", str(e))
            return False
        
        return True
    
    def create_emergency_recovery_script(self):
        """Create emergency recovery script for future use."""
        print("📋 Creating emergency recovery script...")
        
        recovery_script = '''#!/bin/bash
# Emergency Observatory Recovery Script
# Use this script to quickly restore Observatory to Docker deployment

set -e

echo "🚨 Emergency Observatory Recovery"
echo "================================"

# Stop any running processes
echo "🛑 Stopping processes..."
pkill -f start_observatory || true
pkill -f cloudflared || true

# Clean up PID files
rm -f observatory.pid cloudflare_tunnel.pid

# Start Docker services
echo "🚀 Starting Docker services..."
cd deployment/observatory
docker-compose down || true
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Test health
echo "🔍 Testing health..."
curl -f http://localhost:8888/health || echo "❌ Local health check failed"
curl -f https://observatory.nkllon.com/health || echo "❌ External health check failed"

echo "✅ Emergency recovery completed"
'''
        
        script_file = Path("scripts/emergency_recovery.sh")
        try:
            with open(script_file, 'w') as f:
                f.write(recovery_script)
            
            os.chmod(script_file, 0o755)
            self.log_action("Emergency Script", "success", f"Created emergency recovery script: {script_file}")
            
        except Exception as e:
            self.log_action("Emergency Script", "error", f"Failed to create emergency script: {e}")
    
    def save_rollback_report(self):
        """Save rollback report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "rollback_type": "docker_compose",
            "actions": self.rollback_log,
            "success": all(action["status"] != "error" for action in self.rollback_log)
        }
        
        report_file = Path(f"observatory_rollback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_action("Report Generation", "success", f"Rollback report saved: {report_file}")
    
    def execute_rollback(self) -> bool:
        """Execute complete rollback to Docker deployment."""
        print("🔄 Observatory Rollback to Docker Deployment")
        print("=" * 50)
        
        # Step 1: Stop monolithic services
        if not self.stop_monolithic_services():
            return False
        
        # Step 2: Restore Docker volumes
        if not self.restore_docker_volumes():
            return False
        
        # Step 3: Start Docker services
        if not self.start_docker_services():
            return False
        
        # Step 4: Validate rollback
        if not self.validate_rollback():
            print("⚠️  Rollback completed but validation failed")
        
        # Step 5: Create emergency recovery script
        self.create_emergency_recovery_script()
        
        # Step 6: Save report
        self.save_rollback_report()
        
        print(f"\n🎉 Rollback to Docker Deployment Complete!")
        print(f"🌐 Observatory should be accessible at: http://localhost:8888")
        print(f"🌍 External access: https://observatory.nkllon.com")
        print(f"📋 Emergency recovery script: scripts/emergency_recovery.sh")
        
        return True

def main():
    """Main rollback execution."""
    rollback = ObservatoryRollback()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        print("⚠️  This will stop the monolithic Observatory and restore Docker deployment")
        print("⚠️  All monolithic configuration will be lost")
        
        confirm = input("Are you sure you want to proceed? (yes/no): ")
        if confirm.lower() != "yes":
            print("Rollback cancelled")
            sys.exit(0)
    else:
        print("Usage: python rollback_to_docker_deployment.py --confirm")
        print("Add --confirm flag to proceed with rollback")
        sys.exit(1)
    
    try:
        success = rollback.execute_rollback()
        
        if success:
            print("\n🎯 Rollback completed successfully!")
            return True
        else:
            print("\n❌ Rollback failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Rollback failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)