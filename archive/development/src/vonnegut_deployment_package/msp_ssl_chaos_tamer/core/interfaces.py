"""
Core interfaces for MSP SSL Chaos Tamer

Defines the fundamental interfaces that establish system boundaries
and enable plugin architecture with systematic observability.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Import the Beastly Module for systematic observability
from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class CertificateRequest:
    """Certificate signing request with MSP-specific metadata"""
    domain: str
    client_id: str
    ca_provider: str
    certificate_type: str = "domain_validated"
    validity_days: int = 90
    emergency: bool = False
    metadata: Dict[str, Any] = None


@dataclass
class CertificateStatus:
    """Certificate status information"""
    certificate_id: str
    status: str  # pending, issued, expired, revoked, error
    issued_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class RevocationStatus:
    """Certificate revocation status"""
    certificate_id: str
    revoked: bool
    revocation_date: Optional[datetime] = None
    reason: Optional[str] = None


class CAPlugin(ReflectiveModule):
    """
    Abstract base class for Certificate Authority plugins
    
    All CA plugins must inherit from this class and implement the required methods.
    This ensures consistent interface across different CAs while providing
    systematic observability through ReflectiveModule.
    """
    
    def __init__(self, ca_name: str, config: Dict[str, Any]):
        super().__init__()
        self.ca_name = ca_name
        self.config = config
        self.logger = logging.getLogger(f"msp_ssl.ca_plugin.{ca_name}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get CA plugin module information"""
        return {
            "module_name": f"ca_plugin_{self.ca_name}",
            "module_type": "ca_plugin",
            "ca_name": self.ca_name,
            "version": "1.0.0",
            "description": f"Certificate Authority plugin for {self.ca_name}"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get CA plugin capabilities"""
        return [
            {"name": "certificate_request", "enabled": True},
            {"name": "certificate_renewal", "enabled": True},
            {"name": "certificate_revocation", "enabled": True},
            {"name": "certificate_status", "enabled": True},
            {"name": "certificate_download", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get CA plugin health status"""
        return {
            "status": "healthy",
            "ca_name": self.ca_name,
            "authenticated": getattr(self, 'authenticated', False),
            "last_check": datetime.utcnow().isoformat()
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for CA plugin"""
        return {
            "degradation_applied": False,
            "fallback_mode": None,
            "message": f"CA plugin {self.ca_name} operating normally"
        }
        
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """
        Authenticate with the Certificate Authority
        
        Args:
            credentials: CA-specific authentication credentials
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def request_certificate(self, request: CertificateRequest) -> str:
        """
        Request a new certificate from the CA
        
        Args:
            request: Certificate request details
            
        Returns:
            str: Certificate ID for tracking
            
        Raises:
            CertificateRequestError: If request fails
        """
        pass
    
    @abstractmethod
    def renew_certificate(self, certificate_id: str) -> str:
        """
        Renew an existing certificate
        
        Args:
            certificate_id: ID of certificate to renew
            
        Returns:
            str: New certificate ID
            
        Raises:
            CertificateRenewalError: If renewal fails
        """
        pass
    
    @abstractmethod
    def revoke_certificate(self, certificate_id: str, reason: str = "unspecified") -> RevocationStatus:
        """
        Revoke a certificate
        
        Args:
            certificate_id: ID of certificate to revoke
            reason: Reason for revocation
            
        Returns:
            RevocationStatus: Revocation status information
            
        Raises:
            CertificateRevocationError: If revocation fails
        """
        pass
    
    @abstractmethod
    def get_certificate_status(self, certificate_id: str) -> CertificateStatus:
        """
        Get current status of a certificate
        
        Args:
            certificate_id: ID of certificate to check
            
        Returns:
            CertificateStatus: Current certificate status
            
        Raises:
            CertificateStatusError: If status check fails
        """
        pass
    
    @abstractmethod
    def download_certificate(self, certificate_id: str) -> Dict[str, str]:
        """
        Download certificate files
        
        Args:
            certificate_id: ID of certificate to download
            
        Returns:
            Dict containing certificate, chain, and private key
            
        Raises:
            CertificateDownloadError: If download fails
        """
        pass
    
    def get_ca_info(self) -> Dict[str, Any]:
        """Get information about this CA plugin"""
        return {
            "ca_name": self.ca_name,
            "plugin_version": "1.0.0",
            "supported_features": self.get_supported_features(),
            "rate_limits": self.get_rate_limits()
        }
    
    def get_supported_features(self) -> List[str]:
        """Get list of features supported by this CA"""
        return ["domain_validation", "certificate_renewal", "certificate_revocation"]
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get CA-specific rate limits"""
        return {
            "requests_per_hour": 100,
            "requests_per_day": 1000
        }


class DiscoveryEngine(ReflectiveModule):
    """
    Abstract base class for certificate discovery engines
    
    Discovers existing certificates across client domains and infrastructure.
    """
    
    @abstractmethod
    def discover_certificates(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Discover certificates for given domains
        
        Args:
            domains: List of domains to scan
            
        Returns:
            List of discovered certificate information
        """
        pass


class RenewalEngine(ReflectiveModule):
    """
    Abstract base class for certificate renewal engines
    
    Manages predictive renewal scheduling and execution.
    """
    
    @abstractmethod
    def schedule_renewal(self, certificate_id: str, days_before_expiry: int = 30) -> bool:
        """
        Schedule certificate renewal
        
        Args:
            certificate_id: Certificate to schedule for renewal
            days_before_expiry: Days before expiry to trigger renewal
            
        Returns:
            bool: True if scheduling successful
        """
        pass


class EmergencyManager(ReflectiveModule):
    """
    Abstract base class for emergency certificate management
    
    Handles "oh shit" scenarios when certificates expire or are compromised.
    """
    
    @abstractmethod
    def detect_emergency(self, certificate_id: str) -> bool:
        """
        Detect if certificate is in emergency state
        
        Args:
            certificate_id: Certificate to check
            
        Returns:
            bool: True if emergency detected
        """
        pass
    
    @abstractmethod
    def emergency_provision(self, domain: str, client_id: str) -> str:
        """
        Emergency certificate provisioning
        
        Args:
            domain: Domain needing emergency certificate
            client_id: Client ID for the domain
            
        Returns:
            str: Emergency certificate ID
        """
        pass


# Custom exceptions for MSP SSL operations
class MSPSSLError(Exception):
    """Base exception for MSP SSL operations"""
    pass


class AuthenticationError(MSPSSLError):
    """CA authentication failed"""
    pass


class CertificateRequestError(MSPSSLError):
    """Certificate request failed"""
    pass


class CertificateRenewalError(MSPSSLError):
    """Certificate renewal failed"""
    pass


class CertificateRevocationError(MSPSSLError):
    """Certificate revocation failed"""
    pass


class CertificateStatusError(MSPSSLError):
    """Certificate status check failed"""
    pass


class CertificateDownloadError(MSPSSLError):
    """Certificate download failed"""
    pass


class EmergencyProvisioningError(MSPSSLError):
    """Emergency certificate provisioning failed"""
    pass