"""
Doctor Status Indicator Component
Provides real-time "Doctor Is In/Out" status display for AI consultation availability.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class DoctorStatus:
    """Doctor availability status with cost and budget information."""
    is_available: bool
    reason: str
    cost_budget_remaining: float
    daily_usage: float
    monthly_usage: float
    last_updated: datetime
    session_count: int = 0
    queue_size: int = 0

class DoctorStatusIndicator:
    """
    Manages and displays the Doctor Is In/Out status indicator.
    Integrates with Observatory WebSocket system for real-time updates.
    """
    
    def __init__(self, feature_flags: Optional[Dict[str, Any]] = None):
        self.feature_flags = feature_flags or {}
        self.current_status = DoctorStatus(
            is_available=False,  # Default to "Doctor Is Out" for cost safety
            reason="System starting up",
            cost_budget_remaining=100.0,
            daily_usage=0.0,
            monthly_usage=0.0,
            last_updated=datetime.now(),
            session_count=0,
            queue_size=0
        )
        
    def is_enabled(self) -> bool:
        """Check if doctor status indicator is enabled via feature flags."""
        return self.feature_flags.get('doctor_status_enabled', True)
    
    def get_status(self) -> DoctorStatus:
        """Get current doctor status."""
        return self.current_status
    
    def set_status(self, is_available: bool, reason: str = "") -> DoctorStatus:
        """Update doctor status and return new status."""
        if not self.is_enabled():
            logger.info("Doctor status indicator is disabled via feature flags")
            return self.current_status
            
        self.current_status.is_available = is_available
        self.current_status.reason = reason or ("Available for real-time consultation" if is_available else "Queries will be queued for processing")
        self.current_status.last_updated = datetime.now()
        
        logger.info(f"Doctor status updated: {'IN' if is_available else 'OUT'} - {reason}")
        return self.current_status
    
    def update_usage(self, daily_usage: float, monthly_usage: float, budget_remaining: float) -> None:
        """Update cost and usage information."""
        self.current_status.daily_usage = daily_usage
        self.current_status.monthly_usage = monthly_usage
        self.current_status.cost_budget_remaining = budget_remaining
        self.current_status.last_updated = datetime.now()
        
        # Auto-transition to "Out" if budget is low
        if budget_remaining <= 0 and self.current_status.is_available:
            self.set_status(False, "Budget limit reached - queries queued for batch processing")
    
    def update_activity(self, session_count: int, queue_size: int) -> None:
        """Update activity counters."""
        self.current_status.session_count = session_count
        self.current_status.queue_size = queue_size
        self.current_status.last_updated = datetime.now()
    
    def get_status_for_ui(self) -> Dict[str, Any]:
        """Get status formatted for UI display."""
        if not self.is_enabled():
            return {
                "enabled": False,
                "message": "AI consultation feature is currently disabled"
            }
        
        status = self.current_status
        
        # Determine status color and icon
        if status.is_available:
            status_color = "#2ecc71"  # Green
            status_icon = "🟢"
            status_text = "Doctor Is In"
            action_text = "Start real-time consultation"
        else:
            status_color = "#e74c3c"  # Red
            status_icon = "🔴"
            status_text = "Doctor Is Out"
            action_text = "Submit query to queue"
        
        # Budget status indicator
        budget_status = "good"
        if status.cost_budget_remaining <= 10:
            budget_status = "critical"
        elif status.cost_budget_remaining <= 25:
            budget_status = "warning"
        
        return {
            "enabled": True,
            "is_available": status.is_available,
            "status_text": status_text,
            "status_icon": status_icon,
            "status_color": status_color,
            "reason": status.reason,
            "action_text": action_text,
            "last_updated": status.last_updated.isoformat(),
            "activity": {
                "session_count": status.session_count,
                "queue_size": status.queue_size
            },
            "budget": {
                "remaining": status.cost_budget_remaining,
                "daily_usage": status.daily_usage,
                "monthly_usage": status.monthly_usage,
                "status": budget_status
            }
        }
    
    def get_websocket_message(self) -> Dict[str, Any]:
        """Get status as WebSocket message for real-time updates."""
        return {
            "type": "doctor_status_update",
            "data": self.get_status_for_ui()
        }

# Global instance for the Observatory
_doctor_status_indicator = None

def get_doctor_status_indicator(feature_flags: Optional[Dict[str, Any]] = None) -> DoctorStatusIndicator:
    """Get or create the global doctor status indicator instance."""
    global _doctor_status_indicator
    if _doctor_status_indicator is None:
        _doctor_status_indicator = DoctorStatusIndicator(feature_flags)
    return _doctor_status_indicator