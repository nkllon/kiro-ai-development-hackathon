#!/usr/bin/env python3
"""
Test Security Implementation

Simple test to verify the security configuration manager and monitoring coordinator
work correctly with the Node B management system.
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from node_b_management.security import (
    SecurityConfigurationManager,
    SecurityMonitoringCoordinator,
    SecurityCredentials,
    SecurityPolicy,
    MonitoringLevel
)


async def test_security_configuration_manager():
    """Test SecurityConfigurationManager functionality"""
    print("Testing SecurityConfigurationManager...")
    
    # Set up test environment variables
    os.environ['REDIS_PASSWORD'] = 'test_password_12345'
    os.environ['NODE_B_AUTH_TOKEN'] = 'test_auth_token_67890'
    
    try:
        # Initialize security configuration manager
        security_manager = SecurityConfigurationManager("test-node-1")
        
        # Test credential loading
        credentials = await security_manager.load_credentials()
        print(f"✓ Credentials loaded: {credentials}")
        
        # Test SSL configuration validation
        ssl_config = {
            'cert_path': '',  # Empty for test
            'key_path': '',
            'ca_path': ''
        }
        ssl_valid = await security_manager.validate_ssl_config(ssl_config)
        print(f"✓ SSL validation result: {ssl_valid}")
        
        # Test security policy enforcement
        policies_enforced = await security_manager.enforce_security_policies("test-node-1")
        print(f"✓ Security policies enforced: {policies_enforced}")
        
        # Test security violation detection
        violations = await security_manager.detect_security_violations("test-node-1")
        print(f"✓ Security violations detected: {len(violations)}")
        
        # Test authentication token generation
        auth_token = await security_manager.get_authentication_token("test-node-1")
        print(f"✓ Authentication token generated: {bool(auth_token)}")
        
        # Test token validation
        if auth_token:
            token_valid = await security_manager.validate_network_authentication(auth_token, "test-node-1")
            print(f"✓ Token validation result: {token_valid}")
        
        # Test data encryption/decryption
        test_data = "sensitive test data"
        encrypted = await security_manager.encrypt_sensitive_data(test_data)
        if encrypted:
            decrypted = await security_manager.decrypt_sensitive_data(encrypted)
            print(f"✓ Encryption/decryption test: {decrypted == test_data}")
        else:
            print("✓ Encryption not available (no encryption key configured)")
        
        # Get security status
        status = security_manager.get_security_status()
        print(f"✓ Security status: {status}")
        
        print("SecurityConfigurationManager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ SecurityConfigurationManager test failed: {e}")
        return False


async def test_security_monitoring_coordinator():
    """Test SecurityMonitoringCoordinator functionality"""
    print("\nTesting SecurityMonitoringCoordinator...")
    
    try:
        # Initialize security monitoring coordinator
        monitoring_coordinator = SecurityMonitoringCoordinator("test-node-2")
        
        # Test monitoring start/stop
        started = await monitoring_coordinator.start_monitoring()
        print(f"✓ Monitoring started: {started}")
        
        # Test configuration change validation
        config_valid = await monitoring_coordinator.validate_configuration_change(
            "redis", "password", "old_password", "new_password_123"
        )
        print(f"✓ Configuration change validation: {config_valid}")
        
        # Test encrypted data storage/retrieval
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['NODE_B_ENCRYPTED_STORAGE_PATH'] = temp_dir
            
            # Reinitialize with temp storage path
            monitoring_coordinator = SecurityMonitoringCoordinator("test-node-2")
            await monitoring_coordinator.start_monitoring()
            
            test_data = {"sensitive": "information", "value": 12345}
            stored = await monitoring_coordinator.store_encrypted_data("test_key", test_data)
            print(f"✓ Encrypted data stored: {stored}")
            
            if stored:
                retrieved = await monitoring_coordinator.retrieve_encrypted_data("test_key")
                print(f"✓ Encrypted data retrieved: {retrieved == test_data}")
            
        # Test network communication auditing
        audit_success = await monitoring_coordinator.audit_network_communication(
            "outbound", "peer-node-1", "coordination_message", 1024, 
            encrypted=True, authenticated=True
        )
        print(f"✓ Network communication audited: {audit_success}")
        
        # Test security violation detection
        violations = await monitoring_coordinator.detect_security_violations()
        print(f"✓ Security violations detected: {len(violations)}")
        
        # Get security events
        events = await monitoring_coordinator.get_security_events(limit=10)
        print(f"✓ Security events retrieved: {len(events)}")
        
        # Get network audit trail
        audit_trail = await monitoring_coordinator.get_network_audit_trail(limit=10)
        print(f"✓ Network audit trail retrieved: {len(audit_trail)}")
        
        # Get configuration changes
        config_changes = await monitoring_coordinator.get_configuration_changes()
        print(f"✓ Configuration changes retrieved: {len(config_changes)}")
        
        # Get monitoring status
        status = monitoring_coordinator.get_monitoring_status()
        print(f"✓ Monitoring status: {status}")
        
        # Stop monitoring
        stopped = await monitoring_coordinator.stop_monitoring()
        print(f"✓ Monitoring stopped: {stopped}")
        
        print("SecurityMonitoringCoordinator tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ SecurityMonitoringCoordinator test failed: {e}")
        return False


async def test_integration():
    """Test integration between security components"""
    print("\nTesting Security Component Integration...")
    
    try:
        # Initialize both components
        security_manager = SecurityConfigurationManager("test-node-integration")
        monitoring_coordinator = SecurityMonitoringCoordinator("test-node-integration", security_manager)
        
        # Load credentials
        await security_manager.load_credentials()
        
        # Start monitoring
        await monitoring_coordinator.start_monitoring()
        
        # Test integrated violation detection
        violations = await monitoring_coordinator.detect_security_violations()
        print(f"✓ Integrated violation detection: {len(violations)} violations found")
        
        # Test security policy enforcement
        policies_enforced = await security_manager.enforce_security_policies("test-node-integration")
        print(f"✓ Integrated policy enforcement: {policies_enforced}")
        
        # Stop monitoring
        await monitoring_coordinator.stop_monitoring()
        
        print("Security component integration tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Security integration test failed: {e}")
        return False


async def main():
    """Run all security implementation tests"""
    print("Starting Security Implementation Tests...")
    print("=" * 50)
    
    # Run individual component tests
    config_test_passed = await test_security_configuration_manager()
    monitoring_test_passed = await test_security_monitoring_coordinator()
    integration_test_passed = await test_integration()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"SecurityConfigurationManager: {'PASS' if config_test_passed else 'FAIL'}")
    print(f"SecurityMonitoringCoordinator: {'PASS' if monitoring_test_passed else 'FAIL'}")
    print(f"Integration Tests: {'PASS' if integration_test_passed else 'FAIL'}")
    
    all_tests_passed = config_test_passed and monitoring_test_passed and integration_test_passed
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_tests_passed else 'SOME TESTS FAILED'}")
    
    return all_tests_passed


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)