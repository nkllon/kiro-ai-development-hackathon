"""
Client Validation

This module was extracted from client.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
import random
import aiohttp
from aiohttp import ClientTimeout, ClientError, ClientResponseError
from ..interfaces import DevpostAPIClientInterface
from ..models import DevpostProject, AuthResult
from ..auth.auth_service import DevpostAuthService
from ....core.exceptions import NetworkError, AuthenticationError, ValidationError

def _validate_media_file(self, file_path: Path) -> Dict[str, Any]:
    """
        Validate media file and extract metadata.
        
        Args:
            file_path: Path to media file
            
        Returns:
            Dictionary with validation result and metadata
        """
    if not file_path.exists():
        return {'valid': False, 'error': 'File does not exist'}
    if not self._is_valid_media_file(file_path):
        return {'valid': False, 'error': f'Unsupported file type: {file_path.suffix}'}
    file_size = file_path.stat().st_size
    if file_size > self.MAX_REQUEST_SIZE:
        return {'valid': False, 'error': f'File too large: {file_size} bytes (max: {self.MAX_REQUEST_SIZE})'}
    if file_size == 0:
        return {'valid': False, 'error': 'File is empty'}
    metadata = {'valid': True, 'filename': file_path.name, 'size': file_size, 'content_type': self._get_content_type(file_path), 'extension': file_path.suffix.lower(), 'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()}
    if metadata['extension'] in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}:
        metadata['media_type'] = 'image'
    elif metadata['extension'] in {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}:
        metadata['media_type'] = 'video'
    else:
        metadata['media_type'] = 'document'
    return metadata

def _check_rate_limit(self) -> bool:
    """
        Check if request is within rate limits.
        
        Returns:
            True if request is allowed, False if rate limited
        """
    now = time.time()
    cutoff = now - self.RATE_LIMIT_WINDOW
    self._request_timestamps = [ts for ts in self._request_timestamps if ts > cutoff]
    self._burst_timestamps = [ts for ts in self._burst_timestamps if ts > now - 10]
    if len(self._burst_timestamps) >= self.BURST_LIMIT:
        logger.warning('Burst rate limit exceeded')
        return False
    if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_WINDOW:
        logger.warning('Rate limit exceeded')
        return False
    self._request_timestamps.append(now)
    self._burst_timestamps.append(now)
    return True

def _validate_project_updates(self, updates: Dict[str, Any]) -> None:
    """Validate project update data."""
    allowed_fields = {'title', 'tagline', 'description', 'tags', 'links', 'team_members', 'submission_status'}
    for field in updates.keys():
        if field not in allowed_fields:
            raise ValidationError(f'Invalid update field: {field}')
    if 'title' in updates and (not updates['title'].strip()):
        raise ValidationError('Title cannot be empty')
    if 'tagline' in updates and len(updates['tagline']) > 120:
        raise ValidationError('Tagline must be 120 characters or less')
    if 'description' in updates and len(updates['description']) > 5000:
        raise ValidationError('Description must be 5000 characters or less')
    if 'tags' in updates and len(updates['tags']) > 10:
        raise ValidationError('Maximum 10 tags allowed')

def _validate_project_data(self, project_data: Dict[str, Any]) -> None:
    """Validate project creation data."""
    required_fields = {'title', 'description'}
    for field in required_fields:
        if field not in project_data:
            raise ValidationError(f'Required field missing: {field}')
        if not project_data[field].strip():
            raise ValidationError(f'Required field cannot be empty: {field}')
    self._validate_project_updates(project_data)
