"""
Upstream Issue Tracking Integration for Technical Debt Patch Annotation System.

This module provides comprehensive integration with external issue tracking systems
including GitHub Issues and Jira REST API for enterprise environments. It monitors
issue status changes for cleanup triggers and tracks dependency version information.

Requirements addressed:
- 3.1: Reference specific upstream issues or bugs
- 3.2: Flag patches for cleanup when upstream issues are resolved
- 3.3: Track external dependency version information
- 3.4: Include remediation guidance when root causes are identified
- 3.5: Prioritize patch removal when upstream fixes are available
"""

import os
import json
import logging
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from urllib.parse import urlparse

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import PatchAnnotation, DebtLevel


class IssueStatus(Enum):
    """Status of upstream issues."""
    OPEN = "open"
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"
    UNKNOWN = "unknown"


@dataclass
class IssueInfo:
    """Information about an upstream issue."""
    issue_id: str
    title: str
    status: IssueStatus
    url: str
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    description: str = ""
    resolution: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VersionInfo:
    """Information about external dependency versions."""
    dependency_name: str
    current_version: str
    latest_version: Optional[str] = None
    fixed_version: Optional[str] = None
    release_date: Optional[datetime] = None
    changelog_url: Optional[str] = None
    security_fixes: List[str] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IssueTrackerError(Exception):
    """Base exception for issue tracker operations."""
    pass


class IssueNotFoundError(IssueTrackerError):
    """Raised when an issue cannot be found."""
    pass


class AuthenticationError(IssueTrackerError):
    """Raised when authentication fails."""
    pass


