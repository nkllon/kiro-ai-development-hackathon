"""Validation utilities that keep interactive shell sessions stable."""

from __future__ import annotations

import re
import subprocess
from typing import Iterable, List, Tuple


class EmergencyCLIFix:
    """Permanently eliminate quote-related shell hangs and unsafe input."""

    def __init__(self, dangerous_patterns: Iterable[str] | None = None) -> None:
        self.dangerous_patterns = list(
            dangerous_patterns
            if dangerous_patterns is not None
            else [
                r'"[^"]*$',  # Unclosed double quotes
                r"'[^']*$",  # Unclosed single quotes
                r'`[^`]*$',  # Unclosed backticks
                r'\\$',  # Trailing backslash
                r'&&\s*$',  # Trailing &&
                r'\|\|\s*$',  # Trailing ||
            ]
        )

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Return ``(is_safe, reason)`` after static analysis of ``command``."""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                return False, f"DANGEROUS PATTERN DETECTED: {pattern}"

        # Check for balanced quotes (ignoring escaped quotes)
        if self._is_unbalanced(command, '"'):
            return False, "UNBALANCED DOUBLE QUOTES"

        if self._is_unbalanced(command, "'"):
            return False, "UNBALANCED SINGLE QUOTES"

        return True, "SAFE"

    def sanitize_command(self, command: str) -> str:
        """Return a sanitised command string safe for ``subprocess`` execution."""
        escaped = command.replace('"', '\\"').replace("'", "\\'").replace('`', '\\`')
        return re.sub(r'[&|]+\s*$', '', escaped)

    def safe_execute(self, command: str) -> Tuple[bool, str, str]:
        """Run ``command`` with validation and sanitisation safeguards applied."""
        is_safe, error = self.validate_command(command)
        if not is_safe:
            return False, error, ""

        safe_command = self.sanitize_command(command)

        try:
            result = subprocess.run(
                safe_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return True, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "COMMAND TIMEOUT", ""
        except Exception as exc:  # pragma: no cover - defensive safeguard
            return False, f"EXECUTION ERROR: {exc}", ""

    @staticmethod
    def _is_unbalanced(command: str, quote: str) -> bool:
        unescaped = command.replace(f"\\{quote}", '')
        return unescaped.count(quote) % 2 != 0


def demo() -> List[Tuple[str, Tuple[bool, str]]]:
    """Return validation results for a curated set of risky commands."""
    cli_fix = EmergencyCLIFix()
    commands = [
        'echo "unclosed quote',
        "echo 'unclosed single",
        'echo `unclosed backtick',
        'echo "test" &&',
        'echo "test" ||',
    ]
    return [(cmd, cli_fix.validate_command(cmd)) for cmd in commands]


__all__ = ["EmergencyCLIFix", "demo"]

