#!/usr/bin/env python3
"""
State Analyzer - State mutation analysis
=======================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Analyzes state mutations to determine node type.
"""

import hashlib
import json
from typing import Any, Dict, List


class StateMutationAnalyzer:
    """Analyzes state mutations to determine node type"""

    def __init__(self):
        self.modular_indicators = [
            "investigation_results",
            "successful_modules",
            "total_modules",
            "PageStructureAnalyzer",
            "NavigationAnalyzer",
            "ContentAnalyzer",
            "DiagnosticTester",
            "InvestigationOrchestrator",
        ]
        self.monolithic_indicators = [
            "comprehensive_investigation",
            "run_diagnostic_tests",
            "analyze_page_structure",
            "analyze_navigation_elements",
            "analyze_content_elements",
        ]

    def analyze_state_mutations(
        self, initial_state: Dict[str, Any], final_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze state mutations to determine node type"""
        analysis = {
            "mutation_count": 0,
            "modular_indicators_found": [],
            "monolithic_indicators_found": [],
            "state_signature": "",
            "mutation_pattern": "unknown",
        }
        
        # Count mutations
        for key, value in final_state.items():
            if key not in initial_state or initial_state[key] != value:
                analysis["mutation_count"] += 1
        
        # Look for modular indicators
        state_str = json.dumps(final_state, sort_keys=True)
        for indicator in self.modular_indicators:
            if indicator in state_str:
                analysis["modular_indicators_found"].append(indicator)
        
        # Look for monolithic indicators
        for indicator in self.monolithic_indicators:
            if indicator in state_str:
                analysis["monolithic_indicators_found"].append(indicator)
        
        # Create state signature
        analysis["state_signature"] = hashlib.md5(state_str.encode()).hexdigest()[:16]
        
        # Determine mutation pattern
        modular_count = len(analysis["modular_indicators_found"])
        monolithic_count = len(analysis["monolithic_indicators_found"])
        
        if modular_count > monolithic_count:
            analysis["mutation_pattern"] = "modular"
        elif monolithic_count > modular_count:
            analysis["mutation_pattern"] = "monolithic"
        else:
            analysis["mutation_pattern"] = "unclear"
        
        return analysis


