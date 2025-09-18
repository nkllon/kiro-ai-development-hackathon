"""
RDI Enhanced Test Module

Requirements Traceability:

Enhanced: 2025-09-14T06:30:15.477330
"""






import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src.ghostbusters.api.gateway import GhostbustersAPI
from src.ghostbusters.api.auth import AuthenticationManager
from src.ghostbusters.api.circuit_breaker import CircuitBreaker, CircuitState
from src.ghostbusters.api.rate_limiter import RateLimiter
from src.ghostbusters.core.models import (
    AnalysisResult, AnalysisContext, ValidationResult, ConsensusResult
)
from src.ghostbusters.core.interfaces import (
# from src.multi_instance_orchestration.core.reflective_module import ReflectiveModule

    GhostbustersExpertAgent, ConsensusEngine, ValidationFramework,
    AgentCoordinator, AnalysisError, ConsensusError, ValidationError
)


class MockExpertAgent(GhostbustersExpertAgent, ReflectiveModule):
    """Mock expert agent for testing"""

    def __init__(self, name: str = "MockAgent"):
        self.module_id = self.__class__.__name__
        self.health_status = "healthy"
        self.registry_metadata = {}
        super().__init__(name)
        self._capabilities = ["test_analysis", "mock_capability"]

    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        return AnalysisResult(
            agent_name=self.name,
            confidence=0.9,
            analysis_duration=0.1
        )

    def get_capabilities(self) -> list:
        return self._capabilities

    def validate_confidence(self, result: AnalysisResult) -> bool:
        return 0.0 <= result.confidence <= 1.0


class TestAuthenticationManager(ReflectiveModule):
    """Test authentication manager functionality"""

    @pytest.fixture
    def auth_manager(self):
        return AuthenticationManager(require_auth=True, token_expiry_hours=1)

    @pytest.mark.asyncio
    async def test_generate_and_validate_token(self, auth_manager):
        """Test token generation and validation"""
        client_id = "test_client"
        token = await auth_manager.generate_token(client_id)

        assert token is not None
        assert len(token) > 0

        # Token should be valid
        is_valid = await auth_manager.validate_token(token)
        assert is_valid is True

        # Invalid token should fail
        is_valid = await auth_manager.validate_token("invalid_token")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_token_permissions(self, auth_manager):
        """Test token permission checking"""
        client_id = "test_client"
        permissions = {"read", "write"}
        token = await auth_manager.generate_token(client_id, permissions)

        # Should have granted permissions
        has_read = await auth_manager.check_permission(token, "read")
        assert has_read is True

        has_write = await auth_manager.check_permission(token, "write")
        assert has_write is True

        # Should not have other permissions
        has_admin = await auth_manager.check_permission(token, "admin")
        assert has_admin is False

    @pytest.mark.asyncio
    async def test_token_revocation(self, auth_manager):
        """Test token revocation"""
        client_id = "test_client"
        token = await auth_manager.generate_token(client_id)

        # Token should be valid initially
        is_valid = await auth_manager.validate_token(token)
        assert is_valid is True

        # Revoke token
        revoked = await auth_manager.revoke_token(token)
        assert revoked is True

        # Token should no longer be valid
        is_valid = await auth_manager.validate_token(token)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_token_expiry(self):
        """Test token expiry functionality"""
        # Create auth manager with very short expiry
        auth_manager = AuthenticationManager(
            require_auth=True,
            token_expiry_hours=0.001  # ~3.6 seconds
        )

        client_id = "test_client"
        token = await auth_manager.generate_token(client_id)

        # Token should be valid initially
        is_valid = await auth_manager.validate_token(token)
        assert is_valid is True

        # Wait for expiry (in real test, would mock time)
        # For now, just test the expiry logic exists
        token_info = await auth_manager.get_token_info(token)
        assert token_info is not None
        assert "expires_at" in token_info

    def test_auth_stats(self, auth_manager):
        """Test authentication statistics"""
        stats = auth_manager.get_auth_stats()

        assert "require_auth" in stats
        assert "active_tokens" in stats
        assert "active_clients" in stats
        assert "token_expiry_hours" in stats
        assert "max_tokens_per_client" in stats


