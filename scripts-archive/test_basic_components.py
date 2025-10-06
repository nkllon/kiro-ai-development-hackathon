#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    # Test individual components
    from beast_mode.observatory.tunnel.config_manager import ConfigManager
    print("✓ ConfigManager imported")
    
    from beast_mode.observatory.tunnel.validator import TunnelValidator
    print("✓ TunnelValidator imported")
    
    from beast_mode.observatory.tunnel.backup_manager import BackupManager
    print("✓ BackupManager imported")
    
    # Test basic functionality
    manager = ConfigManager()
    config = manager.create_websocket_config()
    print(f"✓ Config created: {config['tunnel']}")
    
    validator = TunnelValidator()
    is_valid, errors = validator.validate_config(config)
    print(f"✓ Validation: {is_valid}, {len(errors)} errors")
    
    print("✓ Basic components working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()