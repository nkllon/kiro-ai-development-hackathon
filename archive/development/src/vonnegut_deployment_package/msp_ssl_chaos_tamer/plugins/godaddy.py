"""
GoDaddy API plugin for MSP SSL Chaos Tamer

Implements GoDaddy REST API client for certificate management with
authentication, certificate request, renewal, and revocation workflows.
"""

import logging
import time
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin

from .base import BaseCAPlugin
from ..core.interfaces import (
    CertificateRequest, CertificateStatus, RevocationStatus,
    AuthenticationError, CertificateRequestError, CertificateRenewalError,
    CertificateRevocationError, CertificateStatusError, CertificateDownloadError
)


class GoDaddyAPIPlugin(BaseCAPlugin):
    """
    GoDaddy API plugin implementation
    
    Provides GoDaddy REST API integration for certificate management
    with support for DV, OV, and EV certificates.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        config.setdefault("ca_name", "godaddy")
        config.setdefault("rate_limit_requests", 60)  # GoDaddy allows 60/minute
        config.setdefault("rate_limit_window", 60)
        config.setdefault("max_retries", 3)
        config.setdefault("supported_features", [
            "certificate_request", "certificate_renewal", "certificate_revocation",
            "domain_validation", "organization_validation", "extended_validation"
        ])
        
        super().__init__("godaddy", config)
        
        # GoDaddy API configuration
        self.api_base_url = config.get(
            "api_base_url", 
            "https://api.godaddy.com"
        )
        self.api_version = config.get("api_version", "v1")
        
        # Authentication
        self._api_key: Optional[str] = None
        self._api_secret: Optional[str] = None
        self._auth_header: Optional[str] = None
        
        # Certificate storage
        self._certificates: Dict[str, Dict[str, Any]] = {}
        
        # Request session
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "MSP-SSL-Chaos-Tamer/1.0"
        })
        
        self.logger.info("GoDaddy API plugin initialized")
    
    def _make_api_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated API request to GoDaddy
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: API response
        """
        if not self._auth_header:
            raise AuthenticationError("GoDaddy API not authenticated")
        
        url = urljoin(f"{self.api_base_url}/{self.api_version}/", endpoint.lstrip("/"))
        
        # Add authentication header
        headers = kwargs.get("headers", {})
        headers["Authorization"] = self._auth_header
        kwargs["headers"] = headers
        
        # Add timeout
        kwargs.setdefault("timeout", 30)
        
        try:
            response = self._session.request(method, url, **kwargs)
            
            # Log request for debugging
            self.logger.debug(f"GoDaddy API {method} {url} -> {response.status_code}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GoDaddy API request failed: {e}")
            raise CertificateRequestError(f"API request failed: {e}")
    
    def _authenticate_impl(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with GoDaddy API
        
        Args:
            credentials: Must contain 'api_key' and 'api_secret'
            
        Returns:
            bool: True if authentication successful
        """
        try:
            api_key = credentials.get("api_key")
            api_secret = credentials.get("api_secret")
            
            if not api_key or not api_secret:
                self.logger.error("GoDaddy API key and secret are required")
                return False
            
            self._api_key = api_key
            self._api_secret = api_secret
            self._auth_header = f"sso-key {api_key}:{api_secret}"
            
            # Test authentication by making a simple API call
            response = self._make_api_request("GET", "/certificates")
            
            if response.status_code == 200:
                self.logger.info("GoDaddy API authentication successful")
                return True
            elif response.status_code == 401:
                self.logger.error("GoDaddy API authentication failed: Invalid credentials")
                return False
            else:
                self.logger.error(f"GoDaddy API authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"GoDaddy authentication error: {e}")
            return False
    
    def _request_certificate_impl(self, request: CertificateRequest) -> str:
        """
        Request certificate from GoDaddy
        
        Args:
            request: Certificate request details
            
        Returns:
            str: Certificate ID for tracking
        """
        domain = request.domain
        certificate_id = f"gd_{domain}_{int(time.time())}"
        
        try:
            self.logger.info(f"Requesting GoDaddy certificate for {domain}")
            
            # Prepare certificate request payload
            cert_request = {
                "type": request.metadata.get("certificate_type", "DV_SSL"),
                "commonName": domain,
                "organization": request.metadata.get("organization", ""),
                "organizationalUnit": request.metadata.get("organizational_unit", ""),
                "city": request.metadata.get("city", ""),
                "state": request.metadata.get("state", ""),
                "country": request.metadata.get("country", "US"),
                "email": request.metadata.get("email", ""),
                "validityPeriod": request.validity_days or 365,
                "subjectAlternativeNames": request.metadata.get("san_domains", [])
            }
            
            # Make certificate request
            response = self._make_api_request(
                "POST", 
                "/certificates",
                json=cert_request
            )
            
            if response.status_code == 201:
                cert_data = response.json()
                
                # Store certificate data
                self._certificates[certificate_id] = {
                    "domain": domain,
                    "godaddy_cert_id": cert_data.get("certificateId"),
                    "status": "pending",
                    "type": cert_request["type"],
                    "requested_at": datetime.utcnow(),
                    "validity_period": cert_request["validityPeriod"],
                    "request_data": cert_request,
                    "response_data": cert_data
                }
                
                self.logger.info(f"GoDaddy certificate requested: {certificate_id}")
                return certificate_id
                
            else:
                error_msg = f"GoDaddy certificate request failed: {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                
                raise CertificateRequestError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GoDaddy certificate request failed for {domain}: {e}")
            raise CertificateRequestError(f"GoDaddy certificate request failed: {e}")
    
    def _renew_certificate_impl(self, certificate_id: str) -> str:
        """
        Renew GoDaddy certificate
        
        Args:
            certificate_id: ID of certificate to renew
            
        Returns:
            str: New certificate ID
        """
        if certificate_id not in self._certificates:
            raise CertificateRenewalError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        godaddy_cert_id = cert_data.get("godaddy_cert_id")
        
        if not godaddy_cert_id:
            raise CertificateRenewalError(f"GoDaddy certificate ID not found for {certificate_id}")
        
        try:
            self.logger.info(f"Renewing GoDaddy certificate {certificate_id}")
            
            # Make renewal request
            response = self._make_api_request(
                "POST",
                f"/certificates/{godaddy_cert_id}/renew"
            )
            
            if response.status_code == 200:
                renewal_data = response.json()
                
                # Create new certificate entry for renewal
                new_certificate_id = f"gd_renewal_{certificate_id}_{int(time.time())}"
                
                self._certificates[new_certificate_id] = {
                    "domain": cert_data["domain"],
                    "godaddy_cert_id": renewal_data.get("certificateId", godaddy_cert_id),
                    "status": "pending",
                    "type": cert_data["type"],
                    "requested_at": datetime.utcnow(),
                    "validity_period": cert_data["validity_period"],
                    "renewed_from": certificate_id,
                    "response_data": renewal_data
                }
                
                # Mark original certificate as renewed
                cert_data["status"] = "renewed"
                cert_data["renewed_to"] = new_certificate_id
                
                self.logger.info(f"GoDaddy certificate renewed: {new_certificate_id}")
                return new_certificate_id
                
            else:
                error_msg = f"GoDaddy certificate renewal failed: {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                
                raise CertificateRenewalError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GoDaddy certificate renewal failed for {certificate_id}: {e}")
            raise CertificateRenewalError(f"GoDaddy renewal failed: {e}")
    
    def _revoke_certificate_impl(self, certificate_id: str, reason: str) -> RevocationStatus:
        """
        Revoke GoDaddy certificate
        
        Args:
            certificate_id: ID of certificate to revoke
            reason: Reason for revocation
            
        Returns:
            RevocationStatus: Revocation status information
        """
        if certificate_id not in self._certificates:
            raise CertificateRevocationError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        godaddy_cert_id = cert_data.get("godaddy_cert_id")
        
        if not godaddy_cert_id:
            raise CertificateRevocationError(f"GoDaddy certificate ID not found for {certificate_id}")
        
        try:
            self.logger.info(f"Revoking GoDaddy certificate {certificate_id}")
            
            # Prepare revocation request
            revoke_request = {
                "reason": reason
            }
            
            # Make revocation request
            response = self._make_api_request(
                "POST",
                f"/certificates/{godaddy_cert_id}/revoke",
                json=revoke_request
            )
            
            if response.status_code == 200:
                # Update certificate status
                cert_data["status"] = "revoked"
                cert_data["revoked_at"] = datetime.utcnow()
                cert_data["revocation_reason"] = reason
                
                return RevocationStatus(
                    certificate_id=certificate_id,
                    revoked=True,
                    revocation_date=datetime.utcnow(),
                    reason=reason
                )
                
            else:
                error_msg = f"GoDaddy certificate revocation failed: {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                
                raise CertificateRevocationError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GoDaddy certificate revocation failed for {certificate_id}: {e}")
            raise CertificateRevocationError(f"GoDaddy revocation failed: {e}")
    
    def _get_certificate_status_impl(self, certificate_id: str) -> CertificateStatus:
        """
        Get GoDaddy certificate status
        
        Args:
            certificate_id: ID of certificate to check
            
        Returns:
            CertificateStatus: Current certificate status
        """
        if certificate_id not in self._certificates:
            raise CertificateStatusError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        godaddy_cert_id = cert_data.get("godaddy_cert_id")
        
        if not godaddy_cert_id:
            # Return local status if no GoDaddy ID
            return CertificateStatus(
                certificate_id=certificate_id,
                status=cert_data["status"],
                last_checked=datetime.utcnow()
            )
        
        try:
            # Get current status from GoDaddy API
            response = self._make_api_request(
                "GET",
                f"/certificates/{godaddy_cert_id}"
            )
            
            if response.status_code == 200:
                api_data = response.json()
                
                # Map GoDaddy status to our status
                gd_status = api_data.get("status", "unknown").lower()
                status_mapping = {
                    "pending": "pending",
                    "issued": "issued",
                    "active": "issued",
                    "expired": "expired",
                    "revoked": "revoked",
                    "cancelled": "revoked"
                }
                
                mapped_status = status_mapping.get(gd_status, "unknown")
                
                # Update local status
                cert_data["status"] = mapped_status
                cert_data["last_status_check"] = datetime.utcnow()
                
                # Extract dates if available
                issued_date = None
                expiration_date = None
                
                if api_data.get("validFrom"):
                    try:
                        issued_date = datetime.fromisoformat(api_data["validFrom"].replace("Z", "+00:00"))
                    except:
                        pass
                
                if api_data.get("validTo"):
                    try:
                        expiration_date = datetime.fromisoformat(api_data["validTo"].replace("Z", "+00:00"))
                    except:
                        pass
                
                return CertificateStatus(
                    certificate_id=certificate_id,
                    status=mapped_status,
                    issued_date=issued_date,
                    expiration_date=expiration_date,
                    last_checked=datetime.utcnow()
                )
                
            else:
                # Return local status if API call fails
                return CertificateStatus(
                    certificate_id=certificate_id,
                    status=cert_data["status"],
                    last_checked=datetime.utcnow(),
                    error_message=f"API status check failed: {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"GoDaddy status check failed for {certificate_id}: {e}")
            return CertificateStatus(
                certificate_id=certificate_id,
                status=cert_data["status"],
                last_checked=datetime.utcnow(),
                error_message=str(e)
            )
    
    def _download_certificate_impl(self, certificate_id: str) -> Dict[str, str]:
        """
        Download GoDaddy certificate files
        
        Args:
            certificate_id: ID of certificate to download
            
        Returns:
            Dict containing certificate, chain, and private key
        """
        if certificate_id not in self._certificates:
            raise CertificateDownloadError(f"Certificate not found: {certificate_id}")
        
        cert_data = self._certificates[certificate_id]
        godaddy_cert_id = cert_data.get("godaddy_cert_id")
        
        if not godaddy_cert_id:
            raise CertificateDownloadError(f"GoDaddy certificate ID not found for {certificate_id}")
        
        try:
            self.logger.info(f"Downloading GoDaddy certificate {certificate_id}")
            
            # Download certificate
            response = self._make_api_request(
                "GET",
                f"/certificates/{godaddy_cert_id}/download"
            )
            
            if response.status_code == 200:
                cert_data_response = response.json()
                
                return {
                    "certificate": cert_data_response.get("certificate", ""),
                    "chain": cert_data_response.get("intermediate", ""),
                    "private_key": cert_data_response.get("privateKey", ""),
                    "root": cert_data_response.get("root", "")
                }
                
            else:
                error_msg = f"GoDaddy certificate download failed: {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                
                raise CertificateDownloadError(error_msg)
                
        except Exception as e:
            self.logger.error(f"GoDaddy certificate download failed for {certificate_id}: {e}")
            raise CertificateDownloadError(f"GoDaddy download failed: {e}")
    
    def get_supported_features(self) -> List[str]:
        """Get GoDaddy specific features"""
        return [
            "certificate_request",
            "certificate_renewal",
            "certificate_revocation",
            "domain_validation",
            "organization_validation", 
            "extended_validation",
            "wildcard_certificates",
            "multi_domain_certificates",
            "1_year_validity",
            "2_year_validity"
        ]
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get GoDaddy specific rate limits"""
        return {
            "requests_per_window": self.rate_limit_requests,
            "window_seconds": self.rate_limit_window,
            "current_usage": len(self._request_timestamps),
            "remaining_requests": max(0, self.rate_limit_requests - len(self._request_timestamps)),
            "api_calls_per_minute": 60
        }
    
    def get_ca_info(self) -> Dict[str, Any]:
        """Get comprehensive GoDaddy plugin information"""
        base_info = super().get_ca_info()
        base_info.update({
            "api_base_url": self.api_base_url,
            "api_version": self.api_version,
            "certificate_types": ["DV_SSL", "OV_SSL", "EV_SSL", "UCC_DV_SSL", "UCC_OV_SSL"],
            "validity_periods": [365, 730],  # 1 year, 2 years
            "certificates_managed": len(self._certificates),
            "supports_wildcard": True,
            "supports_multi_domain": True
        })
        return base_info


# Register plugin
def create_plugin(config: Dict[str, Any] = None) -> GoDaddyAPIPlugin:
    """Factory function to create GoDaddy plugin"""
    return GoDaddyAPIPlugin(config)


# Plugin metadata
PLUGIN_INFO = {
    "name": "godaddy",
    "display_name": "GoDaddy",
    "description": "GoDaddy REST API client for SSL certificate management",
    "version": "1.0.0",
    "ca_url": "https://www.godaddy.com/web-security/ssl-certificate",
    "supported_features": [
        "certificate_request",
        "certificate_renewal",
        "certificate_revocation",
        "domain_validation",
        "organization_validation",
        "extended_validation",
        "wildcard_certificates",
        "multi_domain_certificates"
    ],
    "rate_limits": {
        "api_calls_per_minute": 60
    },
    "certificate_validity_days": [365, 730],
    "cost": "paid"
}