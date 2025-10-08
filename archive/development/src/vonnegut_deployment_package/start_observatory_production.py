#!/usr/bin/env python3
"""
Observatory Production Starter
Manages Observatory and Cloudflare tunnel as background services.
"""

import os
import sys
import subprocess
import signal
import time
import json
from pathlib import Path
import psutil

class ObservatoryManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.pid_file = self.project_root / "observatory.pid"
        self.log_dir = self.project_root / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
    def is_running(self):
        """Check if Observatory is already running."""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            # Check if processes are still running
            for service, pid in pids.items():
                if not psutil.pid_exists(pid):
                    return False
            
            return True
        except:
            return False
    
    def stop_services(self):
        """Stop running Observatory services."""
        if not self.pid_file.exists():
            print("No running services found.")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            print("🛑 Stopping Observatory services...")
            
            for service, pid in pids.items():
                try:
                    if psutil.pid_exists(pid):
                        os.kill(pid, signal.SIGTERM)
                        print(f"✅ Stopped {service} (PID: {pid})")
                    else:
                        print(f"⚠️  {service} (PID: {pid}) was not running")
                except ProcessLookupError:
                    print(f"⚠️  {service} (PID: {pid}) was already stopped")
            
            # Wait for processes to stop
            time.sleep(2)
            
            # Force kill if still running
            for service, pid in pids.items():
                try:
                    if psutil.pid_exists(pid):
                        os.kill(pid, signal.SIGKILL)
                        print(f"🔥 Force killed {service} (PID: {pid})")
                except ProcessLookupError:
                    pass
            
            self.pid_file.unlink()
            print("✅ All services stopped")
            
        except Exception as e:
            print(f"❌ Error stopping services: {e}")
    
    def start_services(self):
        """Start Observatory and Cloudflare tunnel as background services."""
        if self.is_running():
            print("Observatory is already running. Use --stop to stop it first.")
            return
        
        print("🚀 Starting Observatory services...")
        
        # Start Observatory
        observatory_log = self.log_dir / "observatory.log"
        observatory_cmd = [
            sys.executable, "-m", "src.beast_mode.observatory.main"
        ]
        
        print("📡 Starting Observatory server...")
        observatory_proc = subprocess.Popen(
            observatory_cmd,
            cwd=self.project_root,
            stdout=open(observatory_log, 'w'),
            stderr=subprocess.STDOUT,
            env={**os.environ, 'PYTHONPATH': str(self.project_root)}
        )
        
        # Wait a moment for Observatory to start
        time.sleep(3)
        
        # Start Cloudflare tunnel
        tunnel_log = self.log_dir / "cloudflared.log"
        tunnel_cmd = [
            "/opt/homebrew/bin/cloudflared", "tunnel", "run", "observatory-tunnel"
        ]
        
        print("🌐 Starting Cloudflare tunnel...")
        tunnel_proc = subprocess.Popen(
            tunnel_cmd,
            stdout=open(tunnel_log, 'w'),
            stderr=subprocess.STDOUT
        )
        
        # Save PIDs
        pids = {
            "observatory": observatory_proc.pid,
            "cloudflared": tunnel_proc.pid
        }
        
        with open(self.pid_file, 'w') as f:
            json.dump(pids, f, indent=2)
        
        print("✅ Services started successfully!")
        print(f"   Observatory PID: {observatory_proc.pid}")
        print(f"   Cloudflared PID: {tunnel_proc.pid}")
        print(f"   Logs: {self.log_dir}/")
        print(f"   Local: http://localhost:8888/")
        print(f"   Public: https://observatory.nkllon.com/")
        
        return pids
    
    def status(self):
        """Show status of Observatory services."""
        if not self.is_running():
            print("Observatory services are not running.")
            return
        
        try:
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
            
            print("📊 Observatory Service Status:")
            print("-" * 40)
            
            for service, pid in pids.items():
                if psutil.pid_exists(pid):
                    proc = psutil.Process(pid)
                    cpu_percent = proc.cpu_percent()
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    print(f"✅ {service.title()}: Running (PID: {pid})")
                    print(f"   CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.1f}MB")
                else:
                    print(f"❌ {service.title()}: Not running (PID: {pid})")
            
            print(f"\n📁 Logs: {self.log_dir}/")
            print(f"🌐 Public URL: https://observatory.nkllon.com/")
            
        except Exception as e:
            print(f"❌ Error checking status: {e}")
    
    def logs(self, service=None, follow=False):
        """Show logs for Observatory services."""
        if service:
            log_file = self.log_dir / f"{service}.log"
            if not log_file.exists():
                print(f"Log file not found: {log_file}")
                return
            
            if follow:
                subprocess.run(["tail", "-f", str(log_file)])
            else:
                subprocess.run(["tail", "-50", str(log_file)])
        else:
            print("Available logs:")
            for log_file in self.log_dir.glob("*.log"):
                print(f"  {log_file.name}")
            print("\nUse --logs <service> to view specific logs")
            print("Use --logs <service> --follow to follow logs")

def main():
    manager = ObservatoryManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--stop":
            manager.stop_services()
        elif command == "--status":
            manager.status()
        elif command == "--logs":
            service = sys.argv[2] if len(sys.argv) > 2 else None
            follow = "--follow" in sys.argv
            manager.logs(service, follow)
        elif command == "--restart":
            manager.stop_services()
            time.sleep(2)
            manager.start_services()
        else:
            print("Usage: python start_observatory_production.py [--stop|--status|--logs|--restart]")
    else:
        manager.start_services()

if __name__ == "__main__":
    main()