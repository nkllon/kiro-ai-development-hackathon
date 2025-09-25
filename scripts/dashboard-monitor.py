#!/usr/bin/env python3
"""
Smart Dashboard Monitor - Prevents WebSocket disconnections with intelligent monitoring
"""

import time
import subprocess
import sys
import signal
import os
from pathlib import Path

class SmartMonitor:
    def __init__(self):
        self.consecutive_failures = 0
        self.max_failures = 3
        self.check_interval = 30  # Check every 30 seconds
        self.backoff_multiplier = 2
        self.max_backoff = 300  # Max 5 minutes between checks
        self.running = True
        
    def check_dashboard(self):
        """Check if dashboard is responding"""
        try:
            result = subprocess.run([
                'curl', '-s', 'http://localhost:8888/health'
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'healthy' in result.stdout
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def restart_dashboard(self):
        """Restart dashboard with proper error handling"""
        print(f"🔄 Attempting dashboard restart (failure #{self.consecutive_failures})...")
        
        try:
            # Stop any existing processes
            subprocess.run(['pkill', '-f', 'observatory.*server'], 
                         capture_output=True, timeout=10)
            time.sleep(2)
            
            # Restart using make
            result = subprocess.run(['make', 'dashboard-restart'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Dashboard restarted successfully")
                return True
            else:
                print(f"❌ Restart failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Restart error: {e}")
            return False
    
    def calculate_backoff(self):
        """Calculate exponential backoff interval"""
        backoff = self.check_interval * (self.backoff_multiplier ** self.consecutive_failures)
        return min(backoff, self.max_backoff)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Monitoring stopped by user")
        self.running = False
    
    def run(self):
        """Main monitoring loop"""
        print("🛡️ Starting intelligent dashboard monitor...")
        print(f"• Checking every {self.check_interval} seconds")
        print(f"• Restarting after {self.max_failures} consecutive failures")
        print("• Using exponential backoff to prevent restart loops")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        while self.running:
            if self.check_dashboard():
                if self.consecutive_failures > 0:
                    print(f"✅ Dashboard recovered! Resetting failure count to {self.consecutive_failures}")
                self.consecutive_failures = 0
                print("✅ Dashboard healthy")
            else:
                self.consecutive_failures += 1
                print(f"❌ Dashboard failure #{self.consecutive_failures}/{self.max_failures}")
                
                if self.consecutive_failures >= self.max_failures:
                    if self.restart_dashboard():
                        self.consecutive_failures = 0
                        print("🔄 Monitoring reset - dashboard restarted")
                    else:
                        print("🚨 Restart failed - manual intervention needed")
                        # Increase backoff for repeated failures
                        backoff = self.calculate_backoff()
                        print(f"⏳ Increasing check interval to {backoff}s")
                        self.consecutive_failures = 0  # Reset to prevent immediate retry
            
            if self.running:
                interval = self.check_interval if self.consecutive_failures == 0 else self.calculate_backoff()
                print(f"⏰ Next check in {interval} seconds...")
                time.sleep(interval)
        
        print("👋 Monitoring stopped")

def main():
    monitor = SmartMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
EOF && echo "" && echo "=== STARTING SMART MONITOR ===" && chmod +x scripts/dashboard-monitor.py && python3 scripts/dashboard-monitor.py