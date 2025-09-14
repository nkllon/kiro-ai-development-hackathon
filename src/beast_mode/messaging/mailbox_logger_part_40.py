from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _initialize_log_file(self) -> None:
    """Initialize the current log file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    self.current_log_file = self.log_directory / f'mailbox_{timestamp}.log'
    try:
        self.current_log_handle = open(self.current_log_file, 'a', encoding='utf-8')
        logger.info(f'Initialized log file: {self.current_log_file}')
    except Exception as e:
        logger.error(f'Failed to initialize log file: {e}')
        raise
