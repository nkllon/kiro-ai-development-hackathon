#!/usr/bin/env python3
"""
Performance Analyzer - Performance characteristics analysis
=========================================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Analyzes performance characteristics to determine node type.
"""

from typing import Any, Dict, List


class PerformanceAnalyzer:
    """Analyzes performance characteristics"""

    def __init__(self):
        self.performance_baselines = {
            "monolithic": {
                "min_execution_time": 0.05,
                "max_execution_time": 0.5,
                "min_memory_delta": 2.0,
                "max_memory_delta": 20.0,
                "execution_variance": 0.1,
            },
            "modular": {
                "min_execution_time": 0.001,
                "max_execution_time": 0.1,
                "min_memory_delta": 0.5,
                "max_memory_delta": 5.0,
                "execution_variance": 0.05,
            },
        }

    def analyze_performance(
        self, execution_times: List[float], memory_deltas: List[float]
    ) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        analysis = {
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "execution_variance": max(execution_times) - min(execution_times),
            "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
            "performance_type": "unknown",
            "confidence": 0.0,
        }
        
        # Analyze execution time
        avg_time = analysis["avg_execution_time"]
        monolithic_time_range = self.performance_baselines["monolithic"]
        modular_time_range = self.performance_baselines["modular"]
        
        if (
            modular_time_range["min_execution_time"]
            <= avg_time
            <= modular_time_range["max_execution_time"]
        ):
            analysis["performance_type"] = "modular"
            analysis["confidence"] += 0.4
        elif (
            monolithic_time_range["min_execution_time"]
            <= avg_time
            <= monolithic_time_range["max_execution_time"]
        ):
            analysis["performance_type"] = "monolithic"
            analysis["confidence"] += 0.4
        
        # Analyze memory usage
        avg_memory = analysis["avg_memory_delta"]
        if (
            modular_time_range["min_memory_delta"]
            <= avg_memory
            <= modular_time_range["max_memory_delta"]
        ):
            if analysis["performance_type"] == "modular":
                analysis["confidence"] += 0.3
            else:
                analysis["performance_type"] = "modular"
                analysis["confidence"] = 0.3
        elif (
            monolithic_time_range["min_memory_delta"]
            <= avg_memory
            <= monolithic_time_range["max_memory_delta"]
        ):
            if analysis["performance_type"] == "monolithic":
                analysis["confidence"] += 0.3
            else:
                analysis["performance_type"] = "monolithic"
                analysis["confidence"] = 0.3
        
        # Analyze execution variance
        variance = analysis["execution_variance"]
        if variance <= modular_time_range["execution_variance"]:
            if analysis["performance_type"] == "modular":
                analysis["confidence"] += 0.2
        elif variance >= monolithic_time_range["execution_variance"]:
            if analysis["performance_type"] == "monolithic":
                analysis["confidence"] += 0.2
        
        return analysis

