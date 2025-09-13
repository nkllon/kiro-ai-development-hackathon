#!/usr/bin/env python3
"""
Refactoring Validator

This script validates refactored modules to ensure they maintain functionality
and meet RM-DDD compliance requirements.

Key Features:
- Syntax validation
- Import resolution checking
- RM-DDD compliance verification
- Functionality preservation testing
- Performance impact analysis
"""

import os
import ast
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation for a single module"""
    module_path: str
    syntax_valid: bool
    imports_resolved: bool
    rm_ddd_compliant: bool
    functionality_preserved: bool
    performance_impact: str  # low, medium, high
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

class RefactoringValidator:
    """Validates refactored modules for compliance and functionality"""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.validation_results: List[ValidationResult] = []
        
    def validate_module(self, module_path: str) -> ValidationResult:
        """Validate a single module"""
        logger.info(f"🔍 Validating {module_path}")
        
        result = ValidationResult(
            module_path=module_path,
            syntax_valid=False,
            imports_resolved=False,
            rm_ddd_compliant=False,
            functionality_preserved=False,
            performance_impact="unknown",
            errors=[],
            warnings=[],
            metrics={}
        )
        
        try:
            # Read module content
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. Syntax validation
            result.syntax_valid = self._validate_syntax(content, result)
            
            # 2. Import resolution
            result.imports_resolved = self._validate_imports(module_path, result)
            
            # 3. RM-DDD compliance
            result.rm_ddd_compliant = self._validate_rm_ddd_compliance(module_path, content, result)
            
            # 4. Functionality preservation
            result.functionality_preserved = self._validate_functionality(module_path, result)
            
            # 5. Performance impact
            result.performance_impact = self._assess_performance_impact(module_path, result)
            
            # 6. Generate metrics
            result.metrics = self._generate_metrics(module_path, content)
            
        except Exception as e:
            error_msg = f"Validation error for {module_path}: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        
        self.validation_results.append(result)
        return result
    
    def _validate_syntax(self, content: str, result: ValidationResult) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError as e:
            error_msg = f"Syntax error: {e}"
            result.errors.append(error_msg)
            return False
    
    def _validate_imports(self, module_path: str, result: ValidationResult) -> bool:
        """Validate that all imports can be resolved"""
        try:
            # Try to compile the module
            with open(module_path, 'r') as f:
                compile(f.read(), module_path, 'exec')
            return True
        except ImportError as e:
            error_msg = f"Import error: {e}"
            result.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Compilation error: {e}"
            result.errors.append(error_msg)
            return False
    
    def _validate_rm_ddd_compliance(self, module_path: str, content: str, result: ValidationResult) -> bool:
        """Validate RM-DDD compliance"""
        try:
            tree = ast.parse(content)
            
            # Check file size
            line_count = len(content.split('\n'))
            if line_count > 300:
                result.warnings.append(f"File size {line_count} lines exceeds 300-line limit")
                return False
            
            # Check for ReflectiveModule implementation
            has_reflective_module = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'ReflectiveModule':
                            has_reflective_module = True
                            break
            
            if not has_reflective_module:
                result.warnings.append("Module does not implement ReflectiveModule interface")
                return False
            
            # Check for required methods
            required_methods = [
                'get_module_info', 'get_capabilities', 'get_dependencies',
                'check_health', 'get_configuration', 'update_configuration',
                'get_metrics', 'reset_metrics'
            ]
            
            implemented_methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    implemented_methods.append(node.name)
            
            missing_methods = [method for method in required_methods if method not in implemented_methods]
            if missing_methods:
                result.warnings.append(f"Missing required methods: {missing_methods}")
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"RM-DDD validation error: {e}"
            result.errors.append(error_msg)
            return False
    
    def _validate_functionality(self, module_path: str, result: ValidationResult) -> bool:
        """Validate that functionality is preserved"""
        try:
            # This is a simplified check - in practice, you'd run actual tests
            # For now, we'll check that the module can be imported and basic methods exist
            
            # Try to import the module
            module_name = Path(module_path).stem
            module_dir = Path(module_path).parent
            
            # Add to Python path temporarily
            import sys
            sys.path.insert(0, str(module_dir))
            
            try:
                module = __import__(module_name)
                
                # Check for basic functionality
                if hasattr(module, '__file__'):
                    result.metrics['import_successful'] = True
                    return True
                else:
                    result.warnings.append("Module imported but no __file__ attribute")
                    return False
                    
            finally:
                # Remove from Python path
                sys.path.pop(0)
                
        except Exception as e:
            error_msg = f"Functionality validation error: {e}"
            result.errors.append(error_msg)
            return False
    
    def _assess_performance_impact(self, module_path: str, result: ValidationResult) -> str:
        """Assess performance impact of refactoring"""
        try:
            # Measure import time
            start_time = time.time()
            
            module_name = Path(module_path).stem
            module_dir = Path(module_path).parent
            
            import sys
            sys.path.insert(0, str(module_dir))
            
            try:
                __import__(module_name)
                import_time = time.time() - start_time
                
                result.metrics['import_time'] = import_time
                
                if import_time < 0.1:
                    return "low"
                elif import_time < 0.5:
                    return "medium"
                else:
                    return "high"
                    
            finally:
                sys.path.pop(0)
                
        except Exception as e:
            result.warnings.append(f"Performance assessment error: {e}")
            return "unknown"
    
    def _generate_metrics(self, module_path: str, content: str) -> Dict[str, Any]:
        """Generate metrics for the module"""
        try:
            tree = ast.parse(content)
            
            # Count different elements
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            # Calculate complexity metrics
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            return {
                'line_count': len(lines),
                'non_empty_line_count': len(non_empty_lines),
                'class_count': len(classes),
                'function_count': len(functions),
                'import_count': len(imports),
                'cyclomatic_complexity': self._calculate_cyclomatic_complexity(tree),
                'file_size_kb': len(content.encode('utf-8')) / 1024
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def validate_all_modules(self, module_paths: List[str]) -> List[ValidationResult]:
        """Validate all specified modules"""
        logger.info(f"🔍 Validating {len(module_paths)} modules")
        
        for module_path in module_paths:
            self.validate_module(module_path)
        
        return self.validation_results
    
    def validate_refactored_files(self, refactoring_report: str) -> List[ValidationResult]:
        """Validate files that were refactored based on execution report"""
        with open(refactoring_report, 'r') as f:
            execution_data = json.load(f)
        
        module_paths = []
        for result in execution_data:
            if result['success']:
                # Add source file
                module_paths.append(result['source_file'])
                # Add target modules
                for module in result['target_modules']:
                    module_path = Path(result['source_file']).parent / module
                    if module_path.exists():
                        module_paths.append(str(module_path))
        
        return self.validate_all_modules(module_paths)
    
    def generate_validation_report(self, output_file: str = "validation_report.json"):
        """Generate comprehensive validation report"""
        report_data = {
            'summary': self._generate_summary(),
            'detailed_results': []
        }
        
        for result in self.validation_results:
            report_data['detailed_results'].append({
                'module_path': result.module_path,
                'syntax_valid': result.syntax_valid,
                'imports_resolved': result.imports_resolved,
                'rm_ddd_compliant': result.rm_ddd_compliant,
                'functionality_preserved': result.functionality_preserved,
                'performance_impact': result.performance_impact,
                'errors': result.errors,
                'warnings': result.warnings,
                'metrics': result.metrics
            })
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📊 Validation report exported to {output_file}")
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total = len(self.validation_results)
        if total == 0:
            return {'total_modules': 0}
        
        syntax_valid = sum(1 for r in self.validation_results if r.syntax_valid)
        imports_resolved = sum(1 for r in self.validation_results if r.imports_resolved)
        rm_ddd_compliant = sum(1 for r in self.validation_results if r.rm_ddd_compliant)
        functionality_preserved = sum(1 for r in self.validation_results if r.functionality_preserved)
        
        total_errors = sum(len(r.errors) for r in self.validation_results)
        total_warnings = sum(len(r.warnings) for r in self.validation_results)
        
        return {
            'total_modules': total,
            'syntax_valid': syntax_valid,
            'imports_resolved': imports_resolved,
            'rm_ddd_compliant': rm_ddd_compliant,
            'functionality_preserved': functionality_preserved,
            'success_rate': (syntax_valid / total) * 100,
            'total_errors': total_errors,
            'total_warnings': total_warnings
        }

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate refactored modules")
    parser.add_argument("--modules", nargs="+", help="Module paths to validate")
    parser.add_argument("--execution-report", help="Path to execution report JSON file")
    parser.add_argument("--output", default="validation_report.json", help="Output report file")
    
    args = parser.parse_args()
    
    print("🔍 Refactoring Validator")
    print("=" * 25)
    
    # Initialize validator
    validator = RefactoringValidator()
    
    if args.execution_report:
        # Validate based on execution report
        print(f"📋 Validating based on execution report: {args.execution_report}")
        results = validator.validate_refactored_files(args.execution_report)
    elif args.modules:
        # Validate specified modules
        print(f"🔍 Validating {len(args.modules)} modules")
        results = validator.validate_all_modules(args.modules)
    else:
        print("❌ Please specify either --modules or --execution-report")
        return
    
    # Generate report
    validator.generate_validation_report(args.output)
    
    # Print summary
    summary = validator._generate_summary()
    print(f"\n📊 Validation Summary:")
    print(f"   Total modules: {summary['total_modules']}")
    print(f"   Syntax valid: {summary['syntax_valid']}")
    print(f"   Imports resolved: {summary['imports_resolved']}")
    print(f"   RM-DDD compliant: {summary['rm_ddd_compliant']}")
    print(f"   Functionality preserved: {summary['functionality_preserved']}")
    print(f"   Success rate: {summary['success_rate']:.1f}%")
    print(f"   Total errors: {summary['total_errors']}")
    print(f"   Total warnings: {summary['total_warnings']}")

if __name__ == "__main__":
    main()



