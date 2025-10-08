#!/usr/bin/env python3
"""
Simplified Observatory Deployment Script
=======================================

Deploys Observatory with minimal dependencies to avoid startup loops.
Part of Observatory Vonnegut Deployment Recovery.
"""

import os
import sys
import subprocess
import json
import time
import signal
import requests
from datetime import datetime
from pathlib import Path

class SimplifiedObservatoryDeployment:
    def __init__(self):
        self.observatory_port = 8888
        self.process = None
        self.deployment_log = []
        
    def log_action(self, action, status, details=""):
        """Log deployment actions for audit purposes."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        }
        self.deployment_log.append(entry)
        
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "ℹ️"
        print(f"{status_icon} {action}: {details}")
    
    def check_port_availability(self, port):
        """Check if a port is available for use."""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def validate_prerequisites(self):
        """Validate system prerequisites for Observatory deployment."""
        print("🔍 Validating deployment prerequisites...")
        
        # Check if Observatory port is available
        if not self.check_port_availability(self.observatory_port):
            self.log_action("Port Check", "error", f"Port {self.observatory_port} is already in use")
            return False
        
        self.log_action("Port Check", "success", f"Port {self.observatory_port} is available")
        
        # Check if minimal start script exists
        minimal_script = Path("start_observatory_minimal.py")
        if not minimal_script.exists():
            self.log_action("Script Check", "error", "start_observatory_minimal.py not found")
            return False
        
        self.log_action("Script Check", "success", "start_observatory_minimal.py found")
        
        return True
    
    def start_minimal_observatory(self):
        """Start Observatory in minimal mode to avoid dependency loops."""
        print("🚀 Starting Observatory in minimal mode...")
        
        try:
            # Set environment variables for proper configuration
            env = os.environ.copy()
            env.update({
                'OBSERVATORY_HOST': '0.0.0.0',
                'OBSERVATORY_PORT': str(self.observatory_port),
                'LOG_LEVEL': 'INFO',
                'PYTHONUNBUFFERED': '1'
            })
            
            # Start the minimal Observatory process
            self.process = subprocess.Popen(
                [sys.executable, "start_observatory_minimal.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log_action("Process Start", "success", f"Minimal Observatory started with PID {self.process.pid}")
            
            # Give the process time to start
            time.sleep(5)
            
            # Check if process is still running
            if self.process.poll() is None:
                self.log_action("Process Health", "success", "Minimal Observatory process is running")
                return True
            else:
                # Process died, get the output
                stdout, stderr = self.process.communicate()
                self.log_action("Process Health", "error", f"Minimal Observatory process died: {stdout}")
                return False
                
        except Exception as e:
            self.log_action("Process Start", "error", f"Failed to start minimal Observatory: {e}")
            return False
    
    def wait_for_startup(self, timeout=30):
        """Wait for Observatory to fully start up."""
        print(f"⏳ Waiting for Observatory startup (timeout: {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    self.log_action("Startup Wait", "error", "Observatory process died during startup")
                    return False
                
                # Try to connect to health endpoint
                response = requests.get(f"http://localhost:{self.observatory_port}/health", timeout=5)
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_action("Startup Wait", "success", f"Observatory is healthy: {health_data}")
                    return True
                    
            except requests.exceptions.RequestException:
                # Observatory not ready yet, continue waiting
                pass
            
            time.sleep(2)
        
        self.log_action("Startup Wait", "error", f"Observatory failed to start within {timeout} seconds")
        return False
    
    def validate_endpoints(self):
        """Validate that Observatory endpoints are working."""
        print("🔍 Validating Observatory endpoints...")
        
        endpoints = [
            ("/health", "Health endpoint"),
            ("/api/observatory/status", "Status endpoint"),
            ("/", "Root endpoint")
        ]
        
        all_valid = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"http://localhost:{self.observatory_port}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    self.log_action("Endpoint Validation", "success", f"{description} is working")
                else:
                    self.log_action("Endpoint Validation", "error", f"{description} returned status {response.status_code}")
                    all_valid = False
                    
            except requests.exceptions.RequestException as e:
                self.log_action("Endpoint Validation", "error", f"{description} failed: {e}")
                all_valid = False
        
        return all_valid
    
    def create_upgrade_script(self):
        """Create script to upgrade from minimal to full Observatory later."""
        print("📋 Creating upgrade script for future full deployment...")
        
        upgrade_script_content = '''#!/usr/bin/env python3
"""
Observatory Upgrade Script
=========================

