#!/usr/bin/env python3
"""
🎯 METRICS CALCULATOR MODULE
===========================
Enhanced metrics calculation for SCA procedure.
Handles efficiency metrics and performance tracking.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from typing import Dict


class MetricsCalculatorModule:
    """Metrics calculator module for SCA procedure."""

    def calculate_enhanced_efficiency_metrics(
        self, loop_results: Dict, enhanced_metrics: Dict
    ) -> Dict:
        """Calculate enhanced efficiency metrics."""
        # Calculate efficiency score
        total_files = sum(
            result.get("files_processed", 0) for result in loop_results.values()
        )

        if total_files == 0:
            return {"efficiency_score": 0.0}

        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate(enhanced_metrics)

        # Calculate saturation rate
        saturation_rate = self._calculate_saturation_rate(enhanced_metrics)

        # Calculate resource utilization
        resource_utilization = self._calculate_resource_utilization(enhanced_metrics)

        # Calculate overall efficiency score
        efficiency_score = (
            improvement_rate * 0.4 + saturation_rate * 0.3 + resource_utilization * 0.3
        )

        return {
            "efficiency_score": efficiency_score,
            "improvement_rate": improvement_rate,
            "saturation_rate": saturation_rate,
            "resource_utilization": resource_utilization,
            "files_processed": total_files,
        }

    def _calculate_improvement_rate(self, enhanced_metrics: Dict) -> float:
        """Calculate improvement rate from metrics."""
        if not enhanced_metrics.get("improvement_rates"):
            return 0.0

        recent_rates = enhanced_metrics["improvement_rates"][-5:]  # Last 5 rates
        return sum(recent_rates) / len(recent_rates) if recent_rates else 0.0

    def _calculate_saturation_rate(self, enhanced_metrics: Dict) -> float:
        """Calculate saturation rate from metrics."""
        if not enhanced_metrics.get("saturation_rates"):
            return 0.0

        recent_rates = enhanced_metrics["saturation_rates"][-5:]  # Last 5 rates
        return sum(recent_rates) / len(recent_rates) if recent_rates else 0.0

    def _calculate_resource_utilization(self, enhanced_metrics: Dict) -> float:
        """Calculate resource utilization from metrics."""
        if not enhanced_metrics.get("resource_utilization"):
            return 0.0

        recent_utilization = enhanced_metrics["resource_utilization"][-5:]  # Last 5
        return (
            sum(recent_utilization) / len(recent_utilization)
            if recent_utilization
            else 0.0
        )


