#!/usr/bin/env python3
"""
Test Domain Index System
========================
Test script for the Domain Index System to verify intelligent querying
and relationship analysis functionality.
Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Test domain querying and analysis capabilities
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from beast_mode.domain_index.domain_index_core import DomainIndexCore


def test_domain_index():
    """Test the Domain Index System functionality."""
    print("🧪 Testing Domain Index System")
    print("=" * 50)
    # Create domain index
    domain_index = DomainIndexCore()
    # Test module info
    print("\n📋 Module Information:")
    module_info = domain_index.get_module_info()
    for key, value in module_info.items():
        print("   {key}: {value}")
    # Test health status
    print("\n🏥 Health Status:")
    domain_index.get_health_status()
    print("   Status: {health.status.value}")
    print("   Health Score: {health.health_score}")
    print("   Issues: {len(health.issues)}")
    # Test index summary
    print("\n📊 Index Summary:")
    summary = domain_index.get_index_summary()
    for key, value in summary.items():
        print("   {key}: {value}")
    print("\n✅ Domain Index System test completed successfully!")
    return True


def test_domain_queries():
    """Test domain querying functionality."""
    print("\n🔍 Testing Domain Queries")
    print("=" * 50)
    domain_index = DomainIndexCore()
    # Test specific domain query
    print("\n🎯 Testing Specific Domain Query:")
    test_domain = "snowflake_openflow_demo"
    domain_info = domain_index.query_domain(test_domain)
    if domain_info:
        print("   Found domain: {domain_info.name}")
        print("   Type: {domain_info.type.value}")
        print("   Description: {domain_info.description[:100]}...")
        print("   Patterns: {len(domain_info.patterns)}")
        print("   Dependencies: {len(domain_info.dependencies)}")
        print("   Tools: {len(domain_info.tools)}")
        print("   Extraction Potential: {domain_info.extraction_potential}")
    else:
        print("   Domain '{test_domain}' not found")
    # Test capability search
    print("\n🔍 Testing Capability Search:")
    capability = "testing"
    search_result = domain_index.search_domains_by_capability(capability)
    print("   Search for '{capability}':")
    print(
        "   Found {search_result.total_count} domains in {search_result.query_time_ms:.2f}ms"
    )
    for i, domain in enumerate(search_result.domains[:5], 1):  # Show top 5
        search_result.relevance_scores.get(domain.name, 0)
        print("   {i}. {domain.name} (relevance: {score:.3f})")
    print("\n✅ Domain queries test completed successfully!")
    return True


def test_relationship_analysis():
    """Test domain relationship analysis."""
    print("\n🔗 Testing Relationship Analysis")
    print("=" * 50)
    domain_index = DomainIndexCore()
    # Test domain relationships
    print("\n🔗 Testing Domain Relationships:")
    test_domain = "snowflake_openflow_demo"
    relationships = domain_index.get_domain_relationships(test_domain)
    print("   Domain: {relationships['domain']}")
    print("   Dependencies: {len(relationships['dependencies'])}")
    print("   Dependents: {len(relationships['dependents'])}")
    print("   Impact Score: {relationships['impact_score']:.2f}")
    if relationships["dependencies"]:
        print("   Top Dependencies: {relationships['dependencies'][:3]}")
    if relationships["dependents"]:
        print("   Top Dependents: {relationships['dependents'][:3]}")
    # Test cross-domain pattern analysis
    print("\n🔍 Testing Cross-Domain Pattern Analysis:")
    pattern_analysis = domain_index.analyze_cross_domain_patterns()
    print("   Total Patterns: {pattern_analysis['total_patterns']}")
    print("   Common Patterns: {len(pattern_analysis['common_patterns'])}")
    print("   Pattern Diversity: {pattern_analysis['pattern_diversity']:.3f}")
    if pattern_analysis["common_patterns"]:
        print("   Top Common Patterns:")
        for i, pattern in enumerate(pattern_analysis["common_patterns"][:3], 1):
            print(
                "     {i}. {pattern['pattern']} (used by {pattern['frequency']} domains)"
            )
    print("\n✅ Relationship analysis test completed successfully!")
    return True


def test_health_monitoring():
    """Test domain health monitoring."""
    print("\n🏥 Testing Health Monitoring")
    print("=" * 50)
    domain_index = DomainIndexCore()
    # Test health check
    print("\n🏥 Testing Health Check:")
    health_report = domain_index.perform_health_check()
    print("   Total Domains: {health_report['total_domains']}")
    print("   Healthy Domains: {health_report['healthy_domains']}")
    print("   Warning Domains: {health_report['warning_domains']}")
    print("   Error Domains: {health_report['error_domains']}")
    # Calculate health percentage
    if health_report["total_domains"] > 0:
        health_percentage = (
            health_report["healthy_domains"] / health_report["total_domains"]
        ) * 100
        print("   Health Percentage: {health_percentage:.1f}%")
    print("\n✅ Health monitoring test completed successfully!")
    return True


def test_integration_with_pdca():
    """Test integration with PDCA Orchestrator."""
    print("\n🔄 Testing Integration with PDCA Orchestrator")
    print("=" * 60)
    domain_index = DomainIndexCore()
    # Simulate PDCA task domain analysis
    print("\n🎯 Simulating PDCA Task Domain Analysis:")
    test_task_domain = "authentication"
    # Search for relevant domains
    search_result = domain_index.search_domains_by_capability(test_task_domain)
    print("   Task Domain: {test_task_domain}")
    print("   Relevant Domains Found: {search_result.total_count}")
    if search_result.domains:
        best_match = search_result.domains[0]
        print(
            "   Best Match: {best_match.name} (relevance: {search_result.relevance_scores.get(best_match.name, 0):.3f})"
        )
        # Get relationships for the best match
        domain_index.get_domain_relationships(best_match.name)
        print("   Domain Impact Score: {relationships['impact_score']:.2f}")
        print("   Dependencies: {len(relationships['dependencies'])}")
        print("   Dependents: {len(relationships['dependents'])}")
    # Test domain assignment suggestion
    print("\n📁 Testing Domain Assignment Suggestion:")
    test_file = "src/auth/user_management.py"
    suggestions = domain_index.suggest_domain_assignment(test_file)
    print("   File: {test_file}")
    print("   Suggestions: {len(suggestions)}")
    if suggestions:
        for i, (domain_name, score) in enumerate(suggestions[:3], 1):
            print("   {i}. {domain_name} (score: {score:.3f})")
    print("\n✅ PDCA integration test completed successfully!")
    return True


if __name__ == "__main__":
    print("🚀 Starting Domain Index System Tests")
    print("=" * 60)
    # Test basic functionality
    success1 = test_domain_index()
    # Test domain queries
    success2 = test_domain_queries()
    # Test relationship analysis
    success3 = test_relationship_analysis()
    # Test health monitoring
    success4 = test_health_monitoring()
    # Test PDCA integration
    success5 = test_integration_with_pdca()
    if success1 and success2 and success3 and success4 and success5:
        print("\n🎉 All Domain Index System tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
