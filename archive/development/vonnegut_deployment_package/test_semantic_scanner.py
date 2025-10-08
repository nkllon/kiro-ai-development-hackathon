#!/usr/bin/env python3
"""
Test script for semantic orphaned scanner
"""

import sys
from pathlib import Path

sys.path.append('scripts')
from semantic_orphaned_scanner import SemanticOrphanedScanner

def test_semantic_scanner():
    """Test the semantic scanner with a small subset."""
    print("🧪 Testing Semantic Orphaned Scanner")
    print("=" * 40)
    
    scanner = SemanticOrphanedScanner()
    
    # Test with very strict thresholds for manageable results
    scanner.min_lines = 200
    scanner.min_complexity = 20
    scanner.match_threshold = 0.3
    
    # Test discovery
    print("📁 Testing implementation discovery...")
    implementations = scanner._discover_implementations()
    print(f"   Found {len(implementations)} substantial implementations")
    
    print("📋 Testing specification discovery...")
    specifications = scanner._discover_specifications()
    print(f"   Found {len(specifications)} specifications")
    
    # Test with small subset
    test_impls = implementations[:5]
    test_specs = specifications[:10]
    
    print(f"🔍 Testing semantic matching with {len(test_impls)} impls and {len(test_specs)} specs...")
    matches = scanner.matcher.find_matches(test_specs, test_impls)
    print(f"   Found {len(matches)} semantic matches")
    
    # Show top matches
    for match in matches[:3]:
        spec_name = Path(match.spec_path).name
        impl_name = Path(match.impl_path).name
        print(f"   {match.confidence:.1%}: {spec_name} → {impl_name}")
    
    # Test orphan detection
    print("🚨 Testing orphan detection...")
    orphaned = scanner._identify_orphaned_solutions(test_impls, matches)
    print(f"   Found {len(orphaned)} orphaned solutions")
    
    for orphan in orphaned[:3]:
        print(f"   Priority {orphan['priority']}: {Path(orphan['implementation_path']).name} ({orphan['estimated_effort_hours']}h)")
    
    print("\n✅ Semantic scanner test complete!")
    return len(implementations), len(specifications), len(matches), len(orphaned)

if __name__ == "__main__":
    test_semantic_scanner()