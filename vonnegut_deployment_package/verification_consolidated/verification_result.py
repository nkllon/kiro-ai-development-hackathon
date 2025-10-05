#!/usr/bin/env python3
"""
Verification Result - Data structures
====================================

Extracted from sophisticated_indirect_verification.py for RDI compliance.
Contains data structures for verification results.
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class VerificationResult:
    """Result of verification analysis"""

    node_type: str
    confidence: float
    evidence: List[str]
    execution_characteristics: Dict[str, Any]
    state_mutations: Dict[str, Any]
    performance_metrics: Dict[str, Any]


