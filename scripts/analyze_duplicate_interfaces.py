#!/usr/bin/env python3
"""
Beast Mode: Duplicate Interface Analysis

Analyzes all duplicate interfaces to understand patterns and create
systematic consolidation strategy for full compliance spread.
"""

import sys
import os
import json
from collections import defaultdict, Counter
from typing import Dict, List, Any, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_registry_data():
    """Load registry data from files."""
    registry_file = '.beast_mode/interface_registry.json'
    enhanced_file = '.beast_mode/enhanced_interface_registry.json'
    
    registry_data = {}
    enhanced_data = {}
    
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            registry_data = json.load(f)
    
    if os.path.exists(enhanced_file):
        with open(enhanced_file, 'r') as f:
            enhanced_data = json.load(f)
    
    return registry_data, enhanced_data

def analyze_duplicate_patterns(registry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze duplicate interface patterns."""
    print("🔍 Analyzing Duplicate Interface Patterns...")
    
    # Group interfaces by name
    interfaces_by_name = defaultdict(list)
    interfaces_by_type = defaultdict(list)
    interfaces_by_file = defaultdict(list)
    
    # Analyze main interfaces
    for interface_name, interface_data in registry_data.get('interfaces', {}).items():
        interfaces_by_name[interface_name].append(interface_data)
        interfaces_by_type[interface_data.get('interface_type', 'unknown')].append(interface_data)
        interfaces_by_file[interface_data.get('file_path', 'unknown')].append(interface_data)
    
    # Analyze duplicates
    duplicates = registry_data.get('duplicates', [])
    conflicts = registry_data.get('conflicts', [])
    
    # Group duplicates by name
    duplicate_groups = defaultdict(list)
    for dup in duplicates:
        interface_name = dup.get('interface_name', 'unknown')
        duplicate_groups[interface_name].append(dup)
    
    # Analyze duplicate patterns
    patterns = {
        'total_duplicates': len(duplicates),
        'duplicate_names': list(duplicate_groups.keys()),
        'duplicate_groups': dict(duplicate_groups),
        'interface_types_with_duplicates': set(),
        'files_with_duplicates': set(),
        'common_duplicate_patterns': Counter(),
        'consolidation_candidates': [],
        'priority_consolidations': []
    }
    
    # Analyze each duplicate group
    for interface_name, dup_list in duplicate_groups.items():
        if len(dup_list) > 1:
            # Get interface types
            types = [dup.get('interface_type', 'unknown') for dup in dup_list]
            patterns['interface_types_with_duplicates'].update(types)
            
            # Get file paths
            files = [dup.get('file_path', 'unknown') for dup in dup_list]
            patterns['files_with_duplicates'].update(files)
            
            # Analyze patterns
            if all(t == types[0] for t in types):
                patterns['common_duplicate_patterns']['same_type_duplicates'] += 1
            else:
                patterns['common_duplicate_patterns']['mixed_type_duplicates'] += 1
            
            # Check if files are in same directory
            dirs = [os.path.dirname(f) for f in files if f != 'unknown']
            if len(set(dirs)) == 1 and len(dirs) > 1:
                patterns['common_duplicate_patterns']['same_directory_duplicates'] += 1
                patterns['priority_consolidations'].append({
                    'interface_name': interface_name,
                    'reason': 'same_directory',
                    'directory': dirs[0],
                    'count': len(dup_list)
                })
            
            # Check for backup files
            backup_files = [f for f in files if 'backup' in f.lower() or '.backup_' in f]
            if backup_files:
                patterns['common_duplicate_patterns']['backup_file_duplicates'] += 1
                patterns['priority_consolidations'].append({
                    'interface_name': interface_name,
                    'reason': 'backup_files',
                    'backup_files': backup_files,
                    'count': len(dup_list)
                })
            
            # Check for versioned files
            versioned_files = [f for f in files if any(v in f for v in ['_v2', '_v3', '_core', '_core_core'])]
            if versioned_files:
                patterns['common_duplicate_patterns']['versioned_file_duplicates'] += 1
                patterns['priority_consolidations'].append({
                    'interface_name': interface_name,
                    'reason': 'versioned_files',
                    'versioned_files': versioned_files,
                    'count': len(dup_list)
                })
            
            # Add to consolidation candidates
            patterns['consolidation_candidates'].append({
                'interface_name': interface_name,
                'duplicates': dup_list,
                'consolidation_priority': len(dup_list),
                'types': types,
                'files': files
            })
    
    # Convert sets to lists for JSON serialization
    patterns['interface_types_with_duplicates'] = list(patterns['interface_types_with_duplicates'])
    patterns['files_with_duplicates'] = list(patterns['files_with_duplicates'])
    patterns['common_duplicate_patterns'] = dict(patterns['common_duplicate_patterns'])
    
    return patterns

def analyze_interface_quality(enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze interface quality metrics."""
    print("📊 Analyzing Interface Quality Metrics...")
    
    interfaces = enhanced_data.get('interfaces', {})
    
    quality_metrics = {
        'total_interfaces': len(interfaces),
        'interfaces_with_methods': 0,
        'interfaces_with_docstrings': 0,
        'interfaces_with_type_annotations': 0,
        'compliance_scores': [],
        'interface_types': Counter(),
        'file_distribution': Counter(),
        'quality_issues': [],
        'improvement_candidates': []
    }
    
    for interface_name, interface_data in interfaces.items():
        # Count interfaces with methods
        methods = interface_data.get('methods', [])
        if methods:
            quality_metrics['interfaces_with_methods'] += 1
        
        # Check for docstrings
        if any(method.get('docstring') for method in methods):
            quality_metrics['interfaces_with_docstrings'] += 1
        
        # Check for type annotations
        if any(method.get('type_annotations') for method in methods):
            quality_metrics['interfaces_with_type_annotations'] += 1
        
        # Collect compliance scores
        compliance = interface_data.get('compliance_score', 0)
        quality_metrics['compliance_scores'].append(compliance)
        
        # Count interface types
        interface_type = interface_data.get('interface_type', 'unknown')
        quality_metrics['interface_types'][interface_type] += 1
        
        # Count file distribution
        file_path = interface_data.get('file_path', 'unknown')
        directory = os.path.dirname(file_path)
        quality_metrics['file_distribution'][directory] += 1
        
        # Identify quality issues
        if compliance < 50:
            quality_metrics['quality_issues'].append({
                'interface_name': interface_name,
                'issue': 'low_compliance',
                'compliance_score': compliance,
                'file_path': file_path
            })
        
        # Identify improvement candidates
        if compliance < 70 and len(methods) > 0:
            quality_metrics['improvement_candidates'].append({
                'interface_name': interface_name,
                'compliance_score': compliance,
                'method_count': len(methods),
                'file_path': file_path,
                'improvement_potential': 100 - compliance
            })
    
    # Calculate averages
    if quality_metrics['compliance_scores']:
        quality_metrics['average_compliance'] = sum(quality_metrics['compliance_scores']) / len(quality_metrics['compliance_scores'])
        quality_metrics['min_compliance'] = min(quality_metrics['compliance_scores'])
        quality_metrics['max_compliance'] = max(quality_metrics['compliance_scores'])
    
    # Convert counters to dicts
    quality_metrics['interface_types'] = dict(quality_metrics['interface_types'])
    quality_metrics['file_distribution'] = dict(quality_metrics['file_distribution'])
    
    return quality_metrics

def generate_consolidation_strategy(patterns: Dict[str, Any], quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate systematic consolidation strategy."""
    print("🎯 Generating Consolidation Strategy...")
    
    strategy = {
        'consolidation_phases': [],
        'priority_actions': [],
        'estimated_impact': {},
        'compliance_targets': {},
        'risk_assessment': {}
    }
    
    # Phase 1: Remove backup files
    backup_consolidations = [p for p in patterns['priority_consolidations'] if p['reason'] == 'backup_files']
    if backup_consolidations:
        strategy['consolidation_phases'].append({
            'phase': 1,
            'name': 'Backup File Cleanup',
            'description': 'Remove duplicate interfaces from backup files',
            'actions': [
                {
                    'action': 'delete_backup_files',
                    'targets': backup_consolidations,
                    'estimated_reduction': len(backup_consolidations),
                    'risk': 'low'
                }
            ]
        })
    
    # Phase 2: Consolidate versioned files
    versioned_consolidations = [p for p in patterns['priority_consolidations'] if p['reason'] == 'versioned_files']
    if versioned_consolidations:
        strategy['consolidation_phases'].append({
            'phase': 2,
            'name': 'Versioned File Consolidation',
            'description': 'Consolidate duplicate interfaces from versioned files',
            'actions': [
                {
                    'action': 'consolidate_versioned_files',
                    'targets': versioned_consolidations,
                    'estimated_reduction': len(versioned_consolidations),
                    'risk': 'medium'
                }
            ]
        })
    
    # Phase 3: Same directory consolidation
    same_dir_consolidations = [p for p in patterns['priority_consolidations'] if p['reason'] == 'same_directory']
    if same_dir_consolidations:
        strategy['consolidation_phases'].append({
            'phase': 3,
            'name': 'Same Directory Consolidation',
            'description': 'Consolidate duplicate interfaces in same directories',
            'actions': [
                {
                    'action': 'consolidate_same_directory',
                    'targets': same_dir_consolidations,
                    'estimated_reduction': len(same_dir_consolidations),
                    'risk': 'medium'
                }
            ]
        })
    
    # Phase 4: Quality improvement
    low_compliance_interfaces = [i for i in quality_metrics['improvement_candidates'] if i['compliance_score'] < 50]
    if low_compliance_interfaces:
        strategy['consolidation_phases'].append({
            'phase': 4,
            'name': 'Quality Improvement',
            'description': 'Improve compliance scores for low-quality interfaces',
            'actions': [
                {
                    'action': 'improve_compliance',
                    'targets': low_compliance_interfaces[:10],  # Top 10 candidates
                    'estimated_improvement': len(low_compliance_interfaces),
                    'risk': 'low'
                }
            ]
        })
    
    # Calculate estimated impact
    total_duplicates = patterns['total_duplicates']
    strategy['estimated_impact'] = {
        'current_duplicates': total_duplicates,
        'estimated_reduction': sum(len(phase['actions'][0]['targets']) for phase in strategy['consolidation_phases']),
        'estimated_compliance_improvement': len(low_compliance_interfaces) * 20,  # Assume 20% improvement per interface
        'final_duplicate_count': max(0, total_duplicates - sum(len(phase['actions'][0]['targets']) for phase in strategy['consolidation_phases']))
    }
    
    # Set compliance targets
    current_avg = quality_metrics.get('average_compliance', 48.13)
    strategy['compliance_targets'] = {
        'current_average': current_avg,
        'target_average': 85.0,
        'minimum_compliance': 70.0,
        'excellent_compliance': 95.0
    }
    
    # Risk assessment
    strategy['risk_assessment'] = {
        'low_risk_actions': len([p for p in strategy['consolidation_phases'] if any(a['risk'] == 'low' for a in p['actions'])]),
        'medium_risk_actions': len([p for p in strategy['consolidation_phases'] if any(a['risk'] == 'medium' for a in p['actions'])]),
        'high_risk_actions': len([p for p in strategy['consolidation_phases'] if any(a['risk'] == 'high' for a in p['actions'])]),
        'overall_risk': 'medium'
    }
    
    return strategy

def main():
    """Main analysis function."""
    print("🚀 BEAST MODE: Duplicate Interface Analysis")
    print("=" * 60)
    
    # Load data
    registry_data, enhanced_data = load_registry_data()
    
    if not registry_data:
        print("❌ No registry data found. Run enhanced registry workflow first.")
        return
    
    # Analyze patterns
    patterns = analyze_duplicate_patterns(registry_data)
    
    # Analyze quality
    quality_metrics = analyze_interface_quality(enhanced_data)
    
    # Generate strategy
    strategy = generate_consolidation_strategy(patterns, quality_metrics)
    
    # Print analysis results
    print(f"\n📊 DUPLICATE INTERFACE ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n🔍 Duplicate Patterns:")
    print(f"   Total Duplicates: {patterns['total_duplicates']}")
    print(f"   Duplicate Names: {len(patterns['duplicate_names'])}")
    print(f"   Interface Types with Duplicates: {len(patterns['interface_types_with_duplicates'])}")
    print(f"   Files with Duplicates: {len(patterns['files_with_duplicates'])}")
    
    print(f"\n📈 Quality Metrics:")
    print(f"   Total Interfaces: {quality_metrics['total_interfaces']}")
    print(f"   Average Compliance: {quality_metrics.get('average_compliance', 0):.2f}%")
    print(f"   Min Compliance: {quality_metrics.get('min_compliance', 0):.2f}%")
    print(f"   Max Compliance: {quality_metrics.get('max_compliance', 0):.2f}%")
    print(f"   Low Compliance Interfaces: {len(quality_metrics['quality_issues'])}")
    
    print(f"\n🎯 Consolidation Strategy:")
    print(f"   Consolidation Phases: {len(strategy['consolidation_phases'])}")
    print(f"   Estimated Duplicate Reduction: {strategy['estimated_impact']['estimated_reduction']}")
    print(f"   Target Compliance: {strategy['compliance_targets']['target_average']:.1f}%")
    print(f"   Overall Risk: {strategy['risk_assessment']['overall_risk']}")
    
    print(f"\n🔥 Priority Actions:")
    for i, phase in enumerate(strategy['consolidation_phases'], 1):
        print(f"   Phase {i}: {phase['name']}")
        for action in phase['actions']:
            print(f"     - {action['action']}: {len(action['targets'])} targets (risk: {action['risk']})")
    
    # Save analysis results
    analysis_results = {
        'patterns': patterns,
        'quality_metrics': quality_metrics,
        'strategy': strategy,
        'timestamp': str(datetime.now())
    }
    
    os.makedirs('.beast_mode', exist_ok=True)
    with open('.beast_mode/duplicate_interface_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"\n💾 Analysis results saved to .beast_mode/duplicate_interface_analysis.json")
    print(f"\n🎉 Duplicate Interface Analysis Complete!")
    
    return analysis_results

if __name__ == "__main__":
    from datetime import datetime
    main()
