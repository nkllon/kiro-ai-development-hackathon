"""
Spore Manager Models

This module was extracted from spore_manager.py
as part of RM-DDD compliance refactoring.
"""

import json
import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError
import yaml
from .models import BeastModeMessage, MessageType

class SporeMetadata(BaseModel):
    """Metadata for a Beast Mode spore"""
    name: str
    version: str
    author: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    capabilities_required: List[str] = Field(default_factory=list)
    compatibility_version: str = '1.0'
    checksum: str = ''
    file_path: str = ''
    validation_criteria: Dict[str, Any] = Field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 0.0
