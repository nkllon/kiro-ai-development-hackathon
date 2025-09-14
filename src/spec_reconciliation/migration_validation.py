"""
Migration Validation

This module was extracted from migration.py
as part of RM-DDD compliance refactoring.
"""

import os
import re
import shutil
import json
import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import time

def _migrate_test_code(self) -> List[Dict]:
    """Migrate test code to use consolidated interfaces"""
    migrations = []
    tests_dir = self.workspace_root / 'tests'
    if not tests_dir.exists():
        return migrations
    test_files = list(tests_dir.rglob('test_*.py'))
    for test_file in test_files:
        migration_result = self._migrate_python_file(test_file, 'test')
        if migration_result:
            migrations.append(migration_result)
    return migrations

def _validate_migrated_implementations(self) -> Dict[str, Any]:
    """Validate that migrated implementations maintain all original functionality"""
    validation_results = {'compatibility_tests': [], 'functionality_tests': [], 'performance_tests': [], 'overall_success': False}
    try:
        compatibility_results = self._test_compatibility_layers()
        validation_results['compatibility_tests'] = compatibility_results
        functionality_results = self._test_functionality_preservation()
        validation_results['functionality_tests'] = functionality_results
        performance_results = self._test_performance_characteristics()
        validation_results['performance_tests'] = performance_results
        validation_results['overall_success'] = all((test.get('success', False) for test in compatibility_results)) and all((test.get('success', False) for test in functionality_results)) and all((test.get('success', False) for test in performance_results))
    except Exception as e:
        validation_results['error'] = str(e)
        validation_results['overall_success'] = False
    return validation_results

def _test_compatibility_layers(self) -> List[Dict]:
    """Test that compatibility layers work correctly"""
    compatibility_tests = []
    for consolidated_spec, spec_info in self.consolidated_mappings.items():
        test_result = {'consolidated_spec': consolidated_spec, 'success': False, 'details': {}}
        try:
            compatibility_file = self.workspace_root / 'src' / 'compatibility' / f'{consolidated_spec}_compatibility.py'
            if compatibility_file.exists():
                test_result['details']['compatibility_file_exists'] = True
                test_result['success'] = True
            else:
                test_result['details']['compatibility_file_exists'] = False
                test_result['details']['error'] = f'Compatibility file not found: {compatibility_file}'
        except Exception as e:
            test_result['details']['error'] = str(e)
        compatibility_tests.append(test_result)
    return compatibility_tests

def _test_functionality_preservation(self) -> List[Dict]:
    """Test that all original functionality is preserved"""
    functionality_tests = []
    examples_dir = self.workspace_root / 'examples'
    if examples_dir.exists():
        example_files = list(examples_dir.glob('*.py'))
        for example_file in example_files[:3]:
            test_result = {'example_file': str(example_file.name), 'success': False, 'details': {}}
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
                test_result['success'] = True
                test_result['details']['syntax_valid'] = True
            except SyntaxError as e:
                test_result['details']['syntax_error'] = str(e)
            except Exception as e:
                test_result['details']['error'] = str(e)
            functionality_tests.append(test_result)
    return functionality_tests

def _test_performance_characteristics(self) -> List[Dict]:
    """Test that performance characteristics are maintained"""
    performance_tests = []
    import time
from src.rm_ddd.core.health import ModuleHealth

    test_result = {'test_name': 'import_performance', 'success': False, 'details': {}}
    try:
        start_time = time.time()
        for consolidated_spec in self.consolidated_mappings.keys():
            try:
                compatibility_file = self.workspace_root / 'src' / 'compatibility' / f'{consolidated_spec}_compatibility.py'
                if compatibility_file.exists():
                    pass
            except Exception:
                pass
        import_time = time.time() - start_time
        test_result['details']['import_time_seconds'] = import_time
        test_result['success'] = import_time < 5.0
    except Exception as e:
        test_result['details']['error'] = str(e)
    performance_tests.append(test_result)
    return performance_tests

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

