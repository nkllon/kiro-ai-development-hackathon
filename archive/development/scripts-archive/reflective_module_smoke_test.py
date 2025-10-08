#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE REFLECTIVE MODULE SMOKE TEST
============================================
Heuristic and smoke testing for ReflectiveModule base class implementations.

Tests:
1. Import and instantiation testing
2. Interface compliance validation
3. CMS functionality verification
4. Health monitoring validation
5. CLI generation testing
6. DDD compliance checking
7. Error handling validation
8. Memory and performance testing
"""

import sys
import traceback
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import inspect
import gc


class ReflectiveModuleSmokeTest:
    """Comprehensive smoke test suite for ReflectiveModule implementations."""
    
    def __init__(self):
        self.test_results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "warnings": [],
            "performance_metrics": {},
            "implementation_analysis": {}
        }
        
    def log_test(self, test_name: str, passed: bool, details: str = "", warning: str = ""):
        """Log test result."""
        self.test_results["tests_run"] += 1
        if passed:
            self.test_results["tests_passed"] += 1
            print(f"✅ {test_name}: PASSED")
        else:
            self.test_results["tests_failed"] += 1
            self.test_results["failures"].append({
                "test": test_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
            print(f"❌ {test_name}: FAILED - {details}")
            
        if warning:
            self.test_results["warnings"].append({
                "test": test_name,
                "warning": warning,
                "timestamp": datetime.now().isoformat()
            })
            print(f"⚠️  {test_name}: WARNING - {warning}")
            
        if details and passed:
            print(f"   Details: {details}")

    def test_import_capabilities(self) -> bool:
        """Test import capabilities of both ReflectiveModule implementations."""
        print("\n🔍 TESTING IMPORT CAPABILITIES")
        
        # Test base implementation
        try:
            from src.rm_ddd.core.base_reflective_module import ReflectiveModule as BaseRM
            from src.rm_ddd.core.base_reflective_module import ModuleStatus, ModuleCapability, ModuleHealth
            self.log_test("Base ReflectiveModule Import", True, "All base classes imported successfully")
        except Exception as e:
            self.log_test("Base ReflectiveModule Import", False, f"Import failed: {str(e)}")
            return False
            
        # Test unified implementation
        try:
            from src.rm_ddd.core.reflective_module import ReflectiveModule as UnifiedRM
            self.log_test("Unified ReflectiveModule Import", True, "Unified implementation imported successfully")
        except Exception as e:
            self.log_test("Unified ReflectiveModule Import", False, f"Import failed: {str(e)}")
            return False
            
        return True

    def test_instantiation(self) -> Optional[Any]:
        """Test instantiation of ReflectiveModule implementations."""
        print("\n🏗️  TESTING INSTANTIATION")
        
        # Create test implementation
        try:
            from src.rm_ddd.core.base_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth
            
            class TestModule(ReflectiveModule):
                def __init__(self):
                    super().__init__("test_module", "1.0.0")
                    
                def get_module_info(self) -> Dict[str, Any]:
                    return {"name": "TestModule", "version": "1.0.0"}
                    
                def get_capabilities(self) -> List[ModuleCapability]:
                    return [ModuleCapability.CORE_FUNCTIONALITY]
                    
                def get_dependencies(self) -> List[str]:
                    return []
                    
                def check_health(self) -> ModuleHealth:
                    return ModuleHealth(
                        module_id=self.module_id,
                        status=ModuleStatus.HEALTHY,
                        health_score=1.0,
                        issues=[],
                        capabilities=self.get_capabilities(),
                        dependencies=self.get_dependencies(),
                        metrics=self.get_metrics(),
                        last_check=datetime.now()
                    )
                    
                def test_method(self, param1: str, param2: int = 42) -> str:
                    """Test method for capability discovery."""
                    return f"Test result: {param1} - {param2}"
            
            # Test instantiation
            test_module = TestModule()
            self.log_test("Base Module Instantiation", True, f"Module ID: {test_module.module_id}")
            return test_module
            
        except Exception as e:
            self.log_test("Base Module Instantiation", False, f"Instantiation failed: {str(e)}\n{traceback.format_exc()}")
            return None

    def test_unified_instantiation(self) -> Optional[Any]:
        """Test unified ReflectiveModule instantiation."""
        print("\n🔄 TESTING UNIFIED INSTANTIATION")
        
        try:
            from src.rm_ddd.core.reflective_module import ReflectiveModule
            
            class UnifiedTestModule(ReflectiveModule):
                def test_method(self, param1: str, param2: int = 42) -> str:
                    """Test method for unified module."""
                    return f"Unified test: {param1} - {param2}"
                    
                def get_test_data(self) -> Dict[str, Any]:
                    """Get test data for CMS testing."""
                    return {"test": "data", "timestamp": datetime.now().isoformat()}
            
            # Test instantiation
            unified_module = UnifiedTestModule()
            self.log_test("Unified Module Instantiation", True, f"Module ID: {unified_module.module_id}")
            return unified_module
            
        except Exception as e:
            self.log_test("Unified Module Instantiation", False, f"Instantiation failed: {str(e)}\n{traceback.format_exc()}")
            return None

    def test_interface_compliance(self, module: Any) -> bool:
        """Test interface compliance."""
        print("\n📋 TESTING INTERFACE COMPLIANCE")
        
        if not module:
            self.log_test("Interface Compliance", False, "No module provided")
            return False
            
        # Test required methods
        required_methods = [
            "get_module_info", "get_capabilities", "get_dependencies", 
            "check_health", "get_configuration", "get_metrics",
            "is_healthy", "get_module_status", "health_check"
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(module, method):
                missing_methods.append(method)
                
        if missing_methods:
            self.log_test("Interface Compliance", False, f"Missing methods: {missing_methods}")
            return False
        else:
            self.log_test("Interface Compliance", True, f"All {len(required_methods)} required methods present")
            
        # Test method calls
        try:
            module_info = module.get_module_info()
            capabilities = module.get_capabilities()
            dependencies = module.get_dependencies()
            health = module.check_health()
            config = module.get_configuration()
            metrics = module.get_metrics()
            
            self.log_test("Method Execution", True, f"All interface methods callable")
            return True
            
        except Exception as e:
            self.log_test("Method Execution", False, f"Method execution failed: {str(e)}")
            return False

    def test_cms_functionality(self, module: Any) -> bool:
        """Test embedded CMS functionality."""
        print("\n💾 TESTING CMS FUNCTIONALITY")
        
        if not module:
            self.log_test("CMS Functionality", False, "No module provided")
            return False
            
        # Check for CMS methods
        cms_methods = ["store_content", "get_content", "list_content"]
        has_cms = all(hasattr(module, method) for method in cms_methods)
        
        if not has_cms:
            self.log_test("CMS Methods", False, f"Missing CMS methods: {[m for m in cms_methods if not hasattr(module, m)]}")
            return False
            
        try:
            # Test CMS operations
            test_content = {"test": "data", "timestamp": datetime.now().isoformat()}
            
            # Store content
            stored = module.store_content("test_content", "test_type", test_content)
            self.log_test("CMS Store", True, f"Content stored with ID: test_content")
            
            # Retrieve content
            retrieved = module.get_content("test_content")
            if retrieved and retrieved.get("data") == test_content:
                self.log_test("CMS Retrieve", True, "Content retrieved successfully")
            else:
                self.log_test("CMS Retrieve", False, f"Retrieved content mismatch: {retrieved}")
                return False
                
            # List content
            content_list = module.list_content()
            if isinstance(content_list, list) and len(content_list) > 0:
                self.log_test("CMS List", True, f"Found {len(content_list)} content items")
            else:
                self.log_test("CMS List", False, f"Content list invalid: {content_list}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("CMS Operations", False, f"CMS operations failed: {str(e)}")
            return False

    def test_health_monitoring(self, module: Any) -> bool:
        """Test health monitoring capabilities."""
        print("\n🏥 TESTING HEALTH MONITORING")
        
        if not module:
            self.log_test("Health Monitoring", False, "No module provided")
            return False
            
        try:
            # Test health check
            health_status = module.get_health_status()
            if isinstance(health_status, dict) and "status" in health_status:
                self.log_test("Health Status", True, f"Status: {health_status.get('status')}")
            else:
                self.log_test("Health Status", False, f"Invalid health status: {health_status}")
                return False
                
            # Test health metrics
            is_healthy = module.is_healthy()
            self.log_test("Health Check", True, f"Module healthy: {is_healthy}")
            
            # Test uptime
            if hasattr(module, "get_uptime_seconds"):
                uptime = module.get_uptime_seconds()
                self.log_test("Uptime Tracking", True, f"Uptime: {uptime:.2f} seconds")
            
            return True
            
        except Exception as e:
            self.log_test("Health Monitoring", False, f"Health monitoring failed: {str(e)}")
            return False

    def test_cli_generation(self, module: Any) -> bool:
        """Test CLI generation capabilities."""
        print("\n🖥️  TESTING CLI GENERATION")
        
        if not module:
            self.log_test("CLI Generation", False, "No module provided")
            return False
            
        try:
            # Test CLI interface generation
            if hasattr(module, "generate_cli_interface"):
                cli_code = module.generate_cli_interface()
                if isinstance(cli_code, str) and len(cli_code) > 100:
                    self.log_test("CLI Generation", True, f"Generated {len(cli_code)} characters of CLI code")
                else:
                    self.log_test("CLI Generation", False, f"Invalid CLI code: {len(cli_code) if cli_code else 0} chars")
                    return False
            else:
                self.log_test("CLI Generation", False, "No generate_cli_interface method")
                return False
                
            # Test CLI commands
            if hasattr(module, "get_cli_commands"):
                commands = module.get_cli_commands()
                if isinstance(commands, dict):
                    self.log_test("CLI Commands", True, f"Found {len(commands)} CLI commands")
                else:
                    self.log_test("CLI Commands", False, f"Invalid CLI commands: {commands}")
                    return False
                    
            return True
            
        except Exception as e:
            self.log_test("CLI Generation", False, f"CLI generation failed: {str(e)}")
            return False

    def test_ddd_compliance(self, module: Any) -> bool:
        """Test DDD compliance features."""
        print("\n🏛️  TESTING DDD COMPLIANCE")
        
        if not module:
            self.log_test("DDD Compliance", False, "No module provided")
            return False
            
        try:
            # Test bounded context
            if hasattr(module, "bounded_context"):
                context = module.bounded_context
                if context and hasattr(context, "name"):
                    self.log_test("Bounded Context", True, f"Context: {context.name}")
                else:
                    self.log_test("Bounded Context", False, f"Invalid bounded context: {context}")
                    
            # Test domain vocabulary
            if hasattr(module, "domain_vocabulary"):
                vocab = module.domain_vocabulary
                if vocab and hasattr(vocab, "terms"):
                    self.log_test("Domain Vocabulary", True, f"Vocabulary terms: {len(vocab.terms)}")
                else:
                    self.log_test("Domain Vocabulary", False, f"Invalid domain vocabulary: {vocab}")
                    
            # Test DDD pattern
            if hasattr(module, "ddd_pattern"):
                pattern = module.ddd_pattern
                self.log_test("DDD Pattern", True, f"Pattern: {pattern}")
                
            return True
            
        except Exception as e:
            self.log_test("DDD Compliance", False, f"DDD compliance test failed: {str(e)}")
            return False

    def test_error_handling(self, module: Any) -> bool:
        """Test error handling capabilities."""
        print("\n🚨 TESTING ERROR HANDLING")
        
        if not module:
            self.log_test("Error Handling", False, "No module provided")
            return False
            
        try:
            # Test error logging
            if hasattr(module, "log_error"):
                test_error = Exception("Test error")
                module.log_error(test_error, {"test": "context"})
                self.log_test("Error Logging", True, "Error logged successfully")
                
                # Test error history
                if hasattr(module, "get_error_history"):
                    history = module.get_error_history()
                    if isinstance(history, list) and len(history) > 0:
                        self.log_test("Error History", True, f"Found {len(history)} error entries")
                    else:
                        self.log_test("Error History", False, f"Invalid error history: {history}")
                        
            # Test error count tracking
            if hasattr(module, "increment_error_count"):
                initial_count = getattr(module, "_error_count", 0)
                module.increment_error_count()
                new_count = getattr(module, "_error_count", 0)
                if new_count > initial_count:
                    self.log_test("Error Count Tracking", True, f"Error count: {initial_count} -> {new_count}")
                else:
                    self.log_test("Error Count Tracking", False, f"Error count not incremented: {initial_count} -> {new_count}")
                    
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Error handling test failed: {str(e)}")
            return False

    def test_performance_metrics(self, module: Any) -> bool:
        """Test performance and memory usage."""
        print("\n⚡ TESTING PERFORMANCE METRICS")
        
        if not module:
            self.log_test("Performance Metrics", False, "No module provided")
            return False
            
        try:
            # Memory usage test
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform operations
            start_time = time.time()
            for i in range(100):
                module.get_health_status()
                if hasattr(module, "store_content"):
                    module.store_content(f"perf_test_{i}", "test", {"data": i})
            end_time = time.time()
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_delta = memory_after - memory_before
            
            self.test_results["performance_metrics"] = {
                "execution_time_100_ops": execution_time,
                "memory_usage_mb": memory_after,
                "memory_delta_mb": memory_delta,
                "ops_per_second": 100 / execution_time if execution_time > 0 else 0
            }
            
            self.log_test("Performance Test", True, 
                         f"100 ops in {execution_time:.3f}s, Memory: {memory_after:.1f}MB (+{memory_delta:.1f}MB)")
            
            # Performance thresholds
            if execution_time > 1.0:
                self.log_test("Performance Threshold", False, 
                             f"Execution too slow: {execution_time:.3f}s > 1.0s", 
                             "Performance may be suboptimal")
            else:
                self.log_test("Performance Threshold", True, f"Good performance: {execution_time:.3f}s")
                
            return True
            
        except Exception as e:
            self.log_test("Performance Metrics", False, f"Performance test failed: {str(e)}")
            return False

    def analyze_implementation_quality(self, module: Any) -> Dict[str, Any]:
        """Analyze implementation quality heuristics."""
        print("\n🔬 ANALYZING IMPLEMENTATION QUALITY")
        
        analysis = {
            "class_name": module.__class__.__name__ if module else "Unknown",
            "module_path": module.__module__ if module else "Unknown",
            "method_count": 0,
            "abstract_methods": 0,
            "public_methods": 0,
            "private_methods": 0,
            "properties": 0,
            "docstring_coverage": 0,
            "complexity_score": 0
        }
        
        if not module:
            return analysis
            
        try:
            # Analyze methods
            methods = inspect.getmembers(module, predicate=inspect.ismethod)
            functions = inspect.getmembers(module.__class__, predicate=inspect.isfunction)
            all_methods = methods + functions
            
            analysis["method_count"] = len(all_methods)
            
            documented_methods = 0
            for name, method in all_methods:
                if name.startswith("_"):
                    analysis["private_methods"] += 1
                else:
                    analysis["public_methods"] += 1
                    
                if hasattr(method, "__doc__") and method.__doc__:
                    documented_methods += 1
                    
            # Calculate docstring coverage
            if analysis["method_count"] > 0:
                analysis["docstring_coverage"] = documented_methods / analysis["method_count"]
                
            # Analyze properties
            properties = inspect.getmembers(module.__class__, predicate=lambda x: isinstance(x, property))
            analysis["properties"] = len(properties)
            
            # Simple complexity heuristic
            analysis["complexity_score"] = (
                analysis["method_count"] * 0.5 +
                analysis["properties"] * 0.3 +
                (1.0 - analysis["docstring_coverage"]) * 10  # Penalty for poor documentation
            )
            
            self.test_results["implementation_analysis"] = analysis
            
            self.log_test("Implementation Analysis", True, 
                         f"Methods: {analysis['method_count']}, "
                         f"Docs: {analysis['docstring_coverage']:.1%}, "
                         f"Complexity: {analysis['complexity_score']:.1f}")
            
            return analysis
            
        except Exception as e:
            self.log_test("Implementation Analysis", False, f"Analysis failed: {str(e)}")
            return analysis

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive smoke test suite."""
        print("🧪 STARTING COMPREHENSIVE REFLECTIVE MODULE SMOKE TEST")
        print("=" * 60)
        
        # Test imports
        if not self.test_import_capabilities():
            print("❌ CRITICAL: Import test failed - aborting")
            return self.test_results
            
        # Test base implementation
        base_module = self.test_instantiation()
        if base_module:
            self.test_interface_compliance(base_module)
            self.test_health_monitoring(base_module)
            self.test_error_handling(base_module)
            self.test_performance_metrics(base_module)
            self.analyze_implementation_quality(base_module)
            
        # Test unified implementation
        unified_module = self.test_unified_instantiation()
        if unified_module:
            self.test_cms_functionality(unified_module)
            self.test_cli_generation(unified_module)
            self.test_ddd_compliance(unified_module)
            
        # Final summary
        print("\n" + "=" * 60)
        print("🏁 SMOKE TEST SUMMARY")
        print(f"Tests Run: {self.test_results['tests_run']}")
        print(f"Passed: {self.test_results['tests_passed']} ✅")
        print(f"Failed: {self.test_results['tests_failed']} ❌")
        print(f"Warnings: {len(self.test_results['warnings'])} ⚠️")
        
        success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100 if self.test_results['tests_run'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results['tests_failed'] > 0:
            print("\n❌ FAILURES:")
            for failure in self.test_results['failures']:
                print(f"  - {failure['test']}: {failure['details']}")
                
        if self.test_results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in self.test_results['warnings']:
                print(f"  - {warning['test']}: {warning['warning']}")
                
        return self.test_results


def main():
    """Run the smoke test suite."""
    tester = ReflectiveModuleSmokeTest()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open("reflective_module_smoke_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
        
    print(f"\n📊 Results saved to: reflective_module_smoke_test_results.json")
    
    # Exit with appropriate code
    if results['tests_failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()