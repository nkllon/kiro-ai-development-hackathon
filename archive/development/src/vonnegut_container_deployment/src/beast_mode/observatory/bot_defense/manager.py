"""
Bot Defense Manager
Central coordinator for all bot defense systems and operations.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .config import get_config, DefenseMode
from .database import get_database, initialize_database
from .models import DefenseMetrics, BotProfile
from .base import DefenseSystem, DefenseSystemStatus, get_resource_monitor

logger = logging.getLogger(__name__)

class BotDefenseManager:
    """Central manager for bot defense operations."""
    
    def __init__(self):
        self.config = get_config()
        self.database = get_database()
        self.resource_monitor = get_resource_monitor()
        
        # Defense systems registry
        self.defense_systems: Dict[str, DefenseSystem] = {}
        
        # Operational state
        self.is_running = False
        self.metrics = DefenseMetrics()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> None:
        """Initialize the bot defense manager."""
        logger.info("Initializing Bot Defense Manager...")
        
        # Initialize database
        await initialize_database()
        
        # Initialize defense systems (will be implemented in later tasks)
        await self._initialize_defense_systems()
        
        # Start background tasks
        await self._start_background_tasks()
        
        self.is_running = True
        logger.info("Bot Defense Manager initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown the bot defense manager."""
        logger.info("Shutting down Bot Defense Manager...")
        
        self.is_running = False
        
        # Stop background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._metrics_task:
            self._metrics_task.cancel()
        
        # Stop all defense systems
        for system in self.defense_systems.values():
            await system.stop()
        
        logger.info("Bot Defense Manager shutdown complete")
    
    async def _initialize_defense_systems(self) -> None:
        """Initialize all defense systems."""
        # Defense systems will be implemented in later tasks
        # For now, just log that we're ready for them
        logger.info("Defense systems registry ready")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._metrics_task = asyncio.create_task(self._metrics_loop())
    
    async def _cleanup_loop(self) -> None:
        """Background task for database cleanup."""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.database.cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _metrics_loop(self) -> None:
        """Background task for metrics collection."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.websocket_update_interval)
                await self._update_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics task error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _update_metrics(self) -> None:
        """Update defense metrics."""
        # Get active defense systems
        active_systems = []
        for name, system in self.defense_systems.items():
            if system.status == DefenseSystemStatus.ACTIVE:
                active_systems.append(name)
        
        self.metrics.active_defense_systems = active_systems
        self.metrics.last_updated = datetime.now()
        
        # Update resource usage
        if self.resource_monitor.cpu_usage_history:
            self.metrics.system_load_percent = self.resource_monitor.get_average_cpu_usage()
    
    def register_defense_system(self, name: str, system: DefenseSystem) -> None:
        """Register a defense system."""
        self.defense_systems[name] = system
        logger.info(f"Registered defense system: {name}")
    
    def get_defense_system(self, name: str) -> Optional[DefenseSystem]:
        """Get a defense system by name."""
        return self.defense_systems.get(name)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive bot defense status."""
        return {
            'enabled': self.config.enabled,
            'running': self.is_running,
            'mode': self.config.defense_systems.mode.value,
            'metrics': self.metrics.to_dict(),
            'defense_systems': {
                name: system.get_status() 
                for name, system in self.defense_systems.items()
            },
            'resource_monitor': self.resource_monitor.get_status(),
            'database_stats': {
                'total_bots_tracked': 0,
                'active_bots': 0,
                'blocked_bots': 0,
                'terminated_bots': 0
            }
        }
    
    async def get_live_attacks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent attacks for live feed."""
        # For now, return empty list since we haven't implemented attack detection yet
        return []
    
    async def get_hall_of_shame(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get hall of shame leaderboard."""
        # For now, return empty list since we haven't implemented bot tracking yet
        return []
    
    def is_enabled(self) -> bool:
        """Check if bot defense is enabled."""
        return self.config.enabled and self.is_running
    
    def get_mode(self) -> DefenseMode:
        """Get current defense mode."""
        return self.config.defense_systems.mode
    
    async def set_mode(self, mode: DefenseMode) -> None:
        """Set defense mode."""
        self.config.defense_systems.mode = mode
        logger.info(f"Defense mode changed to: {mode.value}")
        
        # Notify all defense systems of mode change
        for system in self.defense_systems.values():
            if hasattr(system, 'on_mode_change'):
                await system.on_mode_change(mode)

# Global manager instance
_manager: Optional[BotDefenseManager] = None

def get_bot_defense_manager() -> BotDefenseManager:
    """Get the global bot defense manager."""
    global _manager
    if _manager is None:
        _manager = BotDefenseManager()
    return _manager

async def initialize_bot_defense() -> BotDefenseManager:
    """Initialize the global bot defense system."""
    manager = get_bot_defense_manager()
    await manager.initialize()
    return manager

async def shutdown_bot_defense() -> None:
    """Shutdown the global bot defense system."""
    global _manager
    if _manager:
        await _manager.shutdown()
        _manager = None