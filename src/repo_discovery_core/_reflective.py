"""Shared helper to import the unified reflective module dependency."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - prefer external dependency when available
    from rm_ddd.core.unified_reflective_module import (  # type: ignore
        GracefulDegradationResult,
        ModuleCapability,
        ModuleHealth,
        ModuleStatus,
        ReflectiveModule,
    )
except Exception:  # pragma: no cover - fallback when dependency absent
    try:
        from src.rm_ddd.core.unified_reflective_module import (  # type: ignore
            GracefulDegradationResult,
            ModuleCapability,
            ModuleHealth,
            ModuleStatus,
            ReflectiveModule,
        )
    except Exception:  # pragma: no cover - lightweight local fallback

        class ModuleStatus(Enum):
            HEALTHY = "healthy"
            WARNING = "warning"
            ERROR = "error"

        class ModuleCapability(Enum):
            CORE_FUNCTIONALITY = "core_functionality"
            DATA_PROCESSING = "data_processing"
            API_INTEGRATION = "api_integration"
            VALIDATION = "validation"
            MONITORING = "monitoring"

        @dataclass
        class ModuleHealth:
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
            success: bool
            degraded_capabilities: List[ModuleCapability]
            remaining_capabilities: List[ModuleCapability]
            error_message: Optional[str] = None

        class ReflectiveModule:
            """Minimal fallback implementation."""

            module_id: str

            def __init__(self) -> None:
                self._start_time = datetime.now()

            def get_module_info(self) -> Dict[str, Any]:  # pragma: no cover - runtime only
                raise NotImplementedError

            def get_capabilities(self) -> List[ModuleCapability]:  # pragma: no cover - runtime only
                return []

            def get_health_status(self) -> ModuleHealth:  # pragma: no cover - runtime only
                return ModuleHealth(
                    module_id=getattr(self, "module_id", self.__class__.__name__),
                    status=ModuleStatus.HEALTHY,
                    health_score=1.0,
                    issues=[],
                    last_check=datetime.now(),
                )

            def graceful_degradation(self) -> GracefulDegradationResult:  # pragma: no cover
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[],
                    remaining_capabilities=self.get_capabilities(),
                )

__all__ = [
    "GracefulDegradationResult",
    "ModuleCapability",
    "ModuleHealth",
    "ModuleStatus",
    "ReflectiveModule",
]

