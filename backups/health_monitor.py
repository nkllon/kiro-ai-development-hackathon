"""
Health monitoring system for Beast Mode components.

Provides comprehensive health checking for all system components including
Redis connections, message processing, and agent communication.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pydantic import BaseModel

import redis.asyncio as redis


class HealthStatus(str, Enum):
    """Health status levels for components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health information for a system component."""

    component_name: str
    status: HealthStatus
    last_check: datetime
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    check_duration_ms: float = 0.0


class HealthCheck(BaseModel):
    """Configuration for a health check."""

    name: str
    check_function: Callable
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    recovery_threshold: int = 2


class HealthMonitor:
    """
    Comprehensive health monitoring system for Beast Mode components.

    Monitors Redis connectivity, message processing performance, agent
    communication health, and system resource usage.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.logger = logging.getLogger(__name__)
        self.health_checks: Dict[str, HealthCheck] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        self.failure_counts: Dict[str, int] = {}
        self.recovery_counts: Dict[str, int] = {}
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None

    async def register_health_check(
        self,
        name: str,
        check_function: Callable,
        interval_seconds: int = 30,
        timeout_seconds: int = 5,
        failure_threshold: int = 3,
        recovery_threshold: int = 2,
    ) -> None:
        """Register a new health check."""
        self.health_checks[name] = HealthCheck(
            name=name,
            check_function=check_function,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            failure_threshold=failure_threshold,
            recovery_threshold=recovery_threshold,
        )

        # Initialize component health
        self.component_health[name] = ComponentHealth(
            component_name=name,
            status=HealthStatus.UNKNOWN,
            last_check=datetime.now(),
            message="Health check registered",
        )

        self.failure_counts[name] = 0
        self.recovery_counts[name] = 0

        self.logger.info(f"Registered health check: {name}")

    async def start_monitoring(self) -> None:
        """Start the health monitoring system."""
        if self.monitoring_active:
            self.logger.warning("Health monitoring already active")
            return

        self.monitoring_active = True

        # Register default health checks
        await self._register_default_checks()

        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        self.logger.info("Health monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop the health monitoring system."""
        self.monitoring_active = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Health monitoring stopped")

    async def get_system_health(self) -> Dict[str, ComponentHealth]:
        """Get current health status for all components."""
        return self.component_health.copy()

    async def get_component_health(
        self, component_name: str
    ) -> Optional[ComponentHealth]:
        """Get health status for a specific component."""
        return self.component_health.get(component_name)

    async def is_system_healthy(self) -> bool:
        """Check if the entire system is healthy."""
        for health in self.component_health.values():
            if health.status == HealthStatus.UNHEALTHY:
                return False
        return True

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health."""
        healthy_count = sum(
            1
            for h in self.component_health.values()
            if h.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1
            for h in self.component_health.values()
            if h.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1
            for h in self.component_health.values()
            if h.status == HealthStatus.UNHEALTHY
        )
        unknown_count = sum(
            1
            for h in self.component_health.values()
            if h.status == HealthStatus.UNKNOWN
        )

        overall_status = HealthStatus.HEALTHY
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED
        elif unknown_count > 0:
            overall_status = HealthStatus.UNKNOWN

        return {
            "overall_status": overall_status,
            "total_components": len(self.component_health),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "unknown": unknown_count,
            "last_updated": datetime.now().isoformat(),
        }

    async def _register_default_checks(self) -> None:
        """Register default health checks for core components."""
        # Redis connectivity check
        await self.register_health_check(
            name="redis_connectivity",
            check_function=self._check_redis_connectivity,
            interval_seconds=15,
            timeout_seconds=3,
        )

        # Redis pub/sub check
        await self.register_health_check(
            name="redis_pubsub",
            check_function=self._check_redis_pubsub,
            interval_seconds=30,
            timeout_seconds=5,
        )

        # System resources check
        await self.register_health_check(
            name="system_resources",
            check_function=self._check_system_resources,
            interval_seconds=60,
            timeout_seconds=2,
        )

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        self.logger.info("Starting health monitoring loop")

        while self.monitoring_active:
            try:
                # Run all health checks
                tasks = []
                for check_name, health_check in self.health_checks.items():
                    # Check if it's time to run this check
                    last_check = self.component_health[check_name].last_check
                    if (
                        datetime.now() - last_check
                    ).total_seconds() >= health_check.interval_seconds:
                        task = asyncio.create_task(
                            self._run_health_check(check_name, health_check)
                        )
                        tasks.append(task)

                # Wait for all checks to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                # Sleep before next iteration
                await asyncio.sleep(5)  # Check every 5 seconds for due checks

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Back off on error

    async def _run_health_check(
        self, check_name: str, health_check: HealthCheck
    ) -> None:
        """Run a single health check."""
        start_time = time.time()

        try:
            # Run the check with timeout
            result = await asyncio.wait_for(
                health_check.check_function(), timeout=health_check.timeout_seconds
            )

            check_duration = (time.time() - start_time) * 1000  # Convert to ms

            # Process result
            if result.get("healthy", False):
                await self._handle_check_success(check_name, result, check_duration)
            else:
                await self._handle_check_failure(check_name, result, check_duration)

        except asyncio.TimeoutError:
            check_duration = (time.time() - start_time) * 1000
            await self._handle_check_failure(
                check_name,
                {"healthy": False, "message": "Health check timed out"},
                check_duration,
            )
        except Exception as e:
            check_duration = (time.time() - start_time) * 1000
            await self._handle_check_failure(
                check_name,
                {"healthy": False, "message": f"Health check failed: {str(e)}"},
                check_duration,
            )

    async def _handle_check_success(
        self, check_name: str, result: Dict[str, Any], duration_ms: float
    ) -> None:
        """Handle successful health check."""
        health_check = self.health_checks[check_name]

        # Reset failure count and increment recovery count
        self.failure_counts[check_name] = 0
        self.recovery_counts[check_name] += 1

        # Determine status based on recovery threshold
        if self.recovery_counts[check_name] >= health_check.recovery_threshold:
            status = HealthStatus.HEALTHY
            self.recovery_counts[check_name] = 0  # Reset after recovery
        else:
            # Still recovering
            current_health = self.component_health[check_name]
            if current_health.status == HealthStatus.UNHEALTHY:
                status = HealthStatus.DEGRADED
            else:
                status = current_health.status

        # Update component health
        self.component_health[check_name] = ComponentHealth(
            component_name=check_name,
            status=status,
            last_check=datetime.now(),
            message=result.get("message", "Health check passed"),
            details=result.get("details", {}),
            check_duration_ms=duration_ms,
        )

    async def _handle_check_failure(
        self, check_name: str, result: Dict[str, Any], duration_ms: float
    ) -> None:
        """Handle failed health check."""
        health_check = self.health_checks[check_name]

        # Reset recovery count and increment failure count
        self.recovery_counts[check_name] = 0
        self.failure_counts[check_name] += 1

        # Determine status based on failure threshold
        if self.failure_counts[check_name] >= health_check.failure_threshold:
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.DEGRADED

        # Update component health
        self.component_health[check_name] = ComponentHealth(
            component_name=check_name,
            status=status,
            last_check=datetime.now(),
            message=result.get("message", "Health check failed"),
            details=result.get("details", {}),
            check_duration_ms=duration_ms,
        )

    async def _check_redis_connectivity(self) -> Dict[str, Any]:
        """Check Redis server connectivity."""
        try:
            redis_client = redis.from_url(self.redis_url)

            # Test basic connectivity
            await redis_client.ping()

            # Get server info
            info = await redis_client.info()

            await redis_client.close()

            return {
                "healthy": True,
                "message": "Redis connectivity OK",
                "details": {
                    "redis_version": info.get("redis_version"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory_human": info.get("used_memory_human"),
                },
            }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Redis connectivity failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_redis_pubsub(self) -> Dict[str, Any]:
        """Check Redis pub/sub functionality."""
        try:
            redis_client = redis.from_url(self.redis_url)

            # Test pub/sub by publishing a test message
            test_channel = "beast_mode_health_check"
            test_message = f"health_check_{int(time.time())}"

            # Publish test message
            result = await redis_client.publish(test_channel, test_message)

            await redis_client.close()

            return {
                "healthy": True,
                "message": "Redis pub/sub OK",
                "details": {"test_channel": test_channel, "subscribers": result},
            }

        except Exception as e:
            return {
                "healthy": False,
                "message": f"Redis pub/sub failed: {str(e)}",
                "details": {"error": str(e)},
            }

    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil

            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Get memory usage
            memory = psutil.virtual_memory()

            # Get disk usage
            disk = psutil.disk_usage("/")

            # Determine health based on thresholds
            healthy = True
            issues = []

            if cpu_percent > 90:
                healthy = False
                issues.append(f"High CPU usage: {cpu_percent}%")

            if memory.percent > 90:
                healthy = False
                issues.append(f"High memory usage: {memory.percent}%")

            if disk.percent > 90:
                healthy = False
                issues.append(f"High disk usage: {disk.percent}%")

            message = (
                "System resources OK"
                if healthy
                else f"Resource issues: {', '.join(issues)}"
            )

            return {
                "healthy": healthy,
                "message": message,
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "disk_percent": disk.percent,
                    "disk_free_gb": round(disk.free / (1024**3), 2),
                },
            }

        except ImportError:
            return {
                "healthy": True,
                "message": "System resource monitoring unavailable (psutil not installed)",
                "details": {"note": "Install psutil for system resource monitoring"},
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": f"System resource check failed: {str(e)}",
                "details": {"error": str(e)},
            }
