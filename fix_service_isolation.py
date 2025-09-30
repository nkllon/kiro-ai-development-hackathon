#!/usr/bin/env python3
"""
Service Isolation Fix
Resolves port conflicts and properly isolates Beast Mode services
"""

import subprocess
import time
import requests
from pathlib import Path

class ServiceIsolationFix:
    """Fix service port conflicts and implement proper isolation"""
    
    def __init__(self):
        self.services = {
            'prometheus_metrics': 9091,
            'empirical_data': 9092, 
            'beast_mode_dashboard': 9093,
            'nginx_proxy': 8080
        }
        
    def check_port_conflicts(self):
        """Check what's running on our target ports"""
        print("🔍 Checking port conflicts...")
        
        conflicts = {}
        for service, port in self.services.items():
            try:
                result = subprocess.run(['lsof', '-i', f':{port}'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    conflicts[port] = result.stdout.strip().split('\n')[1:]
                    print(f"⚠️  Port {port} ({service}) is in use:")
                    for line in conflicts[port]:
                        print(f"   {line}")
                else:
                    print(f"✅ Port {port} ({service}) is available")
            except Exception as e:
                print(f"❌ Error checking port {port}: {e}")
        
        return conflicts
    
    def kill_conflicting_processes(self, conflicts):
        """Kill processes that are conflicting with our services"""
        print("\n🛑 Stopping conflicting processes...")
        
        for port, processes in conflicts.items():
            for process_line in processes:
                try:
                    # Extract PID from lsof output
                    parts = process_line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        if pid.isdigit():
                            print(f"🔪 Killing process {pid} on port {port}")
                            subprocess.run(['kill', '-9', pid])
                            time.sleep(1)
                except Exception as e:
                    print(f"❌ Error killing process: {e}")
    
    def start_isolated_metrics_server(self):
        """Start metrics server on isolated port"""
        print(f"\n🚀 Starting isolated metrics server on port {self.services['prometheus_metrics']}")
        
        # Create isolated metrics server script
        metrics_script = f"""#!/usr/bin/env python3
import time
from prometheus_client import start_http_server, Gauge, Counter, CollectorRegistry
import json
from pathlib import Path
from datetime import datetime

# Create custom registry
registry = CollectorRegistry()

# Create metrics
cpu_usage = Gauge('beast_mode_cpu_usage_percent', 'CPU usage', registry=registry)
memory_usage = Gauge('beast_mode_memory_usage_percent', 'Memory usage', registry=registry)
kiro_processes = Gauge('beast_mode_kiro_processes', 'Kiro processes', registry=registry)
data_collection_active = Gauge('beast_mode_data_collection_active', 'Data collection status', registry=registry)

def update_metrics():
    try:
        # Read latest empirical data
        data_dir = Path("empirical_data")
        session_dirs = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('session_')]
        
        if session_dirs:
            latest_session = max(session_dirs, key=lambda x: x.name)
            system_file = latest_session / "system_metrics.jsonl"
            
            if system_file.exists():
                with open(system_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        latest = json.loads(lines[-1])
                        cpu_usage.set(latest['system']['cpu_percent'])
                        memory_usage.set(latest['system']['memory_percent'])
                        kiro_processes.set(latest['processes']['kiro_processes'])
                        data_collection_active.set(1)
                        print(f"📊 Updated metrics: CPU={{latest['system']['cpu_percent']:.1f}}%, Memory={{latest['system']['memory_percent']:.1f}}%")
    except Exception as e:
        print(f"❌ Error updating metrics: {{e}}")
        data_collection_active.set(0)

# Start server
start_http_server({self.services['prometheus_metrics']}, registry=registry)
print(f"✅ Metrics server started on port {self.services['prometheus_metrics']}")

# Update loop
while True:
    update_metrics()
    time.sleep(30)
"""
        
        with open('isolated_metrics_server.py', 'w') as f:
            f.write(metrics_script)
        
        # Start the server
        subprocess.Popen(['python', 'isolated_metrics_server.py'])
        time.sleep(3)
        
        # Verify it's working
        try:
            response = requests.get(f"http://localhost:{self.services['prometheus_metrics']}/metrics", timeout=5)
            if response.status_code == 200:
                print("✅ Isolated metrics server is responding")
                return True
            else:
                print(f"❌ Metrics server returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach metrics server: {e}")
            return False
    
    def setup_nginx_proxy(self):
        """Setup nginx proxy for service isolation"""
        print(f"\n🌐 Setting up nginx proxy on port {self.services['nginx_proxy']}")
        
        # Check if nginx is available
        try:
            result = subprocess.run(['which', 'nginx'], capture_output=True, text=True)
            if not result.stdout.strip():
                print("❌ nginx not found. Installing via homebrew...")
                subprocess.run(['brew', 'install', 'nginx'])
        except Exception as e:
            print(f"⚠️  Could not check/install nginx: {e}")
            return False
        
        # Test nginx config
        try:
            result = subprocess.run(['nginx', '-t', '-c', str(Path.cwd() / 'nginx_service_isolation.conf')], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Nginx configuration is valid")
            else:
                print(f"❌ Nginx configuration error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error testing nginx config: {e}")
            return False
        
        # Start nginx with our config
        try:
            subprocess.run(['nginx', '-c', str(Path.cwd() / 'nginx_service_isolation.conf')])
            print(f"✅ Nginx proxy started on port {self.services['nginx_proxy']}")
            return True
        except Exception as e:
            print(f"❌ Error starting nginx: {e}")
            return False
    
    def verify_isolation(self):
        """Verify that service isolation is working"""
        print("\n🔍 Verifying service isolation...")
        
        endpoints = {
            f"http://localhost:{self.services['nginx_proxy']}/metrics": "Metrics via nginx",
            f"http://localhost:{self.services['nginx_proxy']}/health": "Health check",
            f"http://localhost:{self.services['prometheus_metrics']}/metrics": "Direct metrics",
            "http://localhost:9090/api/v1/status/config": "Prometheus server"
        }
        
        results = {}
        for url, description in endpoints.items():
            try:
                response = requests.get(url, timeout=5)
                results[description] = f"✅ {response.status_code}"
                print(f"✅ {description}: {response.status_code}")
            except Exception as e:
                results[description] = f"❌ {str(e)}"
                print(f"❌ {description}: {e}")
        
        return results
    
    def run_isolation_fix(self):
        """Run complete service isolation fix"""
        print("🔧 Service Isolation Fix")
        print("=" * 40)
        
        # Check conflicts
        conflicts = self.check_port_conflicts()
        
        # Kill conflicting processes if needed
        if conflicts:
            self.kill_conflicting_processes(conflicts)
            time.sleep(2)
        
        # Start isolated services
        if self.start_isolated_metrics_server():
            print("✅ Metrics server isolation complete")
        else:
            print("❌ Failed to isolate metrics server")
            return False
        
        # Setup nginx proxy
        if self.setup_nginx_proxy():
            print("✅ Nginx proxy isolation complete")
        else:
            print("⚠️  Nginx proxy setup failed, but direct access should work")
        
        # Verify everything
        results = self.verify_isolation()
        
        print("\n🎯 Service Isolation Summary:")
        print(f"📊 Metrics: http://localhost:{self.services['prometheus_metrics']}/metrics")
        print(f"🌐 Proxy: http://localhost:{self.services['nginx_proxy']}/metrics")
        print(f"🔍 Prometheus: http://localhost:9090")
        
        return True

def main():
    """Main execution"""
    fixer = ServiceIsolationFix()
    
    try:
        if fixer.run_isolation_fix():
            print("\n✅ Service isolation completed successfully")
        else:
            print("\n❌ Service isolation failed")
    except KeyboardInterrupt:
        print("\n🛑 Service isolation interrupted")
    except Exception as e:
        print(f"\n❌ Error in service isolation: {e}")

if __name__ == "__main__":
    main()