"""
Interfaces Services

This module was extracted from interfaces.py
as part of RM-DDD compliance refactoring.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from .models import AnalysisResult, AnalysisContext, Delusion, RecoveryPlan, ValidationResult, ConsensusResult, MultiDimensionalResult, RecoveryAction, ValidationCertificate

class RecoveryEngine(ABC):
    """
    Abstract base class for recovery engines that detect and fix delusions.
    
    Recovery engines provide systematic fix generation and application
    for detected code delusions and issues.
    """

    def __init__(self, name: str, version: str='1.0.0'):
        self.name = name
        self.version = version

    @abstractmethod
    async def detect_delusions(self, code: str, context: Optional[AnalysisContext]=None) -> List[Delusion]:
        """
        Detect systematic delusions in code using pattern recognition.
        
        Args:
            code: Source code to analyze for delusions
            context: Optional analysis context for additional information
            
        Returns:
            List of detected delusions with confidence scores
        """
        pass

    @abstractmethod
    async def generate_fix(self, delusion: Delusion) -> RecoveryPlan:
        """
        Generate systematic fix plan for detected delusion.
        
        Args:
            delusion: Delusion to generate fix for
            
        Returns:
            RecoveryPlan with actions to resolve the delusion
            
        Raises:
            RecoveryError: If fix cannot be generated for the delusion
        """
        pass

    @abstractmethod
    async def apply_recovery(self, plan: RecoveryPlan) -> ValidationResult:
        """
        Apply recovery plan with validation and rollback capability.
        
        Args:
            plan: Recovery plan to execute
            
        Returns:
            ValidationResult indicating success/failure of recovery
            
        Raises:
            RecoveryError: If recovery application fails
        """
        pass

    @abstractmethod
    async def validate_fix(self, original: str, fixed: str, delusion: Delusion) -> ValidationResult:
        """
        Validate that fix resolves delusion without introducing new issues.
        
        Args:
            original: Original code before fix
            fixed: Code after applying fix
            delusion: Original delusion that was fixed
            
        Returns:
            ValidationResult with validation details and confidence
        """
        pass

    def get_supported_delusion_types(self) -> List[str]:
        """Get list of delusion types this engine can handle"""
        return []

    def can_handle_delusion(self, delusion: Delusion) -> bool:
        """Check if engine can handle a specific delusion"""
        supported_types = self.get_supported_delusion_types()
        return delusion.category.value in supported_types

class ConsensusEngine(ABC):
    """
    Abstract base class for multi-agent consensus engines.
    
    Consensus engines coordinate multiple expert agents to build
    consensus and resolve conflicts in analysis results.
    """

    def __init__(self, name: str, version: str='1.0.0'):
        self.name = name
        self.version = version

    @abstractmethod
    async def build_consensus(self, agents: List[GhostbustersExpertAgent], context: AnalysisContext, confidence_threshold: float=0.8) -> ConsensusResult:
        """
        Orchestrate multiple agents to build consensus on analysis.
        
        Args:
            agents: List of expert agents to coordinate
            context: Analysis context for all agents
            confidence_threshold: Minimum confidence required for consensus
            
        Returns:
            ConsensusResult with unified analysis or conflict information
        """
        pass

    @abstractmethod
    async def resolve_conflicts(self, conflicting_results: List[AnalysisResult]) -> AnalysisResult:
        """
        Resolve conflicts between agent analyses using systematic methods.
        
        Args:
            conflicting_results: Analysis results that conflict with each other
            
        Returns:
            Unified AnalysisResult that resolves the conflicts
            
        Raises:
            ConsensusError: If conflicts cannot be resolved systematically
        """
        pass

    def get_resolution_methods(self) -> List[str]:
        """Get list of conflict resolution methods supported"""
        return ['majority_vote', 'weighted_confidence', 'expert_override', 'human_escalation']
