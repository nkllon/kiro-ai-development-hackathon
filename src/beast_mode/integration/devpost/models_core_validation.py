"""
Models Core Validation

This module was extracted from models_core.py
as part of RM-DDD compliance refactoring.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, HttpUrl
import re
import json
import fnmatch
import fnmatch
import fnmatch

@field_validator('tagline')
@classmethod
def tagline_length_check(cls, v):
    if len(v) > 120:
        raise ValueError('Tagline must be 120 characters or less')
    return v

@field_validator('description')
@classmethod
def description_length_check(cls, v):
    if len(v) > 5000:
        raise ValueError('Description must be 5000 characters or less')
    return v

@field_validator('tags')
@classmethod
def validate_tags(cls, v):
    if len(v) > 10:
        raise ValueError('Maximum 10 tags allowed')
    for tag in v:
        if len(tag) > 50:
            raise ValueError('Each tag must be 50 characters or less')
        if not re.match('^[a-zA-Z0-9\\-_\\s]+$', tag):
            raise ValueError('Tags can only contain letters, numbers, hyphens, underscores, and spaces')
    return v

@model_validator(mode='after')
def validate_deadline(self):
    if self.deadline and self.deadline <= datetime.now():
        raise ValueError('Deadline must be in the future')
    return self

@field_validator('priority')
@classmethod
def validate_priority(cls, v):
    if not 1 <= v <= 10:
        raise ValueError('Priority must be between 1 and 10')
    return v

@field_validator('max_retries')
@classmethod
def validate_max_retries(cls, v):
    if v < 0:
        raise ValueError('Max retries cannot be negative')
    return v

@model_validator(mode='after')
def validate_retry_count(self):
    if self.retry_count > self.max_retries:
        raise ValueError('Retry count cannot exceed max retries')
    return self

@field_validator('file_size')
@classmethod
def validate_file_size(cls, v):
    if v is not None and v < 0:
        raise ValueError('File size cannot be negative')
    return v

@model_validator(mode='after')
def validate_deleted_file(self):
    if self.change_type == ChangeType.DELETED and self.file_size is not None:
        raise ValueError('Deleted files should not have file size')
    return self

@field_validator('watch_patterns')
@classmethod
def validate_watch_patterns(cls, v):
    if not v:
        raise ValueError('At least one watch pattern is required')
    for pattern in v:
        if not pattern.strip():
            raise ValueError('Watch patterns cannot be empty')
    return v

def validate_configuration(self) -> List[str]:
    """Validate configuration completeness."""
    issues = []
    if not self.project_id:
        issues.append('project_id is required')
    if not self.hackathon_id:
        issues.append('hackathon_id is required')
    if self.sync_enabled and (not self.watch_patterns):
        issues.append('watch_patterns required when sync is enabled')
    return issues
