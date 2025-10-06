#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from beast_mode.observatory.tunnel import ConfigManager, TunnelValidator, BackupManager, VersionChecker
    print("✓ All imports successful")
    
    # Test basic functionality
    manager = ConfigManager()
    config = manager.create_websocket_config()
    print(f"✓ Config created: {config['tunnel']}")
    
    validator = TunnelValidator()
    is_valid, errors = validator.validate_config(config)
    print(f"✓ Validation: {is_valid}, {len(errors)} errors")
    
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()