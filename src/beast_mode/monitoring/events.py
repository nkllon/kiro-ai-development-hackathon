"""
Event system for Beast Mode monitoring

Defines event types and structures for the monitoring dashboard
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class EventSeverity(Enum):
    """Event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class Event:
    """Base event class for all monitoring events"""
    event_id: str
    event_type: str
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    severity: EventSeverity
    tags: List[str]
    correlation_id: Optional[str] = None


class TestResultEvent(Event):
    """Event for test execution results"""
    
    def __init__(self, event_id: str, timestamp: datetime, source: str, 
                 test_file: str, test_status: TestStatus, duration: float,
                 failure_details: Optional[str] = None, 
                 severity: EventSeverity = EventSeverity.INFO,
                 tags: List[str] = None, correlation_id: Optional[str] = None):
        data = {
            'test_file': test_file,
            'test_status': test_status.value,
            'duration': duration,
            'failure_details': failure_details
        }
        super().__init__(event_id, "test_result", timestamp, source, data, 
                        severity, tags or [], correlation_id)
        self.test_file = test_file
        self.test_status = test_status
        self.duration = duration
        self.failure_details = failure_details


class HubrisPreventionEvent(Event):
    """Event for hubris prevention system activations"""
    
    def __init__(self, event_id: str, timestamp: datetime, source: str,
                 actor_id: str, hubris_type: str, accountability_chain: List[str],
                 intervention_required: bool, mama_discovery_status: str,
                 severity: EventSeverity = EventSeverity.WARNING,
                 tags: List[str] = None, correlation_id: Optional[str] = None):
        data = {
            'actor_id': actor_id,
            'hubris_type': hubris_type,
            'accountability_chain': accountability_chain,
            'intervention_required': intervention_required,
            'mama_discovery_status': mama_discovery_status
        }
        super().__init__(event_id, "hubris_prevention", timestamp, source, data,
                        severity, tags or [], correlation_id)
        self.actor_id = actor_id
        self.hubris_type = hubris_type
        self.accountability_chain = accountability_chain
        self.intervention_required = intervention_required
        self.mama_discovery_status = mama_discovery_status


class SystemHealthEvent(Event):
    """Event for system health metrics"""
    
    def __init__(self, event_id: str, timestamp: datetime, source: str,
                 cpu_percent: float, memory_percent: float, disk_usage: float,
                 network_io: Dict[str, float],
                 severity: EventSeverity = EventSeverity.INFO,
                 tags: List[str] = None, correlation_id: Optional[str] = None):
        data = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_usage': disk_usage,
            'network_io': network_io
        }
        super().__init__(event_id, "system_health", timestamp, source, data,
                        severity, tags or [], correlation_id)
        self.cpu_percent = cpu_percent
        self.memory_percent = memory_percent
        self.disk_usage = disk_usage
        self.network_io = network_io


class FilesystemEvent(Event):
    """Event for filesystem changes"""
    
    def __init__(self, event_id: str, timestamp: datetime, source: str,
                 file_path: str, change_type: str, file_size: Optional[int] = None,
                 severity: EventSeverity = EventSeverity.INFO,
                 tags: List[str] = None, correlation_id: Optional[str] = None):
        data = {
            'file_path': file_path,
            'change_type': change_type,
            'file_size': file_size
        }
        super().__init__(event_id, "filesystem", timestamp, source, data,
                        severity, tags or [], correlation_id)
        self.file_path = file_path
        self.change_type = change_type
        self.file_size = file_size