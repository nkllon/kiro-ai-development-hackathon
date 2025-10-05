#!/usr/bin/env python3
"""
Requirements Compliance Test for Technical Debt Patch Annotation System - Issue Tracking Integration.

This test suite validates that the issue tracking integration meets all specified requirements:
- 3.1: Reference specific upstream issues or bugs
- 3.2: Flag patches for cleanup when upstream issues are resolved  
- 3.3: Track external dependency version information
- 3.4: Include remediation guidance when root causes are identified
- 3.5: Prioritize patch removal when upstream fixes are available

Usage:
    python test_requirements_compliance.py
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.technical_debt_patch_annotation.integration.issue_tracker import (
    IssueTracker,
    GitHubIssueTracker,
    JiraIssueTracker,
    IssueStatus,
    IssueInfo,
    VersionInfo,
    create_issue_tracker,
    IssueTrackerError,
    AuthenticationError,
    IssueNotFoundError
)
from src.technical_debt_patch_annotation.core.models import (
    PatchAnnotation,
    DebtLevel,
    BypassType
)


class TestRequirement31_ReferenceUpstreamIssues(unittest.TestCase):
    """Test Requirement 3.1: Reference specific upstream issues or bugs."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
        self.jira_config = {
            'base_url': 'https://test.atlassian.net',
            'username': 'test-user',
            'token': 'test-token'
        }
    
    def test_github_link_patch_to_issue(self):
        """Test linking patches to GitHub issues."""
        with patch('requests.Session') as mock_session:
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'Test Issue',
                'state': 'open',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
                'assignee': None,
                'labels': [],
                'body': 'Test issue description',
                'id': 12345,
                'comments': 0
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Test linking patch to issue
            patch_id = "PATCH-TEST001"
            issue_ref = "owner/repo#123"
            
            # Should not raise exception
            tracker.link_patch_to_issue(patch_id, issue_ref)
            
            # Verify API was called
            mock_session.return_value.get.assert_called()
            
            # Verify metrics were updated
            self.assertGreater(tracker.metrics['api_calls_made'], 0)
    
    def test_jira_link_patch_to_issue(self):
        """Test linking patches to Jira issues."""
        with patch('requests.Session') as mock_session:
            # Mock successful API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'id': '12345',
                'key': 'PROJ-123',
                'fields': {
                    'summary': 'Test Jira Issue',
                    'status': {'name': 'Open', 'statusCategory': {'name': 'To Do'}},
                    'created': '2024-01-01T00:00:00.000+0000',
                    'updated': '2024-01-01T00:00:00.000+0000',
                    'assignee': None,
                    'labels': [],
                    'description': 'Test issue description',
                    'project': {'key': 'PROJ'},
                    'issuetype': {'name': 'Bug'},
                    'components': [],
                    'fixVersions': []
                }
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = JiraIssueTracker(self.jira_config)
            
            # Test linking patch to issue
            patch_id = "PATCH-TEST002"
            issue_ref = "PROJ-123"
            
            # Should not raise exception
            tracker.link_patch_to_issue(patch_id, issue_ref)
            
            # Verify API was called
            mock_session.return_value.get.assert_called()
    
    def test_invalid_issue_reference_handling(self):
        """Test handling of invalid issue references."""
        tracker = GitHubIssueTracker(self.github_config)
        
        # Test invalid GitHub issue format
        with self.assertRaises(ValueError):
            tracker._parse_github_issue_ref("invalid-format")
        
        with self.assertRaises(ValueError):
            tracker._parse_github_issue_ref("no-hash-symbol")


