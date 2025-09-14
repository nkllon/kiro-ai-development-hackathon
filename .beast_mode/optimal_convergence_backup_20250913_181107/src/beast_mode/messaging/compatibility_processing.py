"""
Compatibility Processing

This module was extracted from compatibility.py
as part of RM-DDD compliance refactoring.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from .models import BeastModeMessage, MessageType, AgentCapabilities
import uuid
import uuid

def convert_message(message_data: Union[Dict[str, Any], str]) -> Optional[BeastModeMessage]:
    """
    Convert message data to BeastModeMessage with compatibility handling.
    
    Args:
        message_data: Raw message data
        
    Returns:
        BeastModeMessage or None if conversion fails
    """
    compatibility_layer = MessageCompatibilityLayer(CompatibilityMode.CONVERT)
    result = compatibility_layer.process_message(message_data)
    if result.success:
        return result.message
    else:
        logger.error(f'Message conversion failed: {result.errors}')
        return None

def convert_to_current(self, message_data: Union[Dict[str, Any], str]) -> ConversionResult:
    """
        Convert message to current format (V2.0).
        
        Args:
            message_data: Raw message data (dict or JSON string)
            
        Returns:
            ConversionResult: Conversion result with message or errors
        """
    result = ConversionResult(success=False, target_version=MessageVersion.V2_0)
    try:
        if isinstance(message_data, str):
            try:
                message_data = json.loads(message_data)
            except json.JSONDecodeError as e:
                result.errors.append(f'Invalid JSON: {e}')
                return result
        if not isinstance(message_data, dict):
            result.errors.append('Message data must be a dictionary')
            return result
        source_version = self.detector.detect_version(message_data)
        result.original_version = source_version
        if source_version == MessageVersion.UNKNOWN:
            result.warnings.append('Unknown message format, attempting best-effort conversion')
        converted_data = self._convert_from_version(message_data, source_version)
        try:
            message = BeastModeMessage(**converted_data)
            result.success = True
            result.message = message
            if source_version != MessageVersion.V2_0:
                result.warnings.append(f'Converted from {source_version.value} to {MessageVersion.V2_0.value}')
        except ValidationError as e:
            result.errors.append(f'Validation failed: {e}')
            try:
                lenient_data = self._apply_lenient_conversion(converted_data)
                message = BeastModeMessage(**lenient_data)
                result.success = True
                result.message = message
                result.warnings.append('Applied lenient conversion due to validation errors')
            except ValidationError as e2:
                result.errors.append(f'Lenient conversion also failed: {e2}')
    except Exception as e:
        result.errors.append(f'Conversion error: {e}')
        logger.error(f'Message conversion error: {e}')
    return result

def _convert_from_version(self, message_data: Dict[str, Any], source_version: MessageVersion) -> Dict[str, Any]:
    """Convert message from specific version to current format"""
    converted = message_data.copy()
    if source_version == MessageVersion.V1_0:
        converted = self._convert_from_v1_0(converted)
    elif source_version == MessageVersion.V1_1:
        converted = self._convert_from_v1_1(converted)
    elif source_version == MessageVersion.V1_2:
        converted = self._convert_from_v1_2(converted)
    elif source_version == MessageVersion.UNKNOWN:
        if 'from' in converted or 'content' in converted:
            converted = self._convert_from_v1_0(converted)
    if 'id' not in converted:
        import uuid
        converted['id'] = str(uuid.uuid4())
    if 'timestamp' not in converted:
        converted['timestamp'] = datetime.now()
    elif isinstance(converted['timestamp'], str):
        try:
            converted['timestamp'] = datetime.fromisoformat(converted['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            converted['timestamp'] = datetime.now()
    if 'priority' not in converted:
        converted['priority'] = 5
    if 'payload' not in converted:
        converted['payload'] = {}
    if 'type' in converted:
        try:
            MessageType(converted['type'])
        except ValueError:
            converted['type'] = self.translator.translate_to_current(converted['type']).value
    else:
        converted['type'] = MessageType.SIMPLE_MESSAGE.value
    if 'source' not in converted:
        converted['source'] = 'unknown_agent'
    return converted

def _convert_from_v1_0(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.0 format"""
    converted = message_data.copy()
    if 'from' in converted:
        converted['source'] = converted.pop('from')
    if 'to' in converted:
        converted['target'] = converted.pop('to')
    if 'payload' not in converted:
        standard_fields = {'type', 'source', 'target', 'timestamp', 'priority', 'id', 'correlation_id'}
        payload_data = {}
        fields_to_move = []
        for key, value in converted.items():
            if key not in standard_fields:
                payload_data[key] = value
                fields_to_move.append(key)
        for key in fields_to_move:
            converted.pop(key)
        converted['payload'] = payload_data
    return converted

