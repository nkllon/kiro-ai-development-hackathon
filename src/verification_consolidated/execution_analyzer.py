#!/usr/bin/env python3
"""
Execution Analyzer - Execution characteristics analysis
=====================================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Analyzes execution characteristics to determine node type.
"""

from typing import Any, Dict


class IndirectVerificationAnalyzer:
    """Analyzes execution characteristics to determine node type"""

    def __init__(self):
        self.baseline_characteristics = {
            "monolithic": {
                "execution_time_range": (0.1, 0.5),
                "memory_usage_range": (5, 20),
                "state_mutation_count": (10, 30),
                "message_count": (2, 5),
                "investigation_depth": "comprehensive",
            },
            "modular": {
                "execution_time_range": (0.01, 0.1),
                "memory_usage_range": (1, 5),
                "state_mutation_count": (5, 15),
                "message_count": (3, 8),
                "investigation_depth": "orchestrated",
            },
        }

    def analyze_execution_characteristics(
        self, execution_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze execution characteristics against baselines"""
        scores = {"monolithic_score": 0.0, "modular_score": 0.0}
        
        # Execution time analysis
        exec_time = execution_data.get("execution_time", 0)
        monolithic_time_range = self.baseline_characteristics["monolithic"]["execution_time_range"]
        modular_time_range = self.baseline_characteristics["modular"]["execution_time_range"]
        
        if monolithic_time_range[0] <= exec_time <= monolithic_time_range[1]:
            scores["monolithic_score"] += 0.3
        if modular_time_range[0] <= exec_time <= modular_time_range[1]:
            scores["modular_score"] += 0.3
        
        # Memory usage analysis
        memory_usage = execution_data.get("memory_delta", 0)
        monolithic_memory_range = self.baseline_characteristics["monolithic"]["memory_usage_range"]
        modular_memory_range = self.baseline_characteristics["modular"]["memory_usage_range"]
        
        if monolithic_memory_range[0] <= memory_usage <= monolithic_memory_range[1]:
            scores["monolithic_score"] += 0.2
        if modular_memory_range[0] <= memory_usage <= modular_memory_range[1]:
            scores["modular_score"] += 0.2
        
        # State mutation analysis
        state_mutations = execution_data.get("state_mutation_count", 0)
        monolithic_state_range = self.baseline_characteristics["monolithic"]["state_mutation_count"]
        modular_state_range = self.baseline_characteristics["modular"]["state_mutation_count"]
        
        if monolithic_state_range[0] <= state_mutations <= monolithic_state_range[1]:
            scores["monolithic_score"] += 0.2
        if modular_state_range[0] <= state_mutations <= modular_state_range[1]:
            scores["modular_score"] += 0.2
        
        # Message count analysis
        message_count = execution_data.get("message_count", 0)
        monolithic_message_range = self.baseline_characteristics["monolithic"]["message_count"]
        modular_message_range = self.baseline_characteristics["modular"]["message_count"]
        
        if monolithic_message_range[0] <= message_count <= monolithic_message_range[1]:
            scores["monolithic_score"] += 0.1
        if modular_message_range[0] <= message_count <= modular_message_range[1]:
            scores["modular_score"] += 0.1
        
        return scores
