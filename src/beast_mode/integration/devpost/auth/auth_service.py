"""
Devpost authentication service implementation.

This module provides OAuth and API key authentication for Devpost API,
including token management, validation, and refresh capabilities.
"""

import asyncio
import base64
import hashlib
import json
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import logging
import random
import time

import aiohttp
from aiohttp import web
import keyring

from ..interfaces import AuthenticationServiceInterface
from ..models import AuthToken, AuthResult
from ....core.exceptions import AuthenticationError, NetworkError


logger = logging.getLogger(__name__)


class DevpostAuthService(AuthenticationServiceInterface):
    """
    Authentication service for Devpost API integration.
    
    Supports both OAuth 2.0 flow and API key authentication with secure
    token storage, automatic refresh capabilities, and robust error handling
    with exponential backoff retry logic.
    """
    
    # Devpost OAuth endpoints
    OAUTH_BASE_URL = "https://devpost.com/oauth"
    AUTHORIZE_URL = f"{OAUTH_BASE_URL}/authorize"
    TOKEN_URL = f"{OAUTH_BASE_URL}/token"
    
    # OAuth scopes
    DEFAULT_SCOPES = ["read", "write"]
    
    # Token storage keys
    TOKEN_STORAGE_KEY = "devpost_auth_token"
    REFRESH_TOKEN_KEY = "devpost_refresh_token"
    
    # Retry configuration
    MAX_RETRY_ATTEMPTS = 3
    BASE_RETRY_DELAY = 1.0  # seconds
    MAX_RETRY_DELAY = 60.0  # seconds
    RETRY_MULTIPLIER = 2.0
    JITTER_RANGE = 0.1  # 10% jitter
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW = 10
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_key: Optional[str] = None,
        redirect_uri: str = "http://localhost:8080/callback",
        scopes: Optional[List[str]] = None,
        max_retry_attempts: int = None,
        base_retry_delay: float = None
    ):
        """
        Initialize authentication service.
        
        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            api_key: API key for direct authentication
            redirect_uri: OAuth redirect URI
            scopes: OAuth scopes to request
            max_retry_attempts: Maximum number of retry attempts
            base_retry_delay: Base delay for exponential backoff
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.redirect_uri = redirect_uri
        self.scopes = scopes or self.DEFAULT_SCOPES
        
        # Retry configuration
        self.max_retry_attempts = max_retry_attempts or self.MAX_RETRY_ATTEMPTS
        self.base_retry_delay = base_retry_delay or self.BASE_RETRY_DELAY
        
        self._current_token: Optional[AuthToken] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_timestamps: List[float] = []
        self._auth_attempts: Dict[str, int] = {}
        
        # Load existing token from secure storage
        self._load_stored_token()
    
    async def authenticate(self) -> AuthResult:
        """
        Perform authentication flow with retry logic.
        
        Attempts OAuth first if credentials are available, falls back to API key.
        Implements exponential backoff for failed attempts.
        
        Returns:
            AuthResult with success status and token information
        """
        auth_method = "oauth" if (self.client_id and self.client_secret) else "api_key"
        
        return await self._retry_with_backoff(
            self._authenticate_internal,
            operation_name=f"{auth_method}_authentication",
            max_attempts=self.max_retry_attempts
        )
    
    async def _authenticate_internal(self) -> AuthResult:
        """Internal authentication method without retry logic."""
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                return AuthResult(
                    success=False,
                    error_message="Rate limit exceeded. Please wait before retrying.",
                    requires_user_action=True
                )
            
            # Try OAuth authentication first
            if self.client_id and self.client_secret:
                logger.info("Attempting OAuth authentication")
                return await self._oauth_authenticate()
            
            # Fall back to API key authentication
            elif self.api_key:
                logger.info("Attempting API key authentication")
                return await self._api_key_authenticate()
            
            else:
                return AuthResult(
                    success=False,
                    error_message="No authentication credentials provided",
                    requires_user_action=True
                )
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error during authentication: {e}")
            raise NetworkError(f"Network error during authentication: {str(e)}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    async def _oauth_authenticate(self) -> AuthResult:
        """
        Perform OAuth 2.0 authentication flow.
        
        Returns:
            AuthResult with OAuth token information
        """
        try:
            # Generate PKCE parameters for security
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            state = secrets.token_urlsafe(32)
            
            # Build authorization URL
            auth_params = {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "scope": " ".join(self.scopes),
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }
            
            auth_url = f"{self.AUTHORIZE_URL}?{urllib.parse.urlencode(auth_params)}"
            
            # Start local server to handle callback
            callback_result = await self._handle_oauth_callback(auth_url, state)
            
            if not callback_result["success"]:
                return AuthResult(
                    success=False,
                    error_message=callback_result["error"],
                    requires_user_action=True
                )
            
            # Exchange authorization code for access token
            token_result = await self._exchange_code_for_token(
                callback_result["code"],
                code_verifier
            )
            
            if token_result.success:
                self._current_token = token_result.token
                await self._store_token_securely(token_result.token)
            
            return token_result
            
        except Exception as e:
            logger.error(f"OAuth authentication failed: {e}")
            return AuthResult(
                success=False,
                error_message=f"OAuth authentication failed: {str(e)}"
            )
    
    async def _api_key_authenticate(self) -> AuthResult:
        """
        Perform API key authentication.
        
        Returns:
            AuthResult with API key token information
        """
        try:
            # Validate API key by making a test request
            if not await self._validate_api_key():
                return AuthResult(
                    success=False,
                    error_message="Invalid API key"
                )
            
            # Create token object for API key
            token = AuthToken(
                access_token=self.api_key,
                token_type="ApiKey",
                expires_at=None,  # API keys don't expire
                refresh_token=None,
                scope=" ".join(self.scopes)
            )
            
            self._current_token = token
            await self._store_token_securely(token)
            
            return AuthResult(
                success=True,
                token=token
            )
            
        except Exception as e:
            logger.error(f"API key authentication failed: {e}")
            return AuthResult(
                success=False,
                error_message=f"API key authentication failed: {str(e)}"
            )
    
    async def _validate_api_key(self) -> bool:
        """
        Validate API key by making a test request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            session = await self._get_session()
            headers = {
                "Authorization": f"ApiKey {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make a simple request to validate the key
            async with session.get(
                "https://devpost.com/api/v2/user/profile",
                headers=headers
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            True if authenticated and token is valid
        """
        if not self._current_token:
            return False
        
        # Check if token is expired
        if self._current_token.expires_at:
            if datetime.now() >= self._current_token.expires_at:
                return False
        
        return True
    
    def get_current_token(self) -> Optional[AuthToken]:
        """
        Get current authentication token.
        
        Returns:
            Current AuthToken or None if not authenticated
        """
        if self.is_authenticated():
            return self._current_token
        return None
    
    async def refresh_token(self) -> AuthToken:
        """
        Refresh authentication token with retry logic.
        
        Returns:
            New AuthToken
            
        Raises:
            AuthenticationError: If refresh fails
        """
        if not self._current_token or not self._current_token.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        return await self._retry_with_backoff(
            self._refresh_token_internal,
            operation_name="token_refresh",
            max_attempts=self.max_retry_attempts
        )
    
    async def _refresh_token_internal(self) -> AuthToken:
        """Internal token refresh method without retry logic."""
        try:
            session = await self._get_session()
            
            refresh_data = {
                "grant_type": "refresh_token",
                "refresh_token": self._current_token.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            async with session.post(
                self.TOKEN_URL, 
                data=refresh_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 401:
                    raise AuthenticationError("Refresh token is invalid or expired")
                elif response.status == 429:
                    raise NetworkError("Rate limited by Devpost API")
                elif response.status != 200:
                    error_text = await response.text()
                    raise AuthenticationError(f"Token refresh failed: {response.status} - {error_text}")
                
                token_data = await response.json()
                
                # Create new token
                expires_at = None
                if "expires_in" in token_data:
                    expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
                
                new_token = AuthToken(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "Bearer"),
                    expires_at=expires_at,
                    refresh_token=token_data.get("refresh_token", self._current_token.refresh_token),
                    scope=token_data.get("scope")
                )
                
                self._current_token = new_token
                await self._store_token_securely(new_token)
                
                logger.info("Token refreshed successfully")
                return new_token
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error during token refresh: {e}")
            raise NetworkError(f"Network error during token refresh: {str(e)}")
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def _handle_oauth_callback(self, auth_url: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback by starting local server.
        
        Args:
            auth_url: Authorization URL to display to user
            state: CSRF protection state parameter
            
        Returns:
            Dictionary with callback result
        """
        callback_result = {"success": False, "error": None, "code": None}
        
        async def handle_callback(request):
            nonlocal callback_result
            
            # Check for error in callback
            if "error" in request.query:
                callback_result["error"] = request.query.get("error_description", "Authorization failed")
                return web.Response(text="Authorization failed. You can close this window.")
            
            # Verify state parameter
            if request.query.get("state") != state:
                callback_result["error"] = "Invalid state parameter"
                return web.Response(text="Invalid state parameter. You can close this window.")
            
            # Get authorization code
            code = request.query.get("code")
            if not code:
                callback_result["error"] = "No authorization code received"
                return web.Response(text="No authorization code received. You can close this window.")
            
            callback_result["success"] = True
            callback_result["code"] = code
            
            return web.Response(text="Authorization successful! You can close this window.")
        
        # Create web application
        app = web.Application()
        app.router.add_get("/callback", handle_callback)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Parse redirect URI to get port
        from urllib.parse import urlparse
        parsed_uri = urlparse(self.redirect_uri)
        port = parsed_uri.port or 8080
        
        site = web.TCPSite(runner, "localhost", port)
        await site.start()
        
        try:
            # Display authorization URL to user
            print(f"\nPlease visit the following URL to authorize the application:")
            print(f"{auth_url}\n")
            print("Waiting for authorization...")
            
            # Wait for callback with timeout
            timeout = 300  # 5 minutes
            start_time = asyncio.get_event_loop().time()
            
            while not callback_result["success"] and not callback_result["error"]:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    callback_result["error"] = "Authorization timeout"
                    break
                await asyncio.sleep(1)
            
            return callback_result
            
        finally:
            await runner.cleanup()
    
    async def _exchange_code_for_token(self, code: str, code_verifier: str) -> AuthResult:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            code_verifier: PKCE code verifier
            
        Returns:
            AuthResult with token information
        """
        try:
            session = await self._get_session()
            
            token_data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code_verifier": code_verifier
            }
            
            async with session.post(self.TOKEN_URL, data=token_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return AuthResult(
                        success=False,
                        error_message=f"Token exchange failed: {error_text}"
                    )
                
                token_response = await response.json()
                
                # Create token object
                expires_at = None
                if "expires_in" in token_response:
                    expires_at = datetime.now() + timedelta(seconds=token_response["expires_in"])
                
                token = AuthToken(
                    access_token=token_response["access_token"],
                    token_type=token_response.get("token_type", "Bearer"),
                    expires_at=expires_at,
                    refresh_token=token_response.get("refresh_token"),
                    scope=token_response.get("scope")
                )
                
                return AuthResult(
                    success=True,
                    token=token
                )
                
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            return AuthResult(
                success=False,
                error_message=f"Token exchange failed: {str(e)}"
            )
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    def _load_stored_token(self) -> None:
        """Load token from secure storage."""
        try:
            token_json = keyring.get_password("devpost", self.TOKEN_STORAGE_KEY)
            if token_json:
                token_data = json.loads(token_json)
                
                # Parse expires_at if present
                expires_at = None
                if token_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(token_data["expires_at"])
                
                self._current_token = AuthToken(
                    access_token=token_data["access_token"],
                    token_type=token_data.get("token_type", "Bearer"),
                    expires_at=expires_at,
                    refresh_token=token_data.get("refresh_token"),
                    scope=token_data.get("scope")
                )
                
                logger.info("Loaded stored authentication token")
                
        except Exception as e:
            logger.warning(f"Failed to load stored token: {e}")
    
    async def _store_token_securely(self, token: AuthToken) -> None:
        """Store token in secure storage."""
        try:
            token_data = {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "refresh_token": token.refresh_token,
                "scope": token.scope
            }
            
            keyring.set_password(
                "devpost",
                self.TOKEN_STORAGE_KEY,
                json.dumps(token_data)
            )
            
            logger.info("Token stored securely")
            
        except Exception as e:
            logger.warning(f"Failed to store token securely: {e}")
    
    async def logout(self) -> None:
        """Clear authentication and remove stored tokens."""
        try:
            # Clear in-memory token
            self._current_token = None
            
            # Remove from secure storage
            keyring.delete_password("devpost", self.TOKEN_STORAGE_KEY)
            
            # Close session
            if self._session and not self._session.closed:
                await self._session.close()
            
            logger.info("Logged out successfully")
            
        except Exception as e:
            logger.warning(f"Logout cleanup failed: {e}")
    
    async def _retry_with_backoff(
        self,
        operation,
        operation_name: str,
        max_attempts: int = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with exponential backoff retry logic.
        
        Args:
            operation: Async function to execute
            operation_name: Name of operation for logging
            max_attempts: Maximum retry attempts
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result of successful operation
            
        Raises:
            AuthenticationError: If all retry attempts fail
        """
        max_attempts = max_attempts or self.max_retry_attempts
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                logger.debug(f"Attempting {operation_name} (attempt {attempt + 1}/{max_attempts})")
                result = await operation(*args, **kwargs)
                
                # Reset attempt counter on success
                if operation_name in self._auth_attempts:
                    del self._auth_attempts[operation_name]
                
                return result
                
            except (NetworkError, aiohttp.ClientError) as e:
                last_exception = e
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{max_attempts}): {e}")
                
                # Don't retry on the last attempt
                if attempt == max_attempts - 1:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = self._calculate_backoff_delay(attempt)
                logger.info(f"Retrying {operation_name} in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
                
            except AuthenticationError as e:
                # Don't retry authentication errors that require user action
                if "credentials" in str(e).lower() or "invalid" in str(e).lower():
                    logger.error(f"{operation_name} failed with non-retryable error: {e}")
                    raise e
                
                last_exception = e
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{max_attempts}): {e}")
                
                if attempt == max_attempts - 1:
                    break
                
                delay = self._calculate_backoff_delay(attempt)
                logger.info(f"Retrying {operation_name} in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
                
            except Exception as e:
                # Don't retry unexpected errors
                logger.error(f"{operation_name} failed with unexpected error: {e}")
                raise AuthenticationError(f"{operation_name} failed: {str(e)}")
        
        # Track failed attempts
        self._auth_attempts[operation_name] = self._auth_attempts.get(operation_name, 0) + 1
        
        # All attempts failed
        error_msg = f"{operation_name} failed after {max_attempts} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        
        logger.error(error_msg)
        raise AuthenticationError(error_msg)
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * (multiplier ^ attempt)
        delay = self.base_retry_delay * (self.RETRY_MULTIPLIER ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, self.MAX_RETRY_DELAY)
        
        # Add jitter to prevent thundering herd
        jitter = delay * self.JITTER_RANGE * (2 * random.random() - 1)
        delay += jitter
        
        return max(0, delay)
    
    def _check_rate_limit(self) -> bool:
        """
        Check if request is within rate limits.
        
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        
        # Remove old timestamps outside the window
        cutoff = now - self.RATE_LIMIT_WINDOW
        self._request_timestamps = [ts for ts in self._request_timestamps if ts > cutoff]
        
        # Check if we're under the limit
        if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_WINDOW:
            logger.warning("Rate limit exceeded")
            return False
        
        # Add current timestamp
        self._request_timestamps.append(now)
        return True
    
    def get_auth_stats(self) -> Dict[str, Any]:
        """
        Get authentication statistics for monitoring.
        
        Returns:
            Dictionary with authentication statistics
        """
        return {
            "is_authenticated": self.is_authenticated(),
            "token_type": self._current_token.token_type if self._current_token else None,
            "token_expires_at": self._current_token.expires_at.isoformat() if (
                self._current_token and self._current_token.expires_at
            ) else None,
            "failed_attempts": dict(self._auth_attempts),
            "recent_requests": len(self._request_timestamps),
            "rate_limit_window": self.RATE_LIMIT_WINDOW,
            "max_requests_per_window": self.MAX_REQUESTS_PER_WINDOW
        }
    
    async def validate_connection(self) -> bool:
        """
        Validate connection to Devpost API.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            if not self.is_authenticated():
                return False
            
            # Make a simple API call to validate connection
            session = await self._get_session()
            headers = self._get_auth_headers()
            
            async with session.get(
                "https://devpost.com/api/v2/user/profile",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.warning(f"Connection validation failed: {e}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary with authentication headers
        """
        if not self._current_token:
            return {}
        
        if self._current_token.token_type == "ApiKey":
            return {
                "Authorization": f"ApiKey {self._current_token.access_token}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "Authorization": f"{self._current_token.token_type} {self._current_token.access_token}",
                "Content-Type": "application/json"
            }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session and not self._session.closed:
            await self._session.close()