class IssueTracker(ReflectiveModule, ABC):
    """
    Abstract base class for upstream issue tracking integrations.
    
    Provides common interface for different issue tracking systems
    with systematic observability and health monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize issue tracker with configuration.
        
        Args:
            config: Configuration dictionary with tracker-specific settings
        """
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._session = requests.Session()
        self._setup_authentication()
        self._start_time = datetime.now()
        
        # Metrics tracking
        self.metrics = {
            'issues_checked': 0,
            'issues_resolved': 0,
            'patches_flagged_for_cleanup': 0,
            'api_calls_made': 0,
            'api_errors': 0,
            'last_check_timestamp': None
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get issue tracker module information."""
        return {
            'module_id': f'{self.__class__.__name__.lower()}',
            'name': self.__class__.__name__,
            'version': '1.0.0',
            'description': 'Base issue tracker for upstream issue monitoring',
            'capabilities': [cap.value for cap in self.get_capabilities()]
        }
    
    def get_capabilities(self) -> List:
        """Get issue tracker capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def graceful_degradation(self):
        """Perform graceful degradation for issue tracker."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities(),
            error_message=None
        )
    
    @abstractmethod
    def _setup_authentication(self) -> None:
        """Setup authentication for the issue tracking system."""
        pass
    
    @abstractmethod
    def get_issue_info(self, issue_ref: str) -> IssueInfo:
        """
        Get information about a specific issue.
        
        Args:
            issue_ref: Issue reference (e.g., "owner/repo#123" for GitHub)
            
        Returns:
            IssueInfo with current issue details
            
        Raises:
            IssueNotFoundError: If issue doesn't exist
            AuthenticationError: If authentication fails
            IssueTrackerError: For other API errors
        """
        pass
    
    @abstractmethod
    def check_issue_status(self, issue_ref: str) -> IssueStatus:
        """
        Check the current status of an issue.
        
        Args:
            issue_ref: Issue reference
            
        Returns:
            Current IssueStatus
        """
        pass
    
    @abstractmethod
    def get_dependency_version_info(self, dependency_name: str) -> VersionInfo:
        """
        Get version information for an external dependency.
        
        Args:
            dependency_name: Name of the dependency
            
        Returns:
            VersionInfo with current and latest version details
        """
        pass
    
    def link_patch_to_issue(self, patch_id: str, issue_ref: str) -> None:
        """
        Link a patch to an upstream issue.
        
        Args:
            patch_id: Unique patch identifier
            issue_ref: Issue reference to link to
            
        Requirements: 3.1 - Reference specific upstream issues or bugs
        """
        try:
            issue_info = self.get_issue_info(issue_ref)
            
            # Store the link in our tracking system
            link_data = {
                'patch_id': patch_id,
                'issue_ref': issue_ref,
                'issue_title': issue_info.title,
                'issue_status': issue_info.status.value,
                'linked_date': datetime.now().isoformat(),
                'issue_url': issue_info.url
            }
            
            self._store_patch_issue_link(link_data)
            
            self.logger.info(f"Linked patch {patch_id} to issue {issue_ref}")
            self.metrics['api_calls_made'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to link patch {patch_id} to issue {issue_ref}: {str(e)}")
            self.metrics['api_errors'] += 1
            raise
    
    def check_patches_for_resolved_issues(self, patches: List[PatchAnnotation]) -> List[str]:
        """
        Check patches against their upstream issues and flag resolved ones for cleanup.
        
        Args:
            patches: List of patch annotations to check
            
        Returns:
            List of patch IDs that should be flagged for cleanup
            
        Requirements: 3.2 - Flag patches for cleanup when upstream issues are resolved
        """
        patches_ready_for_cleanup = []
        
        for patch in patches:
            if not patch.upstream_issue:
                continue
                
            try:
                issue_status = self.check_issue_status(patch.upstream_issue)
                self.metrics['issues_checked'] += 1
                
                if issue_status in [IssueStatus.CLOSED, IssueStatus.RESOLVED]:
                    patches_ready_for_cleanup.append(patch.patch_id)
                    self.metrics['issues_resolved'] += 1
                    self.metrics['patches_flagged_for_cleanup'] += 1
                    
                    self.logger.info(
                        f"Patch {patch.patch_id} flagged for cleanup - "
                        f"upstream issue {patch.upstream_issue} is {issue_status.value}"
                    )
                    
                    # Notify about cleanup opportunity
                    self._notify_patch_cleanup_ready(patch, issue_status)
                    
            except Exception as e:
                self.logger.warning(
                    f"Failed to check status for issue {patch.upstream_issue} "
                    f"(patch {patch.patch_id}): {str(e)}"
                )
                self.metrics['api_errors'] += 1
        
        self.metrics['last_check_timestamp'] = datetime.now().isoformat()
        return patches_ready_for_cleanup
    
    def track_dependency_versions(self, patch: PatchAnnotation) -> VersionInfo:
        """
        Track external dependency versions for a patch.
        
        Args:
            patch: Patch annotation to track dependencies for
            
        Returns:
            VersionInfo with dependency version details
            
        Requirements: 3.3 - Track external dependency version information
        """
        # Extract dependency name from patch metadata or upstream issue
        dependency_name = self._extract_dependency_name(patch)
        
        if not dependency_name:
            raise ValueError(f"Cannot determine dependency name for patch {patch.patch_id}")
        
        try:
            version_info = self.get_dependency_version_info(dependency_name)
            
            # Store version tracking information
            tracking_data = {
                'patch_id': patch.patch_id,
                'dependency_name': dependency_name,
                'current_version': version_info.current_version,
                'latest_version': version_info.latest_version,
                'fixed_version': version_info.fixed_version,
                'tracked_date': datetime.now().isoformat()
            }
            
            self._store_dependency_tracking(tracking_data)
            
            self.logger.info(
                f"Tracking dependency {dependency_name} for patch {patch.patch_id}: "
                f"current={version_info.current_version}, latest={version_info.latest_version}"
            )
            
            return version_info
            
        except Exception as e:
            self.logger.error(
                f"Failed to track dependency versions for patch {patch.patch_id}: {str(e)}"
            )
            raise
    
    def correlate_issues_with_observability(self, issue_ref: str) -> Dict[str, Any]:
        """
        Correlate issues with Jaeger traces and Prometheus metrics.
        
        Args:
            issue_ref: Issue reference to correlate
            
        Returns:
            Dictionary with observability correlation data
        """
        correlation_data = {
            'issue_ref': issue_ref,
            'correlation_timestamp': datetime.now().isoformat(),
            'jaeger_traces': [],
            'prometheus_metrics': [],
            'performance_impact': None
        }
        
        try:
            issue_info = self.get_issue_info(issue_ref)
            
            # Extract keywords from issue for correlation
            keywords = self._extract_correlation_keywords(issue_info)
            
            # TODO: Integrate with Jaeger and Prometheus when available
            # This would search for traces and metrics related to the issue
            
            correlation_data['keywords'] = keywords
            correlation_data['issue_title'] = issue_info.title
            correlation_data['issue_status'] = issue_info.status.value
            
            self.logger.info(f"Correlated issue {issue_ref} with observability data")
            
        except Exception as e:
            self.logger.warning(f"Failed to correlate issue {issue_ref}: {str(e)}")
            correlation_data['error'] = str(e)
        
        return correlation_data
    
    def generate_remediation_guidance(self, patch: PatchAnnotation) -> Dict[str, Any]:
        """
        Generate remediation guidance when root causes are identified.
        
        Args:
            patch: Patch annotation to generate guidance for
            
        Returns:
            Dictionary with remediation guidance
            
        Requirements: 3.4 - Include remediation guidance when root causes are identified
        """
        guidance = {
            'patch_id': patch.patch_id,
            'generated_date': datetime.now().isoformat(),
            'remediation_steps': [],
            'validation_criteria': patch.validation_criteria.copy(),
            'estimated_effort': 'Unknown',
            'risk_level': patch.debt_level.value,
            'dependencies': []
        }
        
        try:
            if patch.upstream_issue:
                issue_info = self.get_issue_info(patch.upstream_issue)
                
                # Generate guidance based on issue information
                guidance['upstream_issue_title'] = issue_info.title
                guidance['upstream_issue_status'] = issue_info.status.value
                
                if issue_info.status in [IssueStatus.CLOSED, IssueStatus.RESOLVED]:
                    guidance['remediation_steps'] = [
                        f"Verify that upstream issue {patch.upstream_issue} is resolved",
                        "Remove the temporary patch code",
                        "Implement proper solution based on upstream fix",
                        "Run validation tests to ensure functionality is maintained",
                        "Update documentation to reflect the permanent solution"
                    ]
                    guidance['estimated_effort'] = 'Low' if patch.debt_level in [DebtLevel.LOW, DebtLevel.MEDIUM] else 'Medium'
                else:
                    guidance['remediation_steps'] = [
                        f"Monitor upstream issue {patch.upstream_issue} for resolution",
                        "Consider alternative solutions if issue remains open",
                        "Evaluate if patch can be improved while waiting for upstream fix"
                    ]
                    guidance['estimated_effort'] = 'Blocked'
                
                # Check for dependency version information
                try:
                    dependency_name = self._extract_dependency_name(patch)
                    if dependency_name:
                        version_info = self.get_dependency_version_info(dependency_name)
                        guidance['dependencies'].append({
                            'name': dependency_name,
                            'current_version': version_info.current_version,
                            'latest_version': version_info.latest_version,
                            'fixed_version': version_info.fixed_version
                        })
                        
                        if version_info.fixed_version:
                            guidance['remediation_steps'].insert(0, 
                                f"Upgrade {dependency_name} to version {version_info.fixed_version} or later"
                            )
                except Exception:
                    pass  # Dependency tracking is optional
            
            self.logger.info(f"Generated remediation guidance for patch {patch.patch_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to generate guidance for patch {patch.patch_id}: {str(e)}")
            guidance['error'] = str(e)
        
        return guidance
    
    def prioritize_patch_removal(self, patches: List[PatchAnnotation]) -> List[Tuple[str, int]]:
        """
        Prioritize patch removal when upstream fixes are available.
        
        Args:
            patches: List of patch annotations to prioritize
            
        Returns:
            List of tuples (patch_id, priority_score) sorted by priority
            
        Requirements: 3.5 - Prioritize patch removal when upstream fixes are available
        """
        prioritized_patches = []
        
        for patch in patches:
            priority_score = 0
            
            try:
                # Base priority on debt level
                debt_scores = {
                    DebtLevel.CRITICAL: 100,
                    DebtLevel.HIGH: 75,
                    DebtLevel.MEDIUM: 50,
                    DebtLevel.LOW: 25
                }
                priority_score += debt_scores.get(patch.debt_level, 25)
                
                # Check upstream issue status
                if patch.upstream_issue:
                    issue_status = self.check_issue_status(patch.upstream_issue)
                    
                    if issue_status in [IssueStatus.CLOSED, IssueStatus.RESOLVED]:
                        priority_score += 50  # High priority for resolved issues
                    elif issue_status == IssueStatus.IN_PROGRESS:
                        priority_score += 25  # Medium priority for in-progress issues
                
                # Check dependency versions
                try:
                    dependency_name = self._extract_dependency_name(patch)
                    if dependency_name:
                        version_info = self.get_dependency_version_info(dependency_name)
                        if version_info.fixed_version:
                            priority_score += 30  # Boost for available fixes
                except Exception:
                    pass
                
                # Age factor - older patches get higher priority
                if patch.created_date:
                    age_days = (datetime.now() - patch.created_date).days
                    if age_days > 90:
                        priority_score += 20
                    elif age_days > 30:
                        priority_score += 10
                
                # Expected resolution factor
                if patch.expected_resolution and patch.expected_resolution < datetime.now():
                    priority_score += 25  # Overdue patches get priority boost
                
                prioritized_patches.append((patch.patch_id, priority_score))
                
            except Exception as e:
                self.logger.warning(f"Failed to prioritize patch {patch.patch_id}: {str(e)}")
                # Give default priority for patches we can't evaluate
                prioritized_patches.append((patch.patch_id, 25))
        
        # Sort by priority score (highest first)
        prioritized_patches.sort(key=lambda x: x[1], reverse=True)
        
        self.logger.info(f"Prioritized {len(prioritized_patches)} patches for removal")
        return prioritized_patches
    
    def get_health_status(self):
        """
        Get health status of the issue tracker integration.
        
        Returns:
            ModuleHealth with health status information
        """
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        try:
            # Test API connectivity
            test_result = self._test_api_connectivity()
            
            status = ModuleStatus.HEALTHY if test_result else ModuleStatus.ERROR
            health_score = 1.0 if test_result else 0.0
            issues = [] if test_result else ["API connectivity failed"]
            
            return ModuleHealth(
                module_id=self.__class__.__name__,
                status=status,
                health_score=health_score,
                issues=issues,
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0.0,
                error_count=self.metrics.get('api_errors', 0),
                warning_count=0
            )
        except Exception as e:
            return ModuleHealth(
                module_id=self.__class__.__name__,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health check failed: {str(e)}"],
                last_check=datetime.now(),
                uptime_seconds=0.0,
                error_count=self.metrics.get('api_errors', 0) + 1,
                warning_count=0
            )
    
    def get_health_status_dict(self) -> Dict[str, Any]:
        """
        Get health status as dictionary (for backward compatibility).
        
        Returns:
            Dictionary with health status information
        """
        try:
            # Test API connectivity
            test_result = self._test_api_connectivity()
            
            return {
                'status': 'healthy' if test_result else 'unhealthy',
                'api_connectivity': test_result,
                'metrics': self.metrics.copy(),
                'last_health_check': datetime.now().isoformat(),
                'configuration': {
                    'tracker_type': self.__class__.__name__,
                    'base_url': getattr(self, 'base_url', 'Not configured')
                }
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'metrics': self.metrics.copy(),
                'last_health_check': datetime.now().isoformat()
            }
    
    def _test_api_connectivity(self) -> bool:
        """Test API connectivity. Override in subclasses."""
        return True
    
    def _extract_dependency_name(self, patch: PatchAnnotation) -> Optional[str]:
        """Extract dependency name from patch information."""
        # Try to extract from upstream issue reference
        if patch.upstream_issue:
            # Look for GitHub format "owner/repo#issue"
            if '#' in patch.upstream_issue:
                repo_part = patch.upstream_issue.split('#')[0]
                if '/' in repo_part:
                    return repo_part  # Return full "owner/repo"
            
            # Look for common patterns like "package-name", "library/issue"
            parts = patch.upstream_issue.split('/')
            if len(parts) >= 2:
                return '/'.join(parts[:2])  # Return "owner/repo" format
        
        # Try to extract from component name
        if patch.component:
            return patch.component.lower().replace('_', '-')
        
        return None
    
    def _extract_correlation_keywords(self, issue_info: IssueInfo) -> List[str]:
        """Extract keywords from issue for observability correlation."""
        keywords = []
        
        # Extract from title
        title_words = issue_info.title.lower().split()
        keywords.extend([word for word in title_words if len(word) > 3])
        
        # Extract from labels
        keywords.extend([label.lower() for label in issue_info.labels])
        
        # Common technical keywords
        tech_keywords = ['performance', 'error', 'timeout', 'memory', 'cpu', 'database', 'api']
        keywords.extend([kw for kw in tech_keywords if kw in issue_info.title.lower() or kw in issue_info.description.lower()])
        
        return list(set(keywords))  # Remove duplicates
    
    def _store_patch_issue_link(self, link_data: Dict[str, Any]) -> None:
        """Store patch-to-issue link. Override in subclasses for persistence."""
        self.logger.debug(f"Storing patch-issue link: {link_data}")
    
    def _store_dependency_tracking(self, tracking_data: Dict[str, Any]) -> None:
        """Store dependency tracking data. Override in subclasses for persistence."""
        self.logger.debug(f"Storing dependency tracking: {tracking_data}")
    
    def _notify_patch_cleanup_ready(self, patch: PatchAnnotation, issue_status: IssueStatus) -> None:
        """Notify about patch cleanup opportunity. Override in subclasses."""
        self.logger.info(
            f"CLEANUP READY: Patch {patch.patch_id} can be cleaned up - "
            f"upstream issue {patch.upstream_issue} is {issue_status.value}"
        )


class GitHubIssueTracker(IssueTracker):
    """
    GitHub Issues API integration for patch-to-issue linking.
    
    Provides comprehensive GitHub Issues integration with authentication,
    issue status monitoring, and dependency version tracking.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize GitHub issue tracker.
        
        Args:
            config: Configuration with 'token' and optional 'base_url'
        """
        self.base_url = config.get('base_url', 'https://api.github.com')
        super().__init__(config)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get GitHub issue tracker module information."""
        return {
            'module_id': 'github_issue_tracker',
            'name': 'GitHub Issue Tracker',
            'version': '1.0.0',
            'description': 'GitHub Issues API integration for patch tracking',
            'base_url': self.base_url,
            'capabilities': [cap.value for cap in self.get_capabilities()]
        }
    
    def get_capabilities(self) -> List:
        """Get GitHub issue tracker capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def graceful_degradation(self):
        """Perform graceful degradation for GitHub tracker."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        # Test API connectivity
        try:
            if self._test_api_connectivity():
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[],
                    remaining_capabilities=self.get_capabilities()
                )
            else:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[ModuleCapability.API_INTEGRATION],
                    remaining_capabilities=[ModuleCapability.DATA_PROCESSING],
                    error_message="GitHub API connectivity lost - operating in offline mode"
                )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=f"GitHub tracker degradation failed: {str(e)}"
            )
    
    def _setup_authentication(self) -> None:
        """Setup GitHub API authentication."""
        token = self.config.get('token') or os.getenv('GITHUB_TOKEN')
        if not token:
            raise AuthenticationError("GitHub token not provided in config or GITHUB_TOKEN environment variable")
        
        self._session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TechnicalDebtPatchAnnotationSystem/1.0'
        })
    
    def get_issue_info(self, issue_ref: str) -> IssueInfo:
        """
        Get GitHub issue information.
        
        Args:
            issue_ref: GitHub issue reference in format "owner/repo#number"
            
        Returns:
            IssueInfo with GitHub issue details
        """
        owner, repo, issue_number = self._parse_github_issue_ref(issue_ref)
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        
        try:
            response = self._session.get(url)
            response.raise_for_status()
            
            issue_data = response.json()
            
            # Map GitHub status to our enum
            status_mapping = {
                'open': IssueStatus.OPEN,
                'closed': IssueStatus.CLOSED
            }
            
            status = status_mapping.get(issue_data['state'], IssueStatus.UNKNOWN)
            
            # Parse dates
            created_date = datetime.fromisoformat(issue_data['created_at'].replace('Z', '+00:00'))
            updated_date = datetime.fromisoformat(issue_data['updated_at'].replace('Z', '+00:00'))
            closed_date = None
            if issue_data.get('closed_at'):
                closed_date = datetime.fromisoformat(issue_data['closed_at'].replace('Z', '+00:00'))
            
            return IssueInfo(
                issue_id=str(issue_data['number']),
                title=issue_data['title'],
                status=status,
                url=issue_data['html_url'],
                created_date=created_date,
                updated_date=updated_date,
                closed_date=closed_date,
                assignee=issue_data['assignee']['login'] if issue_data.get('assignee') else None,
                labels=[label['name'] for label in issue_data.get('labels', [])],
                description=issue_data.get('body', ''),
                metadata={
                    'github_id': issue_data['id'],
                    'state': issue_data['state'],
                    'comments': issue_data.get('comments', 0),
                    'milestone': issue_data.get('milestone', {}).get('title') if issue_data.get('milestone') else None
                }
            )
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise IssueNotFoundError(f"GitHub issue not found: {issue_ref}")
            elif e.response.status_code == 401:
                raise AuthenticationError("GitHub API authentication failed")
            else:
                raise IssueTrackerError(f"GitHub API error: {e}")
        except Exception as e:
            raise IssueTrackerError(f"Failed to get GitHub issue info: {e}")
    
    def check_issue_status(self, issue_ref: str) -> IssueStatus:
        """Check GitHub issue status."""
        issue_info = self.get_issue_info(issue_ref)
        return issue_info.status
    
    def get_dependency_version_info(self, dependency_name: str) -> VersionInfo:
        """
        Get version information for a GitHub repository dependency.
        
        Args:
            dependency_name: Repository name in format "owner/repo"
            
        Returns:
            VersionInfo with release information
        """
        if '/' not in dependency_name:
            raise ValueError(f"GitHub dependency name must be in format 'owner/repo': {dependency_name}")
        
        owner, repo = dependency_name.split('/', 1)
        
        # Get latest release
        url = f"{self.base_url}/repos/{owner}/{repo}/releases/latest"
        
        try:
            response = self._session.get(url)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Parse release date
            release_date = None
            if release_data.get('published_at'):
                release_date = datetime.fromisoformat(release_data['published_at'].replace('Z', '+00:00'))
            
            return VersionInfo(
                dependency_name=dependency_name,
                current_version="unknown",  # We don't know the current version being used
                latest_version=release_data['tag_name'],
                fixed_version=release_data['tag_name'],  # Assume latest is the fix
                release_date=release_date,
                changelog_url=release_data.get('html_url'),
                metadata={
                    'github_release_id': release_data['id'],
                    'prerelease': release_data.get('prerelease', False),
                    'draft': release_data.get('draft', False),
                    'author': release_data.get('author', {}).get('login'),
                    'assets_count': len(release_data.get('assets', []))
                }
            )
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # No releases found, try to get tags
                return self._get_version_from_tags(owner, repo)
            else:
                raise IssueTrackerError(f"GitHub API error getting releases: {e}")
        except Exception as e:
            raise IssueTrackerError(f"Failed to get GitHub version info: {e}")
    
    def _get_version_from_tags(self, owner: str, repo: str) -> VersionInfo:
        """Get version information from repository tags."""
        url = f"{self.base_url}/repos/{owner}/{repo}/tags"
        
        try:
            response = self._session.get(url)
            response.raise_for_status()
            
            tags_data = response.json()
            
            if not tags_data:
                return VersionInfo(
                    dependency_name=f"{owner}/{repo}",
                    current_version="unknown",
                    latest_version="no-releases",
                    metadata={'source': 'tags', 'tags_count': 0}
                )
            
            # Get the first (latest) tag
            latest_tag = tags_data[0]
            
            return VersionInfo(
                dependency_name=f"{owner}/{repo}",
                current_version="unknown",
                latest_version=latest_tag['name'],
                fixed_version=latest_tag['name'],
                metadata={
                    'source': 'tags',
                    'tags_count': len(tags_data),
                    'commit_sha': latest_tag['commit']['sha']
                }
            )
            
        except Exception as e:
            raise IssueTrackerError(f"Failed to get GitHub tags: {e}")
    
    def _parse_github_issue_ref(self, issue_ref: str) -> Tuple[str, str, str]:
        """Parse GitHub issue reference."""
        if '#' not in issue_ref:
            raise ValueError(f"Invalid GitHub issue reference format: {issue_ref}")
        
        repo_part, issue_number = issue_ref.rsplit('#', 1)
        
        if '/' not in repo_part:
            raise ValueError(f"Invalid GitHub issue reference format: {issue_ref}")
        
        owner, repo = repo_part.rsplit('/', 1)
        
        return owner, repo, issue_number
    
    def _test_api_connectivity(self) -> bool:
        """Test GitHub API connectivity."""
        try:
            response = self._session.get(f"{self.base_url}/user")
            return response.status_code == 200
        except Exception:
            return False