class TestCircuitBreaker(ReflectiveModule):
    """Test circuit breaker functionality"""

    @pytest.fixture
    def circuit_breaker(self):
        return CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1,  # 1 second for testing
            success_threshold=2
        )

    def test_initial_state(self, circuit_breaker):
        """Test circuit breaker initial state"""
        operation = "test_operation"

        # Should allow execution initially
        can_execute = circuit_breaker.can_execute(operation)
        assert can_execute is True

        # Should be in closed state after first use
        status = circuit_breaker.get_status()
        assert operation in status["circuits"]  # Circuit created on first use
        assert status["circuits"][operation]["state"] == "closed"

    def test_failure_threshold(self, circuit_breaker):
        """Test circuit opening on failure threshold"""
        operation = "test_operation"

        # Record failures up to threshold
        for i in range(3):
            circuit_breaker.record_failure(operation)
            if i < 2:  # Before threshold
                assert circuit_breaker.can_execute(operation) is True

        # Should be open after threshold
        assert circuit_breaker.can_execute(operation) is False

        status = circuit_breaker.get_status()
        assert status["circuits"][operation]["state"] == "open"

    def test_success_recovery(self, circuit_breaker):
        """Test circuit recovery on success"""
        operation = "test_operation"

        # Open the circuit
        for _ in range(3):
            circuit_breaker.record_failure(operation)

        assert circuit_breaker.can_execute(operation) is False

        # Manually transition to half-open for testing
        circuit_breaker._transition_to_half_open(operation)
        assert circuit_breaker.can_execute(operation) is True

        # Record successes to close circuit
        for _ in range(2):
            circuit_breaker.record_success(operation)

        status = circuit_breaker.get_status()
        assert status["circuits"][operation]["state"] == "closed"

    def test_timeout_handling(self, circuit_breaker):
        """Test timeout handling"""
        operation = "test_operation"

        circuit_breaker.record_timeout(operation)

        status = circuit_breaker.get_status()
        circuit = status["circuits"][operation]
        assert circuit["timeout_count"] == 1
        assert circuit["failure_count"] == 1  # Timeout counts as failure

    def test_circuit_reset(self, circuit_breaker):
        """Test manual circuit reset"""
        operation = "test_operation"

        # Open the circuit
        for _ in range(3):
            circuit_breaker.record_failure(operation)

        assert circuit_breaker.can_execute(operation) is False

        # Reset circuit
        circuit_breaker.reset_circuit(operation)
        assert circuit_breaker.can_execute(operation) is True

        status = circuit_breaker.get_status()
        assert status["circuits"][operation]["state"] == "closed"

    def test_metrics(self, circuit_breaker):
        """Test circuit breaker metrics"""
        operation1 = "test_operation1"
        operation2 = "test_operation2"

        # Generate some activity
        circuit_breaker.record_success(operation1)
        circuit_breaker.record_failure(operation2)
        circuit_breaker.record_timeout(operation1)

        metrics = circuit_breaker.get_metrics()

        assert "total_circuits" in metrics
        assert "total_failures" in metrics
        assert "total_successes" in metrics
        assert "total_timeouts" in metrics
        assert metrics["total_circuits"] == 2
        assert metrics["total_successes"] == 1
        assert metrics["total_failures"] == 2  # failure + timeout
        assert metrics["total_timeouts"] == 1


