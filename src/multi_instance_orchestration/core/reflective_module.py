"""Reflective Module base class for Beast Mode Framework compliance."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class HealthIndicator(BaseModel):
    """Health indicator for system monitoring."""

    name: str
    status: str  # "healthy", "warning", "critical"
    message: str
    timestamp: datetime
    details: dict[str, Any] = {}


class ModuleStatus(BaseModel):
    """Module status information."""

    module_name: str
    version: str
    status: str  # "active", "inactive", "error"
    uptime: float  # seconds
    last_activity: datetime
    health_indicators: list[HealthIndicator]
    performance_metrics: dict[str, Any] = {}


class ReflectiveModule(ABC):
    """Base class for all Beast Mode Framework modules.

    Implements systematic health monitoring and status reporting
    following Beast Mode Framework principles.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self._health_indicators: list[HealthIndicator] = []

    @abstractmethod
    def get_module_status(self) -> ModuleStatus:
        """Get current module status with health indicators."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if module is in healthy state."""
        pass

    @abstractmethod
    def get_health_indicators(self) -> list[HealthIndicator]:
        """Get current health indicators."""
        pass

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()

    def add_health_indicator(self, indicator: HealthIndicator) -> None:
        """Add a health indicator."""
        self._health_indicators.append(indicator)
        # Keep only last 100 indicators
        if len(self._health_indicators) > 100:
            self._health_indicators = self._health_indicators[-100:]

    def get_uptime(self) -> float:
        """Get module uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def create_health_indicator(
        self, name: str, status: str, message: str, details: Optional[dict[str, Any]] = None
    ) -> HealthIndicator:
        """Create a new health indicator."""
        return HealthIndicator(
            name=name,
            status=status,
            message=message,
            timestamp=datetime.now(),
            details=details or {},
        )
