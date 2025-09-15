#!/usr/bin/env python3
"""
Beast Mode Debug System - Full Compliance Spread
==============================================

Enhanced debugging system with comprehensive trace information capture.
Ensures all trace information is preserved at every stopping point.
"""

import sys
import os
import traceback
import json
import inspect
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
import functools
import logging
import signal
import atexit


class BeastModeDebugSystem:
    """Beast Mode Debug System with full compliance spread"""
    
    def __init__(self):
        self.debug_session_id = f"beast_mode_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.trace_data = {}
        self.call_stack = []
        self.debug_log = []
        self.setup_comprehensive_logging()
        self.setup_signal_handlers()
        self.setup_exit_handlers()
        self.register_debug_hooks()
        
        print("🚀 BEAST MODE DEBUG SYSTEM ACTIVATED")
        print("=" * 60)
        print(f"Debug Session ID: {self.debug_session_id}")
        print(f"Full Compliance Spread: ENABLED")
        print(f"Comprehensive Trace Capture: ACTIVE")
        print("=" * 60)
    
    def setup_comprehensive_logging(self):
        """Setup comprehensive logging system"""
        
        # Create debug log file
        self.debug_log_file = f"{self.debug_session_id}_debug.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.debug_log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('BeastModeDebug')
        self.logger.info("Beast Mode Debug System initialized")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for comprehensive trace capture"""
        
        def signal_handler(signum, frame):
            self.logger.critical(f"Signal {signum} received - capturing full trace")
            self.capture_comprehensive_trace(f"signal_{signum}")
            sys.exit(1)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGABRT, signal_handler)
        
        self.logger.info("Signal handlers registered for comprehensive trace capture")
    
    def setup_exit_handlers(self):
        """Setup exit handlers for automatic trace capture"""
        
        def exit_handler():
            self.logger.info("Exit handler triggered - capturing final trace")
            self.capture_comprehensive_trace("exit_handler")
        
        atexit.register(exit_handler)
        self.logger.info("Exit handlers registered")
    
    def register_debug_hooks(self):
        """Register debug hooks for function tracing"""
        
        # Hook into sys.excepthook for exception tracing
        original_excepthook = sys.excepthook
        
        def enhanced_excepthook(exc_type, exc_value, exc_traceback):
            self.logger.critical("Exception occurred - capturing comprehensive trace")
            self.capture_comprehensive_trace("exception", exc_type, exc_value, exc_traceback)
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = enhanced_excepthook
        
        # Hook into threading for thread tracing
        original_threading_excepthook = threading.excepthook
        
        def enhanced_threading_excepthook(args):
            self.logger.critical("Threading exception occurred - capturing trace")
            self.capture_comprehensive_trace("threading_exception", args)
            if original_threading_excepthook:
                original_threading_excepthook(args)
        
        threading.excepthook = enhanced_threading_excepthook
        
        self.logger.info("Debug hooks registered for comprehensive tracing")
    
    def trace_function(self, func: Callable) -> Callable:
        """Decorator to trace function calls"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Capture entry trace
            entry_trace = {
                'timestamp': datetime.now().isoformat(),
                'function': func_name,
                'event': 'entry',
                'args': str(args)[:500],  # Truncate for safety
                'kwargs': str(kwargs)[:500],
                'caller': self._get_caller_info()
            }
            
            self.call_stack.append(entry_trace)
            self.logger.debug(f"ENTER: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                
                # Capture exit trace
                exit_trace = {
                    'timestamp': datetime.now().isoformat(),
                    'function': func_name,
                    'event': 'exit',
                    'result_type': type(result).__name__,
                    'result_size': len(str(result)) if hasattr(result, '__len__') else 'unknown'
                }
                
                self.call_stack.append(exit_trace)
                self.logger.debug(f"EXIT: {func_name}")
                
                return result
                
            except Exception as e:
                # Capture exception trace
                exception_trace = {
                    'timestamp': datetime.now().isoformat(),
                    'function': func_name,
                    'event': 'exception',
                    'exception_type': type(e).__name__,
                    'exception_message': str(e),
                    'traceback': traceback.format_exc()
                }
                
                self.call_stack.append(exception_trace)
                self.logger.error(f"EXCEPTION in {func_name}: {e}")
                
                raise
        
        return wrapper
    
    def capture_comprehensive_trace(self, trigger: str, exc_type=None, exc_value=None, exc_traceback=None):
        """Capture comprehensive trace information"""
        
        trace_id = f"trace_{trigger}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.logger.info(f"Capturing comprehensive trace: {trace_id}")
        
        trace_data = {
            'trace_id': trace_id,
            'trigger': trigger,
            'timestamp': datetime.now().isoformat(),
            'debug_session_id': self.debug_session_id,
            'system_info': self._capture_system_info(),
            'python_info': self._capture_python_info(),
            'call_stack': self.call_stack.copy(),
            'debug_log': self.debug_log.copy(),
            'thread_info': self._capture_thread_info(),
            'memory_info': self._capture_memory_info(),
            'file_system_info': self._capture_filesystem_info(),
            'exception_info': self._capture_exception_info(exc_type, exc_value, exc_traceback),
            'module_info': self._capture_module_info(),
            'environment_info': self._capture_environment_info()
        }
        
        # Save trace data
        trace_file = f"{trace_id}.json"
        try:
            with open(trace_file, 'w') as f:
                json.dump(trace_data, f, indent=2, default=str)
            
            self.logger.info(f"Trace data saved to: {trace_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save trace data: {e}")
            # Fallback: save to debug log
            self.logger.error(f"TRACE DATA: {json.dumps(trace_data, default=str)[:1000]}...")
        
        return trace_file
    
    def _capture_system_info(self) -> Dict[str, Any]:
        """Capture system information"""
        
        try:
            import platform
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'hostname': platform.node(),
                'python_implementation': platform.python_implementation(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_python_info(self) -> Dict[str, Any]:
        """Capture Python environment information"""
        
        return {
            'executable': sys.executable,
            'path': sys.path,
            'version_info': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
                'micro': sys.version_info.micro,
                'releaselevel': sys.version_info.releaselevel,
                'serial': sys.version_info.serial
            },
            'platform': sys.platform,
            'argv': sys.argv,
            'modules_loaded': list(sys.modules.keys()),
            'recursion_limit': sys.getrecursionlimit(),
            'thread_info': threading.current_thread().name if threading.current_thread() else 'unknown'
        }
    
    def _capture_thread_info(self) -> Dict[str, Any]:
        """Capture thread information"""
        
        try:
            thread_info = {}
            for thread in threading.enumerate():
                thread_info[thread.name] = {
                    'ident': thread.ident,
                    'is_alive': thread.is_alive(),
                    'daemon': thread.daemon
                }
            return thread_info
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_memory_info(self) -> Dict[str, Any]:
        """Capture memory information"""
        
        try:
            import psutil
            process = psutil.Process()
            return {
                'memory_info': process.memory_info()._asdict(),
                'memory_percent': process.memory_percent(),
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'create_time': process.create_time()
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_filesystem_info(self) -> Dict[str, Any]:
        """Capture filesystem information"""
        
        try:
            current_dir = Path.cwd()
            return {
                'current_directory': str(current_dir),
                'files_in_current_dir': [f.name for f in current_dir.iterdir() if f.is_file()],
                'directories_in_current_dir': [d.name for d in current_dir.iterdir() if d.is_dir()],
                'disk_usage': self._get_disk_usage()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(Path.cwd())
            return {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': (used / total) * 100
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _capture_exception_info(self, exc_type, exc_value, exc_traceback) -> Dict[str, Any]:
        """Capture exception information"""
        
        if exc_type is None:
            return {'no_exception': True}
        
        return {
            'exception_type': str(exc_type),
            'exception_value': str(exc_value),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback),
            'current_exception': traceback.format_exc()
        }
    
    def _capture_module_info(self) -> Dict[str, Any]:
        """Capture module information"""
        
        module_info = {}
        for name, module in sys.modules.items():
            try:
                module_info[name] = {
                    'file': getattr(module, '__file__', None),
                    'package': getattr(module, '__package__', None),
                    'version': getattr(module, '__version__', None)
                }
            except Exception as e:
                module_info[name] = {'error': str(e)}
        
        return module_info
    
    def _capture_environment_info(self) -> Dict[str, Any]:
        """Capture environment information"""
        
        return {
            'environment_variables': dict(os.environ),
            'working_directory': os.getcwd(),
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
            'home': os.getenv('HOME', os.getenv('USERPROFILE', 'unknown'))
        }
    
    def _get_caller_info(self) -> Dict[str, Any]:
        """Get caller information"""
        
        try:
            frame = inspect.currentframe().f_back.f_back
            return {
                'filename': frame.f_code.co_filename,
                'function': frame.f_code.co_name,
                'line_number': frame.f_lineno
            }
        except Exception as e:
            return {'error': str(e)}
    
    def log_debug_event(self, event: str, data: Any = None):
        """Log debug event"""
        
        debug_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'data': str(data)[:1000] if data else None
        }
        
        self.debug_log.append(debug_entry)
        self.logger.debug(f"DEBUG EVENT: {event}")
    
    def create_emergency_dump(self, reason: str = "emergency"):
        """Create emergency dump with full trace information"""
        
        self.logger.critical(f"Creating emergency dump: {reason}")
        
        dump_file = self.capture_comprehensive_trace(f"emergency_{reason}")
        
        self.logger.critical(f"Emergency dump created: {dump_file}")
        return dump_file
    
    def stop_and_dump(self, reason: str = "stop_requested"):
        """Stop and dump all trace information"""
        
        print("\n" + "="*60)
        print("🛑 BEAST MODE DEBUG SYSTEM - STOP AND DUMP")
        print("="*60)
        print(f"Reason: {reason}")
        print(f"Debug Session: {self.debug_session_id}")
        print("="*60)
        
        self.logger.critical(f"Stop and dump requested: {reason}")
        
        # Create comprehensive dump
        dump_file = self.create_emergency_dump(reason)
        
        # Print summary
        print(f"\n📊 TRACE CAPTURE SUMMARY:")
        print(f"   Debug Session ID: {self.debug_session_id}")
        print(f"   Dump File: {dump_file}")
        print(f"   Call Stack Entries: {len(self.call_stack)}")
        print(f"   Debug Log Entries: {len(self.debug_log)}")
        print(f"   Debug Log File: {self.debug_log_file}")
        
        print(f"\n💾 ALL TRACE INFORMATION PRESERVED")
        print(f"   Comprehensive trace capture completed")
        print(f"   Full compliance spread achieved")
        print(f"   Recovery information available")
        
        return dump_file


# Global debug system instance
debug_system = None

def initialize_beast_mode_debug():
    """Initialize Beast Mode Debug System"""
    global debug_system
    debug_system = BeastModeDebugSystem()
    return debug_system

def stop_and_dump_trace(reason: str = "stop_requested"):
    """Stop and dump all trace information"""
    if debug_system:
        return debug_system.stop_and_dump(reason)
    else:
        print("⚠️ Debug system not initialized - creating emergency dump")
        # Create minimal emergency dump
        emergency_dump = f"emergency_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(emergency_dump, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'reason': reason,
                    'error': 'Debug system not initialized',
                    'traceback': traceback.format_exc()
                }, f, indent=2)
            return emergency_dump
        except Exception as e:
            print(f"Failed to create emergency dump: {e}")
            return None


# Decorator for automatic function tracing
def beast_mode_trace(func):
    """Decorator to trace functions in Beast Mode"""
    if debug_system:
        return debug_system.trace_function(func)
    else:
        return func


if __name__ == "__main__":
    # Initialize Beast Mode Debug System
    debug_system = initialize_beast_mode_debug()
    
    print("\n🚀 BEAST MODE DEBUG SYSTEM READY")
    print("   Full Compliance Spread: ACTIVE")
    print("   Comprehensive Trace Capture: ENABLED")
    print("   Automatic Exit Handling: CONFIGURED")
    print("\n   Use stop_and_dump_trace() to capture all trace information")
    print("   All stopping points will automatically capture comprehensive traces")
    
    # Test the system
    debug_system.log_debug_event("system_initialized", "Beast Mode Debug System ready")
    
    print(f"\n✅ Beast Mode Debug System operational")
    print(f"   Session ID: {debug_system.debug_session_id}")
    print(f"   Ready for comprehensive trace capture")