class TestRequirement32_FlagPatchesForCleanup(unittest.TestCase):
    """Test Requirement 3.2: Flag patches for cleanup when upstream issues are resolved."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
        
        # Create sample patches
        self.patches = [
            PatchAnnotation(
                patch_id="PATCH-RESOLVED",
                reason="Test patch with resolved issue",
                upstream_issue="owner/repo#123",
                cleanup_task="Remove patch when issue is resolved",
                debt_level=DebtLevel.MEDIUM,
                component="test_component"
            ),
            PatchAnnotation(
                patch_id="PATCH-OPEN",
                reason="Test patch with open issue",
                upstream_issue="owner/repo#456",
                cleanup_task="Wait for upstream fix",
                debt_level=DebtLevel.HIGH,
                component="test_component"
            ),
            PatchAnnotation(
                patch_id="PATCH-NO-ISSUE",
                reason="Test patch without upstream issue",
                upstream_issue="",
                cleanup_task="Manual cleanup needed",
                debt_level=DebtLevel.LOW,
                component="test_component"
            )
        ]
    
    def test_check_patches_for_resolved_issues(self):
        """Test checking patches against resolved upstream issues."""
        with patch('requests.Session') as mock_session:
            # Mock API responses for different issue statuses
            def mock_get_response(url):
                mock_response = Mock()
                mock_response.status_code = 200
                
                if 'issues/123' in url:
                    # Resolved issue
                    mock_response.json.return_value = {
                        'number': 123,
                        'title': 'Resolved Issue',
                        'state': 'closed',
                        'html_url': 'https://github.com/owner/repo/issues/123',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-02T00:00:00Z',
                        'closed_at': '2024-01-02T00:00:00Z',
                        'assignee': None,
                        'labels': [],
                        'body': 'This issue has been resolved',
                        'id': 12345,
                        'comments': 0
                    }
                elif 'issues/456' in url:
                    # Open issue
                    mock_response.json.return_value = {
                        'number': 456,
                        'title': 'Open Issue',
                        'state': 'open',
                        'html_url': 'https://github.com/owner/repo/issues/456',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'assignee': None,
                        'labels': [],
                        'body': 'This issue is still open',
                        'id': 45678,
                        'comments': 2
                    }
                
                return mock_response
            
            mock_session.return_value.get.side_effect = mock_get_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Check patches for resolved issues
            cleanup_ready = tracker.check_patches_for_resolved_issues(self.patches)
            
            # Should flag the patch with resolved issue
            self.assertIn("PATCH-RESOLVED", cleanup_ready)
            self.assertNotIn("PATCH-OPEN", cleanup_ready)
            self.assertNotIn("PATCH-NO-ISSUE", cleanup_ready)
            
            # Verify metrics were updated
            self.assertGreater(tracker.metrics['issues_checked'], 0)
            self.assertGreater(tracker.metrics['issues_resolved'], 0)
            self.assertGreater(tracker.metrics['patches_flagged_for_cleanup'], 0)
    
    def test_issue_status_mapping(self):
        """Test proper mapping of issue statuses."""
        with patch('requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'Test Issue',
                'state': 'closed',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
                'closed_at': '2024-01-02T00:00:00Z',
                'assignee': None,
                'labels': [],
                'body': 'Test issue',
                'id': 12345,
                'comments': 0
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Test status checking
            status = tracker.check_issue_status("owner/repo#123")
            self.assertEqual(status, IssueStatus.CLOSED)


class TestRequirement33_TrackDependencyVersions(unittest.TestCase):
    """Test Requirement 3.3: Track external dependency version information."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
        
        self.patch = PatchAnnotation(
            patch_id="PATCH-DEPENDENCY",
            reason="Workaround for dependency bug",
            upstream_issue="facebook/react#12345",
            cleanup_task="Update dependency when fix is released",
            debt_level=DebtLevel.MEDIUM,
            component="frontend"
        )
    
    def test_track_dependency_versions(self):
        """Test tracking external dependency versions."""
        with patch('requests.Session') as mock_session:
            # Mock GitHub releases API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'id': 12345,
                'tag_name': 'v18.2.0',
                'name': 'React 18.2.0',
                'published_at': '2024-01-01T00:00:00Z',
                'html_url': 'https://github.com/facebook/react/releases/tag/v18.2.0',
                'prerelease': False,
                'draft': False,
                'author': {'login': 'gaearon'},
                'assets': []
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Track dependency versions
            version_info = tracker.track_dependency_versions(self.patch)
            
            # Verify version information
            self.assertEqual(version_info.dependency_name, "facebook/react")
            self.assertEqual(version_info.latest_version, "v18.2.0")
            self.assertEqual(version_info.fixed_version, "v18.2.0")
            self.assertIsNotNone(version_info.release_date)
            self.assertIsNotNone(version_info.changelog_url)
    
    def test_dependency_name_extraction(self):
        """Test extraction of dependency names from patch information."""
        tracker = GitHubIssueTracker(self.github_config)
        
        # Test extraction from upstream issue
        dependency_name = tracker._extract_dependency_name(self.patch)
        self.assertEqual(dependency_name, "facebook")
        
        # Test extraction from component name
        patch_with_component = PatchAnnotation(
            patch_id="PATCH-COMP",
            reason="Test",
            upstream_issue="",
            cleanup_task="Test",
            component="my_awesome_library"
        )
        
        dependency_name = tracker._extract_dependency_name(patch_with_component)
        self.assertEqual(dependency_name, "my-awesome-library")
    
    def test_version_info_fallback_to_tags(self):
        """Test fallback to tags when no releases are available."""
        with patch('requests.Session') as mock_session:
            def mock_get_response(url):
                mock_response = Mock()
                
                if 'releases/latest' in url:
                    # No releases available
                    mock_response.status_code = 404
                elif 'tags' in url:
                    # Tags available
                    mock_response.status_code = 200
                    mock_response.json.return_value = [
                        {
                            'name': 'v1.2.3',
                            'commit': {'sha': 'abc123'}
                        }
                    ]
                
                return mock_response
            
            mock_session.return_value.get.side_effect = mock_get_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Should fallback to tags
            version_info = tracker.get_dependency_version_info("owner/repo")
            self.assertEqual(version_info.latest_version, "v1.2.3")
            self.assertEqual(version_info.metadata['source'], 'tags')


