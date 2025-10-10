"""
Unit tests for ConsultationRouter
Tests intelligent routing decisions, capacity management, and emergency mode handling.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.beast_mode.observatory.ai_consultation.consultation_router import (
    ConsultationRouter, RoutingDecision, RoutingReason, RoutingContext, RoutingResult,
    get_consultation_router, route_consultation_request
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ProcessingMode, ObservatoryContext
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.exceptions import (
    ValidationError, ProcessingError
)


class TestConsultationRouter:
    """Test ConsultationRouter functionality"""
    
    @pytest.fixture
    async def router(self):
        """Create router instance for testing"""
        router = ConsultationRouter(
            max_concurrent_realtime=5,
            max_queue_size=100,
            cost_threshold_realtime=2.0,
            load_threshold=0.7,
            emergency_mode_threshold=0.9
        )
        await router.initialize()
        return router
    
    @pytest.fixture
    def sample_query(self):
        """Create sample consultation query"""
        return ConsultationQuery(
            query_id="test-query-123",
            user_id="test-user",
            query_text="What is the current system status?",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_security_context(self):
        """Create sample security context"""
        return SecurityContext(
            user_id="test-user",
            session_id="test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_observatory_context(self):
        """Create sample observatory context"""
        return ObservatoryContext(
            system_status="healthy",
            active_alerts=2,
            metrics_summary={"count": 150, "healthy": 140, "warning": 8, "critical": 2},
            recent_events=[],
            data_sensitivity="medium"
        )
    
    async def test_router_initialization(self, router):
        """Test router initializes correctly"""
        assert router.max_concurrent_realtime == 5
        assert router.max_queue_size == 100
        assert router._active_realtime_sessions == 0
        assert router._current_queue_size == 0
        assert not router._emergency_mode
        assert router._stats['total_requests'] == 0
    
    async def test_query_validation_success(self, router, sample_query, sample_security_context):
        """Test successful query validation"""
        # Should not raise exception
        await router._validate_query(sample_query, sample_security_context)
    
    async def test_query_validation_empty_text(self, router, sample_security_context):
        """Test validation fails for empty query text"""
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with pytest.raises(ValidationError, match="Query text cannot be empty"):
            await router._validate_query(query, sample_security_context)
    
    async def test_query_validation_too_long(self, router, sample_security_context):
        """Test validation fails for overly long query"""
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="x" * 10001,  # Too long
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with pytest.raises(ValidationError, match="Query text too long"):
            await router._validate_query(query, sample_security_context)
    
    async def test_query_validation_harmful_content(self, router, sample_security_context):
        """Test validation fails for potentially harmful content"""
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="DROP TABLE users; --",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        with pytest.raises(ValidationError, match="potentially harmful content"):
            await router._validate_query(query, sample_security_context)
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_observatory_context')
    async def test_build_routing_context(
        self, 
        mock_get_context, 
        mock_get_status,
        router, 
        sample_query, 
        sample_security_context,
        sample_observatory_context
    ):
        """Test building routing context"""
        # Mock doctor status
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_status.reason.value = "available"
        mock_status.cost_budget_remaining = 100.0
        mock_status.active_sessions = 2
        mock_status.queue_length = 5
        mock_get_status.return_value = mock_status
        
        # Mock observatory context
        mock_get_context.return_value = sample_observatory_context
        
        context = await router._build_routing_context(
            sample_query, sample_security_context, {"preferred_mode": "realtime"}
        )
        
        assert context.query == sample_query
        assert context.security_context == sample_security_context
        assert context.observatory_context == sample_observatory_context
        assert context.doctor_status['is_available'] is True
        assert context.doctor_status['active_sessions'] == 2
        assert "preferred_mode" in router._user_preferences["test-user"]
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_routing_decision_urgent_priority(self, mock_flags, router, sample_query):
        """Test routing decision for urgent priority queries"""
        # Enable features
        mock_flags.is_enabled.return_value = True
        
        # Create context with available doctor
        context = RoutingContext(
            query=ConsultationQuery(
                query_id="urgent-test",
                user_id="test-user",
                query_text="URGENT: System is down!",
                priority=QueryPriority.URGENT,
                timestamp=datetime.utcnow()
            ),
            security_context=None,
            observatory_context=None,
            doctor_status={'is_available': True, 'cost_budget_remaining': 50.0},
            system_load={'cpu_percent': 30, 'memory_percent': 40, 'active_connections': 2, 'response_time_avg': 0.5},
            routing_timestamp=datetime.utcnow()
        )
        
        result = await router._make_routing_decision(context)
        
        assert result.decision == RoutingDecision.REAL_TIME
        assert result.reason == RoutingReason.DOCTOR_AVAILABLE
        assert result.processing_mode == ProcessingMode.REAL_TIME
        assert result.metadata['priority'] == 'urgent'
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_routing_decision_system_overloaded(self, mock_flags, router, sample_query):
        """Test routing decision when system is overloaded"""
        # Enable features
        mock_flags.is_enabled.return_value = True
        
        # Create context with high system load
        context = RoutingContext(
            query=sample_query,
            security_context=None,
            observatory_context=None,
            doctor_status={'is_available': True, 'cost_budget_remaining': 50.0},
            system_load={'cpu_percent': 95, 'memory_percent': 90, 'active_connections': 20, 'response_time_avg': 8.0},
            routing_timestamp=datetime.utcnow()
        )
        
        result = await router._make_routing_decision(context)
        
        # Should route to queue due to system overload
        assert result.decision == RoutingDecision.QUEUE
        assert result.reason == RoutingReason.SYSTEM_OVERLOADED
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_routing_decision_emergency_mode(self, mock_flags, router, sample_query):
        """Test routing decision in emergency mode"""
        # Enable features
        mock_flags.is_enabled.return_value = True
        
        # Force emergency mode
        router._emergency_mode = True
        
        context = RoutingContext(
            query=sample_query,
            security_context=None,
            observatory_context=None,
            doctor_status={'is_available': True},
            system_load={'cpu_percent': 50, 'memory_percent': 50, 'active_connections': 3, 'response_time_avg': 1.0},
            routing_timestamp=datetime.utcnow()
        )
        
        result = await router._make_routing_decision(context)
        
        assert result.decision == RoutingDecision.REJECT
        assert result.reason == RoutingReason.EMERGENCY_MODE
        assert result.metadata['emergency_mode'] is True
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_routing_decision_features_disabled(self, mock_flags, router, sample_query):
        """Test routing decision when features are disabled"""
        # Disable all features
        mock_flags.is_enabled.return_value = False
        
        context = RoutingContext(
            query=sample_query,
            security_context=None,
            observatory_context=None,
            doctor_status={'is_available': True},
            system_load={'cpu_percent': 30, 'memory_percent': 40, 'active_connections': 2, 'response_time_avg': 0.5},
            routing_timestamp=datetime.utcnow()
        )
        
        result = await router._make_routing_decision(context)
        
        assert result.decision == RoutingDecision.REJECT
        assert result.reason == RoutingReason.FEATURE_DISABLED
    
    async def test_system_overload_detection(self, router):
        """Test system overload detection"""
        # Normal load
        context = RoutingContext(
            query=MagicMock(),
            security_context=None,
            observatory_context=None,
            doctor_status=None,
            system_load={'cpu_percent': 50, 'memory_percent': 60, 'active_connections': 3, 'response_time_avg': 1.0},
            routing_timestamp=datetime.utcnow()
        )
        
        overloaded = await router._is_system_overloaded(context)
        assert not overloaded
        
        # High CPU load
        context.system_load['cpu_percent'] = 85
        overloaded = await router._is_system_overloaded(context)
        assert overloaded
        
        # High memory load
        context.system_load = {'cpu_percent': 50, 'memory_percent': 85, 'active_connections': 3, 'response_time_avg': 1.0}
        overloaded = await router._is_system_overloaded(context)
        assert overloaded
        
        # High response time
        context.system_load = {'cpu_percent': 50, 'memory_percent': 60, 'active_connections': 3, 'response_time_avg': 6.0}
        overloaded = await router._is_system_overloaded(context)
        assert overloaded
    
    async def test_cost_estimation_realtime(self, router):
        """Test real-time cost estimation"""
        context = RoutingContext(
            query=ConsultationQuery(
                query_id="test",
                user_id="test-user",
                query_text="Short query",
                priority=QueryPriority.NORMAL,
                timestamp=datetime.utcnow()
            ),
            security_context=None,
            observatory_context=None,
            doctor_status=None,
            system_load={},
            routing_timestamp=datetime.utcnow()
        )
        
        cost = await router._estimate_realtime_cost(context)
        assert isinstance(cost, float)
        assert cost > 0
        
        # Test with high priority
        context.query.priority = QueryPriority.URGENT
        urgent_cost = await router._estimate_realtime_cost(context)
        assert urgent_cost > cost  # Should be more expensive
    
    async def test_cost_estimation_queue(self, router):
        """Test queue cost estimation"""
        context = RoutingContext(
            query=ConsultationQuery(
                query_id="test",
                user_id="test-user",
                query_text="Test query",
                priority=QueryPriority.NORMAL,
                timestamp=datetime.utcnow()
            ),
            security_context=None,
            observatory_context=None,
            doctor_status=None,
            system_load={},
            routing_timestamp=datetime.utcnow()
        )
        
        queue_cost = await router._estimate_queue_cost(context)
        realtime_cost = await router._estimate_realtime_cost(context)
        
        assert isinstance(queue_cost, float)
        assert queue_cost > 0
        assert queue_cost < realtime_cost  # Queue should be cheaper
    
    async def test_wait_time_estimation(self, router):
        """Test queue wait time estimation"""
        # Empty queue
        router._current_queue_size = 0
        wait_time = await router._estimate_queue_wait_time(QueryPriority.NORMAL)
        assert wait_time >= timedelta(minutes=5)  # Minimum wait time
        
        # Queue with items
        router._current_queue_size = 10
        wait_time = await router._estimate_queue_wait_time(QueryPriority.NORMAL)
        assert wait_time > timedelta(minutes=5)
        
        # Urgent priority should have shorter wait
        urgent_wait = await router._estimate_queue_wait_time(QueryPriority.URGENT)
        normal_wait = await router._estimate_queue_wait_time(QueryPriority.NORMAL)
        assert urgent_wait < normal_wait
    
    async def test_session_management(self, router):
        """Test real-time session management"""
        # Register sessions
        assert await router.register_realtime_session("session1")
        assert await router.register_realtime_session("session2")
        assert router._active_realtime_sessions == 2
        
        # Unregister session
        assert await router.unregister_realtime_session("session1")
        assert router._active_realtime_sessions == 1
        
        # Test capacity limit
        for i in range(10):  # Try to exceed capacity
            await router.register_realtime_session(f"session{i}")
        
        assert router._active_realtime_sessions <= router.max_concurrent_realtime
    
    async def test_capacity_updates(self, router):
        """Test updating system capacity"""
        # Valid updates
        assert await router.update_capacity(max_concurrent_realtime=10)
        assert router.max_concurrent_realtime == 10
        
        assert await router.update_capacity(max_queue_size=500)
        assert router.max_queue_size == 500
        
        # Invalid updates
        assert not await router.update_capacity(max_concurrent_realtime=0)  # Too low
        assert not await router.update_capacity(max_concurrent_realtime=200)  # Too high
        assert not await router.update_capacity(max_queue_size=5)  # Too low
        assert not await router.update_capacity(max_queue_size=20000)  # Too high
    
    async def test_emergency_mode_management(self, router):
        """Test emergency mode management"""
        assert not router._emergency_mode
        
        # Force enable emergency mode
        assert await router.force_emergency_mode(True)
        assert router._emergency_mode
        
        # Force disable emergency mode
        assert await router.force_emergency_mode(False)
        assert not router._emergency_mode
    
    async def test_health_status(self, router):
        """Test health status reporting"""
        health = await router.get_health_status()
        
        assert health.component == "consultation_router"
        assert health.status in ["healthy", "degraded", "critical", "unhealthy"]
        assert isinstance(health.response_time, (int, float))
        assert health.last_check is not None
        assert 'active_sessions' in health.metadata
        assert 'total_requests' in health.metadata
    
    async def test_routing_stats(self, router):
        """Test routing statistics"""
        stats = await router.get_routing_stats()
        
        assert 'routing_stats' in stats
        assert 'system_state' in stats
        assert 'system_load' in stats
        assert 'capacity' in stats
        assert 'thresholds' in stats
        
        # Check required fields
        assert 'total_requests' in stats['routing_stats']
        assert 'active_realtime_sessions' in stats['system_state']
        assert 'max_concurrent_realtime' in stats['capacity']
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_observatory_context')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_full_routing_flow(
        self, 
        mock_flags, 
        mock_get_context, 
        mock_get_status,
        router, 
        sample_query, 
        sample_security_context
    ):
        """Test complete routing flow"""
        # Setup mocks
        mock_flags.is_enabled.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_status.reason.value = "available"
        mock_status.cost_budget_remaining = 100.0
        mock_status.active_sessions = 1
        mock_status.queue_length = 2
        mock_get_status.return_value = mock_status
        
        mock_get_context.return_value = None  # No observatory context
        
        # Route consultation
        result = await router.route_consultation(
            sample_query, 
            sample_security_context,
            {"preferred_mode": "realtime"}
        )
        
        assert isinstance(result, RoutingResult)
        assert result.decision in [RoutingDecision.REAL_TIME, RoutingDecision.QUEUE]
        assert result.reason is not None
        assert result.cost_estimate is not None
        
        # Check stats updated
        assert router._stats['total_requests'] == 1
        if result.decision == RoutingDecision.REAL_TIME:
            assert router._stats['realtime_routed'] == 1
        else:
            assert router._stats['queue_routed'] == 1


class TestGlobalRouterFunctions:
    """Test global router functions"""
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router._consultation_router', None)
    async def test_get_consultation_router(self):
        """Test getting global router instance"""
        router1 = await get_consultation_router()
        router2 = await get_consultation_router()
        
        assert router1 is router2  # Should be singleton
        assert isinstance(router1, ConsultationRouter)
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_consultation_router')
    async def test_route_consultation_request(self, mock_get_router):
        """Test convenience routing function"""
        # Mock router
        mock_router = AsyncMock()
        mock_result = RoutingResult(
            decision=RoutingDecision.REAL_TIME,
            reason=RoutingReason.DOCTOR_AVAILABLE,
            processing_mode=ProcessingMode.REAL_TIME,
            estimated_wait_time=timedelta(seconds=30),
            cost_estimate=0.25,
            metadata={}
        )
        mock_router.route_consultation.return_value = mock_result
        mock_get_router.return_value = mock_router
        
        # Create test query
        query = ConsultationQuery(
            query_id="test",
            user_id="test-user",
            query_text="Test query",
            priority=QueryPriority.NORMAL,
            timestamp=datetime.utcnow()
        )
        
        # Route request
        result = await route_consultation_request(query)
        
        assert result == mock_result
        mock_router.route_consultation.assert_called_once_with(query, None, None)


if __name__ == "__main__":
    pytest.main([__file__])