"""
Base CA plugin implementation for MSP SSL Chaos Tamer

Provides concrete base implementation of CAPlugin interface with common
functionality, plugin discovery, lifecycle management, and testing utilities.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from abc import abstractmethod

from ..core.interfaces import (
    CAPlugin, CertificateRequest, CertificateStatus, RevocationStatus,
    AuthenticationError, CertificateRequestError, CertificateRenewalError,
    CertificateRevocationError, CertificateStatusError, CertificateDownloadError
)


class BaseCAPlugin(CAPlugin):
    """
    Base implementation of CA plugin with common functionality
    
    Provides rate limiting, retry logic, authentication management,
    and standardized error handling for all CA plugins.
    """
    
    def __init__(self, ca_name: str, config: Dict[str, Any]):
        super().__init__(ca_name, config)
        
        # Rate limiting
        self.rate_limit_requests = config.get("rate_limit_requests", 100)
        self.rate_limit_window = config.get("rate_limit_window", 3600)  # 1 hour
        self._request_timestamps: List[float] = []
        
        # Retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.retry_backoff = config.get("retry_backoff", 2.0)
        
        # Authentication state
        self._authenticated = False
        self._auth_expires_at: Optional[datetime] = None
        self._auth_token: Optional[str] = None
        
        # Plugin metadata
        self.plugin_version = config.get("version", "1.0.0")
        self.supported_features = config.get("supported_features", [
            "certificate_request", "certificate_renewal", "certificate_revocation"
        ])
        
        self.logger.info(f"Base CA plugin initialized: {ca_name}")
    
    def _check_rate_limit(self) -> bool:
        """
        Check if request is within rate limits
        
        Returns:
            bool: True if request allowed, False if rate limited
        """
        now = time.time()
        
        # Remove old timestamps outside the window
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if now - ts < self.rate_limit_window
        ]
        
        # Check if we're at the limit
        if len(self._request_timestamps) >= self.rate_limit_requests:
            self.logger.warning(f"Rate limit exceeded for {self.ca_name}")
            return False
        
        # Add current timestamp
        self._request_timestamps.append(now)
        return True
    
    def _retry_with_backoff(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute operation with exponential backoff retry
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for {self.ca_name}: {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= self.retry_backoff
                else:
                    self.logger.error(
                        f"All {self.max_retries + 1} attempts failed for {self.ca_name}: {e}"
                    )
        
        raise last_exception
    
    def _ensure_authenticated(self) -> bool:
        """
        Ensure plugin is authenticated, re-authenticate if needed
        
        Returns:
            bool: True if authenticated successfully
        """
        # Check if authentication is still valid
        if (self._authenticated and self._auth_expires_at and 
            datetime.utcnow() < self._auth_expires_at):
            return True
        
        # Re-authenticate if needed
        if not self._authenticated or (self._auth_expires_at and 
                                     datetime.utcnow() >= self._auth_expires_at):
            self.logger.info(f"Re-authenticating with {self.ca_name}")
            
            # Get credentials from config (in production, these would be encrypted)
            credentials = self.config.get("credentials", {})
            if not credentials:
                self.logger.error(f"No credentials configured for {self.ca_name}")
                return False
            
            try:
                return self.authenticate(credentials)
            except Exception as e:
                self.logger.error(f"Re-authentication failed for {self.ca_name}: {e}")
                return False
        
        return self._authenticated
    
    def _validate_certificate_request(self, request: CertificateRequest) -> bool:
        """
        Validate certificate request before processing
        
        Args:
            request: Certificate request to validate
            
        Returns:
            bool: True if request is valid
        """
        if not request.domain:
            self.logger.error("Certificate request missing domain")
            return False
        
        if not request.client_id:
            self.logger.error("Certificate request missing client_id")
            return False
        
        if request.ca_provider != self.ca_name:
            self.logger.error(
                f"Certificate request CA provider mismatch: "
                f"expected {self.ca_name}, got {request.ca_provider}"
            )
            return False
        
        return True
    
    # Abstract methods that must be implemented by concrete plugins
    @abstractmethod
    def _authenticate_impl(self, credentials: Dict[str, str]) -> bool:
        """
        Concrete authentication implementation
        
        Args:
            credentials: CA-specific authentication credentials
            
        Returns:
            bool: True if authentication successful
        """
        pass
    
    @abstractmethod
    def _request_certificate_impl(self, request: CertificateRequest) -> str:
        """
        Concrete certificate request implementation
        
        Args:
            request: Certificate request details
            
        Returns:
            str: Certificate ID for tracking
        """
        pass
    
    @abstractmethod
    def _renew_certificate_impl(self, certificate_id: str) -> str:
        """
        Concrete certificate renewal implementation
        
        Args:
            certificate_id: ID of certificate to renew
            
        Returns:
            str: New certificate ID
        """
        pass
    
    @abstractmethod
    def _revoke_certificate_impl(self, certificate_id: str, reason: str) -> RevocationStatus:
        """
        Concrete certificate revocation implementation
        
        Args:
            certificate_id: ID of certificate to revoke
            reason: Reason for revocation
            
        Returns:
            RevocationStatus: Revocation status information
        """
        pass
    
    @abstractmethod
    def _get_certificate_status_impl(self, certificate_id: str) -> CertificateStatus:
        """
        Concrete certificate status implementation
        
        Args:
            certificate_id: ID of certificate to check
            
        Returns:
            CertificateStatus: Current certificate status
        """
        pass
    
    @abstractmethod
    def _download_certificate_impl(self, certificate_id: str) -> Dict[str, str]:
        """
        Concrete certificate download implementation
        
        Args:
            certificate_id: ID of certificate to download
            
        Returns:
            Dict containing certificate, chain, and private key
        """
        pass
    
    # CAPlugin interface implementation with common functionality
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with the Certificate Authority
        
        Args:
            credentials: CA-specific authentication credentials
            
        Returns:
            bool: True if authentication successful
        """
        try:
            self.logger.info(f"Authenticating with {self.ca_name}")
            
            # Call concrete implementation
            success = self._authenticate_impl(credentials)
            
            if success:
                self._authenticated = True
                # Set authentication expiry (default 1 hour)
                auth_duration = self.config.get("auth_duration_hours", 1)
                self._auth_expires_at = datetime.utcnow() + timedelta(hours=auth_duration)
                
                self.logger.info(f"Authentication successful for {self.ca_name}")
            else:
                self._authenticated = False
                self._auth_expires_at = None
                self.logger.error(f"Authentication failed for {self.ca_name}")
            
            return success
            
        except Exception as e:
            self._authenticated = False
            self._auth_expires_at = None
            self.logger.error(f"Authentication error for {self.ca_name}: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def request_certificate(self, request: CertificateRequest) -> str:
        """
        Request a new certificate from the CA
        
        Args:
            request: Certificate request details
            
        Returns:
            str: Certificate ID for tracking
        """
        # Validate request
        if not self._validate_certificate_request(request):
            raise CertificateRequestError("Invalid certificate request")
        
        # Check rate limits
        if not self._check_rate_limit():
            raise CertificateRequestError("Rate limit exceeded")
        
        # Ensure authentication
        if not self._ensure_authenticated():
            raise AuthenticationError("Authentication required")
        
        try:
            self.logger.info(f"Requesting certificate for {request.domain} from {self.ca_name}")
            
            # Execute with retry logic
            certificate_id = self._retry_with_backoff(
                self._request_certificate_impl, request
            )
            
            self.logger.info(f"Certificate requested successfully: {certificate_id}")
            return certificate_id
            
        except Exception as e:
            self.logger.error(f"Certificate request failed for {request.domain}: {e}")
            raise CertificateRequestError(f"Certificate request failed: {e}")
    
    def renew_certificate(self, certificate_id: str) -> str:
        """
        Renew an existing certificate
        
        Args:
            certificate_id: ID of certificate to renew
            
        Returns:
            str: New certificate ID
        """
        if not certificate_id:
            raise CertificateRenewalError("Certificate ID is required")
        
        # Check rate limits
        if not self._check_rate_limit():
            raise CertificateRenewalError("Rate limit exceeded")
        
        # Ensure authentication
        if not self._ensure_authenticated():
            raise AuthenticationError("Authentication required")
        
        try:
            self.logger.info(f"Renewing certificate {certificate_id} with {self.ca_name}")
            
            # Execute with retry logic
            new_certificate_id = self._retry_with_backoff(
                self._renew_certificate_impl, certificate_id
            )
            
            self.logger.info(f"Certificate renewed successfully: {new_certificate_id}")
            return new_certificate_id
            
        except Exception as e:
            self.logger.error(f"Certificate renewal failed for {certificate_id}: {e}")
            raise CertificateRenewalError(f"Certificate renewal failed: {e}")
    
    def revoke_certificate(self, certificate_id: str, reason: str = "unspecified") -> RevocationStatus:
        """
        Revoke a certificate
        
        Args:
            certificate_id: ID of certificate to revoke
            reason: Reason for revocation
            
        Returns:
            RevocationStatus: Revocation status information
        """
        if not certificate_id:
            raise CertificateRevocationError("Certificate ID is required")
        
        # Check rate limits
        if not self._check_rate_limit():
            raise CertificateRevocationError("Rate limit exceeded")
        
        # Ensure authentication
        if not self._ensure_authenticated():
            raise AuthenticationError("Authentication required")
        
        try:
            self.logger.info(f"Revoking certificate {certificate_id} with {self.ca_name}")
            
            # Execute with retry logic
            revocation_status = self._retry_with_backoff(
                self._revoke_certificate_impl, certificate_id, reason
            )
            
            self.logger.info(f"Certificate revoked successfully: {certificate_id}")
            return revocation_status
            
        except Exception as e:
            self.logger.error(f"Certificate revocation failed for {certificate_id}: {e}")
            raise CertificateRevocationError(f"Certificate revocation failed: {e}")
    
    def get_certificate_status(self, certificate_id: str) -> CertificateStatus:
        """
        Get current status of a certificate
        
        Args:
            certificate_id: ID of certificate to check
            
        Returns:
            CertificateStatus: Current certificate status
        """
        if not certificate_id:
            raise CertificateStatusError("Certificate ID is required")
        
        # Check rate limits
        if not self._check_rate_limit():
            raise CertificateStatusError("Rate limit exceeded")
        
        # Ensure authentication
        if not self._ensure_authenticated():
            raise AuthenticationError("Authentication required")
        
        try:
            self.logger.debug(f"Checking certificate status {certificate_id} with {self.ca_name}")
            
            # Execute with retry logic
            status = self._retry_with_backoff(
                self._get_certificate_status_impl, certificate_id
            )
            
            return status
            
        except Exception as e:
            self.logger.error(f"Certificate status check failed for {certificate_id}: {e}")
            raise CertificateStatusError(f"Certificate status check failed: {e}")
    
    def download_certificate(self, certificate_id: str) -> Dict[str, str]:
        """
        Download certificate files
        
        Args:
            certificate_id: ID of certificate to download
            
        Returns:
            Dict containing certificate, chain, and private key
        """
        if not certificate_id:
            raise CertificateDownloadError("Certificate ID is required")
        
        # Check rate limits
        if not self._check_rate_limit():
            raise CertificateDownloadError("Rate limit exceeded")
        
        # Ensure authentication
        if not self._ensure_authenticated():
            raise AuthenticationError("Authentication required")
        
        try:
            self.logger.info(f"Downloading certificate {certificate_id} from {self.ca_name}")
            
            # Execute with retry logic
            certificate_data = self._retry_with_backoff(
                self._download_certificate_impl, certificate_id
            )
            
            self.logger.info(f"Certificate downloaded successfully: {certificate_id}")
            return certificate_data
            
        except Exception as e:
            self.logger.error(f"Certificate download failed for {certificate_id}: {e}")
            raise CertificateDownloadError(f"Certificate download failed: {e}")
    
    # Enhanced plugin information
    def get_ca_info(self) -> Dict[str, Any]:
        """Get comprehensive information about this CA plugin"""
        return {
            "ca_name": self.ca_name,
            "plugin_version": self.plugin_version,
            "supported_features": self.supported_features,
            "rate_limits": {
                "requests_per_window": self.rate_limit_requests,
                "window_seconds": self.rate_limit_window,
                "current_usage": len(self._request_timestamps)
            },
            "authentication": {
                "authenticated": self._authenticated,
                "expires_at": self._auth_expires_at.isoformat() if self._auth_expires_at else None
            },
            "retry_config": {
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "retry_backoff": self.retry_backoff
            }
        }
    
    def get_supported_features(self) -> List[str]:
        """Get list of features supported by this CA"""
        return self.supported_features.copy()
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get CA-specific rate limits"""
        return {
            "requests_per_window": self.rate_limit_requests,
            "window_seconds": self.rate_limit_window,
            "current_usage": len(self._request_timestamps),
            "remaining_requests": max(0, self.rate_limit_requests - len(self._request_timestamps))
        }
    
    def is_healthy(self) -> bool:
        """Check if plugin is healthy and operational"""
        try:
            # Check authentication status
            if not self._authenticated:
                return False
            
            # Check if authentication is expired
            if (self._auth_expires_at and 
                datetime.utcnow() >= self._auth_expires_at):
                return False
            
            return True
            
        except Exception:
            return False
    
    # ReflectiveModule enhancements
    def get_health_status(self) -> Dict[str, Any]:
        """Get enhanced CA plugin health status"""
        base_health = super().get_health_status()
        
        # Add CA-specific health information
        base_health.update({
            "authenticated": self._authenticated,
            "auth_expires_at": self._auth_expires_at.isoformat() if self._auth_expires_at else None,
            "rate_limit_usage": len(self._request_timestamps),
            "rate_limit_capacity": self.rate_limit_requests,
            "is_healthy": self.is_healthy()
        })
        
        return base_health