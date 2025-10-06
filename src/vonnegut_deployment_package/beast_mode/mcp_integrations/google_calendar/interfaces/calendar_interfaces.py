"""Calendar operations interface definitions.

This module contains interfaces related to calendar functionality,
focusing solely on Google Calendar API operation contracts.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class CalendarOperationsInterface(ABC):
    """Interface for calendar operations.
    
    Defines the contract for Google Calendar API operations
    including event management and availability checking.
    """
    
    @abstractmethod
    def get_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get calendar events in the specified time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of calendar events
        """
        pass
    
    @abstractmethod
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Created event data
        """
        pass
    
    @abstractmethod
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event.
        
        Args:
            event_id: ID of event to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated event data
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event.
        
        Args:
            event_id: ID of event to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        pass