#!/usr/bin/env python3
"""
Test CLI generation without terminal commands
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from devpost_integration.cli_generator import CLIGeneratorEngine
    from devpost_integration.cli import Unknown as CLIUnknown
    
    print("✅ CLI Generator imported successfully")
    
    # Test CLI generation
    cli_module = CLIUnknown()
    generator = CLIGeneratorEngine()
    
    # Analyze module
    analysis = generator.analyze_module(cli_module)
    print(f"✅ Module analysis completed for {cli_module.__class__.__name__}")
    
    # Generate CLI code
    cli_code = generator.generate_cli_code(analysis)
    print(f"✅ CLI code generated ({len(cli_code)} characters)")
    
    # Test CLI entry point generation
    entry_point = generator.generate_cli_entry_point(cli_module)
    print(f"✅ CLI entry point generated ({len(entry_point)} characters)")
    
    print("\n🎯 RM-DDD CLI Generation System Status: WORKING")
    print("✅ CLI Generator Engine: Functional")
    print("✅ Module Analysis: Functional") 
    print("✅ CLI Code Generation: Functional")
    print("✅ Entry Point Generation: Functional")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

