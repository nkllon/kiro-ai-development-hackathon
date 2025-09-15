"""
Compatibility Core Core

This module was extracted from compatibility_core.py
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
import uuid
import uuid
import uuid


class MessageVersion(str, Enum):
    """Supported message format versions"""

    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"
    V2_0 = "2.0"
    UNKNOWN = "unknown"


class CompatibilityMode(str, Enum):
    """Compatibility handling modes"""

    STRICT = "strict"
    CONVERT = "convert"
    PASSTHROUGH = "passthrough"


class MessageCompatibilityError(Exception):
    """Raised when message compatibility issues occur"""

    pass


class MessageConversionError(Exception):
    """Raised when message conversion fails"""

    pass


@dataclass
class ConversionResult:
    """Result of message conversion attempt"""

    success: bool
    message: Optional[BeastModeMessage] = None
    original_version: Optional[MessageVersion] = None
    target_version: Optional[MessageVersion] = None
    warnings: List[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


class LegacyMessageType(str, Enum):
    """Legacy message type mappings"""

    MESSAGE = "message"
    REQUEST = "request"
    RESPONSE = "response"
    DISCOVERY = "discovery"
    HELP = "help"
    SPORE = "spore"
    TEXT_MESSAGE = "text_message"
    AGENT_ANNOUNCE = "agent_announce"
    CAPABILITY_REQUEST = "capability_request"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


class MessageTypeTranslator:
    """Translates message types between different versions"""

    def __init__(self):
        self.legacy_mappings = {
            LegacyMessageType.MESSAGE: MessageType.SIMPLE_MESSAGE,
            LegacyMessageType.REQUEST: MessageType.PROMPT_REQUEST,
            LegacyMessageType.RESPONSE: MessageType.PROMPT_RESPONSE,
            LegacyMessageType.DISCOVERY: MessageType.AGENT_DISCOVERY,
            LegacyMessageType.HELP: MessageType.HELP_WANTED,
            LegacyMessageType.SPORE: MessageType.SPORE_DELIVERY,
            LegacyMessageType.TEXT_MESSAGE: MessageType.SIMPLE_MESSAGE,
            LegacyMessageType.AGENT_ANNOUNCE: MessageType.AGENT_DISCOVERY,
            LegacyMessageType.CAPABILITY_REQUEST: MessageType.HELP_WANTED,
            "msg": MessageType.SIMPLE_MESSAGE,
            "text": MessageType.SIMPLE_MESSAGE,
            "chat": MessageType.SIMPLE_MESSAGE,
            "prompt": MessageType.PROMPT_REQUEST,
            "query": MessageType.PROMPT_REQUEST,
            "answer": MessageType.PROMPT_RESPONSE,
            "reply": MessageType.PROMPT_RESPONSE,
            "announce": MessageType.AGENT_DISCOVERY,
            "broadcast": MessageType.AGENT_DISCOVERY,
            "ping": MessageType.SYSTEM_HEALTH,
            "health": MessageType.SYSTEM_HEALTH,
            "status": MessageType.SYSTEM_HEALTH,
        }
        self.current_to_legacy = {
            MessageType.SIMPLE_MESSAGE: LegacyMessageType.MESSAGE,
            MessageType.PROMPT_REQUEST: LegacyMessageType.REQUEST,
            MessageType.PROMPT_RESPONSE: LegacyMessageType.RESPONSE,
            MessageType.AGENT_DISCOVERY: LegacyMessageType.DISCOVERY,
            MessageType.HELP_WANTED: LegacyMessageType.HELP,
            MessageType.SPORE_DELIVERY: LegacyMessageType.SPORE,
        }

    def translate_to_current(
        self, legacy_type: Union[str, LegacyMessageType]
    ) -> MessageType:
        """
        Translate legacy message type to current format.

        Args:
            legacy_type: Legacy message type

        Returns:
            MessageType: Current message type

        Raises:
            MessageConversionError: If translation fails
        """
        if isinstance(legacy_type, str):
            try:
                return MessageType(legacy_type)
            except ValueError:
                pass
            legacy_type_lower = legacy_type.lower()
            if legacy_type_lower in self.legacy_mappings:
                return self.legacy_mappings[legacy_type_lower]
            try:
                legacy_enum = LegacyMessageType(legacy_type_lower)
                if legacy_enum in self.legacy_mappings:
                    return self.legacy_mappings[legacy_enum]
            except ValueError:
                pass
        elif isinstance(legacy_type, LegacyMessageType):
            if legacy_type in self.legacy_mappings:
                return self.legacy_mappings[legacy_type]
        logger.warning(
            f"Unknown message type '{legacy_type}', defaulting to SIMPLE_MESSAGE"
        )
        return MessageType.SIMPLE_MESSAGE

    def translate_to_legacy(
        self,
        current_type: MessageType,
        target_version: MessageVersion = MessageVersion.V1_0,
    ) -> str:
        """
        Translate current message type to legacy format.

        Args:
            current_type: Current message type
            target_version: Target legacy version

        Returns:
            str: Legacy message type string
        """
        if current_type in self.current_to_legacy:
            return self.current_to_legacy[current_type].value
        fallback_mappings = {
            MessageType.SPORE_REQUEST: LegacyMessageType.REQUEST.value,
            MessageType.SPORE_SPAWN: LegacyMessageType.SPORE.value,
            MessageType.TECHNICAL_EXCHANGE: LegacyMessageType.MESSAGE.value,
            MessageType.SYSTEM_HEALTH: LegacyMessageType.MESSAGE.value,
            MessageType.OFFICE_HOURS_ANNOUNCEMENT: LegacyMessageType.MESSAGE.value,
            MessageType.COLLABORATION_REQUEST: LegacyMessageType.REQUEST.value,
            MessageType.COLLABORATION_RESPONSE: LegacyMessageType.RESPONSE.value,
            MessageType.COLLABORATION_START: LegacyMessageType.MESSAGE.value,
            MessageType.COLLABORATION_END: LegacyMessageType.MESSAGE.value,
            MessageType.COLLABORATION_UPDATE: LegacyMessageType.MESSAGE.value,
        }
        return fallback_mappings.get(current_type, LegacyMessageType.MESSAGE.value)


class MessageVersionDetector:
    """Detects message format version from message structure"""

    def __init__(self):
        self.version_signatures = {
            MessageVersion.V1_0: {
                "required_fields": {"type", "source"},
                "optional_fields": {"target", "payload", "timestamp"},
                "forbidden_fields": {"correlation_id", "priority", "id"},
                "type_format": "string",
            },
            MessageVersion.V1_1: {
                "required_fields": {"type", "source"},
                "optional_fields": {
                    "target",
                    "payload",
                    "timestamp",
                    "correlation_id",
                    "priority",
                },
                "forbidden_fields": {"id"},
                "type_format": "string",
            },
            MessageVersion.V1_2: {
                "required_fields": {"type", "source"},
                "optional_fields": {
                    "target",
                    "payload",
                    "timestamp",
                    "correlation_id",
                    "priority",
                    "id",
                },
                "forbidden_fields": set(),
                "type_format": "string",
                "collaboration_types": True,
            },
            MessageVersion.V2_0: {
                "required_fields": {"type", "source", "id"},
                "optional_fields": {
                    "target",
                    "payload",
                    "timestamp",
                    "correlation_id",
                    "priority",
                },
                "forbidden_fields": set(),
                "type_format": "enum",
                "full_validation": True,
            },
        }

    def detect_version(self, message_data: Dict[str, Any]) -> MessageVersion:
        """
        Detect message format version from message structure.

        Args:
            message_data: Raw message data

        Returns:
            MessageVersion: Detected version
        """
        if not isinstance(message_data, dict):
            return MessageVersion.UNKNOWN
        message_fields = set(message_data.keys())
        if (
            "id" in message_fields
            and "type" in message_fields
            and ("source" in message_fields)
        ):
            msg_id = message_data.get("id")
            if msg_id and isinstance(msg_id, str) and (len(msg_id) == 36):
                try:
                    import uuid

                    uuid.UUID(msg_id)
                    return MessageVersion.V2_0
                except ValueError:
                    pass
        if "type" in message_fields and "source" in message_fields:
            msg_type = message_data.get("type", "")
            if (
                "collaboration" in msg_type.lower()
                or "office_hours" in msg_type.lower()
            ):
                return MessageVersion.V1_2
        if "source" in message_fields and "type" in message_fields:
            if (
                "correlation_id" in message_fields
                or "priority" in message_fields
                or "request_id" in message_fields
            ):
                return MessageVersion.V1_1
        if "from" in message_fields and "type" in message_fields:
            return MessageVersion.V1_0
        for version, signature in self.version_signatures.items():
            required_fields = signature["required_fields"]
            forbidden_fields = signature["forbidden_fields"]
            if not required_fields.issubset(message_fields):
                continue
            if forbidden_fields.intersection(message_fields):
                continue
            return version
        return MessageVersion.UNKNOWN

    def is_compatible_version(
        self,
        version: MessageVersion,
        target_version: MessageVersion = MessageVersion.V2_0,
    ) -> bool:
        """
        Check if a version is compatible with target version.

        Args:
            version: Source version
            target_version: Target version

        Returns:
            bool: True if compatible
        """
        version_order = [
            MessageVersion.V1_0,
            MessageVersion.V1_1,
            MessageVersion.V1_2,
            MessageVersion.V2_0,
        ]
        if version == MessageVersion.UNKNOWN:
            return False
        try:
            source_idx = version_order.index(version)
            target_idx = version_order.index(target_version)
            return source_idx <= target_idx
        except ValueError:
            return False


class MessageConverter:
    """Converts messages between different format versions"""

    def __init__(self):
        self.translator = MessageTypeTranslator()
        self.detector = MessageVersionDetector()

    def convert_to_current(
        self, message_data: Union[Dict[str, Any], str]
    ) -> ConversionResult:
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
                    result.errors.append(f"Invalid JSON: {e}")
                    return result
            if not isinstance(message_data, dict):
                result.errors.append("Message data must be a dictionary")
                return result
            source_version = self.detector.detect_version(message_data)
            result.original_version = source_version
            if source_version == MessageVersion.UNKNOWN:
                result.warnings.append(
                    "Unknown message format, attempting best-effort conversion"
                )
            converted_data = self._convert_from_version(message_data, source_version)
            try:
                message = BeastModeMessage(**converted_data)
                result.success = True
                result.message = message
                if source_version != MessageVersion.V2_0:
                    result.warnings.append(
                        f"Converted from {source_version.value} to {MessageVersion.V2_0.value}"
                    )
            except ValidationError as e:
                result.errors.append(f"Validation failed: {e}")
                try:
                    lenient_data = self._apply_lenient_conversion(converted_data)
                    message = BeastModeMessage(**lenient_data)
                    result.success = True
                    result.message = message
                    result.warnings.append(
                        "Applied lenient conversion due to validation errors"
                    )
                except ValidationError as e2:
                    result.errors.append(f"Lenient conversion also failed: {e2}")
        except Exception as e:
            result.errors.append(f"Conversion error: {e}")
            logger.error(f"Message conversion error: {e}")
        return result

    def _convert_from_version(
        self, message_data: Dict[str, Any], source_version: MessageVersion
    ) -> Dict[str, Any]:
        """Convert message from specific version to current format"""
        converted = message_data.copy()
        if source_version == MessageVersion.V1_0:
            converted = self._convert_from_v1_0(converted)
        elif source_version == MessageVersion.V1_1:
            converted = self._convert_from_v1_1(converted)
        elif source_version == MessageVersion.V1_2:
            converted = self._convert_from_v1_2(converted)
        elif source_version == MessageVersion.UNKNOWN:
            if "from" in converted or "content" in converted:
                converted = self._convert_from_v1_0(converted)
        if "id" not in converted:
            import uuid

            converted["id"] = str(uuid.uuid4())
        if "timestamp" not in converted:
            converted["timestamp"] = datetime.now()
        elif isinstance(converted["timestamp"], str):
            try:
                converted["timestamp"] = datetime.fromisoformat(
                    converted["timestamp"].replace("Z", "+00:00")
                )
            except ValueError:
                converted["timestamp"] = datetime.now()
        if "priority" not in converted:
            converted["priority"] = 5
        if "payload" not in converted:
            converted["payload"] = {}
        if "type" in converted:
            try:
                MessageType(converted["type"])
            except ValueError:
                converted["type"] = self.translator.translate_to_current(
                    converted["type"]
                ).value
        else:
            converted["type"] = MessageType.SIMPLE_MESSAGE.value
        if "source" not in converted:
            converted["source"] = "unknown_agent"
        return converted

    def _convert_from_v1_0(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert from V1.0 format"""
        converted = message_data.copy()
        if "from" in converted:
            converted["source"] = converted.pop("from")
        if "to" in converted:
            converted["target"] = converted.pop("to")
        if "payload" not in converted:
            standard_fields = {
                "type",
                "source",
                "target",
                "timestamp",
                "priority",
                "id",
                "correlation_id",
            }
            payload_data = {}
            fields_to_move = []
            for key, value in converted.items():
                if key not in standard_fields:
                    payload_data[key] = value
                    fields_to_move.append(key)
            for key in fields_to_move:
                converted.pop(key)
            converted["payload"] = payload_data
        return converted

    def _convert_from_v1_1(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert from V1.1 format"""
        converted = message_data.copy()
        if "request_id" in converted and "correlation_id" not in converted:
            converted["correlation_id"] = converted.pop("request_id")
        return converted

    def _convert_from_v1_2(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert from V1.2 format"""
        return message_data

    def _apply_lenient_conversion(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply lenient conversion rules for problematic messages"""
        converted = message_data.copy()
        if "priority" in converted:
            try:
                priority = int(converted["priority"])
                converted["priority"] = max(1, min(10, priority))
            except (ValueError, TypeError):
                converted["priority"] = 5
        if "payload" in converted and (not isinstance(converted["payload"], dict)):
            if isinstance(converted["payload"], str):
                try:
                    converted["payload"] = json.loads(converted["payload"])
                except json.JSONDecodeError:
                    converted["payload"] = {"content": converted["payload"]}
            else:
                converted["payload"] = {"data": converted["payload"]}
        if "timestamp" in converted and (
            not isinstance(converted["timestamp"], datetime)
        ):
            converted["timestamp"] = datetime.now()
        return converted

    def convert_to_legacy(
        self,
        message: BeastModeMessage,
        target_version: MessageVersion = MessageVersion.V1_0,
    ) -> Dict[str, Any]:
        """
        Convert current message to legacy format.

        Args:
            message: Current format message
            target_version: Target legacy version

        Returns:
            Dict[str, Any]: Legacy format message data
        """
        legacy_data = message.model_dump()
        legacy_data["type"] = self.translator.translate_to_legacy(
            message.type, target_version
        )
        if target_version == MessageVersion.V1_0:
            legacy_data.pop("correlation_id", None)
            legacy_data.pop("priority", None)
            legacy_data.pop("id", None)
            if "target" in legacy_data:
                legacy_data["to"] = legacy_data.pop("target")
            if "source" in legacy_data:
                legacy_data["from"] = legacy_data.pop("source")
        elif target_version == MessageVersion.V1_1:
            legacy_data.pop("id", None)
            if "correlation_id" in legacy_data:
                legacy_data["request_id"] = legacy_data.pop("correlation_id")
        if "timestamp" in legacy_data and isinstance(
            legacy_data["timestamp"], datetime
        ):
            legacy_data["timestamp"] = legacy_data["timestamp"].isoformat()
        return legacy_data


class MessageCompatibilityLayer:
    """Main compatibility layer for handling different message formats"""

    def __init__(self, mode: CompatibilityMode = CompatibilityMode.CONVERT):
        self.mode = mode
        self.converter = MessageConverter()
        self.detector = MessageVersionDetector()
        self.stats = {
            "messages_processed": 0,
            "conversions_successful": 0,
            "conversions_failed": 0,
            "unknown_types_handled": 0,
            "validation_errors": 0,
            "version_distribution": {},
            "last_activity": None,
        }
        self.strict_validation = mode == CompatibilityMode.STRICT
        self.auto_convert = mode in [
            CompatibilityMode.CONVERT,
            CompatibilityMode.PASSTHROUGH,
        ]
        self.log_unknown_types = True
        self.unknown_type_handlers: Dict[str, MessageType] = {}
        self.custom_type_registry: Set[str] = set()

    def register_unknown_type_handler(
        self, unknown_type: str, mapped_type: MessageType
    ) -> None:
        """
        Register a handler for unknown message types.

        Args:
            unknown_type: The unknown type string
            mapped_type: MessageType to map it to
        """
        self.unknown_type_handlers[unknown_type] = mapped_type
        logger.info(
            f"Registered unknown type handler: {unknown_type} -> {mapped_type.value}"
        )

    def register_custom_type(self, custom_type: str) -> None:
        """
        Register a custom message type as valid.

        Args:
            custom_type: Custom type string to accept
        """
        self.custom_type_registry.add(custom_type)
        logger.info(f"Registered custom message type: {custom_type}")

    def process_message(
        self, message_data: Union[Dict[str, Any], str, BeastModeMessage]
    ) -> ConversionResult:
        """
        Process incoming message with compatibility handling.

        Args:
            message_data: Raw message data in any supported format

        Returns:
            ConversionResult: Processing result
        """
        self.stats["messages_processed"] += 1
        self.stats["last_activity"] = datetime.now()
        if isinstance(message_data, BeastModeMessage):
            result = ConversionResult(success=True, message=message_data)
            result.original_version = MessageVersion.V2_0
            result.target_version = MessageVersion.V2_0
            return result
        result = self.converter.convert_to_current(message_data)
        if self.strict_validation and (
            not result.success or result.original_version == MessageVersion.UNKNOWN
        ):
            result.success = False
            if not result.errors:
                result.errors.append("Message format not supported in strict mode")
            self.stats["conversions_failed"] += 1
            return result
        if result.success:
            self.stats["conversions_successful"] += 1
            if result.original_version:
                version_key = result.original_version.value
                self.stats["version_distribution"][version_key] = (
                    self.stats["version_distribution"].get(version_key, 0) + 1
                )
        else:
            self.stats["conversions_failed"] += 1
        if result.message:
            original_type_str = (
                str(message_data.get("type", ""))
                if isinstance(message_data, dict)
                else ""
            )
            if original_type_str and original_type_str in self.unknown_type_handlers:
                result.message.type = self.unknown_type_handlers[original_type_str]
                result.warnings.append(
                    f"Mapped unknown type to {result.message.type.value}"
                )
                self.stats["unknown_types_handled"] += 1
            elif self._is_unknown_type(result.message.type):
                handled_type = self._handle_unknown_type(result.message.type)
                if handled_type and handled_type != result.message.type:
                    result.message.type = handled_type
                    result.warnings.append(
                        f"Mapped unknown type to {handled_type.value}"
                    )
                    self.stats["unknown_types_handled"] += 1
        return result

    def _is_unknown_type(self, message_type: MessageType) -> bool:
        """Check if message type is unknown/custom"""
        try:
            MessageType(message_type.value)
            return False
        except ValueError:
            return True

    def _handle_unknown_type(self, message_type: MessageType) -> Optional[MessageType]:
        """Handle unknown message type"""
        type_str = (
            message_type.value if hasattr(message_type, "value") else str(message_type)
        )
        if type_str in self.unknown_type_handlers:
            return self.unknown_type_handlers[type_str]
        if type_str in self.custom_type_registry:
            return message_type
        if self.log_unknown_types:
            logger.warning(f"Unknown message type encountered: {type_str}")
        type_lower = type_str.lower()
        if any((keyword in type_lower for keyword in ["request", "query", "ask"])):
            return MessageType.PROMPT_REQUEST
        elif any(
            (keyword in type_lower for keyword in ["response", "reply", "answer"])
        ):
            return MessageType.PROMPT_RESPONSE
        elif any((keyword in type_lower for keyword in ["help", "assist", "support"])):
            return MessageType.HELP_WANTED
        elif any((keyword in type_lower for keyword in ["spore", "share", "deliver"])):
            return MessageType.SPORE_DELIVERY
        elif any((keyword in type_lower for keyword in ["health", "status", "ping"])):
            return MessageType.SYSTEM_HEALTH
        else:
            return MessageType.SIMPLE_MESSAGE

    def validate_message_compatibility(
        self, message: BeastModeMessage, target_agents: List[str] = None
    ) -> List[str]:
        """
        Validate message compatibility with target agents.

        Args:
            message: Message to validate
            target_agents: List of target agent IDs (optional)

        Returns:
            List[str]: List of compatibility warnings
        """
        warnings = []
        newer_types = {
            MessageType.SPORE_SPAWN,
            MessageType.OFFICE_HOURS_ANNOUNCEMENT,
            MessageType.COLLABORATION_REQUEST,
            MessageType.COLLABORATION_RESPONSE,
            MessageType.COLLABORATION_START,
            MessageType.COLLABORATION_END,
            MessageType.COLLABORATION_UPDATE,
        }
        if message.type in newer_types:
            warnings.append(
                f"Message type {message.type.value} may not be supported by older agents"
            )
        if message.payload:
            payload_size = len(json.dumps(message.payload))
            if payload_size > 10000:
                warnings.append("Large payload may cause issues with older agents")
            if self._has_complex_payload(message.payload):
                warnings.append(
                    "Complex payload structure may not be compatible with all agents"
                )
        return warnings

    def _has_complex_payload(
        self, payload: Dict[str, Any], max_depth: int = 3, current_depth: int = 0
    ) -> bool:
        """Check if payload has complex nested structure"""
        if current_depth >= max_depth:
            return True
        for value in payload.values():
            if isinstance(value, dict):
                if self._has_complex_payload(value, max_depth, current_depth + 1):
                    return True
            elif isinstance(value, list) and value:
                if isinstance(value[0], dict):
                    return True
        return False

    def get_compatibility_stats(self) -> Dict[str, Any]:
        """Get compatibility layer statistics"""
        return {
            "mode": self.mode.value,
            "stats": self.stats.copy(),
            "unknown_handlers": len(self.unknown_type_handlers),
            "custom_types": len(self.custom_type_registry),
            "strict_validation": self.strict_validation,
            "auto_convert": self.auto_convert,
        }

    def create_compatibility_report(self) -> Dict[str, Any]:
        """Create detailed compatibility report"""
        total_processed = self.stats["messages_processed"]
        success_rate = (
            self.stats["conversions_successful"] / total_processed * 100
            if total_processed > 0
            else 0
        )
        return {
            "summary": {
                "total_messages_processed": total_processed,
                "conversion_success_rate": f"{success_rate:.1f}%",
                "unknown_types_handled": self.stats["unknown_types_handled"],
                "mode": self.mode.value,
            },
            "version_distribution": self.stats["version_distribution"],
            "registered_handlers": {
                "unknown_type_mappings": dict(self.unknown_type_handlers),
                "custom_types": list(self.custom_type_registry),
            },
            "configuration": {
                "strict_validation": self.strict_validation,
                "auto_convert": self.auto_convert,
                "log_unknown_types": self.log_unknown_types,
            },
        }


def detect_message_version(message_data: Dict[str, Any]) -> MessageVersion:
    """
    Detect message format version.

    Args:
        message_data: Raw message data

    Returns:
        MessageVersion: Detected version
    """
    detector = MessageVersionDetector()
    return detector.detect_version(message_data)


def is_compatible_message(message_data: Union[Dict[str, Any], str]) -> bool:
    """
    Check if message data is compatible with current format.

    Args:
        message_data: Raw message data

    Returns:
        bool: True if compatible
    """
    compatibility_layer = MessageCompatibilityLayer(CompatibilityMode.STRICT)
    result = compatibility_layer.process_message(message_data)
    return result.success


def __post_init__(self):
    if self.warnings is None:
        self.warnings = []
    if self.errors is None:
        self.errors = []


def __init__(self):
    self.legacy_mappings = {
        LegacyMessageType.MESSAGE: MessageType.SIMPLE_MESSAGE,
        LegacyMessageType.REQUEST: MessageType.PROMPT_REQUEST,
        LegacyMessageType.RESPONSE: MessageType.PROMPT_RESPONSE,
        LegacyMessageType.DISCOVERY: MessageType.AGENT_DISCOVERY,
        LegacyMessageType.HELP: MessageType.HELP_WANTED,
        LegacyMessageType.SPORE: MessageType.SPORE_DELIVERY,
        LegacyMessageType.TEXT_MESSAGE: MessageType.SIMPLE_MESSAGE,
        LegacyMessageType.AGENT_ANNOUNCE: MessageType.AGENT_DISCOVERY,
        LegacyMessageType.CAPABILITY_REQUEST: MessageType.HELP_WANTED,
        "msg": MessageType.SIMPLE_MESSAGE,
        "text": MessageType.SIMPLE_MESSAGE,
        "chat": MessageType.SIMPLE_MESSAGE,
        "prompt": MessageType.PROMPT_REQUEST,
        "query": MessageType.PROMPT_REQUEST,
        "answer": MessageType.PROMPT_RESPONSE,
        "reply": MessageType.PROMPT_RESPONSE,
        "announce": MessageType.AGENT_DISCOVERY,
        "broadcast": MessageType.AGENT_DISCOVERY,
        "ping": MessageType.SYSTEM_HEALTH,
        "health": MessageType.SYSTEM_HEALTH,
        "status": MessageType.SYSTEM_HEALTH,
    }
    self.current_to_legacy = {
        MessageType.SIMPLE_MESSAGE: LegacyMessageType.MESSAGE,
        MessageType.PROMPT_REQUEST: LegacyMessageType.REQUEST,
        MessageType.PROMPT_RESPONSE: LegacyMessageType.RESPONSE,
        MessageType.AGENT_DISCOVERY: LegacyMessageType.DISCOVERY,
        MessageType.HELP_WANTED: LegacyMessageType.HELP,
        MessageType.SPORE_DELIVERY: LegacyMessageType.SPORE,
    }


def translate_to_current(
    self, legacy_type: Union[str, LegacyMessageType]
) -> MessageType:
    """
    Translate legacy message type to current format.

    Args:
        legacy_type: Legacy message type

    Returns:
        MessageType: Current message type

    Raises:
        MessageConversionError: If translation fails
    """
    if isinstance(legacy_type, str):
        try:
            return MessageType(legacy_type)
        except ValueError:
            pass
        legacy_type_lower = legacy_type.lower()
        if legacy_type_lower in self.legacy_mappings:
            return self.legacy_mappings[legacy_type_lower]
        try:
            legacy_enum = LegacyMessageType(legacy_type_lower)
            if legacy_enum in self.legacy_mappings:
                return self.legacy_mappings[legacy_enum]
        except ValueError:
            pass
    elif isinstance(legacy_type, LegacyMessageType):
        if legacy_type in self.legacy_mappings:
            return self.legacy_mappings[legacy_type]
    logger.warning(
        f"Unknown message type '{legacy_type}', defaulting to SIMPLE_MESSAGE"
    )
    return MessageType.SIMPLE_MESSAGE


def translate_to_legacy(
    self,
    current_type: MessageType,
    target_version: MessageVersion = MessageVersion.V1_0,
) -> str:
    """
    Translate current message type to legacy format.

    Args:
        current_type: Current message type
        target_version: Target legacy version

    Returns:
        str: Legacy message type string
    """
    if current_type in self.current_to_legacy:
        return self.current_to_legacy[current_type].value
    fallback_mappings = {
        MessageType.SPORE_REQUEST: LegacyMessageType.REQUEST.value,
        MessageType.SPORE_SPAWN: LegacyMessageType.SPORE.value,
        MessageType.TECHNICAL_EXCHANGE: LegacyMessageType.MESSAGE.value,
        MessageType.SYSTEM_HEALTH: LegacyMessageType.MESSAGE.value,
        MessageType.OFFICE_HOURS_ANNOUNCEMENT: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_REQUEST: LegacyMessageType.REQUEST.value,
        MessageType.COLLABORATION_RESPONSE: LegacyMessageType.RESPONSE.value,
        MessageType.COLLABORATION_START: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_END: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_UPDATE: LegacyMessageType.MESSAGE.value,
    }
    return fallback_mappings.get(current_type, LegacyMessageType.MESSAGE.value)


def __init__(self):
    self.version_signatures = {
        MessageVersion.V1_0: {
            "required_fields": {"type", "source"},
            "optional_fields": {"target", "payload", "timestamp"},
            "forbidden_fields": {"correlation_id", "priority", "id"},
            "type_format": "string",
        },
        MessageVersion.V1_1: {
            "required_fields": {"type", "source"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
            },
            "forbidden_fields": {"id"},
            "type_format": "string",
        },
        MessageVersion.V1_2: {
            "required_fields": {"type", "source"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
                "id",
            },
            "forbidden_fields": set(),
            "type_format": "string",
            "collaboration_types": True,
        },
        MessageVersion.V2_0: {
            "required_fields": {"type", "source", "id"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
            },
            "forbidden_fields": set(),
            "type_format": "enum",
            "full_validation": True,
        },
    }


def detect_version(self, message_data: Dict[str, Any]) -> MessageVersion:
    """
    Detect message format version from message structure.

    Args:
        message_data: Raw message data

    Returns:
        MessageVersion: Detected version
    """
    if not isinstance(message_data, dict):
        return MessageVersion.UNKNOWN
    message_fields = set(message_data.keys())
    if (
        "id" in message_fields
        and "type" in message_fields
        and ("source" in message_fields)
    ):
        msg_id = message_data.get("id")
        if msg_id and isinstance(msg_id, str) and (len(msg_id) == 36):
            try:
                import uuid

                uuid.UUID(msg_id)
                return MessageVersion.V2_0
            except ValueError:
                pass
    if "type" in message_fields and "source" in message_fields:
        msg_type = message_data.get("type", "")
        if "collaboration" in msg_type.lower() or "office_hours" in msg_type.lower():
            return MessageVersion.V1_2
    if "source" in message_fields and "type" in message_fields:
        if (
            "correlation_id" in message_fields
            or "priority" in message_fields
            or "request_id" in message_fields
        ):
            return MessageVersion.V1_1
    if "from" in message_fields and "type" in message_fields:
        return MessageVersion.V1_0
    for version, signature in self.version_signatures.items():
        required_fields = signature["required_fields"]
        forbidden_fields = signature["forbidden_fields"]
        if not required_fields.issubset(message_fields):
            continue
        if forbidden_fields.intersection(message_fields):
            continue
        return version
    return MessageVersion.UNKNOWN


def is_compatible_version(
    self, version: MessageVersion, target_version: MessageVersion = MessageVersion.V2_0
) -> bool:
    """
    Check if a version is compatible with target version.

    Args:
        version: Source version
        target_version: Target version

    Returns:
        bool: True if compatible
    """
    version_order = [
        MessageVersion.V1_0,
        MessageVersion.V1_1,
        MessageVersion.V1_2,
        MessageVersion.V2_0,
    ]
    if version == MessageVersion.UNKNOWN:
        return False
    try:
        source_idx = version_order.index(version)
        target_idx = version_order.index(target_version)
        return source_idx <= target_idx
    except ValueError:
        return False


def __init__(self):
    self.translator = MessageTypeTranslator()
    self.detector = MessageVersionDetector()


def _apply_lenient_conversion(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply lenient conversion rules for problematic messages"""
    converted = message_data.copy()
    if "priority" in converted:
        try:
            priority = int(converted["priority"])
            converted["priority"] = max(1, min(10, priority))
        except (ValueError, TypeError):
            converted["priority"] = 5
    if "payload" in converted and (not isinstance(converted["payload"], dict)):
        if isinstance(converted["payload"], str):
            try:
                converted["payload"] = json.loads(converted["payload"])
            except json.JSONDecodeError:
                converted["payload"] = {"content": converted["payload"]}
        else:
            converted["payload"] = {"data": converted["payload"]}
    if "timestamp" in converted and (not isinstance(converted["timestamp"], datetime)):
        converted["timestamp"] = datetime.now()
    return converted


def __init__(self, mode: CompatibilityMode = CompatibilityMode.CONVERT):
    self.mode = mode
    self.converter = MessageConverter()
    self.detector = MessageVersionDetector()
    self.stats = {
        "messages_processed": 0,
        "conversions_successful": 0,
        "conversions_failed": 0,
        "unknown_types_handled": 0,
        "validation_errors": 0,
        "version_distribution": {},
        "last_activity": None,
    }
    self.strict_validation = mode == CompatibilityMode.STRICT
    self.auto_convert = mode in [
        CompatibilityMode.CONVERT,
        CompatibilityMode.PASSTHROUGH,
    ]
    self.log_unknown_types = True
    self.unknown_type_handlers: Dict[str, MessageType] = {}
    self.custom_type_registry: Set[str] = set()


def register_unknown_type_handler(
    self, unknown_type: str, mapped_type: MessageType
) -> None:
    """
    Register a handler for unknown message types.

    Args:
        unknown_type: The unknown type string
        mapped_type: MessageType to map it to
    """
    self.unknown_type_handlers[unknown_type] = mapped_type
    logger.info(
        f"Registered unknown type handler: {unknown_type} -> {mapped_type.value}"
    )


def register_custom_type(self, custom_type: str) -> None:
    """
    Register a custom message type as valid.

    Args:
        custom_type: Custom type string to accept
    """
    self.custom_type_registry.add(custom_type)
    logger.info(f"Registered custom message type: {custom_type}")


def _is_unknown_type(self, message_type: MessageType) -> bool:
    """Check if message type is unknown/custom"""
    try:
        MessageType(message_type.value)
        return False
    except ValueError:
        return True


def _handle_unknown_type(self, message_type: MessageType) -> Optional[MessageType]:
    """Handle unknown message type"""
    type_str = (
        message_type.value if hasattr(message_type, "value") else str(message_type)
    )
    if type_str in self.unknown_type_handlers:
        return self.unknown_type_handlers[type_str]
    if type_str in self.custom_type_registry:
        return message_type
    if self.log_unknown_types:
        logger.warning(f"Unknown message type encountered: {type_str}")
    type_lower = type_str.lower()
    if any((keyword in type_lower for keyword in ["request", "query", "ask"])):
        return MessageType.PROMPT_REQUEST
    elif any((keyword in type_lower for keyword in ["response", "reply", "answer"])):
        return MessageType.PROMPT_RESPONSE
    elif any((keyword in type_lower for keyword in ["help", "assist", "support"])):
        return MessageType.HELP_WANTED
    elif any((keyword in type_lower for keyword in ["spore", "share", "deliver"])):
        return MessageType.SPORE_DELIVERY
    elif any((keyword in type_lower for keyword in ["health", "status", "ping"])):
        return MessageType.SYSTEM_HEALTH
    else:
        return MessageType.SIMPLE_MESSAGE


def _has_complex_payload(
    self, payload: Dict[str, Any], max_depth: int = 3, current_depth: int = 0
) -> bool:
    """Check if payload has complex nested structure"""
    if current_depth >= max_depth:
        return True
    for value in payload.values():
        if isinstance(value, dict):
            if self._has_complex_payload(value, max_depth, current_depth + 1):
                return True
        elif isinstance(value, list) and value:
            if isinstance(value[0], dict):
                return True
    return False


def get_compatibility_stats(self) -> Dict[str, Any]:
    """Get compatibility layer statistics"""
    return {
        "mode": self.mode.value,
        "stats": self.stats.copy(),
        "unknown_handlers": len(self.unknown_type_handlers),
        "custom_types": len(self.custom_type_registry),
        "strict_validation": self.strict_validation,
        "auto_convert": self.auto_convert,
    }


def create_compatibility_report(self) -> Dict[str, Any]:
    """Create detailed compatibility report"""
    total_processed = self.stats["messages_processed"]
    success_rate = (
        self.stats["conversions_successful"] / total_processed * 100
        if total_processed > 0
        else 0
    )
    return {
        "summary": {
            "total_messages_processed": total_processed,
            "conversion_success_rate": f"{success_rate:.1f}%",
            "unknown_types_handled": self.stats["unknown_types_handled"],
            "mode": self.mode.value,
        },
        "version_distribution": self.stats["version_distribution"],
        "registered_handlers": {
            "unknown_type_mappings": dict(self.unknown_type_handlers),
            "custom_types": list(self.custom_type_registry),
        },
        "configuration": {
            "strict_validation": self.strict_validation,
            "auto_convert": self.auto_convert,
            "log_unknown_types": self.log_unknown_types,
        },
    }


def __post_init__(self):
    if self.warnings is None:
        self.warnings = []
    if self.errors is None:
        self.errors = []


def __init__(self):
    self.legacy_mappings = {
        LegacyMessageType.MESSAGE: MessageType.SIMPLE_MESSAGE,
        LegacyMessageType.REQUEST: MessageType.PROMPT_REQUEST,
        LegacyMessageType.RESPONSE: MessageType.PROMPT_RESPONSE,
        LegacyMessageType.DISCOVERY: MessageType.AGENT_DISCOVERY,
        LegacyMessageType.HELP: MessageType.HELP_WANTED,
        LegacyMessageType.SPORE: MessageType.SPORE_DELIVERY,
        LegacyMessageType.TEXT_MESSAGE: MessageType.SIMPLE_MESSAGE,
        LegacyMessageType.AGENT_ANNOUNCE: MessageType.AGENT_DISCOVERY,
        LegacyMessageType.CAPABILITY_REQUEST: MessageType.HELP_WANTED,
        "msg": MessageType.SIMPLE_MESSAGE,
        "text": MessageType.SIMPLE_MESSAGE,
        "chat": MessageType.SIMPLE_MESSAGE,
        "prompt": MessageType.PROMPT_REQUEST,
        "query": MessageType.PROMPT_REQUEST,
        "answer": MessageType.PROMPT_RESPONSE,
        "reply": MessageType.PROMPT_RESPONSE,
        "announce": MessageType.AGENT_DISCOVERY,
        "broadcast": MessageType.AGENT_DISCOVERY,
        "ping": MessageType.SYSTEM_HEALTH,
        "health": MessageType.SYSTEM_HEALTH,
        "status": MessageType.SYSTEM_HEALTH,
    }
    self.current_to_legacy = {
        MessageType.SIMPLE_MESSAGE: LegacyMessageType.MESSAGE,
        MessageType.PROMPT_REQUEST: LegacyMessageType.REQUEST,
        MessageType.PROMPT_RESPONSE: LegacyMessageType.RESPONSE,
        MessageType.AGENT_DISCOVERY: LegacyMessageType.DISCOVERY,
        MessageType.HELP_WANTED: LegacyMessageType.HELP,
        MessageType.SPORE_DELIVERY: LegacyMessageType.SPORE,
    }


def translate_to_current(
    self, legacy_type: Union[str, LegacyMessageType]
) -> MessageType:
    """
    Translate legacy message type to current format.

    Args:
        legacy_type: Legacy message type

    Returns:
        MessageType: Current message type

    Raises:
        MessageConversionError: If translation fails
    """
    if isinstance(legacy_type, str):
        try:
            return MessageType(legacy_type)
        except ValueError:
            pass
        legacy_type_lower = legacy_type.lower()
        if legacy_type_lower in self.legacy_mappings:
            return self.legacy_mappings[legacy_type_lower]
        try:
            legacy_enum = LegacyMessageType(legacy_type_lower)
            if legacy_enum in self.legacy_mappings:
                return self.legacy_mappings[legacy_enum]
        except ValueError:
            pass
    elif isinstance(legacy_type, LegacyMessageType):
        if legacy_type in self.legacy_mappings:
            return self.legacy_mappings[legacy_type]
    logger.warning(
        f"Unknown message type '{legacy_type}', defaulting to SIMPLE_MESSAGE"
    )
    return MessageType.SIMPLE_MESSAGE


def translate_to_legacy(
    self,
    current_type: MessageType,
    target_version: MessageVersion = MessageVersion.V1_0,
) -> str:
    """
    Translate current message type to legacy format.

    Args:
        current_type: Current message type
        target_version: Target legacy version

    Returns:
        str: Legacy message type string
    """
    if current_type in self.current_to_legacy:
        return self.current_to_legacy[current_type].value
    fallback_mappings = {
        MessageType.SPORE_REQUEST: LegacyMessageType.REQUEST.value,
        MessageType.SPORE_SPAWN: LegacyMessageType.SPORE.value,
        MessageType.TECHNICAL_EXCHANGE: LegacyMessageType.MESSAGE.value,
        MessageType.SYSTEM_HEALTH: LegacyMessageType.MESSAGE.value,
        MessageType.OFFICE_HOURS_ANNOUNCEMENT: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_REQUEST: LegacyMessageType.REQUEST.value,
        MessageType.COLLABORATION_RESPONSE: LegacyMessageType.RESPONSE.value,
        MessageType.COLLABORATION_START: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_END: LegacyMessageType.MESSAGE.value,
        MessageType.COLLABORATION_UPDATE: LegacyMessageType.MESSAGE.value,
    }
    return fallback_mappings.get(current_type, LegacyMessageType.MESSAGE.value)


def __init__(self):
    self.version_signatures = {
        MessageVersion.V1_0: {
            "required_fields": {"type", "source"},
            "optional_fields": {"target", "payload", "timestamp"},
            "forbidden_fields": {"correlation_id", "priority", "id"},
            "type_format": "string",
        },
        MessageVersion.V1_1: {
            "required_fields": {"type", "source"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
            },
            "forbidden_fields": {"id"},
            "type_format": "string",
        },
        MessageVersion.V1_2: {
            "required_fields": {"type", "source"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
                "id",
            },
            "forbidden_fields": set(),
            "type_format": "string",
            "collaboration_types": True,
        },
        MessageVersion.V2_0: {
            "required_fields": {"type", "source", "id"},
            "optional_fields": {
                "target",
                "payload",
                "timestamp",
                "correlation_id",
                "priority",
            },
            "forbidden_fields": set(),
            "type_format": "enum",
            "full_validation": True,
        },
    }


def detect_version(self, message_data: Dict[str, Any]) -> MessageVersion:
    """
    Detect message format version from message structure.

    Args:
        message_data: Raw message data

    Returns:
        MessageVersion: Detected version
    """
    if not isinstance(message_data, dict):
        return MessageVersion.UNKNOWN
    message_fields = set(message_data.keys())
    if (
        "id" in message_fields
        and "type" in message_fields
        and ("source" in message_fields)
    ):
        msg_id = message_data.get("id")
        if msg_id and isinstance(msg_id, str) and (len(msg_id) == 36):
            try:
                import uuid

                uuid.UUID(msg_id)
                return MessageVersion.V2_0
            except ValueError:
                pass
    if "type" in message_fields and "source" in message_fields:
        msg_type = message_data.get("type", "")
        if "collaboration" in msg_type.lower() or "office_hours" in msg_type.lower():
            return MessageVersion.V1_2
    if "source" in message_fields and "type" in message_fields:
        if (
            "correlation_id" in message_fields
            or "priority" in message_fields
            or "request_id" in message_fields
        ):
            return MessageVersion.V1_1
    if "from" in message_fields and "type" in message_fields:
        return MessageVersion.V1_0
    for version, signature in self.version_signatures.items():
        required_fields = signature["required_fields"]
        forbidden_fields = signature["forbidden_fields"]
        if not required_fields.issubset(message_fields):
            continue
        if forbidden_fields.intersection(message_fields):
            continue
        return version
    return MessageVersion.UNKNOWN


def is_compatible_version(
    self, version: MessageVersion, target_version: MessageVersion = MessageVersion.V2_0
) -> bool:
    """
    Check if a version is compatible with target version.

    Args:
        version: Source version
        target_version: Target version

    Returns:
        bool: True if compatible
    """
    version_order = [
        MessageVersion.V1_0,
        MessageVersion.V1_1,
        MessageVersion.V1_2,
        MessageVersion.V2_0,
    ]
    if version == MessageVersion.UNKNOWN:
        return False
    try:
        source_idx = version_order.index(version)
        target_idx = version_order.index(target_version)
        return source_idx <= target_idx
    except ValueError:
        return False


def __init__(self):
    self.translator = MessageTypeTranslator()
    self.detector = MessageVersionDetector()


def _apply_lenient_conversion(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply lenient conversion rules for problematic messages"""
    converted = message_data.copy()
    if "priority" in converted:
        try:
            priority = int(converted["priority"])
            converted["priority"] = max(1, min(10, priority))
        except (ValueError, TypeError):
            converted["priority"] = 5
    if "payload" in converted and (not isinstance(converted["payload"], dict)):
        if isinstance(converted["payload"], str):
            try:
                converted["payload"] = json.loads(converted["payload"])
            except json.JSONDecodeError:
                converted["payload"] = {"content": converted["payload"]}
        else:
            converted["payload"] = {"data": converted["payload"]}
    if "timestamp" in converted and (not isinstance(converted["timestamp"], datetime)):
        converted["timestamp"] = datetime.now()
    return converted


def __init__(self, mode: CompatibilityMode = CompatibilityMode.CONVERT):
    self.mode = mode
    self.converter = MessageConverter()
    self.detector = MessageVersionDetector()
    self.stats = {
        "messages_processed": 0,
        "conversions_successful": 0,
        "conversions_failed": 0,
        "unknown_types_handled": 0,
        "validation_errors": 0,
        "version_distribution": {},
        "last_activity": None,
    }
    self.strict_validation = mode == CompatibilityMode.STRICT
    self.auto_convert = mode in [
        CompatibilityMode.CONVERT,
        CompatibilityMode.PASSTHROUGH,
    ]
    self.log_unknown_types = True
    self.unknown_type_handlers: Dict[str, MessageType] = {}
    self.custom_type_registry: Set[str] = set()


def register_unknown_type_handler(
    self, unknown_type: str, mapped_type: MessageType
) -> None:
    """
    Register a handler for unknown message types.

    Args:
        unknown_type: The unknown type string
        mapped_type: MessageType to map it to
    """
    self.unknown_type_handlers[unknown_type] = mapped_type
    logger.info(
        f"Registered unknown type handler: {unknown_type} -> {mapped_type.value}"
    )


def register_custom_type(self, custom_type: str) -> None:
    """
    Register a custom message type as valid.

    Args:
        custom_type: Custom type string to accept
    """
    self.custom_type_registry.add(custom_type)
    logger.info(f"Registered custom message type: {custom_type}")


def _is_unknown_type(self, message_type: MessageType) -> bool:
    """Check if message type is unknown/custom"""
    try:
        MessageType(message_type.value)
        return False
    except ValueError:
        return True


def _handle_unknown_type(self, message_type: MessageType) -> Optional[MessageType]:
    """Handle unknown message type"""
    type_str = (
        message_type.value if hasattr(message_type, "value") else str(message_type)
    )
    if type_str in self.unknown_type_handlers:
        return self.unknown_type_handlers[type_str]
    if type_str in self.custom_type_registry:
        return message_type
    if self.log_unknown_types:
        logger.warning(f"Unknown message type encountered: {type_str}")
    type_lower = type_str.lower()
    if any((keyword in type_lower for keyword in ["request", "query", "ask"])):
        return MessageType.PROMPT_REQUEST
    elif any((keyword in type_lower for keyword in ["response", "reply", "answer"])):
        return MessageType.PROMPT_RESPONSE
    elif any((keyword in type_lower for keyword in ["help", "assist", "support"])):
        return MessageType.HELP_WANTED
    elif any((keyword in type_lower for keyword in ["spore", "share", "deliver"])):
        return MessageType.SPORE_DELIVERY
    elif any((keyword in type_lower for keyword in ["health", "status", "ping"])):
        return MessageType.SYSTEM_HEALTH
    else:
        return MessageType.SIMPLE_MESSAGE


def _has_complex_payload(
    self, payload: Dict[str, Any], max_depth: int = 3, current_depth: int = 0
) -> bool:
    """Check if payload has complex nested structure"""
    if current_depth >= max_depth:
        return True
    for value in payload.values():
        if isinstance(value, dict):
            if self._has_complex_payload(value, max_depth, current_depth + 1):
                return True
        elif isinstance(value, list) and value:
            if isinstance(value[0], dict):
                return True
    return False


def get_compatibility_stats(self) -> Dict[str, Any]:
    """Get compatibility layer statistics"""
    return {
        "mode": self.mode.value,
        "stats": self.stats.copy(),
        "unknown_handlers": len(self.unknown_type_handlers),
        "custom_types": len(self.custom_type_registry),
        "strict_validation": self.strict_validation,
        "auto_convert": self.auto_convert,
    }


def create_compatibility_report(self) -> Dict[str, Any]:
    """Create detailed compatibility report"""
    total_processed = self.stats["messages_processed"]
    success_rate = (
        self.stats["conversions_successful"] / total_processed * 100
        if total_processed > 0
        else 0
    )
    return {
        "summary": {
            "total_messages_processed": total_processed,
            "conversion_success_rate": f"{success_rate:.1f}%",
            "unknown_types_handled": self.stats["unknown_types_handled"],
            "mode": self.mode.value,
        },
        "version_distribution": self.stats["version_distribution"],
        "registered_handlers": {
            "unknown_type_mappings": dict(self.unknown_type_handlers),
            "custom_types": list(self.custom_type_registry),
        },
        "configuration": {
            "strict_validation": self.strict_validation,
            "auto_convert": self.auto_convert,
            "log_unknown_types": self.log_unknown_types,
        },
    }
