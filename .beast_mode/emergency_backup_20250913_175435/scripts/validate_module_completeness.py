#!/usr/bin/env python3
"""
Module Completeness Validator

Systematic validation to ensure all referenced modules exist and are importable.
Prevents missing module issues like the DevPost auth_service problem.
"""

import os
import sys
import ast
import importlib
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModuleCompletenessValidator:
    """Validates that all referenced modules exist and are importable"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_path = self.project_root / "src"
        self.missing_modules: List[str] = []
        self.import_errors: List[Tuple[str, str]] = []
        self.validation_results: Dict[str, bool] = {}
    
    def find_all_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.src_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract all import statements from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return []
    
    def is_local_import(self, import_name: str) -> bool:
        """Check if an import is a local project import"""
        return import_name.startswith('src.') or import_name.startswith('.')
    
    def convert_import_to_path(self, import_name: str) -> Path:
        """Convert import name to file path"""
        if import_name.startswith('src.'):
            import_name = import_name[4:]  # Remove 'src.' prefix
        
        # Handle relative imports
        if import_name.startswith('.'):
            # This would need context from the importing file
            return None
        
        # Convert dots to path separators
        path_parts = import_name.split('.')
        return self.src_path / Path(*path_parts).with_suffix('.py')
    
    def validate_module_exists(self, import_name: str) -> bool:
        """Check if a local module file exists"""
        if not self.is_local_import(import_name):
            return True  # External imports are not our concern
        
        module_path = self.convert_import_to_path(import_name)
        if module_path is None:
            return True  # Can't validate relative imports without context
        
        exists = module_path.exists()
        if not exists:
            self.missing_modules.append(import_name)
            logger.error(f"Missing module: {import_name} -> {module_path}")
        
        return exists
    
    def validate_import_works(self, import_name: str) -> bool:
        """Test if an import actually works"""
        if not self.is_local_import(import_name):
            return True  # Skip external imports
        
        try:
            # Add src to path for testing
            sys.path.insert(0, str(self.src_path))
            
            # Try to import
            importlib.import_module(import_name)
            return True
        except ImportError as e:
            self.import_errors.append((import_name, str(e)))
            logger.error(f"Import failed: {import_name} - {e}")
            return False
        except Exception as e:
            self.import_errors.append((import_name, str(e)))
            logger.error(f"Import error: {import_name} - {e}")
            return False
        finally:
            # Clean up path
            if str(self.src_path) in sys.path:
                sys.path.remove(str(self.src_path))
    
    def validate_all_modules(self) -> Dict[str, bool]:
        """Validate all modules in the project"""
        logger.info("Starting module completeness validation...")
        
        python_files = self.find_all_python_files()
        logger.info(f"Found {len(python_files)} Python files to validate")
        
        all_imports = set()
        
        # Extract all imports
        for file_path in python_files:
            imports = self.extract_imports(file_path)
            all_imports.update(imports)
        
        logger.info(f"Found {len(all_imports)} unique imports to validate")
        
        # Validate each import
        for import_name in sorted(all_imports):
            if self.is_local_import(import_name):
                exists = self.validate_module_exists(import_name)
                works = self.validate_import_works(import_name) if exists else False
                self.validation_results[import_name] = exists and works
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report"""
        report = []
        report.append("🔍 MODULE COMPLETENESS VALIDATION REPORT")
        report.append("=" * 60)
        
        # Summary
        total_imports = len(self.validation_results)
        working_imports = sum(1 for result in self.validation_results.values() if result)
        success_rate = (working_imports / total_imports) * 100 if total_imports > 0 else 0
        
        report.append(f"\n📊 SUMMARY:")
        report.append(f"   Total imports checked: {total_imports}")
        report.append(f"   Working imports: {working_imports}")
        report.append(f"   Failed imports: {total_imports - working_imports}")
        report.append(f"   Success rate: {success_rate:.1f}%")
        
        # Missing modules
        if self.missing_modules:
            report.append(f"\n❌ MISSING MODULES ({len(self.missing_modules)}):")
            for module in self.missing_modules:
                report.append(f"   - {module}")
        else:
            report.append(f"\n✅ NO MISSING MODULES")
        
        # Import errors
        if self.import_errors:
            report.append(f"\n❌ IMPORT ERRORS ({len(self.import_errors)}):")
            for module, error in self.import_errors:
                report.append(f"   - {module}: {error}")
        else:
            report.append(f"\n✅ NO IMPORT ERRORS")
        
        # Failed validations
        failed_imports = [name for name, result in self.validation_results.items() if not result]
        if failed_imports:
            report.append(f"\n❌ FAILED VALIDATIONS ({len(failed_imports)}):")
            for module in failed_imports:
                report.append(f"   - {module}")
        
        # Overall result
        if success_rate >= 95:
            report.append(f"\n🏆 OVERALL RESULT: EXCELLENT - All modules working")
        elif success_rate >= 90:
            report.append(f"\n✅ OVERALL RESULT: GOOD - Minor issues detected")
        elif success_rate >= 80:
            report.append(f"\n⚠️  OVERALL RESULT: FAIR - Some issues need attention")
        else:
            report.append(f"\n❌ OVERALL RESULT: POOR - Significant issues detected")
        
        return "\n".join(report)
    
    def run_validation(self) -> bool:
        """Run complete validation and return success status"""
        self.validate_all_modules()
        
        # Check if we have any critical issues
        has_missing_modules = len(self.missing_modules) > 0
        has_import_errors = len(self.import_errors) > 0
        
        success = not (has_missing_modules or has_import_errors)
        
        # Print report
        print(self.generate_report())
        
        return success


def main():
    """Main validation function"""
    validator = ModuleCompletenessValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🐺 MODULE COMPLETENESS VALIDATION: PASSED! 💪")
        sys.exit(0)
    else:
        print("\n❌ MODULE COMPLETENESS VALIDATION: FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
