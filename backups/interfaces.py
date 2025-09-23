"""
Ghostbusters Framework Core Interfaces

Abstract base classes and protocols that define the contracts
for expert agents, recovery engines, and validation frameworks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from .models import (
    AnalysisResult,
    AnalysisContext,
    Delusion,
    RecoveryPlan,
    ValidationResult,
    ConsensusResult,
    MultiDimensionalResult,
    RecoveryAction,
    ValidationCertificate,
)


class GhostbustersExpertAgent(ABC):
    """
    Abstract base class for all Ghostbusters expert agents.

    Expert agents provide domain-specific analysis capabilities
    that amplify human creativity through systematic AI analysis.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._capabilities: List[str] = []

    @abstractmethod
    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """
        Perform domain-specific analysis with confidence scoring.

        Args:
            context: Analysis context containing target and configuration

        Returns:
            AnalysisResult with findings, recommendations, and confidence score

        Raises:
            AnalysisError: If analysis fails due to invalid input or system error
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of analysis capabilities this agent provides.

        Returns:
            List of capability strings (e.g., ["syntax_analysis", "security_scan"])
        """
        pass

    @abstractmethod
    def validate_confidence(self, result: AnalysisResult) -> bool:
        """
        Validate that confidence score accurately reflects analysis quality.

        Args:
            result: Analysis result to validate

        Returns:
            True if confidence score is accurate, False otherwise
        """
        pass

    def supports_capability(self, capability: str) -> bool:
        """Check if agent supports a specific capability"""
        return capability in self.get_capabilities()

    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent metadata and information"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.get_capabilities(),
            "type": self.__class__.__name__,
        }


class RecoveryEngine(ABC):
    """
    Abstract base class for recovery engines that detect and fix delusions.

    Recovery engines provide systematic fix generation and application
    for detected code delusions and issues.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

    @abstractmethod
    async def detect_delusions(
        self, code: str, context: Optional[AnalysisContext] = None
    ) -> List[Delusion]:
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
    async def validate_fix(
        self, original: str, fixed: str, delusion: Delusion
    ) -> ValidationResult:
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


class ValidationFramework(ABC):
    """
    Abstract base class for validation frameworks.

    Validation frameworks provide systematic validation and confidence
    scoring across multiple dimensions of code quality.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

    @abstractmethod
    async def multi_dimensional_test(
        self, target: str, context: Optional[AnalysisContext] = None
    ) -> MultiDimensionalResult:
        """
        Perform multi-dimensional testing across functionality, performance, security, and integration.

        Args:
            target: Target to validate (file path, directory, etc.)
            context: Optional context for validation configuration

        Returns:
            MultiDimensionalResult with scores across all dimensions
        """
        pass

    @abstractmethod
    def calculate_confidence(self, results: List[AnalysisResult]) -> float:
        """
        Calculate overall confidence score from multiple analysis results.

        Args:
            results: List of analysis results to aggregate

        Returns:
            Overall confidence score between 0.0 and 1.0
        """
        pass

    @abstractmethod
    async def issue_certificate(
        self, target: str, validation_results: List[ValidationResult]
    ) -> ValidationCertificate:
        """
        Issue validation certificate based on validation results.

        Args:
            target: Target that was validated
            validation_results: Results from validation tests

        Returns:
            ValidationCertificate with overall assessment
        """
        pass

    def get_validation_dimensions(self) -> List[str]:
        """Get list of validation dimensions supported"""
        return ["functional", "performance", "security", "integration"]


class ConsensusEngine(ABC):
    """
    Abstract base class for multi-agent consensus engines.

    Consensus engines coordinate multiple expert agents to build
    consensus and resolve conflicts in analysis results.
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

    @abstractmethod
    async def build_consensus(
        self,
        agents: List[GhostbustersExpertAgent],
        context: AnalysisContext,
        confidence_threshold: float = 0.8,
    ) -> ConsensusResult:
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
    async def resolve_conflicts(
        self, conflicting_results: List[AnalysisResult]
    ) -> AnalysisResult:
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
        return [
            "majority_vote",
            "weighted_confidence",
            "expert_override",
            "human_escalation",
        ]


class AgentCoordinator(ABC):
    """
    Abstract base class for agent coordination and workflow management.

    Agent coordinators manage the lifecycle and orchestration of
    multiple expert agents in complex workflows.
    """

    @abstractmethod
    async def register_agent(self, agent: GhostbustersExpertAgent) -> bool:
        """Register an expert agent with the coordinator"""
        pass

    @abstractmethod
    async def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an expert agent from the coordinator"""
        pass

    @abstractmethod
    async def get_available_agents(
        self, capability: Optional[str] = None
    ) -> List[GhostbustersExpertAgent]:
        """Get list of available agents, optionally filtered by capability"""
        pass

    @abstractmethod
    async def orchestrate_workflow(
        self, context: AnalysisContext, required_capabilities: List[str]
    ) -> ConsensusResult:
        """Orchestrate a complete analysis workflow with multiple agents"""
        pass


class ExtensionInterface(ABC):
    """
    Interface for extending Ghostbusters with custom agents and engines.

    Enables dependent specs to add domain-specific capabilities
    while maintaining consistency with the core framework.
    """

    @abstractmethod
    def validate_extension(self, extension: Any) -> ValidationResult:
        """Validate that extension meets framework requirements"""
        pass

    @abstractmethod
    def register_extension(self, extension: Any) -> bool:
        """Register extension with the framework"""
        pass

    @abstractmethod
    def get_extension_info(self, extension_name: str) -> Dict[str, Any]:
        """Get information about registered extension"""
        pass


# Custom Exceptions
class GhostbustersError(Exception):
    """Base exception for Ghostbusters framework"""

    pass


class AnalysisError(GhostbustersError):
    """Exception raised during analysis operations"""

    pass


class RecoveryError(GhostbustersError):
    """Exception raised during recovery operations"""

    pass


class ConsensusError(GhostbustersError):
    """Exception raised during consensus building"""

    pass


class ValidationError(GhostbustersError):
    """Exception raised during validation operations"""

    pass


class ExtensionError(GhostbustersError):
    """Exception raised during extension operations"""

    pass
