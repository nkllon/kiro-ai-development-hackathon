#!/usr/bin/env python3
"""
Deadline Tracker - Main deadline tracking orchestration

Refactored from deadline_tracker.py for RM-DDD compliance.
Single responsibility: Deadline tracking orchestration and coordination.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import (
    Deadline, ProjectSummary, NotificationSettings, ValidationRules,
    DevpostConfig, ProjectConnection
)
from .api_client import DevPostAPIClient
from .notification_manager import NotificationManager
from .deadline_models import (
    DeadlineInfo, DeadlineConfiguration, DeadlineStatistics, DeadlineRequirement
)
from .deadline_calculator import DeadlineCalculator
from .deadline_notifications import DeadlineNotificationManager
from .reflective_module import (
    ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, 
    ModuleConfiguration, register_module
)
from datetime import datetime


logger = logging.getLogger(__name__)

    # ReflectiveModule interface implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get comprehensive module information."""
        return {
            'module_id': self.module_id,
            'version': self.version,
            'name': 'Deadline Tracker Refactored',
            'description': 'deadline_tracker_refactored module for DevPost integration',
            'author': 'DevPost Integration Team',
            'created_at': self._start_time.isoformat(),
            'interface_version': self.get_interface_version()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return []
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return []
    
    def check_health(self) -> ModuleHealth:
        """Perform comprehensive health check."""
        issues = []
        health_score = 1.0
        
        try:
            # Basic health checks
            if not hasattr(self, 'module_id'):
                issues.append("Missing module_id")
                health_score -= 0.2
            
            # Add module-specific health checks here
            
            
            # Determine status
            if health_score >= 0.9:
                status = ModuleStatus.HEALTHY
            elif health_score >= 0.7:
                status = ModuleStatus.DEGRADED
            else:
                status = ModuleStatus.UNHEALTHY
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                last_check=datetime.now(),
                health_score=max(0.0, health_score),
                issues=issues,
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics=self.get_metrics()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.UNHEALTHY,
                last_check=datetime.now(),
                health_score=0.0,
                issues=[f"Health check exception: {e}"],
                capabilities=self.get_capabilities(),
                dependencies=self.get_dependencies(),
                metrics={}
            )
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration."""
        return ModuleConfiguration(
            module_id=self.module_id,
            config_version="1.0.0",
            parameters={},
            required_parameters=[],
            optional_parameters=[],
            validation_rules={},
            last_updated=datetime.now()
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration."""
        try:
            if not config.is_valid():
                logger.error("Invalid configuration provided")
                return False
            
            logger.info(f"Configuration updated for {self.module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'last_check': datetime.now().isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics to initial state."""
        self._start_time = datetime.now()
        logger.info("Metrics reset for {self.module_id} module")


class DevpostDeadlineTracker(ReflectiveModule):
    """
    Devpost Deadline Tracking System
    
    Monitors hackathon deadlines and provides notifications for submission requirements.
    Implements systematic deadline management with proactive notifications.
    """
    
    def __init__(self, config: Optional[DevpostConfig] = None, 
        super().__init__(module_id="deadline_tracker_refactored", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

                 api_client: Optional[DevPostAPIClient] = None,
                 notification_manager: Optional[NotificationManager] = None):
        """Initialize deadline tracker"""
        self.config = config or DevpostConfig()
        self.api_client = api_client or DevPostAPIClient()
        self.notification_manager = notification_manager or NotificationManager()
        
        # Deadline configuration
        self.deadline_config = DeadlineConfiguration()
        
        # Initialize components
        self.calculator = DeadlineCalculator(self.deadline_config)
        self.notification_mgr = DeadlineNotificationManager(
            self.deadline_config, 
            self.notification_manager
        )
        
        # Storage
        self.storage_path = Path("deadline_tracker_data.json")
        self.deadlines: List[DeadlineInfo] = []
        
        # Statistics
        self.stats = DeadlineStatistics()
        
        # Load existing data
        self._load_data()
    
    def add_deadline(self, hackathon_id: str, hackathon_name: str,
                    submission_deadline: datetime,
                    judging_deadline: Optional[datetime] = None,
                    requirements: List[Dict[str, Any]] = None,
                    is_registered: bool = False,
                    submission_status: str = "not_started") -> bool:
        """Add a new deadline to track"""
        try:
            # Create deadline info
            deadline_info = self.calculator.get_deadline_info(
                hackathon_id=hackathon_id,
                hackathon_name=hackathon_name,
                submission_deadline=submission_deadline,
                judging_deadline=judging_deadline,
                requirements=requirements or [],
                is_registered=is_registered,
                submission_status=submission_status
            )
            
            # Add to deadlines list
            self.deadlines.append(deadline_info)
            
            # Save data
            self._save_data()
            
            logger.info(f"Added deadline: {hackathon_name} ({hackathon_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding deadline: {e}")
            return False
    
    def update_deadline(self, hackathon_id: str, **kwargs) -> bool:
        """Update an existing deadline"""
        try:
            # Find deadline
            deadline = next((d for d in self.deadlines if d.hackathon_id == hackathon_id), None)
            if not deadline:
                logger.warning(f"Deadline not found: {hackathon_id}")
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(deadline, key):
                    setattr(deadline, key, value)
            
            # Recalculate status
            updated_deadline = self.calculator.get_deadline_info(
                hackathon_id=deadline.hackathon_id,
                hackathon_name=deadline.hackathon_name,
                submission_deadline=deadline.submission_deadline,
                judging_deadline=deadline.judging_deadline,
                requirements=deadline.requirements,
                is_registered=deadline.is_registered,
                submission_status=deadline.submission_status
            )
            
            # Replace in list
            index = self.deadlines.index(deadline)
            self.deadlines[index] = updated_deadline
            
            # Save data
            self._save_data()
            
            logger.info(f"Updated deadline: {hackathon_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating deadline: {e}")
            return False
    
    def remove_deadline(self, hackathon_id: str) -> bool:
        """Remove a deadline from tracking"""
        try:
            # Find and remove deadline
            original_count = len(self.deadlines)
            self.deadlines = [d for d in self.deadlines if d.hackathon_id != hackathon_id]
            
            if len(self.deadlines) < original_count:
                # Save data
                self._save_data()
                logger.info(f"Removed deadline: {hackathon_id}")
                return True
            else:
                logger.warning(f"Deadline not found: {hackathon_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing deadline: {e}")
            return False
    
    def get_deadline(self, hackathon_id: str) -> Optional[DeadlineInfo]:
        """Get a specific deadline"""
        try:
            return next((d for d in self.deadlines if d.hackathon_id == hackathon_id), None)
        except Exception as e:
            logger.error(f"Error getting deadline: {e}")
            return None
    
    def get_all_deadlines(self) -> List[DeadlineInfo]:
        """Get all deadlines"""
        return self.deadlines.copy()
    
    def get_upcoming_deadlines(self, limit: int = 10) -> List[DeadlineInfo]:
        """Get upcoming deadlines"""
        return self.calculator.get_upcoming_deadlines(self.deadlines, limit)
    
    def get_urgent_deadlines(self) -> List[DeadlineInfo]:
        """Get urgent deadlines"""
        return self.calculator.get_urgent_deadlines(self.deadlines)
    
    def get_overdue_deadlines(self) -> List[DeadlineInfo]:
        """Get overdue deadlines"""
        return self.calculator.get_overdue_deadlines(self.deadlines)
    
    def check_deadlines(self) -> Dict[str, Any]:
        """Check all deadlines and send notifications"""
        try:
            # Update all deadline statuses
            for i, deadline in enumerate(self.deadlines):
                updated_deadline = self.calculator.get_deadline_info(
                    hackathon_id=deadline.hackathon_id,
                    hackathon_name=deadline.hackathon_name,
                    submission_deadline=deadline.submission_deadline,
                    judging_deadline=deadline.judging_deadline,
                    requirements=deadline.requirements,
                    is_registered=deadline.is_registered,
                    submission_status=deadline.submission_status
                )
                self.deadlines[i] = updated_deadline
            
            # Process alerts
            alerts_sent = self.notification_mgr.process_deadline_alerts(self.deadlines)
            
            # Update statistics
            self.stats.update_counts(self.deadlines)
            
            # Save data
            self._save_data()
            
            # Get summary
            summary = self.calculator.get_deadline_summary(self.deadlines)
            summary['alerts_sent'] = alerts_sent
            
            logger.info(f"Checked deadlines: {alerts_sent} alerts sent")
            return summary
            
        except Exception as e:
            logger.error(f"Error checking deadlines: {e}")
            return {'error': str(e)}
    
    def get_deadline_summary(self) -> Dict[str, Any]:
        """Get comprehensive deadline summary"""
        try:
            summary = self.calculator.get_deadline_summary(self.deadlines)
            summary['notification_stats'] = self.notification_mgr.get_notification_stats()
            summary['tracker_stats'] = self.stats.to_dict()
            return summary
            
        except Exception as e:
            logger.error(f"Error getting deadline summary: {e}")
            return {'error': str(e)}
    
    def export_deadlines(self, export_path: str) -> bool:
        """Export deadlines to file"""
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'deadlines': [deadline.to_dict() for deadline in self.deadlines],
                'statistics': self.stats.to_dict(),
                'config': self.deadline_config.to_dict()
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported deadlines to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting deadlines: {e}")
            return False
    
    def import_deadlines(self, import_path: str) -> bool:
        """Import deadlines from file"""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            # Import deadlines
            if 'deadlines' in data:
                self.deadlines = [DeadlineInfo.from_dict(d) for d in data['deadlines']]
            
            # Import statistics
            if 'statistics' in data:
                self.stats = DeadlineStatistics.from_dict(data['statistics'])
            
            # Import config
            if 'config' in data:
                self.deadline_config = DeadlineConfiguration.from_dict(data['config'])
            
            # Save data
            self._save_data()
            
            logger.info(f"Imported deadlines from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing deadlines: {e}")
            return False
    
    def update_configuration(self, new_config: DeadlineConfiguration) -> None:
        """Update deadline configuration"""
        try:
            self.deadline_config = new_config
            self.calculator.config = new_config
            self.notification_mgr.config = new_config
            self._save_data()
            logger.info("Updated deadline configuration")
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
    
    def _load_data(self) -> None:
        """Load deadline data from storage"""
        try:
            if not self.storage_path.exists():
                return
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load deadlines
            if 'deadlines' in data:
                self.deadlines = [DeadlineInfo.from_dict(d) for d in data['deadlines']]
            
            # Load statistics
            if 'statistics' in data:
                self.stats = DeadlineStatistics.from_dict(data['statistics'])
            
            # Load config
            if 'config' in data:
                self.deadline_config = DeadlineConfiguration.from_dict(data['config'])
            
            logger.info(f"Loaded {len(self.deadlines)} deadlines from storage")
            
        except Exception as e:
            logger.error(f"Error loading deadline data: {e}")
    
    def _save_data(self) -> None:
        """Save deadline data to storage"""
        try:
            data = {
                'deadlines': [deadline.to_dict() for deadline in self.deadlines],
                'statistics': self.stats.to_dict(),
                'config': self.deadline_config.to_dict(),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving deadline data: {e}")
    
    def is_healthy(self) -> bool:
        """Check if deadline tracker is healthy"""
        try:
            # Check all components
            if not self.calculator.is_healthy():
                return False
            
            if not self.notification_mgr.is_healthy():
                return False
            
            if not self.api_client.is_healthy():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'tracker_healthy': self.is_healthy(),
                'calculator_healthy': self.calculator.is_healthy(),
                'notification_manager_healthy': self.notification_mgr.is_healthy(),
                'api_client_healthy': self.api_client.is_healthy(),
                'deadlines_count': len(self.deadlines),
                'statistics': self.stats.to_dict(),
                'config': self.deadline_config.to_dict(),
                'storage_accessible': self.storage_path.parent.exists()
            }
        except Exception as e:
            return {
                'tracker_healthy': False,
                'error': str(e)
            }
