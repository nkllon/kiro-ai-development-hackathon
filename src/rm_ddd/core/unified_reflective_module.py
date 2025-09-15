"""
Unified ReflectiveModule Interface - RDI Compliant

This is the SINGLE, CANONICAL ReflectiveModule interface for:
- RDI Compliance
- Single source of truth
- Unified method signatures
- Consistent behavior across all components
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import os
import logging


class ModuleStatus(Enum):
    """Module operational status - RDI Compliant"""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class ModuleCapability(Enum):
    """Module capability types - RDI Compliant"""

    CORE_FUNCTIONALITY = "core_functionality"
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    VALIDATION = "validation"
    MONITORING = "monitoring"


@dataclass
class ModuleHealth:
    """Module health information - RDI Compliant"""

    module_id: str
    status: ModuleStatus
    health_score: float
    issues: List[str]
    last_check: datetime
    uptime_seconds: float = 0.0
    error_count: int = 0
    warning_count: int = 0


@dataclass
class GracefulDegradationResult:
    """Result of graceful degradation - RDI Compliant"""

    success: bool
    degraded_capabilities: List[ModuleCapability]
    remaining_capabilities: List[ModuleCapability]
    error_message: Optional[str] = None


class ReflectiveModule(ABC):
    """Unified ReflectiveModule interface - RDI Compliant"""

    def __init__(self):
        self._start_time = datetime.now()
        self._last_activity = datetime.now()
        self._error_count = 0
        self._warning_count = 0

        # Prometheus exporter integration
        self._prometheus_exporter = None
        self._enable_prometheus = self._should_enable_prometheus()
        self._logger = logging.getLogger(f"reflective_module.{self.__class__.__name__}")

        # Initialize Prometheus metrics if enabled
        if self._enable_prometheus:
            self._initialize_prometheus_metrics()

    @abstractmethod
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        pass

    @abstractmethod
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        pass

    @abstractmethod
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        pass

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, "register"):
            registry.register(metadata)

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": [],
            "capabilities": [],
        }

    def health_check(self):
        """Perform health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "module_id": getattr(self, "module_id", self.__class__.__name__),
        }

    def _should_enable_prometheus(self) -> bool:
        """Check if Prometheus metrics should be enabled."""
        return os.getenv("BEAST_MODE_PROMETHEUS_ENABLED", "true").lower() == "true"

    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for this module."""
        try:
            from beast_mode.monitoring.prometheus_exporter import PrometheusExporter

            self._prometheus_exporter = PrometheusExporter(
                port=int(os.getenv("BEAST_MODE_PROMETHEUS_PORT", "8000")),
                enable_http_server=True,
            )
            self._logger.info(
                f"Prometheus metrics enabled for {self.__class__.__name__}"
            )
        except ImportError:
            self._logger.warning(
                "Prometheus client not available. Install with: pip install prometheus-client"
            )
            self._enable_prometheus = False
        except Exception as e:
            self._logger.error(f"Failed to initialize Prometheus metrics: {e}")
            self._enable_prometheus = False

    def _collect_prometheus_metrics(self):
        """Collect metrics for Prometheus export."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return

        try:
            # Get module info
            module_info = self.get_module_info()
            module_id = module_info.get("module_id", self.__class__.__name__)

            # Get health status
            health_status = self.get_health_status()

            # Record module health metrics
            self._prometheus_exporter.record_module_health(
                module_id=module_id,
                status=health_status.status.value,
                health_score=health_status.health_score,
                error_count=health_status.error_count,
                warning_count=health_status.warning_count,
                uptime_seconds=health_status.uptime_seconds,
            )

            # Record module performance metrics
            self._prometheus_exporter.record_module_performance(
                module_id=module_id,
                class_name=self.__class__.__name__,
                version=module_info.get("version", "1.0.0"),
                capabilities=[cap.value for cap in self.get_capabilities()],
                last_activity=self._last_activity,
            )

        except Exception as e:
            self._logger.error(f"Failed to collect Prometheus metrics: {e}")

    def _update_activity(self):
        """Update last activity timestamp and collect metrics."""
        self._last_activity = datetime.now()
        if self._enable_prometheus:
            self._collect_prometheus_metrics()

    def _increment_error_count(self):
        """Increment error count and collect metrics."""
        self._error_count += 1
        self._update_activity()

    def _increment_warning_count(self):
        """Increment warning count and collect metrics."""
        self._warning_count += 1
        self._update_activity()

    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics for this module."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return {}

        try:
            return self._prometheus_exporter.get_module_metrics(
                module_id=getattr(self, "module_id", self.__class__.__name__)
            )
        except Exception as e:
            self._logger.error(f"Failed to get Prometheus metrics: {e}")
            return {}

    def enable_prometheus_metrics(self, enable: bool = True):
        """Enable or disable Prometheus metrics for this module."""
        self._enable_prometheus = enable
        if enable and not self._prometheus_exporter:
            self._initialize_prometheus_metrics()
        elif not enable:
            self._prometheus_exporter = None
