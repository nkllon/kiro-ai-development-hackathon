#!/usr/bin/env python3
"""
Test the AI Memory Palace built-in CLI capabilities
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from beast_mode.ai_memory_palace.context_manager import ContextManager
    from beast_mode.ai_memory_palace.context_registry import ContextRegistry  
    from beast_mode.ai_memory_palace.storage import ContextStorage

    print("=== AI Memory Palace Built-in CLI Test ===")
    
    # Create a simple context manager
    storage = ContextStorage(Path.home() / '.kiro' / 'context_storage')
    registry = ContextRegistry(storage)
    cm = ContextManager()
    cm.registry = registry

    # Test the built-in CLI
    print('\n🧠 AI Memory Palace CLI Interface:')
    cli_interface = cm.get_cli_interface()
    print(f'Module: {cli_interface["module_name"]}')
    print(f'Health: {cli_interface["health_status"]}')
    print(f'Available commands: {len(cli_interface["commands"])}')
    
    print('\n📋 Available Commands:')
    for cmd_name, cmd_info in list(cli_interface["commands"].items())[:10]:
        print(f'  - {cmd_name}: {cmd_info["docstring"][:60]}...')
    
    print('\n✅ The AI Memory Palace already has CLI capabilities via ReflectiveModule!')
    print('   No need for separate CLI scripts - just use the built-in interface.')

except Exception as e:
    print(f"❌ Error: {e}")
    print("The AI Memory Palace components have import issues that need fixing.")