"""
Integration tests for Observatory Context Provider

Tests the complete integration of Observatory context extraction with
the AI consultation system and brownfield safety.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from src.beast_mode.observatory.ai_consultation.observatory_context_provider import (
    ObservatoryContextProvider, DataSensitivity
)
from src.beast_mode.observatory.ai_consultation.doctor_status_manager import DoctorStatusManager
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag
from src.beast_mode.observatory.ai_consultation.models import ObservatoryContext
from src.beast_mode.observatory.ai_consultation.exceptions import ContextUnavailableError


class TestObservatoryContextIntegration:
    """Integration tests for Observatory context system"""
    
    @pytest.fixture
    async def integrated_context_system(self):
        """Set up integrated context system"""
        # Create components
        context_provider = ObservatoryContextProvider(
            cache_ttl=60,
            max_metrics=20,
            max_alerts=10,
            max_context_tokens=2000
        )
        
        status_manager = DoctorStatusManager(daily_budget=10.0, monthly_budget=100.0)
        
        # Enable feature flags
        flags_to_enable = [
            FeatureFlag.OBSERVATORY_CONTEXT,
            FeatureFlag.METRICS_ACCESS,
            FeatureFlag.ALERTS_ACCESS,
            FeatureFlag.DOCTOR_STATUS_MANAGEMENT,
            FeatureFlag.COST_TRACKING
        ]
        
        for flag in flags_to_enable:
            await feature_flags.set_flag(flag.value, True)
        
        # Initialize components
        await context_provider.initialize()
        await status_manager.initialize()
        
        yield {
            'context_provider': context_provider,
            'status_manager': status_manager
        }
        
        # Cleanup
        await context_provider.cleanup()
        await status_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_context_extraction_with_system_status(self, integrated_context_system):
        """Test context extraction integrated with system status"""
        context_provider = integrated_context_system['context_provider']
        status_manager = integrated_context_system['status_manager']
        
        # Set system status
        await status_manager.set_status_manual(True, "admin")
        
        # Get Observatory context
        context = await context_provider.get_observatory_context(
            user_id="test_user",
            include_metrics=True,
            include_alerts=True,
            include_status=True
        )
        
        # Verify context structure
        assert isinstance(context, ObservatoryContext)
        assert context.timestamp
        assert context.system_status in ["healthy", "degraded", "unhealthy"]
        assert context.active_alerts >= 0
        assert context.critical_alerts >= 0
        assert isinstance(context.metrics_summary, dict)
        assert isinstance(context.alerts_summary, dict)
        assert context.formatted_context
        
        # Verify formatted context contains useful information
        formatted = context.formatted_context
        assert len(formatted) > 0
        assert "System Status:" in formatted or context.system_status.upper() in formatted
    
    @pytest.mark.asyncio
    async def test_context_with_different_sensitivity_levels(self, integrated_context_system):
        """Test context extraction with different sensitivity levels"""
        context_provider = integrated_context_system['context_provider']
        
        # Get context with public sensitivity
        public_context = await context_provider.get_observatory_context(
            user_id="public_user",
            sensitivity_level=DataSensitivity.PUBLIC
        )
        
        # Get context with internal sensitivity
        internal_context = await context_provider.get_observatory_context(
            user_id="internal_user",
            sensitivity_level=DataSensitivity.INTERNAL
        )
        
        # Internal context should have more or equal information
        assert len(internal_context.formatted_context) >= len(public_context.formatted_context)
        assert internal_context.metrics_summary["count"] >= public_context.metrics_summary["count"]
    
    @pytest.mark.asyncio
    async def test_context_caching_performance(self, integrated_context_system):
        """Test context caching for performance optimization"""
        context_provider = integrated_context_system['context_provider']
        
        # First request should populate cache
        start_time = datetime.utcnow()
        context1 = await context_provider.get_observatory_context("user1")
        first_duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Second request should use cache and be faster
        start_time = datetime.utcnow()
        context2 = await context_provider.get_observatory_context("user1")
        second_duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Cached request should be faster (or at least not significantly slower)
        assert second_duration <= first_duration * 2  # Allow some variance
        
        # Content should be the same
        assert context1.system_status == context2.system_status
        assert context1.active_alerts == context2.active_alerts
    
    @pytest.mark.asyncio
    async def test_context_with_feature_flags_disabled(self, integrated_context_system):
        """Test context behavior with various feature flags disabled"""
        context_provider = integrated_context_system['context_provider']
        
        # Disable metrics access
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, False)
        
        context = await context_provider.get_observatory_context("user1")
        assert context.metrics_summary["count"] == 0
        
        # Re-enable metrics, disable alerts
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, True)
        await feature_flags.set_flag(FeatureFlag.ALERTS_ACCESS.value, False)
        
        context = await context_provider.get_observatory_context("user1")
        assert context.alerts_summary["count"] == 0
        assert context.metrics_summary["count"] > 0
        
        # Disable Observatory context entirely
        await feature_flags.set_flag(FeatureFlag.OBSERVATORY_CONTEXT.value, False)
        
        with pytest.raises(ContextUnavailableError):
            await context_provider.get_observatory_context("user1")
    
    @pytest.mark.asyncio
    async def test_context_with_observatory_unavailable(self, integrated_context_system):
        """Test context behavior when Observatory is unavailable"""
        context_provider = integrated_context_system['context_provider']
        
        # Force Observatory unavailable
        context_provider._observatory_available = False
        
        # Should still provide context but with limited data
        context = await context_provider.get_observatory_context("user1")
        
        assert isinstance(context, ObservatoryContext)
        assert context.metrics_summary["count"] == 0
        assert context.alerts_summary["count"] == 0
        assert "unavailable" in context.formatted_context.lower() or len(context.formatted_context) == 0
    
    @pytest.mark.asyncio
    async def test_context_data_sanitization(self, integrated_context_system):
        """Test data sanitization in context extraction"""
        context_provider = integrated_context_system['context_provider']
        
        # Get context
        context = await context_provider.get_observatory_context("user1")
        
        # Check that formatted context doesn't contain sensitive patterns
        formatted = context.formatted_context.lower()
        
        # Should not contain common sensitive patterns
        sensitive_patterns = ['password', 'secret', 'token', 'key', 'credential']
        for pattern in sensitive_patterns:
            if pattern in formatted:
                # If sensitive pattern exists, it should be redacted
                assert '[redacted]' in formatted.lower()
    
    @pytest.mark.asyncio
    async def test_context_token_optimization(self, integrated_context_system):
        """Test token optimization for LLM consumption"""
        context_provider = integrated_context_system['context_provider']
        
        # Set very low token limit
        context_provider.max_context_tokens = 50
        
        # Get context
        context = await context_provider.get_observatory_context("user1")
        
        # Formatted context should be truncated if necessary
        if len(context.formatted_context) > 200:  # Rough token estimation
            assert "[truncated]" in context.formatted_context
    
    @pytest.mark.asyncio
    async def test_concurrent_context_requests(self, integrated_context_system):
        """Test concurrent context requests"""
        context_provider = integrated_context_system['context_provider']
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = context_provider.get_observatory_context(
                user_id=f"user_{i}",
                sensitivity_level=DataSensitivity.INTERNAL
            )
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for result in results:
            assert isinstance(result, ObservatoryContext)
            assert not isinstance(result, Exception)
    
    @pytest.mark.asyncio
    async def test_context_with_system_health_changes(self, integrated_context_system):
        """Test context updates when system health changes"""
        context_provider = integrated_context_system['context_provider']
        status_manager = integrated_context_system['status_manager']
        
        # Set system healthy
        await status_manager.set_system_health(True)
        
        # Get context
        healthy_context = await context_provider.get_observatory_context("user1")
        
        # Set system unhealthy
        await status_manager.set_system_health(False, "Test error")
        
        # Clear cache to get fresh data
        await context_provider.clear_cache()
        
        # Get context again
        unhealthy_context = await context_provider.get_observatory_context("user1")
        
        # Context should reflect system health changes
        # Note: The context provider simulates data, so we mainly test that it doesn't crash
        assert isinstance(healthy_context, ObservatoryContext)
        assert isinstance(unhealthy_context, ObservatoryContext)
    
    @pytest.mark.asyncio
    async def test_context_metrics_filtering(self, integrated_context_system):
        """Test context metrics filtering by names"""
        context_provider = integrated_context_system['context_provider']
        
        # Get specific metrics
        specific_metrics = await context_provider.get_current_metrics(
            metric_names=["cpu_usage_percent", "memory_usage_bytes"]
        )
        
        # Should only return requested metrics
        metric_names = [m.name for m in specific_metrics]
        for name in metric_names:
            assert name in ["cpu_usage_percent", "memory_usage_bytes"]
    
    @pytest.mark.asyncio
    async def test_context_alerts_filtering(self, integrated_context_system):
        """Test context alerts filtering by severity"""
        context_provider = integrated_context_system['context_provider']
        
        # Get only critical alerts
        critical_alerts = await context_provider.get_current_alerts(
            severity_filter=["critical"]
        )
        
        # Should only return critical alerts
        for alert in critical_alerts:
            assert alert.severity == "critical"
    
    @pytest.mark.asyncio
    async def test_context_provider_health_monitoring(self, integrated_context_system):
        """Test context provider health monitoring"""
        context_provider = integrated_context_system['context_provider']
        
        # Get health status
        health = await context_provider.health_check()
        
        assert health.component == "observatory_context_provider"
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert "observatory_available" in health.metadata
        assert "cache_hit_rate" in health.metadata
        
        # Get statistics
        stats = await context_provider.get_stats()
        
        assert "context_requests" in stats
        assert "observatory_available" in stats
        assert "cache_size" in stats
    
    @pytest.mark.asyncio
    async def test_context_integration_with_cost_tracking(self, integrated_context_system):
        """Test context integration with cost tracking"""
        context_provider = integrated_context_system['context_provider']
        status_manager = integrated_context_system['status_manager']
        
        # Track some costs
        await status_manager.track_cost("session_1", 1000, 2.0)
        
        # Get context
        context = await context_provider.get_observatory_context("user1")
        
        # Context should be available regardless of cost tracking
        assert isinstance(context, ObservatoryContext)
        assert context.formatted_context
        
        # Get budget status from status manager
        budget_status = await status_manager.get_budget_status()
        assert budget_status.daily_spent == 2.0
    
    @pytest.mark.asyncio
    async def test_brownfield_safety_patterns(self, integrated_context_system):
        """Test brownfield safety patterns"""
        context_provider = integrated_context_system['context_provider']
        
        # Verify Observatory endpoints are properly namespaced
        endpoints = context_provider._observatory_endpoints
        
        # Should have detected endpoints
        assert len(endpoints) > 0
        
        # Endpoints should be properly configured
        for endpoint_type, url in endpoints.items():
            assert endpoint_type in ['metrics', 'alerts', 'status']
            assert isinstance(url, str)
            assert len(url) > 0
        
        # Verify circuit breaker integration
        # This is tested by ensuring operations don't fail catastrophically
        context = await context_provider.get_observatory_context("user1")
        assert isinstance(context, ObservatoryContext)


if __name__ == "__main__":
    pytest.main([__file__])