Upgrades from minimal Observatory to full Observatory when dependencies are resolved.
"""

import subprocess
import sys
import time
import requests

def stop_minimal_observatory():
    """Stop the minimal Observatory."""
    print("🛑 Stopping minimal Observatory...")
    subprocess.run(["pkill", "-f", "start_observatory_minimal"], capture_output=True)
    time.sleep(2)

def start_full_observatory():
    """Attempt to start full Observatory."""
    print("🚀 Starting full Observatory...")
    try:
        process = subprocess.Popen([sys.executable, "start_observatory.py"])
        time.sleep(10)
        
        # Test if it's working
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            print("✅ Full Observatory started successfully")
            return True
        else:
            print("❌ Full Observatory failed health check")
            return False
    except Exception as e:
        print(f"❌ Full Observatory failed to start: {e}")
        return False

def fallback_to_minimal():
    """Fallback to minimal Observatory."""
    print("🔄 Falling back to minimal Observatory...")
    subprocess.Popen([sys.executable, "start_observatory_minimal.py"])
    time.sleep(5)
    
    try:
        response = requests.get("http://localhost:8888/health", timeout=10)
        if response.status_code == 200:
            print("✅ Minimal Observatory restored")
            return True
    except:
        pass
    
    print("❌ Failed to restore minimal Observatory")
    return False

def main():
    """Main upgrade process."""
    print("🔄 Observatory Upgrade Process")
    print("=" * 40)
    
    # Stop minimal
    stop_minimal_observatory()
    
    # Try full
    if start_full_observatory():
        print("🎉 Upgrade successful!")
        return True
    
    # Fallback to minimal
    if fallback_to_minimal():
        print("⚠️  Upgrade failed, restored minimal mode")
        return False
    
    print("❌ Upgrade failed completely")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
        
        upgrade_script = Path("scripts/upgrade_observatory.py")
        try:
            with open(upgrade_script, 'w') as f:
                f.write(upgrade_script_content)
            
            os.chmod(upgrade_script, 0o755)
            self.log_action("Upgrade Script", "success", f"Created upgrade script: {upgrade_script}")
            return True
            
        except Exception as e:
            self.log_action("Upgrade Script", "error", f"Failed to create upgrade script: {e}")
            return False
    
    def save_deployment_report(self):
        """Save deployment report for audit purposes."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_type": "simplified_minimal",
            "observatory_port": self.observatory_port,
            "process_pid": self.process.pid if self.process else None,
            "deployment_log": self.deployment_log,
            "notes": "Deployed in minimal mode to avoid dependency loops"
        }
        
        report_file = Path("observatory_simplified_deployment_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_action("Report Generation", "success", f"Deployment report saved: {report_file}")
        return report_file
    
    def deploy(self):
        """Execute the complete simplified deployment."""
        print("🚀 Observatory Simplified Deployment")
        print("=" * 50)
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            return False
        
        # Step 2: Start minimal Observatory
        if not self.start_minimal_observatory():
            return False
        
        # Step 3: Wait for startup
        if not self.wait_for_startup():
            return False
        
        # Step 4: Validate endpoints
        if not self.validate_endpoints():
            return False
        
        # Step 5: Create upgrade script
        if not self.create_upgrade_script():
            print("⚠️  Upgrade script creation failed, but deployment continues")
        
        # Step 6: Save deployment report
        self.save_deployment_report()
        
        print(f"\n🎉 Observatory Simplified Deployment Successful!")
        print(f"🌐 Observatory is running at: http://localhost:{self.observatory_port}")
        print(f"🔧 Process PID: {self.process.pid}")
        print(f"⚠️  Running in MINIMAL MODE - limited functionality")
        print(f"🔄 Use 'python scripts/upgrade_observatory.py' to attempt full mode")
        
        return True
    
    def cleanup_on_failure(self):
        """Clean up resources if deployment fails."""
        if self.process and self.process.poll() is None:
            print("🧹 Cleaning up failed deployment...")
            self.process.terminate()
            time.sleep(5)
            if self.process.poll() is None:
                self.process.kill()
            self.log_action("Cleanup", "success", "Terminated Observatory process")

def main():
    """Main deployment execution."""
    deployment = SimplifiedObservatoryDeployment()
    
    def signal_handler(signum, frame):
        print("\n🛑 Deployment interrupted")
        deployment.cleanup_on_failure()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = deployment.deploy()
        
        if success:
            print("\n🎯 Simplified deployment completed successfully!")
            print("Observatory is now running in minimal mode")
            return True
        else:
            print("\n❌ Simplified deployment failed!")
            deployment.cleanup_on_failure()
            return False
            
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        deployment.cleanup_on_failure()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)