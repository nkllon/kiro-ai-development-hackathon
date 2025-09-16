#!/usr/bin/env python3
"""
🚨 CLI SAFETY LINTER
==================
Base class linter for CLI usage to prevent dequote errors.
Ensures all CLI commands are properly escaped for ZSH/bash.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 2.0
"""

import re
import shlex
from typing import List, Optional, Tuple


class CLISafetyLinter:
    """CLI safety linter to prevent dequote errors and shell injection."""

    def __init__(self):
        self.dangerous_patterns = [
            r'[`$]',  # Command substitution
            r'[;&|]',  # Command chaining
            r'[<>]',  # Redirection
            r'[()]',  # Subshells
            r'[{}]',  # Brace expansion
            r'[\[\]]',  # Character classes
            r'[~*?]',  # Path expansion
            r'[!]',  # History expansion
        ]
        self.quote_patterns = [
            r"'[^']*'",  # Single quotes
            r'"[^"]*"',  # Double quotes
            r'`[^`]*`',  # Backticks
        ]

    def validate_command(self, command: str) -> Tuple[bool, List[str]]:
        """Validate CLI command for safety."""
        errors = []
        
        # Check for unescaped dangerous patterns
        for pattern in self.dangerous_patterns:
            matches = re.findall(pattern, command)
            if matches:
                errors.append(f"Unescaped dangerous pattern: {matches}")
        
        # Check for unclosed quotes
        quote_errors = self._check_quote_balance(command)
        errors.extend(quote_errors)
        
        # Check for proper escaping
        escape_errors = self._check_escaping(command)
        errors.extend(escape_errors)
        
        return len(errors) == 0, errors

    def _check_quote_balance(self, command: str) -> List[str]:
        """Check for balanced quotes."""
        errors = []
        
        # Count quotes
        single_quotes = command.count("'")
        double_quotes = command.count('"')
        backticks = command.count('`')
        
        if single_quotes % 2 != 0:
            errors.append("Unbalanced single quotes")
        if double_quotes % 2 != 0:
            errors.append("Unbalanced double quotes")
        if backticks % 2 != 0:
            errors.append("Unbalanced backticks")
        
        return errors

    def _check_escaping(self, command: str) -> List[str]:
        """Check for proper escaping."""
        errors = []
        
        # Check for unescaped quotes in strings
        if "'" in command and '"' in command:
            # Mixed quotes - check for proper escaping
            if not self._is_properly_escaped(command):
                errors.append("Improper quote escaping")
        
        return errors

    def _is_properly_escaped(self, command: str) -> bool:
        """Check if command is properly escaped."""
        try:
            # Use shlex to parse the command
            shlex.split(command)
            return True
        except ValueError:
            return False

    def sanitize_command(self, command: str) -> str:
        """Sanitize command for safe execution."""
        # Escape dangerous characters
        sanitized = command
        
        # Escape quotes
        sanitized = sanitized.replace("'", "\\'")
        sanitized = sanitized.replace('"', '\\"')
        sanitized = sanitized.replace('`', '\\`')
        
        # Escape other dangerous characters
        sanitized = sanitized.replace('$', '\\$')
        sanitized = sanitized.replace(';', '\\;')
        sanitized = sanitized.replace('|', '\\|')
        sanitized = sanitized.replace('&', '\\&')
        sanitized = sanitized.replace('<', '\\<')
        sanitized = sanitized.replace('>', '\\>')
        sanitized = sanitized.replace('(', '\\(')
        sanitized = sanitized.replace(')', '\\)')
        sanitized = sanitized.replace('{', '\\{')
        sanitized = sanitized.replace('}', '\\}')
        sanitized = sanitized.replace('[', '\\[')
        sanitized = sanitized.replace(']', '\\]')
        sanitized = sanitized.replace('~', '\\~')
        sanitized = sanitized.replace('*', '\\*')
        sanitized = sanitized.replace('?', '\\?')
        sanitized = sanitized.replace('!', '\\!')
        
        return sanitized

    def create_safe_command(self, command: str) -> str:
        """Create a safe command with proper escaping."""
        # Validate first
        is_safe, errors = self.validate_command(command)
        
        if is_safe:
            return command
        
        # If not safe, sanitize
        return self.sanitize_command(command)

    def lint_command(self, command: str) -> dict:
        """Lint command and return detailed results."""
        is_safe, errors = self.validate_command(command)
        
        return {
            "command": command,
            "is_safe": is_safe,
            "errors": errors,
            "sanitized": self.sanitize_command(command) if not is_safe else command,
            "recommendations": self._get_recommendations(errors)
        }

    def _get_recommendations(self, errors: List[str]) -> List[str]:
        """Get recommendations for fixing errors."""
        recommendations = []
        
        for error in errors:
            if "Unbalanced" in error:
                recommendations.append("Ensure all quotes are properly closed")
            elif "Unescaped" in error:
                recommendations.append("Escape dangerous characters with backslashes")
            elif "Improper" in error:
                recommendations.append("Use consistent quote types or proper escaping")
        
        return recommendations


# Global CLI safety linter instance
cli_linter = CLISafetyLinter()


def safe_command(command: str) -> str:
    """Create a safe command using the CLI linter."""
    return cli_linter.create_safe_command(command)


def lint_command(command: str) -> dict:
    """Lint a command for safety."""
    return cli_linter.lint_command(command)

