"""
Mama Discoverer Core Validation

This module was extracted from mama_discoverer_core.py
as part of RM-DDD compliance refactoring.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass
from ..interfaces import MamaDiscoverer
from ..models import AccountabilityChain, AccountabilityRelationship, ConstraintSource, IndependenceClaim, ResearchResult, ChainChange, MappingUpdate, HumanEscalation
from src.rm_ddd.core.health import ModuleHealth


def _validate_independence_claim(self, claim: IndependenceClaim, chain: AccountabilityChain) -> bool:
    """Validate independence claim against discovered accountability chain."""
    has_immediate_accountability = len(chain.immediate_accountability) > 0
    has_ultimate_accountability = len(chain.ultimate_accountability) > 0
    has_constraints = len(chain.constraint_sources) > 0
    if chain.verification_confidence > 0.8 and (has_immediate_accountability or has_ultimate_accountability or has_constraints):
        return False
    return True
