"""High-level helpers for executing shell commands safely."""

from __future__ import annotations

import subprocess
from typing import Tuple

from .emergency_cli_fix import EmergencyCLIFix


class SafeShellWrapper:
    """Run shell commands with validation and sanitisation safeguards."""

    def __init__(self, cli_fix: EmergencyCLIFix | None = None):
        self.cli_fix = cli_fix or EmergencyCLIFix()

    def safe_execute(self, command: str) -> Tuple[bool, str, str]:
        """Safely execute a shell command after validation and sanitisation."""
        is_safe, error = self.cli_fix.validate_command(command)
        if not is_safe:
            return False, f"COMMAND REJECTED: {error}", ""

        safe_command = self.cli_fix.sanitize_command(command)

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


_SHARED_WRAPPER = SafeShellWrapper()


def safe_run(command: str) -> Tuple[bool, str, str]:
    """Convenience helper that executes ``command`` using a shared wrapper."""
    return _SHARED_WRAPPER.safe_execute(command)