class TestRequirement34_RemediationGuidance(unittest.TestCase):
    """Test Requirement 3.4: Include remediation guidance when root causes are identified."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
        
        self.patch = PatchAnnotation(
            patch_id="PATCH-GUIDANCE",
            reason="Temporary fix for API issue",
            upstream_issue="owner/repo#123",
            cleanup_task="Replace with proper implementation",
            debt_level=DebtLevel.HIGH,
            component="api_client",
            validation_criteria=[
                "API integration tests pass",
                "Performance improved",
                "Error handling complete"
            ]
        )
    
    def test_generate_remediation_guidance_resolved_issue(self):
        """Test remediation guidance generation for resolved issues."""
        with patch('requests.Session') as mock_session:
            # Mock resolved issue response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'API Rate Limiting Issue',
                'state': 'closed',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
                'closed_at': '2024-01-02T00:00:00Z',
                'assignee': None,
                'labels': ['bug', 'api'],
                'body': 'Fixed rate limiting in API v2',
                'id': 12345,
                'comments': 0
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Generate remediation guidance
            guidance = tracker.generate_remediation_guidance(self.patch)
            
            # Verify guidance structure
            self.assertEqual(guidance['patch_id'], "PATCH-GUIDANCE")
            self.assertIn('remediation_steps', guidance)
            self.assertIn('validation_criteria', guidance)
            self.assertIn('estimated_effort', guidance)
            self.assertIn('risk_level', guidance)
            
            # Verify guidance content for resolved issue
            self.assertGreater(len(guidance['remediation_steps']), 0)
            self.assertEqual(guidance['estimated_effort'], 'Medium')  # HIGH debt level
            self.assertEqual(guidance['risk_level'], 'High')
            
            # Should include upstream issue information
            self.assertIn('upstream_issue_title', guidance)
            self.assertIn('upstream_issue_status', guidance)
    
    def test_generate_remediation_guidance_open_issue(self):
        """Test remediation guidance generation for open issues."""
        with patch('requests.Session') as mock_session:
            # Mock open issue response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'API Issue Still Open',
                'state': 'open',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
                'assignee': {'login': 'developer'},
                'labels': ['bug'],
                'body': 'Working on fix',
                'id': 12345,
                'comments': 5
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Generate remediation guidance
            guidance = tracker.generate_remediation_guidance(self.patch)
            
            # Verify guidance for open issue
            self.assertEqual(guidance['estimated_effort'], 'Blocked')
            self.assertIn('Monitor upstream issue', guidance['remediation_steps'][0])
    
    def test_remediation_guidance_with_dependency_info(self):
        """Test remediation guidance that includes dependency version information."""
        with patch('requests.Session') as mock_session:
            def mock_get_response(url):
                mock_response = Mock()
                mock_response.status_code = 200
                
                if 'issues' in url:
                    # Issue response
                    mock_response.json.return_value = {
                        'number': 123,
                        'title': 'Fixed in latest version',
                        'state': 'closed',
                        'html_url': 'https://github.com/owner/repo/issues/123',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-02T00:00:00Z',
                        'closed_at': '2024-01-02T00:00:00Z',
                        'assignee': None,
                        'labels': [],
                        'body': 'Fixed in v2.0.0',
                        'id': 12345,
                        'comments': 0
                    }
                elif 'releases' in url:
                    # Release response
                    mock_response.json.return_value = {
                        'id': 67890,
                        'tag_name': 'v2.0.0',
                        'name': 'Version 2.0.0',
                        'published_at': '2024-01-02T00:00:00Z',
                        'html_url': 'https://github.com/owner/repo/releases/tag/v2.0.0',
                        'prerelease': False,
                        'draft': False,
                        'author': {'login': 'maintainer'},
                        'assets': []
                    }
                
                return mock_response
            
            mock_session.return_value.get.side_effect = mock_get_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Generate guidance
            guidance = tracker.generate_remediation_guidance(self.patch)
            
            # Should include dependency information
            self.assertIn('dependencies', guidance)
            if guidance['dependencies']:
                dep = guidance['dependencies'][0]
                self.assertIn('name', dep)
                self.assertIn('fixed_version', dep)


class TestRequirement35_PrioritizePatchRemoval(unittest.TestCase):
    """Test Requirement 3.5: Prioritize patch removal when upstream fixes are available."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
        
        # Create patches with different characteristics for prioritization
        self.patches = [
            PatchAnnotation(
                patch_id="PATCH-CRITICAL-RESOLVED",
                reason="Critical security patch",
                upstream_issue="owner/repo#100",
                cleanup_task="Remove ASAP",
                debt_level=DebtLevel.CRITICAL,
                component="security",
                created_date=datetime.now() - timedelta(days=120),  # Old patch
                expected_resolution=datetime.now() - timedelta(days=30)  # Overdue
            ),
            PatchAnnotation(
                patch_id="PATCH-HIGH-OPEN",
                reason="High priority workaround",
                upstream_issue="owner/repo#200",
                cleanup_task="Wait for fix",
                debt_level=DebtLevel.HIGH,
                component="core",
                created_date=datetime.now() - timedelta(days=60)
            ),
            PatchAnnotation(
                patch_id="PATCH-LOW-RECENT",
                reason="Minor workaround",
                upstream_issue="owner/repo#300",
                cleanup_task="Low priority cleanup",
                debt_level=DebtLevel.LOW,
                component="utils",
                created_date=datetime.now() - timedelta(days=10)
            )
        ]
    
    def test_prioritize_patch_removal(self):
        """Test patch removal prioritization algorithm."""
        with patch('requests.Session') as mock_session:
            def mock_get_response(url):
                mock_response = Mock()
                mock_response.status_code = 200
                
                if 'issues/100' in url:
                    # Resolved critical issue
                    mock_response.json.return_value = {
                        'number': 100,
                        'title': 'Critical Security Issue',
                        'state': 'closed',
                        'html_url': 'https://github.com/owner/repo/issues/100',
                        'created_at': '2023-10-01T00:00:00Z',
                        'updated_at': '2023-11-01T00:00:00Z',
                        'closed_at': '2023-11-01T00:00:00Z',
                        'assignee': None,
                        'labels': ['security', 'critical'],
                        'body': 'Security vulnerability fixed',
                        'id': 10000,
                        'comments': 0
                    }
                elif 'issues/200' in url:
                    # Open high priority issue
                    mock_response.json.return_value = {
                        'number': 200,
                        'title': 'High Priority Issue',
                        'state': 'open',
                        'html_url': 'https://github.com/owner/repo/issues/200',
                        'created_at': '2023-12-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                        'assignee': {'login': 'developer'},
                        'labels': ['enhancement'],
                        'body': 'Working on this',
                        'id': 20000,
                        'comments': 3
                    }
                elif 'issues/300' in url:
                    # Open low priority issue
                    mock_response.json.return_value = {
                        'number': 300,
                        'title': 'Minor Issue',
                        'state': 'open',
                        'html_url': 'https://github.com/owner/repo/issues/300',
                        'created_at': '2024-01-15T00:00:00Z',
                        'updated_at': '2024-01-15T00:00:00Z',
                        'assignee': None,
                        'labels': ['minor'],
                        'body': 'Low priority fix needed',
                        'id': 30000,
                        'comments': 0
                    }
                
                return mock_response
            
            mock_session.return_value.get.side_effect = mock_get_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Prioritize patches
            prioritized = tracker.prioritize_patch_removal(self.patches)
            
            # Verify prioritization order
            self.assertEqual(len(prioritized), 3)
            
            # Extract patch IDs in priority order
            patch_ids = [patch_id for patch_id, score in prioritized]
            
            # Critical resolved patch should be highest priority
            self.assertEqual(patch_ids[0], "PATCH-CRITICAL-RESOLVED")
            
            # Verify scores are in descending order
            scores = [score for patch_id, score in prioritized]
            self.assertEqual(scores, sorted(scores, reverse=True))
            
            # Critical patch should have highest score
            critical_score = next(score for patch_id, score in prioritized if patch_id == "PATCH-CRITICAL-RESOLVED")
            self.assertGreater(critical_score, 150)  # Should get high base score + bonuses
    
    def test_priority_scoring_factors(self):
        """Test individual factors that contribute to priority scoring."""
        tracker = GitHubIssueTracker(self.github_config)
        
        # Test debt level scoring
        critical_patch = PatchAnnotation(
            patch_id="CRITICAL",
            reason="Test",
            upstream_issue="",
            cleanup_task="Test",
            debt_level=DebtLevel.CRITICAL
        )
        
        low_patch = PatchAnnotation(
            patch_id="LOW",
            reason="Test", 
            upstream_issue="",
            cleanup_task="Test",
            debt_level=DebtLevel.LOW
        )
        
        # Mock empty responses to avoid API calls
        with patch.object(tracker, 'check_issue_status', return_value=IssueStatus.UNKNOWN):
            with patch.object(tracker, '_extract_dependency_name', return_value=None):
                critical_priority = tracker.prioritize_patch_removal([critical_patch])
                low_priority = tracker.prioritize_patch_removal([low_patch])
                
                # Critical should have higher score than low
                critical_score = critical_priority[0][1]
                low_score = low_priority[0][1]
                self.assertGreater(critical_score, low_score)


