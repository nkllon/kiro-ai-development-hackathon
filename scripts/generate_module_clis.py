#!/usr/bin/env python3
"""
Generate CLIs for all ReflectiveModule instances

This script implements the RM-DDD requirement that every module must have a CLI
with stdin/stdout pipe support.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from devpost_integration.cli_generator import CLIGeneratorEngine, CLIRegistry
from devpost_integration.reflective_module import ReflectiveModuleRegistry


def discover_reflective_modules() -> List[Any]:
    """Discover all ReflectiveModule instances in the codebase"""
    modules = []
    
    # Get all Python files in src/devpost_integration
    integration_path = src_path / "devpost_integration"
    
    for py_file in integration_path.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        try:
            # Import the module
            module_name = py_file.stem
            module_path = f"devpost_integration.{module_name}"
            
            # Import the module
            module = __import__(module_path, fromlist=[module_name])
            
            # Look for ReflectiveModule classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '__bases__') and 
                    any('ReflectiveModule' in str(base) for base in attr.__bases__)):
                    
                    # Try to instantiate the class
                    try:
                        instance = attr()
                        if hasattr(instance, 'module_id'):
                            modules.append(instance)
                    except Exception as e:
                        print(f"Warning: Could not instantiate {attr_name}: {e}")
                        
        except Exception as e:
            print(f"Warning: Could not process {py_file}: {e}")
    
    return modules


def generate_cli_for_module(module, output_dir: Path) -> bool:
    """Generate CLI for a single module"""
    try:
        generator = CLIGeneratorEngine()
        
        # Analyze module
        analysis = generator.analyze_module(module)
        
        # Generate CLI code
        cli_code = generator.generate_cli_code(analysis)
        
        # Generate entry point
        entry_point = generator.generate_cli_entry_point(module)
        
        # Create output files
        module_name = module.__class__.__name__.lower()
        cli_file = output_dir / f"{module_name}_cli.py"
        entry_file = output_dir / f"{module_name}_cli_entry.py"
        
        # Write CLI code
        with open(cli_file, 'w') as f:
            f.write(cli_code)
        
        # Write entry point
        with open(entry_file, 'w') as f:
            f.write(entry_point)
        
        # Make entry point executable
        entry_file.chmod(0o755)
        
        # Register CLI
        registry = CLIRegistry.get_instance()
        registry.register_cli(module, cli_code)
        
        print(f"✅ Generated CLI for {module.__class__.__name__}")
        print(f"   CLI file: {cli_file}")
        print(f"   Entry point: {entry_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate CLI for {module.__class__.__name__}: {e}")
        return False


def generate_all_clis() -> Dict[str, Any]:
    """Generate CLIs for all discovered modules"""
    print("🔍 Discovering ReflectiveModule instances...")
    
    modules = discover_reflective_modules()
    print(f"Found {len(modules)} ReflectiveModule instances")
    
    # Create output directory
    output_dir = Path("generated_clis")
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    
    # Generate CLIs
    results = {
        'total_modules': len(modules),
        'successful': 0,
        'failed': 0,
        'generated_files': [],
        'errors': []
    }
    
    for module in modules:
        success = generate_cli_for_module(module, output_dir)
        if success:
            results['successful'] += 1
        else:
            results['failed'] += 1
    
    # Generate master CLI script
    generate_master_cli_script(output_dir, modules)
    
    return results


def generate_master_cli_script(output_dir: Path, modules: List[Any]) -> None:
    """Generate master CLI script that can invoke any module CLI"""
    master_cli = f'''#!/usr/bin/env python3
"""
Master CLI for all ReflectiveModule instances

This script provides a unified interface to all module CLIs.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Available module CLIs
AVAILABLE_CLIS = {{
'''
    
    for module in modules:
        module_name = module.__class__.__name__.lower()
        master_cli += f'    "{module_name}": "{module_name}_cli_entry.py",\n'
    
    master_cli += '''}

def list_available_clis():
    """List all available module CLIs"""
    print("Available module CLIs:")
    for name, script in AVAILABLE_CLIS.items():
        print(f"  {name}: {script}")

def run_module_cli(module_name: str, args: List[str]) -> int:
    """Run CLI for specific module"""
    if module_name not in AVAILABLE_CLIS:
        print(f"Error: Unknown module CLI '{module_name}'")
        print("Available CLIs:")
        list_available_clis()
        return 1
    
    script_path = Path(__file__).parent / AVAILABLE_CLIS[module_name]
    
    if not script_path.exists():
        print(f"Error: CLI script not found: {script_path}")
        return 1
    
    try:
        # Run the module CLI
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error running CLI: {e}")
        return 1

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python master_cli.py <module_name> [args...]")
        print()
        list_available_clis()
        return 1
    
    module_name = sys.argv[1]
    args = sys.argv[2:]
    
    return run_module_cli(module_name, args)

if __name__ == '__main__':
    sys.exit(main())
'''
    
    master_file = output_dir / "master_cli.py"
    with open(master_file, 'w') as f:
        f.write(master_cli)
    
    master_file.chmod(0o755)
    print(f"📄 Generated master CLI: {master_file}")


def main():
    """Main entry point"""
    print("🚀 RM-DDD CLI Generation System")
    print("=" * 50)
    
    # Generate all CLIs
    results = generate_all_clis()
    
    # Print summary
    print("\n📊 Generation Summary:")
    print(f"  Total modules: {results['total_modules']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    
    if results['failed'] > 0:
        print("\n❌ Some CLIs failed to generate. Check the errors above.")
        return 1
    else:
        print("\n✅ All CLIs generated successfully!")
        print("\n🎯 Usage Examples:")
        print("  python generated_clis/master_cli.py --help")
        print("  python generated_clis/master_cli.py cli status")
        print("  echo 'data' | python generated_clis/master_cli.py cli process")
        return 0


if __name__ == '__main__':
    sys.exit(main())



