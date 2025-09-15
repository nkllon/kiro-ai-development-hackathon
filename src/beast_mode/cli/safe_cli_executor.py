#!/usr/bin/env python3
"""
Safe CLI Executor
================

Bulletproof CLI execution framework with comprehensive timeout protection,
error handling, and failure mode detection. Addresses the critical failure
modes identified in the systematic failure analysis.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Safe CLI execution with timeout protection
"""

import sys
import os
import time
import subprocess
import json
import logging
import signal
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import shlex
import tempfile
import re
from pathlib import Path


class ExecutionStatus(Enum):
    """Execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Execution mode enumeration."""

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BACKGROUND = "background"


@dataclass
class ExecutionResult:
    """Result of CLI execution."""

    command: str
    status: ExecutionStatus
    return_code: int = 0
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    timeout_seconds: int = 30
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionConfig:
    """Configuration for CLI execution."""

    timeout_seconds: int = 30
    mode: ExecutionMode = ExecutionMode.SYNCHRONOUS
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    capture_output: bool = True
    shell: bool = False
    validate_command: bool = True
    sanitize_input: bool = True
    retry_attempts: int = 0
    retry_delay: float = 1.0


class SafeCLIExecutor:
    """
    Safe CLI execution framework with comprehensive protection.

    Provides timeout protection, error handling, and failure mode detection
    for all CLI operations in the Beast Mode framework.
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        """Initialize the safe CLI executor."""
        self.config = config or ExecutionConfig()
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.execution_history: List[ExecutionResult] = []
        self.logger = self._setup_logging()
        self._shutdown_event = threading.Event()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CLI execution."""
        logger = logging.getLogger("safe_cli_executor")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command syntax and safety."""
        if not command or not command.strip():
            return False, "Empty command"

        # Check for dangerous patterns
        dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Dangerous rm commands
            r"mkfs\s+",  # Filesystem formatting
            r"format\s+",  # Disk formatting
            r"dd\s+if=/dev/",  # Direct disk access
            r">\s*/dev/",  # Output to device files
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Dangerous command pattern detected: {pattern}"

        # Validate shell syntax if using shell
        if self.config.shell:
            try:
                shlex.split(command)
            except ValueError as e:
                return False, f"Invalid shell syntax: {e}"

        return True, "Command is safe"

    def sanitize_command(self, command: str) -> str:
        """Sanitize command input to prevent injection attacks."""
        if not self.config.sanitize_input:
            return command

        # Remove potentially dangerous characters
        dangerous_chars = ["`", "$", ";", "|", "&", "(", ")", "<", ">"]
        sanitized = command

        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")

        # Limit command length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
            self.logger.warning("Command truncated due to length limit")

        return sanitized.strip()

    def check_cli_availability(self, command: str) -> Tuple[bool, str]:
        """Check if CLI command is available."""
        try:
            # Extract the base command
            base_command = command.split()[0] if command.split() else command

            # Check if command exists in PATH
            result = subprocess.run(
                ["which", base_command], capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                return False, f"Command '{base_command}' not found in PATH"

            # Check if command is executable
            command_path = result.stdout.strip()
            if not os.access(command_path, os.X_OK):
                return False, f"Command '{command_path}' is not executable"

            return True, f"Command '{base_command}' is available"

        except subprocess.TimeoutExpired:
            return False, "CLI availability check timed out"
        except Exception as e:
            return False, f"CLI availability check failed: {e}"

    def execute_safe(
        self,
        command: str,
        config: Optional[ExecutionConfig] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """
        Execute command safely with comprehensive protection.

        Args:
            command: Command to execute
            config: Execution configuration
            progress_callback: Optional callback for progress updates

        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        execution_config = config or self.config

        # Generate execution ID
        execution_id = f"exec_{int(start_time)}_{len(self.execution_history)}"

        self.logger.info(f"Starting execution {execution_id}: {command}")

        # Validate command if enabled
        if execution_config.validate_command:
            is_valid, validation_message = self.validate_command(command)
            if not is_valid:
                return ExecutionResult(
                    command=command,
                    status=ExecutionStatus.FAILED,
                    return_code=1,
                    error_message=f"Command validation failed: {validation_message}",
                    execution_time=0.0,
                    timeout_seconds=execution_config.timeout_seconds,
                )

        # Sanitize command if enabled
        if execution_config.sanitize_input:
            command = self.sanitize_command(command)

        # Check CLI availability
        is_available, availability_message = self.check_cli_availability(command)
        if not is_available:
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.FAILED,
                return_code=1,
                error_message=f"CLI availability check failed: {availability_message}",
                execution_time=0.0,
                timeout_seconds=execution_config.timeout_seconds,
            )

        # Prepare execution environment
        env = os.environ.copy()
        env.update(execution_config.environment)

        # Execute command with timeout protection
        try:
            if execution_config.mode == ExecutionMode.SYNCHRONOUS:
                result = self._execute_synchronous(
                    command, execution_config, env, execution_id, progress_callback
                )
            elif execution_config.mode == ExecutionMode.ASYNCHRONOUS:
                result = self._execute_asynchronous(
                    command, execution_config, env, execution_id, progress_callback
                )
            elif execution_config.mode == ExecutionMode.BACKGROUND:
                result = self._execute_background(
                    command, execution_config, env, execution_id
                )
            else:
                raise ValueError(f"Unknown execution mode: {execution_config.mode}")

            # Update execution time
            result.execution_time = time.time() - start_time

            # Store in history
            self.execution_history.append(result)

            self.logger.info(
                f"Execution {execution_id} completed: {result.status.value}"
            )
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = ExecutionResult(
                command=command,
                status=ExecutionStatus.FAILED,
                return_code=1,
                error_message=str(e),
                execution_time=execution_time,
                timeout_seconds=execution_config.timeout_seconds,
            )

            self.execution_history.append(error_result)
            self.logger.error(f"Execution {execution_id} failed: {e}")
            return error_result

    def _execute_synchronous(
        self,
        command: str,
        config: ExecutionConfig,
        env: Dict[str, str],
        execution_id: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """Execute command synchronously with timeout protection."""
        try:
            # Prepare subprocess arguments
            if config.shell:
                process_args = command
            else:
                process_args = shlex.split(command)

            # Start subprocess
            process = subprocess.Popen(
                process_args,
                stdout=subprocess.PIPE if config.capture_output else None,
                stderr=subprocess.PIPE if config.capture_output else None,
                text=True,
                shell=config.shell,
                cwd=config.working_directory,
                env=env,
            )

            # Store active process
            self.active_processes[execution_id] = process

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=config.timeout_seconds)
                return_code = process.returncode
                status = (
                    ExecutionStatus.COMPLETED
                    if return_code == 0
                    else ExecutionStatus.FAILED
                )

            except subprocess.TimeoutExpired:
                # Terminate process on timeout
                process.terminate()
                try:
                    process.wait(timeout=5)  # Give it 5 seconds to terminate
                except subprocess.TimeoutExpired:
                    process.kill()  # Force kill if it doesn't terminate

                return ExecutionResult(
                    command=command,
                    status=ExecutionStatus.TIMEOUT,
                    return_code=124,  # Standard timeout exit code
                    error_message=f"Command timed out after {config.timeout_seconds} seconds",
                    timeout_seconds=config.timeout_seconds,
                )

            finally:
                # Remove from active processes
                self.active_processes.pop(execution_id, None)

            return ExecutionResult(
                command=command,
                status=status,
                return_code=return_code,
                stdout=stdout or "",
                stderr=stderr or "",
                timeout_seconds=config.timeout_seconds,
            )

        except Exception as e:
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.FAILED,
                return_code=1,
                error_message=f"Execution failed: {e}",
                timeout_seconds=config.timeout_seconds,
            )

    def _execute_asynchronous(
        self,
        command: str,
        config: ExecutionConfig,
        env: Dict[str, str],
        execution_id: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ExecutionResult:
        """Execute command asynchronously with progress monitoring."""
        # For now, delegate to synchronous execution
        # TODO: Implement true asynchronous execution with threading
        return self._execute_synchronous(
            command, config, env, execution_id, progress_callback
        )

    def _execute_background(
        self,
        command: str,
        config: ExecutionConfig,
        env: Dict[str, str],
        execution_id: str,
    ) -> ExecutionResult:
        """Execute command in background."""
        try:
            # Prepare subprocess arguments
            if config.shell:
                process_args = command
            else:
                process_args = shlex.split(command)

            # Start background process
            process = subprocess.Popen(
                process_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=config.shell,
                cwd=config.working_directory,
                env=env,
            )

            # Store active process
            self.active_processes[execution_id] = process

            return ExecutionResult(
                command=command,
                status=ExecutionStatus.RUNNING,
                return_code=0,
                metadata={"process_id": process.pid, "execution_id": execution_id},
                timeout_seconds=config.timeout_seconds,
            )

        except Exception as e:
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.FAILED,
                return_code=1,
                error_message=f"Background execution failed: {e}",
                timeout_seconds=config.timeout_seconds,
            )

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        if execution_id not in self.active_processes:
            return False

        process = self.active_processes[execution_id]
        try:
            process.terminate()
            process.wait(timeout=5)
            self.active_processes.pop(execution_id, None)
            self.logger.info(f"Execution {execution_id} cancelled")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            self.active_processes.pop(execution_id, None)
            self.logger.warning(f"Execution {execution_id} force killed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return False

    def get_execution_status(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get status of a specific execution."""
        for result in self.execution_history:
            if execution_id in result.metadata.get("execution_id", ""):
                return result
        return None

    def get_active_executions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active executions."""
        active_info = {}
        for execution_id, process in self.active_processes.items():
            active_info[execution_id] = {
                "process_id": process.pid,
                "status": process.poll(),
                "running": process.poll() is None,
            }
        return active_info

    def cleanup_active_processes(self):
        """Cleanup all active processes."""
        for execution_id in list(self.active_processes.keys()):
            self.cancel_execution(execution_id)

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions."""
        if not self.execution_history:
            return {"total_executions": 0, "message": "No executions recorded"}

        status_counts = {}
        for result in self.execution_history:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        total_time = sum(result.execution_time for result in self.execution_history)
        average_time = total_time / len(self.execution_history)

        return {
            "total_executions": len(self.execution_history),
            "active_executions": len(self.active_processes),
            "status_distribution": status_counts,
            "total_execution_time": total_time,
            "average_execution_time": average_time,
            "success_rate": status_counts.get("completed", 0)
            / len(self.execution_history)
            * 100,
        }

    def generate_execution_report(self) -> str:
        """Generate comprehensive execution report."""
        if not self.execution_history:
            return "No executions recorded - system is idle"

        report = []
        report.append("=" * 80)
        report.append("SAFE CLI EXECUTION REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        summary = self.get_execution_summary()
        report.append("EXECUTION SUMMARY:")
        report.append(f"  Total Executions: {summary['total_executions']}")
        report.append(f"  Active Executions: {summary['active_executions']}")
        report.append(f"  Success Rate: {summary['success_rate']:.1f}%")
        report.append(f"  Total Execution Time: {summary['total_execution_time']:.2f}s")
        report.append(
            f"  Average Execution Time: {summary['average_execution_time']:.2f}s"
        )
        report.append("")

        report.append("STATUS DISTRIBUTION:")
        for status, count in summary["status_distribution"].items():
            report.append(f"  {status}: {count}")
        report.append("")

        report.append("RECENT EXECUTIONS:")
        for result in self.execution_history[-10:]:  # Last 10 executions
            report.append(f"  Command: {result.command}")
            report.append(f"    Status: {result.status.value}")
            report.append(f"    Return Code: {result.return_code}")
            report.append(f"    Execution Time: {result.execution_time:.2f}s")
            if result.error_message:
                report.append(f"    Error: {result.error_message}")
            report.append("")

        return "\n".join(report)


def main():
    """Main function for testing the safe CLI executor."""
    executor = SafeCLIExecutor()

    print("Testing Safe CLI Executor...")

    # Test basic execution
    result = executor.execute_safe("echo 'Hello World'")
    print(f"Basic execution: {result.status.value}")

    # Test timeout protection
    timeout_config = ExecutionConfig(timeout_seconds=2)
    result = executor.execute_safe("sleep 5", timeout_config)
    print(f"Timeout protection: {result.status.value}")

    # Test command validation
    result = executor.execute_safe("rm -rf /", ExecutionConfig(validate_command=True))
    print(f"Command validation: {result.status.value}")

    # Test CLI availability
    result = executor.execute_safe("nonexistentcommand")
    print(f"CLI availability: {result.status.value}")

    # Generate report
    print("\n" + executor.generate_execution_report())


if __name__ == "__main__":
    main()
