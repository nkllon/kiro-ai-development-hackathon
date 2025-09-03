#!/usr/bin/env python3
"""
RM-RDI Analysis System - Operator Control Script

EMERGENCY COMMANDS for operators:
- analysis-kill: INSTANT STOP (5 seconds)
- analysis-throttle: REDUCE RESOURCES (10 seconds)  
- analysis-stop: GRACEFUL SHUTDOWN (30 seconds)
- analysis-uninstall: COMPLETE REMOVAL (2 minutes)
"""

import sys
import os
import signal
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Try to import psutil, fall back to basic process management if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class AnalysisController:
    """Operator control interface for RM-RDI analysis system"""
    
    def __init__(self):
        self.process_name = "rm_rdi_analysis"
        self.analysis_processes: List[psutil.Process] = []
        
    def find_analysis_processes(self) -> List:
        """Find all running analysis processes"""
        if not HAS_PSUTIL:
            # Fallback: use ps command to find processes
            try:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                processes = []
                for line in result.stdout.split('\n'):
                    if 'rm_rdi' in line.lower() or 'analysis' in line.lower():
                        parts = line.split()
                        if len(parts) > 1:
                            try:
                                pid = int(parts[1])
                                processes.append({'pid': pid, 'cmdline': line})
                            except ValueError:
                                continue
                return processes
            except Exception:
                return []
        
        # Use psutil if available
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'rm_rdi' in cmdline.lower() or 'analysis' in proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
        
    def kill_analysis(self) -> Dict[str, Any]:
        """EMERGENCY KILL - Immediate termination of all analysis processes"""
        print("🚨 EMERGENCY KILL INITIATED - Stopping all analysis processes...")
        
        processes = self.find_analysis_processes()
        killed_count = 0
        errors = []
        
        for proc in processes:
            try:
                if HAS_PSUTIL:
                    print(f"  Killing process {proc.pid} ({proc.name()})")
                    proc.kill()  # SIGKILL - immediate termination
                else:
                    pid = proc['pid']
                    print(f"  Killing process {pid}")
                    os.kill(pid, signal.SIGKILL)
                killed_count += 1
            except Exception as e:
                pid = proc.pid if HAS_PSUTIL else proc['pid']
                errors.append(f"Failed to kill {pid}: {e}")
                
        # Wait a moment and verify
        time.sleep(1)
        remaining = self.find_analysis_processes()
        
        result = {
            "action": "emergency_kill",
            "processes_killed": killed_count,
            "processes_remaining": len(remaining),
            "errors": errors,
            "success": len(remaining) == 0,
            "time_taken": "< 5 seconds"
        }
        
        if result["success"]:
            print("✅ EMERGENCY KILL COMPLETE - All analysis processes stopped")
        else:
            print(f"⚠️  {len(remaining)} processes still running - may need manual intervention")
            
        return result
        
    def throttle_analysis(self) -> Dict[str, Any]:
        """THROTTLE - Reduce resource usage of analysis processes"""
        print("⚡ THROTTLING ANALYSIS - Reducing resource usage...")
        
        processes = self.find_analysis_processes()
        throttled_count = 0
        errors = []
        
        for proc in processes:
            try:
                # Set to lowest priority (nice value 19)
                proc.nice(19)
                
                # Send SIGUSR1 signal to trigger throttling (if supported)
                proc.send_signal(signal.SIGUSR1)
                
                print(f"  Throttled process {proc.pid} ({proc.name()})")
                throttled_count += 1
            except Exception as e:
                errors.append(f"Failed to throttle {proc.pid}: {e}")
                
        result = {
            "action": "throttle",
            "processes_throttled": throttled_count,
            "errors": errors,
            "success": throttled_count > 0,
            "time_taken": "< 10 seconds"
        }
        
        if result["success"]:
            print("✅ THROTTLING COMPLETE - Analysis processes running at reduced priority")
        else:
            print("⚠️  No processes found to throttle")
            
        return result
        
    def stop_analysis(self) -> Dict[str, Any]:
        """GRACEFUL STOP - Clean shutdown of analysis processes"""
        print("🛑 GRACEFUL STOP INITIATED - Requesting clean shutdown...")
        
        processes = self.find_analysis_processes()
        stopped_count = 0
        errors = []
        
        # Send SIGTERM for graceful shutdown
        for proc in processes:
            try:
                print(f"  Requesting shutdown of process {proc.pid} ({proc.name()})")
                proc.terminate()  # SIGTERM - graceful shutdown
                stopped_count += 1
            except Exception as e:
                errors.append(f"Failed to stop {proc.pid}: {e}")
                
        # Wait for graceful shutdown (up to 30 seconds)
        print("  Waiting for processes to shutdown gracefully...")
        for i in range(30):
            remaining = self.find_analysis_processes()
            if not remaining:
                break
            time.sleep(1)
            if i % 5 == 0:
                print(f"    Still waiting... ({30-i} seconds remaining)")
                
        # Force kill any remaining processes
        remaining = self.find_analysis_processes()
        if remaining:
            print("  Force killing remaining processes...")
            for proc in remaining:
                try:
                    proc.kill()
                except:
                    pass
                    
        final_remaining = self.find_analysis_processes()
        
        result = {
            "action": "graceful_stop",
            "processes_stopped": stopped_count,
            "processes_remaining": len(final_remaining),
            "errors": errors,
            "success": len(final_remaining) == 0,
            "time_taken": "< 30 seconds"
        }
        
        if result["success"]:
            print("✅ GRACEFUL STOP COMPLETE - All analysis processes stopped cleanly")
        else:
            print(f"⚠️  {len(final_remaining)} processes still running - manual intervention needed")
            
        return result
        
    def uninstall_analysis(self) -> Dict[str, Any]:
        """COMPLETE REMOVAL - Remove all analysis system components"""
        print("🔄 COMPLETE REMOVAL INITIATED - Removing analysis system...")
        
        # First stop all processes
        stop_result = self.stop_analysis()
        
        # Remove analysis system files (if they exist)
        removed_files = []
        errors = []
        
        analysis_paths = [
            Path("src/beast_mode/analysis/rm_rdi"),
            Path("scripts/analysis_control.py"),
            Path(".analysis_cache"),
            Path("analysis_reports"),
            Path("analysis_logs")
        ]
        
        for path in analysis_paths:
            try:
                if path.exists():
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                        removed_files.append(str(path))
                        print(f"  Removed directory: {path}")
                    else:
                        path.unlink()
                        removed_files.append(str(path))
                        print(f"  Removed file: {path}")
            except Exception as e:
                errors.append(f"Failed to remove {path}: {e}")
                
        result = {
            "action": "complete_removal",
            "processes_stopped": stop_result["success"],
            "files_removed": len(removed_files),
            "removed_paths": removed_files,
            "errors": errors,
            "success": stop_result["success"] and len(errors) == 0,
            "time_taken": "< 2 minutes"
        }
        
        if result["success"]:
            print("✅ COMPLETE REMOVAL SUCCESSFUL - System returned to baseline")
        else:
            print("⚠️  Removal completed with some errors - check logs")
            
        return result
        
    def status_analysis(self) -> Dict[str, Any]:
        """Get current status of analysis system"""
        processes = self.find_analysis_processes()
        
        if not HAS_PSUTIL:
            # Simple status without detailed metrics
            return {
                "action": "status",
                "processes_running": len(processes),
                "total_cpu_percent": "unknown (psutil not available)",
                "total_memory_mb": "unknown (psutil not available)",
                "process_details": processes,
                "system_healthy": True,  # Assume healthy if no processes found
                "note": "Install psutil for detailed resource monitoring"
            }
        
        # Detailed status with psutil
        process_info = []
        total_cpu = 0
        total_memory = 0
        
        for proc in processes:
            try:
                cpu_percent = proc.cpu_percent()
                memory_mb = proc.memory_info().rss / 1024 / 1024
                
                process_info.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "status": proc.status()
                })
                
                total_cpu += cpu_percent
                total_memory += memory_mb
                
            except Exception as e:
                process_info.append({
                    "pid": proc.pid,
                    "error": str(e)
                })
                
        return {
            "action": "status",
            "processes_running": len(processes),
            "total_cpu_percent": total_cpu,
            "total_memory_mb": total_memory,
            "process_details": process_info,
            "system_healthy": total_cpu < 25 and total_memory < 512  # Within limits
        }


def main():
    """Main entry point for operator commands"""
    if len(sys.argv) != 2:
        print("Usage: python analysis_control.py <command>")
        print("Commands:")
        print("  kill      - EMERGENCY KILL (instant stop)")
        print("  throttle  - THROTTLE (reduce resources)")
        print("  stop      - GRACEFUL STOP (clean shutdown)")
        print("  uninstall - COMPLETE REMOVAL (remove system)")
        print("  status    - STATUS (show current state)")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    controller = AnalysisController()
    
    try:
        if command == "kill":
            result = controller.kill_analysis()
        elif command == "throttle":
            result = controller.throttle_analysis()
        elif command == "stop":
            result = controller.stop_analysis()
        elif command == "uninstall":
            result = controller.uninstall_analysis()
        elif command == "status":
            result = controller.status_analysis()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
        # Print result summary
        print(f"\nResult: {result}")
        
        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()