#!/usr/bin/env python3
"""
Demo script for Technical Debt Patch Annotation System - Issue Tracking Integration.

This script demonstrates the upstream issue tracking capabilities including:
- GitHub Issues API integration
- Jira REST API support  
- Issue status monitoring
- Dependency version tracking
- Patch cleanup prioritization

Usage:
    python demo_issue_tracking.py [--github] [--jira] [--test-connectivity]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.technical_debt_patch_annotation.integration.issue_tracker import (
    create_issue_tracker,
    IssueTracker,
    GitHubIssueTracker,
    JiraIssueTracker,
    IssueStatus,
    IssueTrackerError,
    AuthenticationError
)
from src.technical_debt_patch_annotation.core.models import (
    PatchAnnotation,
    DebtLevel,
    BypassType
)


def create_sample_patches() -> List[PatchAnnotation]:
    """Create sample patch annotations for demonstration."""
    patches = [
        PatchAnnotation(
            patch_id="PATCH-DEMO001",
            reason="Temporary workaround for API rate limiting",
            upstream_issue="octocat/Hello-World#1",  # GitHub issue
            cleanup_task="Replace with proper retry mechanism when API v2 available",
            debt_level=DebtLevel.MEDIUM,
            bypass_type=BypassType.INTEGRATION,
            component="api_client",
            file_path="src/api/client.py",
            line_start=45,
            line_end=52,
            validation_criteria=[
                "API v2 integration tests pass",
                "Rate limiting removed",
                "Response time improved"
            ],
            created_by="developer@example.com",
            expected_resolution=datetime.now() + timedelta(days=30)
        ),
        PatchAnnotation(
            patch_id="PATCH-DEMO002", 
            reason="Security bypass for legacy authentication",
            upstream_issue="PROJ-456",  # Jira issue
            cleanup_task="Implement OAuth 2.0 when security team approves",
            debt_level=DebtLevel.HIGH,
            bypass_type=BypassType.SECURITY,
            component="auth_service",
            file_path="src/auth/legacy.py",
            line_start=123,
            line_end=145,
            validation_criteria=[
                "OAuth 2.0 implementation complete",
                "Security audit passes",
                "All legacy auth removed"
            ],
            created_by="security@example.com",
            expected_resolution=datetime.now() + timedelta(days=60)
        ),
        PatchAnnotation(
            patch_id="PATCH-DEMO003",
            reason="Performance workaround for database query",
            upstream_issue="facebook/react#12345",  # Another GitHub issue
            cleanup_task="Optimize query when database upgrade is complete",
            debt_level=DebtLevel.LOW,
            bypass_type=BypassType.PERFORMANCE,
            component="database_layer",
            file_path="src/db/queries.py",
            line_start=78,
            line_end=85,
            validation_criteria=[
                "Database upgrade completed",
                "Query performance improved by 50%",
                "Memory usage reduced"
            ],
            created_by="dba@example.com",
            expected_resolution=datetime.now() - timedelta(days=10)  # Overdue
        )
    ]
    
    return patches


def demo_github_integration():
    """Demonstrate GitHub Issues integration."""
    print("\n" + "="*60)
    print("GITHUB ISSUES INTEGRATION DEMO")
    print("="*60)
    
    # Configuration for GitHub (using environment variables)
    github_config = {
        'token': os.getenv('GITHUB_TOKEN', 'demo-token-not-real'),
        'base_url': 'https://api.github.com'
    }
    
    try:
        # Create GitHub issue tracker
        github_tracker = create_issue_tracker('github', github_config)
        print(f"✓ Created GitHub issue tracker")
        
        # Test health status
        health = github_tracker.get_health_status_dict()
        print(f"✓ Health Status: {health['status']}")
        print(f"  - API Connectivity: {health.get('api_connectivity', 'Unknown')}")
        print(f"  - Metrics: {health['metrics']}")
        
        # Demo with sample patches
        patches = create_sample_patches()
        github_patches = [p for p in patches if 'github.com' in p.upstream_issue or '#' in p.upstream_issue]
        
        print(f"\n📋 Processing {len(github_patches)} GitHub-linked patches:")
        
        for patch in github_patches:
            print(f"\n🔍 Patch: {patch.patch_id}")
            print(f"   Upstream Issue: {patch.upstream_issue}")
            print(f"   Debt Level: {patch.debt_level.value}")
            
            try:
                # Link patch to issue (this would normally store the link)
                github_tracker.link_patch_to_issue(patch.patch_id, patch.upstream_issue)
                print(f"   ✓ Linked to upstream issue")
                
                # Generate remediation guidance
                guidance = github_tracker.generate_remediation_guidance(patch)
                print(f"   📝 Remediation Steps: {len(guidance['remediation_steps'])} steps")
                print(f"   ⏱️  Estimated Effort: {guidance['estimated_effort']}")
                
                # Try to get dependency version info
                if patch.component:
                    try:
                        # For demo, we'll try to get version info for the component
                        # In practice, this would be extracted from the patch context
                        if '/' in patch.upstream_issue:
                            repo_name = patch.upstream_issue.split('#')[0]
                            version_info = github_tracker.get_dependency_version_info(repo_name)
                            print(f"   📦 Latest Version: {version_info.latest_version}")
                    except Exception as e:
                        print(f"   ⚠️  Version info not available: {str(e)[:50]}...")
                
            except AuthenticationError:
                print(f"   ❌ Authentication failed (expected with demo token)")
            except Exception as e:
                print(f"   ⚠️  Error: {str(e)[:50]}...")
        
        # Demo patch prioritization
        print(f"\n🎯 PATCH PRIORITIZATION:")
        prioritized = github_tracker.prioritize_patch_removal(github_patches)
        for patch_id, priority_score in prioritized:
            print(f"   {patch_id}: Priority Score {priority_score}")
        
    except Exception as e:
        print(f"❌ GitHub integration error: {e}")


def demo_jira_integration():
    """Demonstrate Jira REST API integration."""
    print("\n" + "="*60)
    print("JIRA REST API INTEGRATION DEMO")
    print("="*60)
    
    # Configuration for Jira (using environment variables)
    jira_config = {
        'base_url': os.getenv('JIRA_BASE_URL', 'https://your-company.atlassian.net'),
        'username': os.getenv('JIRA_USERNAME', 'demo-user'),
        'token': os.getenv('JIRA_TOKEN', 'demo-token-not-real')
    }
    
    try:
        # Create Jira issue tracker
        jira_tracker = create_issue_tracker('jira', jira_config)
        print(f"✓ Created Jira issue tracker")
        print(f"  - Base URL: {jira_config['base_url']}")
        
        # Test health status
        health = jira_tracker.get_health_status_dict()
        print(f"✓ Health Status: {health['status']}")
        print(f"  - Configuration: {health['configuration']}")
        
        # Demo with sample patches
        patches = create_sample_patches()
        jira_patches = [p for p in patches if not '#' in p.upstream_issue]
        
        print(f"\n📋 Processing {len(jira_patches)} Jira-linked patches:")
        
        for patch in jira_patches:
            print(f"\n🔍 Patch: {patch.patch_id}")
            print(f"   Upstream Issue: {patch.upstream_issue}")
            print(f"   Debt Level: {patch.debt_level.value}")
            print(f"   Bypass Type: {patch.bypass_type.value}")
            
            try:
                # Generate remediation guidance
                guidance = jira_tracker.generate_remediation_guidance(patch)
                print(f"   📝 Remediation Steps: {len(guidance['remediation_steps'])} steps")
                print(f"   ⏱️  Estimated Effort: {guidance['estimated_effort']}")
                print(f"   🎯 Risk Level: {guidance['risk_level']}")
                
                # Show some remediation steps
                if guidance['remediation_steps']:
                    print(f"   📋 First Step: {guidance['remediation_steps'][0]}")
                
            except AuthenticationError:
                print(f"   ❌ Authentication failed (expected with demo credentials)")
            except Exception as e:
                print(f"   ⚠️  Error: {str(e)[:50]}...")
        
        # Demo cleanup monitoring
        print(f"\n🔄 CLEANUP MONITORING:")
        cleanup_ready = jira_tracker.check_patches_for_resolved_issues(jira_patches)
        if cleanup_ready:
            print(f"   📢 {len(cleanup_ready)} patches ready for cleanup:")
            for patch_id in cleanup_ready:
                print(f"      - {patch_id}")
        else:
            print(f"   ℹ️  No patches ready for cleanup at this time")
        
    except Exception as e:
        print(f"❌ Jira integration error: {e}")


def demo_observability_correlation():
    """Demonstrate observability correlation features."""
    print("\n" + "="*60)
    print("OBSERVABILITY CORRELATION DEMO")
    print("="*60)
    
    # Use GitHub tracker for this demo
    github_config = {
        'token': os.getenv('GITHUB_TOKEN', 'demo-token'),
        'base_url': 'https://api.github.com'
    }
    
    try:
        tracker = create_issue_tracker('github', github_config)
        
        # Demo correlation with sample issue
        sample_issue = "octocat/Hello-World#1"
        print(f"🔗 Correlating issue: {sample_issue}")
        
        correlation_data = tracker.correlate_issues_with_observability(sample_issue)
        
        print(f"📊 Correlation Results:")
        print(f"   - Issue Reference: {correlation_data['issue_ref']}")
        print(f"   - Correlation Timestamp: {correlation_data['correlation_timestamp']}")
        print(f"   - Keywords: {correlation_data.get('keywords', [])}")
        print(f"   - Jaeger Traces: {len(correlation_data.get('jaeger_traces', []))}")
        print(f"   - Prometheus Metrics: {len(correlation_data.get('prometheus_metrics', []))}")
        
        if correlation_data.get('error'):
            print(f"   ⚠️  Note: {correlation_data['error']}")
        
        print(f"\n💡 In a real implementation, this would:")
        print(f"   - Search Jaeger traces for issue-related keywords")
        print(f"   - Query Prometheus metrics around issue timeframes")
        print(f"   - Correlate performance anomalies with patch locations")
        print(f"   - Provide data-driven cleanup prioritization")
        
    except Exception as e:
        print(f"❌ Observability correlation error: {e}")


def demo_comprehensive_workflow():
    """Demonstrate a comprehensive patch management workflow."""
    print("\n" + "="*60)
    print("COMPREHENSIVE PATCH MANAGEMENT WORKFLOW")
    print("="*60)
    
    patches = create_sample_patches()
    
    # Create both trackers for comprehensive demo
    trackers = {}
    
    try:
        # GitHub tracker
        github_config = {'token': os.getenv('GITHUB_TOKEN', 'demo-token')}
        trackers['github'] = create_issue_tracker('github', github_config)
        print("✓ GitHub tracker initialized")
    except Exception as e:
        print(f"⚠️  GitHub tracker unavailable: {e}")
    
    try:
        # Jira tracker
        jira_config = {
            'base_url': os.getenv('JIRA_BASE_URL', 'https://demo.atlassian.net'),
            'username': os.getenv('JIRA_USERNAME', 'demo'),
            'token': os.getenv('JIRA_TOKEN', 'demo-token')
        }
        trackers['jira'] = create_issue_tracker('jira', jira_config)
        print("✓ Jira tracker initialized")
    except Exception as e:
        print(f"⚠️  Jira tracker unavailable: {e}")
    
    if not trackers:
        print("❌ No trackers available for comprehensive demo")
        return
    
    print(f"\n📋 PATCH INVENTORY ({len(patches)} patches):")
    for patch in patches:
        print(f"   {patch.patch_id}: {patch.debt_level.value} - {patch.reason[:50]}...")
    
    # Process patches with appropriate trackers
    all_prioritized = []
    
    for tracker_name, tracker in trackers.items():
        print(f"\n🔄 Processing with {tracker_name.upper()} tracker:")
        
        try:
            # Check for resolved issues
            cleanup_ready = tracker.check_patches_for_resolved_issues(patches)
            if cleanup_ready:
                print(f"   📢 {len(cleanup_ready)} patches ready for cleanup")
            
            # Prioritize patches
            prioritized = tracker.prioritize_patch_removal(patches)
            all_prioritized.extend(prioritized)
            
            print(f"   🎯 Top 3 priority patches:")
            for patch_id, score in prioritized[:3]:
                print(f"      {patch_id}: {score} points")
            
            # Show metrics
            health = tracker.get_health_status_dict()
            metrics = health.get('metrics', {})
            print(f"   📊 Metrics: {metrics.get('issues_checked', 0)} issues checked, "
                  f"{metrics.get('api_calls_made', 0)} API calls made")
            
        except Exception as e:
            print(f"   ❌ Error processing with {tracker_name}: {e}")
    
    # Combined prioritization
    if all_prioritized:
        print(f"\n🏆 OVERALL TOP PRIORITY PATCHES:")
        # Combine and re-sort all prioritized patches
        combined = {}
        for patch_id, score in all_prioritized:
            combined[patch_id] = max(combined.get(patch_id, 0), score)
        
        sorted_patches = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        for i, (patch_id, score) in enumerate(sorted_patches[:5], 1):
            print(f"   {i}. {patch_id}: {score} points")
    
    print(f"\n✅ Comprehensive workflow demonstration complete!")


def test_connectivity():
    """Test connectivity to configured issue tracking systems."""
    print("\n" + "="*60)
    print("CONNECTIVITY TEST")
    print("="*60)
    
    # Test GitHub
    print("🔍 Testing GitHub connectivity...")
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token and github_token != 'demo-token':
        try:
            github_config = {'token': github_token}
            github_tracker = create_issue_tracker('github', github_config)
            health = github_tracker.get_health_status_dict()
            
            if health['status'] == 'healthy':
                print("✅ GitHub API: Connected successfully")
                print(f"   - API calls made: {health['metrics']['api_calls_made']}")
            else:
                print("❌ GitHub API: Connection failed")
                print(f"   - Error: {health.get('error', 'Unknown')}")
        except Exception as e:
            print(f"❌ GitHub API: {e}")
    else:
        print("⚠️  GitHub API: No valid token provided (set GITHUB_TOKEN)")
    
    # Test Jira
    print("\n🔍 Testing Jira connectivity...")
    jira_url = os.getenv('JIRA_BASE_URL')
    jira_user = os.getenv('JIRA_USERNAME')
    jira_token = os.getenv('JIRA_TOKEN')
    
    if all([jira_url, jira_user, jira_token]) and jira_token != 'demo-token':
        try:
            jira_config = {
                'base_url': jira_url,
                'username': jira_user,
                'token': jira_token
            }
            jira_tracker = create_issue_tracker('jira', jira_config)
            health = jira_tracker.get_health_status_dict()
            
            if health['status'] == 'healthy':
                print("✅ Jira API: Connected successfully")
                print(f"   - Base URL: {jira_url}")
                print(f"   - Username: {jira_user}")
            else:
                print("❌ Jira API: Connection failed")
                print(f"   - Error: {health.get('error', 'Unknown')}")
        except Exception as e:
            print(f"❌ Jira API: {e}")
    else:
        print("⚠️  Jira API: Missing configuration (set JIRA_BASE_URL, JIRA_USERNAME, JIRA_TOKEN)")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='Demo Technical Debt Patch Annotation Issue Tracking')
    parser.add_argument('--github', action='store_true', help='Run GitHub integration demo')
    parser.add_argument('--jira', action='store_true', help='Run Jira integration demo')
    parser.add_argument('--observability', action='store_true', help='Run observability correlation demo')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive workflow demo')
    parser.add_argument('--test-connectivity', action='store_true', help='Test API connectivity')
    parser.add_argument('--all', action='store_true', help='Run all demos')
    
    args = parser.parse_args()
    
    print("🚀 Technical Debt Patch Annotation System - Issue Tracking Integration Demo")
    print("=" * 80)
    
    if args.all or not any([args.github, args.jira, args.observability, args.comprehensive, args.test_connectivity]):
        # Run all demos if no specific demo is requested
        demo_github_integration()
        demo_jira_integration()
        demo_observability_correlation()
        demo_comprehensive_workflow()
        test_connectivity()
    else:
        if args.github:
            demo_github_integration()
        if args.jira:
            demo_jira_integration()
        if args.observability:
            demo_observability_correlation()
        if args.comprehensive:
            demo_comprehensive_workflow()
        if args.test_connectivity:
            test_connectivity()
    
    print("\n" + "="*80)
    print("📚 SETUP INSTRUCTIONS:")
    print("="*80)
    print("To use with real APIs, set these environment variables:")
    print("")
    print("For GitHub:")
    print("  export GITHUB_TOKEN='your_github_personal_access_token'")
    print("")
    print("For Jira:")
    print("  export JIRA_BASE_URL='https://your-company.atlassian.net'")
    print("  export JIRA_USERNAME='your_jira_username'")
    print("  export JIRA_TOKEN='your_jira_api_token'")
    print("")
    print("Then run: python demo_issue_tracking.py --test-connectivity")
    print("="*80)


if __name__ == '__main__':
    main()