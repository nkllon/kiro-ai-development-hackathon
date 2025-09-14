"""
Models Core Validation

This module was extracted from models_core.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from dataclasses import dataclass, field, asdict, MISSING
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import hashlib
import re
from src.rm_ddd.core.health import ModuleHealth


def validate_content(self, content: str) -> Tuple[bool, str]:
    """Validate content against this rule"""
    try:
        if self.rule_type == 'terminology':
            forbidden_patterns = self.rule_expression.split('|')
            for pattern in forbidden_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return (False, self.error_message)
        return (True, '')
    except Exception as e:
        return (False, f'Validation error: {e}')
