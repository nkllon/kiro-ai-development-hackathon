from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def initialize_safety_systems(self) -> bool:
        """Initialize all safety systems"""
        try:
            self.logger.info('Initializing operator safety systems...')
            self.resource_monitor.start_monitoring()
            if not self._validate_initial_safety():
                self.logger.error('Initial safety validation failed')
                return False
            self.logger.info('Safety systems initialized successfully')
            return True
        except Exception as e:
            self.logger.error(f'Failed to initialize safety systems: {e}')
            return False
