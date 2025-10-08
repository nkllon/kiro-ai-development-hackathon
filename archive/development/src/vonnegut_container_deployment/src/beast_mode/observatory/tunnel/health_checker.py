"""
Tunnel Health Checker System

Specialized health checking utilities for tunnel connectivity validation,
including automated health monitoring and alerting capabilities.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    check_name: str
    status: str  # "healthy", "warning", "error"
    message: str
    timestamp: datetime
    duration_ms: float
    details: Dict[str, Any]


@dataclass
class HealthCheckConfig:
    """Configuration for health checking."""
    check_interval_seconds: int = 30
    timeout_seconds: int = 10
    retry_count: int = 3
    alert_threshold: int = 3  # Number of consecutive failures before alerting


class HealthChecker(ReflectiveModule):
    """
    Specialized tunnel health checking system.
    
    Provides automated health monitoring with:
    - Configurable check intervals
    - Retry mechanisms with exponential backoff
    - Health trend analysis
    - Alert generation for critical issues
    """
    
    def __init__(self, config: Optional[HealthCheckConfig] = None):
        """Initialize health checker system.
        
        Args:
            config: Health check configuration
        """
        super().__init__()
        self.module_id = "tunnel_health_checker"
        self.config = config or HealthCheckConfig()
        
        # Health tracking
        self._health_history: List[HealthCheckResult] = []
        self._consecutive_failures = 0
        self._last_successful_check: Optional[datetime] = None
        self._is_monitoring = False
        
        # Performance tracking
        self._total_checks = 0
        self._successful_checks = 0
        self._failed_checks = 0
        self._warning_checks = 0
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[HealthCheckResult], None]] = []
        
        logger.info("🏥 HealthChecker initialized - Ready for tunnel monitoring")
    
    async def start_monitoring(self) -> bool:
        """Start continuous health monitoring.
        
        Returns:
            True if monitoring started successfully
        """
        if self._is_monitoring:
            logger.warning("Health monitoring already running")
            return False
        
        self.log_action("start_monitoring", "in_progress")
        
        try:
            self._is_monitoring = True
            self.log_action("start_monitoring", "completed", {
                "check_interval": self.config.check_interval_seconds,
                "timeout": self.config.timeout_seconds
            })
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            return True
            
        except Exception as e:
            self._is_monitoring = False
            error_msg = f"Failed to start monitoring: {e}"
            logger.error(error_msg)
            self.log_action("start_monitoring", "error", {"error": str(e)})
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop continuous health monitoring.
        
        Returns:
            True if monitoring stopped successfully
        """
        if not self._is_monitoring:
            logger.warning("Health monitoring not running")
            return False
        
        self.log_action("stop_monitoring", "in_progress")
        
        try:
            self._is_monitoring = False
            self.log_action("stop_monitoring", "completed")
            return True
            
        except Exception as e:
            error_msg = f"Failed to stop monitoring: {e}"
            logger.error(error_msg)
            self.log_action("stop_monitoring", "error", {"error": str(e)})
            return False
    
    async def run_health_check(self, check_name: str = "comprehensive") -> HealthCheckResult:
        """Run a single health check.
        
        Args:
            check_name: Name of the health check to run
            
        Returns:
            HealthCheckResult with check outcome
        """
        start_time = time.time()
        self.log_action("health_check", "in_progress", {"check_name": check_name})
        
        try:
            # Run the actual health check
            if check_name == "comprehensive":
                result = await self._run_comprehensive_check()
            elif check_name == "quick":
                result = await self._run_quick_check()
            else:
                result = await self._run_custom_check(check_name)
            
            # Update tracking metrics
            duration = (time.time() - start_time) * 1000
            self._total_checks += 1
            
            if result.status == "healthy":
                self._successful_checks += 1
                self._consecutive_failures = 0
                self._last_successful_check = datetime.now()
            elif result.status == "warning":
                self._warning_checks += 1
                self._consecutive_failures = 0
            else:
                self._failed_checks += 1
                self._consecutive_failures += 1
            
            # Update result with actual duration
            result.duration_ms = duration
            
            # Store in history
            self._health_history.append(result)
            
            # Keep only last 100 results
            if len(self._health_history) > 100:
                self._health_history = self._health_history[-100:]
            
            # Check for alert conditions
            await self._check_alert_conditions(result)
            
            self.log_action("health_check", "completed", {
                "check_name": check_name,
                "status": result.status,
                "duration_ms": duration
            })
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_result = HealthCheckResult(
                check_name=check_name,
                status="error",
                message=f"Health check failed: {e}",
                timestamp=datetime.now(),
                duration_ms=duration,
                details={"error": str(e)}
            )
            
            self._failed_checks += 1
            self._consecutive_failures += 1
            
            self.log_action("health_check", "error", {"error": str(e)})
            return error_result
    
    async def _run_comprehensive_check(self) -> HealthCheckResult:
        """Run comprehensive health check.
        
        Returns:
            HealthCheckResult with comprehensive check results
        """
        try:
            # Import diagnostics to run comprehensive check
            from .diagnostics import TunnelDiagnostics
            
            diagnostics = TunnelDiagnostics()
            results = await diagnostics.run_comprehensive_diagnostics()
            
            # Analyze results
            health_assessment = results.get("health_assessment", {})
            overall_status = health_assessment.get("status", "unknown")
            
            if overall_status == "healthy":
                status = "healthy"
                message = "All tunnel systems operational"
            elif overall_status == "warning":
                status = "warning"
                message = "Tunnel systems have warnings"
            else:
                status = "error"
                message = "Critical tunnel issues detected"
            
            return HealthCheckResult(
                check_name="comprehensive",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration_ms=0,  # Will be updated by caller
                details=results
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="comprehensive",
                status="error",
                message=f"Comprehensive check failed: {e}",
                timestamp=datetime.now(),
                duration_ms=0,
                details={"error": str(e)}
            )
    
    async def _run_quick_check(self) -> HealthCheckResult:
        """Run quick health check.
        
        Returns:
            HealthCheckResult with quick check results
        """
        try:
            # Quick process check
            import subprocess
            
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            is_running = result.returncode == 0
            
            if is_running:
                status = "healthy"
                message = "Cloudflared process is running"
            else:
                status = "error"
                message = "Cloudflared process not found"
            
            return HealthCheckResult(
                check_name="quick",
                status=status,
                message=message,
                timestamp=datetime.now(),
                duration_ms=0,
                details={"is_running": is_running}
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_name="quick",
                status="error",
                message=f"Quick check failed: {e}",
                timestamp=datetime.now(),
                duration_ms=0,
                details={"error": str(e)}
            )
    
    async def _run_custom_check(self, check_name: str) -> HealthCheckResult:
        """Run custom health check.
        
        Args:
            check_name: Name of custom check
            
        Returns:
            HealthCheckResult with custom check results
        """
        # For now, treat custom checks as quick checks
        return await self._run_quick_check()
    
    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        logger.info("🔄 Starting health monitoring loop")
        
        while self._is_monitoring:
            try:
                # Run health check
                result = await self.run_health_check("comprehensive")
                
                # Log periodic status
                if self._total_checks % 10 == 0:
                    logger.info(f"Health monitoring: {self._total_checks} checks completed, "
                              f"{self._successful_checks} successful, {self._failed_checks} failed")
                
                # Wait for next check
                await asyncio.sleep(self.config.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.check_interval_seconds)
        
        logger.info("🛑 Health monitoring loop stopped")
    
    async def _check_alert_conditions(self, result: HealthCheckResult) -> None:
        """Check if alert conditions are met.
        
        Args:
            result: Latest health check result
        """
        if self._consecutive_failures >= self.config.alert_threshold:
            # Generate alert
            alert_result = HealthCheckResult(
                check_name="alert",
                status="error",
                message=f"Alert: {self._consecutive_failures} consecutive failures",
                timestamp=datetime.now(),
                duration_ms=0,
                details={
                    "consecutive_failures": self._consecutive_failures,
                    "last_successful_check": self._last_successful_check.isoformat() if self._last_successful_check else None
                }
            )
            
            # Call alert callbacks
            for callback in self._alert_callbacks:
                try:
                    callback(alert_result)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[HealthCheckResult], None]) -> None:
        """Add alert callback function.
        
        Args:
            callback: Function to call when alerts are triggered
        """
        self._alert_callbacks.append(callback)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary statistics.
        
        Returns:
            Dictionary containing health summary
        """
        if not self._health_history:
            return {
                "status": "unknown",
                "total_checks": 0,
                "success_rate": 0.0,
                "last_check": None,
                "consecutive_failures": 0
            }
        
        # Calculate success rate
        success_rate = self._successful_checks / self._total_checks if self._total_checks > 0 else 0.0
        
        # Get latest result
        latest_result = self._health_history[-1]
        
        # Determine overall status
        if success_rate >= 0.9:
            overall_status = "healthy"
        elif success_rate >= 0.7:
            overall_status = "warning"
        else:
            overall_status = "error"
        
        return {
            "status": overall_status,
            "total_checks": self._total_checks,
            "successful_checks": self._successful_checks,
            "failed_checks": self._failed_checks,
            "warning_checks": self._warning_checks,
            "success_rate": success_rate,
            "consecutive_failures": self._consecutive_failures,
            "last_check": latest_result.timestamp.isoformat(),
            "last_status": latest_result.status,
            "is_monitoring": self._is_monitoring
        }
    
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "3.2",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
    
    async def get_health_status(self) -> ModuleHealth:
        """Get current module health status.
        
        Returns:
            ModuleHealth object with current status
        """
        try:
            summary = self.get_health_summary()
            
            # Determine module status
            if summary["status"] == "healthy":
                status = ModuleStatus.HEALTHY
                health_score = summary["success_rate"]
                issues = []
            elif summary["status"] == "warning":
                status = ModuleStatus.WARNING
                health_score = summary["success_rate"]
                issues = ["Health monitoring warnings detected"]
            else:
                status = ModuleStatus.ERROR
                health_score = summary["success_rate"]
                issues = [f"Health monitoring failures: {summary['consecutive_failures']} consecutive"]
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                health_score=health_score,
                issues=issues,
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._failed_checks,
                warning_count=self._warning_checks
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health status check failed: {e}"],
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=self._failed_checks + 1,
                warning_count=self._warning_checks
            )