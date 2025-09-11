#!/usr/bin/env python3
"""
Deadline Calculator - Deadline calculations and status logic

Extracted from deadline_tracker.py for RM-DDD compliance.
Single responsibility: Deadline calculations and status determination.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from .deadline_models import DeadlineInfo, DeadlineStatus, DeadlineConfiguration, DeadlineStatistics
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
            'name': 'Deadline Calculator',
            'description': 'deadline_calculator module for DevPost integration',
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


class DeadlineCalculator(ReflectiveModule):
    """Calculates deadline status and time remaining"""
    
    def __init__(self, config: Optional[DeadlineConfiguration] = None):
        super().__init__(module_id="deadline_calculator", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """Initialize deadline calculator"""
        self.config = config or DeadlineConfiguration()
        self.stats = DeadlineStatistics()
    
    def calculate_deadline_status(self, deadline_date: datetime, 
                                current_time: Optional[datetime] = None) -> DeadlineStatus:
        """Calculate deadline status based on time remaining"""
        try:
            if current_time is None:
                current_time = datetime.now()
            
            time_diff = deadline_date - current_time
            
            if time_diff.total_seconds() <= 0:
                return DeadlineStatus.OVERDUE
            elif time_diff.total_seconds() <= self.config.critical_threshold_hours * 3600:
                return DeadlineStatus.SOON
            elif time_diff.total_seconds() <= self.config.warning_threshold_hours * 3600:
                return DeadlineStatus.SOON
            else:
                return DeadlineStatus.UPCOMING
                
        except Exception as e:
            logger.error(f"Error calculating deadline status: {e}")
            return DeadlineStatus.UPCOMING
    
    def calculate_time_remaining(self, deadline_date: datetime, 
                               current_time: Optional[datetime] = None) -> str:
        """Calculate human-readable time remaining"""
        try:
            if current_time is None:
                current_time = datetime.now()
            
            time_diff = deadline_date - current_time
            total_seconds = int(time_diff.total_seconds())
            
            if total_seconds <= 0:
                return "Overdue"
            
            # Calculate components
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            # Format based on time remaining
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
                
        except Exception as e:
            logger.error(f"Error calculating time remaining: {e}")
            return "Unknown"
    
    def get_deadline_info(self, hackathon_id: str, hackathon_name: str,
                         submission_deadline: datetime,
                         judging_deadline: Optional[datetime] = None,
                         requirements: List[Dict[str, Any]] = None,
                         is_registered: bool = False,
                         submission_status: str = "not_started") -> DeadlineInfo:
        """Get comprehensive deadline information"""
        try:
            if requirements is None:
                requirements = []
            
            # Calculate status for submission deadline
            submission_status_enum = self.calculate_deadline_status(submission_deadline)
            time_remaining = self.calculate_time_remaining(submission_deadline)
            
            # Determine overall status
            overall_status = submission_status_enum
            
            # If judging deadline exists and is sooner, use that
            if judging_deadline and judging_deadline < submission_deadline:
                judging_status = self.calculate_deadline_status(judging_deadline)
                if judging_status == DeadlineStatus.OVERDUE:
                    overall_status = DeadlineStatus.OVERDUE
                elif judging_status == DeadlineStatus.SOON:
                    overall_status = DeadlineStatus.SOON
                time_remaining = self.calculate_time_remaining(judging_deadline)
            
            return DeadlineInfo(
                hackathon_id=hackathon_id,
                hackathon_name=hackathon_name,
                deadline_date=submission_deadline,
                submission_deadline=submission_deadline,
                judging_deadline=judging_deadline,
                status=overall_status,
                time_remaining=time_remaining,
                requirements=requirements,
                is_registered=is_registered,
                submission_status=submission_status
            )
            
        except Exception as e:
            logger.error(f"Error getting deadline info: {e}")
            return DeadlineInfo(
                hackathon_id=hackathon_id,
                hackathon_name=hackathon_name,
                deadline_date=submission_deadline,
                submission_deadline=submission_deadline,
                judging_deadline=judging_deadline,
                status=DeadlineStatus.UPCOMING,
                time_remaining="Unknown",
                requirements=requirements or [],
                is_registered=is_registered,
                submission_status=submission_status
            )
    
    def get_upcoming_deadlines(self, deadlines: List[DeadlineInfo], 
                              limit: int = 10) -> List[DeadlineInfo]:
        """Get upcoming deadlines sorted by date"""
        try:
            upcoming = [d for d in deadlines if d.is_upcoming]
            upcoming.sort(key=lambda x: x.deadline_date)
            return upcoming[:limit]
            
        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {e}")
            return []
    
    def get_urgent_deadlines(self, deadlines: List[DeadlineInfo]) -> List[DeadlineInfo]:
        """Get urgent deadlines (soon or overdue)"""
        try:
            urgent = [d for d in deadlines if d.is_soon or d.is_overdue]
            urgent.sort(key=lambda x: x.deadline_date)
            return urgent
            
        except Exception as e:
            logger.error(f"Error getting urgent deadlines: {e}")
            return []
    
    def get_overdue_deadlines(self, deadlines: List[DeadlineInfo]) -> List[DeadlineInfo]:
        """Get overdue deadlines"""
        try:
            overdue = [d for d in deadlines if d.is_overdue]
            overdue.sort(key=lambda x: x.deadline_date, reverse=True)
            return overdue
            
        except Exception as e:
            logger.error(f"Error getting overdue deadlines: {e}")
            return []
    
    def calculate_deadline_priority(self, deadline: DeadlineInfo) -> int:
        """Calculate priority score for deadline (lower = higher priority)"""
        try:
            priority = 1000  # Base priority
            
            # Reduce priority based on status
            if deadline.is_overdue:
                priority -= 500
            elif deadline.is_soon:
                priority -= 300
            elif deadline.is_upcoming:
                priority -= 100
            
            # Reduce priority based on time remaining
            time_diff = deadline.deadline_date - datetime.now()
            hours_remaining = time_diff.total_seconds() / 3600
            
            if hours_remaining <= 1:
                priority -= 200
            elif hours_remaining <= 6:
                priority -= 150
            elif hours_remaining <= 24:
                priority -= 100
            elif hours_remaining <= 72:
                priority -= 50
            
            # Reduce priority if not registered
            if not deadline.is_registered:
                priority -= 50
            
            # Reduce priority if submission not started
            if deadline.submission_status == "not_started":
                priority -= 25
            
            return max(0, priority)
            
        except Exception as e:
            logger.error(f"Error calculating deadline priority: {e}")
            return 1000
    
    def get_deadline_summary(self, deadlines: List[DeadlineInfo]) -> Dict[str, Any]:
        """Get summary of all deadlines"""
        try:
            # Update statistics
            self.stats.update_counts(deadlines)
            
            # Calculate additional metrics
            total_deadlines = len(deadlines)
            upcoming_count = len([d for d in deadlines if d.is_upcoming])
            soon_count = len([d for d in deadlines if d.is_soon])
            overdue_count = len([d for d in deadlines if d.is_overdue])
            completed_count = len([d for d in deadlines if d.is_completed])
            
            # Get urgent deadlines
            urgent_deadlines = self.get_urgent_deadlines(deadlines)
            
            # Calculate average time remaining
            active_deadlines = [d for d in deadlines if not d.is_completed and not d.is_overdue]
            avg_time_remaining = 0
            if active_deadlines:
                total_hours = sum(
                    (d.deadline_date - datetime.now()).total_seconds() / 3600 
                    for d in active_deadlines
                )
                avg_time_remaining = total_hours / len(active_deadlines)
            
            return {
                'total_deadlines': total_deadlines,
                'upcoming_deadlines': upcoming_count,
                'soon_deadlines': soon_count,
                'overdue_deadlines': overdue_count,
                'completed_deadlines': completed_count,
                'urgent_deadlines': len(urgent_deadlines),
                'average_time_remaining_hours': round(avg_time_remaining, 2),
                'next_deadline': min(deadlines, key=lambda x: x.deadline_date).to_dict() if deadlines else None,
                'statistics': self.stats.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting deadline summary: {e}")
            return {
                'total_deadlines': 0,
                'error': str(e)
            }
    
    def should_send_alert(self, deadline: DeadlineInfo, 
                         last_alert_time: Optional[datetime] = None) -> bool:
        """Determine if alert should be sent for deadline"""
        try:
            if not self.config.enable_notifications:
                return False
            
            # Don't alert for completed deadlines
            if deadline.is_completed:
                return False
            
            # Always alert for overdue deadlines
            if deadline.is_overdue:
                return True
            
            # Check if deadline is soon
            if deadline.is_soon:
                # Check if we've already sent an alert recently
                if last_alert_time:
                    time_since_alert = datetime.now() - last_alert_time
                    if time_since_alert.total_seconds() < 3600:  # 1 hour
                        return False
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking alert condition: {e}")
            return False
    
    def get_alert_message(self, deadline: DeadlineInfo) -> str:
        """Generate alert message for deadline"""
        try:
            if deadline.is_overdue:
                return f"🚨 OVERDUE: {deadline.hackathon_name} deadline has passed!"
            elif deadline.is_soon:
                return f"⚠️ URGENT: {deadline.hackathon_name} deadline in {deadline.time_remaining}"
            else:
                return f"📅 REMINDER: {deadline.hackathon_name} deadline in {deadline.time_remaining}"
                
        except Exception as e:
            logger.error(f"Error generating alert message: {e}")
            return f"Deadline alert for {deadline.hackathon_name}"
    
    def is_healthy(self) -> bool:
        """Check if deadline calculator is healthy"""
        try:
            # Test basic calculation
            test_deadline = datetime.now() + timedelta(hours=1)
            status = self.calculate_deadline_status(test_deadline)
            time_remaining = self.calculate_time_remaining(test_deadline)
            
            return status is not None and time_remaining is not None
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators"""
        try:
            return {
                'calculator_healthy': self.is_healthy(),
                'config': self.config.to_dict(),
                'statistics': self.stats.to_dict(),
                'warning_threshold_hours': self.config.warning_threshold_hours,
                'critical_threshold_hours': self.config.critical_threshold_hours
            }
        except Exception as e:
            return {
                'calculator_healthy': False,
                'error': str(e)
            }
