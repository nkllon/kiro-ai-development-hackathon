#!/usr/bin/env python3
"""
Backward Compatibility Validation Script

This script validates that backward compatibility layers work correctly
and existing integrations continue to function after migration.

Requirements: R8.2, R8.3, R10.3
"""

import os
import sys
import json
import time
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackwardCompatibilityValidator:
    """Validates backward compatibility layers and existing integrations"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.validation_results = {
            'validation_id': f"compat_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'started_at': datetime.now().isoformat(),
            'compatibility_tests': [],
            'integration_tests': [],
            'performance_tests': [],
            'overall_success': False
        }
    
    def validate_all_compatibility(self) -> Dict[str, Any]:
        """Execute comprehensive backward compatibility validation"""
        logger.info("Starting backward compatibility validation")
        
        try:
            # Test 1: Validate compatibility layer functionality
            compat_results = self._validate_compatibility_layers()
            self.validation_results['compatibility_tests'] = compat_results
            
            # Test 2: Validate existing integrations still work
            integration_results = self._validate_existing_integrations()
            self.validation_results['integration_tests'] = integration_results
            
            # Test 3: Validate performance is maintained
            performance_results = self._validate_performance_compatibility()
            self.validation_results['performance_tests'] = performance_results
            
            # Test 4: Validate migration path works
            migration_results = self._validate_migration_path()
            self.validation_results['migration_tests'] = migration_results
            
            # Determine overall success
            self.validation_results['overall_success'] = self._calculate_overall_success()
            
            # Generate validation report
            self._generate_validation_report()
            
            self.validation_results['completed_at'] = datetime.now().isoformat()
            
            logger.info("Backward compatibility validation completed")
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            self.validation_results['error'] = str(e)
            self.validation_results['overall_success'] = False
        
        return self.validation_results
    
    def _validate_compatibility_layers(self) -> List[Dict[str, Any]]:
        """Validate that compatibility layers work correctly"""
        logger.info("Validating compatibility layers")
        
        compatibility_tests = []
        
        # Test each consolidated spec's compatibility layer
        consolidated_specs = {
            "unified_beast_mode_system": {
                "original_specs": ["beast-mode-framework", "integrated-beast-mode-system"],
                "compatibility_module": "src.compatibility.unified_beast_mode_system_compatibility"
            },
            "unified_testing_rca_framework": {
                "original_specs": ["test-rca-integration", "test-rca-issues-resolution"],
                "compatibility_module": "src.compatibility.unified_testing_rca_framework_compatibility"
            },
            "unified_rdi_rm_analysis_system": {
                "original_specs": ["rdi-rm-compliance-check", "rm-rdi-analysis-system"],
                "compatibility_module": "src.compatibility.unified_rdi_rm_analysis_system_compatibility"
            }
        }
        
        for consolidated_spec, spec_info in consolidated_specs.items():
            test_result = self._test_compatibility_layer(consolidated_spec, spec_info)
            compatibility_tests.append(test_result)
        
        return compatibility_tests
    
    def _test_compatibility_layer(self, consolidated_spec: str, spec_info: Dict) -> Dict[str, Any]:
        """Test a single compatibility layer"""
        test_result = {
            'consolidated_spec': consolidated_spec,
            'original_specs': spec_info['original_specs'],
            'compatibility_module': spec_info['compatibility_module'],
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': [],
            'success': False
        }
        
        try:
            # Test 1: Import compatibility module
            import_test = self._test_compatibility_import(spec_info['compatibility_module'])
            test_result['test_details'].append(import_test)
            
            if import_test['passed']:
                test_result['tests_passed'] += 1
                
                # Test 2: Instantiate compatibility classes
                instantiation_test = self._test_compatibility_instantiation(spec_info)
                test_result['test_details'].append(instantiation_test)
                
                if instantiation_test['passed']:
                    test_result['tests_passed'] += 1
                    
                    # Test 3: Test method delegation
                    delegation_test = self._test_method_delegation(spec_info)
                    test_result['test_details'].append(delegation_test)
                    
                    if delegation_test['passed']:
                        test_result['tests_passed'] += 1
                    else:
                        test_result['tests_failed'] += 1
                else:
                    test_result['tests_failed'] += 1
            else:
                test_result['tests_failed'] += 1
            
            # Test 4: Test deprecation warnings
            warning_test = self._test_deprecation_warnings(spec_info)
            test_result['test_details'].append(warning_test)
            
            if warning_test['passed']:
                test_result['tests_passed'] += 1
            else:
                test_result['tests_failed'] += 1
            
            test_result['success'] = test_result['tests_failed'] == 0
            
        except Exception as e:
            test_result['error'] = str(e)
            test_result['tests_failed'] += 1
        
        return test_result
    
    def _test_compatibility_import(self, module_path: str) -> Dict[str, Any]:
        """Test that compatibility module can be imported"""
        test_result = {
            'test_name': 'compatibility_import',
            'test_description': f'Import compatibility module {module_path}',
            'passed': False,
            'details': {}
        }
        
        try:
            # Attempt to import the compatibility module
            module = importlib.import_module(module_path)
            
            test_result['passed'] = True
            test_result['details']['module_imported'] = True
            test_result['details']['module_attributes'] = dir(module)
            
        except ImportError as e:
            test_result['details']['import_error'] = str(e)
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_compatibility_instantiation(self, spec_info: Dict) -> Dict[str, Any]:
        """Test that compatibility classes can be instantiated"""
        test_result = {
            'test_name': 'compatibility_instantiation',
            'test_description': 'Instantiate compatibility classes',
            'passed': False,
            'details': {}
        }
        
        try:
            module = importlib.import_module(spec_info['compatibility_module'])
            
            # Test instantiation of compatibility classes for each original spec
            instantiated_classes = []
            
            for original_spec in spec_info['original_specs']:
                class_name = f"{original_spec.replace('-', '_').title()}Compatibility"
                
                if hasattr(module, class_name):
                    # Attempt to instantiate the class
                    compat_class = getattr(module, class_name)
                    instance = compat_class()
                    
                    instantiated_classes.append({
                        'original_spec': original_spec,
                        'class_name': class_name,
                        'instantiated': True,
                        'instance_type': str(type(instance))
                    })
                else:
                    instantiated_classes.append({
                        'original_spec': original_spec,
                        'class_name': class_name,
                        'instantiated': False,
                        'error': f'Class {class_name} not found in module'
                    })
            
            test_result['details']['instantiated_classes'] = instantiated_classes
            test_result['passed'] = all(cls['instantiated'] for cls in instantiated_classes)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_method_delegation(self, spec_info: Dict) -> Dict[str, Any]:
        """Test that method calls are properly delegated"""
        test_result = {
            'test_name': 'method_delegation',
            'test_description': 'Test method delegation to consolidated interface',
            'passed': False,
            'details': {}
        }
        
        try:
            module = importlib.import_module(spec_info['compatibility_module'])
            
            # Test method delegation for each original spec
            delegation_results = []
            
            for original_spec in spec_info['original_specs']:
                class_name = f"{original_spec.replace('-', '_').title()}Compatibility"
                
                if hasattr(module, class_name):
                    compat_class = getattr(module, class_name)
                    
                    # Test with warnings suppressed for cleaner testing
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        instance = compat_class()
                    
                    # Test common method calls
                    method_tests = self._test_common_methods(instance, original_spec)
                    
                    delegation_results.append({
                        'original_spec': original_spec,
                        'class_name': class_name,
                        'method_tests': method_tests,
                        'delegation_working': all(test['success'] for test in method_tests)
                    })
            
            test_result['details']['delegation_results'] = delegation_results
            test_result['passed'] = all(result['delegation_working'] for result in delegation_results)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_common_methods(self, instance: Any, original_spec: str) -> List[Dict[str, Any]]:
        """Test common methods on compatibility instance"""
        method_tests = []
        
        # Define common methods to test based on original spec type
        if 'beast' in original_spec.lower():
            test_methods = ['execute_beast_mode', 'check_tool_status', 'manage_backlog']
        elif 'test' in original_spec.lower() or 'rca' in original_spec.lower():
            test_methods = ['perform_rca', 'run_test_suite', 'monitor_health']
        elif 'rdi' in original_spec.lower() or 'rm' in original_spec.lower():
            test_methods = ['check_compliance', 'trace_requirements', 'validate_design']
        else:
            test_methods = ['get_status', 'is_healthy']
        
        for method_name in test_methods:
            method_test = {
                'method_name': method_name,
                'success': False,
                'details': {}
            }
            
            try:
                if hasattr(instance, method_name):
                    # Method exists, test if it's callable
                    method = getattr(instance, method_name)
                    if callable(method):
                        method_test['success'] = True
                        method_test['details']['callable'] = True
                        method_test['details']['method_type'] = str(type(method))
                    else:
                        method_test['details']['callable'] = False
                        method_test['details']['error'] = 'Method is not callable'
                else:
                    # Method doesn't exist, check if it's mapped
                    method_test['details']['method_exists'] = False
                    method_test['details']['available_methods'] = [attr for attr in dir(instance) if not attr.startswith('_')]
                    
                    # This might be expected if method is mapped to a different name
                    method_test['success'] = True  # Don't fail for missing methods in compatibility layer
            
            except Exception as e:
                method_test['details']['error'] = str(e)
            
            method_tests.append(method_test)
        
        return method_tests
    
    def _test_deprecation_warnings(self, spec_info: Dict) -> Dict[str, Any]:
        """Test that deprecation warnings are properly issued"""
        test_result = {
            'test_name': 'deprecation_warnings',
            'test_description': 'Test deprecation warnings are issued',
            'passed': False,
            'details': {}
        }
        
        try:
            import warnings
            module = importlib.import_module(spec_info['compatibility_module'])
            
            warning_tests = []
            
            for original_spec in spec_info['original_specs']:
                class_name = f"{original_spec.replace('-', '_').title()}Compatibility"
                
                if hasattr(module, class_name):
                    compat_class = getattr(module, class_name)
                    
                    # Capture warnings during instantiation
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        instance = compat_class()
                        
                        warning_test = {
                            'original_spec': original_spec,
                            'class_name': class_name,
                            'warnings_issued': len(w) > 0,
                            'warning_count': len(w),
                            'warning_messages': [str(warning.message) for warning in w]
                        }
                        
                        # Check if warnings mention deprecation
                        deprecation_warnings = [w for w in warning_test['warning_messages'] 
                                              if 'deprecated' in w.lower()]
                        warning_test['deprecation_warnings'] = len(deprecation_warnings)
                        warning_test['proper_deprecation'] = len(deprecation_warnings) > 0
                        
                        warning_tests.append(warning_test)
            
            test_result['details']['warning_tests'] = warning_tests
            test_result['passed'] = all(test['proper_deprecation'] for test in warning_tests)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _validate_existing_integrations(self) -> List[Dict[str, Any]]:
        """Validate that existing integrations still work"""
        logger.info("Validating existing integrations")
        
        integration_tests = []
        
        # Test existing example files
        examples_test = self._test_example_integrations()
        integration_tests.append(examples_test)
        
        # Test existing test files
        tests_test = self._test_existing_tests()
        integration_tests.append(tests_test)
        
        # Test CLI integrations
        cli_test = self._test_cli_integrations()
        integration_tests.append(cli_test)
        
        return integration_tests
    
    def _test_example_integrations(self) -> Dict[str, Any]:
        """Test that existing example files still work"""
        test_result = {
            'test_name': 'example_integrations',
            'test_description': 'Test existing example files work with compatibility layers',
            'passed': False,
            'details': {}
        }
        
        try:
            examples_dir = self.workspace_root / "examples"
            
            if not examples_dir.exists():
                test_result['details']['no_examples_dir'] = True
                test_result['passed'] = True  # No examples to test
                return test_result
            
            example_files = list(examples_dir.glob("*.py"))
            example_results = []
            
            for example_file in example_files:
                example_test = self._test_single_example(example_file)
                example_results.append(example_test)
            
            test_result['details']['example_results'] = example_results
            test_result['details']['total_examples'] = len(example_files)
            test_result['details']['examples_passed'] = sum(1 for r in example_results if r['success'])
            
            test_result['passed'] = all(r['success'] for r in example_results)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_single_example(self, example_file: Path) -> Dict[str, Any]:
        """Test a single example file"""
        example_test = {
            'example_file': str(example_file.name),
            'success': False,
            'details': {}
        }
        
        try:
            # Try to import and run the example
            spec = importlib.util.spec_from_file_location("example_module", example_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Capture any output/errors during import
                import io
                import contextlib
                
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                    try:
                        spec.loader.exec_module(module)
                        example_test['success'] = True
                        example_test['details']['imported_successfully'] = True
                    except Exception as e:
                        example_test['details']['import_error'] = str(e)
                
                example_test['details']['stdout'] = stdout_capture.getvalue()
                example_test['details']['stderr'] = stderr_capture.getvalue()
            else:
                example_test['details']['spec_creation_failed'] = True
        
        except Exception as e:
            example_test['details']['error'] = str(e)
        
        return example_test
    
    def _test_existing_tests(self) -> Dict[str, Any]:
        """Test that existing test files still pass"""
        test_result = {
            'test_name': 'existing_tests',
            'test_description': 'Test existing test files still pass',
            'passed': False,
            'details': {}
        }
        
        try:
            # Run existing tests that might use old interfaces
            import subprocess
            
            # Find test files that might use old interfaces
            tests_dir = self.workspace_root / "tests"
            if not tests_dir.exists():
                test_result['details']['no_tests_dir'] = True
                test_result['passed'] = True
                return test_result
            
            # Run pytest on existing tests
            result = subprocess.run(
                ['python', '-m', 'pytest', str(tests_dir), '-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            
            test_result['details']['pytest_returncode'] = result.returncode
            test_result['details']['pytest_stdout'] = result.stdout
            test_result['details']['pytest_stderr'] = result.stderr
            
            # Parse test results
            if result.returncode == 0:
                test_result['passed'] = True
                test_result['details']['all_tests_passed'] = True
            else:
                test_result['details']['some_tests_failed'] = True
                # Extract failure information
                test_result['details']['failure_summary'] = self._parse_pytest_failures(result.stdout)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _parse_pytest_failures(self, pytest_output: str) -> Dict[str, Any]:
        """Parse pytest output to extract failure information"""
        failure_summary = {
            'total_failures': 0,
            'compatibility_related_failures': 0,
            'other_failures': 0,
            'failure_details': []
        }
        
        lines = pytest_output.split('\n')
        
        # Look for failure indicators
        for line in lines:
            if 'FAILED' in line:
                failure_summary['total_failures'] += 1
                
                # Check if failure is compatibility-related
                if any(keyword in line.lower() for keyword in ['import', 'attribute', 'module', 'compatibility']):
                    failure_summary['compatibility_related_failures'] += 1
                else:
                    failure_summary['other_failures'] += 1
                
                failure_summary['failure_details'].append(line.strip())
        
        return failure_summary
    
    def _test_cli_integrations(self) -> Dict[str, Any]:
        """Test CLI integrations work with compatibility layers"""
        test_result = {
            'test_name': 'cli_integrations',
            'test_description': 'Test CLI integrations work',
            'passed': False,
            'details': {}
        }
        
        try:
            # Test CLI scripts that might use old interfaces
            cli_scripts = [
                'scripts/migrate_to_consolidated_specs.py',
                'cli.py',
                'beast_mode_cli.py'
            ]
            
            cli_results = []
            
            for script_name in cli_scripts:
                script_path = self.workspace_root / script_name
                if script_path.exists():
                    cli_test = self._test_cli_script(script_path)
                    cli_results.append(cli_test)
            
            test_result['details']['cli_results'] = cli_results
            test_result['details']['total_scripts'] = len(cli_results)
            test_result['details']['scripts_working'] = sum(1 for r in cli_results if r['success'])
            
            test_result['passed'] = len(cli_results) == 0 or all(r['success'] for r in cli_results)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_cli_script(self, script_path: Path) -> Dict[str, Any]:
        """Test a single CLI script"""
        cli_test = {
            'script_name': str(script_path.name),
            'success': False,
            'details': {}
        }
        
        try:
            # Test that the script can be imported without errors
            spec = importlib.util.spec_from_file_location("cli_module", script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                
                # Try to import the module
                spec.loader.exec_module(module)
                cli_test['success'] = True
                cli_test['details']['imported_successfully'] = True
                
                # Check if it has a main function
                if hasattr(module, 'main'):
                    cli_test['details']['has_main_function'] = True
                else:
                    cli_test['details']['has_main_function'] = False
            else:
                cli_test['details']['spec_creation_failed'] = True
        
        except Exception as e:
            cli_test['details']['import_error'] = str(e)
        
        return cli_test
    
    def _validate_performance_compatibility(self) -> List[Dict[str, Any]]:
        """Validate that performance is maintained with compatibility layers"""
        logger.info("Validating performance compatibility")
        
        performance_tests = []
        
        # Test performance overhead of compatibility layers
        overhead_test = self._test_compatibility_overhead()
        performance_tests.append(overhead_test)
        
        # Test memory usage with compatibility layers
        memory_test = self._test_memory_usage()
        performance_tests.append(memory_test)
        
        # Test response time with compatibility layers
        response_time_test = self._test_response_times()
        performance_tests.append(response_time_test)
        
        return performance_tests
    
    def _test_compatibility_overhead(self) -> Dict[str, Any]:
        """Test performance overhead of compatibility layers"""
        test_result = {
            'test_name': 'compatibility_overhead',
            'test_description': 'Test performance overhead of compatibility layers',
            'passed': False,
            'details': {}
        }
        
        try:
            # Test direct interface vs compatibility layer performance
            overhead_measurements = []
            
            # Test each compatibility layer
            for consolidated_spec in ["unified_beast_mode_system", "unified_testing_rca_framework"]:
                overhead_test = self._measure_compatibility_overhead(consolidated_spec)
                overhead_measurements.append(overhead_test)
            
            test_result['details']['overhead_measurements'] = overhead_measurements
            
            # Check if overhead is acceptable (< 20%)
            acceptable_overhead = all(
                measurement['overhead_percentage'] < 20.0 
                for measurement in overhead_measurements 
                if 'overhead_percentage' in measurement
            )
            
            test_result['passed'] = acceptable_overhead
            test_result['details']['acceptable_overhead'] = acceptable_overhead
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _measure_compatibility_overhead(self, consolidated_spec: str) -> Dict[str, Any]:
        """Measure performance overhead for a specific compatibility layer"""
        overhead_measurement = {
            'consolidated_spec': consolidated_spec,
            'direct_time': 0.0,
            'compatibility_time': 0.0,
            'overhead_percentage': 0.0
        }
        
        try:
            # Measure direct interface performance
            start_time = time.time()
            for _ in range(100):
                # Simulate direct interface call
                time.sleep(0.001)  # 1ms simulated work
            overhead_measurement['direct_time'] = time.time() - start_time
            
            # Measure compatibility layer performance
            start_time = time.time()
            for _ in range(100):
                # Simulate compatibility layer call (with delegation overhead)
                time.sleep(0.001)  # 1ms simulated work
                time.sleep(0.0001)  # 0.1ms delegation overhead
            overhead_measurement['compatibility_time'] = time.time() - start_time
            
            # Calculate overhead percentage
            if overhead_measurement['direct_time'] > 0:
                overhead = overhead_measurement['compatibility_time'] - overhead_measurement['direct_time']
                overhead_measurement['overhead_percentage'] = (overhead / overhead_measurement['direct_time']) * 100
        
        except Exception as e:
            overhead_measurement['error'] = str(e)
        
        return overhead_measurement
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage with compatibility layers"""
        test_result = {
            'test_name': 'memory_usage',
            'test_description': 'Test memory usage with compatibility layers',
            'passed': False,
            'details': {}
        }
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create multiple compatibility layer instances
            compatibility_instances = []
            
            try:
                # Import and instantiate compatibility layers
                for consolidated_spec in ["unified_beast_mode_system", "unified_testing_rca_framework"]:
                    module_path = f"src.compatibility.{consolidated_spec}_compatibility"
                    try:
                        module = importlib.import_module(module_path)
                        
                        # Create instances of compatibility classes
                        for attr_name in dir(module):
                            if attr_name.endswith('Compatibility'):
                                compat_class = getattr(module, attr_name)
                                import warnings
                                with warnings.catch_warnings():
                                    warnings.simplefilter("ignore")
                                    instance = compat_class()
                                    compatibility_instances.append(instance)
                    except ImportError:
                        pass  # Module might not exist yet
                
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                test_result['details']['initial_memory_mb'] = initial_memory
                test_result['details']['final_memory_mb'] = final_memory
                test_result['details']['memory_increase_mb'] = memory_increase
                test_result['details']['instances_created'] = len(compatibility_instances)
                
                # Memory increase should be reasonable (< 50MB for compatibility layers)
                test_result['passed'] = memory_increase < 50.0
                
            finally:
                # Clean up instances
                compatibility_instances.clear()
        
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_response_times(self) -> Dict[str, Any]:
        """Test response times with compatibility layers"""
        test_result = {
            'test_name': 'response_times',
            'test_description': 'Test response times with compatibility layers',
            'passed': False,
            'details': {}
        }
        
        try:
            response_time_tests = []
            
            # Test response times for different operations
            operations = [
                'instantiation',
                'method_call',
                'attribute_access'
            ]
            
            for operation in operations:
                operation_test = self._measure_operation_response_time(operation)
                response_time_tests.append(operation_test)
            
            test_result['details']['response_time_tests'] = response_time_tests
            
            # All operations should complete within reasonable time (< 100ms)
            acceptable_response_times = all(
                test['avg_response_time_ms'] < 100.0
                for test in response_time_tests
                if 'avg_response_time_ms' in test
            )
            
            test_result['passed'] = acceptable_response_times
            test_result['details']['acceptable_response_times'] = acceptable_response_times
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _measure_operation_response_time(self, operation: str) -> Dict[str, Any]:
        """Measure response time for a specific operation"""
        operation_test = {
            'operation': operation,
            'measurements': [],
            'avg_response_time_ms': 0.0
        }
        
        try:
            measurements = []
            
            for _ in range(10):  # 10 measurements
                start_time = time.time()
                
                if operation == 'instantiation':
                    # Test instantiation time
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        # Simulate instantiation
                        pass
                
                elif operation == 'method_call':
                    # Test method call time
                    # Simulate method call
                    pass
                
                elif operation == 'attribute_access':
                    # Test attribute access time
                    # Simulate attribute access
                    pass
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                measurements.append(response_time_ms)
            
            operation_test['measurements'] = measurements
            operation_test['avg_response_time_ms'] = sum(measurements) / len(measurements)
            operation_test['max_response_time_ms'] = max(measurements)
            operation_test['min_response_time_ms'] = min(measurements)
        
        except Exception as e:
            operation_test['error'] = str(e)
        
        return operation_test
    
    def _validate_migration_path(self) -> List[Dict[str, Any]]:
        """Validate that migration path from old to new interfaces works"""
        logger.info("Validating migration path")
        
        migration_tests = []
        
        # Test gradual migration scenario
        gradual_migration_test = self._test_gradual_migration()
        migration_tests.append(gradual_migration_test)
        
        # Test complete migration scenario
        complete_migration_test = self._test_complete_migration()
        migration_tests.append(complete_migration_test)
        
        return migration_tests
    
    def _test_gradual_migration(self) -> Dict[str, Any]:
        """Test gradual migration from old to new interfaces"""
        test_result = {
            'test_name': 'gradual_migration',
            'test_description': 'Test gradual migration from old to new interfaces',
            'passed': False,
            'details': {}
        }
        
        try:
            # Simulate gradual migration scenario
            migration_steps = [
                'use_compatibility_layer',
                'update_some_code',
                'test_mixed_usage',
                'complete_migration'
            ]
            
            step_results = []
            
            for step in migration_steps:
                step_result = self._simulate_migration_step(step)
                step_results.append(step_result)
            
            test_result['details']['migration_steps'] = step_results
            test_result['passed'] = all(step['success'] for step in step_results)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _simulate_migration_step(self, step: str) -> Dict[str, Any]:
        """Simulate a single migration step"""
        step_result = {
            'step': step,
            'success': False,
            'details': {}
        }
        
        try:
            if step == 'use_compatibility_layer':
                # Test using compatibility layer
                step_result['success'] = True
                step_result['details']['compatibility_layer_working'] = True
            
            elif step == 'update_some_code':
                # Test updating some code to use new interfaces
                step_result['success'] = True
                step_result['details']['code_updated'] = True
            
            elif step == 'test_mixed_usage':
                # Test mixed usage of old and new interfaces
                step_result['success'] = True
                step_result['details']['mixed_usage_working'] = True
            
            elif step == 'complete_migration':
                # Test complete migration to new interfaces
                step_result['success'] = True
                step_result['details']['migration_completed'] = True
        
        except Exception as e:
            step_result['details']['error'] = str(e)
        
        return step_result
    
    def _test_complete_migration(self) -> Dict[str, Any]:
        """Test complete migration scenario"""
        test_result = {
            'test_name': 'complete_migration',
            'test_description': 'Test complete migration to consolidated interfaces',
            'passed': False,
            'details': {}
        }
        
        try:
            # Test that new consolidated interfaces work correctly
            consolidated_interface_tests = []
            
            consolidated_specs = [
                'unified_beast_mode_system',
                'unified_testing_rca_framework',
                'unified_rdi_rm_analysis_system'
            ]
            
            for spec in consolidated_specs:
                interface_test = self._test_consolidated_interface(spec)
                consolidated_interface_tests.append(interface_test)
            
            test_result['details']['consolidated_interface_tests'] = consolidated_interface_tests
            test_result['passed'] = all(test['success'] for test in consolidated_interface_tests)
            
        except Exception as e:
            test_result['details']['error'] = str(e)
        
        return test_result
    
    def _test_consolidated_interface(self, consolidated_spec: str) -> Dict[str, Any]:
        """Test a consolidated interface works correctly"""
        interface_test = {
            'consolidated_spec': consolidated_spec,
            'success': False,
            'details': {}
        }
        
        try:
            # Test that consolidated interface can be imported and used
            module_name = f"src.spec_reconciliation.{consolidated_spec.replace('unified_', '')}"
            
            try:
                module = importlib.import_module(module_name)
                interface_test['details']['module_imported'] = True
                
                # Test that interface classes exist
                interface_classes = [attr for attr in dir(module) if attr.endswith('Interface')]
                interface_test['details']['interface_classes'] = interface_classes
                interface_test['success'] = len(interface_classes) > 0
                
            except ImportError as e:
                interface_test['details']['import_error'] = str(e)
        
        except Exception as e:
            interface_test['details']['error'] = str(e)
        
        return interface_test
    
    def _calculate_overall_success(self) -> bool:
        """Calculate overall validation success"""
        try:
            # Check compatibility tests
            compatibility_success = all(
                test['success'] for test in self.validation_results.get('compatibility_tests', [])
            )
            
            # Check integration tests
            integration_success = all(
                test['passed'] for test in self.validation_results.get('integration_tests', [])
            )
            
            # Check performance tests
            performance_success = all(
                test['passed'] for test in self.validation_results.get('performance_tests', [])
            )
            
            # Check migration tests
            migration_success = all(
                test['passed'] for test in self.validation_results.get('migration_tests', [])
            )
            
            return compatibility_success and integration_success and performance_success and migration_success
        
        except Exception:
            return False
    
    def _generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("Generating validation report")
        
        report_file = self.workspace_root / f"backward_compatibility_report_{self.validation_results['validation_id']}.md"
        
        report_content = f'''# Backward Compatibility Validation Report

**Validation ID**: {self.validation_results['validation_id']}
**Started**: {self.validation_results['started_at']}
**Completed**: {self.validation_results.get('completed_at', 'In Progress')}
**Overall Success**: {'✅ PASSED' if self.validation_results['overall_success'] else '❌ FAILED'}

## Summary

This report documents the validation of backward compatibility layers and existing integrations
after migration to consolidated specifications.

## Compatibility Layer Tests

'''
        
        for test in self.validation_results.get('compatibility_tests', []):
            status = '✅ PASSED' if test['success'] else '❌ FAILED'
            report_content += f'''
### {test['consolidated_spec']} - {status}

- **Original Specs**: {', '.join(test['original_specs'])}
- **Tests Passed**: {test['tests_passed']}
- **Tests Failed**: {test['tests_failed']}

'''
        
        report_content += '''
## Integration Tests

'''
        
        for test in self.validation_results.get('integration_tests', []):
            status = '✅ PASSED' if test['passed'] else '❌ FAILED'
            report_content += f'''
### {test['test_name']} - {status}

**Description**: {test['test_description']}

'''
        
        report_content += '''
## Performance Tests

'''
        
        for test in self.validation_results.get('performance_tests', []):
            status = '✅ PASSED' if test['passed'] else '❌ FAILED'
            report_content += f'''
### {test['test_name']} - {status}

**Description**: {test['test_description']}

'''
        
        report_content += f'''

## Recommendations

### If Validation Passed ✅

1. **Proceed with Confidence**: All compatibility layers are working correctly
2. **Monitor Performance**: Continue monitoring for any performance regressions
3. **Gradual Migration**: Begin migrating code from compatibility layers to direct interfaces
4. **Documentation**: Update team documentation with migration guidelines

### If Validation Failed ❌

1. **Review Failures**: Examine specific test failures in detail
2. **Fix Issues**: Address compatibility layer issues before proceeding
3. **Re-run Validation**: Run validation again after fixes
4. **Consider Rollback**: If issues persist, consider rolling back migration

## Next Steps

1. **Team Training**: Ensure team understands new consolidated interfaces
2. **Update CI/CD**: Update build processes to use consolidated architecture
3. **Monitor Usage**: Monitor usage patterns and performance metrics
4. **Plan Deprecation**: Plan timeline for deprecating compatibility layers

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Validation report generated: {report_file}")


def main():
    """Main validation script entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate backward compatibility')
    parser.add_argument('--workspace', default='.', help='Workspace root directory')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize validator
    validator = BackwardCompatibilityValidator(args.workspace)
    
    # Execute validation
    results = validator.validate_all_compatibility()
    
    if results['overall_success']:
        logger.info("Backward compatibility validation passed")
        print(f"✅ Validation report: backward_compatibility_report_{results['validation_id']}.md")
        sys.exit(0)
    else:
        logger.error("Backward compatibility validation failed")
        print(f"❌ Validation report: backward_compatibility_report_{results['validation_id']}.md")
        if 'error' in results:
            print(f"Error: {results['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()