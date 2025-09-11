#!/usr/bin/env python3
"""
Devpost Deadline Tracking System

Monitors hackathon deadlines and provides notifications for submission requirements.
Implements systematic deadline management with proactive notifications.

Requirements: 4.1, 4.2, 4.3
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from .models import (
    Deadline, ProjectSummary, NotificationSettings, ValidationRules,
    DevpostConfig, ProjectConnection
)
from .api_client import DevpostAPIClient
from .notification_manager import NotificationManager


class DeadlineStatus(Enum):
    """Deadline status enumeration."""
    UPCOMING = "upcoming"
    SOON = "soon"  # Within warning threshold
    OVERDUE = "overdue"
    COMPLETED = "completed"


@dataclass
class DeadlineInfo:
    """Extended deadline information with status and requirements."""
    hackathon_id: str
    hackathon_name: str
    deadline_date: datetime
    submission_deadline: datetime
    judging_deadline: Optional[datetime]
    status: DeadlineStatus
    time_remaining: str
    requirements: List[Dict[str, Any]]
    is_registered: bool
    submission_status: str
    
    @property
    def is_overdue(self) -> bool:
        """Check if deadline is overdue."""
        return self.status == DeadlineStatus.OVERDUE
    
    @property
    def is_soon(self) -> bool:
        """Check if deadline is approaching soon."""
        return self.status == DeadlineStatus.SOON
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining until deadline."""
        if self.deadline_date <= datetime.now():
            return 0
        return (self.deadline_date - datetime.now()).days


