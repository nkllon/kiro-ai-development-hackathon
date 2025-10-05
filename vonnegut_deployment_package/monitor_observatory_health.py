#!/usr/bin/env python3
"""
Observatory Health Monitoring and Process Management
==================================================

Monitors Observatory process health, provides restart capabilities,
and implements structured logging and resource monitoring.
"""

import os
import sys
import time
import json
import signal
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

class ObservatoryMonitor:
    def __init__(self):
        self.pid_file = Path("observatory.pid")
        self.log_file = Path("observatory_monitor.log")
        self.status_file = Path("observatory_status.json")
        
    def log_message(self, level: str, message: str):
        """Log structured messages."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level.upper()}: {message}"
        
        print(log_entry)
        
        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def get_process_info(self, pid: int) -> dict:
        """Get detailed process information."""
        try:
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict(),
                "create_time": process.create_time(),
                "cmdline": process.cmdline(),
                "connections": len(process.connections()),
                "num_threads": process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def is_observatory_running(self) -> tuple[bool, int]:
        """Check if Observatory process is running."""
        if not self.pid_file.exists():
            return False, 0
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and is actually Observatory
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                cmdline = ' '.join(process.cmdline())
                if 'start_observatory' in cmdline:
                    return True, pid
            
            # PID file exists but process is dead
            self.pid_file.unlink()
            return False, 0
            
        except (ValueError, FileNotFoundError, psutil.NoSuchProcess):
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False, 0
    
    def start_observatory(self) -> bool:
        """Start Observatory process."""
        self.log_message("info", "Starting Observatory process...")
        
        if self.is_observatory_running()[0]:
            self.log_message("warning", "Observatory is already running")
            return True
        
        try:
            # Start Observatory in background
            process = subprocess.Popen(
                [sys.executable, "start_observatory.py"],
                stdout=open("observatory.log", "w"),
                stderr=subprocess.STDOUT,
                env=dict(os.environ, PYTHONUNBUFFERED="1")
            )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            self.log_message("info", f"Observatory started with PID {process.pid}")
            
            # Wait a moment to see if it starts successfully
            time.sleep(3)
            
            if self.is_observatory_running()[0]:
                self.log_message("info", "Observatory startup confirmed")
                return True
            else:
                self.log_message("error", "Observatory failed to start properly")
                return False
                
        except Exception as e:
            self.log_message("error", f"Failed to start Observatory: {e}")
            return False
    
    def stop_observatory(self) -> bool:
        """Stop Observatory process gracefully."""
        self.log_message("info", "Stopping Observatory process...")
        
        running, pid = self.is_observatory_running()
        if not running:
            self.log_message("warning", "Observatory is not running")
            return True
        
        try:
            # Try graceful shutdown first
            os.kill(pid, signal.SIGTERM)
            self.log_message("info", f"Sent SIGTERM to Observatory process {pid}")
            
            # Wait for graceful shutdown
            for i in range(10):
                if not psutil.pid_exists(pid):
                    self.log_message("info", "Observatory stopped gracefully")
                    if self.pid_file.exists():
                        self.pid_file.unlink()
                    return True
                time.sleep(1)
            
            # Force kill if still running
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGKILL)
                self.log_message("warning", f"Force killed Observatory process {pid}")
                time.sleep(2)
            
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except (ProcessLookupError, psutil.NoSuchProcess):
            self.log_message("info", "Observatory process already stopped")
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
        except Exception as e:
            self.log_message("error", f"Failed to stop Observatory: {e}")
            return False
    
    def restart_observatory(self) -> bool:
        """Restart Observatory process."""
        self.log_message("info", "Restarting Observatory...")
        
        if not self.stop_observatory():
            return False
        
        time.sleep(2)
        return self.start_observatory()
    
    def get_status(self) -> dict:
        """Get comprehensive Observatory status."""
        running, pid = self.is_observatory_running()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "running": running,
            "pid": pid if running else None,
            "process_info": None,
            "health_check": None,
            "resource_usage": None
        }
        
        if running:
            # Get process information
            process_info = self.get_process_info(pid)
            if process_info:
                status["process_info"] = process_info
                
                # Calculate uptime
                uptime_seconds = time.time() - process_info["create_time"]
                status["uptime_seconds"] = uptime_seconds
                status["uptime_human"] = self.format_uptime(uptime_seconds)
            
            # Try health check
            try:
                import requests
                response = requests.get("http://localhost:8888/health", timeout=5)
                status["health_check"] = {
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else None,
                    "accessible": response.status_code == 200
                }
            except Exception as e:
                status["health_check"] = {
                    "status_code": None,
                    "response": None,
                    "accessible": False,
                    "error": str(e)
                }
        
        return status
    
    def format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def save_status(self, status: dict):
        """Save status to file."""
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def monitor_loop(self, interval: int = 30):
        """Continuous monitoring loop."""
        self.log_message("info", f"Starting Observatory monitoring (interval: {interval}s)")
        
        try:
            while True:
                status = self.get_status()
                self.save_status(status)
                
                if status["running"]:
                    if status["health_check"] and status["health_check"]["accessible"]:
                        self.log_message("info", f"Observatory healthy (PID: {status['pid']}, Uptime: {status.get('uptime_human', 'unknown')})")
                    else:
                        self.log_message("warning", f"Observatory running but not responding to health checks (PID: {status['pid']})")
                else:
                    self.log_message("error", "Observatory is not running")
                    
                    # Auto-restart if configured
                    if os.getenv("OBSERVATORY_AUTO_RESTART", "false").lower() == "true":
                        self.log_message("info", "Auto-restart enabled, attempting to start Observatory")
                        self.start_observatory()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log_message("info", "Monitoring stopped by user")
        except Exception as e:
            self.log_message("error", f"Monitoring loop error: {e}")

def main():
    """Main monitoring execution."""
    monitor = ObservatoryMonitor()
    
    if len(sys.argv) < 2:
        print("Usage: python monitor_observatory_health.py [start|stop|restart|status|monitor]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        success = monitor.start_observatory()
        sys.exit(0 if success else 1)
        
    elif command == "stop":
        success = monitor.stop_observatory()
        sys.exit(0 if success else 1)
        
    elif command == "restart":
        success = monitor.restart_observatory()
        sys.exit(0 if success else 1)
        
    elif command == "status":
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
        
        if status["running"]:
            print(f"\n✅ Observatory is running (PID: {status['pid']})")
            if status.get("uptime_human"):
                print(f"⏱️  Uptime: {status['uptime_human']}")
            if status["health_check"] and status["health_check"]["accessible"]:
                print("🏥 Health check: PASS")
            else:
                print("🏥 Health check: FAIL")
        else:
            print("\n❌ Observatory is not running")
        
        sys.exit(0 if status["running"] else 1)
        
    elif command == "monitor":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor.monitor_loop(interval)
        
    else:
        print("Unknown command. Use: start, stop, restart, status, or monitor")
        sys.exit(1)

if __name__ == "__main__":
    main()