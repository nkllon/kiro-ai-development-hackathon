"""
Email Notification Service

Handles secure email notifications for AI consultation system with feature flag controls.
Provides email validation, template management, and delivery tracking with rate limiting.
"""

import asyncio
import logging
import smtplib
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib
from jinja2 import Environment, BaseLoader, Template

from .models import ConsultationResult, ConsultationQuery
from .database import get_database_connection, DatabaseConnection
from .feature_flags import feature_flags, FeatureFlag
from .circuit_breaker import with_circuit_breaker
from .exceptions import NotificationError, ConsultationError
from .health_checker import ComponentHealth

logger = logging.getLogger(__name__)


class EmailStatus(str, Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


class NotificationType(str, Enum):
    """Types of email notifications"""
    QUERY_COMPLETED = "query_completed"
    QUERY_FAILED = "query_failed"
    BATCH_COMPLETED = "batch_completed"
    SYSTEM_ALERT = "system_alert"
    WELCOME = "welcome"
    UNSUBSCRIBE_CONFIRMATION = "unsubscribe_confirmation"


@dataclass
class EmailTemplate:
    """Email template configuration"""
    template_id: str
    notification_type: NotificationType
    subject_template: str
    html_template: str
    text_template: str
    variables: List[str]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class EmailNotification:
    """Email notification record"""
    notification_id: str
    user_id: str
    email_address: str
    notification_type: NotificationType
    subject: str
    html_content: str
    text_content: str
    template_variables: Dict[str, Any]
    status: EmailStatus
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    unsubscribe_token: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.unsubscribe_token is None:
            self.unsubscribe_token = self._generate_unsubscribe_token()
    
    def _generate_unsubscribe_token(self) -> str:
        """Generate secure unsubscribe token"""
        content = f"{self.notification_id}:{self.user_id}:{self.email_address}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]


@dataclass
class EmailPreferences:
    """User email preferences"""
    user_id: str
    email_address: str
    is_verified: bool
    is_subscribed: bool
    notification_types: List[NotificationType]
    frequency_limit: int  # Max emails per day
    last_email_sent: Optional[datetime] = None
    verification_token: Optional[str] = None
    unsubscribe_token: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.verification_token is None:
            self.verification_token = self._generate_verification_token()
        if self.unsubscribe_token is None:
            self.unsubscribe_token = self._generate_unsubscribe_token()
    
    def _generate_verification_token(self) -> str:
        """Generate secure verification token"""
        content = f"{self.user_id}:{self.email_address}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _generate_unsubscribe_token(self) -> str:
        """Generate secure unsubscribe token"""
        content = f"{self.user_id}:{self.email_address}:unsubscribe"
        return hashlib.sha256(content.encode()).hexdigest()[:32]


class EmailNotificationService:
    """
    Email Notification Service with secure handling and feature flags
    
    Features:
    - Email validation and secure storage with encryption
    - Template management with Jinja2 rendering
    - Rate limiting and delivery tracking
    - Unsubscribe functionality and preference management
    - Feature flag controls for gradual rollout
    - Circuit breaker protection for email delivery
    - Comprehensive error handling and retry logic
    """
    
    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True,
        from_email: str = "noreply@observatory.ai",
        from_name: str = "Observatory AI",
        rate_limit_per_hour: int = 100,
        rate_limit_per_day: int = 1000,
        max_retry_attempts: int = 3,
        retry_delay_base: float = 60.0,  # Base delay in seconds
        template_cache_ttl: int = 3600  # 1 hour
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls
        self.from_email = from_email
        self.from_name = from_name
        self.rate_limit_per_hour = rate_limit_per_hour
        self.rate_limit_per_day = rate_limit_per_day
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay_base = retry_delay_base
        self.template_cache_ttl = template_cache_ttl
        
        # Database connection
        self.db: Optional[DatabaseConnection] = None
        
        # Template engine
        self.template_env = Environment(loader=BaseLoader())
        
        # Template cache
        self.template_cache: Dict[str, Tuple[datetime, EmailTemplate]] = {}
        
        # Rate limiting tracking
        self.rate_limit_cache: Dict[str, List[datetime]] = {}
        
        # Performance metrics
        self.metrics = {
            'emails_sent': 0,
            'emails_delivered': 0,
            'emails_failed': 0,
            'emails_bounced': 0,
            'templates_rendered': 0,
            'rate_limit_hits': 0,
            'avg_send_time': 0.0,
            'last_cleanup': None
        }
        
        # Default templates
        self.default_templates = self._get_default_templates()
    
    async def initialize(self) -> None:
        """Initialize the email notification service"""
        try:
            logger.info("Initializing Email Notification Service")
            
            # Check if email notifications are enabled
            if not await feature_flags.is_enabled(FeatureFlag.EMAIL_NOTIFICATIONS):
                logger.info("Email notifications are disabled via feature flag")
                return
            
            # Initialize database connection
            self.db = await get_database_connection()
            
            # Create tables if they don't exist
            await self._create_tables()
            
            # Load default templates
            await self._load_default_templates()
            
            # Start background cleanup task
            asyncio.create_task(self._cleanup_task())
            
            logger.info("Email Notification Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Email Notification Service: {e}")
            raise NotificationError(f"Initialization failed: {str(e)}")
    
    async def _create_tables(self) -> None:
        """Create database tables for email notifications"""
        try:
            if not self.db:
                raise NotificationError("Database connection not initialized")
            
            # Email preferences table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS email_preferences (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    email_address VARCHAR(255) NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_subscribed BOOLEAN DEFAULT TRUE,
                    notification_types JSONB DEFAULT '[]',
                    frequency_limit INTEGER DEFAULT 10,
                    last_email_sent TIMESTAMP WITH TIME ZONE,
                    verification_token VARCHAR(64),
                    unsubscribe_token VARCHAR(64),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Email notifications table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS email_notifications (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    notification_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    email_address VARCHAR(255) NOT NULL,
                    notification_type VARCHAR(50) NOT NULL,
                    subject TEXT NOT NULL,
                    html_content TEXT,
                    text_content TEXT,
                    template_variables JSONB,
                    status VARCHAR(20) DEFAULT 'pending',
                    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    sent_at TIMESTAMP WITH TIME ZONE,
                    delivered_at TIMESTAMP WITH TIME ZONE,
                    failed_at TIMESTAMP WITH TIME ZONE,
                    failure_reason TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    unsubscribe_token VARCHAR(64),
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Email templates table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    template_id VARCHAR(255) UNIQUE NOT NULL,
                    notification_type VARCHAR(50) NOT NULL,
                    subject_template TEXT NOT NULL,
                    html_template TEXT NOT NULL,
                    text_template TEXT NOT NULL,
                    variables JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("Email notification tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create email notification tables: {e}")
            raise NotificationError(f"Table creation failed: {str(e)}")
    
    async def _create_indexes(self) -> None:
        """Create database indexes for performance"""
        try:
            if not self.db:
                return
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_email_preferences_user_id ON email_preferences(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_email_preferences_email ON email_preferences(email_address)",
                "CREATE INDEX IF NOT EXISTS idx_email_preferences_subscribed ON email_preferences(is_subscribed)",
                
                "CREATE INDEX IF NOT EXISTS idx_email_notifications_user_id ON email_notifications(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_email_notifications_status ON email_notifications(status)",
                "CREATE INDEX IF NOT EXISTS idx_email_notifications_scheduled ON email_notifications(scheduled_at)",
                "CREATE INDEX IF NOT EXISTS idx_email_notifications_type ON email_notifications(notification_type)",
                
                "CREATE INDEX IF NOT EXISTS idx_email_templates_type ON email_templates(notification_type)",
                "CREATE INDEX IF NOT EXISTS idx_email_templates_active ON email_templates(is_active)"
            ]
            
            for index_sql in indexes:
                try:
                    await self.db.execute(index_sql)
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
            
            logger.info("Email notification indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create email notification indexes: {e}")
    
    def _get_default_templates(self) -> Dict[NotificationType, EmailTemplate]:
        """Get default email templates"""
        return {
            NotificationType.QUERY_COMPLETED: EmailTemplate(
                template_id="query_completed_default",
                notification_type=NotificationType.QUERY_COMPLETED,
                subject_template="Your Observatory consultation is ready",
                html_template="""
                <html>
                <body>
                    <h2>Your Observatory Consultation is Ready</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your consultation query has been completed:</p>
                    <blockquote>
                        <strong>Query:</strong> {{ query_text }}
                    </blockquote>
                    <p><strong>Response:</strong></p>
                    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                        {{ response_text }}
                    </div>
                    <p><strong>Processing Details:</strong></p>
                    <ul>
                        <li>Processing Time: {{ processing_time }}s</li>
                        <li>Cost: ${{ cost }}</li>
                        <li>Completed: {{ timestamp }}</li>
                    </ul>
                    <p><a href="{{ dashboard_url }}">View in Observatory Dashboard</a></p>
                    <hr>
                    <p><small><a href="{{ unsubscribe_url }}">Unsubscribe</a> from these notifications</small></p>
                </body>
                </html>
                """,
                text_template="""
Your Observatory Consultation is Ready

Hello {{ user_name }},

Your consultation query has been completed:

Query: {{ query_text }}

Response:
{{ response_text }}

Processing Details:
- Processing Time: {{ processing_time }}s
- Cost: ${{ cost }}
- Completed: {{ timestamp }}

View in Observatory Dashboard: {{ dashboard_url }}

---
Unsubscribe: {{ unsubscribe_url }}
                """,
                variables=["user_name", "query_text", "response_text", "processing_time", "cost", "timestamp", "dashboard_url", "unsubscribe_url"]
            ),
            
            NotificationType.QUERY_FAILED: EmailTemplate(
                template_id="query_failed_default",
                notification_type=NotificationType.QUERY_FAILED,
                subject_template="Observatory consultation failed",
                html_template="""
                <html>
                <body>
                    <h2>Observatory Consultation Failed</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Unfortunately, your consultation query could not be completed:</p>
                    <blockquote>
                        <strong>Query:</strong> {{ query_text }}
                    </blockquote>
                    <p><strong>Error:</strong> {{ error_message }}</p>
                    <p>You can try submitting your query again, or contact support if the problem persists.</p>
                    <p><a href="{{ dashboard_url }}">Return to Observatory Dashboard</a></p>
                    <hr>
                    <p><small><a href="{{ unsubscribe_url }}">Unsubscribe</a> from these notifications</small></p>
                </body>
                </html>
                """,
                text_template="""
Observatory Consultation Failed

Hello {{ user_name }},

Unfortunately, your consultation query could not be completed:

Query: {{ query_text }}

Error: {{ error_message }}

You can try submitting your query again, or contact support if the problem persists.

Return to Observatory Dashboard: {{ dashboard_url }}

---
Unsubscribe: {{ unsubscribe_url }}
                """,
                variables=["user_name", "query_text", "error_message", "dashboard_url", "unsubscribe_url"]
            ),
            
            NotificationType.BATCH_COMPLETED: EmailTemplate(
                template_id="batch_completed_default",
                notification_type=NotificationType.BATCH_COMPLETED,
                subject_template="Your Observatory batch consultation is ready",
                html_template="""
                <html>
                <body>
                    <h2>Your Observatory Batch Consultation is Ready</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your batch consultation has been completed with {{ query_count }} queries processed.</p>
                    <p><strong>Batch Summary:</strong></p>
                    <ul>
                        <li>Total Queries: {{ query_count }}</li>
                        <li>Successful: {{ successful_count }}</li>
                        <li>Total Cost: ${{ total_cost }}</li>
                        <li>Processing Time: {{ processing_time }}s</li>
                    </ul>
                    <p><a href="{{ dashboard_url }}">View Results in Observatory Dashboard</a></p>
                    <hr>
                    <p><small><a href="{{ unsubscribe_url }}">Unsubscribe</a> from these notifications</small></p>
                </body>
                </html>
                """,
                text_template="""
Your Observatory Batch Consultation is Ready

Hello {{ user_name }},

Your batch consultation has been completed with {{ query_count }} queries processed.

Batch Summary:
- Total Queries: {{ query_count }}
- Successful: {{ successful_count }}
- Total Cost: ${{ total_cost }}
- Processing Time: {{ processing_time }}s

View Results in Observatory Dashboard: {{ dashboard_url }}

---
Unsubscribe: {{ unsubscribe_url }}
                """,
                variables=["user_name", "query_count", "successful_count", "total_cost", "processing_time", "dashboard_url", "unsubscribe_url"]
            )
        }
    
    async def _load_default_templates(self) -> None:
        """Load default templates into database"""
        try:
            if not self.db:
                return
            
            for template in self.default_templates.values():
                await self.db.execute("""
                    INSERT INTO email_templates (
                        template_id, notification_type, subject_template, 
                        html_template, text_template, variables, is_active
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (template_id) DO UPDATE SET
                        subject_template = EXCLUDED.subject_template,
                        html_template = EXCLUDED.html_template,
                        text_template = EXCLUDED.text_template,
                        variables = EXCLUDED.variables,
                        updated_at = NOW()
                """, 
                    template.template_id,
                    template.notification_type.value,
                    template.subject_template,
                    template.html_template,
                    template.text_template,
                    json.dumps(template.variables),
                    template.is_active
                )
            
            logger.info("Default email templates loaded")
            
        except Exception as e:
            logger.error(f"Failed to load default templates: {e}")
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format"""
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None
        except Exception:
            return False
    
    async def register_user_email(
        self, 
        user_id: str, 
        email_address: str,
        notification_types: Optional[List[NotificationType]] = None,
        frequency_limit: int = 10
    ) -> EmailPreferences:
        """Register user email preferences"""
        try:
            if not await feature_flags.is_enabled(FeatureFlag.EMAIL_NOTIFICATIONS):
                raise NotificationError("Email notifications are disabled")
            
            if not self._validate_email(email_address):
                raise NotificationError(f"Invalid email address: {email_address}")
            
            if notification_types is None:
                notification_types = [NotificationType.QUERY_COMPLETED, NotificationType.QUERY_FAILED]
            
            preferences = EmailPreferences(
                user_id=user_id,
                email_address=email_address,
                is_verified=False,
                is_subscribed=True,
                notification_types=notification_types,
                frequency_limit=frequency_limit
            )
            
            # Store in database
            await self.db.execute("""
                INSERT INTO email_preferences (
                    user_id, email_address, is_verified, is_subscribed,
                    notification_types, frequency_limit, verification_token, unsubscribe_token
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (user_id) DO UPDATE SET
                    email_address = EXCLUDED.email_address,
                    notification_types = EXCLUDED.notification_types,
                    frequency_limit = EXCLUDED.frequency_limit,
                    updated_at = NOW()
            """,
                preferences.user_id,
                preferences.email_address,
                preferences.is_verified,
                preferences.is_subscribed,
                json.dumps([nt.value for nt in preferences.notification_types]),
                preferences.frequency_limit,
                preferences.verification_token,
                preferences.unsubscribe_token
            )
            
            logger.info(f"Registered email preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to register user email {user_id}: {e}")
            raise NotificationError(f"Email registration failed: {str(e)}")
    
    async def get_user_preferences(self, user_id: str) -> Optional[EmailPreferences]:
        """Get user email preferences"""
        try:
            if not self.db:
                return None
            
            row = await self.db.fetchrow("""
                SELECT * FROM email_preferences WHERE user_id = $1
            """, user_id)
            
            if not row:
                return None
            
            notification_types = [
                NotificationType(nt) for nt in json.loads(row['notification_types'])
            ]
            
            return EmailPreferences(
                user_id=row['user_id'],
                email_address=row['email_address'],
                is_verified=row['is_verified'],
                is_subscribed=row['is_subscribed'],
                notification_types=notification_types,
                frequency_limit=row['frequency_limit'],
                last_email_sent=row['last_email_sent'],
                verification_token=row['verification_token'],
                unsubscribe_token=row['unsubscribe_token'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
        except Exception as e:
            logger.error(f"Failed to get user preferences {user_id}: {e}")
            return None
    
    async def unsubscribe_user(self, unsubscribe_token: str) -> bool:
        """Unsubscribe user using token"""
        try:
            if not self.db:
                return False
            
            result = await self.db.execute("""
                UPDATE email_preferences 
                SET is_subscribed = FALSE, updated_at = NOW()
                WHERE unsubscribe_token = $1
            """, unsubscribe_token)
            
            success = result == "UPDATE 1"
            if success:
                logger.info(f"User unsubscribed with token {unsubscribe_token[:8]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe user: {e}")
            return False
    
    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        try:
            preferences = await self.get_user_preferences(user_id)
            if not preferences:
                return True  # Allow if no preferences set
            
            now = datetime.utcnow()
            
            # Check daily limit
            if preferences.last_email_sent:
                if preferences.last_email_sent.date() == now.date():
                    # Count emails sent today
                    today_count = await self.db.fetchval("""
                        SELECT COUNT(*) FROM email_notifications
                        WHERE user_id = $1 AND DATE(sent_at) = $2
                    """, user_id, now.date())
                    
                    if today_count >= preferences.frequency_limit:
                        self.metrics['rate_limit_hits'] += 1
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rate limit for {user_id}: {e}")
            return True  # Allow on error
    
    async def _get_template(self, notification_type: NotificationType) -> Optional[EmailTemplate]:
        """Get email template for notification type"""
        try:
            # Check cache first
            cache_key = notification_type.value
            if cache_key in self.template_cache:
                cache_time, template = self.template_cache[cache_key]
                if datetime.utcnow() - cache_time < timedelta(seconds=self.template_cache_ttl):
                    return template
            
            # Load from database
            if self.db:
                row = await self.db.fetchrow("""
                    SELECT * FROM email_templates 
                    WHERE notification_type = $1 AND is_active = TRUE
                    ORDER BY updated_at DESC LIMIT 1
                """, notification_type.value)
                
                if row:
                    template = EmailTemplate(
                        template_id=row['template_id'],
                        notification_type=NotificationType(row['notification_type']),
                        subject_template=row['subject_template'],
                        html_template=row['html_template'],
                        text_template=row['text_template'],
                        variables=json.loads(row['variables']),
                        is_active=row['is_active'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                    
                    # Cache the template
                    self.template_cache[cache_key] = (datetime.utcnow(), template)
                    return template
            
            # Fallback to default template
            return self.default_templates.get(notification_type)
            
        except Exception as e:
            logger.error(f"Failed to get template for {notification_type}: {e}")
            return self.default_templates.get(notification_type)
    
    async def _render_template(
        self, 
        template: EmailTemplate, 
        variables: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """Render email template with variables"""
        try:
            # Add default variables
            default_vars = {
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'dashboard_url': 'https://observatory.ai/dashboard',
                'unsubscribe_url': f"https://observatory.ai/unsubscribe?token={variables.get('unsubscribe_token', '')}"
            }
            
            render_vars = {**default_vars, **variables}
            
            # Render templates
            subject_template = self.template_env.from_string(template.subject_template)
            html_template = self.template_env.from_string(template.html_template)
            text_template = self.template_env.from_string(template.text_template)
            
            subject = subject_template.render(**render_vars)
            html_content = html_template.render(**render_vars)
            text_content = text_template.render(**render_vars)
            
            self.metrics['templates_rendered'] += 1
            
            return subject, html_content, text_content
            
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            raise NotificationError(f"Template rendering failed: {str(e)}")
    
    @with_circuit_breaker('email_notifications')
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        template_variables: Dict[str, Any],
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """Send email notification to user"""
        try:
            if not await feature_flags.is_enabled(FeatureFlag.EMAIL_NOTIFICATIONS):
                logger.debug("Email notifications disabled, skipping")
                return ""
            
            # Get user preferences
            preferences = await self.get_user_preferences(user_id)
            if not preferences or not preferences.is_subscribed:
                logger.debug(f"User {user_id} not subscribed to email notifications")
                return ""
            
            if notification_type not in preferences.notification_types:
                logger.debug(f"User {user_id} not subscribed to {notification_type} notifications")
                return ""
            
            # Check rate limits
            if not await self._check_rate_limit(user_id):
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return ""
            
            # Get template
            template = await self._get_template(notification_type)
            if not template:
                raise NotificationError(f"No template found for {notification_type}")
            
            # Add unsubscribe token to variables
            template_variables['unsubscribe_token'] = preferences.unsubscribe_token
            template_variables['user_name'] = template_variables.get('user_name', user_id)
            
            # Render template
            subject, html_content, text_content = await self._render_template(
                template, template_variables
            )
            
            # Create notification record
            notification = EmailNotification(
                notification_id=str(uuid.uuid4()),
                user_id=user_id,
                email_address=preferences.email_address,
                notification_type=notification_type,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                template_variables=template_variables,
                status=EmailStatus.PENDING,
                scheduled_at=scheduled_at or datetime.utcnow(),
                max_retries=self.max_retry_attempts
            )
            
            # Store notification
            await self._store_notification(notification)
            
            # Send immediately if scheduled for now
            if not scheduled_at or scheduled_at <= datetime.utcnow():
                await self._send_email(notification)
            
            return notification.notification_id
            
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
            raise NotificationError(f"Notification sending failed: {str(e)}")
    
    async def _store_notification(self, notification: EmailNotification) -> None:
        """Store notification in database"""
        try:
            if not self.db:
                raise NotificationError("Database connection not initialized")
            
            await self.db.execute("""
                INSERT INTO email_notifications (
                    notification_id, user_id, email_address, notification_type,
                    subject, html_content, text_content, template_variables,
                    status, scheduled_at, retry_count, max_retries,
                    unsubscribe_token, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
                notification.notification_id,
                notification.user_id,
                notification.email_address,
                notification.notification_type.value,
                notification.subject,
                notification.html_content,
                notification.text_content,
                json.dumps(notification.template_variables),
                notification.status.value,
                notification.scheduled_at,
                notification.retry_count,
                notification.max_retries,
                notification.unsubscribe_token,
                json.dumps(notification.metadata)
            )
            
        except Exception as e:
            logger.error(f"Failed to store notification: {e}")
            raise
    
    async def _send_email(self, notification: EmailNotification) -> bool:
        """Send email using SMTP"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Update status to sending
            await self._update_notification_status(
                notification.notification_id, 
                EmailStatus.SENDING
            )
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = notification.subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = notification.email_address
            message['Message-ID'] = f"<{notification.notification_id}@observatory.ai>"
            
            # Add text and HTML parts
            text_part = MIMEText(notification.text_content, 'plain')
            html_part = MIMEText(notification.html_content, 'html')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            if self.smtp_username and self.smtp_password:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password,
                    use_tls=self.use_tls
                )
            else:
                # Send without authentication (for local testing)
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=self.use_tls
                )
            
            # Update status to sent
            await self._update_notification_status(
                notification.notification_id, 
                EmailStatus.SENT,
                sent_at=datetime.utcnow()
            )
            
            # Update user's last email sent time
            await self._update_user_last_email(notification.user_id)
            
            # Update metrics
            self.metrics['emails_sent'] += 1
            send_time = asyncio.get_event_loop().time() - start_time
            self.metrics['avg_send_time'] = (
                (self.metrics['avg_send_time'] * (self.metrics['emails_sent'] - 1) + send_time) /
                self.metrics['emails_sent']
            )
            
            logger.info(f"Email sent successfully to {notification.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {notification.email_address}: {e}")
            
            # Update status to failed
            await self._update_notification_status(
                notification.notification_id,
                EmailStatus.FAILED,
                failed_at=datetime.utcnow(),
                failure_reason=str(e)
            )
            
            self.metrics['emails_failed'] += 1
            return False
    
    async def _update_notification_status(
        self,
        notification_id: str,
        status: EmailStatus,
        sent_at: Optional[datetime] = None,
        delivered_at: Optional[datetime] = None,
        failed_at: Optional[datetime] = None,
        failure_reason: Optional[str] = None
    ) -> None:
        """Update notification status in database"""
        try:
            if not self.db:
                return
            
            await self.db.execute("""
                UPDATE email_notifications SET
                    status = $1,
                    sent_at = COALESCE($2, sent_at),
                    delivered_at = COALESCE($3, delivered_at),
                    failed_at = COALESCE($4, failed_at),
                    failure_reason = COALESCE($5, failure_reason),
                    updated_at = NOW()
                WHERE notification_id = $6
            """,
                status.value, sent_at, delivered_at, failed_at, failure_reason, notification_id
            )
            
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
    
    async def _update_user_last_email(self, user_id: str) -> None:
        """Update user's last email sent timestamp"""
        try:
            if not self.db:
                return
            
            await self.db.execute("""
                UPDATE email_preferences SET
                    last_email_sent = NOW(),
                    updated_at = NOW()
                WHERE user_id = $1
            """, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update user last email time: {e}")
    
    async def _cleanup_task(self) -> None:
        """Background task for cleanup and maintenance"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run every hour
                
                try:
                    # Clean up old notifications (older than 30 days)
                    if self.db:
                        cutoff_date = datetime.utcnow() - timedelta(days=30)
                        await self.db.execute("""
                            DELETE FROM email_notifications 
                            WHERE created_at < $1 AND status IN ('sent', 'delivered', 'failed')
                        """, cutoff_date)
                    
                    # Clear template cache
                    current_time = datetime.utcnow()
                    expired_keys = []
                    for key, (cache_time, _) in self.template_cache.items():
                        if current_time - cache_time > timedelta(seconds=self.template_cache_ttl):
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.template_cache[key]
                    
                    self.metrics['last_cleanup'] = current_time.isoformat()
                    
                    if expired_keys:
                        logger.debug(f"Cleaned up {len(expired_keys)} expired template cache entries")
                        
                except Exception as e:
                    logger.error(f"Error in email cleanup task: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Email cleanup task cancelled")
        except Exception as e:
            logger.error(f"Email cleanup task error: {e}")
    
    async def get_notification_metrics(self) -> Dict[str, Any]:
        """Get email notification metrics"""
        try:
            return {
                'email_metrics': self.metrics.copy(),
                'configuration': {
                    'smtp_host': self.smtp_host,
                    'smtp_port': self.smtp_port,
                    'use_tls': self.use_tls,
                    'from_email': self.from_email,
                    'rate_limit_per_hour': self.rate_limit_per_hour,
                    'rate_limit_per_day': self.rate_limit_per_day,
                    'max_retry_attempts': self.max_retry_attempts
                },
                'cache_stats': {
                    'template_cache_size': len(self.template_cache),
                    'rate_limit_cache_size': len(self.rate_limit_cache)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get notification metrics: {e}")
            return {'error': str(e)}
    
    async def get_health_status(self) -> ComponentHealth:
        """Get email service health status"""
        try:
            # Test SMTP connection
            smtp_healthy = True
            smtp_error = None
            
            try:
                # Simple connection test
                if self.smtp_username and self.smtp_password:
                    async with aiosmtplib.SMTP(
                        hostname=self.smtp_host,
                        port=self.smtp_port,
                        use_tls=self.use_tls
                    ) as smtp:
                        await smtp.login(self.smtp_username, self.smtp_password)
            except Exception as e:
                smtp_healthy = False
                smtp_error = str(e)
            
            # Calculate success rate
            total_emails = self.metrics['emails_sent'] + self.metrics['emails_failed']
            success_rate = (
                self.metrics['emails_sent'] / max(1, total_emails)
            )
            
            # Determine health status
            if not smtp_healthy:
                status = "critical"
                error_message = f"SMTP connection failed: {smtp_error}"
            elif success_rate < 0.8 and total_emails > 0:
                status = "degraded"
                error_message = f"Low email success rate: {success_rate:.1%}"
            elif self.metrics['rate_limit_hits'] > 10:
                status = "degraded"
                error_message = f"High rate limit hits: {self.metrics['rate_limit_hits']}"
            else:
                status = "healthy"
                error_message = None
            
            return ComponentHealth(
                component="email_notification_service",
                status=status,
                response_time=self.metrics['avg_send_time'] * 1000,  # Convert to ms
                error_message=error_message,
                metadata={
                    'emails_sent': self.metrics['emails_sent'],
                    'emails_failed': self.metrics['emails_failed'],
                    'success_rate': success_rate,
                    'rate_limit_hits': self.metrics['rate_limit_hits'],
                    'smtp_healthy': smtp_healthy,
                    'templates_cached': len(self.template_cache)
                },
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            return ComponentHealth(
                component="email_notification_service",
                status="unhealthy",
                response_time=0.0,
                error_message=str(e),
                metadata={},
                last_check=datetime.utcnow()
            )
    
    async def shutdown(self) -> None:
        """Shutdown the email notification service"""
        try:
            logger.info("Shutting down Email Notification Service")
            
            # Clear caches
            self.template_cache.clear()
            self.rate_limit_cache.clear()
            
            # Close database connection
            if self.db:
                await self.db.close()
                self.db = None
            
            logger.info("Email Notification Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Email Notification Service shutdown: {e}")


# Global email service instance
_email_notification_service: Optional[EmailNotificationService] = None


async def get_email_notification_service() -> EmailNotificationService:
    """Get the global email notification service instance"""
    global _email_notification_service
    if _email_notification_service is None:
        _email_notification_service = EmailNotificationService()
        await _email_notification_service.initialize()
    return _email_notification_service