"""
Bot Defense Base Classes
Abstract base classes and interfaces for defense systems.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

from .models import Attack, DefenseAction, DefenseActionType, BotProfile
from .config import get_config

logger = logging.getLogger(__name__)

class DefenseSystemStatus(Enum):
    """Defense system operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    OVERLOADED = "overloaded"

@dataclass
class DefenseResult:
    """Result of a defense action."""
    
    success: bool
    action: DefenseAction
    response_data: Optional[bytes] = None
    response_headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'action': self.action.to_dict(),
            'response_size': len(self.response_data) if self.response_data else 0,
            'response_headers': self.response_headers or {},
            'error_message': self.error_message
        }

class DefenseSystem(ABC):
    """Abstract base class for all defense systems."""
    
    def __init__(self, name: str):
        self.name = name
        self.status = DefenseSystemStatus.INACTIVE
        self.config = get_config()
        self.active_defenses = 0
        self.total_defenses = 0
        self.total_bytes_generated = 0
        self.last_error: Optional[str] = None
        self.last_error_time: Optional[float] = None
        
    @abstractmethod
    async def execute_defense(self, attack: Attack, intensity: int = 1) -> DefenseResult:
        """Execute defense action against an attack."""
        pass
    
    @abstractmethod
    def get_max_intensity(self) -> int:
        """Get maximum intensity level for this defense system."""
        pass
    
    @abstractmethod
    def estimate_resource_usage(self, intensity: int) -> Dict[str, float]:
        """Estimate resource usage for given intensity."""
        pass
    
    def is_available(self) -> bool:
        """Check if defense system is available for use."""
        if self.status != DefenseSystemStatus.ACTIVE:
            return False
        
        max_concurrent = self.config.defense_systems.max_concurrent_defenses
        if self.active_defenses >= max_concurrent:
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of defense system."""
        return {
            'name': self.name,
            'status': self.status.value,
            'active_defenses': self.active_defenses,
            'total_defenses': self.total_defenses,
            'total_bytes_generated': self.total_bytes_generated,
            'bytes_generated_mb': round(self.total_bytes_generated / 1024 / 1024, 2),
            'is_available': self.is_available(),
            'max_intensity': self.get_max_intensity(),
            'last_error': self.last_error,
            'last_error_time': self.last_error_time
        }
    
    async def start(self) -> None:
        """Start the defense system."""
        logger.info(f"Starting defense system: {self.name}")
        self.status = DefenseSystemStatus.ACTIVE
    
    async def stop(self) -> None:
        """Stop the defense system."""
        logger.info(f"Stopping defense system: {self.name}")
        self.status = DefenseSystemStatus.INACTIVE
        
        # Wait for active defenses to complete
        while self.active_defenses > 0:
            await asyncio.sleep(0.1)

class ResourceMonitor:
    """Monitor system resources during defense operations."""
    
    def __init__(self):
        self.cpu_usage_history: List[float] = []
        self.memory_usage_history: List[float] = []
        self.active_connections = 0
        self.max_connections = 1000
    
    def record_cpu_usage(self, usage_percent: float):
        """Record CPU usage sample."""
        self.cpu_usage_history.append(usage_percent)
        if len(self.cpu_usage_history) > 100:
            self.cpu_usage_history.pop(0)
    
    def record_memory_usage(self, usage_percent: float):
        """Record memory usage sample."""
        self.memory_usage_history.append(usage_percent)
        if len(self.memory_usage_history) > 100:
            self.memory_usage_history.pop(0)
    
    def get_average_cpu_usage(self) -> float:
        """Get average CPU usage."""
        if not self.cpu_usage_history:
            return 0.0
        return sum(self.cpu_usage_history) / len(self.cpu_usage_history)
    
    def get_average_memory_usage(self) -> float:
        """Get average memory usage."""
        if not self.memory_usage_history:
            return 0.0
        return sum(self.memory_usage_history) / len(self.memory_usage_history)
    
    def is_overloaded(self) -> bool:
        """Check if system is overloaded."""
        avg_cpu = self.get_average_cpu_usage()
        avg_memory = self.get_average_memory_usage()
        
        return (avg_cpu > 80.0 or 
                avg_memory > 80.0 or 
                self.active_connections > self.max_connections * 0.9)
    
    def get_status(self) -> Dict[str, Any]:
        """Get resource monitor status."""
        return {
            'average_cpu_usage': self.get_average_cpu_usage(),
            'average_memory_usage': self.get_average_memory_usage(),
            'active_connections': self.active_connections,
            'max_connections': self.max_connections,
            'is_overloaded': self.is_overloaded()
        }

# Global resource monitor
_resource_monitor = ResourceMonitor()

def get_resource_monitor() -> ResourceMonitor:
    """Get the global resource monitor."""
    return _resource_monitor