class DeadlineTracker:
    """
    Tracks hackathon deadlines and manages notifications.
    
    Provides systematic deadline monitoring with:
    - Automatic deadline retrieval from Devpost API
    - Configurable notification thresholds
    - Submission requirement tracking
    - Multi-project deadline management
    """
    
    def __init__(
        self,
        config_file: Optional[Path] = None,
        api_client: Optional[DevpostAPIClient] = None,
        notification_manager: Optional[NotificationManager] = None
    ):
        """
        Initialize deadline tracker.
        
        Args:
            config_file: Path to configuration file
            api_client: Devpost API client instance
            notification_manager: Notification manager instance
        """
        self.config_file = config_file or Path.cwd() / '.devpost' / 'config.json'
        self.api_client = api_client or DevpostAPIClient()
        self.notification_manager = notification_manager or NotificationManager()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Cache for deadline data
        self._deadline_cache: Dict[str, DeadlineInfo] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = 3600  # 1 hour
    
    def _load_config(self) -> DevpostConfig:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                config_data = json.loads(self.config_file.read_text())
                return DevpostConfig(**config_data)
            else:
                # Create default configuration
                default_config = DevpostConfig()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return DevpostConfig()
    
    def _save_config(self, config: DevpostConfig) -> None:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(asdict(config), indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def get_current_project_deadlines(self) -> List[DeadlineInfo]:
        """
        Get deadlines for the current project.
        
        Returns:
            List of deadline information for current project
        """
        try:
            # Get current project connection
            current_project = self._get_current_project()
            if not current_project:
                return []
            
            # Get hackathon deadlines for the project
            hackathon_ids = self._get_project_hackathons(current_project.project_id)
            
            deadlines = []
            for hackathon_id in hackathon_ids:
                deadline_info = self._get_hackathon_deadline(hackathon_id)
                if deadline_info:
                    deadlines.append(deadline_info)
            
            # Sort by deadline date
            deadlines.sort(key=lambda d: d.deadline_date)
            
            return deadlines
            
        except Exception as e:
            self.logger.error(f"Failed to get current project deadlines: {e}")
            return []
    
    def get_all_deadlines(self) -> List[DeadlineInfo]:
        """
        Get all hackathon deadlines across all projects.
        
        Returns:
            List of all deadline information
        """
        try:
            all_deadlines = []
            
            # Get deadlines for all connected projects
            for connection in self.config.project_connections:
                hackathon_ids = self._get_project_hackathons(connection.project_id)
                
                for hackathon_id in hackathon_ids:
                    deadline_info = self._get_hackathon_deadline(hackathon_id)
                    if deadline_info:
                        all_deadlines.append(deadline_info)
            
            # Remove duplicates and sort
            unique_deadlines = {d.hackathon_id: d for d in all_deadlines}
            sorted_deadlines = sorted(unique_deadlines.values(), key=lambda d: d.deadline_date)
            
            return sorted_deadlines
            
        except Exception as e:
            self.logger.error(f"Failed to get all deadlines: {e}")
            return []
    
    def check_upcoming_deadlines(self) -> List[DeadlineInfo]:
        """
        Check for upcoming deadlines that need notifications.
        
        Returns:
            List of deadlines requiring notifications
        """
        try:
            current_deadlines = self.get_current_project_deadlines()
            notification_settings = self.config.notification_settings
            
            upcoming_deadlines = []
            
            for deadline in current_deadlines:
                # Check if deadline is within notification threshold
                hours_until_deadline = (deadline.deadline_date - datetime.now()).total_seconds() / 3600
                
                if (0 < hours_until_deadline <= notification_settings.deadline_warning_hours and
                    deadline.status in [DeadlineStatus.UPCOMING, DeadlineStatus.SOON]):
                    upcoming_deadlines.append(deadline)
            
            return upcoming_deadlines
            
        except Exception as e:
            self.logger.error(f"Failed to check upcoming deadlines: {e}")
            return []
    
    def send_deadline_notifications(self) -> int:
        """
        Send notifications for upcoming deadlines.
        
        Returns:
            Number of notifications sent
        """
        try:
            upcoming_deadlines = self.check_upcoming_deadlines()
            
            if not upcoming_deadlines:
                return 0
            
            notifications_sent = 0
            
            for deadline in upcoming_deadlines:
                # Create notification message
                message = self._create_deadline_notification_message(deadline)
                
                # Send notification
                success = self.notification_manager.send_deadline_notification(
                    hackathon_name=deadline.hackathon_name,
                    deadline_date=deadline.deadline_date,
                    time_remaining=deadline.time_remaining,
                    requirements=deadline.requirements,
                    message=message
                )
                
                if success:
                    notifications_sent += 1
                    self.logger.info(f"Sent deadline notification for {deadline.hackathon_name}")
            
            return notifications_sent
            
        except Exception as e:
            self.logger.error(f"Failed to send deadline notifications: {e}")
            return 0
    
    def update_deadline_cache(self) -> None:
        """Update the deadline cache with fresh data."""
        try:
            self.logger.info("Updating deadline cache...")
            
            # Clear existing cache
            self._deadline_cache.clear()
            
            # Get all hackathon IDs from connected projects
            hackathon_ids = set()
            for connection in self.config.project_connections:
                project_hackathons = self._get_project_hackathons(connection.project_id)
                hackathon_ids.update(project_hackathons)
            
            # Fetch deadline information for each hackathon
            for hackathon_id in hackathon_ids:
                deadline_info = self._fetch_hackathon_deadline(hackathon_id)
                if deadline_info:
                    self._deadline_cache[hackathon_id] = deadline_info
            
            self._cache_timestamp = datetime.now()
            self.logger.info(f"Updated deadline cache with {len(self._deadline_cache)} hackathons")
            
        except Exception as e:
            self.logger.error(f"Failed to update deadline cache: {e}")
    
    def _get_current_project(self) -> Optional[ProjectConnection]:
        """Get the current project connection."""
        if not self.config.project_connections:
            return None
        
        # Return the first project or the one marked as current
        for connection in self.config.project_connections:
            if hasattr(connection, 'is_current') and connection.is_current:
                return connection
        
        # Default to first project
        return self.config.project_connections[0]
    
    def _get_project_hackathons(self, project_id: str) -> List[str]:
        """Get hackathon IDs associated with a project."""
        try:
            # Use API to get project details and extract hackathon information
            project_details = self.api_client.get_project_details(project_id)
            
            hackathon_ids = []
            if project_details and 'hackathons' in project_details:
                hackathon_ids = [h['id'] for h in project_details['hackathons']]
            
            return hackathon_ids
            
        except Exception as e:
            self.logger.error(f"Failed to get project hackathons for {project_id}: {e}")
            return []
    
    def _get_hackathon_deadline(self, hackathon_id: str) -> Optional[DeadlineInfo]:
        """Get deadline information for a hackathon."""
        # Check cache first
        if (self._deadline_cache and hackathon_id in self._deadline_cache and
            self._cache_timestamp and 
            (datetime.now() - self._cache_timestamp).seconds < self._cache_ttl):
            return self._deadline_cache[hackathon_id]
        
        # Fetch fresh data
        return self._fetch_hackathon_deadline(hackathon_id)
    
    def _fetch_hackathon_deadline(self, hackathon_id: str) -> Optional[DeadlineInfo]:
        """Fetch deadline information from API."""
        try:
            # Get hackathon details from API
            hackathon_data = self.api_client.get_hackathon_deadlines(hackathon_id)
            
            if not hackathon_data:
                return None
            
            # Parse deadline information
            deadline_date = datetime.fromisoformat(hackathon_data['submission_deadline'])
            submission_deadline = deadline_date
            judging_deadline = None
            
            if 'judging_deadline' in hackathon_data:
                judging_deadline = datetime.fromisoformat(hackathon_data['judging_deadline'])
            
            # Determine status
            now = datetime.now()
            status = DeadlineStatus.UPCOMING
            
            if deadline_date <= now:
                status = DeadlineStatus.OVERDUE
            elif (deadline_date - now).total_seconds() <= (24 * 3600):  # Within 24 hours
                status = DeadlineStatus.SOON
            
            # Calculate time remaining
            time_remaining = self._format_time_remaining(deadline_date)
            
            # Get submission requirements
            requirements = self._get_submission_requirements(hackathon_id)
            
            # Check registration and submission status
            is_registered = hackathon_data.get('is_registered', False)
            submission_status = hackathon_data.get('submission_status', 'not_submitted')
            
            return DeadlineInfo(
                hackathon_id=hackathon_id,
                hackathon_name=hackathon_data['name'],
                deadline_date=deadline_date,
                submission_deadline=submission_deadline,
                judging_deadline=judging_deadline,
                status=status,
                time_remaining=time_remaining,
                requirements=requirements,
                is_registered=is_registered,
                submission_status=submission_status
            )
            
        except Exception as e:
            self.logger.error(f"Failed to fetch hackathon deadline for {hackathon_id}: {e}")
            return None
    
    def _get_submission_requirements(self, hackathon_id: str) -> List[Dict[str, Any]]:
        """Get submission requirements for a hackathon."""
        try:
            requirements_data = self.api_client.get_submission_requirements(hackathon_id)
            
            if not requirements_data:
                return []
            
            requirements = []
            for req in requirements_data.get('requirements', []):
                requirements.append({
                    'id': req.get('id'),
                    'description': req.get('description'),
                    'is_required': req.get('is_required', True),
                    'is_met': req.get('is_met', False),
                    'type': req.get('type', 'text')
                })
            
            return requirements
            
        except Exception as e:
            self.logger.error(f"Failed to get submission requirements for {hackathon_id}: {e}")
            return []
    
    def _format_time_remaining(self, deadline_date: datetime) -> str:
        """Format time remaining until deadline."""
        now = datetime.now()
        
        if deadline_date <= now:
            return "Overdue"
        
        time_diff = deadline_date - now
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} days, {hours} hours"
        elif hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    def _create_deadline_notification_message(self, deadline: DeadlineInfo) -> str:
        """Create notification message for deadline."""
        message = f"⏰ Deadline Alert: {deadline.hackathon_name}\n"
        message += f"📅 Deadline: {deadline.deadline_date.strftime('%Y-%m-%d %H:%M')}\n"
        message += f"⏳ Time remaining: {deadline.time_remaining}\n"
        
        if deadline.requirements:
            unmet_requirements = [r for r in deadline.requirements if not r.get('is_met', False)]
            if unmet_requirements:
                message += f"\n📋 Outstanding requirements ({len(unmet_requirements)}):\n"
                for req in unmet_requirements[:3]:  # Show first 3
                    message += f"  • {req['description']}\n"
                
                if len(unmet_requirements) > 3:
                    message += f"  ... and {len(unmet_requirements) - 3} more\n"
        
        message += "\n💡 Run 'devpost validate' to check your submission status"
        
        return message