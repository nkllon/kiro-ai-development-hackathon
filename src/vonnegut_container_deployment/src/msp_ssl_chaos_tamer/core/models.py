"""
Core data models for MSP SSL Chaos Tamer

Defines the fundamental data structures for certificates, clients, and MSPs
with validation methods and lifecycle state management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class CertificateStatus(Enum):
    """Certificate status enumeration"""
    PENDING = "pending"
    ISSUED = "issued"
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"
    EMERGENCY = "emergency"


class UrgencyLevel(Enum):
    """Certificate urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Certificate:
    """
    Certificate data model with validation and lifecycle management
    
    Represents an SSL/TLS certificate with all associated metadata
    for MSP certificate management.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    client_id: str = ""
    ca_provider: str = ""
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    certificate_chain: List[str] = field(default_factory=list)
    private_key_fingerprint: str = ""  # Never store actual private keys
    status: CertificateStatus = CertificateStatus.PENDING
    renewal_policy: Dict[str, Any] = field(default_factory=dict)
    emergency_contacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate certificate data after initialization"""
        if not self.domain:
            raise ValueError("Domain is required")
        if not self.client_id:
            raise ValueError("Client ID is required")
        if not self.ca_provider:
            raise ValueError("CA provider is required")
    
    def days_until_expiration(self) -> Optional[int]:
        """
        Calculate days until certificate expiration
        
        Returns:
            int: Days until expiration, None if expiration date not set
        """
        if not self.expiration_date:
            return None
        
        delta = self.expiration_date - datetime.utcnow()
        return delta.days
    
    def is_renewal_due(self, days_threshold: int = 30) -> bool:
        """
        Check if certificate renewal is due
        
        Args:
            days_threshold: Days before expiration to trigger renewal
            
        Returns:
            bool: True if renewal is due
        """
        days_left = self.days_until_expiration()
        if days_left is None:
            return False
        
        return days_left <= days_threshold
    
    def get_renewal_urgency(self) -> UrgencyLevel:
        """
        Get renewal urgency level based on days until expiration
        
        Returns:
            UrgencyLevel: Urgency level for renewal
        """
        days_left = self.days_until_expiration()
        
        if days_left is None:
            return UrgencyLevel.LOW
        
        if days_left <= 0:
            return UrgencyLevel.EMERGENCY
        elif days_left <= 7:
            return UrgencyLevel.CRITICAL
        elif days_left <= 14:
            return UrgencyLevel.HIGH
        elif days_left <= 30:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW
    
    def is_expired(self) -> bool:
        """Check if certificate is expired"""
        if not self.expiration_date:
            return False
        return datetime.utcnow() > self.expiration_date
    
    def update_status(self) -> CertificateStatus:
        """
        Update certificate status based on current state
        
        Returns:
            CertificateStatus: Updated status
        """
        if self.is_expired():
            self.status = CertificateStatus.EXPIRED
        elif self.is_renewal_due(7):  # Expiring within 7 days
            self.status = CertificateStatus.EXPIRING_SOON
        elif self.status == CertificateStatus.ISSUED and self.expiration_date:
            self.status = CertificateStatus.ACTIVE
        
        self.updated_at = datetime.utcnow()
        return self.status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert certificate to dictionary"""
        return {
            "id": self.id,
            "domain": self.domain,
            "client_id": self.client_id,
            "ca_provider": self.ca_provider,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "certificate_chain": self.certificate_chain,
            "private_key_fingerprint": self.private_key_fingerprint,
            "status": self.status.value,
            "renewal_policy": self.renewal_policy,
            "emergency_contacts": self.emergency_contacts,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "days_until_expiration": self.days_until_expiration(),
            "renewal_urgency": self.get_renewal_urgency().value
        }


@dataclass
class Client:
    """
    MSP client data model
    
    Represents an MSP client with their domains, contacts, and certificate policies.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    msp_id: str = ""
    domains: List[str] = field(default_factory=list)
    preferred_ca: str = "letsencrypt"
    billing_contact: str = ""
    technical_contact: str = ""
    emergency_contact: str = ""
    certificate_policies: List[Dict[str, Any]] = field(default_factory=list)
    portal_access_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate client data after initialization"""
        if not self.name:
            raise ValueError("Client name is required")
        if not self.msp_id:
            raise ValueError("MSP ID is required")
    
    def get_certificate_inventory(self) -> List[Dict[str, Any]]:
        """
        Get certificate inventory for this client
        
        Note: This would typically query the certificate database
        Returns placeholder for now.
        """
        # This would be implemented to query the certificate database
        # For now, return empty list as placeholder
        return []
    
    def calculate_monthly_certificate_costs(self) -> float:
        """
        Calculate monthly certificate costs for this client
        
        Returns:
            float: Monthly certificate costs
        """
        # This would calculate based on certificate inventory and CA costs
        # Placeholder implementation
        return 0.0
    
    def add_domain(self, domain: str) -> bool:
        """
        Add domain to client
        
        Args:
            domain: Domain to add
            
        Returns:
            bool: True if domain added successfully
        """
        if domain not in self.domains:
            self.domains.append(domain)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_domain(self, domain: str) -> bool:
        """
        Remove domain from client
        
        Args:
            domain: Domain to remove
            
        Returns:
            bool: True if domain removed successfully
        """
        if domain in self.domains:
            self.domains.remove(domain)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert client to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "msp_id": self.msp_id,
            "domains": self.domains,
            "preferred_ca": self.preferred_ca,
            "billing_contact": self.billing_contact,
            "technical_contact": self.technical_contact,
            "emergency_contact": self.emergency_contact,
            "certificate_policies": self.certificate_policies,
            "portal_access_enabled": self.portal_access_enabled,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "domain_count": len(self.domains)
        }


@dataclass
class MSP:
    """
    Managed Service Provider data model
    
    Represents an MSP with their clients, CA credentials, and configuration.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    ca_credentials: Dict[str, str] = field(default_factory=dict)  # Encrypted credentials
    clients: List[str] = field(default_factory=list)  # Client IDs
    default_policies: List[Dict[str, Any]] = field(default_factory=list)
    integration_settings: Dict[str, Any] = field(default_factory=dict)
    branding_config: Dict[str, Any] = field(default_factory=dict)
    contact_info: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate MSP data after initialization"""
        if not self.name:
            raise ValueError("MSP name is required")
    
    def get_total_certificate_count(self) -> int:
        """
        Get total certificate count across all clients
        
        Returns:
            int: Total certificate count
        """
        # This would query the certificate database for all client certificates
        # Placeholder implementation
        return 0
    
    def get_certificates_expiring_soon(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get certificates expiring soon across all clients
        
        Args:
            days: Days threshold for "expiring soon"
            
        Returns:
            List of certificates expiring within the threshold
        """
        # This would query the certificate database
        # Placeholder implementation
        return []
    
    def add_client(self, client_id: str) -> bool:
        """
        Add client to MSP
        
        Args:
            client_id: Client ID to add
            
        Returns:
            bool: True if client added successfully
        """
        if client_id not in self.clients:
            self.clients.append(client_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_client(self, client_id: str) -> bool:
        """
        Remove client from MSP
        
        Args:
            client_id: Client ID to remove
            
        Returns:
            bool: True if client removed successfully
        """
        if client_id in self.clients:
            self.clients.remove(client_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def add_ca_credentials(self, ca_name: str, encrypted_credentials: str) -> bool:
        """
        Add encrypted CA credentials
        
        Args:
            ca_name: Name of the CA
            encrypted_credentials: Encrypted credential string
            
        Returns:
            bool: True if credentials added successfully
        """
        self.ca_credentials[ca_name] = encrypted_credentials
        self.updated_at = datetime.utcnow()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert MSP to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "ca_credentials": list(self.ca_credentials.keys()),  # Don't expose actual credentials
            "clients": self.clients,
            "client_count": len(self.clients),
            "default_policies": self.default_policies,
            "integration_settings": self.integration_settings,
            "branding_config": self.branding_config,
            "contact_info": self.contact_info,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# Validation functions
def validate_domain(domain: str) -> bool:
    """
    Validate domain name format
    
    Args:
        domain: Domain name to validate
        
    Returns:
        bool: True if domain is valid
    """
    import re
    
    # Basic domain validation regex
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not domain or len(domain) > 253:
        return False
    
    return bool(re.match(domain_pattern, domain))


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid
    """
    import re
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(email_pattern, email)) if email else False