class TestIssueTrackerHealthAndObservability(unittest.TestCase):
    """Test health monitoring and observability features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.github_config = {'token': 'test-token'}
    
    def test_health_status_reporting(self):
        """Test health status reporting functionality."""
        with patch('requests.Session') as mock_session:
            # Mock successful connectivity test
            mock_response = Mock()
            mock_response.status_code = 200
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Get health status
            health = tracker.get_health_status_dict()
            
            # Verify health status structure
            self.assertIn('status', health)
            self.assertIn('api_connectivity', health)
            self.assertIn('metrics', health)
            self.assertIn('last_health_check', health)
            self.assertIn('configuration', health)
            
            # Should be healthy with successful connectivity
            self.assertEqual(health['status'], 'healthy')
            self.assertTrue(health['api_connectivity'])
    
    def test_metrics_tracking(self):
        """Test metrics tracking during operations."""
        with patch('requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'Test Issue',
                'state': 'closed',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
                'closed_at': '2024-01-02T00:00:00Z',
                'assignee': None,
                'labels': [],
                'body': 'Test issue',
                'id': 12345,
                'comments': 0
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Perform operations that should update metrics
            tracker.link_patch_to_issue("PATCH-001", "owner/repo#123")
            
            patches = [PatchAnnotation(
                patch_id="PATCH-001",
                reason="Test",
                upstream_issue="owner/repo#123",
                cleanup_task="Test"
            )]
            
            tracker.check_patches_for_resolved_issues(patches)
            
            # Verify metrics were updated
            metrics = tracker.metrics
            self.assertGreater(metrics['api_calls_made'], 0)
            self.assertGreater(metrics['issues_checked'], 0)
            self.assertGreater(metrics['issues_resolved'], 0)
            self.assertGreater(metrics['patches_flagged_for_cleanup'], 0)
    
    def test_observability_correlation(self):
        """Test observability correlation functionality."""
        with patch('requests.Session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'number': 123,
                'title': 'Performance Issue with Database Queries',
                'state': 'open',
                'html_url': 'https://github.com/owner/repo/issues/123',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
                'assignee': None,
                'labels': ['performance', 'database'],
                'body': 'Slow database queries causing timeout errors',
                'id': 12345,
                'comments': 0
            }
            mock_session.return_value.get.return_value = mock_response
            
            tracker = GitHubIssueTracker(self.github_config)
            
            # Test observability correlation
            correlation = tracker.correlate_issues_with_observability("owner/repo#123")
            
            # Verify correlation structure
            self.assertIn('issue_ref', correlation)
            self.assertIn('correlation_timestamp', correlation)
            self.assertIn('keywords', correlation)
            self.assertIn('jaeger_traces', correlation)
            self.assertIn('prometheus_metrics', correlation)
            
            # Should extract relevant keywords
            keywords = correlation['keywords']
            self.assertIn('performance', keywords)
            self.assertIn('database', keywords)


class TestFactoryFunction(unittest.TestCase):
    """Test the issue tracker factory function."""
    
    def test_create_github_tracker(self):
        """Test creating GitHub tracker via factory."""
        config = {'token': 'test-token'}
        tracker = create_issue_tracker('github', config)
        
        self.assertIsInstance(tracker, GitHubIssueTracker)
    
    def test_create_jira_tracker(self):
        """Test creating Jira tracker via factory."""
        config = {
            'base_url': 'https://test.atlassian.net',
            'username': 'test-user',
            'token': 'test-token'
        }
        tracker = create_issue_tracker('jira', config)
        
        self.assertIsInstance(tracker, JiraIssueTracker)
    
    def test_unsupported_tracker_type(self):
        """Test error handling for unsupported tracker types."""
        with self.assertRaises(ValueError):
            create_issue_tracker('unsupported', {})


def run_compliance_tests():
    """Run all requirements compliance tests."""
    print("🧪 Running Technical Debt Patch Annotation System - Issue Tracking Requirements Compliance Tests")
    print("=" * 90)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestRequirement31_ReferenceUpstreamIssues,
        TestRequirement32_FlagPatchesForCleanup,
        TestRequirement33_TrackDependencyVersions,
        TestRequirement34_RemediationGuidance,
        TestRequirement35_PrioritizePatchRemoval,
        TestIssueTrackerHealthAndObservability,
        TestFactoryFunction
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 90)
    print("📊 TEST SUMMARY")
    print("=" * 90)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, traceback in result.failures:
            error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"   - {test}: {error_msg}")
    
    if result.errors:
        print(f"\n💥 ERRORS:")
        for test, traceback in result.errors:
            error_msg = traceback.split('\n')[-2]
            print(f"   - {test}: {error_msg}")
    
    if not result.failures and not result.errors:
        print("✅ All requirements compliance tests passed!")
        print("\n🎯 REQUIREMENTS COVERAGE:")
        print("   ✅ 3.1: Reference specific upstream issues or bugs")
        print("   ✅ 3.2: Flag patches for cleanup when upstream issues are resolved")
        print("   ✅ 3.3: Track external dependency version information")
        print("   ✅ 3.4: Include remediation guidance when root causes are identified")
        print("   ✅ 3.5: Prioritize patch removal when upstream fixes are available")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_compliance_tests()
    sys.exit(0 if success else 1)