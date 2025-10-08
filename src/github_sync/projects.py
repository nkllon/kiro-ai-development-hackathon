"""
Project management integration for GitHub synchronization.

This module provides functionality for integrating with GitHub project boards,
milestones, and progress tracking features.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from .client import GitHubAPIClient
from .auth import AuthenticationManager

logger = logging.getLogger(__name__)


class ProjectState(Enum):
    """Project board states."""
    OPEN = "open"
    CLOSED = "closed"


class MilestoneState(Enum):
    """Milestone states."""
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class ProjectColumn:
    """Represents a project board column."""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    cards_count: int = 0


@dataclass
class ProjectCard:
    """Represents a card in a project board."""
    id: int
    note: Optional[str]
    created_at: datetime
    updated_at: datetime
    column_id: int
    content_url: Optional[str] = None
    content_type: Optional[str] = None  # Issue or PullRequest
    content_id: Optional[int] = None


@dataclass
class Project:
    """Represents a GitHub project board."""
    id: int
    name: str
    body: Optional[str]
    state: ProjectState
    created_at: datetime
    updated_at: datetime
    creator: str
    columns: List[ProjectColumn] = field(default_factory=list)
    cards: List[ProjectCard] = field(default_factory=list)


@dataclass
class Milestone:
    """Represents a GitHub milestone."""
    id: int
    number: int
    title: str
    description: Optional[str]
    state: MilestoneState
    created_at: datetime
    updated_at: datetime
    due_on: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    creator: Optional[str] = None
    open_issues: int = 0
    closed_issues: int = 0
    
    @property
    def progress_percentage(self) -> float:
        """Calculate milestone progress percentage."""
        total_issues = self.open_issues + self.closed_issues
        if total_issues == 0:
            return 0.0
        return (self.closed_issues / total_issues) * 100.0


@dataclass
class Notification:
    """Represents a GitHub notification."""
    id: str
    title: str
    subject_type: str  # Issue, PullRequest, etc.
    subject_title: str
    subject_url: str
    repository_name: str
    repository_full_name: str
    reason: str  # subscribed, mentioned, etc.
    unread: bool
    updated_at: datetime
    last_read_at: Optional[datetime] = None


class ProjectManagementIntegration:
    """
    Handles GitHub project management integration.
    
    This class provides functionality for synchronizing with GitHub project boards,
    milestones, and managing notifications.
    """
    
    def __init__(self, api_client: GitHubAPIClient, auth_manager: AuthenticationManager):
        """
        Initialize project management integration.
        
        Args:
            api_client: GitHub API client
            auth_manager: Authentication manager
        """
        self.api_client = api_client
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
    
    async def get_repository_projects(self, owner: str, repo: str) -> List[Project]:
        """
        Get all project boards for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of project boards
        """
        try:
            projects_data = await self.api_client.get_repository_projects(owner, repo)
            projects = []
            
            for project_data in projects_data:
                # Get project columns and cards
                columns = await self.get_project_columns(project_data['id'])
                cards = []
                for column in columns:
                    column_cards = await self.get_column_cards(column.id)
                    cards.extend(column_cards)
                
                project = Project(
                    id=project_data['id'],
                    name=project_data['name'],
                    body=project_data.get('body'),
                    state=ProjectState(project_data['state']),
                    created_at=datetime.fromisoformat(project_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(project_data['updated_at'].replace('Z', '+00:00')),
                    creator=project_data['creator']['login'],
                    columns=columns,
                    cards=cards
                )
                projects.append(project)
            
            return projects
            
        except Exception as e:
            self.logger.error(f"Failed to get projects for {owner}/{repo}: {e}")
            raise
    
    async def get_project_columns(self, project_id: int) -> List[ProjectColumn]:
        """
        Get columns for a project board.
        
        Args:
            project_id: Project board ID
            
        Returns:
            List of project columns
        """
        try:
            columns_data = await self.api_client.get_project_columns(project_id)
            columns = []
            
            for column_data in columns_data:
                column = ProjectColumn(
                    id=column_data['id'],
                    name=column_data['name'],
                    created_at=datetime.fromisoformat(column_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(column_data['updated_at'].replace('Z', '+00:00'))
                )
                columns.append(column)
            
            return columns
            
        except Exception as e:
            self.logger.error(f"Failed to get columns for project {project_id}: {e}")
            raise
    
    async def get_column_cards(self, column_id: int) -> List[ProjectCard]:
        """
        Get cards for a project column.
        
        Args:
            column_id: Project column ID
            
        Returns:
            List of project cards
        """
        try:
            cards_data = await self.api_client.get_column_cards(column_id)
            cards = []
            
            for card_data in cards_data:
                card = ProjectCard(
                    id=card_data['id'],
                    note=card_data.get('note'),
                    created_at=datetime.fromisoformat(card_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(card_data['updated_at'].replace('Z', '+00:00')),
                    column_id=column_id,
                    content_url=card_data.get('content_url'),
                    content_type=self._extract_content_type(card_data.get('content_url')),
                    content_id=self._extract_content_id(card_data.get('content_url'))
                )
                cards.append(card)
            
            return cards
            
        except Exception as e:
            self.logger.error(f"Failed to get cards for column {column_id}: {e}")
            raise
    
    def _extract_content_type(self, content_url: Optional[str]) -> Optional[str]:
        """Extract content type from content URL."""
        if not content_url:
            return None
        
        if '/issues/' in content_url:
            return 'Issue'
        elif '/pulls/' in content_url:
            return 'PullRequest'
        
        return None
    
    def _extract_content_id(self, content_url: Optional[str]) -> Optional[int]:
        """Extract content ID from content URL."""
        if not content_url:
            return None
        
        try:
            # Extract ID from URL like https://api.github.com/repos/owner/repo/issues/123
            parts = content_url.split('/')
            return int(parts[-1])
        except (ValueError, IndexError):
            return None
    
    async def get_repository_milestones(self, owner: str, repo: str, state: str = "open") -> List[Milestone]:
        """
        Get milestones for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Milestone state filter ("open", "closed", "all")
            
        Returns:
            List of milestones
        """
        try:
            milestones_data = await self.api_client.get_repository_milestones(owner, repo, state)
            milestones = []
            
            for milestone_data in milestones_data:
                milestone = Milestone(
                    id=milestone_data['id'],
                    number=milestone_data['number'],
                    title=milestone_data['title'],
                    description=milestone_data.get('description'),
                    state=MilestoneState(milestone_data['state']),
                    created_at=datetime.fromisoformat(milestone_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(milestone_data['updated_at'].replace('Z', '+00:00')),
                    due_on=datetime.fromisoformat(milestone_data['due_on'].replace('Z', '+00:00')) if milestone_data.get('due_on') else None,
                    closed_at=datetime.fromisoformat(milestone_data['closed_at'].replace('Z', '+00:00')) if milestone_data.get('closed_at') else None,
                    creator=milestone_data['creator']['login'] if milestone_data.get('creator') else None,
                    open_issues=milestone_data.get('open_issues', 0),
                    closed_issues=milestone_data.get('closed_issues', 0)
                )
                milestones.append(milestone)
            
            return milestones
            
        except Exception as e:
            self.logger.error(f"Failed to get milestones for {owner}/{repo}: {e}")
            raise
    
    async def create_milestone(self, owner: str, repo: str, title: str, 
                             description: Optional[str] = None, 
                             due_on: Optional[datetime] = None) -> Milestone:
        """
        Create a new milestone.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Milestone title
            description: Milestone description
            due_on: Due date
            
        Returns:
            Created milestone
        """
        try:
            milestone_data = {
                'title': title
            }
            
            if description:
                milestone_data['description'] = description
            
            if due_on:
                milestone_data['due_on'] = due_on.isoformat()
            
            response = await self.api_client.create_milestone(owner, repo, milestone_data)
            
            return Milestone(
                id=response['id'],
                number=response['number'],
                title=response['title'],
                description=response.get('description'),
                state=MilestoneState(response['state']),
                created_at=datetime.fromisoformat(response['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(response['updated_at'].replace('Z', '+00:00')),
                due_on=datetime.fromisoformat(response['due_on'].replace('Z', '+00:00')) if response.get('due_on') else None,
                creator=response['creator']['login'] if response.get('creator') else None,
                open_issues=response.get('open_issues', 0),
                closed_issues=response.get('closed_issues', 0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create milestone in {owner}/{repo}: {e}")
            raise
    
    async def get_notifications(self, all_notifications: bool = False, 
                              participating: bool = False) -> List[Notification]:
        """
        Get GitHub notifications for the authenticated user.
        
        Args:
            all_notifications: Include read notifications
            participating: Only notifications where user is participating
            
        Returns:
            List of notifications
        """
        try:
            notifications_data = await self.api_client.get_notifications(all_notifications, participating)
            notifications = []
            
            for notification_data in notifications_data:
                notification = Notification(
                    id=notification_data['id'],
                    title=notification_data['subject']['title'],
                    subject_type=notification_data['subject']['type'],
                    subject_title=notification_data['subject']['title'],
                    subject_url=notification_data['subject']['url'],
                    repository_name=notification_data['repository']['name'],
                    repository_full_name=notification_data['repository']['full_name'],
                    reason=notification_data['reason'],
                    unread=notification_data['unread'],
                    updated_at=datetime.fromisoformat(notification_data['updated_at'].replace('Z', '+00:00')),
                    last_read_at=datetime.fromisoformat(notification_data['last_read_at'].replace('Z', '+00:00')) if notification_data.get('last_read_at') else None
                )
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"Failed to get notifications: {e}")
            raise
    
    async def mark_notification_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful
        """
        try:
            await self.api_client.mark_notification_as_read(notification_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            raise
    
    async def get_project_progress_summary(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get a summary of project progress across all project boards.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Project progress summary
        """
        try:
            projects = await self.get_repository_projects(owner, repo)
            milestones = await self.get_repository_milestones(owner, repo, "all")
            
            # Calculate project statistics
            total_projects = len(projects)
            open_projects = sum(1 for p in projects if p.state == ProjectState.OPEN)
            closed_projects = total_projects - open_projects
            
            # Calculate milestone statistics
            total_milestones = len(milestones)
            open_milestones = sum(1 for m in milestones if m.state == MilestoneState.OPEN)
            closed_milestones = total_milestones - open_milestones
            
            # Calculate overall progress
            total_milestone_issues = sum(m.open_issues + m.closed_issues for m in milestones)
            completed_milestone_issues = sum(m.closed_issues for m in milestones)
            
            overall_progress = 0.0
            if total_milestone_issues > 0:
                overall_progress = (completed_milestone_issues / total_milestone_issues) * 100.0
            
            return {
                'projects': {
                    'total': total_projects,
                    'open': open_projects,
                    'closed': closed_projects
                },
                'milestones': {
                    'total': total_milestones,
                    'open': open_milestones,
                    'closed': closed_milestones,
                    'overall_progress': overall_progress
                },
                'issues': {
                    'total': total_milestone_issues,
                    'completed': completed_milestone_issues,
                    'remaining': total_milestone_issues - completed_milestone_issues
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project progress summary for {owner}/{repo}: {e}")
            raise
    
    def format_milestone_progress(self, milestone: Milestone) -> str:
        """
        Format milestone progress for display.
        
        Args:
            milestone: Milestone object
            
        Returns:
            Formatted progress string
        """
        progress = milestone.progress_percentage
        total_issues = milestone.open_issues + milestone.closed_issues
        
        status_emoji = "🎯" if milestone.state == MilestoneState.OPEN else "✅"
        progress_bar = self._create_progress_bar(progress)
        
        due_text = ""
        if milestone.due_on:
            due_text = f" (Due: {milestone.due_on.strftime('%Y-%m-%d')})"
        
        return f"{status_emoji} {milestone.title}: {progress_bar} {progress:.1f}% ({milestone.closed_issues}/{total_issues}){due_text}"
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text-based progress bar."""
        filled = int((percentage / 100.0) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"