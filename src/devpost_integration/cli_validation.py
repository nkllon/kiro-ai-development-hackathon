#!/usr/bin/env python3
"""
CLI Validation - Argument validation and validation utilities

Extracted from cli_parser.py for RM-DDD compliance.
Single responsibility: CLI argument validation and validation utilities.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CLIValidation:
    """CLI argument validation and validation utilities."""
    
    def __init__(self):
        """Initialize CLI validation."""
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parsed arguments."""
        validated_args = {
            'command': args['command'],
            'verbose': args.get('verbose', False),
            'json': args.get('json', False),
            'log_level': args.get('log_level', 'INFO')
        }
        
        # Command-specific validation
        if args['command'] == 'interrogate':
            validated_args.update({
                'project_id': args.get('project_id')
            })
        
        elif args['command'] == 'status':
            validated_args.update({
                'project_id': args.get('project_id')
            })
        
        elif args['command'] == 'create':
            validated_args.update({
                'title': args['title'],
                'description': args['description'],
                'technologies': args.get('technologies', []),
                'tags': args.get('tags', [])
            })
            
            # Validate required fields
            if not self.validate_title(args['title']):
                raise ValueError("Title must be between 1 and 100 characters")
            if not self.validate_description(args['description']):
                raise ValueError("Description must be between 10 and 2000 characters")
        
        elif args['command'] == 'update':
            validated_args.update({
                'project_id': args['project_id'],
                'title': args.get('title'),
                'description': args.get('description'),
                'technologies': args.get('technologies'),
                'tags': args.get('tags')
            })
            
            # Validate project ID
            if not self.validate_project_id(args['project_id']):
                raise ValueError("Project ID must be alphanumeric with underscores/hyphens")
            
            # Check if at least one field is being updated
            update_fields = ['title', 'description', 'technologies', 'tags']
            if not any(args.get(field) is not None for field in update_fields):
                raise ValueError("At least one field must be specified for update")
        
        elif args['command'] == 'delete':
            validated_args.update({
                'project_id': args['project_id'],
                'force': args.get('force', False)
            })
            
            # Validate project ID
            if not self.validate_project_id(args['project_id']):
                raise ValueError("Project ID must be alphanumeric with underscores/hyphens")
        
        return validated_args
    
    def validate_project_id(self, project_id: str) -> bool:
        """Validate project ID format."""
        if not project_id or not project_id.strip():
            return False
        
        # Basic validation - should be alphanumeric with underscores/hyphens
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, project_id.strip()))
    
    def validate_title(self, title: str) -> bool:
        """Validate project title."""
        if not title or not title.strip():
            return False
        
        # Title should be between 1 and 100 characters
        return 1 <= len(title.strip()) <= 100
    
    def validate_description(self, description: str) -> bool:
        """Validate project description."""
        if not description or not description.strip():
            return False
        
        # Description should be between 10 and 2000 characters
        return 10 <= len(description.strip()) <= 2000
    
    def validate_technologies(self, technologies: list) -> bool:
        """Validate technologies list."""
        if not isinstance(technologies, list):
            return False
        
        # Each technology should be a non-empty string
        return all(isinstance(tech, str) and tech.strip() for tech in technologies)
    
    def validate_tags(self, tags: list) -> bool:
        """Validate tags list."""
        if not isinstance(tags, list):
            return False
        
        # Each tag should be a non-empty string
        return all(isinstance(tag, str) and tag.strip() for tag in tags)
    
    def validate_log_level(self, log_level: str) -> bool:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        return log_level.upper() in valid_levels
    
    def validate_verbose_flag(self, verbose: bool) -> bool:
        """Validate verbose flag."""
        return isinstance(verbose, bool)
    
    def validate_json_flag(self, json_output: bool) -> bool:
        """Validate JSON output flag."""
        return isinstance(json_output, bool)
    
    def get_validation_error_message(self, field: str, error_type: str) -> str:
        """Get validation error message for a field."""
        error_messages = {
            'project_id': {
                'empty': 'Project ID cannot be empty',
                'invalid_format': 'Project ID must be alphanumeric with underscores/hyphens',
                'too_long': 'Project ID must be 50 characters or less'
            },
            'title': {
                'empty': 'Title cannot be empty',
                'too_short': 'Title must be at least 1 character',
                'too_long': 'Title must be 100 characters or less'
            },
            'description': {
                'empty': 'Description cannot be empty',
                'too_short': 'Description must be at least 10 characters',
                'too_long': 'Description must be 2000 characters or less'
            },
            'technologies': {
                'invalid_type': 'Technologies must be a list',
                'invalid_item': 'Each technology must be a non-empty string'
            },
            'tags': {
                'invalid_type': 'Tags must be a list',
                'invalid_item': 'Each tag must be a non-empty string'
            }
        }
        
        if field in error_messages and error_type in error_messages[field]:
            return error_messages[field][error_type]
        
        return f"Validation error for {field}: {error_type}"
