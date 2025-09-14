"""
Spore Manager Services Validation

This module was extracted from spore_manager_services.py
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
from src.rm_ddd.core.health import ModuleHealth


def _calculate_checksum(self, content: str) -> str:
    """Calculate SHA-256 checksum of content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def validate_spore(self, spore_content: str) -> bool:
    """
        Validate spore content for basic syntax and structure
        
        Args:
            spore_content: The spore implementation content
            
        Returns:
            bool: True if valid, False otherwise
        """
    try:
        compile(spore_content, '<spore>', 'exec')
        required_elements = ['def execute(', 'class']
        has_required = any((element in spore_content for element in required_elements))
        if not has_required:
            logger.warning('Spore missing required structure (execute function or class)')
            return False
        dangerous_patterns = ['import os', 'import subprocess', 'exec(', 'eval(', '__import__', 'open(']
        for pattern in dangerous_patterns:
            if pattern in spore_content:
                logger.warning(f'Spore contains potentially dangerous pattern: {pattern}')
        return True
    except SyntaxError as e:
        logger.error(f'Spore syntax error: {e}')
        return False
    except Exception as e:
        logger.error(f'Spore validation error: {e}')
        return False
