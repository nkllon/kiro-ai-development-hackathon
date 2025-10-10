"""
Integration tests for Security Manager

Tests the complete integration of security, permissions, and Observatory context
with brownfield safety features.
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityManager, PermissionLevel, ResourceType, DataSensitivity
)
from src.beast_mode.observatory.ai_consultation.observatory_context_provider import (
    ObservatoryContextProvider
)
from src.beast_mode.observatory.ai_consultation.models import ObservatoryContext
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag


class TestSecurityIntegration:
    """Integration tests for complete security system"""
    
    @pytest.fixture
    async def integrated_security_system(self):
        """Set up integrated security system"""
        # Create components
        security_mgr = SecurityManager(
            jwt_secret="test_secret_for_integration",
            session_timeout=timedelta(hours=2),
            max_sessions_per_user=5,
            audit_log_enabled=True
        )
        
        context_provider = ObservatoryContextProvider(
            cache_ttl=300,
            max_metrics=50,
            max_alerts=20,
            max_context_tokens=2000
        )
        
        # Enable feature flags
        flags_to_enable = [
            FeatureFlag.OBSERVATORY_CONTEXT,
            FeatureFlag.METRICS_ACCESS,
            FeatureFlag.ALERTS_ACCESS,
            FeatureFlag.DOCTOR_STATUS_MANAGEMENT
        ]
        
        for flag in flags_to_enable:
            await feature_flags.set_flag(flag.value, True)
        
        # Initialize components
        await security_mgr.initialize()
        await context_provider.initialize()
        
        yield {
            'security_manager': security_mgr,
            'context_provider': context_provider
        }
        
        # Cleanup
        await security_mgr.cleanup()
        await context_provider.cleanup()
    
    @pytest.mark.asyncio
    async def test_end_to_end_authentication_and_context(self, integrated_security_system):
        """Test complete authentication and context retrieval flow"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create user token
        token = await security_mgr.create_user_token("test_user", PermissionLevel.OPERATOR)
        
        # Authenticate user
        security_context = await security_mgr.authenticate_user(token, source_ip="127.0.0.1")
        
        assert security_context is not None
        assert security_context.user_id == "test_user"
        assert security_context.permissions.permission_level == PermissionLevel.OPERATOR
        
        # Get Observatory context with security
        observatory_context = await context_provider.get_observatory_context(
            user_id="test_user",
            security_context=security_context,
            include_metrics=True,
            include_alerts=True,
            include_status=True
        )
        
        assert isinstance(observatory_context, ObservatoryContext)
        assert observatory_context.system_status
        assert observatory_context.formatted_context
        
        # OPERATOR should have access to metrics and alerts
        assert observatory_context.metrics_summary["count"] > 0
        assert observatory_context.alerts_summary["count"] >= 0
    
    @pytest.mark.asyncio
    async def test_permission_based_context_filtering(self, integrated_security_system):
        """Test context filtering based on different permission levels"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create users with different permission levels
        guest_token = await security_mgr.create_user_token("guest_user", PermissionLevel.GUEST)
        user_token = await security_mgr.create_user_token("regular_user", PermissionLevel.USER)
        admin_token = await security_mgr.create_user_token("admin_user", PermissionLevel.ADMIN)
        
        # Authenticate users
        guest_context = await security_mgr.authenticate_user(guest_token)
        user_context = await security_mgr.authenticate_user(user_token)
        admin_context = await security_mgr.authenticate_user(admin_token)
        
        # Get contexts for each user
        guest_obs_context = await context_provider.get_observatory_context(
            user_id="guest_user",
            security_context=guest_context
        )
        
        user_obs_context = await context_provider.get_observatory_context(
            user_id="regular_user",
            security_context=user_context
        )
        
        admin_obs_context = await context_provider.get_observatory_context(
            user_id="admin_user",
            security_context=admin_context
        )
        
        # Guest should have minimal access
        assert guest_obs_context.metrics_summary["count"] == 0  # No metrics access
        assert guest_obs_context.active_alerts == 0  # No alerts access
        assert guest_obs_context.system_status  # Should have system status
        
        # User should have metrics but limited alerts
        assert user_obs_context.metrics_summary["count"] > 0  # Has metrics access
        assert user_obs_context.active_alerts == 0  # No alerts access for USER level
        
        # Admin should have full access
        assert admin_obs_context.metrics_summary["count"] > 0  # Has metrics access
        assert admin_obs_context.alerts_summary["count"] >= 0  # Has alerts access
    
    @pytest.mark.asyncio
    async def test_data_sensitivity_filtering(self, integrated_security_system):
        """Test data filtering based on sensitivity levels"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create users with different sensitivity limits
        public_token = await security_mgr.create_user_token("public_user", PermissionLevel.GUEST)
        internal_token = await security_mgr.create_user_token("internal_user", PermissionLevel.USER)
        
        public_context = await security_mgr.authenticate_user(public_token)
        internal_context = await security_mgr.authenticate_user(internal_token)
        
        # Get contexts
        public_obs_context = await context_provider.get_observatory_context(
            user_id="public_user",
            security_context=public_context
        )
        
        internal_obs_context = await context_provider.get_observatory_context(
            user_id="internal_user",
            security_context=internal_context
        )
        
        # Public user should have more limited formatted context
        assert len(public_obs_context.formatted_context) <= len(internal_obs_context.formatted_context)
        
        # Internal user should have access to more detailed information
        assert internal_obs_context.metrics_summary["count"] >= public_obs_context.metrics_summary["count"]
    
    @pytest.mark.asyncio
    async def test_session_management_integration(self, integrated_security_system):
        """Test session management with context access"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create and authenticate user
        token = await security_mgr.create_user_token("session_user", PermissionLevel.OPERATOR)
        security_context = await security_mgr.authenticate_user(token)
        session_id = security_context.session_id
        
        # Access context with session
        context1 = await context_provider.get_observatory_context(
            user_id="session_user",
            security_context=security_context
        )
        
        assert isinstance(context1, ObservatoryContext)
        
        # Validate session and access context again
        validated_context = await security_mgr.validate_session(session_id)
        assert validated_context is not None
        
        context2 = await context_provider.get_observatory_context(
            user_id="session_user",
            security_context=validated_context
        )
        
        assert isinstance(context2, ObservatoryContext)
        
        # Revoke session
        await security_mgr.revoke_session(session_id)
        
        # Session should no longer be valid
        invalid_context = await security_mgr.validate_session(session_id)
        assert invalid_context is None
    
    @pytest.mark.asyncio
    async def test_audit_logging_integration(self, integrated_security_system):
        """Test audit logging across security and context operations"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Perform various operations that should be audited
        token = await security_mgr.create_user_token("audit_user", PermissionLevel.USER)
        security_context = await security_mgr.authenticate_user(token)
        
        # Access context (should trigger permission checks)
        await context_provider.get_observatory_context(
            user_id="audit_user",
            security_context=security_context
        )
        
        # Check permissions explicitly
        await security_mgr.check_permission(security_context, ResourceType.METRICS)
        await security_mgr.check_permission(security_context, ResourceType.LOGS)  # Should be denied
        
        # Get audit events
        audit_events = await security_mgr.get_audit_events(limit=20)
        
        # Should have multiple audit events
        assert len(audit_events) > 0
        
        # Check for expected event types
        event_types = [event['event_type'] for event in audit_events]
        assert 'token_created' in event_types
        assert 'auth_success' in event_types
        
        # Should have permission denial for logs access
        permission_events = [e for e in audit_events if e['event_type'] == 'permission_denied']
        assert len(permission_events) > 0
    
    @pytest.mark.asyncio
    async def test_observatory_auth_integration(self, integrated_security_system):
        """Test integration with Observatory authentication"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Use Observatory token format
        obs_token = "obs_operator_12345"
        
        # Should authenticate with Observatory format
        security_context = await security_mgr.authenticate_user(obs_token)
        
        assert security_context is not None
        assert security_context.user_id == "operator"
        assert security_context.permissions.permission_level == PermissionLevel.OPERATOR
        
        # Should be able to access context
        observatory_context = await context_provider.get_observatory_context(
            user_id="operator",
            security_context=security_context
        )
        
        assert isinstance(observatory_context, ObservatoryContext)
        assert observatory_context.metrics_summary["count"] > 0  # OPERATOR has metrics access
        assert observatory_context.alerts_summary["count"] >= 0  # OPERATOR has alerts access
    
    @pytest.mark.asyncio
    async def test_concurrent_security_operations(self, integrated_security_system):
        """Test concurrent security operations"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create multiple users concurrently
        async def create_and_authenticate_user(user_id: str, level: PermissionLevel):
            token = await security_mgr.create_user_token(user_id, level)
            security_context = await security_mgr.authenticate_user(token)
            observatory_context = await context_provider.get_observatory_context(
                user_id=user_id,
                security_context=security_context
            )
            return security_context, observatory_context
        
        # Run multiple operations concurrently
        tasks = [
            create_and_authenticate_user("user1", PermissionLevel.USER),
            create_and_authenticate_user("user2", PermissionLevel.OPERATOR),
            create_and_authenticate_user("user3", PermissionLevel.ADMIN),
            create_and_authenticate_user("user4", PermissionLevel.GUEST),
            create_and_authenticate_user("user5", PermissionLevel.USER)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for result in results:
            assert not isinstance(result, Exception)
            security_context, observatory_context = result
            assert isinstance(security_context.permissions.permission_level, PermissionLevel)
            assert isinstance(observatory_context, ObservatoryContext)
        
        # Should have 5 active sessions
        active_sessions = await security_mgr.get_active_sessions()
        assert len(active_sessions) == 5
    
    @pytest.mark.asyncio
    async def test_feature_flag_security_integration(self, integrated_security_system):
        """Test feature flag integration with security"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Create authenticated user
        token = await security_mgr.create_user_token("feature_user", PermissionLevel.OPERATOR)
        security_context = await security_mgr.authenticate_user(token)
        
        # Disable metrics access via feature flag
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, False)
        
        # Should not have metrics access even with OPERATOR permissions
        observatory_context = await context_provider.get_observatory_context(
            user_id="feature_user",
            security_context=security_context
        )
        
        assert observatory_context.metrics_summary["count"] == 0
        
        # Re-enable metrics access
        await feature_flags.set_flag(FeatureFlag.METRICS_ACCESS.value, True)
        
        # Should have metrics access again
        observatory_context = await context_provider.get_observatory_context(
            user_id="feature_user",
            security_context=security_context
        )
        
        assert observatory_context.metrics_summary["count"] > 0
    
    @pytest.mark.asyncio
    async def test_security_health_monitoring(self, integrated_security_system):
        """Test security system health monitoring"""
        security_mgr = integrated_security_system['security_manager']
        context_provider = integrated_security_system['context_provider']
        
        # Perform some operations to generate statistics
        token = await security_mgr.create_user_token("health_user", PermissionLevel.USER)
        security_context = await security_mgr.authenticate_user(token)
        await context_provider.get_observatory_context(
            user_id="health_user",
            security_context=security_context
        )
        
        # Check security manager health
        security_health = await security_mgr.health_check()
        assert security_health.component == "security_manager"
        assert security_health.status in ["healthy", "degraded"]
        assert "active_sessions" in security_health.metadata
        
        # Check context provider health
        context_health = await context_provider.health_check()
        assert context_health.component == "observatory_context_provider"
        assert context_health.status in ["healthy", "degraded"]
        
        # Get statistics
        security_stats = await security_mgr.get_stats()
        context_stats = await context_provider.get_stats()
        
        assert security_stats['auth_requests'] > 0
        assert security_stats['active_sessions'] > 0
        assert context_stats['context_requests'] > 0


if __name__ == "__main__":
    pytest.main([__file__])