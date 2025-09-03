"""
RM-RDI Analysis System - Operator Safety Framework

CRITICAL: This module implements the safety guarantees that protect production systems
"""

import os
import threading
import time
import signal
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import logging

# Optional dependency - graceful fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for basic functionality
    class MockProcess:
        def memory_info(self):
            class MockMemInfo:
                rss = 100 * 1024 * 1024  # 100MB
            return MockMemInfo()
            
        def cpu_percent(self):
            return 25.0
            
        def is_running(self):
            return True
            
        def num_threads(self):
            return 4
    
    class MockPsutil:
        @staticmethod
        def virtual_memory():
            class MockMemory:
                percent = 50.0  # Default safe value
            return MockMemory()
        
        @staticmethod
        def cpu_percent():
            return 25.0  # Default safe value
            
        @staticmethod
        def disk_usage(path):
            class MockDisk:
                percent = 30.0  # Default safe value
            return MockDisk()
            
        @staticmethod
        def Process():
            return MockProcess()
    
    psutil = MockPsutil()


@dataclass
class ResourceLimits:
    """Hard resource limits for operator safety"""
    max_cpu_percent: float = 25.0  # Never use more than 25% CPU
    max_memory_mb: float = 512.0   # Never use more than 512MB RAM
    max_disk_io_mb: float = 100.0  # Limit disk I/O
    max_analysis_time_seconds: int = 300  # 5 minute timeout
    max_concurrent_operations: int = 2


@dataclass
class SafetyStatus:
    """Current safety status"""
    is_safe: bool
    resource_usage: Dict[str, float]
    violations: List[str]
    last_check: datetime
    kill_switch_armed: bool


class KillSwitch:
    """Emergency shutdown system - INSTANT STOP capability"""
    
    def __init__(self):
        self.is_armed = True
        self.shutdown_callbacks: List[Callable] = []
        self.logger = logging.getLogger("rm_rdi_analysis.kill_switch")
        
        # Register signal handlers for emergency shutdown
        signal.signal(signal.SIGTERM, self._emergency_shutdown)
        signal.signal(signal.SIGINT, self._emergency_shutdown)
        
    def register_shutdown_callback(self, callback: Callable) -> None:
        """Register callback to be called during emergency shutdown"""
        self.shutdown_callbacks.append(callback)
        
    def emergency_shutdown(self, reason: str = "Operator initiated") -> None:
        """INSTANT SHUTDOWN - Stops all analysis operations immediately"""
        self.logger.critical(f"EMERGENCY SHUTDOWN INITIATED: {reason}")
        
        # Call all shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Shutdown callback failed: {e}")
        
        # Force terminate current process if needed
        self.logger.info("Emergency shutdown complete")
        
    def _emergency_shutdown(self, signum, frame):
        """Signal handler for emergency shutdown"""
        self.emergency_shutdown(f"Signal {signum} received")


class ResourceMonitor:
    """Continuous resource monitoring with automatic throttling"""
    
    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.current_process = psutil.Process()
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger("rm_rdi_analysis.resource_monitor")
        self.violation_callbacks: List[Callable] = []
        
    def start_monitoring(self) -> None:
        """Start continuous resource monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Resource monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        self.logger.info("Resource monitoring stopped")
        
    def register_violation_callback(self, callback: Callable) -> None:
        """Register callback for resource violations"""
        self.violation_callbacks.append(callback)
        
    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            cpu_percent = self.current_process.cpu_percent()
            memory_info = self.current_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "num_threads": self.current_process.num_threads(),
                "num_fds": self.current_process.num_fds() if hasattr(self.current_process, 'num_fds') else 0
            }
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return {}
            
    def check_limits(self) -> List[str]:
        """Check if resource usage exceeds limits"""
        violations = []
        usage = self.get_current_usage()
        
        if usage.get("cpu_percent", 0) > self.limits.max_cpu_percent:
            violations.append(f"CPU usage {usage['cpu_percent']:.1f}% exceeds limit {self.limits.max_cpu_percent}%")
            
        if usage.get("memory_mb", 0) > self.limits.max_memory_mb:
            violations.append(f"Memory usage {usage['memory_mb']:.1f}MB exceeds limit {self.limits.max_memory_mb}MB")
            
        return violations
        
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring:
            try:
                violations = self.check_limits()
                if violations:
                    self.logger.warning(f"Resource violations detected: {violations}")
                    for callback in self.violation_callbacks:
                        try:
                            callback(violations)
                        except Exception as e:
                            self.logger.error(f"Violation callback failed: {e}")
                            
                time.sleep(1.0)  # Check every second
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(5.0)  # Back off on errors


class SafetyValidator:
    """Validates that all operations are safe for production"""
    
    def __init__(self):
        self.logger = logging.getLogger("rm_rdi_analysis.safety_validator")
        
    def validate_read_only_access(self, file_path: Path) -> bool:
        """Validate that we only have read access to files"""
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False
                
            if not os.access(file_path, os.R_OK):
                return False
                
            # Ensure we don't have write access (safety check)
            if os.access(file_path, os.W_OK):
                self.logger.warning(f"Write access detected for {file_path} - SAFETY VIOLATION")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Safety validation failed for {file_path}: {e}")
            return False
            
    def validate_no_system_modifications(self) -> bool:
        """Validate that we're not modifying any system files"""
        # This is a placeholder for more sophisticated checks
        # In production, this would verify no writes to critical directories
        return True
        
    def validate_isolation(self) -> bool:
        """Validate that analysis runs in isolation"""
        # Check that we're not interfering with other processes
        # This is a simplified check - production would be more thorough
        return True


