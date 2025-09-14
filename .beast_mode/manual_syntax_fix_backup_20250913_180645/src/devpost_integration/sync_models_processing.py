"""
Sync Models Processing

This module was extracted from sync_models.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from .enum_models import SyncOperationType, ChangeType
from typing import Dict, List, Any, Optional

def add_processed_record(self) -> None:
    """Increment processed records count."""
    try:
        self.records_processed += 1
        self._operation_count += 1
    except Exception as e:
        logger.error(f'Failed to add processed record: {e}')
        self._errors += 1
