#!/usr/bin/env python3
"""
Auth Session Manager - Session management and token handling

Extracted from auth_service.py for RM-DDD compliance.
Single responsibility: Session management and token handling.
"""

import json
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .auth_models import AuthSession, AuthCredentials, AuthResult, AuthConfig

logger = logging.getLogger(__name__)


class AuthSessionManager:
    """Manages authentication sessions and tokens"""
    
    def __init__(self, config: AuthConfig, storage_path: Optional[Path] = None):
        """Initialize session manager"""
        self.config = config
        self.storage_path = storage_path or Path("auth_sessions.json")
        self.active_sessions: Dict[str, AuthSession] = {}
        self.session_tokens: Dict[str, str] = {}  # token -> session_id mapping
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids
        self.load_sessions()
    
    def create_session(self, user_id: str, username: str, credentials: AuthCredentials) -> AuthResult:
        """Create a new authentication session"""
        try:
            # Check if user has too many active sessions
            if self._has_too_many_sessions(user_id):
                return AuthResult(
                    success=False,
                    message="Too many active sessions",
                    error_code="TOO_MANY_SESSIONS"
                )
            
            # Create session
            session_id = self._generate_session_id()
            session = AuthSession(
                session_id=session_id,
                user_id=user_id,
                username=username,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=self.config.session_timeout_minutes),
                metadata={'created_from': 'auth_service'}
            )
            
            # Generate session token
            session_token = self._generate_session_token()
            
            # Store session
            self.active_sessions[session_id] = session
            self.session_tokens[session_token] = session_id
            
            # Update user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Update credentials with session token
            credentials.session_token = session_token
            credentials.expires_at = session.expires_at
            
            # Save sessions
            self.save_sessions()
            
            logger.info(f"Created session {session_id} for user {username}")
            
            return AuthResult(
                success=True,
                message="Session created successfully",
                session=session,
                credentials=credentials
            )
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return AuthResult(
                success=False,
                message=f"Failed to create session: {str(e)}",
                error_code="SESSION_CREATION_ERROR"
            )
    
    def validate_session(self, session_token: str) -> AuthResult:
        """Validate a session token"""
        try:
            if not session_token:
                return AuthResult(
                    success=False,
                    message="No session token provided",
                    error_code="NO_TOKEN"
                )
            
            # Get session ID from token
            session_id = self.session_tokens.get(session_token)
            if not session_id:
                return AuthResult(
                    success=False,
                    message="Invalid session token",
                    error_code="INVALID_TOKEN"
                )
            
            # Get session
            session = self.active_sessions.get(session_id)
            if not session:
                return AuthResult(
                    success=False,
                    message="Session not found",
                    error_code="SESSION_NOT_FOUND"
                )
            
            # Check if session is valid
            if not session.is_valid():
                # Clean up expired session
                self._cleanup_session(session_id)
                return AuthResult(
                    success=False,
                    message="Session expired",
                    error_code="SESSION_EXPIRED"
                )
            
            # Update last activity
            session.update_activity()
            self.save_sessions()
            
            return AuthResult(
                success=True,
                message="Session is valid",
                session=session
            )
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return AuthResult(
                success=False,
                message=f"Session validation failed: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
    
    def refresh_session(self, session_token: str) -> AuthResult:
        """Refresh an existing session"""
        try:
            # Validate session first
            validation_result = self.validate_session(session_token)
            if not validation_result.success:
                return validation_result
            
            # Extend session
            session = validation_result.session
            session.extend_session(self.config.session_timeout_minutes)
            self.save_sessions()
            
            logger.info(f"Refreshed session {session.session_id}")
            
            return AuthResult(
                success=True,
                message="Session refreshed successfully",
                session=session
            )
            
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return AuthResult(
                success=False,
                message=f"Session refresh failed: {str(e)}",
                error_code="REFRESH_ERROR"
            )
    
    def invalidate_session(self, session_token: str) -> AuthResult:
        """Invalidate a session"""
        try:
            if not session_token:
                return AuthResult(
                    success=False,
                    message="No session token provided",
                    error_code="NO_TOKEN"
                )
            
            # Get session ID from token
            session_id = self.session_tokens.get(session_token)
            if not session_id:
                return AuthResult(
                    success=False,
                    message="Invalid session token",
                    error_code="INVALID_TOKEN"
                )
            
            # Invalidate session
            self._cleanup_session(session_id)
            
            logger.info(f"Invalidated session {session_id}")
            
            return AuthResult(
                success=True,
                message="Session invalidated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            return AuthResult(
                success=False,
                message=f"Session invalidation failed: {str(e)}",
                error_code="INVALIDATION_ERROR"
            )
    
    def get_user_sessions(self, user_id: str) -> List[AuthSession]:
        """Get all active sessions for a user"""
        try:
            session_ids = self.user_sessions.get(user_id, [])
            sessions = []
            
            for session_id in session_ids:
                session = self.active_sessions.get(session_id)
                if session and session.is_valid():
                    sessions.append(session)
                else:
                    # Clean up invalid session
                    self._cleanup_session(session_id)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                if session.is_expired():
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self._cleanup_session(session_id)
            
            if expired_sessions:
                self.save_sessions()
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def _has_too_many_sessions(self, user_id: str) -> bool:
        """Check if user has too many active sessions"""
        active_count = len([s for s in self.get_user_sessions(user_id)])
        return active_count >= self.config.max_sessions_per_user
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{secrets.token_hex(16)}_{int(time.time())}"
    
    def _generate_session_token(self) -> str:
        """Generate unique session token"""
        return f"token_{secrets.token_urlsafe(32)}_{int(time.time())}"
    
    def _cleanup_session(self, session_id: str) -> None:
        """Clean up a session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            # Remove from active sessions
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove from user sessions
            if session.user_id in self.user_sessions:
                if session_id in self.user_sessions[session.user_id]:
                    self.user_sessions[session.user_id].remove(session_id)
                if not self.user_sessions[session.user_id]:
                    del self.user_sessions[session.user_id]
            
            # Remove token mapping
            token_to_remove = None
            for token, sid in self.session_tokens.items():
                if sid == session_id:
                    token_to_remove = token
                    break
            if token_to_remove:
                del self.session_tokens[token_to_remove]
                
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
    
    def load_sessions(self) -> None:
        """Load sessions from storage"""
        try:
            if not self.storage_path.exists():
                return
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load active sessions
            for session_data in data.get('sessions', []):
                session = AuthSession.from_dict(session_data)
                if session.is_valid():
                    self.active_sessions[session.session_id] = session
            
            # Load session tokens
            self.session_tokens = data.get('tokens', {})
            
            # Load user sessions
            self.user_sessions = data.get('user_sessions', {})
            
            logger.info(f"Loaded {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    
    def save_sessions(self) -> None:
        """Save sessions to storage"""
        try:
            if not self.config.enable_session_persistence:
                return
            
            data = {
                'sessions': [session.to_dict() for session in self.active_sessions.values()],
                'tokens': self.session_tokens,
                'user_sessions': self.user_sessions,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            'total_sessions': len(self.active_sessions),
            'total_users': len(self.user_sessions),
            'total_tokens': len(self.session_tokens),
            'storage_enabled': self.config.enable_session_persistence,
            'storage_path': str(self.storage_path)
        }
