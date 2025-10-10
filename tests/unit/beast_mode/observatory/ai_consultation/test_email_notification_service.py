"""
Unit tests for Email Notification Service
Tests email validation, template rendering, delivery tracking, and feature flag integration.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
import json

from src.beast_mode.observatory.ai_consultation.email_notification_service import (
    EmailNotificationService, EmailTemplate, EmailNotification, EmailPreferences,
    EmailStatus, NotificationType, get_email_notification_service
)
from src.beast_mode.observatory.ai_consultation.exceptions import NotificationError


class TestEmailNotificationService:
    """Test EmailNotificationService functionality"""
    
    @pytest.fixture
    def email_service(self):
        """Create email service for testing"""
        return EmailNotificationService(
            smtp_host="localhost",
            smtp_port=587,
            smtp_username="test@example.com",
            smtp_password="testpass",
            use_tls=True,
            from_email="noreply@observatory.ai",
            from_name="Observatory AI",
            rate_limit_per_hour=10,
            rate_limit_per_day=100,
            max_retry_attempts=3
        )
    
    @pytest.fixture
    def mock_database(self):
        """Create mock database connection"""
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.fetch = AsyncMock()
        mock_db.fetchrow = AsyncMock()
        mock_db.fetchval = AsyncMock()
        mock_db.close = AsyncMock()
        return mock_db
    
    @pytest.fixture
    def sample_email_preferences(self):
        """Create sample email preferences"""
        return EmailPreferences(
            user_id="test-user-123",
            email_address="test@example.com",
            is_verified=True,
            is_subscribed=True,
            notification_types=[NotificationType.QUERY_COMPLETED, NotificationType.QUERY_FAILED],
            frequency_limit=10
        )
    
    async def test_initialization(self, email_service, mock_database):
        """Test email service initialization"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.get_database_connection') as mock_get_db:
                mock_flags.is_enabled.return_value = True
                mock_get_db.return_value = mock_database
                
                await email_service.initialize()
                
                assert email_service.db == mock_database
                mock_get_db.assert_called_once()
                mock_database.execute.assert_called()  # Table creation calls
    
    async def test_initialization_disabled(self, email_service):
        """Test initialization when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            
            await email_service.initialize()
            
            assert email_service.db is None
    
    def test_email_validation(self, email_service):
        """Test email address validation"""
        # Valid emails
        assert email_service._validate_email("test@example.com") == True
        assert email_service._validate_email("user.name+tag@domain.co.uk") == True
        assert email_service._validate_email("test123@test-domain.com") == True
        
        # Invalid emails
        assert email_service._validate_email("invalid-email") == False
        assert email_service._validate_email("@domain.com") == False
        assert email_service._validate_email("test@") == False
        assert email_service._validate_email("test..test@domain.com") == False
        assert email_service._validate_email("") == False
    
    async def test_register_user_email_success(self, email_service, mock_database):
        """Test successful user email registration"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            preferences = await email_service.register_user_email(
                user_id="test-user-123",
                email_address="test@example.com",
                notification_types=[NotificationType.QUERY_COMPLETED],
                frequency_limit=5
            )
            
            assert preferences.user_id == "test-user-123"
            assert preferences.email_address == "test@example.com"
            assert preferences.is_subscribed == True
            assert preferences.is_verified == False
            assert NotificationType.QUERY_COMPLETED in preferences.notification_types
            assert preferences.frequency_limit == 5
            
            mock_database.execute.assert_called()
    
    async def test_register_user_email_invalid(self, email_service, mock_database):
        """Test user email registration with invalid email"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            with pytest.raises(NotificationError, match="Invalid email address"):
                await email_service.register_user_email(
                    user_id="test-user-123",
                    email_address="invalid-email"
                )
    
    async def test_register_user_email_disabled(self, email_service, mock_database):
        """Test user email registration when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            email_service.db = mock_database
            
            with pytest.raises(NotificationError, match="Email notifications are disabled"):
                await email_service.register_user_email(
                    user_id="test-user-123",
                    email_address="test@example.com"
                )
    
    async def test_get_user_preferences(self, email_service, mock_database):
        """Test retrieving user preferences"""
        email_service.db = mock_database
        
        # Mock database response
        mock_database.fetchrow.return_value = {
            'user_id': 'test-user-123',
            'email_address': 'test@example.com',
            'is_verified': True,
            'is_subscribed': True,
            'notification_types': '["query_completed", "query_failed"]',
            'frequency_limit': 10,
            'last_email_sent': None,
            'verification_token': 'verify123',
            'unsubscribe_token': 'unsub123',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        preferences = await email_service.get_user_preferences("test-user-123")
        
        assert preferences is not None
        assert preferences.user_id == "test-user-123"
        assert preferences.email_address == "test@example.com"
        assert preferences.is_verified == True
        assert preferences.is_subscribed == True
        assert len(preferences.notification_types) == 2
        assert NotificationType.QUERY_COMPLETED in preferences.notification_types
        assert NotificationType.QUERY_FAILED in preferences.notification_types
    
    async def test_get_user_preferences_not_found(self, email_service, mock_database):
        """Test retrieving non-existent user preferences"""
        email_service.db = mock_database
        mock_database.fetchrow.return_value = None
        
        preferences = await email_service.get_user_preferences("nonexistent-user")
        
        assert preferences is None
    
    async def test_unsubscribe_user_success(self, email_service, mock_database):
        """Test successful user unsubscribe"""
        email_service.db = mock_database
        mock_database.execute.return_value = "UPDATE 1"
        
        result = await email_service.unsubscribe_user("unsubscribe-token-123")
        
        assert result == True
        mock_database.execute.assert_called_once()
    
    async def test_unsubscribe_user_invalid_token(self, email_service, mock_database):
        """Test unsubscribe with invalid token"""
        email_service.db = mock_database
        mock_database.execute.return_value = "UPDATE 0"
        
        result = await email_service.unsubscribe_user("invalid-token")
        
        assert result == False
    
    async def test_check_rate_limit_within_limit(self, email_service, mock_database, sample_email_preferences):
        """Test rate limit check within limits"""
        email_service.db = mock_database
        
        # Mock get_user_preferences
        with patch.object(email_service, 'get_user_preferences', return_value=sample_email_preferences):
            # Mock today's email count (within limit)
            mock_database.fetchval.return_value = 5  # Less than limit of 10
            
            result = await email_service._check_rate_limit("test-user-123")
            
            assert result == True
    
    async def test_check_rate_limit_exceeded(self, email_service, mock_database, sample_email_preferences):
        """Test rate limit check when exceeded"""
        email_service.db = mock_database
        
        # Set last email sent today
        sample_email_preferences.last_email_sent = datetime.utcnow()
        
        with patch.object(email_service, 'get_user_preferences', return_value=sample_email_preferences):
            # Mock today's email count (exceeds limit)
            mock_database.fetchval.return_value = 15  # More than limit of 10
            
            result = await email_service._check_rate_limit("test-user-123")
            
            assert result == False
            assert email_service.metrics['rate_limit_hits'] == 1
    
    async def test_get_template_from_cache(self, email_service):
        """Test template retrieval from cache"""
        # Add template to cache
        template = EmailTemplate(
            template_id="test-template",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject_template="Test Subject",
            html_template="<p>Test HTML</p>",
            text_template="Test Text",
            variables=["user_name"]
        )
        
        cache_key = NotificationType.QUERY_COMPLETED.value
        email_service.template_cache[cache_key] = (datetime.utcnow(), template)
        
        result = await email_service._get_template(NotificationType.QUERY_COMPLETED)
        
        assert result == template
    
    async def test_get_template_from_database(self, email_service, mock_database):
        """Test template retrieval from database"""
        email_service.db = mock_database
        
        # Mock database response
        mock_database.fetchrow.return_value = {
            'template_id': 'db-template',
            'notification_type': 'query_completed',
            'subject_template': 'DB Subject',
            'html_template': '<p>DB HTML</p>',
            'text_template': 'DB Text',
            'variables': '["user_name", "query_text"]',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = await email_service._get_template(NotificationType.QUERY_COMPLETED)
        
        assert result is not None
        assert result.template_id == 'db-template'
        assert result.subject_template == 'DB Subject'
        assert 'user_name' in result.variables
        assert 'query_text' in result.variables
    
    async def test_get_template_fallback_to_default(self, email_service, mock_database):
        """Test template fallback to default when not found in database"""
        email_service.db = mock_database
        mock_database.fetchrow.return_value = None
        
        result = await email_service._get_template(NotificationType.QUERY_COMPLETED)
        
        assert result is not None
        assert result.template_id == "query_completed_default"
        assert "Your Observatory consultation is ready" in result.subject_template
    
    async def test_render_template_success(self, email_service):
        """Test successful template rendering"""
        template = EmailTemplate(
            template_id="test-template",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject_template="Query Complete for {{ user_name }}",
            html_template="<p>Hello {{ user_name }}, your query: {{ query_text }}</p>",
            text_template="Hello {{ user_name }}, your query: {{ query_text }}",
            variables=["user_name", "query_text"]
        )
        
        variables = {
            "user_name": "John Doe",
            "query_text": "What is the system status?",
            "unsubscribe_token": "token123"
        }
        
        subject, html_content, text_content = await email_service._render_template(template, variables)
        
        assert subject == "Query Complete for John Doe"
        assert "Hello John Doe" in html_content
        assert "What is the system status?" in html_content
        assert "Hello John Doe" in text_content
        assert "What is the system status?" in text_content
        assert email_service.metrics['templates_rendered'] == 1
    
    async def test_render_template_with_defaults(self, email_service):
        """Test template rendering with default variables"""
        template = EmailTemplate(
            template_id="test-template",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject_template="Query Complete",
            html_template="<p>Completed at {{ timestamp }}</p>",
            text_template="Completed at {{ timestamp }}",
            variables=["timestamp"]
        )
        
        variables = {"unsubscribe_token": "token123"}
        
        subject, html_content, text_content = await email_service._render_template(template, variables)
        
        assert subject == "Query Complete"
        assert "Completed at" in html_content
        assert "UTC" in html_content  # Default timestamp format
        assert "Completed at" in text_content
        assert "UTC" in text_content
    
    async def test_send_notification_success(self, email_service, mock_database, sample_email_preferences):
        """Test successful notification sending"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            # Mock dependencies
            with patch.object(email_service, 'get_user_preferences', return_value=sample_email_preferences):
                with patch.object(email_service, '_check_rate_limit', return_value=True):
                    with patch.object(email_service, '_get_template') as mock_get_template:
                        with patch.object(email_service, '_render_template') as mock_render:
                            with patch.object(email_service, '_store_notification') as mock_store:
                                with patch.object(email_service, '_send_email', return_value=True) as mock_send:
                                    
                                    # Setup mocks
                                    mock_template = MagicMock()
                                    mock_get_template.return_value = mock_template
                                    mock_render.return_value = ("Subject", "<p>HTML</p>", "Text")
                                    
                                    # Send notification
                                    notification_id = await email_service.send_notification(
                                        user_id="test-user-123",
                                        notification_type=NotificationType.QUERY_COMPLETED,
                                        template_variables={"query_text": "Test query"}
                                    )
                                    
                                    assert notification_id != ""
                                    mock_store.assert_called_once()
                                    mock_send.assert_called_once()
    
    async def test_send_notification_user_not_subscribed(self, email_service, mock_database):
        """Test notification sending when user is not subscribed"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            # Create unsubscribed preferences
            unsubscribed_prefs = EmailPreferences(
                user_id="test-user-123",
                email_address="test@example.com",
                is_verified=True,
                is_subscribed=False,  # Not subscribed
                notification_types=[NotificationType.QUERY_COMPLETED],
                frequency_limit=10
            )
            
            with patch.object(email_service, 'get_user_preferences', return_value=unsubscribed_prefs):
                notification_id = await email_service.send_notification(
                    user_id="test-user-123",
                    notification_type=NotificationType.QUERY_COMPLETED,
                    template_variables={"query_text": "Test query"}
                )
                
                assert notification_id == ""  # Empty string indicates not sent
    
    async def test_send_notification_wrong_type(self, email_service, mock_database, sample_email_preferences):
        """Test notification sending for unsubscribed notification type"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            # User is not subscribed to BATCH_COMPLETED
            with patch.object(email_service, 'get_user_preferences', return_value=sample_email_preferences):
                notification_id = await email_service.send_notification(
                    user_id="test-user-123",
                    notification_type=NotificationType.BATCH_COMPLETED,  # Not in user's types
                    template_variables={"query_text": "Test query"}
                )
                
                assert notification_id == ""  # Empty string indicates not sent
    
    async def test_send_notification_rate_limited(self, email_service, mock_database, sample_email_preferences):
        """Test notification sending when rate limited"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = True
            email_service.db = mock_database
            
            with patch.object(email_service, 'get_user_preferences', return_value=sample_email_preferences):
                with patch.object(email_service, '_check_rate_limit', return_value=False):  # Rate limited
                    notification_id = await email_service.send_notification(
                        user_id="test-user-123",
                        notification_type=NotificationType.QUERY_COMPLETED,
                        template_variables={"query_text": "Test query"}
                    )
                    
                    assert notification_id == ""  # Empty string indicates not sent
    
    async def test_send_notification_disabled(self, email_service, mock_database):
        """Test notification sending when feature is disabled"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.feature_flags') as mock_flags:
            mock_flags.is_enabled.return_value = False
            email_service.db = mock_database
            
            notification_id = await email_service.send_notification(
                user_id="test-user-123",
                notification_type=NotificationType.QUERY_COMPLETED,
                template_variables={"query_text": "Test query"}
            )
            
            assert notification_id == ""  # Empty string indicates not sent
    
    async def test_store_notification(self, email_service, mock_database):
        """Test notification storage in database"""
        email_service.db = mock_database
        
        notification = EmailNotification(
            notification_id="test-notification-123",
            user_id="test-user-123",
            email_address="test@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
            template_variables={"test": "value"},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        await email_service._store_notification(notification)
        
        mock_database.execute.assert_called_once()
        # Verify the call was made with correct parameters
        call_args = mock_database.execute.call_args
        assert "INSERT INTO email_notifications" in call_args[0][0]
        assert notification.notification_id in call_args[0]
    
    async def test_send_email_success(self, email_service, mock_database):
        """Test successful email sending via SMTP"""
        email_service.db = mock_database
        
        notification = EmailNotification(
            notification_id="test-notification-123",
            user_id="test-user-123",
            email_address="test@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
            template_variables={},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            with patch.object(email_service, '_update_notification_status') as mock_update:
                with patch.object(email_service, '_update_user_last_email') as mock_update_user:
                    mock_smtp.send.return_value = None  # Successful send
                    
                    result = await email_service._send_email(notification)
                    
                    assert result == True
                    assert email_service.metrics['emails_sent'] == 1
                    mock_smtp.send.assert_called_once()
                    
                    # Verify status updates
                    assert mock_update.call_count == 2  # SENDING and SENT
                    mock_update_user.assert_called_once()
    
    async def test_send_email_failure(self, email_service, mock_database):
        """Test email sending failure"""
        email_service.db = mock_database
        
        notification = EmailNotification(
            notification_id="test-notification-123",
            user_id="test-user-123",
            email_address="test@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
            template_variables={},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            with patch.object(email_service, '_update_notification_status') as mock_update:
                mock_smtp.send.side_effect = Exception("SMTP connection failed")
                
                result = await email_service._send_email(notification)
                
                assert result == False
                assert email_service.metrics['emails_failed'] == 1
                
                # Verify failure status update
                mock_update.assert_called()
                # Check that the last call was for FAILED status
                last_call = mock_update.call_args_list[-1]
                assert last_call[0][1] == EmailStatus.FAILED
    
    async def test_update_notification_status(self, email_service, mock_database):
        """Test notification status update"""
        email_service.db = mock_database
        
        await email_service._update_notification_status(
            notification_id="test-notification-123",
            status=EmailStatus.SENT,
            sent_at=datetime.utcnow()
        )
        
        mock_database.execute.assert_called_once()
        call_args = mock_database.execute.call_args
        assert "UPDATE email_notifications" in call_args[0][0]
        assert "test-notification-123" in call_args[0]
    
    async def test_update_user_last_email(self, email_service, mock_database):
        """Test user last email timestamp update"""
        email_service.db = mock_database
        
        await email_service._update_user_last_email("test-user-123")
        
        mock_database.execute.assert_called_once()
        call_args = mock_database.execute.call_args
        assert "UPDATE email_preferences" in call_args[0][0]
        assert "test-user-123" in call_args[0]
    
    async def test_get_notification_metrics(self, email_service):
        """Test notification metrics retrieval"""
        # Set some metrics
        email_service.metrics['emails_sent'] = 50
        email_service.metrics['emails_failed'] = 5
        email_service.metrics['templates_rendered'] = 45
        email_service.metrics['rate_limit_hits'] = 2
        
        metrics = await email_service.get_notification_metrics()
        
        assert 'email_metrics' in metrics
        assert 'configuration' in metrics
        assert 'cache_stats' in metrics
        assert metrics['email_metrics']['emails_sent'] == 50
        assert metrics['email_metrics']['emails_failed'] == 5
        assert metrics['configuration']['smtp_host'] == "localhost"
        assert metrics['configuration']['rate_limit_per_day'] == 100
    
    async def test_get_health_status_healthy(self, email_service):
        """Test health status when system is healthy"""
        # Set good metrics
        email_service.metrics['emails_sent'] = 100
        email_service.metrics['emails_failed'] = 5
        email_service.metrics['rate_limit_hits'] = 1
        
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            # Mock successful SMTP connection
            mock_smtp.SMTP.return_value.__aenter__.return_value.login = AsyncMock()
            
            health = await email_service.get_health_status()
            
            assert health.component == "email_notification_service"
            assert health.status == "healthy"
            assert health.error_message is None
            assert health.metadata['emails_sent'] == 100
            assert health.metadata['success_rate'] > 0.9
    
    async def test_get_health_status_smtp_failure(self, email_service):
        """Test health status when SMTP connection fails"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            # Mock SMTP connection failure
            mock_smtp.SMTP.return_value.__aenter__.side_effect = Exception("Connection refused")
            
            health = await email_service.get_health_status()
            
            assert health.status == "critical"
            assert "SMTP connection failed" in health.error_message
    
    async def test_get_health_status_low_success_rate(self, email_service):
        """Test health status with low success rate"""
        # Set poor metrics
        email_service.metrics['emails_sent'] = 10
        email_service.metrics['emails_failed'] = 40  # 20% success rate
        email_service.metrics['rate_limit_hits'] = 1
        
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            mock_smtp.SMTP.return_value.__aenter__.return_value.login = AsyncMock()
            
            health = await email_service.get_health_status()
            
            assert health.status == "degraded"
            assert "Low email success rate" in health.error_message
    
    async def test_get_health_status_high_rate_limits(self, email_service):
        """Test health status with high rate limit hits"""
        # Set high rate limit hits
        email_service.metrics['emails_sent'] = 100
        email_service.metrics['emails_failed'] = 5
        email_service.metrics['rate_limit_hits'] = 15  # High rate limit hits
        
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.aiosmtplib') as mock_smtp:
            mock_smtp.SMTP.return_value.__aenter__.return_value.login = AsyncMock()
            
            health = await email_service.get_health_status()
            
            assert health.status == "degraded"
            assert "High rate limit hits" in health.error_message
    
    async def test_shutdown(self, email_service, mock_database):
        """Test email service shutdown"""
        email_service.db = mock_database
        email_service.template_cache = {'key1': 'value1'}
        email_service.rate_limit_cache = {'key2': 'value2'}
        
        await email_service.shutdown()
        
        assert len(email_service.template_cache) == 0
        assert len(email_service.rate_limit_cache) == 0
        mock_database.close.assert_called_once()
        assert email_service.db is None


class TestEmailTemplate:
    """Test EmailTemplate functionality"""
    
    def test_email_template_creation(self):
        """Test EmailTemplate creation"""
        template = EmailTemplate(
            template_id="test-template",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject_template="Test Subject",
            html_template="<p>Test HTML</p>",
            text_template="Test Text",
            variables=["user_name", "query_text"]
        )
        
        assert template.template_id == "test-template"
        assert template.notification_type == NotificationType.QUERY_COMPLETED
        assert template.subject_template == "Test Subject"
        assert template.html_template == "<p>Test HTML</p>"
        assert template.text_template == "Test Text"
        assert template.variables == ["user_name", "query_text"]
        assert template.is_active == True
        assert template.created_at is not None
        assert template.updated_at is not None


class TestEmailNotification:
    """Test EmailNotification functionality"""
    
    def test_email_notification_creation(self):
        """Test EmailNotification creation"""
        notification = EmailNotification(
            notification_id="test-notification",
            user_id="test-user",
            email_address="test@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
            template_variables={"test": "value"},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        assert notification.notification_id == "test-notification"
        assert notification.user_id == "test-user"
        assert notification.email_address == "test@example.com"
        assert notification.notification_type == NotificationType.QUERY_COMPLETED
        assert notification.status == EmailStatus.PENDING
        assert notification.retry_count == 0
        assert notification.max_retries == 3
        assert notification.unsubscribe_token is not None
        assert notification.metadata == {}
    
    def test_unsubscribe_token_generation(self):
        """Test unsubscribe token generation"""
        notification1 = EmailNotification(
            notification_id="test-1",
            user_id="user-1",
            email_address="test1@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test",
            html_content="HTML",
            text_content="Text",
            template_variables={},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        notification2 = EmailNotification(
            notification_id="test-2",
            user_id="user-2",
            email_address="test2@example.com",
            notification_type=NotificationType.QUERY_COMPLETED,
            subject="Test",
            html_content="HTML",
            text_content="Text",
            template_variables={},
            status=EmailStatus.PENDING,
            scheduled_at=datetime.utcnow()
        )
        
        # Different notifications should have different tokens
        assert notification1.unsubscribe_token != notification2.unsubscribe_token
        assert len(notification1.unsubscribe_token) == 32
        assert len(notification2.unsubscribe_token) == 32


class TestEmailPreferences:
    """Test EmailPreferences functionality"""
    
    def test_email_preferences_creation(self):
        """Test EmailPreferences creation"""
        preferences = EmailPreferences(
            user_id="test-user",
            email_address="test@example.com",
            is_verified=True,
            is_subscribed=True,
            notification_types=[NotificationType.QUERY_COMPLETED],
            frequency_limit=10
        )
        
        assert preferences.user_id == "test-user"
        assert preferences.email_address == "test@example.com"
        assert preferences.is_verified == True
        assert preferences.is_subscribed == True
        assert NotificationType.QUERY_COMPLETED in preferences.notification_types
        assert preferences.frequency_limit == 10
        assert preferences.verification_token is not None
        assert preferences.unsubscribe_token is not None
        assert preferences.created_at is not None
        assert preferences.updated_at is not None
    
    def test_token_generation(self):
        """Test verification and unsubscribe token generation"""
        preferences1 = EmailPreferences(
            user_id="user-1",
            email_address="test1@example.com",
            is_verified=False,
            is_subscribed=True,
            notification_types=[NotificationType.QUERY_COMPLETED],
            frequency_limit=10
        )
        
        preferences2 = EmailPreferences(
            user_id="user-2",
            email_address="test2@example.com",
            is_verified=False,
            is_subscribed=True,
            notification_types=[NotificationType.QUERY_COMPLETED],
            frequency_limit=10
        )
        
        # Different users should have different tokens
        assert preferences1.verification_token != preferences2.verification_token
        assert preferences1.unsubscribe_token != preferences2.unsubscribe_token
        assert len(preferences1.verification_token) == 32
        assert len(preferences1.unsubscribe_token) == 32


class TestGlobalEmailService:
    """Test global email service instance"""
    
    async def test_get_email_notification_service_singleton(self):
        """Test that get_email_notification_service returns singleton"""
        with patch('src.beast_mode.observatory.ai_consultation.email_notification_service.EmailNotificationService') as mock_class:
            mock_instance = AsyncMock()
            mock_class.return_value = mock_instance
            
            # First call
            service1 = await get_email_notification_service()
            
            # Second call
            service2 = await get_email_notification_service()
            
            # Should be the same instance
            assert service1 is service2
            
            # Should only create one instance
            mock_class.assert_called_once()
            mock_instance.initialize.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])