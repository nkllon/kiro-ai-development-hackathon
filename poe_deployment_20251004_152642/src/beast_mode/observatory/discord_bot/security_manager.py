"""
Security Manager for Discord Bot

Handles token management, permissions, and security for Discord bot.
Built with extraction-ready architecture for standalone framework.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64
import hashlib

from .models import BotConfig, AuditLogEntry
from .exceptions import SecurityError, AuthenticationError, PermissionError
from .interfaces import SecurityServiceInterface, AuditServiceInterface

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages Discord bot tokens securely"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            self._cipher = Fernet(encryption_key.encode())
        else:
            # Generate a key from environment or create one
            key = os.getenv('DISCORD_BOT_ENCRYPTION_KEY')
            if not key:
                # Generate a new key (in production, this should be stored securely)
                key = Fernet.generate_key().decode()
                logger.warning("Generated new encryption key. Store DISCORD_BOT_ENCRYPTION_KEY securely!")
            self._cipher = Fernet(key.encode())
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a Discord bot token"""
        try:
            encrypted = self._cipher.encrypt(token.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt token: {e}")
            raise SecurityError("Token encryption failed")
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a Discord bot token"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_token.encode())
            decrypted = self._cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            raise SecurityError("Token decryption failed")
    
    def validate_token_format(self, token: str) -> bool:
        """Validate Discord token format"""
        if not token:
            return False
        
        # Discord bot tokens have a specific format
        # They start with the bot's user ID in base64, followed by a dot, then the token
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Basic length checks
        if len(parts[0]) < 10 or len(parts[2]) < 20:
            return False
        
        return True
    
    def mask_token(self, token: str) -> str:
        """Mask token for logging (show only last 8 characters)"""
        if not token or len(token) < 16:
            return "***"
        return f"...{token[-8:]}"


class SecurityManager:
    """Manages security for Discord bot operations"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.token_manager = TokenManager()
        self._audit_log: List[AuditLogEntry] = []
        self._rate_limits: Dict[str, List[datetime]] = {}
        self._failed_attempts: Dict[str, int] = {}
        
    async def initialize(self) -> bool:
        """Initialize security manager"""
        try:
            # Validate bot token
            if not self.token_manager.validate_token_format(self.config.token):
                logger.error("Invalid Discord bot token format")
                return False
            
            logger.info("Security manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize security manager: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up security manager"""
        # Clear sensitive data
        self._rate_limits.clear()
        self._failed_attempts.clear()
        logger.info("Security manager cleanup complete")
    
    async def validate_permissions(self, user_id: str, action: str, resource: str) -> bool:
        """Validate user permissions for an action"""
        try:
            # For now, implement basic permission checking
            # In production, this would integrate with Discord's permission system
            
            # Log the permission check
            await self._audit_action(
                user_id=user_id,
                action=f"permission_check:{action}",
                resource=resource,
                details={"result": "allowed"}  # Simplified for now
            )
            
            return True  # Allow all actions for now
            
        except Exception as e:
            logger.error(f"Permission validation failed: {e}")
            return False
    
    async def is_rate_limited(self, user_id: str, action: str) -> bool:
        """Check if user is rate limited for an action"""
        try:
            key = f"{user_id}:{action}"
            now = datetime.utcnow()
            
            # Clean old entries (older than 1 minute)
            if key in self._rate_limits:
                self._rate_limits[key] = [
                    timestamp for timestamp in self._rate_limits[key]
                    if now - timestamp < timedelta(minutes=1)
                ]
            
            # Check rate limit (max 10 actions per minute)
            if key in self._rate_limits and len(self._rate_limits[key]) >= 10:
                logger.warning(f"Rate limit exceeded for {user_id}:{action}")
                return True
            
            # Record this action
            if key not in self._rate_limits:
                self._rate_limits[key] = []
            self._rate_limits[key].append(now)
            
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Fail safe - assume rate limited
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        # Simplified implementation
        # In production, this would query Discord's permission system
        return ["basic_commands", "help", "status", "health"]
    
    async def _audit_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """Log an action to the audit trail"""
        if not self.config.audit_logging:
            return
        
        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {},
            success=success,
            error_message=error_message,
            correlation_id=self._generate_correlation_id()
        )
        
        self._audit_log.append(entry)
        
        # Keep only last 1000 entries to prevent memory issues
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]
        
        logger.info(f"Audit: {user_id} {action} on {resource} - {'success' if success else 'failed'}")
    
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        entries = self._audit_log
        
        # Filter by user_id if specified
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        
        # Filter by action if specified
        if action:
            entries = [e for e in entries if action in e.action]
        
        # Sort by timestamp (newest first) and limit
        entries = sorted(entries, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        # Convert to dictionaries
        return [
            {
                'timestamp': entry.timestamp.isoformat(),
                'user_id': entry.user_id,
                'action': entry.action,
                'resource': entry.resource,
                'success': entry.success,
                'details': entry.details,
                'error_message': entry.error_message,
                'correlation_id': entry.correlation_id
            }
            for entry in entries
        ]
    
    def _generate_correlation_id(self) -> str:
        """Generate a correlation ID for audit logging"""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{timestamp}:{os.urandom(8).hex()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    async def detect_suspicious_activity(self, user_id: str, action: str) -> bool:
        """Detect suspicious activity patterns"""
        try:
            # Check for rapid repeated actions
            key = f"{user_id}:{action}"
            if key in self._rate_limits:
                recent_actions = len(self._rate_limits[key])
                if recent_actions > 20:  # More than 20 actions per minute
                    logger.warning(f"Suspicious activity detected: {user_id} performed {action} {recent_actions} times")
                    return True
            
            # Check for failed attempts
            if user_id in self._failed_attempts and self._failed_attempts[user_id] > 5:
                logger.warning(f"Multiple failed attempts detected for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Suspicious activity detection failed: {e}")
            return False
    
    async def record_failed_attempt(self, user_id: str, reason: str) -> None:
        """Record a failed attempt"""
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = 0
        
        self._failed_attempts[user_id] += 1
        
        await self._audit_action(
            user_id=user_id,
            action="failed_attempt",
            resource="bot_access",
            details={"reason": reason},
            success=False,
            error_message=reason
        )
    
    async def reset_failed_attempts(self, user_id: str) -> None:
        """Reset failed attempts for a user"""
        if user_id in self._failed_attempts:
            del self._failed_attempts[user_id]


# Security service implementations for Observatory integration

class DiscordSecurityService(SecurityServiceInterface):
    """Security service implementation for Observatory integration"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
    
    async def get_health(self):
        return "healthy"  # Simplified
    
    async def initialize(self) -> bool:
        return await self.security_manager.initialize()
    
    async def cleanup(self) -> None:
        await self.security_manager.cleanup()
    
    async def validate_permissions(self, user_id: str, action: str, resource: str) -> bool:
        return await self.security_manager.validate_permissions(user_id, action, resource)
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        return await self.security_manager.get_user_permissions(user_id)
    
    async def is_rate_limited(self, user_id: str, action: str) -> bool:
        return await self.security_manager.is_rate_limited(user_id, action)


class DiscordAuditService(AuditServiceInterface):
    """Audit service implementation for Observatory integration"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
    
    async def get_health(self):
        return "healthy"  # Simplified
    
    async def initialize(self) -> bool:
        return True
    
    async def cleanup(self) -> None:
        pass
    
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        await self.security_manager._audit_action(user_id, action, resource, details)
    
    async def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        return await self.security_manager.get_audit_log(user_id, action, limit)