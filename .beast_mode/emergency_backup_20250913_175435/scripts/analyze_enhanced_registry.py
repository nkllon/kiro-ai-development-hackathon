#!/usr/bin/env python3
"""
Enhanced Interface Registry Analyzer
Provides detailed analysis of interface metadata including:
- Method signature analysis
- Domain vocabulary coverage
- Ubiquitous language usage
- Compliance scoring details
- File location precision
"""

import json
from typing import Dict, List, Any
from collections import Counter, defaultdict

def load_enhanced_registry(registry_file: str = ".beast_mode/enhanced_interface_registry.json") -> Dict[str, Any]:
    """Load the enhanced interface registry."""
    try:
        with open(registry_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Enhanced registry not found: {registry_file}")
        return {}
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return {}

def analyze_method_signatures(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze method signatures across all interfaces."""
    method_stats = {
        'total_methods': 0,
        'methods_with_docstrings': 0,
        'methods_with_type_annotations': 0,
        'abstract_methods': 0,
        'decorated_methods': 0,
        'common_method_names': Counter(),
        'common_decorators': Counter(),
        'common_return_types': Counter(),
        'average_parameters_per_method': 0
    }
    
    total_params = 0
    
    for interface_data in data.get('interfaces', {}).values():
        for method in interface_data.get('methods', []):
            method_stats['total_methods'] += 1
            
            if method.get('docstring'):
                method_stats['methods_with_docstrings'] += 1
            
            if method.get('return_type'):
                method_stats['methods_with_type_annotations'] += 1
                method_stats['common_return_types'][method['return_type']] += 1
            
            if method.get('is_abstract'):
                method_stats['abstract_methods'] += 1
            
            if method.get('decorators'):
                method_stats['decorated_methods'] += 1
                for decorator in method['decorators']:
                    method_stats['common_decorators'][decorator] += 1
            
            method_stats['common_method_names'][method['name']] += 1
            total_params += len(method.get('parameters', []))
    
    if method_stats['total_methods'] > 0:
        method_stats['average_parameters_per_method'] = round(total_params / method_stats['total_methods'], 2)
    
    return method_stats

def analyze_domain_vocabulary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze domain vocabulary usage."""
    domain_stats = {
        'total_domain_terms': len(data.get('domain_index', {})),
        'total_ubiquitous_terms': len(data.get('ubiquitous_language_index', {})),
        'most_common_domain_terms': Counter(),
        'most_common_ubiquitous_terms': Counter(),
        'interfaces_per_domain_term': defaultdict(int),
        'interfaces_per_ubiquitous_term': defaultdict(int)
    }
    
    # Analyze domain terms
    for term, interfaces in data.get('domain_index', {}).items():
        domain_stats['most_common_domain_terms'][term] = len(interfaces)
        domain_stats['interfaces_per_domain_term'][term] = len(interfaces)
    
    # Analyze ubiquitous language terms
    for term, interfaces in data.get('ubiquitous_language_index', {}).items():
        domain_stats['most_common_ubiquitous_terms'][term] = len(interfaces)
        domain_stats['interfaces_per_ubiquitous_term'][term] = len(interfaces)
    
    return domain_stats

def analyze_file_locations(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze file location tracking precision."""
    location_stats = {
        'total_interfaces': 0,
        'interfaces_with_precise_locations': 0,
        'interfaces_by_directory': Counter(),
        'interfaces_by_file': Counter(),
        'average_lines_per_interface': 0,
        'largest_interfaces': [],
        'most_interface_dense_files': []
    }
    
    total_lines = 0
    interface_sizes = []
    file_interface_counts = defaultdict(int)
    
    for interface_id, interface_data in data.get('interfaces', {}).items():
        location_stats['total_interfaces'] += 1
        
        file_path = interface_data['file_path']
        line_number = interface_data['line_number']
        end_line_number = interface_data['end_line_number']
        
        # Check if location is precise (has both start and end)
        if end_line_number and end_line_number > line_number:
            location_stats['interfaces_with_precise_locations'] += 1
        
        # Directory analysis
        directory = '/'.join(file_path.split('/')[:-1]) if '/' in file_path else '.'
        location_stats['interfaces_by_directory'][directory] += 1
        
        # File analysis
        location_stats['interfaces_by_file'][file_path] += 1
        file_interface_counts[file_path] += 1
        
        # Size analysis
        if end_line_number:
            size = end_line_number - line_number + 1
            interface_sizes.append((interface_data['interface_name'], size))
            total_lines += size
    
    # Calculate averages and find extremes
    if location_stats['total_interfaces'] > 0:
        location_stats['average_lines_per_interface'] = round(total_lines / location_stats['total_interfaces'], 2)
    
    # Find largest interfaces
    interface_sizes.sort(key=lambda x: x[1], reverse=True)
    location_stats['largest_interfaces'] = interface_sizes[:10]
    
    # Find most interface-dense files
    file_densities = [(file, count) for file, count in file_interface_counts.items()]
    file_densities.sort(key=lambda x: x[1], reverse=True)
    location_stats['most_interface_dense_files'] = file_densities[:10]
    
    return location_stats

def analyze_compliance_scores(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze compliance scores across interfaces."""
    compliance_stats = {
        'total_interfaces': 0,
        'average_compliance': 0,
        'compliance_distribution': defaultdict(int),
        'highest_compliance_interfaces': [],
        'lowest_compliance_interfaces': [],
        'compliance_by_type': defaultdict(list)
    }
    
    compliance_scores = []
    
    for interface_id, interface_data in data.get('interfaces', {}).items():
        compliance_stats['total_interfaces'] += 1
        
        compliance_score = interface_data.get('compliance_score', 0)
        compliance_scores.append((interface_data['interface_name'], compliance_score))
        
        # Distribution analysis
        score_range = (compliance_score // 10) * 10
        compliance_stats['compliance_distribution'][f"{score_range}-{score_range+9}"] += 1
        
        # Type analysis
        interface_type = interface_data.get('interface_type', 'unknown')
        compliance_stats['compliance_by_type'][interface_type].append(compliance_score)
    
    # Calculate average
    if compliance_scores:
        compliance_stats['average_compliance'] = round(
            sum(score for _, score in compliance_scores) / len(compliance_scores), 2
        )
        
        # Find extremes
        compliance_scores.sort(key=lambda x: x[1], reverse=True)
        compliance_stats['highest_compliance_interfaces'] = compliance_scores[:10]
        compliance_stats['lowest_compliance_interfaces'] = compliance_scores[-10:]
    
    return compliance_stats

def analyze_interface_types(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze interface type distribution and characteristics."""
    type_stats = {
        'total_types': 0,
        'interfaces_by_type': Counter(),
        'methods_by_type': defaultdict(int),
        'compliance_by_type': defaultdict(list),
        'domain_coverage_by_type': defaultdict(set)
    }
    
    for interface_id, interface_data in data.get('interfaces', {}).items():
        interface_type = interface_data.get('interface_type', 'unknown')
        type_stats['interfaces_by_type'][interface_type] += 1
        type_stats['total_types'] += 1
        
        # Methods by type
        method_count = len(interface_data.get('methods', []))
        type_stats['methods_by_type'][interface_type] += method_count
        
        # Compliance by type
        compliance_score = interface_data.get('compliance_score', 0)
        type_stats['compliance_by_type'][interface_type].append(compliance_score)
        
        # Domain coverage by type
        domain_terms = set(interface_data.get('domain_terms', []))
        type_stats['domain_coverage_by_type'][interface_type].update(domain_terms)
    
    # Calculate averages for compliance by type
    for interface_type, scores in type_stats['compliance_by_type'].items():
        if scores:
            type_stats['compliance_by_type'][interface_type] = round(sum(scores) / len(scores), 2)
    
    return type_stats

def generate_comprehensive_report(data: Dict[str, Any]) -> None:
    """Generate and display a comprehensive analysis report."""
    print("🔍 Enhanced Interface Registry Analysis")
    print("=" * 60)
    
    # Basic statistics
    metadata = data.get('metadata', {})
    print(f"📊 Basic Statistics:")
    print(f"   Total interfaces: {metadata.get('total_interfaces', 0)}")
    print(f"   Domain terms indexed: {metadata.get('total_domain_terms', 0)}")
    print(f"   Ubiquitous language terms: {metadata.get('total_ubiquitous_terms', 0)}")
    print(f"   Last updated: {metadata.get('last_updated', 'Unknown')}")
    
    # Method signature analysis
    print(f"\n🔧 Method Signature Analysis:")
    method_stats = analyze_method_signatures(data)
    print(f"   Total methods: {method_stats['total_methods']}")
    print(f"   Methods with docstrings: {method_stats['methods_with_docstrings']} ({method_stats['methods_with_docstrings']/method_stats['total_methods']*100:.1f}%)" if method_stats['total_methods'] > 0 else "   Methods with docstrings: 0")
    print(f"   Methods with type annotations: {method_stats['methods_with_type_annotations']} ({method_stats['methods_with_type_annotations']/method_stats['total_methods']*100:.1f}%)" if method_stats['total_methods'] > 0 else "   Methods with type annotations: 0")
    print(f"   Abstract methods: {method_stats['abstract_methods']}")
    print(f"   Decorated methods: {method_stats['decorated_methods']}")
    print(f"   Average parameters per method: {method_stats['average_parameters_per_method']}")
    
    print(f"\n   Most common method names:")
    for method_name, count in method_stats['common_method_names'].most_common(10):
        print(f"     {method_name}: {count}")
    
    print(f"\n   Most common decorators:")
    for decorator, count in method_stats['common_decorators'].most_common(5):
        print(f"     {decorator}: {count}")
    
    # Domain vocabulary analysis
    print(f"\n📚 Domain Vocabulary Analysis:")
    domain_stats = analyze_domain_vocabulary(data)
    print(f"   Total domain terms: {domain_stats['total_domain_terms']}")
    print(f"   Total ubiquitous language terms: {domain_stats['total_ubiquitous_terms']}")
    
    print(f"\n   Most common domain terms:")
    for term, count in domain_stats['most_common_domain_terms'].most_common(10):
        print(f"     {term}: {count} interfaces")
    
    print(f"\n   Most common ubiquitous language terms:")
    for term, count in domain_stats['most_common_ubiquitous_terms'].most_common(5):
        print(f"     {term}: {count} interfaces")
    
    # File location analysis
    print(f"\n📍 File Location Analysis:")
    location_stats = analyze_file_locations(data)
    print(f"   Total interfaces: {location_stats['total_interfaces']}")
    print(f"   Interfaces with precise locations: {location_stats['interfaces_with_precise_locations']} ({location_stats['interfaces_with_precise_locations']/location_stats['total_interfaces']*100:.1f}%)" if location_stats['total_interfaces'] > 0 else "   Interfaces with precise locations: 0")
    print(f"   Average lines per interface: {location_stats['average_lines_per_interface']}")
    
    print(f"\n   Most interface-dense directories:")
    for directory, count in location_stats['interfaces_by_directory'].most_common(5):
        print(f"     {directory}: {count} interfaces")
    
    print(f"\n   Largest interfaces (by line count):")
    for interface_name, size in location_stats['largest_interfaces'][:5]:
        print(f"     {interface_name}: {size} lines")
    
    # Compliance analysis
    print(f"\n✅ Compliance Analysis:")
    compliance_stats = analyze_compliance_scores(data)
    print(f"   Average compliance score: {compliance_stats['average_compliance']}%")
    
    print(f"\n   Compliance distribution:")
    for range_str, count in sorted(compliance_stats['compliance_distribution'].items()):
        print(f"     {range_str}%: {count} interfaces")
    
    print(f"\n   Highest compliance interfaces:")
    for interface_name, score in compliance_stats['highest_compliance_interfaces'][:5]:
        print(f"     {interface_name}: {score}%")
    
    print(f"\n   Lowest compliance interfaces:")
    for interface_name, score in compliance_stats['lowest_compliance_interfaces'][:5]:
        print(f"     {interface_name}: {score}%")
    
    # Interface type analysis
    print(f"\n🏷️  Interface Type Analysis:")
    type_stats = analyze_interface_types(data)
    print(f"   Total interface types: {type_stats['total_types']}")
    
    print(f"\n   Interfaces by type:")
    for interface_type, count in type_stats['interfaces_by_type'].most_common():
        avg_compliance = type_stats['compliance_by_type'].get(interface_type, 0)
        avg_methods = type_stats['methods_by_type'][interface_type] / count if count > 0 else 0
        domain_coverage = len(type_stats['domain_coverage_by_type'][interface_type])
        print(f"     {interface_type}: {count} interfaces, {avg_compliance}% avg compliance, {avg_methods:.1f} avg methods, {domain_coverage} domain terms")
    
    print(f"\n🎉 Enhanced Registry Analysis Complete!")

def main():
    """Main execution function."""
    data = load_enhanced_registry()
    if data:
        generate_comprehensive_report(data)
    else:
        print("❌ No enhanced registry data available. Run enhanced_interface_registry.py first.")

if __name__ == "__main__":
    main()
