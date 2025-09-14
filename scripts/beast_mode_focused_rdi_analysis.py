#!/usr/bin/env python3
"""
🚀 BEAST MODE FOCUSED RDI ANALYSIS
=================================
Focused RDI analysis on key modified files for requirements compliance.
"""

import os
import sys
import json
import ast
import re
from datetime import datetime
from pathlib import Path

class BeastModeFocusedRDIAnalysis:
    """Focused RDI Analysis for key modified files"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.key_files = [
            'src/rm_ddd/core/unified_reflective_module.py',
            'src/rm_ddd/core/interface_registry.py',
            'src/rm_ddd/core/compliance.py',
            'src/rm_ddd/core/enhanced_interface_registry.py',
            'src/rm_ddd/core/interface_governance_system.py',
            'src/beast_mode/core/exceptions.py',
            'src/beast_mode/core/pdca_models.py',
            'src/beast_mode/core/safe_subprocess.py',
            'src/beast_mode/compliance/rm/rm_validator.py',
            'src/beast_mode/backlog/beast_readiness_validator.py'
        ]
        
    def run_focused_rdi_analysis(self):
        """Run focused RDI analysis on key files"""
        print("🚀 BEAST MODE FOCUSED RDI ANALYSIS")
        print("=" * 60)
        print("📊 Requirements-Driven Implementation Analysis")
        print("🎯 Focused analysis on key modified files")
        print()
        
        # Phase 1: Analyze Key Files
        print("🔍 PHASE 1: ANALYZING KEY MODIFIED FILES")
        print("=" * 40)
        
        file_analysis = self.analyze_key_files()
        
        # Phase 2: Requirements Extraction
        print("\n📝 PHASE 2: REQUIREMENTS EXTRACTION")
        print("=" * 40)
        
        requirements = self.extract_requirements(file_analysis)
        
        # Phase 3: Compliance Assessment
        print("\n✅ PHASE 3: COMPLIANCE ASSESSMENT")
        print("=" * 40)
        
        compliance = self.assess_compliance(file_analysis, requirements)
        
        # Phase 4: Gap Analysis
        print("\n🎯 PHASE 4: GAP ANALYSIS")
        print("=" * 40)
        
        gaps = self.analyze_gaps(compliance)
        
        # Phase 5: Solution Generation
        print("\n🔧 PHASE 5: REQUIREMENTS-CONFORMING SOLUTION")
        print("=" * 40)
        
        solution = self.generate_solution(gaps)
        
        # Generate report
        self.generate_report(file_analysis, requirements, compliance, gaps, solution)
        
        return True
    
    def analyze_key_files(self):
        """Analyze key modified files"""
        print("🔍 Analyzing key modified files...")
        
        file_analysis = {}
        
        for file_path in self.key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parse AST
                    tree = ast.parse(content)
                    
                    # Extract information
                    file_info = {
                        'path': file_path,
                        'size': len(content),
                        'lines': len(content.split('\n')),
                        'classes': [],
                        'functions': [],
                        'imports': [],
                        'docstrings': []
                    }
                    
                    # Extract classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_info = {
                                'name': node.name,
                                'line': node.lineno,
                                'docstring': ast.get_docstring(node) or '',
                                'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                                'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                            }
                            file_info['classes'].append(class_info)
                        
                        elif isinstance(node, ast.FunctionDef):
                            function_info = {
                                'name': node.name,
                                'line': node.lineno,
                                'docstring': ast.get_docstring(node) or '',
                                'args': [arg.arg for arg in node.args.args],
                                'is_method': any(arg == 'self' for arg in [arg.arg for arg in node.args.args])
                            }
                            file_info['functions'].append(function_info)
                        
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                file_info['imports'].append({
                                    'type': 'import',
                                    'name': alias.name,
                                    'alias': alias.asname,
                                    'line': node.lineno
                                })
                        
                        elif isinstance(node, ast.ImportFrom):
                            for alias in node.names:
                                file_info['imports'].append({
                                    'type': 'import_from',
                                    'module': node.module,
                                    'name': alias.name,
                                    'alias': alias.asname,
                                    'line': node.lineno
                                })
                    
                    # Extract docstrings
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '"""' in line or "'''" in line:
                            file_info['docstrings'].append({
                                'line': i + 1,
                                'content': line.strip()
                            })
                    
                    file_analysis[file_path] = file_info
                    print(f"      ✅ Analyzed: {os.path.basename(file_path)} ({len(file_info['classes'])} classes, {len(file_info['functions'])} functions)")
                    
                except Exception as e:
                    print(f"      ❌ Error analyzing {file_path}: {e}")
                    continue
        
        print(f"      📊 Successfully analyzed {len(file_analysis)} key files")
        return file_analysis
    
    def extract_requirements(self, file_analysis):
        """Extract requirements from file analysis"""
        print("📝 Extracting requirements from file analysis...")
        
        requirements = {
            'functional': [],
            'interface': [],
            'compliance': [],
            'architecture': []
        }
        
        for file_path, file_info in file_analysis.items():
            # Extract functional requirements from classes
            for class_info in file_info['classes']:
                class_name = class_info['name']
                
                # Interface Registry requirements
                if 'InterfaceRegistry' in class_name:
                    requirements['functional'].append({
                        'id': 'IFR-001',
                        'description': 'Interface Registry should manage interface metadata',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'functional'
                    })
                    requirements['interface'].append({
                        'id': 'IFR-002',
                        'description': 'Interface Registry should provide registration methods',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'interface'
                    })
                
                # Compliance requirements
                elif 'Compliance' in class_name:
                    requirements['compliance'].append({
                        'id': 'COMP-001',
                        'description': 'Compliance system should validate interface standards',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'compliance'
                    })
                
                # Reflective Module requirements
                elif 'ReflectiveModule' in class_name:
                    requirements['architecture'].append({
                        'id': 'ARCH-001',
                        'description': 'Reflective Module should support introspection',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'architecture'
                    })
                    requirements['functional'].append({
                        'id': 'RFM-001',
                        'description': 'Reflective Module should register with interface registry',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'functional'
                    })
                
                # Validator requirements
                elif 'Validator' in class_name:
                    requirements['functional'].append({
                        'id': 'VAL-001',
                        'description': f'{class_name} should validate inputs and outputs',
                        'priority': 'medium',
                        'source': file_path,
                        'type': 'functional'
                    })
            
            # Extract requirements from functions
            for function_info in file_info['functions']:
                func_name = function_info['name']
                
                if func_name.startswith('register_'):
                    requirements['functional'].append({
                        'id': f'REG-{func_name.upper()}',
                        'description': f'{func_name} should register interfaces properly',
                        'priority': 'high',
                        'source': file_path,
                        'type': 'functional'
                    })
                
                elif func_name.startswith('validate_'):
                    requirements['compliance'].append({
                        'id': f'VAL-{func_name.upper()}',
                        'description': f'{func_name} should validate compliance',
                        'priority': 'medium',
                        'source': file_path,
                        'type': 'compliance'
                    })
                
                elif func_name.startswith('get_') or func_name.startswith('retrieve_'):
                    requirements['functional'].append({
                        'id': f'GET-{func_name.upper()}',
                        'description': f'{func_name} should retrieve data correctly',
                        'priority': 'medium',
                        'source': file_path,
                        'type': 'functional'
                    })
            
            # Extract requirements from imports
            for import_info in file_info['imports']:
                if import_info['name'] in ['abc', 'typing', 'enum']:
                    requirements['architecture'].append({
                        'id': f'IMPORT-{import_info["name"].upper()}',
                        'description': f'Should use {import_info["name"]} for type safety',
                        'priority': 'medium',
                        'source': file_path,
                        'type': 'architecture'
                    })
        
        print(f"      📊 Requirements extracted:")
        print(f"         • Functional: {len(requirements['functional'])}")
        print(f"         • Interface: {len(requirements['interface'])}")
        print(f"         • Compliance: {len(requirements['compliance'])}")
        print(f"         • Architecture: {len(requirements['architecture'])}")
        
        return requirements
    
    def assess_compliance(self, file_analysis, requirements):
        """Assess compliance with requirements"""
        print("✅ Assessing compliance with requirements...")
        
        compliance = {
            'overall_score': 0.0,
            'functional_score': 0.0,
            'interface_score': 0.0,
            'compliance_score': 0.0,
            'architecture_score': 0.0,
            'detailed_assessment': []
        }
        
        # Assess functional compliance
        functional_reqs = requirements['functional']
        functional_compliant = 0
        
        for req in functional_reqs:
            if self.check_functional_compliance(file_analysis, req):
                functional_compliant += 1
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'compliant',
                    'score': 1.0,
                    'description': req['description']
                })
            else:
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'non_compliant',
                    'score': 0.0,
                    'description': req['description'],
                    'gap': f'Missing implementation for {req["description"]}'
                })
        
        compliance['functional_score'] = (functional_compliant / len(functional_reqs) * 100) if functional_reqs else 100
        
        # Assess interface compliance
        interface_reqs = requirements['interface']
        interface_compliant = 0
        
        for req in interface_reqs:
            if self.check_interface_compliance(file_analysis, req):
                interface_compliant += 1
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'compliant',
                    'score': 1.0,
                    'description': req['description']
                })
            else:
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'non_compliant',
                    'score': 0.0,
                    'description': req['description'],
                    'gap': f'Missing interface implementation for {req["description"]}'
                })
        
        compliance['interface_score'] = (interface_compliant / len(interface_reqs) * 100) if interface_reqs else 100
        
        # Assess compliance requirements
        compliance_reqs = requirements['compliance']
        compliance_compliant = 0
        
        for req in compliance_reqs:
            if self.check_compliance_requirement(file_analysis, req):
                compliance_compliant += 1
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'compliant',
                    'score': 1.0,
                    'description': req['description']
                })
            else:
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'non_compliant',
                    'score': 0.0,
                    'description': req['description'],
                    'gap': f'Missing compliance implementation for {req["description"]}'
                })
        
        compliance['compliance_score'] = (compliance_compliant / len(compliance_reqs) * 100) if compliance_reqs else 100
        
        # Assess architecture compliance
        architecture_reqs = requirements['architecture']
        architecture_compliant = 0
        
        for req in architecture_reqs:
            if self.check_architecture_compliance(file_analysis, req):
                architecture_compliant += 1
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'compliant',
                    'score': 1.0,
                    'description': req['description']
                })
            else:
                compliance['detailed_assessment'].append({
                    'requirement_id': req['id'],
                    'status': 'non_compliant',
                    'score': 0.0,
                    'description': req['description'],
                    'gap': f'Missing architecture implementation for {req["description"]}'
                })
        
        compliance['architecture_score'] = (architecture_compliant / len(architecture_reqs) * 100) if architecture_reqs else 100
        
        # Calculate overall score
        total_reqs = len(functional_reqs) + len(interface_reqs) + len(compliance_reqs) + len(architecture_reqs)
        total_compliant = functional_compliant + interface_compliant + compliance_compliant + architecture_compliant
        compliance['overall_score'] = (total_compliant / total_reqs * 100) if total_reqs > 0 else 100
        
        print(f"      📊 Compliance Assessment:")
        print(f"         • Overall: {compliance['overall_score']:.1f}%")
        print(f"         • Functional: {compliance['functional_score']:.1f}%")
        print(f"         • Interface: {compliance['interface_score']:.1f}%")
        print(f"         • Compliance: {compliance['compliance_score']:.1f}%")
        print(f"         • Architecture: {compliance['architecture_score']:.1f}%")
        
        return compliance
    
    def check_functional_compliance(self, file_analysis, requirement):
        """Check functional compliance for a requirement"""
        req_id = requirement['id']
        
        if req_id == 'IFR-001':  # Interface Registry should manage interface metadata
            for file_path, file_info in file_analysis.items():
                for class_info in file_info['classes']:
                    if 'InterfaceRegistry' in class_info['name']:
                        # Check if class has methods to manage metadata
                        metadata_methods = ['register', 'get_metadata', 'save_metadata', 'load_metadata']
                        if any(method in ' '.join(class_info['methods']) for method in metadata_methods):
                            return True
        
        elif req_id == 'RFM-001':  # Reflective Module should register with interface registry
            for file_path, file_info in file_analysis.items():
                for class_info in file_info['classes']:
                    if 'ReflectiveModule' in class_info['name']:
                        # Check if class has registration methods
                        registration_methods = ['register', 'register_interface', '_register_interface']
                        if any(method in ' '.join(class_info['methods']) for method in registration_methods):
                            return True
        
        elif 'REG-' in req_id:  # Registration methods
            for file_path, file_info in file_analysis.items():
                for function_info in file_info['functions']:
                    if function_info['name'].startswith('register_'):
                        return True
        
        elif 'GET-' in req_id:  # Get methods
            for file_path, file_info in file_analysis.items():
                for function_info in file_info['functions']:
                    if function_info['name'].startswith('get_') or function_info['name'].startswith('retrieve_'):
                        return True
        
        return False
    
    def check_interface_compliance(self, file_analysis, requirement):
        """Check interface compliance for a requirement"""
        req_id = requirement['id']
        
        if req_id == 'IFR-002':  # Interface Registry should provide registration methods
            for file_path, file_info in file_analysis.items():
                for class_info in file_info['classes']:
                    if 'InterfaceRegistry' in class_info['name']:
                        # Check if class has registration methods
                        registration_methods = ['register', 'register_interface', 'add_interface']
                        if any(method in ' '.join(class_info['methods']) for method in registration_methods):
                            return True
        
        return False
    
    def check_compliance_requirement(self, file_analysis, requirement):
        """Check compliance requirement"""
        req_id = requirement['id']
        
        if req_id == 'COMP-001':  # Compliance system should validate interface standards
            for file_path, file_info in file_analysis.items():
                for class_info in file_info['classes']:
                    if 'Compliance' in class_info['name']:
                        # Check if class has validation methods
                        validation_methods = ['validate', 'check_compliance', 'assess']
                        if any(method in ' '.join(class_info['methods']) for method in validation_methods):
                            return True
        
        elif 'VAL-' in req_id:  # Validation methods
            for file_path, file_info in file_analysis.items():
                for function_info in file_info['functions']:
                    if function_info['name'].startswith('validate_'):
                        return True
        
        return False
    
    def check_architecture_compliance(self, file_analysis, requirement):
        """Check architecture compliance"""
        req_id = requirement['id']
        
        if req_id == 'ARCH-001':  # Reflective Module should support introspection
            for file_path, file_info in file_analysis.items():
                for class_info in file_info['classes']:
                    if 'ReflectiveModule' in class_info['name']:
                        # Check if class has introspection methods
                        introspection_methods = ['get_methods', 'get_attributes', 'introspect', 'inspect']
                        if any(method in ' '.join(class_info['methods']) for method in introspection_methods):
                            return True
        
        elif 'IMPORT-' in req_id:  # Import requirements
            import_name = req_id.split('-')[1].lower()
            for file_path, file_info in file_analysis.items():
                for import_info in file_info['imports']:
                    if import_info['name'] == import_name:
                        return True
        
        return False
    
    def analyze_gaps(self, compliance):
        """Analyze gaps in compliance"""
        print("🎯 Analyzing compliance gaps...")
        
        gaps = {
            'critical_gaps': [],
            'high_priority_gaps': [],
            'medium_priority_gaps': [],
            'recommendations': []
        }
        
        # Identify gaps based on compliance scores
        if compliance['overall_score'] < 70:
            gaps['critical_gaps'].append({
                'area': 'Overall Compliance',
                'current_score': compliance['overall_score'],
                'target_score': 90,
                'description': 'Overall compliance below critical threshold'
            })
        
        if compliance['functional_score'] < 80:
            gaps['high_priority_gaps'].append({
                'area': 'Functional Compliance',
                'current_score': compliance['functional_score'],
                'target_score': 90,
                'description': 'Functional requirements not fully implemented'
            })
        
        if compliance['interface_score'] < 80:
            gaps['high_priority_gaps'].append({
                'area': 'Interface Compliance',
                'current_score': compliance['interface_score'],
                'target_score': 90,
                'description': 'Interface requirements not fully implemented'
            })
        
        if compliance['compliance_score'] < 70:
            gaps['medium_priority_gaps'].append({
                'area': 'Compliance System',
                'current_score': compliance['compliance_score'],
                'target_score': 80,
                'description': 'Compliance validation needs improvement'
            })
        
        if compliance['architecture_score'] < 70:
            gaps['medium_priority_gaps'].append({
                'area': 'Architecture Compliance',
                'current_score': compliance['architecture_score'],
                'target_score': 80,
                'description': 'Architecture patterns need improvement'
            })
        
        # Generate recommendations
        for gap in gaps['critical_gaps']:
            gaps['recommendations'].append({
                'priority': 'critical',
                'action': f'Immediate action required to improve {gap["area"]} from {gap["current_score"]:.1f}% to {gap["target_score"]:.1f}%',
                'implementation': f'Implement comprehensive {gap["area"].lower()} improvement plan'
            })
        
        for gap in gaps['high_priority_gaps']:
            gaps['recommendations'].append({
                'priority': 'high',
                'action': f'Priority action to improve {gap["area"]} from {gap["current_score"]:.1f}% to {gap["target_score"]:.1f}%',
                'implementation': f'Focus on {gap["area"].lower()} enhancement'
            })
        
        for gap in gaps['medium_priority_gaps']:
            gaps['recommendations'].append({
                'priority': 'medium',
                'action': f'Improvement needed for {gap["area"]} from {gap["current_score"]:.1f}% to {gap["target_score"]:.1f}%',
                'implementation': f'Plan {gap["area"].lower()} improvements'
            })
        
        print(f"      📊 Gap Analysis Results:")
        print(f"         • Critical Gaps: {len(gaps['critical_gaps'])}")
        print(f"         • High Priority Gaps: {len(gaps['high_priority_gaps'])}")
        print(f"         • Medium Priority Gaps: {len(gaps['medium_priority_gaps'])}")
        print(f"         • Recommendations: {len(gaps['recommendations'])}")
        
        return gaps
    
    def generate_solution(self, gaps):
        """Generate requirements-conforming solution"""
        print("🔧 Generating requirements-conforming solution...")
        
        solution = {
            'implementation_plan': [],
            'compliance_improvements': [],
            'architecture_enhancements': [],
            'testing_strategy': []
        }
        
        # Generate implementation plan based on gaps
        for gap in gaps['critical_gaps'] + gaps['high_priority_gaps']:
            solution['implementation_plan'].append({
                'phase': 'immediate' if gap in gaps['critical_gaps'] else 'priority',
                'area': gap['area'],
                'actions': [
                    f'Review {gap["area"].lower()} requirements',
                    f'Implement missing functionality',
                    f'Validate {gap["area"].lower()} compliance',
                    f'Test {gap["area"].lower()} implementation'
                ],
                'timeline': '1-2 weeks',
                'success_criteria': f'Achieve {gap["target_score"]:.1f}% compliance'
            })
        
        # Generate compliance improvements
        solution['compliance_improvements'] = [
            'Implement comprehensive interface registration validation',
            'Establish compliance monitoring system',
            'Create automated compliance checks',
            'Develop compliance reporting dashboard'
        ]
        
        # Generate architecture enhancements
        solution['architecture_enhancements'] = [
            'Implement proper interface segregation in ReflectiveModule',
            'Establish clear architectural boundaries',
            'Improve dependency management',
            'Enhance introspection capabilities'
        ]
        
        # Generate testing strategy
        solution['testing_strategy'] = [
            'Implement requirements-based testing for all interfaces',
            'Create compliance validation tests',
            'Establish continuous compliance monitoring',
            'Develop automated testing pipeline'
        ]
        
        print(f"      📊 Conforming Solution Generated:")
        print(f"         • Implementation Plan: {len(solution['implementation_plan'])} phases")
        print(f"         • Compliance Improvements: {len(solution['compliance_improvements'])} items")
        print(f"         • Architecture Enhancements: {len(solution['architecture_enhancements'])} items")
        print(f"         • Testing Strategy: {len(solution['testing_strategy'])} items")
        
        return solution
    
    def generate_report(self, file_analysis, requirements, compliance, gaps, solution):
        """Generate comprehensive RDI analysis report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'Focused Requirements-Driven Implementation Analysis',
            'scope': 'Key Modified Files - Classes, Functions, and Enums',
            'files_analyzed': len(file_analysis),
            'file_details': file_analysis,
            'requirements_analysis': requirements,
            'compliance_assessment': compliance,
            'gap_analysis': gaps,
            'conforming_solution': solution,
            'summary': {
                'overall_compliance': compliance['overall_score'],
                'functional_compliance': compliance['functional_score'],
                'interface_compliance': compliance['interface_score'],
                'compliance_score': compliance['compliance_score'],
                'architecture_compliance': compliance['architecture_score'],
                'critical_gaps': len(gaps['critical_gaps']),
                'high_priority_gaps': len(gaps['high_priority_gaps']),
                'medium_priority_gaps': len(gaps['medium_priority_gaps']),
                'recommendations': len(gaps['recommendations'])
            }
        }
        
        os.makedirs('.beast_mode', exist_ok=True)
        with open('.beast_mode/beast_mode_focused_rdi_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Focused RDI analysis report saved to .beast_mode/beast_mode_focused_rdi_report.json")
        
        # Print summary
        print(f"\n📊 FOCUSED RDI ANALYSIS SUMMARY")
        print("=" * 40)
        print(f"   📁 Files Analyzed: {len(file_analysis)}")
        print(f"   📝 Requirements Identified: {sum(len(reqs) for reqs in requirements.values())}")
        print(f"   ✅ Overall Compliance: {compliance['overall_score']:.1f}%")
        print(f"   🎯 Critical Gaps: {len(gaps['critical_gaps'])}")
        print(f"   🔧 Implementation Plan Phases: {len(solution['implementation_plan'])}")
        
        # Print detailed compliance breakdown
        print(f"\n📊 DETAILED COMPLIANCE BREAKDOWN")
        print("=" * 40)
        print(f"   🔧 Functional Compliance: {compliance['functional_score']:.1f}%")
        print(f"   🔌 Interface Compliance: {compliance['interface_score']:.1f}%")
        print(f"   ✅ Compliance System: {compliance['compliance_score']:.1f}%")
        print(f"   🏗️  Architecture Compliance: {compliance['architecture_score']:.1f}%")
        
        # Print recommendations
        print(f"\n🎯 KEY RECOMMENDATIONS")
        print("=" * 40)
        for i, rec in enumerate(gaps['recommendations'][:5], 1):
            print(f"   {i}. [{rec['priority'].upper()}] {rec['action']}")
        
        return report_data

if __name__ == "__main__":
    analysis = BeastModeFocusedRDIAnalysis()
    success = analysis.run_focused_rdi_analysis()
    
    if success:
        print("\n🎉 BEAST MODE FOCUSED RDI ANALYSIS COMPLETE!")
        print("📊 Requirements-to-implementation analysis successful!")
        sys.exit(0)
    else:
        print("\n❌ BEAST MODE FOCUSED RDI ANALYSIS FAILED")
        print("🔧 Analysis encountered errors")
        sys.exit(1)

