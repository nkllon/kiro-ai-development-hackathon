"""
Go-Python Bridge for Packer Systo

This module provides the bridge between Python and Go components,
enabling systematic integration of Go core functionality with Python APIs.
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import ctypes
import ctypes.util
import structlog

from ..core.exceptions import BridgeError, GoCoreBridgeError
from ..core.models import (
    AnalysisResult,
    DelusionPattern,
    ValidationReport,
    RecoveryResult,
    BuildResult,
)

logger = structlog.get_logger(__name__)


class GoCoreBridge:
    """
    Bridge to Go core functionality using FFI (Foreign Function Interface).
    
    This class provides systematic integration with the Go core toolkit,
    enabling Python applications to leverage Go-based delusion detection,
    recovery engines, and validation agents.
    """
    
    def __init__(self, go_binary_path: Optional[str] = None, use_ffi: bool = True):
        """
        Initialize the Go core bridge.
        
        Args:
            go_binary_path: Path to the Go binary (optional)
            use_ffi: Whether to use FFI or subprocess communication
        """
        self.go_binary_path = go_binary_path or "packer-systo"
        self.use_ffi = use_ffi
        self.ffi_lib = None
        self._initialized = False
        
        if self.use_ffi:
            self._initialize_ffi()
        
        logger.info(
            "Go core bridge initialized",
            binary_path=self.go_binary_path,
            use_ffi=self.use_ffi,
            initialized=self._initialized
        )
    
    def _initialize_ffi(self):
        """Initialize FFI connection to Go shared library."""
        try:
            # Try to load the Go shared library
            lib_path = self._find_go_library()
            if lib_path:
                self.ffi_lib = ctypes.CDLL(lib_path)
                self._setup_ffi_functions()
                self._initialized = True
                logger.info("FFI bridge initialized successfully", lib_path=lib_path)
            else:
                logger.warning("Go shared library not found, falling back to subprocess")
                self.use_ffi = False
        except Exception as e:
            logger.warning("FFI initialization failed, falling back to subprocess", error=str(e))
            self.use_ffi = False
    
    def _find_go_library(self) -> Optional[str]:
        """Find the Go shared library."""
        # Common library names and paths
        lib_names = [
            "libpacker-systo-go.so",
            "libpacker-systo-go.dylib", 
            "packer-systo-go.dll",
        ]
        
        search_paths = [
            Path.cwd(),
            Path.cwd() / "lib",
            Path("/usr/local/lib"),
            Path("/usr/lib"),
        ]
        
        for path in search_paths:
            for lib_name in lib_names:
                lib_path = path / lib_name
                if lib_path.exists():
                    return str(lib_path)
        
        return None
    
    def _setup_ffi_functions(self):
        """Setup FFI function signatures."""
        if not self.ffi_lib:
            return
        
        # Define C structure for bridge results
        class BridgeResult(ctypes.Structure):
            _fields_ = [
                ("data", ctypes.c_char_p),
                ("length", ctypes.c_int),
                ("error_code", ctypes.c_int),
                ("error_message", ctypes.c_char_p),
            ]
        
        # Setup function signatures
        self.ffi_lib.analyze_configuration.argtypes = [ctypes.c_char_p]
        self.ffi_lib.analyze_configuration.restype = ctypes.POINTER(BridgeResult)
        
        self.ffi_lib.detect_patterns.argtypes = [ctypes.c_char_p]
        self.ffi_lib.detect_patterns.restype = ctypes.POINTER(BridgeResult)
        
        self.ffi_lib.diagnose_failure.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.ffi_lib.diagnose_failure.restype = ctypes.POINTER(BridgeResult)
        
        self.ffi_lib.validate_configuration.argtypes = [ctypes.c_char_p]
        self.ffi_lib.validate_configuration.restype = ctypes.POINTER(BridgeResult)
        
        self.ffi_lib.free_result.argtypes = [ctypes.POINTER(BridgeResult)]
        self.ffi_lib.free_result.restype = None
        
        self.BridgeResult = BridgeResult
    
    def _call_ffi_function(self, func_name: str, *args) -> Dict[str, Any]:
        """Call an FFI function and handle the result."""
        if not self.ffi_lib:
            raise BridgeError("FFI library not initialized")
        
        func = getattr(self.ffi_lib, func_name)
        
        # Convert string arguments to bytes
        byte_args = []
        for arg in args:
            if isinstance(arg, str):
                byte_args.append(arg.encode('utf-8'))
            else:
                byte_args.append(arg)
        
        # Call the function
        result_ptr = func(*byte_args)
        
        try:
            # Extract result data
            result = result_ptr.contents
            
            if result.error_code != 0:
                error_msg = result.error_message.decode('utf-8') if result.error_message else "Unknown error"
                raise GoCoreBridgeError(f"Go function {func_name} failed: {error_msg}")
            
            if result.data:
                data_str = result.data.decode('utf-8')
                return json.loads(data_str)
            else:
                return {}
        
        finally:
            # Free the result
            self.ffi_lib.free_result(result_ptr)
    
    async def _call_subprocess(self, command: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Call Go binary via subprocess."""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate(
                input=input_data.encode('utf-8') if input_data else None
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise GoCoreBridgeError(f"Go subprocess failed: {error_msg}")
            
            result_str = stdout.decode('utf-8')
            return json.loads(result_str) if result_str else {}
        
        except json.JSONDecodeError as e:
            raise BridgeError(f"Failed to parse Go response: {e}")
        except Exception as e:
            raise BridgeError(f"Subprocess communication failed: {e}")
    
    async def analyze_configuration(self, config: Dict[str, Any]) -> AnalysisResult:
        """
        Analyze Packer configuration for delusions and issues.
        
        Args:
            config: Packer configuration dictionary
            
        Returns:
            AnalysisResult with delusion patterns and recommendations
        """
        config_json = json.dumps(config)
        
        logger.info("Analyzing configuration", config_size=len(config_json))
        
        if self.use_ffi and self.ffi_lib:
            result_data = self._call_ffi_function("analyze_configuration", config_json)
        else:
            command = [self.go_binary_path, "analyze", "--json", "--stdin"]
            result_data = await self._call_subprocess(command, config_json)
        
        # Convert result to AnalysisResult model
        return AnalysisResult.from_dict(result_data)
    
    async def detect_patterns(self, hcl_content: str) -> List[DelusionPattern]:
        """
        Detect delusion patterns in HCL content.
        
        Args:
            hcl_content: Raw HCL configuration content
            
        Returns:
            List of detected delusion patterns
        """
        logger.info("Detecting patterns", content_size=len(hcl_content))
        
        if self.use_ffi and self.ffi_lib:
            result_data = self._call_ffi_function("detect_patterns", hcl_content)
        else:
            command = [self.go_binary_path, "detect", "--json", "--stdin"]
            result_data = await self._call_subprocess(command, hcl_content)
        
        # Convert result to list of DelusionPattern models
        patterns = []
        for pattern_data in result_data.get("patterns", []):
            patterns.append(DelusionPattern.from_dict(pattern_data))
        
        return patterns
    
    async def diagnose_failure(self, build_log: str, config: Dict[str, Any]) -> RecoveryResult:
        """
        Diagnose build failure and generate recovery plan.
        
        Args:
            build_log: Build failure log content
            config: Packer configuration dictionary
            
        Returns:
            RecoveryResult with diagnosis and recovery plan
        """
        config_json = json.dumps(config)
        
        logger.info("Diagnosing failure", log_size=len(build_log), config_size=len(config_json))
        
        if self.use_ffi and self.ffi_lib:
            result_data = self._call_ffi_function("diagnose_failure", build_log, config_json)
        else:
            # Create temporary files for subprocess communication
            with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as log_file:
                log_file.write(build_log)
                log_path = log_file.name
            
            try:
                command = [self.go_binary_path, "diagnose", "--json", log_path, "--config-stdin"]
                result_data = await self._call_subprocess(command, config_json)
            finally:
                Path(log_path).unlink(missing_ok=True)
        
        # Convert result to RecoveryResult model
        return RecoveryResult.from_dict(result_data)
    
    async def validate_configuration(self, config: Dict[str, Any]) -> ValidationReport:
        """
        Validate Packer configuration with multi-dimensional analysis.
        
        Args:
            config: Packer configuration dictionary
            
        Returns:
            ValidationReport with multi-dimensional validation results
        """
        config_json = json.dumps(config)
        
        logger.info("Validating configuration", config_size=len(config_json))
        
        if self.use_ffi and self.ffi_lib:
            result_data = self._call_ffi_function("validate_configuration", config_json)
        else:
            command = [self.go_binary_path, "validate", "--json", "--stdin"]
            result_data = await self._call_subprocess(command, config_json)
        
        # Convert result to ValidationReport model
        return ValidationReport.from_dict(result_data)
    
    async def get_bridge_info(self) -> Dict[str, Any]:
        """
        Get information about the Go bridge.
        
        Returns:
            Dictionary with bridge information and capabilities
        """
        if self.use_ffi and self.ffi_lib:
            return self._call_ffi_function("get_bridge_info")
        else:
            command = [self.go_binary_path, "version", "--json"]
            return await self._call_subprocess(command)
    
    async def health_check(self) -> bool:
        """
        Perform health check on the Go bridge.
        
        Returns:
            True if bridge is healthy, False otherwise
        """
        try:
            info = await self.get_bridge_info()
            return info.get("status") == "ready"
        except Exception as e:
            logger.warning("Bridge health check failed", error=str(e))
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Cleanup resources if needed
        pass


class SubprocessBridge:
    """
    Alternative bridge implementation using subprocess communication.
    
    This provides a fallback when FFI is not available or preferred.
    """
    
    def __init__(self, go_binary_path: str = "packer-systo"):
        """Initialize subprocess bridge."""
        self.go_binary_path = go_binary_path
        logger.info("Subprocess bridge initialized", binary_path=go_binary_path)
    
    async def execute_command(self, args: List[str], input_data: Optional[str] = None) -> Dict[str, Any]:
        """Execute Go command via subprocess."""
        command = [self.go_binary_path] + args
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate(
                input=input_data.encode('utf-8') if input_data else None
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise GoCoreBridgeError(f"Command failed: {' '.join(command)}: {error_msg}")
            
            result_str = stdout.decode('utf-8')
            return json.loads(result_str) if result_str else {}
        
        except json.JSONDecodeError as e:
            raise BridgeError(f"Failed to parse command output: {e}")
        except Exception as e:
            raise BridgeError(f"Command execution failed: {e}")


# Factory function for creating bridges
def create_bridge(
    go_binary_path: Optional[str] = None,
    prefer_ffi: bool = True,
    **kwargs
) -> GoCoreBridge:
    """
    Create a Go core bridge with automatic fallback.
    
    Args:
        go_binary_path: Path to Go binary
        prefer_ffi: Whether to prefer FFI over subprocess
        **kwargs: Additional bridge configuration
        
    Returns:
        Configured GoCoreBridge instance
    """
    return GoCoreBridge(
        go_binary_path=go_binary_path,
        use_ffi=prefer_ffi,
        **kwargs
    )