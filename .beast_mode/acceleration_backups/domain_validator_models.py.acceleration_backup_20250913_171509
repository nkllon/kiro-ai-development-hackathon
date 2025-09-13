"""
Domain Validator Models

This module was extracted from domain_validator.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from .base import DomainSystemComponent
from .models import Domain, DomainCollection, ValidationResult, HealthIssue, IssueSeverity, IssueCategory, DependencyGraph
from .exceptions import DomainValidationError
import glob
import jsonschema

class SchemaValidator:
    """JSON Schema validator for domain structures"""

    def __init__(self):
        self.domain_schema = {'type': 'object', 'required': ['name', 'description', 'patterns', 'tools', 'metadata'], 'properties': {'name': {'type': 'string', 'pattern': '^[a-z][a-z0-9_]*$', 'minLength': 1}, 'description': {'type': 'string', 'minLength': 10}, 'patterns': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1}, 'content_indicators': {'type': 'array', 'items': {'type': 'string'}}, 'requirements': {'type': 'array', 'items': {'type': 'string'}}, 'dependencies': {'type': 'array', 'items': {'type': 'string'}}, 'tools': {'type': 'object', 'required': ['linter', 'formatter', 'validator'], 'properties': {'linter': {'type': 'string'}, 'formatter': {'type': 'string'}, 'validator': {'type': 'string'}, 'exclusions': {'type': 'array', 'items': {'type': 'string'}}}}, 'metadata': {'type': 'object', 'required': ['demo_role', 'extraction_candidate', 'package_potential'], 'properties': {'demo_role': {'type': 'string'}, 'extraction_candidate': {'type': 'string', 'enum': ['yes', 'no', 'maybe', 'unknown']}, 'status': {'type': 'string', 'enum': ['active', 'deprecated', 'planned', 'archived']}, 'tags': {'type': 'array', 'items': {'type': 'string'}}}}}}

    def validate_schema(self, domain_dict: Dict[str, Any]) -> List[str]:
        """Validate domain dictionary against schema"""
        try:
            import jsonschema
            jsonschema.validate(domain_dict, self.domain_schema)
            return []
        except ImportError:
            return self._basic_schema_validation(domain_dict)
        except jsonschema.ValidationError as e:
            return [str(e)]

    def _basic_schema_validation(self, domain_dict: Dict[str, Any]) -> List[str]:
        """Basic schema validation without jsonschema library"""
        errors = []
        required_fields = ['name', 'description', 'patterns', 'tools', 'metadata']
        for field in required_fields:
            if field not in domain_dict:
                errors.append(f'Missing required field: {field}')
        if 'name' in domain_dict and (not isinstance(domain_dict['name'], str)):
            errors.append("Field 'name' must be a string")
        if 'patterns' in domain_dict and (not isinstance(domain_dict['patterns'], list)):
            errors.append("Field 'patterns' must be an array")
        return errors
