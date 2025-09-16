#!/usr/bin/env python3
"""
🎯 PHASE MANAGER MODULE
======================
Phase management for SCA procedure.
Handles phase prioritization and execution order.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from typing import Dict, List


class PhaseManagerModule:
    """Phase management module for SCA procedure."""

    def determine_phase_priority(self, current_saturation: Dict) -> List[str]:
        """Determine phase priority based on current saturation levels."""
        # Lesson 2: Phase prioritization
        # Focus on areas with lowest saturation first
        phases = []
        saturation_items = [
            ("rdi", current_saturation["rdi"]),
            ("health", current_saturation["health"]),
            ("registry", current_saturation["registry"]),
        ]
        # Sort by saturation (lowest first)
        saturation_items.sort(key=lambda x: x[1])
        for phase, _ in saturation_items:
            phases.append(phase)
        # Always add size fix as last phase
        phases.append("size")
        return phases

    def calculate_phase_weights(self, pre_metrics: Dict) -> Dict:
        """Calculate phase weights based on pre-metrics."""
        weights = {}
        total_impact = sum(pre_metrics.values())

        if total_impact == 0:
            # Equal weights if no impact data
            for phase in ["rdi", "health", "registry", "size"]:
                weights[phase] = 0.25
        else:
            # Weight based on impact
            for phase, impact in pre_metrics.items():
                weights[phase] = impact / total_impact

        return weights