class TestRateLimiter(ReflectiveModule):
    """Test rate limiter functionality"""

    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter(
            default_requests_per_minute=60,
            default_burst_size=10
        )

    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self, rate_limiter):
        """Test basic rate limiting functionality"""
        operation = "test_operation"
        client_id = "test_client"

        # Should allow requests initially
        allowed = await rate_limiter.check_limit(operation, client_id)
        assert allowed is True

        # Check remaining tokens
        remaining = await rate_limiter.get_remaining_tokens(operation, client_id)
        assert remaining == 9  # Started with 10, used 1

    @pytest.mark.asyncio
    async def test_burst_limit(self, rate_limiter):
        """Test burst limit enforcement"""
        operation = "test_operation"
        client_id = "test_client"

        # Use up all burst tokens
        for i in range(10):
            allowed = await rate_limiter.check_limit(operation, client_id)
            assert allowed is True

        # Next request should be rate limited
        allowed = await rate_limiter.check_limit(operation, client_id)
        assert allowed is False

        remaining = await rate_limiter.get_remaining_tokens(operation, client_id)
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_operation_specific_limits(self, rate_limiter):
        """Test operation-specific rate limits"""
        operation = "limited_operation"
        client_id = "test_client"

        # Set custom limit for operation
        rate_limiter.set_operation_limit(operation, requests_per_minute=30, burst_size=5)

        # Should allow up to burst size
        for i in range(5):
            allowed = await rate_limiter.check_limit(operation, client_id)
            assert allowed is True

        # Should be rate limited after burst
        allowed = await rate_limiter.check_limit(operation, client_id)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_client_isolation(self, rate_limiter):
        """Test that clients are isolated from each other"""
        operation = "test_operation"
        client1 = "client1"
        client2 = "client2"

        # Use up client1's tokens
        for _ in range(10):
            allowed = await rate_limiter.check_limit(operation, client1)
            assert allowed is True

        # Client1 should be rate limited
        allowed = await rate_limiter.check_limit(operation, client1)
        assert allowed is False

        # Client2 should still have tokens
        allowed = await rate_limiter.check_limit(operation, client2)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_reset_time(self, rate_limiter):
        """Test reset time calculation"""
        operation = "test_operation"
        client_id = "test_client"

        # Use some tokens
        for _ in range(5):
            await rate_limiter.check_limit(operation, client_id)

        reset_time = await rate_limiter.get_reset_time(operation, client_id)
        assert isinstance(reset_time, datetime)
        assert reset_time >= datetime.utcnow()

    def test_client_stats(self, rate_limiter):
        """Test client statistics"""
        # Test with non-existent client
        stats = rate_limiter.get_client_stats("nonexistent")
        assert "error" in stats

        # Test status and metrics
        status = rate_limiter.get_status()
        assert "active_clients" in status
        assert "total_buckets" in status

        metrics = rate_limiter.get_metrics()
        assert "total_requests_recorded" in metrics
        assert "rejection_rate" in metrics


