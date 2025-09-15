"""
Ghostbusters API Gateway

Main service interface that provides clean APIs for dependent specs
to access Ghostbusters capabilities without circular dependencies.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..core.models import (
    AnalysisResult,
    AnalysisContext,
    ConsensusResult,
    MultiDimensionalResult,
    ValidationResult,
    ValidationCertificate,
)
from ..core.interfaces import (
    GhostbustersExpertAgent,
    ConsensusEngine,
    ValidationFramework,
    AgentCoordinator,
    AnalysisError,
    ConsensusError,
    ValidationError,
)
from .auth import AuthenticationManager
from .circuit_breaker import CircuitBreaker
from .rate_limiter import RateLimiter


logger = logging.getLogger(__name__)


class GhostbustersAPI:
    """
    Main API gateway for Ghostbusters Framework services.

    Provides clean service interfaces that prevent circular dependencies
    with dependent specs while enabling access to all framework capabilities.
    """

    def __init__(
        self,
        auth_manager: Optional[AuthenticationManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.auth_manager = auth_manager or AuthenticationManager()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()

        # Internal components (will be injected by framework)
        self._agent_coordinator: Optional[AgentCoordinator] = None
        self._consensus_engine: Optional[ConsensusEngine] = None
        self._validation_framework: Optional[ValidationFramework] = None

        # Service registry
        self._registered_agents: Dict[str, GhostbustersExpertAgent] = {}
        self._service_health: Dict[str, bool] = {}

        logger.info("Ghostbusters API Gateway initialized")

    def set_coordinator(self, coordinator: AgentCoordinator) -> None:
        """Set the agent coordinator (dependency injection)"""
        self._agent_coordinator = coordinator
        self._service_health["coordinator"] = True
        logger.info("Agent coordinator registered with API gateway")

    def set_consensus_engine(self, engine: ConsensusEngine) -> None:
        """Set the consensus engine (dependency injection)"""
        self._consensus_engine = engine
        self._service_health["consensus"] = True
        logger.info("Consensus engine registered with API gateway")

    def set_validation_framework(self, framework: ValidationFramework) -> None:
        """Set the validation framework (dependency injection)"""
        self._validation_framework = framework
        self._service_health["validation"] = True
        logger.info("Validation framework registered with API gateway")

    # Analysis Services API

    async def analyze_code(
        self,
        target_path: str,
        analysis_type: str,
        configuration: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Analyze code using appropriate expert agents.

        Args:
            target_path: Path to code to analyze
            analysis_type: Type of analysis (e.g., "security", "quality", "performance")
            configuration: Optional analysis configuration
            auth_token: Optional authentication token

        Returns:
            AnalysisResult with findings and recommendations

        Raises:
            AnalysisError: If analysis fails
        """
        # Authentication check
        if not await self._authenticate(auth_token):
            raise AnalysisError("Authentication failed")

        # Rate limiting check
        if not await self._check_rate_limit("analyze_code"):
            raise AnalysisError("Rate limit exceeded")

        # Circuit breaker check
        if not self.circuit_breaker.can_execute("analyze_code"):
            raise AnalysisError("Service temporarily unavailable")

        try:
            # Create analysis context
            context = AnalysisContext(
                target_path=target_path,
                analysis_type=analysis_type,
                configuration=configuration or {},
            )

            # Get appropriate agents
            if not self._agent_coordinator:
                raise AnalysisError("Agent coordinator not available")

            agents = await self._agent_coordinator.get_available_agents(analysis_type)
            if not agents:
                raise AnalysisError(
                    f"No agents available for analysis type: {analysis_type}"
                )

            # Execute analysis
            if len(agents) == 1:
                # Single agent analysis
                result = await agents[0].analyze(context)
            else:
                # Multi-agent consensus
                if not self._consensus_engine:
                    # Fall back to first available agent
                    result = await agents[0].analyze(context)
                else:
                    consensus_result = await self._consensus_engine.build_consensus(
                        agents, context
                    )
                    result = consensus_result.unified_result or AnalysisResult(
                        agent_name="Consensus", confidence=consensus_result.confidence
                    )

            self.circuit_breaker.record_success("analyze_code")
            logger.info(
                f"Analysis completed for {target_path} with confidence {result.confidence}"
            )
            return result

        except Exception as e:
            self.circuit_breaker.record_failure("analyze_code")
            logger.error(f"Analysis failed for {target_path}: {str(e)}")
            raise AnalysisError(f"Analysis failed: {str(e)}")

    async def get_expert_capabilities(
        self, auth_token: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Get capabilities of all available expert agents.

        Args:
            auth_token: Optional authentication token

        Returns:
            Dictionary mapping agent names to their capabilities
        """
        if not await self._authenticate(auth_token):
            raise AnalysisError("Authentication failed")

        if not self._agent_coordinator:
            return {}

        try:
            agents = await self._agent_coordinator.get_available_agents()
            capabilities = {}

            for agent in agents:
                capabilities[agent.name] = agent.get_capabilities()

            return capabilities

        except Exception as e:
            logger.error(f"Failed to get expert capabilities: {str(e)}")
            raise AnalysisError(f"Failed to get capabilities: {str(e)}")

    # Consensus Services API

    async def build_consensus(
        self,
        target_path: str,
        analysis_type: str,
        confidence_threshold: float = 0.8,
        configuration: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> ConsensusResult:
        """
        Build consensus across multiple expert agents.

        Args:
            target_path: Path to analyze
            analysis_type: Type of analysis
            confidence_threshold: Minimum confidence for consensus
            configuration: Optional configuration
            auth_token: Optional authentication token

        Returns:
            ConsensusResult with unified analysis or conflict information
        """
        if not await self._authenticate(auth_token):
            raise ConsensusError("Authentication failed")

        if not await self._check_rate_limit("build_consensus"):
            raise ConsensusError("Rate limit exceeded")

        if not self.circuit_breaker.can_execute("build_consensus"):
            raise ConsensusError("Service temporarily unavailable")

        try:
            if not self._consensus_engine or not self._agent_coordinator:
                raise ConsensusError("Consensus services not available")

            # Create analysis context
            context = AnalysisContext(
                target_path=target_path,
                analysis_type=analysis_type,
                configuration=configuration or {},
            )

            # Get available agents
            agents = await self._agent_coordinator.get_available_agents(analysis_type)
            if len(agents) < 2:
                raise ConsensusError("At least 2 agents required for consensus")

            # Build consensus
            result = await self._consensus_engine.build_consensus(
                agents, context, confidence_threshold
            )

            self.circuit_breaker.record_success("build_consensus")
            logger.info(
                f"Consensus built for {target_path}: {result.consensus_reached}"
            )
            return result

        except Exception as e:
            self.circuit_breaker.record_failure("build_consensus")
            logger.error(f"Consensus building failed for {target_path}: {str(e)}")
            raise ConsensusError(f"Consensus building failed: {str(e)}")

    # Validation Services API

    async def validate_multi_dimensional(
        self,
        target: str,
        configuration: Optional[Dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> MultiDimensionalResult:
        """
        Perform multi-dimensional validation (functional, performance, security, integration).

        Args:
            target: Target to validate
            configuration: Optional validation configuration
            auth_token: Optional authentication token

        Returns:
            MultiDimensionalResult with scores across all dimensions
        """
        if not await self._authenticate(auth_token):
            raise ValidationError("Authentication failed")

        if not await self._check_rate_limit("validate_multi_dimensional"):
            raise ValidationError("Rate limit exceeded")

        if not self.circuit_breaker.can_execute("validate_multi_dimensional"):
            raise ValidationError("Service temporarily unavailable")

        try:
            if not self._validation_framework:
                raise ValidationError("Validation framework not available")

            # Create analysis context for validation
            context = (
                AnalysisContext(
                    target_path=target,
                    analysis_type="multi_dimensional_validation",
                    configuration=configuration or {},
                )
                if configuration
                else None
            )

            # Perform validation
            result = await self._validation_framework.multi_dimensional_test(
                target, context
            )

            self.circuit_breaker.record_success("validate_multi_dimensional")
            logger.info(f"Multi-dimensional validation completed for {target}")
            return result

        except Exception as e:
            self.circuit_breaker.record_failure("validate_multi_dimensional")
            logger.error(f"Multi-dimensional validation failed for {target}: {str(e)}")
            raise ValidationError(f"Validation failed: {str(e)}")

    async def issue_validation_certificate(
        self,
        target: str,
        validation_results: List[ValidationResult],
        auth_token: Optional[str] = None,
    ) -> ValidationCertificate:
        """
        Issue validation certificate based on validation results.

        Args:
            target: Target that was validated
            validation_results: Results from validation tests
            auth_token: Optional authentication token

        Returns:
            ValidationCertificate with overall assessment
        """
        if not await self._authenticate(auth_token):
            raise ValidationError("Authentication failed")

        try:
            if not self._validation_framework:
                raise ValidationError("Validation framework not available")

            certificate = await self._validation_framework.issue_certificate(
                target, validation_results
            )

            logger.info(f"Validation certificate issued for {target}")
            return certificate

        except Exception as e:
            logger.error(f"Certificate issuance failed for {target}: {str(e)}")
            raise ValidationError(f"Certificate issuance failed: {str(e)}")

    # Health and Status API

    async def get_service_health(
        self, auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get health status of all Ghostbusters services.

        Args:
            auth_token: Optional authentication token

        Returns:
            Dictionary with service health information
        """
        if not await self._authenticate(auth_token):
            return {"error": "Authentication failed"}

        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "services": dict(self._service_health),
            "circuit_breaker_status": self.circuit_breaker.get_status(),
            "rate_limiter_status": self.rate_limiter.get_status(),
            "registered_agents": len(self._registered_agents),
        }

        # Check if any critical services are down
        critical_services = ["coordinator", "consensus", "validation"]
        unhealthy_services = [
            service
            for service in critical_services
            if not self._service_health.get(service, False)
        ]

        if unhealthy_services:
            health_status["overall_status"] = "degraded"
            health_status["unhealthy_services"] = unhealthy_services

        return health_status

    async def get_service_metrics(
        self, auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance metrics for Ghostbusters services.

        Args:
            auth_token: Optional authentication token

        Returns:
            Dictionary with service metrics
        """
        if not await self._authenticate(auth_token):
            return {"error": "Authentication failed"}

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "circuit_breaker_metrics": self.circuit_breaker.get_metrics(),
            "rate_limiter_metrics": self.rate_limiter.get_metrics(),
            "api_version": "1.0.0",
            "uptime": "calculated_uptime_here",  # TODO: Implement uptime tracking
        }

    # Private helper methods

    async def _authenticate(self, token: Optional[str]) -> bool:
        """Authenticate request using auth manager"""
        if not token:
            return True  # Allow unauthenticated access for now
        return await self.auth_manager.validate_token(token)

    async def _check_rate_limit(self, operation: str) -> bool:
        """Check rate limit for operation"""
        return await self.rate_limiter.check_limit(operation)

    def _ensure_service_health(self) -> None:
        """Ensure critical services are healthy"""
        critical_services = ["coordinator", "consensus", "validation"]
        for service in critical_services:
            if not self._service_health.get(service, False):
                logger.warning(f"Critical service {service} is not healthy")


# Service interface functions for dependent specs
# These provide clean APIs without exposing internal implementation


async def analyze_with_ghostbusters(
    target_path: str, analysis_type: str, configuration: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """
    Convenience function for dependent specs to analyze code.

    This function provides a clean interface that prevents circular dependencies
    while enabling access to Ghostbusters analysis capabilities.
    """
    # This would be implemented to use a singleton or injected API instance
    # For now, return a placeholder to prevent import errors
    raise NotImplementedError("API instance not configured")


async def validate_with_ghostbusters(
    target: str, configuration: Optional[Dict[str, Any]] = None
) -> MultiDimensionalResult:
    """
    Convenience function for dependent specs to validate code.

    This function provides a clean interface for multi-dimensional validation
    without exposing Ghostbusters internal implementation.
    """
    # This would be implemented to use a singleton or injected API instance
    raise NotImplementedError("API instance not configured")


async def build_consensus_with_ghostbusters(
    target_path: str, analysis_type: str, confidence_threshold: float = 0.8
) -> ConsensusResult:
    """
    Convenience function for dependent specs to build consensus.

    This function provides a clean interface for multi-agent consensus
    without creating circular dependencies.
    """
    # This would be implemented to use a singleton or injected API instance
    raise NotImplementedError("API instance not configured")
