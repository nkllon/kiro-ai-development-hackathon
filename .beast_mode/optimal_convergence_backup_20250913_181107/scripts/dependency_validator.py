#!/usr/bin/env python3
"""
Dependency validation script for test startup.
Validates that all core dependencies are available before running tests.
"""

import sys
from dataclasses import dataclass
from typing import List, Dict, Any
import importlib


@dataclass
class DependencyStatus:
    """Status of dependency validation"""
    all_available: bool
    missing_dependencies: List[str]
    available_dependencies: List[str]
    validation_details: Dict[str, Any]


class DependencyChecker:
    """Validates core dependencies at test startup"""
    
    # Core dependencies required for basic functionality
    CORE_DEPENDENCIES = [
        'jinja2',
        'pydantic', 
        'yaml',
        'click',
        'aiohttp',
        'watchdog'
    ]
    
    # Optional dependencies that may not be available
    OPTIONAL_DEPENDENCIES = [
        'openai',
        'anthropic', 
        'langgraph',
        'keyring'
    ]
    
    def validate_core_dependencies(self) -> DependencyStatus:
        """Validate all core dependencies are available"""
        missing_deps = []
        available_deps = []
        validation_details = {}
        
        for dep in self.CORE_DEPENDENCIES:
            try:
                module = importlib.import_module(dep)
                available_deps.append(dep)
                validation_details[dep] = {
                    'status': 'available',
                    'version': getattr(module, '__version__', 'unknown'),
                    'location': getattr(module, '__file__', 'unknown')
                }
            except ImportError as e:
                missing_deps.append(dep)
                validation_details[dep] = {
                    'status': 'missing',
                    'error': str(e)
                }
        
        return DependencyStatus(
            all_available=len(missing_deps) == 0,
            missing_dependencies=missing_deps,
            available_dependencies=available_deps,
            validation_details=validation_details
        )
    
    def validate_optional_dependencies(self) -> DependencyStatus:
        """Validate optional dependencies"""
        missing_deps = []
        available_deps = []
        validation_details = {}
        
        for dep in self.OPTIONAL_DEPENDENCIES:
            try:
                module = importlib.import_module(dep)
                available_deps.append(dep)
                validation_details[dep] = {
                    'status': 'available',
                    'version': getattr(module, '__version__', 'unknown')
                }
            except ImportError as e:
                missing_deps.append(dep)
                validation_details[dep] = {
                    'status': 'missing',
                    'error': str(e)
                }
        
        return DependencyStatus(
            all_available=len(missing_deps) == 0,
            missing_dependencies=missing_deps,
            available_dependencies=available_deps,
            validation_details=validation_details
        )
    
    def generate_installation_commands(self, missing_deps: List[str]) -> List[str]:
        """Generate pip install commands for missing dependencies"""
        if not missing_deps:
            return []
        
        commands = []
        # Group dependencies for efficient installation
        core_missing = [dep for dep in missing_deps if dep in self.CORE_DEPENDENCIES]
        optional_missing = [dep for dep in missing_deps if dep in self.OPTIONAL_DEPENDENCIES]
        
        if core_missing:
            commands.append(f"pip install {' '.join(core_missing)}")
        
        if optional_missing:
            commands.append(f"pip install {' '.join(optional_missing)}  # Optional")
        
        return commands
    
    def print_validation_report(self, status: DependencyStatus, dependency_type: str = "core"):
        """Print detailed validation report"""
        print(f"\n=== {dependency_type.title()} Dependency Validation Report ===")
        print(f"Overall Status: {'✅ PASS' if status.all_available else '❌ FAIL'}")
        print(f"Available: {len(status.available_dependencies)}")
        print(f"Missing: {len(status.missing_dependencies)}")
        
        if status.available_dependencies:
            print(f"\n✅ Available Dependencies ({len(status.available_dependencies)}):")
            for dep in status.available_dependencies:
                details = status.validation_details[dep]
                version = details.get('version', 'unknown')
                print(f"  - {dep} (v{version})")
        
        if status.missing_dependencies:
            print(f"\n❌ Missing Dependencies ({len(status.missing_dependencies)}):")
            for dep in status.missing_dependencies:
                details = status.validation_details[dep]
                error = details.get('error', 'Unknown error')
                print(f"  - {dep}: {error}")
            
            print(f"\n🔧 Installation Commands:")
            for cmd in self.generate_installation_commands(status.missing_dependencies):
                print(f"  {cmd}")


def main():
    """Main validation function"""
    checker = DependencyChecker()
    
    print("🔍 Validating dependencies for test execution...")
    
    # Validate core dependencies
    core_status = checker.validate_core_dependencies()
    checker.print_validation_report(core_status, "core")
    
    # Validate optional dependencies
    optional_status = checker.validate_optional_dependencies()
    checker.print_validation_report(optional_status, "optional")
    
    # Overall status
    print(f"\n{'='*60}")
    if core_status.all_available:
        print("🎉 All core dependencies are available! Tests can proceed.")
        return 0
    else:
        print("⚠️  Some core dependencies are missing. Please install them before running tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())