def _convert_from_v1_1(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.1 format"""
    converted = message_data.copy()
    if 'request_id' in converted and 'correlation_id' not in converted:
        converted['correlation_id'] = converted.pop('request_id')
    return converted

def _convert_from_v1_2(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert from V1.2 format"""
    return message_data

def convert_to_legacy(self, message: BeastModeMessage, target_version: MessageVersion=MessageVersion.V1_0) -> Dict[str, Any]:
    """
        Convert current message to legacy format.
        
        Args:
            message: Current format message
            target_version: Target legacy version
            
        Returns:
            Dict[str, Any]: Legacy format message data
        """
    legacy_data = message.model_dump()
    legacy_data['type'] = self.translator.translate_to_legacy(message.type, target_version)
    if target_version == MessageVersion.V1_0:
        legacy_data.pop('correlation_id', None)
        legacy_data.pop('priority', None)
        legacy_data.pop('id', None)
        if 'target' in legacy_data:
            legacy_data['to'] = legacy_data.pop('target')
        if 'source' in legacy_data:
            legacy_data['from'] = legacy_data.pop('source')
    elif target_version == MessageVersion.V1_1:
        legacy_data.pop('id', None)
        if 'correlation_id' in legacy_data:
            legacy_data['request_id'] = legacy_data.pop('correlation_id')
    if 'timestamp' in legacy_data and isinstance(legacy_data['timestamp'], datetime):
        legacy_data['timestamp'] = legacy_data['timestamp'].isoformat()
    return legacy_data

def process_message(self, message_data: Union[Dict[str, Any], str, BeastModeMessage]) -> ConversionResult:
    """
        Process incoming message with compatibility handling.
        
        Args:
            message_data: Raw message data in any supported format
            
        Returns:
            ConversionResult: Processing result
        """
    self.stats['messages_processed'] += 1
    self.stats['last_activity'] = datetime.now()
    if isinstance(message_data, BeastModeMessage):
        result = ConversionResult(success=True, message=message_data)
        result.original_version = MessageVersion.V2_0
        result.target_version = MessageVersion.V2_0
        return result
    result = self.converter.convert_to_current(message_data)
    if self.strict_validation and (not result.success or result.original_version == MessageVersion.UNKNOWN):
        result.success = False
        if not result.errors:
            result.errors.append('Message format not supported in strict mode')
        self.stats['conversions_failed'] += 1
        return result
    if result.success:
        self.stats['conversions_successful'] += 1
        if result.original_version:
            version_key = result.original_version.value
            self.stats['version_distribution'][version_key] = self.stats['version_distribution'].get(version_key, 0) + 1
    else:
        self.stats['conversions_failed'] += 1
    if result.message:
        original_type_str = str(message_data.get('type', '')) if isinstance(message_data, dict) else ''
        if original_type_str and original_type_str in self.unknown_type_handlers:
            result.message.type = self.unknown_type_handlers[original_type_str]
            result.warnings.append(f'Mapped unknown type to {result.message.type.value}')
            self.stats['unknown_types_handled'] += 1
        elif self._is_unknown_type(result.message.type):
            handled_type = self._handle_unknown_type(result.message.type)
            if handled_type and handled_type != result.message.type:
                result.message.type = handled_type
                result.warnings.append(f'Mapped unknown type to {handled_type.value}')
                self.stats['unknown_types_handled'] += 1
    return result