class JiraIssueTracker(IssueTracker):
    """
    Jira REST API integration for enterprise environments.
    
    Provides comprehensive Jira integration with authentication,
    issue status monitoring, and project management features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Jira issue tracker.
        
        Args:
            config: Configuration with 'base_url', 'username', 'token'
        """
        self.base_url = config.get('base_url')
        if not self.base_url:
            raise ValueError("Jira base_url is required in configuration")
        
        # Ensure base_url ends with /rest/api/2
        if not self.base_url.endswith('/rest/api/2'):
            if self.base_url.endswith('/'):
                self.base_url += 'rest/api/2'
            else:
                self.base_url += '/rest/api/2'
        
        super().__init__(config)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get Jira issue tracker module information."""
        return {
            'module_id': 'jira_issue_tracker',
            'name': 'Jira Issue Tracker',
            'version': '1.0.0',
            'description': 'Jira REST API integration for enterprise patch tracking',
            'base_url': self.base_url,
            'capabilities': [cap.value for cap in self.get_capabilities()]
        }
    
    def get_capabilities(self) -> List:
        """Get Jira issue tracker capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def graceful_degradation(self):
        """Perform graceful degradation for Jira tracker."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult, ModuleCapability
        
        # Test API connectivity
        try:
            if self._test_api_connectivity():
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[],
                    remaining_capabilities=self.get_capabilities()
                )
            else:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[ModuleCapability.API_INTEGRATION],
                    remaining_capabilities=[ModuleCapability.DATA_PROCESSING],
                    error_message="Jira API connectivity lost - operating in offline mode"
                )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=f"Jira tracker degradation failed: {str(e)}"
            )
    
    def _setup_authentication(self) -> None:
        """Setup Jira API authentication."""
        username = self.config.get('username') or os.getenv('JIRA_USERNAME')
        token = self.config.get('token') or os.getenv('JIRA_TOKEN')
        
        if not username or not token:
            raise AuthenticationError(
                "Jira username and token required in config or "
                "JIRA_USERNAME/JIRA_TOKEN environment variables"
            )
        
        self._session.auth = (username, token)
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_issue_info(self, issue_ref: str) -> IssueInfo:
        """
        Get Jira issue information.
        
        Args:
            issue_ref: Jira issue key (e.g., "PROJ-123")
            
        Returns:
            IssueInfo with Jira issue details
        """
        url = f"{self.base_url}/issue/{issue_ref}"
        
        try:
            response = self._session.get(url)
            response.raise_for_status()
            
            issue_data = response.json()
            fields = issue_data['fields']
            
            # Map Jira status to our enum
            jira_status = fields['status']['name'].lower()
            status_mapping = {
                'open': IssueStatus.OPEN,
                'in progress': IssueStatus.IN_PROGRESS,
                'done': IssueStatus.CLOSED,
                'closed': IssueStatus.CLOSED,
                'resolved': IssueStatus.RESOLVED,
                'cancelled': IssueStatus.WONT_FIX,
                'duplicate': IssueStatus.DUPLICATE
            }
            
            status = IssueStatus.UNKNOWN
            for key, value in status_mapping.items():
                if key in jira_status:
                    status = value
                    break
            
            # Parse dates
            created_date = datetime.fromisoformat(fields['created'].replace('Z', '+00:00').replace('.000', ''))
            updated_date = datetime.fromisoformat(fields['updated'].replace('Z', '+00:00').replace('.000', ''))
            
            # Resolution date
            closed_date = None
            if fields.get('resolutiondate'):
                closed_date = datetime.fromisoformat(fields['resolutiondate'].replace('Z', '+00:00').replace('.000', ''))
            
            # Build issue URL
            base_url_parts = self.base_url.split('/rest/api/2')[0]
            issue_url = f"{base_url_parts}/browse/{issue_ref}"
            
            return IssueInfo(
                issue_id=issue_ref,
                title=fields['summary'],
                status=status,
                url=issue_url,
                created_date=created_date,
                updated_date=updated_date,
                closed_date=closed_date,
                assignee=fields['assignee']['displayName'] if fields.get('assignee') else None,
                labels=[label for label in fields.get('labels', [])],
                description=fields.get('description', ''),
                resolution=fields.get('resolution', {}).get('name') if fields.get('resolution') else None,
                metadata={
                    'jira_id': issue_data['id'],
                    'project_key': fields['project']['key'],
                    'issue_type': fields['issuetype']['name'],
                    'priority': fields.get('priority', {}).get('name'),
                    'status_category': fields['status']['statusCategory']['name'],
                    'components': [comp['name'] for comp in fields.get('components', [])],
                    'fix_versions': [ver['name'] for ver in fields.get('fixVersions', [])]
                }
            )
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise IssueNotFoundError(f"Jira issue not found: {issue_ref}")
            elif e.response.status_code == 401:
                raise AuthenticationError("Jira API authentication failed")
            else:
                raise IssueTrackerError(f"Jira API error: {e}")
        except Exception as e:
            raise IssueTrackerError(f"Failed to get Jira issue info: {e}")
    
    def check_issue_status(self, issue_ref: str) -> IssueStatus:
        """Check Jira issue status."""
        issue_info = self.get_issue_info(issue_ref)
        return issue_info.status
    
    def get_dependency_version_info(self, dependency_name: str) -> VersionInfo:
        """
        Get version information for a dependency tracked in Jira.
        
        This is a basic implementation that could be extended to integrate
        with specific Jira fields or external dependency tracking systems.
        
        Args:
            dependency_name: Name of the dependency
            
        Returns:
            VersionInfo with basic dependency information
        """
        # For Jira, we provide a basic implementation
        # In practice, this might query specific Jira fields or external systems
        
        return VersionInfo(
            dependency_name=dependency_name,
            current_version="unknown",
            latest_version="unknown",
            metadata={
                'source': 'jira',
                'note': 'Dependency version tracking not fully implemented for Jira'
            }
        )
    
    def _test_api_connectivity(self) -> bool:
        """Test Jira API connectivity."""
        try:
            response = self._session.get(f"{self.base_url}/myself")
            return response.status_code == 200
        except Exception:
            return False


def create_issue_tracker(tracker_type: str, config: Dict[str, Any]) -> IssueTracker:
    """
    Factory function to create issue tracker instances.
    
    Args:
        tracker_type: Type of tracker ('github' or 'jira')
        config: Configuration dictionary
        
    Returns:
        Configured IssueTracker instance
        
    Raises:
        ValueError: If tracker_type is not supported
    """
    tracker_classes = {
        'github': GitHubIssueTracker,
        'jira': JiraIssueTracker
    }
    
    if tracker_type.lower() not in tracker_classes:
        raise ValueError(f"Unsupported tracker type: {tracker_type}. Supported types: {list(tracker_classes.keys())}")
    
    return tracker_classes[tracker_type.lower()](config)