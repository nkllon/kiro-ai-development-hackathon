#!/usr/bin/env python3
"""
🚨 HUNG SHELL DETECTOR & KILLER
==============================
Detects and handles hung shells without using shell commands
"""

import os
import signal
import psutil
import time
from typing import List, Optional

class HungShellDetector:
    """Detect and kill hung shells without shell commands"""
    
    def __init__(self):
        self.current_pid = os.getpid()
        self.parent_pid = os.getppid()
        
    def find_hung_shells(self) -> List[int]:
        """Find potentially hung shell processes"""
        hung_pids = []
        
        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
                try:
                    proc_info = proc.info
                    
                    # Look for shell processes that might be hung
                    if proc_info['name'] in ['bash', 'zsh', 'sh', 'fish']:
                        # Check if process is in uninterruptible sleep (D state)
                        if proc_info['status'] == psutil.STATUS_DISK_SLEEP:
                            hung_pids.append(proc_info['pid'])
                        # Check if process has been running too long with no activity
                        elif self._is_process_hung(proc):
                            hung_pids.append(proc_info['pid'])
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error scanning processes: {e}")
            
        return hung_pids
    
    def _is_process_hung(self, proc) -> bool:
        """Check if a process appears to be hung"""
        try:
            # Check CPU usage - hung processes often have 0% CPU
            cpu_percent = proc.cpu_percent()
            
            # Check memory usage - hung processes might have high memory
            memory_info = proc.memory_info()
            
            # Check if process is in uninterruptible sleep
            status = proc.status()
            
            # Simple heuristic: low CPU + uninterruptible sleep = likely hung
            return (cpu_percent < 0.1 and 
                   status == psutil.STATUS_DISK_SLEEP)
                   
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def kill_hung_shells(self, pids: List[int]) -> bool:
        """Kill hung shell processes"""
        killed_count = 0
        
        for pid in pids:
            try:
                # Try SIGTERM first (graceful)
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                
                # Check if still alive
                if psutil.pid_exists(pid):
                    # Force kill with SIGKILL
                    os.kill(pid, signal.SIGKILL)
                    killed_count += 1
                    print(f"🚨 KILLED HUNG SHELL PID: {pid}")
                else:
                    killed_count += 1
                    print(f"✅ TERMINATED SHELL PID: {pid}")
                    
            except (ProcessLookupError, PermissionError) as e:
                print(f"❌ Could not kill PID {pid}: {e}")
                
        return killed_count > 0
    
    def emergency_shell_reset(self):
        """Emergency shell reset procedure"""
        print("🚨 EMERGENCY SHELL RESET INITIATED")
        print("=" * 40)
        
        # Find hung shells
        hung_pids = self.find_hung_shells()
        
        if hung_pids:
            print(f"🔍 Found {len(hung_pids)} potentially hung shells: {hung_pids}")
            
            # Kill them
            success = self.kill_hung_shells(hung_pids)
            
            if success:
                print("✅ HUNG SHELLS TERMINATED")
                print("🔄 Shell should reset on next command")
            else:
                print("❌ FAILED TO KILL HUNG SHELLS")
        else:
            print("ℹ️  No hung shells detected")
            print("🔄 Attempting process cleanup...")
            
            # Try to kill current shell's parent if it's a shell
            try:
                parent_proc = psutil.Process(self.parent_pid)
                if parent_proc.name() in ['bash', 'zsh', 'sh', 'fish']:
                    print(f"🎯 Killing parent shell PID: {self.parent_pid}")
                    os.kill(self.parent_pid, signal.SIGTERM)
            except:
                pass

def main():
    """Run hung shell detector and killer"""
    detector = HungShellDetector()
    detector.emergency_shell_reset()

if __name__ == "__main__":
    main()
