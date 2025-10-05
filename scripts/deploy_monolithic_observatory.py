#!/usr/bin/env python3
"""
Monolithic Observatory Deployment Script
=======================================

Deploys the Observatory using the proven monolithic approach that works on macOS.
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

class ObservatoryDeployment:
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
        
        # Check if start_observatory.py exists
        start_script = Path("start_observatory.py")
        if not start_script.exists():
            self.log_action("Script Check", "error", "start_observatory.py not found")
            return False
        
        self.log_action("Script Check", "success", "start_observatory.py found")
        
        # Check if Observatory source code exists
        observatory_src = Path("src/beast_mode/observatory")
        if not observatory_src.exists():
            self.log_action("Source Check", "error", "Observatory source code not found")
            return False
        
        self.log_action("Source Check", "success", "Observatory source code found")
        
        # Check Python environment
        try:
            import asyncio
            import fastapi
            self.log_action("Python Environment", "success", "Required Python modules available")
        except ImportError as e:
            self.log_action("Python Environment", "error", f"Missing required modules: {e}")
            return False
        
        return True
    
    def create_data_directories(self):
        """Create necessary data directories for Observatory."""
        print("📁 Creating Observatory data directories...")
        
        directories = [
            "observatory_data",
            "observatory_data/metrics",
            "observatory_data/dashboards", 
            "observatory_data/logs",
            "observatory_data/config"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log_action("Directory Creation", "success", f"Created {directory}")
            except Exception as e:
                self.log_action("Directory Creation", "error", f"Failed to create {directory}: {e}")
                return False
        
        return True
    
    def start_observatory_process(self):
        """Start the Observatory process using start_observatory.py."""
        print("🚀 Starting Observatory monolithic process...")
        
        try:
            # Set environment variables for proper configuration
            env = os.environ.copy()
            env.update({
                'OBSERVATORY_HOST': '0.0.0.0',
                'OBSERVATORY_PORT': str(self.observatory_port),
                'LOG_LEVEL': 'INFO',
                'PYTHONUNBUFFERED': '1'
            })
            
            # Start the Observatory process
            self.process = subprocess.Popen(
                [sys.executable, "start_observatory.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log_action("Process Start", "success", f"Observatory process started with PID {self.process.pid}")
            
            # Give the process time to start
            time.sleep(5)
            
            # Check if process is still running
            if self.process.poll() is None:
                self.log_action("Process Health", "success", "Observatory process is running")
                return True
            else:
                # Process died, get the output
                stdout, stderr = self.process.communicate()
                self.log_action("Process Health", "error", f"Observatory process died: {stdout}")
                return False
                
        except Exception as e:
            self.log_action("Process Start", "error", f"Failed to start Observatory: {e}")
            return False
    
    def wait_for_startup(self, timeout=60):
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
        """Validate that all Observatory endpoints are working."""
        print("🔍 Validating Observatory endpoints...")
        
        endpoints = [
            ("/health", "Health endpoint"),
            ("/ready", "Readiness endpoint"),
            ("/metrics", "Metrics endpoint"),
            ("/", "Dashboard endpoint")
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
    
    def check_full_mode(self):
        """Verify Observatory is running in full mode, not emergency/minimal."""
        print("🔍 Verifying Observatory is in full mode...")
        
        try:
            response = requests.get(f"http://localhost:{self.observatory_port}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                mode = health_data.get('mode', 'unknown')
                
                if mode == 'emergency' or mode == 'minimal':
                    self.log_action("Mode Check", "error", f"Observatory is in {mode} mode, not full mode")
                    return False
                else:
                    self.log_action("Mode Check", "success", f"Observatory is in {mode} mode")
                    return True
            else:
                self.log_action("Mode Check", "error", f"Health endpoint returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_action("Mode Check", "error", f"Failed to check mode: {e}")
            return False
    
    def setup_process_management(self):
        """Set up process management for the Observatory."""
        print("🔧 Setting up process management...")
        
        # Create a simple process management script
        process_script = Path("scripts/manage_observatory.py")
        
        script_content = f'''#!/usr/bin/env python3
"""
Observatory Process Management Script
"""

import os
import sys
import signal
import subprocess
import time
import requests

OBSERVATORY_PID_FILE = "observatory.pid"
OBSERVATORY_PORT = {self.observatory_port}

def start_observatory():
    """Start Observatory process."""
    if is_running():
        print("Observatory is already running")
        return True
    
    print("Starting Observatory...")
    process = subprocess.Popen([sys.executable, "start_observatory.py"])
    
    with open(OBSERVATORY_PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    print(f"Observatory started with PID {{process.pid}}")
    return True

def stop_observatory():
    """Stop Observatory process."""
    if not os.path.exists(OBSERVATORY_PID_FILE):
        print("Observatory PID file not found")
        return False
    
    with open(OBSERVATORY_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to Observatory process {{pid}}")
        
        # Wait for graceful shutdown
        time.sleep(5)
        
        # Check if still running
        try:
            os.kill(pid, 0)  # Check if process exists
            print("Process still running, sending SIGKILL")
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            print("Observatory stopped gracefully")
        
        os.remove(OBSERVATORY_PID_FILE)
        return True
        
    except ProcessLookupError:
        print("Observatory process not found")
        os.remove(OBSERVATORY_PID_FILE)
        return False

def is_running():
    """Check if Observatory is running."""
    if not os.path.exists(OBSERVATORY_PID_FILE):
        return False
    
    with open(OBSERVATORY_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, 0)  # Check if process exists
        
        # Also check if Observatory is responding
        try:
            response = requests.get(f"http://localhost:{{OBSERVATORY_PORT}}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    except ProcessLookupError:
        os.remove(OBSERVATORY_PID_FILE)
        return False

def status():
    """Show Observatory status."""
    if is_running():
        print("Observatory is running")
        try:
            response = requests.get(f"http://localhost:{{OBSERVATORY_PORT}}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"Status: {{health}}")
        except:
            print("Observatory process running but not responding")
    else:
        print("Observatory is not running")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage_observatory.py [start|stop|status|restart]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start_observatory()
    elif command == "stop":
        stop_observatory()
    elif command == "status":
        status()
    elif command == "restart":
        stop_observatory()
        time.sleep(2)
        start_observatory()
    else:
        print("Unknown command. Use: start, stop, status, or restart")
'''
        
        try:
            with open(process_script, 'w') as f:
                f.write(script_content)
            
            os.chmod(process_script, 0o755)
            self.log_action("Process Management", "success", f"Created process management script: {process_script}")
            return True
            
        except Exception as e:
            self.log_action("Process Management", "error", f"Failed to create process management script: {e}")
            return False
    
    def save_deployment_report(self):
        """Save deployment report for audit purposes."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_type": "monolithic",
            "observatory_port": self.observatory_port,
            "process_pid": self.process.pid if self.process else None,
            "deployment_log": self.deployment_log
        }
        
        report_file = Path("observatory_deployment_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_action("Report Generation", "success", f"Deployment report saved: {report_file}")
        return report_file
    
    def deploy(self):
        """Execute the complete monolithic deployment."""
        print("🚀 Observatory Monolithic Deployment")
        print("=" * 50)
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            return False
        
        # Step 2: Create data directories
        if not self.create_data_directories():
            return False
        
        # Step 3: Start Observatory process
        if not self.start_observatory_process():
            return False
        
        # Step 4: Wait for startup
        if not self.wait_for_startup():
            return False
        
        # Step 5: Validate endpoints
        if not self.validate_endpoints():
            return False
        
        # Step 6: Check full mode
        if not self.check_full_mode():
            print("⚠️  Observatory is not in full mode, but deployment continues")
        
        # Step 7: Set up process management
        if not self.setup_process_management():
            print("⚠️  Process management setup failed, but deployment continues")
        
        # Step 8: Save deployment report
        self.save_deployment_report()
        
        print(f"\n🎉 Observatory Monolithic Deployment Successful!")
        print(f"🌐 Observatory is running at: http://localhost:{self.observatory_port}")
        print(f"🔧 Process PID: {self.process.pid}")
        print(f"📋 Use 'python scripts/manage_observatory.py status' to check status")
        
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
    deployment = ObservatoryDeployment()
    
    def signal_handler(signum, frame):
        print("\n🛑 Deployment interrupted")
        deployment.cleanup_on_failure()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = deployment.deploy()
        
        if success:
            print("\n🎯 Deployment completed successfully!")
            print("Observatory is now running in monolithic mode")
            return True
        else:
            print("\n❌ Deployment failed!")
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