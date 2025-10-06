#!/usr/bin/env python3
"""
Test script for tunnel components
"""

import sys
import os
sys.path.append('src')

def test_tunnel_components():
    """Test all tunnel components."""
    try:
        from beast_mode.observatory.tunnel.config_manager import ConfigManager
        from beast_mode.observatory.tunnel.validator import TunnelValidator
        from beast_mode.observatory.tunnel.backup_manager import BackupManager
        from beast_mode.observatory.tunnel.version_checker import VersionChecker
        
        print("✓ All tunnel components imported successfully!")
        
        # Test ConfigManager
        manager = ConfigManager('test-config.yml')
        config = manager.create_websocket_config()
        print(f"✓ ConfigManager: Created config with tunnel: {config['tunnel']}")
        
        # Test Validator
        validator = TunnelValidator()
        is_valid, errors = validator.validate_config(config)
        print(f"✓ Validator: Config valid: {is_valid}, errors: {len(errors)}")
        
        # Test BackupManager
        backup_manager = BackupManager('test-config.yml', 'test-backups')
        print("✓ BackupManager: Initialized successfully")
        
        # Test VersionChecker
        version_checker = VersionChecker()
        print("✓ VersionChecker: Initialized successfully")
        
        print("\n🎉 All tunnel components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing tunnel components: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tunnel_components()
    sys.exit(0 if success else 1)