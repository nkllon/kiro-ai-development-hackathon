#!/usr/bin/env python3
"""
🎯 ADAPTIVE INTELLIGENCE MODULE
==============================
Adaptive intelligence for SCA procedure.
Handles subset sizing, thresholds, and diminishing returns detection.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

from typing import Dict, List


class AdaptiveIntelligenceModule:
    """Adaptive intelligence module for SCA procedure."""

    def __init__(self, base_subset_size: int, diminishing_returns_threshold: float):
        self.base_subset_size = base_subset_size
        self.diminishing_returns_threshold = diminishing_returns_threshold

    def calculate_adaptive_subset_size(self, current_saturation: Dict) -> int:
        """Calculate adaptive subset size based on current saturation levels."""
        # Lesson 1: Adaptive subset sizing
        # When saturation is high, use smaller subsets for precision
        # When saturation is low, use larger subsets for coverage
        avg_saturation = (
            current_saturation["rdi"]
            + current_saturation["health"]
            + current_saturation["registry"]
        ) / 3

        if avg_saturation > 0.9:  # High saturation - precision mode
            return max(200, int(self.base_subset_size * 0.3))
        elif avg_saturation > 0.7:  # Medium saturation - balanced mode
            return int(self.base_subset_size * 0.6)
        else:  # Low saturation - coverage mode
            return self.base_subset_size

    def calculate_dynamic_threshold(
        self, loop_number: int, efficiency_history: List[float]
    ) -> float:
        """Calculate dynamic diminishing returns threshold."""
        # Lesson 3: Dynamic threshold adjustment
        # Adjust threshold based on historical performance
        if loop_number < 3:
            return self.diminishing_returns_threshold

        if len(efficiency_history) < 3:
            return self.diminishing_returns_threshold

        # Calculate trend
        recent_avg = sum(efficiency_history[-3:]) / 3
        if recent_avg < 0.3:  # Poor performance - lower threshold
            return self.diminishing_returns_threshold * 0.8
        elif recent_avg > 0.7:  # Good performance - higher threshold
            return min(0.9, self.diminishing_returns_threshold * 1.2)
        else:
            return self.diminishing_returns_threshold

    def enhanced_diminishing_returns_detection(
        self, efficiency_history: List[float], loop_number: int
    ) -> bool:
        """Enhanced diminishing returns detection with adaptive thresholds."""
        if len(efficiency_history) < 3:
            return False

        # Get dynamic threshold
        threshold = self.calculate_dynamic_threshold(loop_number, efficiency_history)

        # Check recent performance
        recent_efficiency = efficiency_history[-1]
        if recent_efficiency < threshold:
            # Check if this is a trend
            if len(efficiency_history) >= 3:
                recent_avg = sum(efficiency_history[-3:]) / 3
                if recent_avg < threshold:
                    return True

        return False


