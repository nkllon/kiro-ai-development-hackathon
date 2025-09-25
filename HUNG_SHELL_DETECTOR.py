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
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
import json

class HungShellDetector:
    """Detect and kill hung shells without shell commands"""

    def __init__(self,
                 hang_timeout_seconds: int = 300,
                 cpu_threshold: float = 0.5,
                 memory_threshold_mb: int = 500,
                 interactive_mode: bool = True,
                 log_level: str = "INFO"):
        self.current_pid = os.getpid()
        self.parent_pid = os.getppid()
        self.hang_timeout = timedelta(seconds=hang_timeout_seconds)
        self.cpu_threshold = cpu_threshold
        self.memory_threshold_mb = memory_threshold_mb
        self.interactive_mode = interactive_mode
        self.process_history: Dict[int, Dict] = {}

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Configurable shell types to monitor
        self.monitored_shells = ['bash', 'zsh', 'sh', 'fish', 'tcsh', 'csh']
        
    def find_hung_shells(self) -> List[Tuple[int, Dict]]:
        """Find potentially hung shell processes with detailed info"""
        hung_processes = []
        current_time = datetime.now()

        try:
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
                try:
                    proc_info = proc.info
                    pid = proc_info['pid']

                    # Look for shell processes that might be hung
                    if proc_info['name'] in self.monitored_shells:
                        # Skip our own process and parent
                        if pid in [self.current_pid, self.parent_pid]:
                            continue

                        hung_info = self._analyze_process_hang_status(proc, current_time)
                        if hung_info['is_hung']:
                            hung_processes.append((pid, hung_info))
                            self.logger.warning(f"Detected hung shell PID {pid}: {hung_info['reason']}")

                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Could not access process: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error scanning processes: {e}")

        return hung_processes
    
    def _analyze_process_hang_status(self, proc, current_time: datetime) -> Dict:
        """Comprehensive analysis of process hang status"""
        try:
            pid = proc.pid
            cpu_percent = proc.cpu_percent(interval=0.1)  # Small sampling interval
            memory_info = proc.memory_info()
            status = proc.status()
            create_time = datetime.fromtimestamp(proc.create_time())

            # Track process history
            if pid not in self.process_history:
                self.process_history[pid] = {
                    'first_seen': current_time,
                    'last_cpu_activity': current_time,
                    'cpu_samples': [],
                    'status_changes': []
                }

            history = self.process_history[pid]
            history['cpu_samples'].append(cpu_percent)
            history['status_changes'].append(status)

            # Keep only recent samples
            if len(history['cpu_samples']) > 10:
                history['cpu_samples'] = history['cpu_samples'][-10:]
            if len(history['status_changes']) > 5:
                history['status_changes'] = history['status_changes'][-5:]

            # Update last activity time
            if cpu_percent > self.cpu_threshold:
                history['last_cpu_activity'] = current_time

            # Calculate averages
            avg_cpu = sum(history['cpu_samples']) / len(history['cpu_samples'])
            memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB

            # Multiple hang detection criteria
            hang_reasons = []
            is_hung = False

            # 1. Uninterruptible sleep state
            if status == psutil.STATUS_DISK_SLEEP:
                hang_reasons.append("Process in uninterruptible disk sleep (D state)")
                is_hung = True

            # 2. Long-running with no CPU activity
            time_since_activity = current_time - history['last_cpu_activity']
            if time_since_activity > self.hang_timeout and avg_cpu < self.cpu_threshold:
                hang_reasons.append(f"No CPU activity for {time_since_activity}")
                is_hung = True

            # 3. High memory usage with no activity
            if memory_mb > self.memory_threshold_mb and avg_cpu < self.cpu_threshold:
                hang_reasons.append(f"High memory usage ({memory_mb:.1f}MB) with no activity")
                is_hung = True

            # 4. Stuck in the same status for too long
            if len(set(history['status_changes'])) == 1 and len(history['status_changes']) >= 5:
                if status in [psutil.STATUS_DISK_SLEEP, psutil.STATUS_STOPPED]:
                    hang_reasons.append(f"Stuck in {status} status")
                    is_hung = True

            return {
                'is_hung': is_hung,
                'reason': '; '.join(hang_reasons),
                'cpu_percent': cpu_percent,
                'avg_cpu': avg_cpu,
                'memory_mb': memory_mb,
                'status': status,
                'runtime': current_time - create_time,
                'time_since_activity': time_since_activity
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.debug(f"Could not analyze process {proc.pid}: {e}")
            return {'is_hung': False, 'reason': f'Access denied: {e}', 'error': True}
    
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
