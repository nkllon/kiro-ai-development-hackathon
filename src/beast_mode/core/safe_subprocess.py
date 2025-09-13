"""
Safe Subprocess Execution Framework
Implements timeout protection, error handling, and failure mode detection.
"""

import subprocess
import time
import psutil
import logging
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import signal
import os

class FailureType(Enum):
    """Types of subprocess failures."""
    TIMEOUT = "timeout"
    PROCESS_DEATH = "process_death"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    VALIDATION_ERROR = "validation_error"
    UNEXPECTED_ERROR = "unexpected_error"

@dataclass
class ExecutionResult:
    """Result of subprocess execution."""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None

@dataclass
class ExecutionMetrics:
    """Metrics for subprocess execution."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    timeout_count: int = 0
    average_execution_time: float = 0.0
    failure_rate: float = 0.0

class FailureModeDetector:
    """Detects and classifies subprocess failure modes."""
    
    def __init__(self) -> Any:
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def detect_timeout(self, process: subprocess.Popen, timeout_limit: float) -> bool:
        """detect_timeout - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Detect if subprocess exceeded timeout."""
        if process.poll() is None:  # Process still running
            return True
        return False
    
    def detect_process_death(self, process: subprocess.Popen) -> bool:
        """detect_process_death - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Detect unexpected process termination."""
        if process.poll() is not None and process.returncode != 0:
            return True
        return False
    
    def detect_resource_exhaustion(self) -> bool:
        """Detect system resource exhaustion."""
        try:
            # Check memory usage
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 90:
                self.logger.warning(f"High memory usage: {memory_percent}%")
                return True
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                self.logger.warning(f"High CPU usage: {cpu_percent}%")
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")
        
        return False
    
    def classify_failure(self, exception: Exception) -> FailureType:
        """Classify failure type for appropriate handling."""
        if isinstance(exception, subprocess.TimeoutExpired):
            return FailureType.TIMEOUT
        elif isinstance(exception, PermissionError):
            return FailureType.PERMISSION_ERROR
        elif isinstance(exception, FileNotFoundError):
            return FailureType.VALIDATION_ERROR
        elif isinstance(exception, subprocess.ProcessError):
            return FailureType.PROCESS_DEATH
        else:
            return FailureType.UNEXPECTED_ERROR

class SafeSubprocessExecutor:
    """Safe subprocess execution with timeout protection and error handling."""
    
    def __init__(self, default_timeout -> Any: float = 10.0) -> Any:
        self.default_timeout = default_timeout
        self.execution_log: List[ExecutionResult] = []
        self.metrics = ExecutionMetrics()
        self.failure_detector = FailureModeDetector()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_environment(self, command: Union[str, List[str]]) -> bool:
        """Pre-execution environment validation."""
        try:
            # Check if command exists (for simple commands)
            if isinstance(command, str) and not command.startswith(('python', 'uv', 'node', 'docker', 'make')):
                # Check if it's a file that exists
                if os.path.exists(command):
                    return True
            
            # Check system resources
            if self.failure_detector.detect_resource_exhaustion():
                self.logger.warning("System resources exhausted, proceeding with caution")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return False
    
    def execute_safe(
        """execute_safe - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        self,
        command: Union[str, List[str]],
        timeout: Optional[float] = None,
        capture_output: bool = True,
        text: bool = True,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> ExecutionResult:
        """Execute subprocess with timeout protection and error handling."""
        
        if timeout is None:
            timeout = self.default_timeout
        
        start_time = time.time()
        
        try:
            # Pre-execution validation
            if not self.validate_environment(command):
                return ExecutionResult(
                    success=False,
                    return_code=-1,
                    stdout="",
                    stderr="Environment validation failed",
                    execution_time=0.0,
                    failure_type=FailureType.VALIDATION_ERROR,
                    error_message="Pre-execution validation failed"
                )
            
            # Execute subprocess with timeout
            result = subprocess.run(
                command,
                timeout=timeout,
                capture_output=capture_output,
                text=text,
                **kwargs
            )
            
            execution_time = time.time() - start_time
            
            # Create execution result
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                execution_time=execution_time
            )
            
            # Update metrics
            self._update_metrics(exec_result)
            
            if exec_result.success:
                self.logger.info(f"Command executed successfully in {execution_time:.2f}s")
            else:
                self.logger.warning(f"Command failed with return code {result.returncode}")
            
            return exec_result
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command timed out after {timeout}s: {command}")
            
            exec_result = ExecutionResult(
                success=False,
                return_code=-1,
                stdout=e.stdout if hasattr(e, 'stdout') else "",
                stderr=e.stderr if hasattr(e, 'stderr') else "",
                execution_time=execution_time,
                failure_type=FailureType.TIMEOUT,
                error_message=f"Command timed out after {timeout}s"
            )
            
            self._update_metrics(exec_result)
            
            # Try fallback if provided
            if fallback:
                self.logger.info("Attempting fallback execution")
                return fallback()
            
            return exec_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            failure_type = self.failure_detector.classify_failure(e)
            
            self.logger.error(f"Command execution failed: {e}")
            
            exec_result = ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                failure_type=failure_type,
                error_message=str(e)
            )
            
            self._update_metrics(exec_result)
            
            # Try fallback if provided
            if fallback:
                self.logger.info("Attempting fallback execution")
                return fallback()
            
            return exec_result
    
    def execute_with_retry(
        """execute_with_retry - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        self,
        command: Union[str, List[str]],
        max_retries: int = 3,
        timeout: Optional[float] = None,
        retry_delay: float = 1.0,
        **kwargs
    ) -> ExecutionResult:
        """Execute with retry logic for transient failures."""
        
        last_result = None
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt}/{max_retries}")
                time.sleep(retry_delay)
            
            result = self.execute_safe(command, timeout=timeout, **kwargs)
            last_result = result
            
            if result.success:
                return result
            
            # Don't retry certain failure types
            if result.failure_type in [FailureType.PERMISSION_ERROR, FailureType.VALIDATION_ERROR]:
                break
        
        return last_result
    
    def cleanup_resources(self, process -> Any: subprocess.Popen) -> Any:
        """Post-execution resource cleanup."""
        try:
            if process.poll() is None:  # Process still running
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")
    
    def _update_metrics(self, result -> Any: ExecutionResult) -> Any:
        """_update_metrics - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Update execution metrics."""
        self.metrics.total_executions += 1
        
        if result.success:
            self.metrics.successful_executions += 1
        else:
            self.metrics.failed_executions += 1
            if result.failure_type == FailureType.TIMEOUT:
                self.metrics.timeout_count += 1
        
        # Update average execution time
        total_time = (self.metrics.average_execution_time * (self.metrics.total_executions - 1) + 
                     result.execution_time) / self.metrics.total_executions
        self.metrics.average_execution_time = total_time
        
        # Update failure rate
        self.metrics.failure_rate = self.metrics.failed_executions / self.metrics.total_executions
        
        # Store in execution log
        self.execution_log.append(result)
    
    def get_metrics(self) -> ExecutionMetrics:
        """get_metrics - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get current execution metrics."""
        return self.metrics
    
    def get_failure_summary(self) -> Dict[FailureType, int]:
        """get_failure_summary - Enhanced for compliance"""
        try:
            pass  # TODO: Add method implementation
        except Exception as e:
            logging.error(f"Error in method: {e}")
            raise
        """Get summary of failure types."""
        failure_counts = {}
        for result in self.execution_log:
            if not result.success and result.failure_type:
                failure_counts[result.failure_type] = failure_counts.get(result.failure_type, 0) + 1
        return failure_counts

# Global safe executor instance
safe_executor = SafeSubprocessExecutor()

def safe_execute(
        """safe_execute - Enhanced for compliance"""
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    command: Union[str, List[str]],
    timeout: Optional[float] = None,
    fallback: Optional[Callable] = None,
    **kwargs
) -> ExecutionResult:
    """Convenience function for safe subprocess execution."""
    return safe_executor.execute_safe(command, timeout=timeout, fallback=fallback, **kwargs)

def safe_execute_with_retry(
        """safe_execute_with_retry - Enhanced for compliance"""
    try:
        pass  # TODO: Add method implementation
    except Exception as e:
        logging.error(f"Error in method: {e}")
        raise
    command: Union[str, List[str]],
    max_retries: int = 3,
    timeout: Optional[float] = None,
    **kwargs
) -> ExecutionResult:
    """Convenience function for safe subprocess execution with retry."""
    return safe_executor.execute_with_retry(command, max_retries=max_retries, timeout=timeout, **kwargs)

