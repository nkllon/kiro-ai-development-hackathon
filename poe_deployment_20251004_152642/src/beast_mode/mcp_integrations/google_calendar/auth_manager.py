"""Google OAuth 2.0 Authentication Manager.

This module provides OAuth 2.0 authentication management for Google Calendar API,
following the Beast Mode framework's ReflectiveModule pattern.
"""

import json
import os
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode, parse_qs, urlparse

import requests
from cryptography.fernet import Fernet

from .base import GoogleCalendarReflectiveModule
from .interfaces.auth_interfaces import AuthManagerInterface
from .models import AuthResult, TokenInfo
from .profiling import profile


class GoogleAuthManager(GoogleCalendarReflectiveModule, AuthManagerInterface):
    """OAuth 2.0 authentication manager for Google Calendar API.
    
    Handles the complete OAuth flow, token management, and credential security
    following Beast Mode framework patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Google authentication manager.
        
        Args:
            config: Authentication configuration dictionary
        """
        super().__init__("google_auth_manager", config)
        
        # Configuration
        self.credentials_file = self.config.get("credentials_file", "/app/credentials/gcp-oauth.keys.json")
        self.scopes = self.config.get("scopes", [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ])
        
        # Authentication state
        self.token_info: Optional[TokenInfo] = None
        self.is_auth_flow_active = False
        
        self.logger.info(
            "Google Auth Manager initialized",
            extra={
                "correlation_id": self.correlation_id,
                "credentials_file": self.credentials_file,
                "scopes": self.scopes
            }
        )
    
    def initialize(self) -> bool:
        """Initialize the authentication manager.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Google Auth Manager")
            
            # Validate credentials file exists and has proper permissions
            if not self._validate_credentials_file():
                self.log_with_correlation("warning", "Invalid credentials file, continuing in stub mode")
                # Don't return False - continue in stub mode
            
            # Try to load existing tokens
            self._load_existing_tokens()
            self.logger.info("Google Auth Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Failed to initialize auth manager: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            # Health is managed by unified ReflectiveModule
            return False
    
    @profile("oauth_authentication")
    def authenticate(self) -> bool:
        """Perform OAuth 2.0 authentication flow.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.logger.info("Starting OAuth 2.0 authentication flow")
            self.is_auth_flow_active = True
            
            # Load client credentials
            client_config = self._load_client_credentials()
            if not client_config:
                self.logger.error("Failed to load client credentials")
                return False
            
            # Step 1: Generate authorization URL
            auth_url = self._generate_auth_url(client_config)
            
            # Step 2: Open browser for user authorization
            self.logger.info("Opening browser for OAuth authorization")
            webbrowser.open(auth_url)
            
            # Step 3: Get authorization code (simplified - in production use callback server)
            auth_code = input("Please enter the authorization code from the browser: ")
            
            # Step 4: Exchange authorization code for tokens
            tokens = self._exchange_code_for_tokens(client_config, auth_code)
            if not tokens:
                self.logger.error("Failed to exchange authorization code for tokens")
                return False
            
            # Step 5: Create and store token info
            expires_at = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
            self.token_info = TokenInfo(
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token'),
                expires_at=expires_at,
                scopes=self.scopes
            )
            
            # Step 6: Save tokens securely
            self._save_tokens()
            
            self.is_auth_flow_active = False
            self.logger.info("OAuth 2.0 authentication completed successfully")
            return True
            
        except Exception as e:
            self.is_auth_flow_active = False
            self.logger.error(
                f"Authentication failed: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid token.
        
        Returns:
            True if authenticated with valid token, False otherwise
        """
        if not self.token_info:
            return False
        
        # Check if token is expired
        if self.token_info.is_expired:
            self.logger.info("Token is expired, attempting refresh")
            return self.refresh_token()
        
        return True
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token if available and valid.
        
        Returns:
            Access token if available and valid, None otherwise
        """
        if not self.is_authenticated():
            return None
        
        return self.token_info.access_token
    
    @profile("oauth_token_refresh")
    def refresh_token(self) -> bool:
        """Refresh the access token using refresh token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        try:
            if not self.token_info or not self.token_info.refresh_token:
                self.logger.warning("No refresh token available")
                return False
            
            self.logger.info("Refreshing access token")
            
            # Load client credentials
            client_config = self._load_client_credentials()
            if not client_config:
                self.logger.error("Failed to load client credentials for token refresh")
                return False
            
            # Prepare refresh request
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': client_config['client_id'],
                'client_secret': client_config['client_secret'],
                'refresh_token': self.token_info.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            # Make refresh request
            response = requests.post(token_url, data=data, timeout=30)
            response.raise_for_status()
            
            tokens = response.json()
            
            # Update token info
            self.token_info.access_token = tokens['access_token']
            self.token_info.expires_at = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))
            
            # Update refresh token if provided
            if 'refresh_token' in tokens:
                self.token_info.refresh_token = tokens['refresh_token']
            
            # Save updated tokens
            self._save_tokens()
            
            self.logger.info("Access token refreshed successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Token refresh failed: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    def revoke_authentication(self) -> bool:
        """Revoke current authentication and clear tokens.
        
        Returns:
            True if revocation successful, False otherwise
        """
        try:
            self.logger.info("Revoking authentication")
            
            # Revoke token with Google if we have one
            if self.token_info and self.token_info.access_token:
                try:
                    revoke_url = "https://oauth2.googleapis.com/revoke"
                    params = {'token': self.token_info.access_token}
                    response = requests.post(revoke_url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        self.logger.info("Token revoked with Google successfully")
                    else:
                        self.logger.warning(f"Token revocation returned status: {response.status_code}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to revoke token with Google: {e}")
            
            # Clear local tokens
            self.token_info = None
            
            # Remove stored token files
            try:
                token_file = Path(self.credentials_file).parent / "tokens.encrypted"
                key_file = Path(self.credentials_file).parent / "token.key"
                
                if token_file.exists():
                    token_file.unlink()
                if key_file.exists():
                    key_file.unlink()
                    
                self.logger.info("Local token files removed")
                
            except Exception as e:
                self.logger.warning(f"Failed to remove local token files: {e}")
            
            self.logger.info("Authentication revoked successfully")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Token revocation failed: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False
    
    def _validate_credentials_file(self) -> bool:
        """Validate that credentials file exists and has proper permissions.
        
        Returns:
            True if credentials file is valid, False otherwise
        """
        try:
            credentials_path = Path(self.credentials_file)
            
            # Check if file exists
            if not credentials_path.exists():
                self.logger.warning(f"Credentials file not found: {self.credentials_file}")
                return False
            
            # Check file permissions (should be 600)
            file_mode = credentials_path.stat().st_mode & 0o777
            if file_mode != 0o600:
                self.logger.warning(f"Credentials file has incorrect permissions: {oct(file_mode)}, should be 600")
                # Try to fix permissions
                credentials_path.chmod(0o600)
            
            # Validate JSON content
            with open(credentials_path, 'r') as f:
                config = json.load(f)
                
            # Check required fields
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            if 'installed' in config:
                client_config = config['installed']
            elif 'web' in config:
                client_config = config['web']
            else:
                self.logger.error("Invalid credentials file format")
                return False
            
            for field in required_fields:
                if field not in client_config:
                    self.logger.error(f"Missing required field in credentials: {field}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating credentials file: {e}")
            return False
    
    def _load_existing_tokens(self):
        """Load existing tokens from secure storage if available."""
        try:
            token_file = Path(self.credentials_file).parent / "tokens.encrypted"
            
            if not token_file.exists():
                self.logger.info("No existing tokens found")
                return
            
            # Load encryption key
            key_file = Path(self.credentials_file).parent / "token.key"
            if not key_file.exists():
                self.logger.warning("Token encryption key not found")
                return
            
            with open(key_file, 'rb') as f:
                key = f.read()
            
            # Decrypt and load tokens
            fernet = Fernet(key)
            with open(token_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            token_data = json.loads(decrypted_data.decode())
            
            # Create TokenInfo object
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            self.token_info = TokenInfo(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                expires_at=expires_at,
                scopes=token_data.get('scopes', self.scopes)
            )
            
            self.logger.info("Existing tokens loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load existing tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to secure storage."""
        try:
            if not self.token_info:
                return
            
            token_file = Path(self.credentials_file).parent / "tokens.encrypted"
            key_file = Path(self.credentials_file).parent / "token.key"
            
            # Generate or load encryption key
            if not key_file.exists():
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                key_file.chmod(0o600)
            else:
                with open(key_file, 'rb') as f:
                    key = f.read()
            
            # Prepare token data
            token_data = {
                'access_token': self.token_info.access_token,
                'refresh_token': self.token_info.refresh_token,
                'expires_at': self.token_info.expires_at.isoformat(),
                'scopes': self.token_info.scopes
            }
            
            # Encrypt and save tokens
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(json.dumps(token_data).encode())
            
            with open(token_file, 'wb') as f:
                f.write(encrypted_data)
            token_file.chmod(0o600)
            
            self.logger.info("Tokens saved securely")
            
        except Exception as e:
            self.logger.error(f"Failed to save tokens: {e}")
    
    def _load_client_credentials(self) -> Optional[Dict[str, str]]:
        """Load OAuth client credentials from file.
        
        Returns:
            Client credentials dictionary or None if failed
        """
        try:
            with open(self.credentials_file, 'r') as f:
                config = json.load(f)
            
            if 'installed' in config:
                return config['installed']
            elif 'web' in config:
                return config['web']
            else:
                self.logger.error("Invalid credentials file format")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load client credentials: {e}")
            return None
    
    def _generate_auth_url(self, client_config: Dict[str, str]) -> str:
        """Generate OAuth authorization URL.
        
        Args:
            client_config: Client configuration dictionary
            
        Returns:
            Authorization URL
        """
        params = {
            'client_id': client_config['client_id'],
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',  # For installed apps
            'scope': ' '.join(self.scopes),
            'response_type': 'code',
            'access_type': 'offline',  # To get refresh token
            'prompt': 'consent'  # Force consent to get refresh token
        }
        
        auth_uri = client_config.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth')
        return f"{auth_uri}?{urlencode(params)}"
    
    def _exchange_code_for_tokens(self, client_config: Dict[str, str], auth_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            client_config: Client configuration dictionary
            auth_code: Authorization code from OAuth flow
            
        Returns:
            Token dictionary or None if failed
        """
        try:
            token_uri = client_config.get('token_uri', 'https://oauth2.googleapis.com/token')
            
            data = {
                'client_id': client_config['client_id'],
                'client_secret': client_config['client_secret'],
                'code': auth_code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
            }
            
            response = requests.post(token_uri, data=data, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to exchange code for tokens: {e}")
            return None
    
    def shutdown(self) -> bool:
        """Gracefully shutdown the authentication manager.
        
        Returns:
            True if shutdown successful, False otherwise
        """
        try:
            self.logger.info("Shutting down Google Auth Manager")
            
            # Save current tokens if available
            if self.token_info:
                self._save_tokens()
            
            # Clear sensitive data
            self.token_info = None
            
            # Health is managed by unified ReflectiveModule
            self.logger.info("Google Auth Manager shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(
                f"Error during auth manager shutdown: {e}",
                extra={"correlation_id": self.correlation_id, "error": str(e)}
            )
            return False