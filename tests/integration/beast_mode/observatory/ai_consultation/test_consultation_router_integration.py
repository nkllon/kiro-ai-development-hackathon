"""
Integration tests for ConsultationRouter
Tests router integration with other system components and real-world scenarios.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.beast_mode.observatory.ai_consultation.consultation_router import (
    ConsultationRouter, RoutingDecision, RoutingReason, get_consultation_router
)
from src.beast_mode.observatory.ai_consultation.models import (
    ConsultationQuery, QueryPriority, ProcessingMode
)
from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityContext, PermissionLevel
)
from src.beast_mode.observatory.ai_consultation.doctor_status_manager import (
    DoctorStatusManager, DoctorStatus, DoctorStatusReason
)
from src.beast_mode.observatory.ai_consultation.feature_flags import FeatureFlag


class TestConsultationRouterIntegration:
    """Integration tests for ConsultationRouter"""
    
    @pytest.fixture
    async def router(self):
        """Create router with realistic configuration"""
        router = ConsultationRouter(
            max_concurrent_realtime=3,
            max_queue_size=50,
            cost_threshold_realtime=1.0,
            load_threshold=0.75,
            emergency_mode_threshold=0.9
        )
        await router.initialize()
        return router
    
    @pytest.fixture
    def security_context(self):
        """Create security context for testing"""
        return SecurityContext(
            user_id="integration-test-user",
            session_id="integration-test-session",
            permission_level=PermissionLevel.USER,
            authenticated=True,
            session_start=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
    
    def create_query(self, priority: QueryPriority = QueryPriority.NORMAL, text: str = None) -> ConsultationQuery:
        """Create test query"""
        return ConsultationQuery(
            query_id=f"integration-test-{datetime.utcnow().timestamp()}",
            user_id="integration-test-user",
            query_text=text or f"Integration test query at {datetime.utcnow()}",
            priority=priority,
            timestamp=datetime.utcnow()
        )
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    async def test_normal_load_routing(self, mock_get_status, mock_flags, router, security_context):
        """Test routing under normal system load"""
        # Setup: Doctor available, features enabled
        mock_flags.is_enabled.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_status.reason = DoctorStatusReason.AVAILABLE
        mock_status.cost_budget_remaining = 50.0
        mock_status.active_sessions = 1
        mock_status.queue_length = 3
        mock_get_status.return_value = mock_status
        
        # Test normal priority query
        query = self.create_query(QueryPriority.NORMAL)
        result = await router.route_consultation(query, security_context)
        
        assert result.decision == RoutingDecision.REAL_TIME
        assert result.reason == RoutingReason.DOCTOR_AVAILABLE
        assert result.processing_mode == ProcessingMode.REAL_TIME
        assert result.cost_estimate > 0
        assert result.estimated_wait_time is not None
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    async def test_high_load_routing(self, mock_get_status, mock_flags, router, security_context):
        """Test routing under high system load"""
        # Setup: Doctor available but system overloaded
        mock_flags.is_enabled.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_status.reason = DoctorStatusReason.AVAILABLE
        mock_status.cost_budget_remaining = 50.0
        mock_status.active_sessions = 5
        mock_status.queue_length = 15
        mock_get_status.return_value = mock_status
        
        # Simulate high system load
        router._system_load_metrics = {
            'cpu_percent': 85,
            'memory_percent': 80,
            'active_connections': 20,
            'response_time_avg': 3.5
        }
        
        # Test normal priority query
        query = self.create_query(QueryPriority.NORMAL)
        result = await router.route_consultation(query, security_context)
        
        # Should route to queue due to high load
        assert result.decision == RoutingDecision.QUEUE
        assert result.reason == RoutingReason.SYSTEM_OVERLOADED
        assert result.processing_mode == ProcessingMode.QUEUE
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    async def test_urgent_priority_override(self, mock_get_status, mock_flags, router, security_context):
        """Test urgent priority queries override normal routing rules"""
        # Setup: Doctor available, system under load
        mock_flags.is_enabled.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = True
        mock_status.reason = DoctorStatusReason.AVAILABLE
        mock_status.cost_budget_remaining = 50.0
        mock_status.active_sessions = 3
        mock_status.queue_length = 10
        mock_get_status.return_value = mock_status
        
        # Simulate moderate system load
        router._system_load_metrics = {
            'cpu_percent': 70,
            'memory_percent': 65,
            'active_connections': 8,
            'response_time_avg': 2.0
        }
        
        # Test urgent priority query
        query = self.create_query(QueryPriority.URGENT, "URGENT: Production system down!")
        result = await router.route_consultation(query, security_context)
        
        # Urgent should still get real-time despite load
        assert result.decision == RoutingDecision.REAL_TIME
        assert result.reason == RoutingReason.DOCTOR_AVAILABLE
        assert result.metadata['priority'] == 'urgent'
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status')
    async def test_doctor_unavailable_routing(self, mock_get_status, mock_flags, router, security_context):
        """Test routing when doctor is unavailable"""
        # Setup: Doctor unavailable, features enabled
        mock_flags.is_enabled.return_value = True
        
        mock_status = MagicMock()
        mock_status.is_available = False
        mock_status.reason = DoctorStatusReason.BUDGET_EXHAUSTED
        mock_status.cost_budget_remaining = 0.0
        mock_status.active_sessions = 0
        mock_status.queue_length = 8
        mock_get_status.return_value = mock_status
        
        # Test normal priority query
        query = self.create_query(QueryPriority.NORMAL)
        result = await router.route_consultation(query, security_context)
        
        # Should route to queue when doctor unavailable
        assert result.decision == RoutingDecision.QUEUE
        assert result.reason == RoutingReason.DOCTOR_UNAVAILABLE
        assert result.processing_mode == ProcessingMode.QUEUE
    
    @patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags')
    async def test_feature_flags_integration(self, mock_flags, router, security_context):
        """Test integration with feature flags"""
        # Test with real-time disabled
        def feature_enabled(flag):
            if flag == FeatureFlag.REAL_TIME_CHAT:
                return False
            elif flag == FeatureFlag.QUERY_QUEUE:
                return True
            else:
                return True
        
        mock_flags.is_enabled.side_effect = feature_enabled
        
        query = self.create_query(QueryPriority.NORMAL)
        result = await router.route_consultation(query, security_context)
        
        # Should route to queue when real-time disabled
        assert result.decision == RoutingDecision.QUEUE
        
        # Test with all features disabled
        mock_flags.is_enabled.return_value = False
        
        result = await router.route_consultation(query, security_context)
        assert result.decision == RoutingDecision.REJECT
        assert result.reason == RoutingReason.FEATURE_DISABLED
    
    async def test_capacity_management_integration(self, router, security_context):
        """Test capacity management with concurrent sessions"""
        # Fill up real-time capacity
        session_ids = []
        for i in range(router.max_concurrent_realtime):
            session_id = f"session-{i}"
            success = await router.register_realtime_session(session_id)
            assert success
            session_ids.append(session_id)
        
        # Next session should fail to register
        overflow_session = await router.register_realtime_session("overflow-session")
        assert not overflow_session
        
        # Routing should now prefer queue
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = router.max_concurrent_realtime
                mock_status.queue_length = 5
                mock_get_status.return_value = mock_status
                
                query = self.create_query(QueryPriority.NORMAL)
                result = await router.route_consultation(query, security_context)
                
                # Should route to queue when capacity full
                assert result.decision == RoutingDecision.QUEUE
        
        # Clean up sessions
        for session_id in session_ids:
            await router.unregister_realtime_session(session_id)
    
    async def test_emergency_mode_integration(self, router, security_context):
        """Test emergency mode activation and behavior"""
        # Simulate extreme system load to trigger emergency mode
        router._system_load_metrics = {
            'cpu_percent': 98,
            'memory_percent': 95,
            'active_connections': 50,
            'response_time_avg': 10.0
        }
        
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = 2
                mock_status.queue_length = 5
                mock_get_status.return_value = mock_status
                
                # This should trigger emergency mode
                query = self.create_query(QueryPriority.NORMAL)
                result = await router.route_consultation(query, security_context)
                
                # Should reject due to emergency mode
                assert result.decision == RoutingDecision.REJECT
                assert result.reason == RoutingReason.EMERGENCY_MODE
                assert router._emergency_mode
    
    async def test_user_preferences_integration(self, router, security_context):
        """Test user preference handling"""
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = 1
                mock_status.queue_length = 3
                mock_get_status.return_value = mock_status
                
                # Test user preference for queue
                query = self.create_query(QueryPriority.NORMAL)
                user_preferences = {"preferred_mode": "queue"}
                
                result = await router.route_consultation(
                    query, security_context, user_preferences
                )
                
                # Should respect user preference for queue
                assert result.decision == RoutingDecision.QUEUE
                assert result.reason == RoutingReason.USER_PREFERENCE
                assert result.metadata['user_preference'] == 'queue'
    
    async def test_cost_tracking_integration(self, router, security_context):
        """Test cost estimation and tracking"""
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = 1
                mock_status.queue_length = 3
                mock_get_status.return_value = mock_status
                
                # Test different query sizes for cost estimation
                short_query = self.create_query(QueryPriority.NORMAL, "Short query")
                long_query = self.create_query(
                    QueryPriority.NORMAL, 
                    "This is a much longer query " * 50
                )
                
                short_result = await router.route_consultation(short_query, security_context)
                long_result = await router.route_consultation(long_query, security_context)
                
                # Longer query should cost more
                assert short_result.cost_estimate is not None
                assert long_result.cost_estimate is not None
                assert long_result.cost_estimate > short_result.cost_estimate
    
    async def test_concurrent_routing_requests(self, router, security_context):
        """Test handling multiple concurrent routing requests"""
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = 1
                mock_status.queue_length = 3
                mock_get_status.return_value = mock_status
                
                # Create multiple concurrent requests
                queries = [
                    self.create_query(QueryPriority.NORMAL, f"Concurrent query {i}")
                    for i in range(10)
                ]
                
                # Route all queries concurrently
                tasks = [
                    router.route_consultation(query, security_context)
                    for query in queries
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # All should complete successfully
                assert len(results) == 10
                for result in results:
                    assert not isinstance(result, Exception)
                    assert hasattr(result, 'decision')
                    assert hasattr(result, 'reason')
                
                # Check statistics updated correctly
                assert router._stats['total_requests'] >= 10
    
    async def test_health_monitoring_integration(self, router):
        """Test health monitoring integration"""
        # Get initial health
        health = await router.get_health_status()
        assert health.component == "consultation_router"
        assert health.status == "healthy"
        
        # Simulate degraded state
        router._active_realtime_sessions = router.max_concurrent_realtime
        health = await router.get_health_status()
        assert health.status == "degraded"
        assert "capacity exhausted" in health.error_message.lower()
        
        # Simulate emergency mode
        router._emergency_mode = True
        health = await router.get_health_status()
        assert health.status == "critical"
        assert "emergency mode" in health.error_message.lower()
    
    async def test_statistics_tracking_integration(self, router, security_context):
        """Test statistics tracking across operations"""
        initial_stats = await router.get_routing_stats()
        initial_requests = initial_stats['routing_stats']['total_requests']
        
        with patch('src.beast_mode.observatory.ai_consultation.consultation_router.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.consultation_router.get_doctor_status') as mock_get_status:
                mock_flags.is_enabled.return_value = True
                
                mock_status = MagicMock()
                mock_status.is_available = True
                mock_status.reason = DoctorStatusReason.AVAILABLE
                mock_status.cost_budget_remaining = 50.0
                mock_status.active_sessions = 1
                mock_status.queue_length = 3
                mock_get_status.return_value = mock_status
                
                # Process several requests
                for i in range(5):
                    query = self.create_query(QueryPriority.NORMAL, f"Stats test query {i}")
                    await router.route_consultation(query, security_context)
        
        # Check statistics updated
        final_stats = await router.get_routing_stats()
        final_requests = final_stats['routing_stats']['total_requests']
        
        assert final_requests >= initial_requests + 5
        assert final_stats['routing_stats']['avg_routing_time_ms'] > 0
        
        # Check system state tracking
        assert 'active_realtime_sessions' in final_stats['system_state']
        assert 'current_queue_size' in final_stats['system_state']
        assert 'emergency_mode' in final_stats['system_state']


class TestGlobalRouterIntegration:
    """Test global router instance integration"""
    
    async def test_singleton_behavior(self):
        """Test that global router maintains singleton behavior"""
        router1 = await get_consultation_router()
        router2 = await get_consultation_router()
        
        assert router1 is router2
        
        # Test state persistence across calls
        await router1.register_realtime_session("test-session")
        
        router3 = await get_consultation_router()
        assert router3._active_realtime_sessions == 1
        
        # Clean up
        await router3.unregister_realtime_session("test-session")


if __name__ == "__main__":
    pytest.main([__file__])