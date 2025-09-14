"""
Models Models

This module was extracted from models.py
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

class DataModelMixin:
    """Base mixin providing validation and serialization for all data models"""

    def validate(self) -> bool:
        """Validate the data model instance"""
        try:
            if hasattr(self.__class__, '__dataclass_fields__'):
                for field_name, field_info in self.__class__.__dataclass_fields__.items():
                    field_value = getattr(self, field_name)
                    is_required = field_info.default is MISSING and field_info.default_factory is MISSING
                    if is_required:
                        if field_value is None:
                            logging.warning(f'Required field {field_name} is None in {self.__class__.__name__}')
                            return False
                        if isinstance(field_value, str) and len(field_value) == 0:
                            logging.warning(f'Required field {field_name} is empty string in {self.__class__.__name__}')
                            return False
            return True
        except Exception as e:
            logging.error(f'Validation error in {self.__class__.__name__}: {e}')
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        try:
            result = {}
            for key, value in asdict(self).items():
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                elif isinstance(value, set):
                    result[key] = list(value)
                elif isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
            return result
        except Exception as e:
            logging.error(f'Serialization error in {self.__class__.__name__}: {e}')
            return {}

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create instance from dictionary"""
        try:
            for key, value in data.items():
                if isinstance(value, str) and 'T' in value and (':' in value):
                    try:
                        data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass
            return cls(**data)
        except Exception as e:
            logging.error(f'Deserialization error in {cls.__name__}: {e}')
            raise
