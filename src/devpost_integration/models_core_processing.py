"""
Models Core Processing

This module was extracted from models_core.py
as part of RM-DDD compliance refactoring.
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional
from enum import Enum
from typing import Dict, Any, List, Optional
from pathlib import Path
from .reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability, ModuleConfiguration, register_module
import uuid
import uuid
import uuid
import uuid
import uuid
import os
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import os
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import uuid
import os
import uuid
import uuid
import uuid
import uuid
import uuid

def mark_processed(self) -> bool:
    """Mark event as processed"""
    try:
        self._update_metrics('mark_processed')
        self.event_data['processed'] = True
        self.updated_at = datetime.now()
        self._metrics['events_processed'] += 1
        self._logger.info(f'Event {self.event_id} marked as processed')
        return True
    except Exception as e:
        self._logger.error(f'Failed to mark as processed: {e}')
        self._metrics['error_count'] += 1
        return False

def is_processed(self) -> bool:
    """Check if event is processed"""
    try:
        self._update_metrics('is_processed')
        return self.event_data.get('processed', False)
    except Exception as e:
        self._logger.error(f'Failed to check processed status: {e}')
        self._metrics['error_count'] += 1
        return False

@classmethod
def get_processing_requirements(cls, media_type: str) -> List[str]:
    """Get processing requirements for media type"""
    requirements_map = {cls.IMAGE.value: ['resize', 'optimize', 'thumbnail_generation'], cls.VIDEO.value: ['transcode', 'thumbnail_generation', 'metadata_extraction'], cls.AUDIO.value: ['transcode', 'metadata_extraction', 'waveform_generation'], cls.DOCUMENT.value: ['text_extraction', 'metadata_extraction'], cls.CODE.value: ['syntax_highlighting', 'linting', 'formatting'], cls.DATA.value: ['validation', 'parsing', 'analysis'], cls.PRESENTATION.value: ['slide_extraction', 'thumbnail_generation'], cls.SPREADSHEET.value: ['data_extraction', 'validation'], cls.TEXT.value: ['encoding_detection', 'line_ending_normalization'], cls.ARCHIVE.value: ['extraction', 'validation', 'virus_scanning'], cls.UNKNOWN.value: ['basic_validation']}
    return requirements_map.get(media_type, [])