class TestGhostbustersAPI(ReflectiveModule):
    """Test main API gateway functionality"""

    @pytest.fixture
    def api_gateway(self):
        auth_manager = AuthenticationManager(require_auth=False)  # Disable auth for testing
        rate_limiter = RateLimiter()
        circuit_breaker = CircuitBreaker()

        return GhostbustersAPI(
            auth_manager=auth_manager,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker
        )

    @pytest.fixture
    def mock_coordinator(self):
        coordinator = Mock(spec=AgentCoordinator)
        coordinator.get_available_agents = AsyncMock()
        return coordinator

    @pytest.fixture
    def mock_consensus_engine(self):
        engine = Mock(spec=ConsensusEngine)
        engine.build_consensus = AsyncMock()
        return engine

    @pytest.fixture
    def mock_validation_framework(self):
        framework = Mock(spec=ValidationFramework)
        framework.multi_dimensional_test = AsyncMock()
        framework.issue_certificate = AsyncMock()
        return framework

    @pytest.mark.asyncio
    async def test_analyze_code_single_agent(self, api_gateway, mock_coordinator):
        """Test code analysis with single agent"""
        # Setup mocks
        mock_agent = MockExpertAgent("TestAgent")
        mock_coordinator.get_available_agents.return_value = [mock_agent]
        api_gateway.set_coordinator(mock_coordinator)

        # Test analysis
        result = await api_gateway.analyze_code(
            target_path="test.py",
            analysis_type="test_analysis"
        )

        assert isinstance(result, AnalysisResult)
        assert result.agent_name == "TestAgent"
        assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_analyze_code_no_agents(self, api_gateway, mock_coordinator):
        """Test code analysis with no available agents"""
        # Setup mocks
        mock_coordinator.get_available_agents.return_value = []
        api_gateway.set_coordinator(mock_coordinator)

        # Should raise AnalysisError
        with pytest.raises(AnalysisError, match="No agents available"):
            await api_gateway.analyze_code(
                target_path="test.py",
                analysis_type="test_analysis"
            )

    @pytest.mark.asyncio
    async def test_analyze_code_no_coordinator(self, api_gateway):
        """Test code analysis without coordinator"""
        # Should raise AnalysisError
        with pytest.raises(AnalysisError, match="Agent coordinator not available"):
            await api_gateway.analyze_code(
                target_path="test.py",
                analysis_type="test_analysis"
            )

    @pytest.mark.asyncio
    async def test_get_expert_capabilities(self, api_gateway, mock_coordinator):
        """Test getting expert capabilities"""
        # Setup mocks
        mock_agent = MockExpertAgent("TestAgent")
        mock_coordinator.get_available_agents.return_value = [mock_agent]
        api_gateway.set_coordinator(mock_coordinator)

        # Test capabilities
        capabilities = await api_gateway.get_expert_capabilities()

        assert "TestAgent" in capabilities
        assert capabilities["TestAgent"] == ["test_analysis", "mock_capability"]

    @pytest.mark.asyncio
    async def test_build_consensus(self, api_gateway, mock_coordinator, mock_consensus_engine):
        """Test consensus building"""
        # Setup mocks
        mock_agents = [MockExpertAgent("Agent1"), MockExpertAgent("Agent2")]
        mock_coordinator.get_available_agents.return_value = mock_agents

        # Create a unified result for consensus
        unified_result = AnalysisResult(
            agent_name="Consensus",
            confidence=0.85
        )

        mock_consensus_result = ConsensusResult(
            consensus_reached=True,
            confidence=0.85,
            unified_result=unified_result,
            participating_agents=["Agent1", "Agent2"],
            resolution_method="majority_vote"
        )
        mock_consensus_engine.build_consensus.return_value = mock_consensus_result

        api_gateway.set_coordinator(mock_coordinator)
        api_gateway.set_consensus_engine(mock_consensus_engine)

        # Test consensus
        result = await api_gateway.build_consensus(
            target_path="test.py",
            analysis_type="test_analysis"
        )

        assert isinstance(result, ConsensusResult)
        assert result.consensus_reached is True
        assert result.confidence == 0.85

    @pytest.mark.asyncio
    async def test_build_consensus_insufficient_agents(self, api_gateway, mock_coordinator, mock_consensus_engine):
        """Test consensus building with insufficient agents"""
        # Setup mocks - only one agent
        mock_coordinator.get_available_agents.return_value = [MockExpertAgent("Agent1")]
        api_gateway.set_coordinator(mock_coordinator)
        api_gateway.set_consensus_engine(mock_consensus_engine)  # Need consensus engine too

        # Should raise ConsensusError
        with pytest.raises(ConsensusError, match="At least 2 agents required"):
            await api_gateway.build_consensus(
                target_path="test.py",
                analysis_type="test_analysis"
            )

    @pytest.mark.asyncio
    async def test_service_health(self, api_gateway):
        """Test service health reporting"""
        health = await api_gateway.get_service_health()

        assert "timestamp" in health
        assert "overall_status" in health
        assert "services" in health
        assert "circuit_breaker_status" in health
        assert "rate_limiter_status" in health

    @pytest.mark.asyncio
    async def test_service_metrics(self, api_gateway):
        """Test service metrics reporting"""
        metrics = await api_gateway.get_service_metrics()

        assert "timestamp" in metrics
        assert "circuit_breaker_metrics" in metrics
        assert "rate_limiter_metrics" in metrics

    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

    def register_module(self, registry):
        """Register module with registry."""
        if hasattr(registry, 'register'):
            registry.register(self.get_interface_metadata())

    def health_check(self):
        """Perform health check."""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'module_id': getattr(self, 'module_id', self.__class__.__name__)
        }

    def get_health_status(self):
        """Get current health status."""
        return self.health_check()

        assert "api_version" in metrics