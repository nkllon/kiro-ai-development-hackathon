"""
Test suite for MSP SSL Chaos Tamer foundation

Validates the core project structure, interfaces, and base classes
to ensure systematic observability and plugin architecture work correctly.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from msp_ssl_chaos_tamer.core.interfaces import (
    CAPlugin, ReflectiveModule, CertificateRequest, CertificateStatus,
    MSPSSLError, AuthenticationError
)
from msp_ssl_chaos_tamer.core.orchestrator import CertificateOrchestrator


class MockCAPlugin(CAPlugin):
    """Mock CA plugin for testing"""
    
    def __init__(self):
        super().__init__("mock_ca", {"test": True})
        self.authenticated = False
    
    def authenticate(self, credentials):
        self.authenticated = credentials.get("valid", False)
        return self.authenticated
    
    def request_certificate(self, request):
        if not self.authenticated:
            raise AuthenticationError("Not authenticated")
        return f"cert_{request.domain}_{request.client_id}"
    
    def renew_certificate(self, certificate_id):
        if not self.authenticated:
            raise AuthenticationError("Not authenticated")
        return f"renewed_{certificate_id}"
    
    def revoke_certificate(self, certificate_id, reason="test"):
        from msp_ssl_chaos_tamer.core.interfaces import RevocationStatus
        from datetime import datetime
        return RevocationStatus(
            certificate_id=certificate_id,
            revoked=True,
            revocation_date=datetime.utcnow(),
            reason=reason
        )
    
    def get_certificate_status(self, certificate_id):
        return CertificateStatus(
            certificate_id=certificate_id,
            status="issued"
        )
    
    def download_certificate(self, certificate_id):
        return {
            "certificate": f"cert_data_{certificate_id}",
            "chain": f"chain_data_{certificate_id}",
            "private_key": f"key_data_{certificate_id}"
        }


class TestFoundationStructure:
    """Test core project structure and imports"""
    
    def test_main_package_import(self):
        """Test main package can be imported"""
        import msp_ssl_chaos_tamer
        assert msp_ssl_chaos_tamer.__version__ == "0.1.0"
        assert "CertificateOrchestrator" in msp_ssl_chaos_tamer.__all__
    
    def test_core_interfaces_import(self):
        """Test core interfaces can be imported"""
        from msp_ssl_chaos_tamer.core.interfaces import CAPlugin, ReflectiveModule
        assert issubclass(CAPlugin, ReflectiveModule)
    
    def test_orchestrator_import(self):
        """Test orchestrator can be imported"""
        from msp_ssl_chaos_tamer.core.orchestrator import CertificateOrchestrator
        assert issubclass(CertificateOrchestrator, ReflectiveModule)
    
    def test_plugin_system_structure(self):
        """Test plugin system structure exists"""
        from msp_ssl_chaos_tamer.plugins import register_plugin, get_plugin, list_plugins
        
        # Test plugin registration
        register_plugin("test_plugin", MockCAPlugin)
        assert "test_plugin" in list_plugins()
        assert get_plugin("test_plugin") == MockCAPlugin


class TestCAPluginInterface:
    """Test CA plugin interface and base functionality"""
    
    def test_ca_plugin_creation(self):
        """Test CA plugin can be created"""
        plugin = MockCAPlugin()
        assert plugin.ca_name == "mock_ca"
        assert plugin.config["test"] is True
    
    def test_ca_plugin_authentication(self):
        """Test CA plugin authentication"""
        plugin = MockCAPlugin()
        
        # Test failed authentication
        assert not plugin.authenticate({"valid": False})
        assert not plugin.authenticated
        
        # Test successful authentication
        assert plugin.authenticate({"valid": True})
        assert plugin.authenticated
    
    def test_ca_plugin_certificate_operations(self):
        """Test CA plugin certificate operations"""
        plugin = MockCAPlugin()
        plugin.authenticate({"valid": True})
        
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
        
        # Test certificate revocation
        revocation = plugin.revoke_certificate(cert_id, "testing")
        assert revocation.certificate_id == cert_id
        assert revocation.revoked is True
        assert revocation.reason == "testing"
    
    def test_ca_plugin_unauthenticated_operations(self):
        """Test CA plugin operations fail when not authenticated"""
        plugin = MockCAPlugin()
        
        request = CertificateRequest(
            domain="test.example.com",
            client_id="test_client",
            ca_provider="mock_ca"
        )
        
        with pytest.raises(AuthenticationError):
            plugin.request_certificate(request)
        
        with pytest.raises(AuthenticationError):
            plugin.renew_certificate("test_cert")


class TestCertificateOrchestrator:
    """Test certificate orchestrator functionality"""
    
    def test_orchestrator_creation(self):
        """Test orchestrator can be created"""
        config = {
            "msp": {"name": "Test MSP"},
            "default_ca": "letsencrypt"
        }
        orchestrator = CertificateOrchestrator(config)
        assert orchestrator.default_ca == "letsencrypt"
        assert orchestrator.msp_config["name"] == "Test MSP"
    
    def test_orchestrator_plugin_registration(self):
        """Test orchestrator can register CA plugins"""
        orchestrator = CertificateOrchestrator({})
        plugin = MockCAPlugin()
        
        success = orchestrator.register_ca_plugin("mock_ca", plugin)
        assert success is True
        assert "mock_ca" in orchestrator.get_available_cas()
    
    def test_orchestrator_system_health(self):
        """Test orchestrator system health reporting"""
        orchestrator = CertificateOrchestrator({})
        plugin = MockCAPlugin()
        orchestrator.register_ca_plugin("mock_ca", plugin)
        
        health = orchestrator.get_system_health()
        assert health["orchestrator_status"] == "healthy"
        assert health["active_ca_plugins"] == 1
        assert health["total_ca_plugins"] == 1
        assert "timestamp" in health
    
    @patch('msp_ssl_chaos_tamer.core.orchestrator.datetime')
    def test_orchestrator_emergency_provision(self, mock_datetime):
        """Test orchestrator emergency provisioning"""
        from datetime import datetime
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        config = {"emergency_ca": "mock_ca"}
        orchestrator = CertificateOrchestrator(config)
        
        # Mock emergency provisioner
        mock_provisioner = Mock()
        mock_provisioner.emergency_provision.return_value = "emergency_cert_123"
        orchestrator.emergency_provisioner = mock_provisioner
        
        # Register CA plugin
        plugin = MockCAPlugin()
        orchestrator.register_ca_plugin("mock_ca", plugin)
        
        # Test emergency provisioning
        result = orchestrator.emergency_provision("emergency.example.com", "expired")
        
        assert result["certificate_id"] == "emergency_cert_123"
        assert result["domain"] == "emergency.example.com"
        assert result["ca_provider"] == "mock_ca"
        assert result["emergency_type"] == "expired"
        assert result["status"] == "emergency_active"


class TestReflectiveModuleIntegration:
    """Test ReflectiveModule integration for systematic observability"""
    
    def test_reflective_module_inheritance(self):
        """Test that core components inherit from ReflectiveModule"""
        orchestrator = CertificateOrchestrator({})
        plugin = MockCAPlugin()
        
        # Both should inherit from ReflectiveModule
        assert isinstance(orchestrator, ReflectiveModule)
        assert isinstance(plugin, ReflectiveModule)
    
    @patch('src.rm_ddd.core.unified_reflective_module.ReflectiveModule.__init__')
    def test_reflective_module_initialization(self, mock_init):
        """Test ReflectiveModule initialization is called"""
        mock_init.return_value = None
        
        # Creating orchestrator should call ReflectiveModule.__init__
        orchestrator = CertificateOrchestrator({})
        mock_init.assert_called()
        
        # Creating plugin should call ReflectiveModule.__init__
        plugin = MockCAPlugin()
        assert mock_init.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])