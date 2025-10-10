"""
Test suite for Phase 2 components of MSP SSL Chaos Tamer

Validates encrypted credential storage, certificate database operations,
and base CA plugin functionality.
"""

import pytest
import sys
import os
import tempfile
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from msp_ssl_chaos_tamer.storage.credentials import EncryptedCredentialStore, CredentialEntry
from msp_ssl_chaos_tamer.storage.database import CertificateDatabase
from msp_ssl_chaos_tamer.plugins.base import BaseCAPlugin
from msp_ssl_chaos_tamer.core.models import Certificate, Client, MSP, CertificateStatus
from msp_ssl_chaos_tamer.core.interfaces import CertificateRequest, CertificateStatus as InterfaceStatus


class TestEncryptedCredentialStore:
    """Test encrypted credential storage system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Use test master key
        self.test_master_key = "dGVzdF9tYXN0ZXJfa2V5XzEyMzQ1Njc4OTA="
        
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_credential_store_creation(self):
        """Test credential store creation"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        assert store.storage_path == self.temp_file.name
        assert store.list_credentials() == []
    
    def test_store_and_retrieve_credentials(self):
        """Test storing and retrieving credentials"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        # Store credentials
        credentials = {
            "api_key": "test_api_key_123",
            "secret": "test_secret_456"
        }
        
        success = store.store_credential("test_ca", credentials)
        assert success is True
        
        # Retrieve credentials
        retrieved = store.retrieve_credential("test_ca")
        assert retrieved == credentials
        
        # List credentials
        ca_list = store.list_credentials()
        assert "test_ca" in ca_list
    
    def test_credential_rotation(self):
        """Test credential rotation"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        # Store initial credentials
        initial_creds = {"api_key": "initial_key"}
        store.store_credential("test_ca", initial_creds)
        
        # Rotate credentials
        new_creds = {"api_key": "rotated_key"}
        success = store.rotate_credential("test_ca", new_creds)
        assert success is True
        
        # Verify new credentials
        retrieved = store.retrieve_credential("test_ca")
        assert retrieved == new_creds
        assert retrieved != initial_creds
    
    def test_credential_deletion(self):
        """Test credential deletion"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        # Store and delete credentials
        store.store_credential("test_ca", {"key": "value"})
        assert "test_ca" in store.list_credentials()
        
        success = store.delete_credential("test_ca")
        assert success is True
        assert "test_ca" not in store.list_credentials()
    
    def test_credential_info_and_rotation_status(self):
        """Test credential metadata and rotation status"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        # Store credentials with custom rotation interval
        store.store_credential("test_ca", {"key": "value"}, rotation_interval_days=30)
        
        # Get credential info
        info = store.get_credential_info("test_ca")
        assert info is not None
        assert info["ca_name"] == "test_ca"
        assert info["rotation_interval_days"] == 30
        assert "created_at" in info
        
        # Get rotation status
        status = store.get_rotation_status()
        assert "test_ca" in status
        assert "rotation_due" in status["test_ca"]
    
    def test_credential_backup(self):
        """Test credential backup functionality"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        # Store some credentials
        store.store_credential("ca1", {"key1": "value1"})
        store.store_credential("ca2", {"key2": "value2"})
        
        # Create backup
        backup_file = tempfile.NamedTemporaryFile(delete=False)
        backup_file.close()
        
        try:
            success = store.backup_credentials(backup_file.name)
            assert success is True
            
            # Verify backup file exists and has content
            assert os.path.exists(backup_file.name)
            with open(backup_file.name, 'r') as f:
                backup_data = json.load(f)
            
            assert "backup_timestamp" in backup_data
            assert "credentials" in backup_data
            assert "ca1" in backup_data["credentials"]
            assert "ca2" in backup_data["credentials"]
            
        finally:
            if os.path.exists(backup_file.name):
                os.unlink(backup_file.name)
    
    def test_health_status(self):
        """Test credential store health status"""
        store = EncryptedCredentialStore(
            storage_path=self.temp_file.name,
            master_key=self.test_master_key
        )
        
        health = store.get_health_status()
        assert health["status"] == "healthy"
        assert health["encryption_functional"] is True
        assert "stored_credentials" in health


class TestCertificateDatabase:
    """Test certificate database operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db = CertificateDatabase(self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization"""
        assert os.path.exists(self.temp_db.name)
        
        # Test database stats
        stats = self.db.get_database_stats()
        assert "certificates" in stats
        assert "clients" in stats
        assert "msps" in stats
        assert stats["certificates"] == 0  # Empty database
    
    def test_certificate_crud_operations(self):
        """Test certificate CRUD operations"""
        # Create certificate
        cert = Certificate(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="letsencrypt",
            expiration_date=datetime.utcnow() + timedelta(days=90)
        )
        
        # Create
        success = self.db.create_certificate(cert)
        assert success is True
        
        # Read
        retrieved = self.db.get_certificate(cert.id)
        assert retrieved is not None
        assert retrieved["domain"] == "test.example.com"
        assert retrieved["client_id"] == "test_client"
        
        # Update
        cert.status = CertificateStatus.ISSUED
        success = self.db.update_certificate(cert)
        assert success is True
        
        # Verify update
        updated = self.db.get_certificate(cert.id)
        assert updated["status"] == "issued"
        
        # Delete
        success = self.db.delete_certificate(cert.id)
        assert success is True
        
        # Verify deletion
        deleted = self.db.get_certificate(cert.id)
        assert deleted is None
    
    def test_client_operations(self):
        """Test client database operations"""
        # Create client
        client = Client(
            name="Test Client",
            msp_id="test_msp",
            domains=["example.com", "test.com"]
        )
        
        success = self.db.create_client(client)
        assert success is True
        
        # Retrieve client
        retrieved = self.db.get_client(client.id)
        assert retrieved is not None
        assert retrieved["name"] == "Test Client"
        assert retrieved["domains"] == ["example.com", "test.com"]
    
    def test_msp_operations(self):
        """Test MSP database operations"""
        # Create MSP
        msp = MSP(
            name="Test MSP",
            clients=["client1", "client2"]
        )
        msp.add_ca_credentials("letsencrypt", "encrypted_creds")
        
        success = self.db.create_msp(msp)
        assert success is True
        
        # Verify MSP was created (would need get_msp method)
        stats = self.db.get_database_stats()
        assert stats["msps"] == 1
    
    def test_certificate_queries(self):
        """Test certificate query operations"""
        # Create MSP and client first for the view to work
        msp = MSP(name="Test MSP")
        self.db.create_msp(msp)
        
        client = Client(name="Test Client", msp_id=msp.id)
        self.db.create_client(client)
        
        # Create test certificates
        cert1 = Certificate(
            domain="expiring.com",
            client_id=client.id,
            ca_provider="letsencrypt",
            status=CertificateStatus.ACTIVE,
            expiration_date=datetime.utcnow() + timedelta(days=15)  # Expiring soon
        )
        
        cert2 = Certificate(
            domain="healthy.com",
            client_id=client.id,
            ca_provider="letsencrypt",
            status=CertificateStatus.ACTIVE,
            expiration_date=datetime.utcnow() + timedelta(days=60)  # Healthy
        )
        
        self.db.create_certificate(cert1)
        self.db.create_certificate(cert2)
        
        # Test client certificates query
        client_certs = self.db.get_client_certificates(client.id)
        assert len(client_certs) == 2
        
        # Test expiring certificates query
        expiring = self.db.get_expiring_certificates(30)
        assert len(expiring) >= 1  # At least the expiring one
        
        # Test certificates by status
        active_certs = self.db.get_certificates_by_status(CertificateStatus.ACTIVE)
        assert len(active_certs) == 2
    
    def test_database_health(self):
        """Test database health monitoring"""
        health = self.db.get_health_status()
        assert health["status"] == "healthy"
        assert health["database_accessible"] is True
        assert "statistics" in health


class MockCAPlugin(BaseCAPlugin):
    """Mock CA plugin for testing base functionality"""
    
    def __init__(self):
        config = {
            "rate_limit_requests": 10,
            "rate_limit_window": 60,
            "max_retries": 2,
            "credentials": {"api_key": "test_key"}
        }
        super().__init__("mock_ca", config)
        self.mock_authenticated = False
    
    def _authenticate_impl(self, credentials):
        self.mock_authenticated = credentials.get("api_key") == "test_key"
        return self.mock_authenticated
    
    def _request_certificate_impl(self, request):
        return f"cert_{request.domain}_{request.client_id}"
    
    def _renew_certificate_impl(self, certificate_id):
        return f"renewed_{certificate_id}"
    
    def _revoke_certificate_impl(self, certificate_id, reason):
        from msp_ssl_chaos_tamer.core.interfaces import RevocationStatus
        return RevocationStatus(
            certificate_id=certificate_id,
            revoked=True,
            revocation_date=datetime.utcnow(),
            reason=reason
        )
    
    def _get_certificate_status_impl(self, certificate_id):
        return InterfaceStatus(
            certificate_id=certificate_id,
            status="issued"
        )
    
    def _download_certificate_impl(self, certificate_id):
        return {
            "certificate": f"cert_data_{certificate_id}",
            "chain": f"chain_data_{certificate_id}",
            "private_key": f"key_data_{certificate_id}"
        }


class TestBaseCAPlugin:
    """Test base CA plugin functionality"""
    
    def test_plugin_creation(self):
        """Test CA plugin creation"""
        plugin = MockCAPlugin()
        assert plugin.ca_name == "mock_ca"
        assert plugin.rate_limit_requests == 10
        assert plugin.max_retries == 2
    
    def test_authentication(self):
        """Test CA plugin authentication"""
        plugin = MockCAPlugin()
        
        # Test successful authentication
        success = plugin.authenticate({"api_key": "test_key"})
        assert success is True
        assert plugin._authenticated is True
        
        # Test failed authentication
        success = plugin.authenticate({"api_key": "wrong_key"})
        assert success is False
        assert plugin._authenticated is False
    
    def test_certificate_operations(self):
        """Test CA plugin certificate operations"""
        plugin = MockCAPlugin()
        plugin.authenticate({"api_key": "test_key"})
        
        # Test certificate request
        request = CertificateRequest(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="mock_ca"
        )
        
        cert_id = plugin.request_certificate(request)
        assert cert_id == "cert_test.example.com_test_client"
        
        # Test certificate renewal
        renewed_id = plugin.renew_certificate(cert_id)
        assert renewed_id == f"renewed_{cert_id}"
        
        # Test certificate status
        status = plugin.get_certificate_status(cert_id)
        assert status.certificate_id == cert_id
        assert status.status == "issued"
        
        # Test certificate download
        cert_data = plugin.download_certificate(cert_id)
        assert "certificate" in cert_data
        assert "chain" in cert_data
        assert "private_key" in cert_data
    
    def test_rate_limiting(self):
        """Test CA plugin rate limiting"""
        plugin = MockCAPlugin()
        plugin.authenticate({"api_key": "test_key"})
        
        # Make requests up to the limit
        request = CertificateRequest(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="mock_ca"
        )
        
        # Should succeed within rate limit
        for i in range(plugin.rate_limit_requests):
            cert_id = plugin.request_certificate(request)
            assert cert_id is not None
        
        # Next request should fail due to rate limit
        from msp_ssl_chaos_tamer.core.interfaces import CertificateRequestError
        with pytest.raises(CertificateRequestError, match="Rate limit exceeded"):
            plugin.request_certificate(request)
    
    def test_plugin_health_and_info(self):
        """Test CA plugin health and information"""
        plugin = MockCAPlugin()
        plugin.authenticate({"api_key": "test_key"})
        
        # Test health status
        health = plugin.get_health_status()
        assert health["status"] == "healthy"
        assert health["authenticated"] is True
        assert health["is_healthy"] is True
        
        # Test CA info
        info = plugin.get_ca_info()
        assert info["ca_name"] == "mock_ca"
        assert "rate_limits" in info
        assert "authentication" in info
        
        # Test rate limits
        limits = plugin.get_rate_limits()
        assert "requests_per_window" in limits
        assert "remaining_requests" in limits


if __name__ == "__main__":
    pytest.main([__file__, "-v"])