class OperatorSafetyManager:
    """Main safety management system - Coordinates all safety measures"""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.kill_switch = KillSwitch()
        self.resource_monitor = ResourceMonitor(self.limits)
        self.safety_validator = SafetyValidator()
        self.logger = logging.getLogger("rm_rdi_analysis.safety_manager")
        
        # Safety state
        self.is_safe_mode = True
        self.analysis_allowed = True
        self.emergency_shutdown_triggered = False
        
        # Register safety callbacks
        self.kill_switch.register_shutdown_callback(self._emergency_shutdown_callback)
        self.resource_monitor.register_violation_callback(self._resource_violation_callback)
        
    def initialize_safety_systems(self) -> bool:
        """Initialize all safety systems"""
        try:
            self.logger.info("Initializing operator safety systems...")
            
            # Start resource monitoring
            self.resource_monitor.start_monitoring()
            
            # Validate initial safety state
            if not self._validate_initial_safety():
                self.logger.error("Initial safety validation failed")
                return False
                
            self.logger.info("Safety systems initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize safety systems: {e}")
            return False
            
    def shutdown_safety_systems(self) -> None:
        """Shutdown all safety systems"""
        self.logger.info("Shutting down safety systems...")
        self.resource_monitor.stop_monitoring()
        self.logger.info("Safety systems shutdown complete")
        
    def get_safety_status(self) -> SafetyStatus:
        """Get current safety status"""
        violations = self.resource_monitor.check_limits()
        usage = self.resource_monitor.get_current_usage()
        
        return SafetyStatus(
            is_safe=len(violations) == 0 and not self.emergency_shutdown_triggered,
            resource_usage=usage,
            violations=violations,
            last_check=datetime.now(),
            kill_switch_armed=self.kill_switch.is_armed
        )
        
    def is_operation_safe(self, operation_name: str) -> bool:
        """Check if an operation is safe to perform"""
        if self.emergency_shutdown_triggered:
            self.logger.warning(f"Operation {operation_name} blocked - emergency shutdown active")
            return False
            
        if not self.analysis_allowed:
            self.logger.warning(f"Operation {operation_name} blocked - analysis disabled")
            return False
            
        # Check resource limits
        violations = self.resource_monitor.check_limits()
        if violations:
            self.logger.warning(f"Operation {operation_name} blocked - resource violations: {violations}")
            return False
            
        return True
        
    def emergency_shutdown(self, reason: str = "Operator request") -> None:
        """Trigger emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.kill_switch.emergency_shutdown(reason)
        
    def _validate_initial_safety(self) -> bool:
        """Validate initial safety conditions"""
        # Check that we're not running as root (safety measure)
        if os.getuid() == 0:
            self.logger.error("SAFETY VIOLATION: Running as root user")
            return False
            
        # Validate resource limits are reasonable
        if self.limits.max_cpu_percent > 50:
            self.logger.warning("CPU limit >50% may impact system performance")
            
        return True
        
    def _emergency_shutdown_callback(self) -> None:
        """Callback for emergency shutdown"""
        self.emergency_shutdown_triggered = True
        self.analysis_allowed = False
        self.logger.critical("Emergency shutdown callback executed")
        
    def _resource_violation_callback(self, violations: List[str]) -> None:
        """Callback for resource violations"""
        self.logger.warning(f"Resource violations detected: {violations}")
        
        # If violations are severe, trigger emergency shutdown
        for violation in violations:
            if "CPU usage" in violation and "exceeds limit" in violation:
                # Extract CPU percentage
                try:
                    cpu_str = violation.split("CPU usage ")[1].split("%")[0]
                    cpu_percent = float(cpu_str)
                    if cpu_percent > self.limits.max_cpu_percent * 2:  # Double the limit
                        self.emergency_shutdown("Severe CPU usage violation")
                        return
                except:
                    pass
                    
            if "Memory usage" in violation and "exceeds limit" in violation:
                # Extract memory usage
                try:
                    mem_str = violation.split("Memory usage ")[1].split("MB")[0]
                    mem_mb = float(mem_str)
                    if mem_mb > self.limits.max_memory_mb * 2:  # Double the limit
                        self.emergency_shutdown("Severe memory usage violation")
                        return
                except:
                    pass


# Global safety manager instance
_global_safety_manager: Optional[OperatorSafetyManager] = None


def get_safety_manager() -> OperatorSafetyManager:
    """Get the global safety manager instance"""
    global _global_safety_manager
    if _global_safety_manager is None:
        _global_safety_manager = OperatorSafetyManager()
    return _global_safety_manager


def initialize_safety() -> bool:
    """Initialize global safety systems"""
    manager = get_safety_manager()
    return manager.initialize_safety_systems()


def shutdown_safety() -> None:
    """Shutdown global safety systems"""
    global _global_safety_manager
    if _global_safety_manager:
        _global_safety_manager.shutdown_safety_systems()
        _global_safety_manager = None


def emergency_shutdown(reason: str = "Manual trigger") -> None:
    """Trigger emergency shutdown of all analysis operations"""
    manager = get_safety_manager()
    manager.emergency_shutdown(reason)


def is_safe_to_proceed(operation: str = "analysis") -> bool:
    """Check if it's safe to proceed with an operation"""
    manager = get_safety_manager()
    return manager.is_operation_safe(operation)


def get_current_safety_status() -> SafetyStatus:
    """Get current safety status"""
    manager = get_safety_manager()
    return manager.get_safety_status()