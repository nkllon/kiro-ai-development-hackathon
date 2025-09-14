from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


    def __init__(self, hackathon_deadline: datetime=None):
        """Initialize deadline manager."""
        self.hackathon_deadline = hackathon_deadline or datetime(2025, 9, 15, 23, 59, 59)
        self.tasks: List[HackathonTask] = []
        self.critical_path: Optional[CriticalPath] = None
        self.emergency_protocols_active = False
        self._load_default_tasks()
        logger.info(f'Hackathon deadline manager initialized for {self.hackathon_deadline}')
