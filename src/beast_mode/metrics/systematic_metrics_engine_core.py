#!/usr/bin/env python3
"""
Systematic Metrics Engine Core
=============================

Core functionality for systematic metrics collection and analysis.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Provide systematic metrics collection and comparison with ad-hoc approaches
"""

import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from ..core.reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
)


@dataclass
class MetricsData:
    """Metrics data structure."""

    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]
    approach: str  # 'systematic' or 'ad-hoc'


class SystematicMetricsEngine(ReflectiveModule):
    """Systematic Metrics Engine for collecting and analyzing development metrics."""

    def __init__(self):
        super().__init__()
        self.module_id = "systematic_metrics_engine"
        self.capabilities = [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
        ]
        self.dependencies = []
        self.metrics_history = []
        self.comparison_data = {}

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": self.dependencies,
            "capabilities": [cap.value for cap in self.capabilities],
        }

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return self.capabilities

    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=100.0,
            issues=[],
            last_check=datetime.now(),
        )

    def graceful_degradation(self):
        """Perform graceful degradation."""
        return {
            "success": True,
            "degraded_capabilities": [],
            "remaining_capabilities": [cap.value for cap in self.capabilities],
        }

    def collect_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        context: Dict[str, Any],
        approach: str = "systematic",
    ) -> MetricsData:
        """Collect a metric."""
        metric = MetricsData(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context,
            approach=approach,
        )
        self.metrics_history.append(metric)
        return metric

    def compare_approaches(
        self, systematic_metrics: List[MetricsData], adhoc_metrics: List[MetricsData]
    ) -> Dict[str, Any]:
        """Compare systematic vs ad-hoc approaches."""
        comparison = {
            "systematic_count": len(systematic_metrics),
            "adhoc_count": len(adhoc_metrics),
            "systematic_avg": 0.0,
            "adhoc_avg": 0.0,
            "improvement_percentage": 0.0,
            "timestamp": datetime.now(),
        }

        if systematic_metrics:
            comparison["systematic_avg"] = sum(
                m.value for m in systematic_metrics
            ) / len(systematic_metrics)

        if adhoc_metrics:
            comparison["adhoc_avg"] = sum(m.value for m in adhoc_metrics) / len(
                adhoc_metrics
            )

        if comparison["adhoc_avg"] > 0:
            improvement = (
                (comparison["systematic_avg"] - comparison["adhoc_avg"])
                / comparison["adhoc_avg"]
            ) * 100
            comparison["improvement_percentage"] = improvement

        self.comparison_data = comparison
        return comparison

    def generate_report(self) -> Dict[str, Any]:
        """Generate metrics report."""
        return {
            "total_metrics": len(self.metrics_history),
            "systematic_metrics": len(
                [m for m in self.metrics_history if m.approach == "systematic"]
            ),
            "adhoc_metrics": len(
                [m for m in self.metrics_history if m.approach == "ad-hoc"]
            ),
            "latest_comparison": self.comparison_data,
            "timestamp": datetime.now(),
        }
