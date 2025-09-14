#!/usr/bin/env python3
"""
Focused Milestone Delivery Gates Check

This system verifies milestone delivery gates specifically for the
devpost_integration modules that were the focus of our RDI compliance work.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class FocusedMilestoneGates:
    """Focused milestone delivery gates check for devpost_integration modules."""
    
    def __init__(self):
        self.target_directory = "src/devpost_integration"
        self.gates = {}
        self.results = {}
        self.overall_status = "PENDING"
    
    def check_all_gates(self):
        """Check all milestone delivery gates for target modules."""
        print("🚪 FOCUSED MILESTONE DELIVERY GATES CHECK")
        print("=" * 60)
        print(f"Target Directory: {self.target_directory}")
        print(f"Check performed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Gate 1: RDI Compliance
        self.check_rdi_compliance_gate()
        
        # Gate 2: Size Compliance
        self.check_size_compliance_gate()
        
        # Gate 3: Health Monitoring
        self.check_health_monitoring_gate()
        
        # Gate 4: Registry Integration
        self.check_registry_integration_gate()
        
        # Gate 5: Interface Consolidation
        self.check_interface_consolidation_gate()
        
        # Gate 6: Test Suite
        self.check_test_suite_gate()
        
        # Gate 7: Documentation
        self.check_documentation_gate()
        
        # Gate 8: System Health
        self.check_system_health_gate()
        
        # Calculate overall status
        self.calculate_overall_status()
        
        # Generate report
        self.generate_delivery_report()
    
    def check_rdi_compliance_gate(self):
        """Check RDI compliance gate for target modules."""
        print("🔍 Gate 1: RDI Compliance (devpost_integration)")
        gate_status = "PASS"
        issues = []
        
        try:
            # Count modules in target directory
            target_modules = self.count_python_files(self.target_directory)
            
            # Count modules with ReflectiveModule
            reflective_modules = self.count_modules_with_reflective(self.target_directory)
            
            compliance_percentage = (reflective_modules / target_modules * 100) if target_modules > 0 else 0
            
            if compliance_percentage < 90:  # 90% threshold
                gate_status = "FAIL"
                issues.append(f"Only {reflective_modules}/{target_modules} modules inherit from ReflectiveModule ({compliance_percentage:.1f}%)")
            
            # Check for required methods
            required_methods = ['get_module_info', 'get_capabilities', 'check_health']
            missing_methods = self.check_required_methods(required_methods, self.target_directory)
            
            if missing_methods:
                gate_status = "FAIL"
                issues.append(f"Missing required methods: {', '.join(missing_methods)}")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking RDI compliance: {e}")
        
        self.gates['rdi_compliance'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"ReflectiveModule compliance: {reflective_modules}/{target_modules} ({compliance_percentage:.1f}%)"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_size_compliance_gate(self):
        """Check size compliance gate for target modules."""
        print("🔍 Gate 2: Size Compliance (devpost_integration)")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for files over 200 lines in target directory
            large_files = self.find_large_files(200, self.target_directory)
            
            if large_files:
                gate_status = "FAIL"
                issues.append(f"Found {len(large_files)} files over 200 lines in {self.target_directory}")
                for file_path, line_count in large_files[:5]:  # Show first 5
                    issues.append(f"  {file_path}: {line_count} lines")
            
            # Check average file size
            avg_size = self.calculate_average_file_size(self.target_directory)
            if avg_size > 150:  # Warning threshold
                issues.append(f"Average file size is high: {avg_size:.1f} lines")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking size compliance: {e}")
        
        self.gates['size_compliance'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Large files: {len(large_files) if 'large_files' in locals() else 0}, Avg size: {avg_size if 'avg_size' in locals() else 0:.1f}"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_health_monitoring_gate(self):
        """Check health monitoring gate for target modules."""
        print("🔍 Gate 3: Health Monitoring (devpost_integration)")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for health monitoring methods
            health_methods = ['check_health', 'get_health_indicators', 'get_status_report']
            modules_with_health = self.count_modules_with_methods(health_methods, self.target_directory)
            total_modules = self.count_python_files(self.target_directory)
            
            health_percentage = (modules_with_health / total_modules * 100) if total_modules > 0 else 0
            
            if health_percentage < 80:  # 80% threshold
                gate_status = "FAIL"
                issues.append(f"Only {modules_with_health}/{total_modules} modules have health monitoring ({health_percentage:.1f}%)")
            
            # Check for health dashboard
            if not os.path.exists("src/health_dashboard.py"):
                gate_status = "FAIL"
                issues.append("Health monitoring dashboard not found")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking health monitoring: {e}")
        
        self.gates['health_monitoring'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Health monitoring: {modules_with_health}/{total_modules} ({health_percentage:.1f}%)"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_registry_integration_gate(self):
        """Check registry integration gate for target modules."""
        print("🔍 Gate 4: Registry Integration (devpost_integration)")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for registry methods
            registry_methods = ['get_module_info', 'get_capabilities', 'get_dependencies', 'register_with_registry']
            modules_with_registry = self.count_modules_with_methods(registry_methods, self.target_directory)
            total_modules = self.count_python_files(self.target_directory)
            
            registry_percentage = (modules_with_registry / total_modules * 100) if total_modules > 0 else 0
            
            if registry_percentage < 80:  # 80% threshold
                gate_status = "FAIL"
                issues.append(f"Only {modules_with_registry}/{total_modules} modules have registry integration ({registry_percentage:.1f}%)")
            
            # Check for registry dashboard
            if not os.path.exists("src/registry_dashboard.py"):
                gate_status = "FAIL"
                issues.append("Registry monitoring dashboard not found")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking registry integration: {e}")
        
        self.gates['registry_integration'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Registry integration: {modules_with_registry}/{total_modules} ({registry_percentage:.1f}%)"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_interface_consolidation_gate(self):
        """Check interface consolidation gate."""
        print("🔍 Gate 5: Interface Consolidation")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for interface consolidation report
            if not os.path.exists("interface_consolidation_report.json"):
                gate_status = "FAIL"
                issues.append("Interface consolidation report not found")
            else:
                with open("interface_consolidation_report.json", 'r') as f:
                    report = json.load(f)
                
                consistency_score = report.get('summary', {}).get('consistency_score', 0)
                if consistency_score < 30:  # 30% threshold
                    gate_status = "FAIL"
                    issues.append(f"Consistency score too low: {consistency_score}%")
            
            # Check for authoritative interfaces
            interfaces_dir = Path("src/interfaces")
            if not interfaces_dir.exists():
                gate_status = "FAIL"
                issues.append("Authoritative interfaces directory not found")
            else:
                interface_files = list(interfaces_dir.glob("*.py"))
                if len(interface_files) < 10:  # Expect at least 10 interfaces
                    issues.append(f"Only {len(interface_files)} authoritative interfaces found")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking interface consolidation: {e}")
        
        self.gates['interface_consolidation'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Consistency score: {consistency_score if 'consistency_score' in locals() else 'unknown'}%"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_test_suite_gate(self):
        """Check test suite gate."""
        print("🔍 Gate 6: Test Suite")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for test files
            test_files = self.find_files("test_*.py", "tests")
            if len(test_files) < 5:
                gate_status = "FAIL"
                issues.append(f"Only {len(test_files)} test files found")
            
            # Check for test utilities
            if not os.path.exists("tests/test_utilities.py"):
                gate_status = "FAIL"
                issues.append("Test utilities not found")
            
            # Check for comprehensive test runner
            if not os.path.exists("tests/run_comprehensive_tests.py"):
                gate_status = "FAIL"
                issues.append("Comprehensive test runner not found")
            
            # Try to run a basic test
            try:
                result = subprocess.run(["python3", "-m", "pytest", "tests/test_basic.py", "-q"], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    gate_status = "FAIL"
                    issues.append("Basic tests are failing")
            except subprocess.TimeoutExpired:
                issues.append("Test execution timed out")
            except Exception as e:
                issues.append(f"Error running tests: {e}")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking test suite: {e}")
        
        self.gates['test_suite'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Test files: {len(test_files) if 'test_files' in locals() else 0}"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_documentation_gate(self):
        """Check documentation gate."""
        print("🔍 Gate 7: Documentation")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check for key documentation files
            required_docs = [
                "README.md",
                "RDI_COMPLIANCE_PROGRESS_REPORT.md",
                "RDI_ANALYSIS_SUMMARY.md"
            ]
            
            for doc in required_docs:
                if not os.path.exists(doc):
                    gate_status = "FAIL"
                    issues.append(f"Missing documentation: {doc}")
            
            # Check for inline documentation in target modules
            modules_with_docstrings = self.count_modules_with_docstrings(self.target_directory)
            total_modules = self.count_python_files(self.target_directory)
            
            doc_percentage = (modules_with_docstrings / total_modules * 100) if total_modules > 0 else 0
            
            if doc_percentage < 70:  # 70% threshold
                issues.append(f"Only {modules_with_docstrings}/{total_modules} modules have docstrings ({doc_percentage:.1f}%)")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking documentation: {e}")
        
        self.gates['documentation'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Docstrings: {modules_with_docstrings}/{total_modules} ({doc_percentage:.1f}%)"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def check_system_health_gate(self):
        """Check system health gate."""
        print("🔍 Gate 8: System Health")
        gate_status = "PASS"
        issues = []
        
        try:
            # Check system resources
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                gate_status = "FAIL"
                issues.append(f"Memory usage too high: {memory.percent}%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 95:
                gate_status = "FAIL"
                issues.append(f"Disk usage too high: {disk.percent}%")
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                issues.append(f"CPU usage high: {cpu_percent}%")
            
        except Exception as e:
            gate_status = "FAIL"
            issues.append(f"Error checking system health: {e}")
        
        self.gates['system_health'] = {
            'status': gate_status,
            'issues': issues,
            'details': f"Memory: {memory.percent if 'memory' in locals() else 'unknown'}%, Disk: {disk.percent if 'disk' in locals() else 'unknown'}%"
        }
        
        print(f"  Status: {gate_status}")
        if issues:
            for issue in issues:
                print(f"  Issue: {issue}")
        print()
    
    def calculate_overall_status(self):
        """Calculate overall milestone status."""
        total_gates = len(self.gates)
        passed_gates = sum(1 for gate in self.gates.values() if gate['status'] == 'PASS')
        
        if passed_gates == total_gates:
            self.overall_status = "PASS"
        elif passed_gates >= total_gates * 0.8:  # 80% threshold
            self.overall_status = "PASS_WITH_WARNINGS"
        else:
            self.overall_status = "FAIL"
    
    def generate_delivery_report(self):
        """Generate milestone delivery report."""
        print("=" * 60)
        print("📋 FOCUSED MILESTONE DELIVERY REPORT")
        print("=" * 60)
        
        total_gates = len(self.gates)
        passed_gates = sum(1 for gate in self.gates.values() if gate['status'] == 'PASS')
        failed_gates = sum(1 for gate in self.gates.values() if gate['status'] == 'FAIL')
        
        print(f"Target Directory: {self.target_directory}")
        print(f"Overall Status: {self.overall_status}")
        print(f"Gates Passed: {passed_gates}/{total_gates}")
        print(f"Gates Failed: {failed_gates}/{total_gates}")
        print()
        
        if self.overall_status == "PASS":
            print("🎉 ALL FOCUSED MILESTONE DELIVERY GATES PASSED!")
            print("✅ The devpost_integration modules are ready for delivery!")
        elif self.overall_status == "PASS_WITH_WARNINGS":
            print("⚠️  FOCUSED MILESTONE DELIVERY GATES PASSED WITH WARNINGS")
            print("✅ The devpost_integration modules are ready for delivery with minor issues to address.")
        else:
            print("❌ FOCUSED MILESTONE DELIVERY GATES FAILED")
            print("🚫 The devpost_integration modules are NOT ready for delivery.")
            print("Please address the failed gates before proceeding.")
        
        print()
        print("Gate Details:")
        for gate_name, gate_data in self.gates.items():
            status_icon = "✅" if gate_data['status'] == 'PASS' else "❌"
            print(f"  {status_icon} {gate_name.replace('_', ' ').title()}: {gate_data['status']}")
            if gate_data['issues']:
                for issue in gate_data['issues']:
                    print(f"    - {issue}")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'target_directory': self.target_directory,
            'overall_status': self.overall_status,
            'total_gates': total_gates,
            'passed_gates': passed_gates,
            'failed_gates': failed_gates,
            'gates': self.gates
        }
        
        with open('focused_milestone_delivery_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: focused_milestone_delivery_report.json")
    
    # Helper methods
    def count_python_files(self, directory):
        """Count Python files in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    count += 1
        return count
    
    def count_modules_with_reflective(self, directory):
        """Count modules that inherit from ReflectiveModule."""
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        if 'ReflectiveModule' in content and 'class ' in content:
                            count += 1
                    except:
                        pass
        return count
    
    def check_required_methods(self, methods, directory):
        """Check for required methods in directory."""
        missing = []
        for method in methods:
            found = False
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                            if f"def {method}(" in content:
                                found = True
                                break
                        except:
                            pass
            if not found:
                missing.append(method)
        return missing
    
    def find_large_files(self, max_lines, directory):
        """Find files over max_lines in directory."""
        large_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            line_count = len(f.readlines())
                        if line_count > max_lines:
                            large_files.append((file_path, line_count))
                    except:
                        pass
        return large_files
    
    def calculate_average_file_size(self, directory):
        """Calculate average file size in directory."""
        total_lines = 0
        file_count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            total_lines += len(f.readlines())
                        file_count += 1
                    except:
                        pass
        return total_lines / file_count if file_count > 0 else 0
    
    def count_modules_with_methods(self, methods, directory):
        """Count modules that have all specified methods in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        if all(f"def {method}(" in content for method in methods):
                            count += 1
                    except:
                        pass
        return count
    
    def count_modules_with_docstrings(self, directory):
        """Count modules with docstrings in directory."""
        count = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        if '"""' in content or "'''" in content:
                            count += 1
                    except:
                        pass
        return count
    
    def find_files(self, pattern, directory="tests"):
        """Find files matching pattern in directory."""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if pattern in filename:
                    files.append(os.path.join(root, filename))
        return files

def main():
    """Main focused milestone delivery gates check."""
    gates = FocusedMilestoneGates()
    gates.check_all_gates()

if __name__ == "__main__":
    main()
