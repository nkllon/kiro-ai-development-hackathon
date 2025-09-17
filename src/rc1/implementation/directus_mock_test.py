#!/usr/bin/env python3
"""
Directus Mock Test
=================

Tests our interface data structure and migration logic without requiring Directus to be running.
Validates that our data is properly formatted and ready for Directus import.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, List, Any

class DirectusMockTest:
    """Mock test for Directus data validation"""
    
    def __init__(self):
        self.test_data = None
        
    def load_test_data(self) -> bool:
        """Load test data from export file"""
        print("📁 Loading test data...")
        try:
            with open('directus_interface_export.json', 'r') as f:
                self.test_data = json.load(f)
            print(f"✅ Loaded test data with {len(self.test_data['interfaces'])} interfaces")
            return True
        except Exception as e:
            print(f"❌ Failed to load test data: {e}")
            return False
    
    def validate_interface_structure(self) -> bool:
        """Validate interface data structure"""
        print("🔍 Validating interface structure...")
        try:
            required_fields = ['name', 'interface_type', 'module_path', 'file_path', 'line_number', 'version', 'status', 'description', 'rdi_compliant', 'health_score']
            
            for interface in self.test_data['interfaces']:
                for field in required_fields:
                    if field not in interface:
                        print(f"❌ Missing field '{field}' in interface {interface.get('name', 'unknown')}")
                        return False
            
            print("✅ All interfaces have required fields")
            return True
        except Exception as e:
            print(f"❌ Error validating interface structure: {e}")
            return False
    
    def validate_method_signatures(self) -> bool:
        """Validate method signature data structure"""
        print("🔍 Validating method signatures...")
        try:
            required_fields = ['interface_name', 'method_name', 'signature', 'return_type', 'is_abstract', 'is_public']
            
            for method in self.test_data['method_signatures']:
                for field in required_fields:
                    if field not in method:
                        print(f"❌ Missing field '{field}' in method {method.get('method_name', 'unknown')}")
                        return False
            
            print(f"✅ All {len(self.test_data['method_signatures'])} method signatures have required fields")
            return True
        except Exception as e:
            print(f"❌ Error validating method signatures: {e}")
            return False
    
    def validate_dependencies(self) -> bool:
        """Validate dependency data structure"""
        print("🔍 Validating dependencies...")
        try:
            required_fields = ['interface_name', 'dependency_type', 'dependency_name', 'is_external', 'is_circular', 'strength']
            
            for dep in self.test_data['dependencies']:
                for field in required_fields:
                    if field not in dep:
                        print(f"❌ Missing field '{field}' in dependency {dep.get('dependency_name', 'unknown')}")
                        return False
            
            print(f"✅ All {len(self.test_data['dependencies'])} dependencies have required fields")
            return True
        except Exception as e:
            print(f"❌ Error validating dependencies: {e}")
            return False
    
    def validate_capabilities(self) -> bool:
        """Validate capability data structure"""
        print("🔍 Validating capabilities...")
        try:
            required_fields = ['interface_name', 'capability', 'confidence', 'detected_by']
            
            for cap in self.test_data['capabilities']:
                for field in required_fields:
                    if field not in cap:
                        print(f"❌ Missing field '{field}' in capability {cap.get('capability', 'unknown')}")
                        return False
            
            print(f"✅ All {len(self.test_data['capabilities'])} capabilities have required fields")
            return True
        except Exception as e:
            print(f"❌ Error validating capabilities: {e}")
            return False
    
    def validate_dependency_graph(self) -> bool:
        """Validate dependency graph has no circular dependencies"""
        print("🔍 Validating dependency graph...")
        try:
            # Build dependency graph
            graph = {}
            for dep in self.test_data['dependencies']:
                interface = dep['interface_name']
                dependency = dep['dependency_name']
                if interface not in graph:
                    graph[interface] = set()
                graph[interface].add(dependency)
            
            # Check for circular dependencies
            def has_circular_dependency(node, visited, rec_stack):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, set()):
                    if neighbor not in visited:
                        if has_circular_dependency(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            visited = set()
            for node in graph:
                if node not in visited:
                    if has_circular_dependency(node, visited, set()):
                        print(f"❌ Circular dependency detected involving {node}")
                        return False
            
            print("✅ No circular dependencies found in dependency graph")
            return True
        except Exception as e:
            print(f"❌ Error validating dependency graph: {e}")
            return False
    
    def validate_signature_analysis(self) -> bool:
        """Validate that signature analysis captured real data"""
        print("🔍 Validating signature analysis...")
        try:
            # Check that we have real method signatures with type information
            real_signatures = 0
            for method in self.test_data['method_signatures']:
                if method['return_type'] != 'Any' and method['return_type'] != 'inspect.Parameter.empty':
                    real_signatures += 1
            
            if real_signatures < 10:  # We should have at least 10 real signatures
                print(f"❌ Only {real_signatures} real signatures found, expected more")
                return False
            
            print(f"✅ Found {real_signatures} real method signatures with type information")
            return True
        except Exception as e:
            print(f"❌ Error validating signature analysis: {e}")
            return False
    
    def validate_rdi_compliance(self) -> bool:
        """Validate RDI compliance markers"""
        print("🔍 Validating RDI compliance...")
        try:
            rdi_compliant_count = 0
            total_interfaces = len(self.test_data['interfaces'])
            
            for interface in self.test_data['interfaces']:
                if interface.get('rdi_compliant', False):
                    rdi_compliant_count += 1
            
            if rdi_compliant_count < total_interfaces * 0.8:  # At least 80% should be RDI compliant
                print(f"❌ Only {rdi_compliant_count}/{total_interfaces} interfaces are RDI compliant")
                return False
            
            print(f"✅ {rdi_compliant_count}/{total_interfaces} interfaces are RDI compliant")
            return True
        except Exception as e:
            print(f"❌ Error validating RDI compliance: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        print("🧪 Running Directus Data Validation Tests")
        print("=" * 50)
        
        if not self.load_test_data():
            return False
        
        tests = [
            ("Interface Structure", self.validate_interface_structure),
            ("Method Signatures", self.validate_method_signatures),
            ("Dependencies", self.validate_dependencies),
            ("Capabilities", self.validate_capabilities),
            ("Dependency Graph", self.validate_dependency_graph),
            ("Signature Analysis", self.validate_signature_analysis),
            ("RDI Compliance", self.validate_rdi_compliance),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}:")
            try:
                success = test_func()
                results.append((test_name, success))
                if success:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY:")
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} validations passed")
        
        if passed == total:
            print("🎉 ALL VALIDATIONS PASSED! Data is ready for Directus import.")
        else:
            print("⚠️  Some validations failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main validation function"""
    print("🚀 Starting Directus Data Validation")
    print("=" * 60)
    
    # Check if test data exists
    if not Path('directus_interface_export.json').exists():
        print("❌ Test data file 'directus_interface_export.json' not found!")
        print("   Run the migration script first: python3 src/rc1/implementation/directus_interface_registry_migration.py")
        return False
    
    # Run validations
    mock_test = DirectusMockTest()
    success = mock_test.run_all_tests()
    
    if success:
        print("\n🎉 Data validation complete! Ready for Directus import.")
        print("   - Data Structure: ✅ Valid")
        print("   - Signature Analysis: ✅ Working")
        print("   - Dependency Tracking: ✅ Working")
        print("   - RDI Compliance: ✅ Maintained")
        print("   - No Circular Dependencies: ✅ Clean")
    else:
        print("\n⚠️  Data validation failed. Fix issues before Directus import.")
    
    return success

if __name__ == "__main__":
    main()
