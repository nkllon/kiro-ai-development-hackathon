"""
Auth Service Services Services Services

This module was extracted from auth_service_services_services.py
as part of RM-DDD compliance refactoring.
"""

import json
import secrets
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from urllib.parse import urlencode, parse_qs, urlparse
import requests
from dataclasses import dataclass
from ..exceptions import DevPostAuthenticationError, DevPostAPIError
import sys
import os
from src.devpost_integration.reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
import logging
from ..api.client import DevPostAPIClient
from ..api.client import DevPostAPIClient
from ..api.client import DevPostAPIClient

class DevPostAuthService:
    """
    Production-ready authentication service for DevPost API.
    
    Supports both OAuth 2.0 and API key authentication methods.
    """
    OAUTH_BASE_URL = 'https://devpost.com/oauth'
    AUTHORIZATION_URL = f'{OAUTH_BASE_URL}/authorize'
    TOKEN_URL = f'{OAUTH_BASE_URL}/token'
    DEFAULT_SCOPES = ['read:projects', 'write:projects', 'read:user', 'write:user']

    def __init__(self, client_id: Optional[str]=None, client_secret: Optional[str]=None):
        """
        Initialize the authentication service.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = AuthCredentials()
        self.credentials_file = Path.home() / '.devpost' / 'credentials.json'
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load stored credentials from file"""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                self.credentials.access_token = data.get('access_token')
                self.credentials.refresh_token = data.get('refresh_token')
                self.credentials.api_key = data.get('api_key')
                self.credentials.token_type = data.get('token_type', 'Bearer')
                self.credentials.scope = data.get('scope')
                if data.get('expires_at'):
                    self.credentials.expires_at = datetime.fromisoformat(data['expires_at'])
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f'⚠️ Could not load credentials: {e}')
                self.credentials = AuthCredentials()

    def _save_credentials(self) -> None:
        """Save credentials to file"""
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        data = {'access_token': self.credentials.access_token, 'refresh_token': self.credentials.refresh_token, 'api_key': self.credentials.api_key, 'token_type': self.credentials.token_type, 'scope': self.credentials.scope, 'expires_at': self.credentials.expires_at.isoformat() if self.credentials.expires_at else None}
        with open(self.credentials_file, 'w') as f:
            json.dump(data, f, indent=2)
        self.credentials_file.chmod(384)

    def authenticate_with_api_key(self, api_key: str) -> bool:
        """
        Authenticate using API key.
        
        Args:
            api_key: DevPost API key
            
        Returns:
            True if authentication successful
        """
        try:
            from ..api.client import DevPostAPIClient
            client = DevPostAPIClient(api_key=api_key)
            if client.test_connection():
                self.credentials.api_key = api_key
                self.credentials.access_token = None
                self.credentials.refresh_token = None
                self._save_credentials()
                return True
            else:
                return False
        except Exception as e:
            raise DevPostAuthenticationError(f'API key authentication failed: {e}')

    def authenticate_with_oauth(self, scopes: Optional[list]=None, redirect_uri: str='http://localhost:8080/callback') -> str:
        """
        Start OAuth 2.0 authentication flow.
        
        Args:
            scopes: List of OAuth scopes to request
            redirect_uri: OAuth redirect URI
            
        Returns:
            Authorization URL for user to visit
        """
        if not self.client_id:
            raise DevPostAuthenticationError('OAuth client ID not configured')
        scopes = scopes or self.DEFAULT_SCOPES
        state = secrets.token_urlsafe(32)
        self._oauth_state = state
        self._redirect_uri = redirect_uri
        params = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': redirect_uri, 'scope': ' '.join(scopes), 'state': state}
        auth_url = f'{self.AUTHORIZATION_URL}?{urlencode(params)}'
        return auth_url

    def complete_oauth_flow(self, authorization_code: str, state: str) -> bool:
        """
        Complete OAuth 2.0 flow with authorization code.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            state: State parameter for verification
            
        Returns:
            True if authentication successful
        """
        if not hasattr(self, '_oauth_state') or state != self._oauth_state:
            raise DevPostAuthenticationError('Invalid state parameter')
        if not self.client_secret:
            raise DevPostAuthenticationError('OAuth client secret not configured')
        try:
            token_data = {'grant_type': 'authorization_code', 'client_id': self.client_id, 'client_secret': self.client_secret, 'code': authorization_code, 'redirect_uri': self._redirect_uri}
            response = requests.post(self.TOKEN_URL, data=token_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=30)
            if response.status_code != 200:
                raise DevPostAuthenticationError(f'Token exchange failed: {response.text}')
            token_response = response.json()
            self.credentials.access_token = token_response['access_token']
            self.credentials.refresh_token = token_response.get('refresh_token')
            self.credentials.token_type = token_response.get('token_type', 'Bearer')
            self.credentials.scope = token_response.get('scope')
            expires_in = token_response.get('expires_in', 3600)
            self.credentials.expires_at = datetime.now() + timedelta(seconds=expires_in)
            delattr(self, '_oauth_state')
            delattr(self, '_redirect_uri')
            self._save_credentials()
            return True
        except requests.RequestException as e:
            raise DevPostAuthenticationError(f'OAuth token exchange failed: {e}')

    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token.
        
        Returns:
            True if refresh successful
        """
        if not self.credentials.refresh_token:
            raise DevPostAuthenticationError('No refresh token available')
        if not self.client_secret:
            raise DevPostAuthenticationError('OAuth client secret not configured')
        try:
            refresh_data = {'grant_type': 'refresh_token', 'client_id': self.client_id, 'client_secret': self.client_secret, 'refresh_token': self.credentials.refresh_token}
            response = requests.post(self.TOKEN_URL, data=refresh_data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=30)
            if response.status_code != 200:
                raise DevPostAuthenticationError(f'Token refresh failed: {response.text}')
            token_response = response.json()
            self.credentials.access_token = token_response['access_token']
            self.credentials.refresh_token = token_response.get('refresh_token', self.credentials.refresh_token)
            expires_in = token_response.get('expires_in', 3600)
            self.credentials.expires_at = datetime.now() + timedelta(seconds=expires_in)
            self._save_credentials()
            return True
        except requests.RequestException as e:
            raise DevPostAuthenticationError(f'Token refresh failed: {e}')

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            True if authenticated and token is valid
        """
        if not self.credentials.access_token and (not self.credentials.api_key):
            return False
        if self.credentials.expires_at and datetime.now() >= self.credentials.expires_at:
            if self.credentials.refresh_token:
                try:
                    return self.refresh_access_token()
                except DevPostAuthenticationError:
                    return False
            return False
        return True

    def get_credentials(self) -> AuthCredentials:
        """
        Get current authentication credentials.
        
        Returns:
            AuthCredentials object
        """
        return self.credentials

    def clear_credentials(self) -> None:
        """Clear stored credentials"""
        self.credentials = AuthCredentials()
        if self.credentials_file.exists():
            self.credentials_file.unlink()

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of authentication headers
        """
        if not self.is_authenticated():
            raise DevPostAuthenticationError('Not authenticated')
        if self.credentials.access_token:
            return {'Authorization': f'{self.credentials.token_type} {self.credentials.access_token}'}
        elif self.credentials.api_key:
            return {'X-API-Key': self.credentials.api_key}
        else:
            raise DevPostAuthenticationError('No valid credentials available')

    def interactive_oauth_flow(self) -> bool:
        """
        Perform interactive OAuth flow with automatic browser opening.
        
        Returns:
            True if authentication successful
        """
        try:
            auth_url = self.authenticate_with_oauth()
            print(f'🌐 Opening browser for OAuth authentication...')
            print(f"🔗 If browser doesn't open, visit: {auth_url}")
            webbrowser.open(auth_url)
            print("\n📋 After authorizing, you'll be redirected to a page with an error.")
            print("🔍 Look for the 'code' parameter in the URL and paste it here:")
            authorization_code = input('Authorization code: ').strip()
            print("🔍 Also look for the 'state' parameter in the URL:")
            state = input('State: ').strip()
            return self.complete_oauth_flow(authorization_code, state)
        except KeyboardInterrupt:
            print('\n❌ OAuth flow cancelled by user')
            return False
        except Exception as e:
            print(f'❌ OAuth flow failed: {e}')
            return False

    def setup_oauth_credentials(self, client_id: str, client_secret: str) -> None:
        """
        Setup OAuth credentials for the service.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        config_data = {'client_id': client_id, 'client_secret': client_secret}
        config_file = Path.home() / '.devpost' / 'config.json'
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config_file, f, indent=2)
        config_file.chmod(384)
        print('✅ OAuth credentials configured successfully')

    def get_authentication_status(self) -> Dict[str, Any]:
        """
        Get detailed authentication status.
        
        Returns:
            Dictionary with authentication status information
        """
        status = {'authenticated': self.is_authenticated(), 'method': None, 'expires_at': None, 'scope': None, 'credentials_file': str(self.credentials_file)}
        if self.credentials.access_token:
            status['method'] = 'oauth'
            status['expires_at'] = self.credentials.expires_at.isoformat() if self.credentials.expires_at else None
            status['scope'] = self.credentials.scope
        elif self.credentials.api_key:
            status['method'] = 'api_key'
        return status

class DevpostAuthService(ReflectiveModule):
    """DevpostAuthService with RM-DDD compliance"""

    def __init__(self):
        """Initialize DevPost auth service"""
        super().__init__(module_id='devpostauthservice', version='1.0.0')
        register_module(self)
        self._logger = logging.getLogger(f'{__name__}.DevpostAuthService')
        self._logger.info('DevpostAuthService initialized with RM-DDD compliance')

    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {'module_id': 'devpostauthservice', 'version': '1.0.0', 'description': 'DevpostAuthService implementation'}

    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [ModuleCapability.CORE_FUNCTIONALITY]

    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ['reflective_module']

    def check_health(self) -> ModuleHealth:
        """Perform health check"""
        return ModuleHealth(module_id='devpostauthservice', status=ModuleStatus.HEALTHY, health_score=1.0, issues=[], capabilities=self.get_capabilities(), dependencies=self.get_dependencies(), metrics={}, last_check=datetime.now())

    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration"""
        return {}

    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration"""
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        return {}

    def reset_metrics(self) -> None:
        """Reset module metrics"""
        pass
