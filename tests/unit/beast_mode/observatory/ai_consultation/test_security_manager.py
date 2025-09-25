"""
Unit tests for Security Manager

Tests authentication, authorization, and data security features.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
import jwt

from src.beast_mode.observatory.ai_consultation.security_manager import (
    SecurityManager,
    PermissionLevel,
    ResourceType,
    UserPermissions,
    SecurityContext,
    DataSensitivity,
    security_manager,
    authenticate_user,
    validate_session,
    check_permission,
    initialize_security_manager,
    cleanup_security_manager
)
from src.beast_mode.observatory.ai_consultation.models import ObservatoryContext
from src.beast_mode.observatory.ai_consultation.exceptions import ValidationError
from src.beast_mode.observatory.ai_consultation.health_checker import ComponentHealth


class TestSecurityManager:
    """Test SecurityManager class"""
    
    @pytest.fixture
    async def security_mgr(self):
        """Create test security manager instance"""
        mgr = SecurityManager(
            jwt_secret="test_secret_key_for_testing_only",
            session_timeout=timedelta(hours=1),
            max_sessions_per_user=3,
            audit_log_enabled=True
        )
        
        yield mgr
        
        # Cleanup
        await mgr.cleanup()
    
    @pytest.mark.asyncio
    async def test_initialization(self, security_mgr):
        """Test security manager initialization"""
        await security_mgr.initialize()
        
        # Should have loaded default permissions
        assert len(security_mgr._permission_cache) > 0
        
        # Should have detected Observatory auth (simulated)
        assert security_mgr._observatory_auth_detected is True
        assert security_mgr._observatory_auth_endpoint is not None
    
    @pytest.mark.asyncio
    async def test_create_user_token(self, security_mgr):
        """Test JWT token creation"""
        await security_mgr.initialize()
        
        # Create token for admin user
        token = await security_mgr.create_user_token(
            "admin_user",
            PermissionLevel.ADMIN,
            expires_in=timedelta(hours=2)
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = jwt.decode(token, "test_secret_key_for_testing_only", algorithms=["HS256"])
        assert payload["user_id"] == "admin_user"
        assert payload["permission_level"] == "admin"
    
    @pytest.mark.asyncio
    async def test_authenticate_with_jwt_token(self, security_mgr):
        """Test authentication with JWT token"""
        await security_mgr.initialize()
        
        # Create a valid token
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        
        # Authenticate with the token
        context = await security_mgr.authenticate_user(token, source_ip="127.0.0.1")
        
        assert context is not None
        assert isinstance(context, SecurityContext)
        assert context.user_id == "test_user"
        assert context.permissions.permission_level == PermissionLevel.USER
        assert context.source_ip == "127.0.0.1"
        assert context.session_id is not None
    
    @pytest.mark.asyncio
    async def test_authenticate_with_observatory_token(self, security_mgr):
        """Test authentication with Observatory token format"""
        await security_mgr.initialize()
        
        # Use Observatory token format
        obs_token = "obs_admin_12345"
        
        context = await security_mgr.authenticate_user(obs_token)
        
        assert context is not None
        assert context.user_id == "admin"
        assert context.permissions.permission_level == PermissionLevel.ADMIN
    
    @pytest.mark.asyncio
    async def test_authenticate_with_demo_token(self, security_mgr):
        """Test authentication with demo token format"""
        await security_mgr.initialize()
        
        # Use demo token format
        demo_token = "user_operator123"
        
        context = await security_mgr.authenticate_user(demo_token)
        
        assert context is not None
        assert context.user_id == "operator123"
        assert context.permissions.permission_level == PermissionLevel.OPERATOR
    
    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, security_mgr):
        """Test authentication with invalid token"""
        await security_mgr.initialize()
        
        # Try invalid token
        context = await security_mgr.authenticate_user("invalid_token")
        
        assert context is None
        assert security_mgr._stats['auth_failures'] > 0
    
    @pytest.mark.asyncio
    async def test_session_validation(self, security_mgr):
        """Test session validation"""
        await security_mgr.initialize()
        
        # Create authenticated user
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        
        assert context is not None
        session_id = context.session_id
        
        # Validate session
        validated_context = await security_mgr.validate_session(session_id)
        assert validated_context is not None
        assert validated_context.user_id == "test_user"
        
        # Try invalid session
        invalid_context = await security_mgr.validate_session("invalid_session")
        assert invalid_context is None
    
    @pytest.mark.asyncio
    async def test_session_expiration(self, security_mgr):
        """Test session expiration"""
        # Set very short session timeout
        security_mgr.session_timeout = timedelta(seconds=1)
        await security_mgr.initialize()
        
        # Create authenticated user
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        session_id = context.session_id
        
        # Wait for session to expire
        await asyncio.sleep(1.1)
        
        # Session should be expired
        expired_context = await security_mgr.validate_session(session_id)
        assert expired_context is None
    
    @pytest.mark.asyncio
    async def test_permission_checking(self, security_mgr):
        """Test permission checking for different resources"""
        await security_mgr.initialize()
        
        # Create user with USER level permissions
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        
        # USER should have access to metrics and system status
        assert await security_mgr.check_permission(context, ResourceType.METRICS) is True
        assert await security_mgr.check_permission(context, ResourceType.SYSTEM_STATUS) is True
        
        # USER should NOT have access to logs or configuration
        assert await security_mgr.check_permission(context, ResourceType.LOGS) is False
        assert await security_mgr.check_permission(context, ResourceType.CONFIGURATION) is False
        
        # Create admin user
        admin_token = await security_mgr.create_user_token("admin_user", PermissionLevel.ADMIN)
        admin_context = await security_mgr.authenticate_user(admin_token)
        
        # ADMIN should have access to all resources
        assert await security_mgr.check_permission(admin_context, ResourceType.METRICS) is True
        assert await security_mgr.check_permission(admin_context, ResourceType.ALERTS) is True
        assert await security_mgr.check_permission(admin_context, ResourceType.LOGS) is True
        assert await security_mgr.check_permission(admin_context, ResourceType.CONFIGURATION) is True
    
    @pytest.mark.asyncio
    async def test_service_permission_checking(self, security_mgr):
        """Test service-specific permission checking"""
        await security_mgr.initialize()
        
        # Create user with limited service access
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        
        # USER should have access to allowed services
        assert await security_mgr.check_permission(context, ResourceType.METRICS, "web") is True
        assert await security_mgr.check_permission(context, ResourceType.METRICS, "api") is True
        
        # USER should NOT have access to restricted services
        assert await security_mgr.check_permission(context, ResourceType.METRICS, "database") is False
    
    @pytest.mark.asyncio
    async def test_observatory_context_filtering(self, security_mgr):
        """Test Observatory context filtering based on permissions"""
        await security_mgr.initialize()
        
        # Create test context
        original_context = ObservatoryContext(
            timestamp=datetime.utcnow(),
            system_status="healthy",
            active_alerts=5,
            critical_alerts=2,
            metrics_summary={"count": 10, "types": ["gauge", "counter"]},
            alerts_summary={"count": 5, "firing": 3, "critical": 2},
            formatted_context="System Status: HEALTHY\nCRITICAL ALERTS:\n- High CPU usage\n- Low disk space"
        )
        
        # Test with GUEST user (limited access)
        guest_token = await security_mgr.create_user_token("guest_user", PermissionLevel.GUEST)
        guest_context = await security_mgr.authenticate_user(guest_token)
        
        filtered_guest = await security_mgr.filter_observatory_context(original_context, guest_context)
        
        # Guest should only see system status
        assert filtered_guest.system_status == "healthy"
        assert filtered_guest.active_alerts == 0  # No alert access
        assert filtered_guest.metrics_summary["count"] == 0  # No metrics access
        
        # Test with OPERATOR user (full monitoring access)
        operator_token = await security_mgr.create_user_token("operator_user", PermissionLevel.OPERATOR)
        operator_context = await security_mgr.authenticate_user(operator_token)
        
        filtered_operator = await security_mgr.filter_observatory_context(original_context, operator_context)
        
        # Operator should see all monitoring data
        assert filtered_operator.system_status == "healthy"
        assert filtered_operator.active_alerts == 5
        assert filtered_operator.critical_alerts == 2
        assert filtered_operator.metrics_summary["count"] == 10
    
    @pytest.mark.asyncio
    async def test_data_sanitization(self, security_mgr):
        """Test data sanitization based on sensitivity levels"""
        # Test text with sensitive information
        sensitive_text = """
        System Status: HEALTHY
        Database IP: 192.168.1.100
        Admin email: admin@company.com
        API key: abc123def456ghi789
        Password: secret123
        """
        
        # Test with INTERNAL sensitivity (should sanitize)
        sanitized = security_mgr._sanitize_sensitive_data(sensitive_text)
        
        assert "[IP_REDACTED]" in sanitized
        assert "[EMAIL_REDACTED]" in sanitized
        assert "[TOKEN_REDACTED]" in sanitized
        assert "[CREDENTIAL_REDACTED]" in sanitized
        assert "192.168.1.100" not in sanitized
        assert "admin@company.com" not in sanitized
    
    @pytest.mark.asyncio
    async def test_session_limits(self, security_mgr):
        """Test session limits per user"""
        security_mgr.max_sessions_per_user = 2
        await security_mgr.initialize()
        
        # Create multiple sessions for same user
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        
        context1 = await security_mgr.authenticate_user(token)
        context2 = await security_mgr.authenticate_user(token)
        context3 = await security_mgr.authenticate_user(token)  # Should remove oldest
        
        # Should only have 2 active sessions
        user_sessions = security_mgr._user_sessions.get("test_user", set())
        assert len(user_sessions) == 2
        
        # First session should be removed
        assert context1.session_id not in security_mgr._active_sessions
        assert context2.session_id in security_mgr._active_sessions
        assert context3.session_id in security_mgr._active_sessions
    
    @pytest.mark.asyncio
    async def test_session_revocation(self, security_mgr):
        """Test session revocation"""
        await security_mgr.initialize()
        
        # Create authenticated user
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        session_id = context.session_id
        
        # Verify session exists
        assert await security_mgr.validate_session(session_id) is not None
        
        # Revoke session
        success = await security_mgr.revoke_session(session_id)
        assert success is True
        
        # Session should no longer exist
        assert await security_mgr.validate_session(session_id) is None
    
    @pytest.mark.asyncio
    async def test_user_session_revocation(self, security_mgr):
        """Test revoking all sessions for a user"""
        await security_mgr.initialize()
        
        # Create multiple sessions for user
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context1 = await security_mgr.authenticate_user(token)
        context2 = await security_mgr.authenticate_user(token)
        
        # Verify sessions exist
        assert len(security_mgr._user_sessions.get("test_user", set())) == 2
        
        # Revoke all user sessions
        revoked_count = await security_mgr.revoke_user_sessions("test_user")
        assert revoked_count == 2
        
        # No sessions should remain
        assert "test_user" not in security_mgr._user_sessions
        assert await security_mgr.validate_session(context1.session_id) is None
        assert await security_mgr.validate_session(context2.session_id) is None
    
    @pytest.mark.asyncio
    async def test_audit_logging(self, security_mgr):
        """Test audit logging functionality"""
        await security_mgr.initialize()
        
        # Perform some auditable actions
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        await security_mgr.check_permission(context, ResourceType.METRICS)
        await security_mgr.revoke_session(context.session_id)
        
        # Get audit events
        events = await security_mgr.get_audit_events(limit=10)
        
        assert len(events) > 0
        
        # Check for expected event types
        event_types = [event['event_type'] for event in events]
        assert 'token_created' in event_types
        assert 'auth_success' in event_types
        assert 'session_revoked' in event_types
    
    @pytest.mark.asyncio
    async def test_audit_event_filtering(self, security_mgr):
        """Test audit event filtering"""
        await security_mgr.initialize()
        
        # Create events for different users
        token1 = await security_mgr.create_user_token("user1", PermissionLevel.USER)
        token2 = await security_mgr.create_user_token("user2", PermissionLevel.USER)
        await security_mgr.authenticate_user(token1)
        await security_mgr.authenticate_user(token2)
        
        # Get events for specific user
        user1_events = await security_mgr.get_audit_events(user_id="user1")
        
        # Should only contain events for user1
        for event in user1_events:
            if 'user_id' in event['details']:
                assert event['details']['user_id'] == "user1"
        
        # Get events by type
        auth_events = await security_mgr.get_audit_events(event_type="auth_success")
        
        # Should only contain auth_success events
        for event in auth_events:
            assert event['event_type'] == "auth_success"
    
    @pytest.mark.asyncio
    async def test_active_sessions_info(self, security_mgr):
        """Test getting active sessions information"""
        await security_mgr.initialize()
        
        # Create some active sessions
        token1 = await security_mgr.create_user_token("user1", PermissionLevel.USER)
        token2 = await security_mgr.create_user_token("user2", PermissionLevel.ADMIN)
        context1 = await security_mgr.authenticate_user(token1)
        context2 = await security_mgr.authenticate_user(token2)
        
        # Get active sessions
        sessions = await security_mgr.get_active_sessions()
        
        assert len(sessions) == 2
        
        # Check session information
        session_users = [s['user_id'] for s in sessions]
        assert "user1" in session_users
        assert "user2" in session_users
        
        # Check session details
        for session in sessions:
            assert 'session_id' in session
            assert 'permission_level' in session
            assert 'created_at' in session
            assert 'expires_at' in session
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, security_mgr):
        """Test statistics tracking"""
        await security_mgr.initialize()
        
        # Perform various operations
        token = await security_mgr.create_user_token("test_user", PermissionLevel.USER)
        context = await security_mgr.authenticate_user(token)
        await security_mgr.check_permission(context, ResourceType.METRICS)
        await security_mgr.check_permission(context, ResourceType.LOGS)  # Should be denied
        
        # Get statistics
        stats = await security_mgr.get_stats()
        
        assert stats['auth_requests'] >= 1
        assert stats['auth_successes'] >= 1
        assert stats['permission_checks'] >= 2
        assert stats['permission_denials'] >= 1
        assert stats['active_sessions'] >= 1
        assert stats['observatory_auth_detected'] is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, security_mgr):
        """Test health check functionality"""
        await security_mgr.initialize()
        
        health = await security_mgr.health_check()
        
        assert isinstance(health, ComponentHealth)
        assert health.component == "security_manager"
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert "active_sessions" in health.metadata
        assert "observatory_auth_detected" in health.metadata
        assert "auth_success_rate" in health.metadata
    
    @pytest.mark.asyncio
    async def test_concurrent_authentication(self, security_mgr):
        """Test concurrent authentication requests"""
        await security_mgr.initialize()
        
        # Create multiple tokens
        tokens = []
        for i in range(5):
            token = await security_mgr.create_user_token(f"user_{i}", PermissionLevel.USER)
            tokens.append(token)
        
        # Authenticate concurrently
        tasks = [security_mgr.authenticate_user(token) for token in tokens]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for result in results:
            assert isinstance(result, SecurityContext)
            assert not isinstance(result, Exception)
        
        # Should have 5 active sessions
        assert len(security_mgr._active_sessions) == 5


class TestGlobalSecurityManager:
    """Test global security manager functions"""
    
    @pytest.mark.asyncio
    async def test_global_functions(self):
        """Test global security manager functions"""
        with patch('src.beast_mode.observatory.ai_consultation.security_manager.security_manager') as mock_mgr:
            mock_context = SecurityContext(
                user_id="test_user",
                session_id="test_session",
                permissions=UserPermissions(
                    user_id="test_user",
                    permission_level=PermissionLevel.USER,
                    allowed_resources={ResourceType.METRICS},
                    allowed_services=set(),
                    data_sensitivity_limit=DataSensitivity.INTERNAL,
                    session_timeout=timedelta(hours=1),
                    created_at=datetime.utcnow()
                ),
                request_timestamp=datetime.utcnow()
            )
            
            mock_mgr.authenticate_user = AsyncMock(return_value=mock_context)
            mock_mgr.validate_session = AsyncMock(return_value=mock_context)
            mock_mgr.check_permission = AsyncMock(return_value=True)
            mock_mgr.initialize = AsyncMock()
            mock_mgr.cleanup = AsyncMock()
            
            # Test authenticate_user
            context = await authenticate_user("test_token")
            assert context.user_id == "test_user"
            mock_mgr.authenticate_user.assert_called_once()
            
            # Test validate_session
            context = await validate_session("test_session")
            assert context.user_id == "test_user"
            mock_mgr.validate_session.assert_called_once()
            
            # Test check_permission
            has_permission = await check_permission(mock_context, ResourceType.METRICS)
            assert has_permission is True
            mock_mgr.check_permission.assert_called_once()
            
            # Test initialize_security_manager
            await initialize_security_manager()
            mock_mgr.initialize.assert_called_once()
            
            # Test cleanup_security_manager
            await cleanup_security_manager()
            mock_mgr.cleanup.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])