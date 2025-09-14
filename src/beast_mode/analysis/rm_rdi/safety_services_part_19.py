from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def shutdown_safety_systems(self) -> None:
        """Shutdown all safety systems"""
        self.logger.info('Shutting down safety systems...')
        self.resource_monitor.stop_monitoring()
        self.logger.info('Safety systems shutdown complete')
