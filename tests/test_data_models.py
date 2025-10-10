"""
Test suite for MSP SSL Chaos Tamer data models

Validates certificate lifecycle state management, data model validation,
and state transitions for Certificate, Client, and MSP models.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from msp_ssl_chaos_tamer.core.models import (
    Certificate, Client, MSP, CertificateStatus, UrgencyLevel,
    validate_domain, validate_email
)


class TestCertificateModel:
    """Test Certificate data model and lifecycle management"""
    
    def test_certificate_creation(self):
        """Test certificate creation with required fields"""
        cert = Certificate(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="letsencrypt"
        )
        
        assert cert.domain == "test.example.com"
        assert cert.client_id == "test_client"
        assert cert.ca_provider == "letsencrypt"
        assert cert.status == CertificateStatus.PENDING
        assert cert.id is not None
        assert isinstance(cert.created_at, datetime)
    
    def test_certificate_validation_errors(self):
        """Test certificate validation with missing required fields"""
        
        # Missing domain
        with pytest.raises(ValueError, match="Domain is required"):
            Certificate(client_id="test", ca_provider="letsencrypt")
        
        # Missing client_id
        with pytest.raises(ValueError, match="Client ID is required"):
            Certificate(domain="test.com", ca_provider="letsencrypt")
        
        # Missing ca_provider
        with pytest.raises(ValueError, match="CA provider is required"):
            Certificate(domain="test.com", client_id="test")
    
    def test_certificate_expiration_calculations(self):
        """Test certificate expiration date calculations"""
        future_date = datetime.utcnow() + timedelta(days=45)
        cert = Certificate(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="letsencrypt",
            expiration_date=future_date
        )
        
        days_left = cert.days_until_expiration()
        assert days_left == 45
        
        # Test renewal due logic
        assert cert.is_renewal_due(30) is True  # 45 days < 30 threshold = False, but 45 > 30 so True
        assert cert.is_renewal_due(50) is True  # 45 days < 50 threshold = True
    
    def test_certificate_urgency_levels(self):
        """Test certificate renewal urgency calculations"""
        
        # Emergency - expired
        expired_cert = Certificate(
            domain="expired.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() - timedelta(days=1)
        )
        assert expired_cert.get_renewal_urgency() == UrgencyLevel.EMERGENCY
        
        # Critical - 5 days left
        critical_cert = Certificate(
            domain="critical.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=5)
        )
        assert critical_cert.get_renewal_urgency() == UrgencyLevel.CRITICAL
        
        # High - 10 days left
        high_cert = Certificate(
            domain="high.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=10)
        )
        assert high_cert.get_renewal_urgency() == UrgencyLevel.HIGH
        
        # Medium - 20 days left
        medium_cert = Certificate(
            domain="medium.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=20)
        )
        assert medium_cert.get_renewal_urgency() == UrgencyLevel.MEDIUM
        
        # Low - 60 days left
        low_cert = Certificate(
            domain="low.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=60)
        )
        assert low_cert.get_renewal_urgency() == UrgencyLevel.LOW
    
    def test_certificate_status_updates(self):
        """Test certificate status update logic"""
        
        # Test expired certificate status update
        expired_cert = Certificate(
            domain="test.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() - timedelta(days=1)
        )
        
        status = expired_cert.update_status()
        assert status == CertificateStatus.EXPIRED
        assert expired_cert.status == CertificateStatus.EXPIRED
        
        # Test expiring soon status
        expiring_cert = Certificate(
            domain="test.com",
            client_id="test",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=5)
        )
        
        status = expiring_cert.update_status()
        assert status == CertificateStatus.EXPIRING_SOON
        
        # Test active certificate
        active_cert = Certificate(
            domain="test.com",
            client_id="test",
            ca_provider="letsencrypt",
            status=CertificateStatus.ISSUED,
            expiration_date=datetime.utcnow() + timedelta(days=60)
        )
        
        status = active_cert.update_status()
        assert status == CertificateStatus.ACTIVE
    
    def test_certificate_to_dict(self):
        """Test certificate serialization to dictionary"""
        cert = Certificate(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=30)
        )
        
        cert_dict = cert.to_dict()
        
        assert cert_dict["domain"] == "test.example.com"
        assert cert_dict["client_id"] == "test_client"
        assert cert_dict["ca_provider"] == "letsencrypt"
        assert cert_dict["status"] == "pending"
        assert "days_until_expiration" in cert_dict
        assert "renewal_urgency" in cert_dict
        assert cert_dict["renewal_urgency"] == "medium"


class TestClientModel:
    """Test Client data model and operations"""
    
    def test_client_creation(self):
        """Test client creation with required fields"""
        client = Client(
            name="Test Client",
            msp_id="test_msp"
        )
        
        assert client.name == "Test Client"
        assert client.msp_id == "test_msp"
        assert client.preferred_ca == "letsencrypt"  # default
        assert client.portal_access_enabled is True  # default
        assert client.id is not None
        assert isinstance(client.created_at, datetime)
    
    def test_client_validation_errors(self):
        """Test client validation with missing required fields"""
        
        # Missing name
        with pytest.raises(ValueError, match="Client name is required"):
            Client(msp_id="test_msp")
        
        # Missing msp_id
        with pytest.raises(ValueError, match="MSP ID is required"):
            Client(name="Test Client")
    
    def test_client_domain_management(self):
        """Test client domain addition and removal"""
        client = Client(name="Test Client", msp_id="test_msp")
        
        # Add domain
        success = client.add_domain("example.com")
        assert success is True
        assert "example.com" in client.domains
        
        # Add duplicate domain
        success = client.add_domain("example.com")
        assert success is False  # Already exists
        
        # Remove domain
        success = client.remove_domain("example.com")
        assert success is True
        assert "example.com" not in client.domains
        
        # Remove non-existent domain
        success = client.remove_domain("nonexistent.com")
        assert success is False
    
    def test_client_to_dict(self):
        """Test client serialization to dictionary"""
        client = Client(
            name="Test Client",
            msp_id="test_msp",
            domains=["example.com", "test.com"]
        )
        
        client_dict = client.to_dict()
        
        assert client_dict["name"] == "Test Client"
        assert client_dict["msp_id"] == "test_msp"
        assert client_dict["domains"] == ["example.com", "test.com"]
        assert client_dict["domain_count"] == 2
        assert client_dict["preferred_ca"] == "letsencrypt"


class TestMSPModel:
    """Test MSP data model and operations"""
    
    def test_msp_creation(self):
        """Test MSP creation with required fields"""
        msp = MSP(name="Test MSP")
        
        assert msp.name == "Test MSP"
        assert msp.id is not None
        assert isinstance(msp.created_at, datetime)
        assert msp.ca_credentials == {}
        assert msp.clients == []
    
    def test_msp_validation_errors(self):
        """Test MSP validation with missing required fields"""
        
        # Missing name
        with pytest.raises(ValueError, match="MSP name is required"):
            MSP()
    
    def test_msp_client_management(self):
        """Test MSP client addition and removal"""
        msp = MSP(name="Test MSP")
        
        # Add client
        success = msp.add_client("client_123")
        assert success is True
        assert "client_123" in msp.clients
        
        # Add duplicate client
        success = msp.add_client("client_123")
        assert success is False  # Already exists
        
        # Remove client
        success = msp.remove_client("client_123")
        assert success is True
        assert "client_123" not in msp.clients
        
        # Remove non-existent client
        success = msp.remove_client("nonexistent")
        assert success is False
    
    def test_msp_ca_credentials(self):
        """Test MSP CA credential management"""
        msp = MSP(name="Test MSP")
        
        # Add CA credentials
        success = msp.add_ca_credentials("letsencrypt", "encrypted_creds_123")
        assert success is True
        assert "letsencrypt" in msp.ca_credentials
        assert msp.ca_credentials["letsencrypt"] == "encrypted_creds_123"
    
    def test_msp_to_dict(self):
        """Test MSP serialization to dictionary"""
        msp = MSP(
            name="Test MSP",
            clients=["client1", "client2"]
        )
        msp.add_ca_credentials("letsencrypt", "encrypted_creds")
        
        msp_dict = msp.to_dict()
        
        assert msp_dict["name"] == "Test MSP"
        assert msp_dict["clients"] == ["client1", "client2"]
        assert msp_dict["client_count"] == 2
        assert msp_dict["ca_credentials"] == ["letsencrypt"]  # Only keys, not values
        assert "id" in msp_dict


class TestValidationFunctions:
    """Test validation utility functions"""
    
    def test_domain_validation(self):
        """Test domain name validation"""
        
        # Valid domains
        assert validate_domain("example.com") is True
        assert validate_domain("sub.example.com") is True
        assert validate_domain("test-domain.co.uk") is True
        assert validate_domain("a.b") is True
        
        # Invalid domains
        assert validate_domain("") is False
        assert validate_domain("invalid..domain.com") is False
        assert validate_domain("-invalid.com") is False
        assert validate_domain("invalid-.com") is False
        assert validate_domain("a" * 254) is False  # Too long
    
    def test_email_validation(self):
        """Test email address validation"""
        
        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        assert validate_email("test123@test-domain.com") is True
        
        # Invalid emails
        assert validate_email("") is False
        assert validate_email("invalid-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("test@") is False
        assert validate_email("test@domain") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])