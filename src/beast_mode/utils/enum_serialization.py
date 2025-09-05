"""
Enum JSON Serialization Utilities

Provides custom JSON encoding for enum types to handle serialization issues
in health reporting and other system components.

Requirements: 6.1, 6.4 - Fix enum serialization and JSON compatibility
"""

import json
from enum import Enum
from typing import Any, Type, Dict, Union


class EnumJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles enum serialization."""
    
    def default(self, obj: Any) -> Any:
        """Convert enum objects to their values for JSON serialization."""
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class SerializationHandler:
    """Utility class for handling enum serialization in various contexts."""
    
    @staticmethod
    def serialize_with_enums(data: Any, **kwargs) -> str:
        """
        Serialize data containing enums to JSON string.
        
        Args:
            data: The data to serialize (can contain enums)
            **kwargs: Additional arguments passed to json.dumps
            
        Returns:
            JSON string with enums properly serialized
        """
        # Set default kwargs if not provided
        if 'cls' not in kwargs:
            kwargs['cls'] = EnumJSONEncoder
        if 'indent' not in kwargs:
            kwargs['indent'] = 2
            
        return json.dumps(data, **kwargs)
    
    @staticmethod
    def ensure_enum_serializable(enum_class: Type[Enum]) -> None:
        """
        Ensure enum class is properly serializable by adding __json__ method.
        
        Args:
            enum_class: The enum class to make serializable
        """
        if not hasattr(enum_class, '__json__'):
            def __json__(self):
                return self.value
            enum_class.__json__ = __json__
    
    @staticmethod
    def convert_enums_to_values(data: Any) -> Any:
        """
        Recursively convert enum objects to their values in data structures.
        
        Args:
            data: Data structure that may contain enums
            
        Returns:
            Data structure with enums converted to values
        """
        if isinstance(data, Enum):
            return data.value
        elif isinstance(data, dict):
            return {key: SerializationHandler.convert_enums_to_values(value) 
                   for key, value in data.items()}
        elif isinstance(data, (list, tuple)):
            return type(data)(SerializationHandler.convert_enums_to_values(item) 
                            for item in data)
        else:
            return data
    
    @staticmethod
    def safe_serialize(data: Any, **kwargs) -> str:
        """
        Safely serialize data with fallback handling for problematic objects.
        
        Args:
            data: The data to serialize
            **kwargs: Additional arguments passed to json.dumps
            
        Returns:
            JSON string with safe serialization
        """
        try:
            return SerializationHandler.serialize_with_enums(data, **kwargs)
        except (TypeError, ValueError) as e:
            # Fallback: convert enums to values first
            try:
                converted_data = SerializationHandler.convert_enums_to_values(data)
                # Remove cls from kwargs to avoid conflicts
                fallback_kwargs = {k: v for k, v in kwargs.items() if k != 'cls'}
                return json.dumps(converted_data, **fallback_kwargs)
            except Exception as fallback_error:
                # Last resort: use default str conversion
                final_kwargs = {k: v for k, v in kwargs.items() if k != 'cls'}
                final_kwargs['default'] = str
                return json.dumps(data, **final_kwargs)


def make_enum_json_serializable(*enum_classes: Type[Enum]) -> None:
    """
    Convenience function to make multiple enum classes JSON serializable.
    
    Args:
        *enum_classes: Enum classes to make serializable
    """
    for enum_class in enum_classes:
        SerializationHandler.ensure_enum_serializable(enum_class)


# Convenience functions for common use cases
def dumps_with_enums(data: Any, **kwargs) -> str:
    """Shorthand for SerializationHandler.serialize_with_enums"""
    return SerializationHandler.serialize_with_enums(data, **kwargs)


def safe_dumps(data: Any, **kwargs) -> str:
    """Shorthand for SerializationHandler.safe_serialize"""
    return SerializationHandler.safe_serialize(data, **kwargs)