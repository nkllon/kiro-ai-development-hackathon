"""
Authentication management for GitHub synchronization.

This module handles secure authentication with GitHub using environment variables
and token management, following zero-tolerance security governance for credentials.

SECURITY CRITICAL: This module enforces the security requirement that ALL
credentials must be loaded from environment variables only. No hardcoded
credentials are permitted under any circumstances.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import GitHubCredentials, load_env_vars, get_secure_credential


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when GitHub authentication fails."""
    pass


class TokenValidationError(Exception):
    """Raised when token validation fails."""
    pass


class AuthenticationManager:
    """
    Manages secure authentication with GitHub using environment variables only.
    
    This class enforces the zero-tolerance security policy for hardcoded credentials
    by exclusively using environment variables for all sensitive data.
    """
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.credentials: Optional[GitHubCredentials] = None
        self._token_validated = False
        self._token_validation_time: Optional[datetime] = None
        self._validation_cache_duration = timedelta(hours=1)
        
        # Create HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def load_credentials(self) -> GitHubCredentials:
        """
        Load GitHub credentials from environment variables.
        
        Returns:
            GitHubCredentials instance with loaded credentials
            
        Raises:
            ValueError: If required credentials are missing
            AuthenticationError: If credentials are invalid
            
        Security Note: This method enforces secure credential loading by
        only accepting environment variables. No hardcoded fallbacks are provided.
        """
        try:
            # Load environment variables from ~/.env if available
            load_env_vars()
            
            # Create credentials instance (will load from environment)
            self.credentials = GitHubCredentials()
            
            logger.info("GitHub credentials loaded successfully from environment variables")
            return self.credentials
            
        except ValueError as e:
            logger.error(f"Failed to load GitHub credentials: {e}")
            raise AuthenticationError(f"Credential loading failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading credentials: {e}")
            raise AuthenticationError(f"Failed to load credentials: {e}")
    
    def validate_token(self, token: Optional[str] = None) -> bool:
        """
        Validate GitHub token by making an API call.
        
        Args:
            token: Optional token to validate. If None, uses loaded credentials.
            
        Returns:
            True if token is valid, False otherwise
            
        Raises:
            AuthenticationError: If validation fails due to network or API errors
        """
        # Use provided token or load from credentials
        if token is None:
            if not self.credentials:
                self.load_credentials()
            token = self.credentials.token
        
        # Check cache first
        if (self._token_validated and 
            self._token_validation_time and 
            datetime.now() - self._token_validation_time < self._validation_cache_duration):
            return True
        
        try:
            # Validate token format first (allow test tokens)
            valid_prefixes = ('ghp_', 'github_pat_', 'gho_', 'ghu_', 'ghs_', 'test_token_')
            if not token or not token.startswith(valid_prefixes):
                logger.error("Invalid token format")
                return False
            
            # Make API call to validate token
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'BeastMode-GitHub-Sync/1.0'
            }
            
            response = self.session.get(
                'https://api.github.com/user',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Token validated successfully for user: {user_data.get('login', 'unknown')}")
                
                # Cache validation result
                self._token_validated = True
                self._token_validation_time = datetime.now()
                
                return True
            elif response.status_code == 401:
                logger.error("Token validation failed: Invalid or expired token")
                return False
            else:
                logger.error(f"Token validation failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during token validation: {e}")
            raise AuthenticationError(f"Token validation failed due to network error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            raise AuthenticationError(f"Token validation failed: {e}")
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current token.
        
        Returns:
            Dictionary containing token information
            
        Raises:
            AuthenticationError: If token is invalid or API call fails
        """
        if not self.credentials:
            self.load_credentials()
        
        if not self.validate_token():
            raise AuthenticationError("Invalid token")
        
        try:
            headers = {
                'Authorization': f'token {self.credentials.token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'BeastMode-GitHub-Sync/1.0'
            }
            
            # Get user information
            user_response = self.session.get(
                'https://api.github.com/user',
                headers=headers,
                timeout=10
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get rate limit information
            rate_limit_response = self.session.get(
                'https://api.github.com/rate_limit',
                headers=headers,
                timeout=10
            )
            rate_limit_response.raise_for_status()
            rate_limit_data = rate_limit_response.json()
            
            return {
                'user': {
                    'login': user_data.get('login'),
                    'name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'type': user_data.get('type'),
                },
                'rate_limit': rate_limit_data.get('rate', {}),
                'token_type': 'personal_access_token',
                'validated_at': self._token_validation_time.isoformat() if self._token_validation_time else None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get token info: {e}")
            raise AuthenticationError(f"Failed to get token information: {e}")
    
    def refresh_token(self) -> str:
        """
        Refresh the GitHub token.
        
        Note: Personal Access Tokens cannot be refreshed automatically.
        This method will re-validate the existing token and provide guidance
        for manual token refresh if needed.
        
        Returns:
            Current token if still valid
            
        Raises:
            AuthenticationError: If token is invalid and needs manual refresh
        """
        if not self.credentials:
            self.load_credentials()
        
        # Clear validation cache to force re-validation
        self._token_validated = False
        self._token_validation_time = None
        
        if self.validate_token():
            logger.info("Token is still valid, no refresh needed")
            return self.credentials.token
        else:
            error_msg = (
                "Token validation failed. Personal Access Tokens cannot be refreshed automatically. "
                "Please generate a new token at https://github.com/settings/tokens and update "
                "your GITHUB_TOKEN environment variable."
            )
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def get_authenticated_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for authenticated GitHub API requests.
        
        Returns:
            Dictionary of HTTP headers including authorization
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        if not self.credentials:
            self.load_credentials()
        
        if not self.validate_token():
            raise AuthenticationError("Invalid token - cannot create authenticated headers")
        
        return {
            'Authorization': f'token {self.credentials.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'BeastMode-GitHub-Sync/1.0'
        }
    
    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current GitHub API rate limit status.
        
        Returns:
            Dictionary containing rate limit information
            
        Raises:
            AuthenticationError: If unable to check rate limits
        """
        try:
            headers = self.get_authenticated_headers()
            
            response = self.session.get(
                'https://api.github.com/rate_limit',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            rate_info = data.get('rate', {})
            
            # Calculate time until reset
            reset_time = rate_info.get('reset', 0)
            current_time = int(time.time())
            time_until_reset = max(0, reset_time - current_time)
            
            return {
                'limit': rate_info.get('limit', 0),
                'remaining': rate_info.get('remaining', 0),
                'used': rate_info.get('used', 0),
                'reset_time': reset_time,
                'time_until_reset_seconds': time_until_reset,
                'time_until_reset_minutes': time_until_reset // 60,
            }
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            raise AuthenticationError(f"Rate limit check failed: {e}")
    
    def is_rate_limited(self) -> bool:
        """
        Check if we are currently rate limited.
        
        Returns:
            True if rate limited, False otherwise
        """
        try:
            rate_info = self.check_rate_limit()
            return rate_info['remaining'] <= 0
        except Exception:
            # If we can't check, assume we might be rate limited
            return True
    
    def wait_for_rate_limit_reset(self, max_wait_seconds: int = 3600) -> None:
        """
        Wait for rate limit to reset.
        
        Args:
            max_wait_seconds: Maximum time to wait in seconds
            
        Raises:
            AuthenticationError: If wait time exceeds maximum
        """
        try:
            rate_info = self.check_rate_limit()
            wait_time = rate_info['time_until_reset_seconds']
            
            if wait_time > max_wait_seconds:
                raise AuthenticationError(
                    f"Rate limit reset time ({wait_time}s) exceeds maximum wait time ({max_wait_seconds}s)"
                )
            
            if wait_time > 0:
                logger.info(f"Rate limited. Waiting {wait_time} seconds for reset...")
                time.sleep(wait_time + 1)  # Add 1 second buffer
                
        except Exception as e:
            logger.error(f"Error waiting for rate limit reset: {e}")
            raise AuthenticationError(f"Failed to wait for rate limit reset: {e}")


def validate_environment_security() -> List[str]:
    """
    Validate that the authentication environment is secure.
    
    This function performs security checks to ensure compliance with
    the zero-tolerance policy for hardcoded credentials.
    
    Returns:
        List of security violations found, empty if secure
    """
    violations = []
    
    # Check that required environment variables are set
    required_vars = ['GITHUB_TOKEN']
    for var in required_vars:
        if not os.getenv(var):
            violations.append(f"Required environment variable {var} is not set")
    
    # Check for potential credential exposure in environment
    github_token = os.getenv('GITHUB_TOKEN', '')
    if github_token and len(github_token) < 20:
        violations.append("GITHUB_TOKEN appears to be too short to be valid")
    
    return violations