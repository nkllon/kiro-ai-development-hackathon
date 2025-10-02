#!/usr/bin/env python3
"""
Makefile Performance Optimizer
==============================

Performance optimization engine for Makefile operations.
Implements parallel execution, caching, and progress indicators.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Performance optimization for Makefile system operations
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import pickle

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CacheStrategy(Enum):
    """Cache strategies for operations."""
    NONE = "none"
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"


class ExecutionMode(Enum):
    """Execution modes for operations."""
    SEQUENTIAL = "sequential"
    THREADED = "threaded"
    PROCESS = "process"
    ADAPTIVE = "adaptive"


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    operation: str
    start_time: float
    end_time: float
    duration: float
    cache_hit: bool = False
    parallel_workers: int = 1
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


@dataclass
class CacheEntry:
    """Cache entry for operation results."""
    key: str
    value: Any
    timestamp: float
    ttl: float
    size_bytes: int = 0
    access_count: int = 0
    last_access: float = 0


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    max_parallel_workers: int = 4
    cache_strategy: CacheStrategy = CacheStrategy.HYBRID
    cache_ttl: float = 3600  # 1 hour
    max_cache_size: int = 100 * 1024 * 1024  # 100MB
    enable_progress_indicators: bool = True
    execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE
    timeout: float = 300  # 5 minutes


class MakefilePerformanceOptimizer(ReflectiveModule):
    """
    ⚡ MAKEFILE PERFORMANCE OPTIMIZER ⚡
    
    Advanced performance optimization engine for Makefile operations.
    Provides parallel execution, intelligent caching, and progress tracking.
    """
    
    def __init__(self, repository_root: str = ".", config: OptimizationConfig = None):
        super().__init__()
        self.module_id = "makefile_performance_optimizer"
        self.repository_root = Path(repository_root)
        self.config = config or OptimizationConfig()
        
        # Cache management
        self.cache_dir = self.repository_root / ".make-tasks" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size": 0
        }
        
        # Performance tracking
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, float] = {}
        
        # Progress tracking
        self.progress_callbacks: Dict[str, Callable] = {}
        
        # Load existing cache
        self._load_disk_cache()
    
    def optimize_target_execution(self, target: str, commands: List[str], 
                                dependencies: List[str] = None) -> Dict[str, Any]:
        """Optimize execution of a Makefile target."""
        self._logger.info(f"⚡ Optimizing target execution: {target}")
        
        start_time = time.time()
        self.active_operations[target] = start_time
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(target, commands, dependencies)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                self._logger.info(f"📦 Cache hit for target: {target}")
                self.cache_stats["hits"] += 1
                
                metrics = PerformanceMetrics(
                    operation=target,
                    start_time=start_time,
                    end_time=time.time(),
                    duration=time.time() - start_time,
                    cache_hit=True
                )
                self.metrics.append(metrics)
                
                return {
                    "target": target,
                    "result": cached_result,
                    "cached": True,
                    "duration": metrics.duration,
                    "metrics": metrics
                }
            
            self.cache_stats["misses"] += 1
            
            # Determine optimal execution strategy
            execution_strategy = self._determine_execution_strategy(commands, dependencies)
            
            # Execute with optimization
            if execution_strategy == ExecutionMode.SEQUENTIAL:
                result = self._execute_sequential(target, commands)
            elif execution_strategy == ExecutionMode.THREADED:
                result = self._execute_threaded(target, commands)
            elif execution_strategy == ExecutionMode.PROCESS:
                result = self._execute_process_parallel(target, commands)
            else:  # ADAPTIVE
                result = self._execute_adaptive(target, commands, dependencies)
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Record metrics
            end_time = time.time()
            metrics = PerformanceMetrics(
                operation=target,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
                cache_hit=False,
                parallel_workers=self._get_worker_count(execution_strategy)
            )
            self.metrics.append(metrics)
            
            return {
                "target": target,
                "result": result,
                "cached": False,
                "duration": metrics.duration,
                "execution_strategy": execution_strategy.value,
                "metrics": metrics
            }
            
        finally:
            if target in self.active_operations:
                del self.active_operations[target]
    
    def _generate_cache_key(self, target: str, commands: List[str], 
                          dependencies: List[str] = None) -> str:
        """Generate cache key for target execution."""
        # Include target, commands, and file modification times
        key_data = {
            "target": target,
            "commands": commands,
            "dependencies": dependencies or [],
            "timestamp": time.time()
        }
        
        # Add file modification times for dependencies
        if dependencies:
            for dep in dependencies:
                dep_path = self.repository_root / dep
                if dep_path.exists():
                    key_data[f"mtime_{dep}"] = dep_path.stat().st_mtime
        
        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def _get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available and valid."""
        # Check memory cache first
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if time.time() - entry.timestamp < entry.ttl:
                entry.access_count += 1
                entry.last_access = time.time()
                return entry.value
            else:
                # Expired, remove from memory cache
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry_data = pickle.load(f)
                
                if time.time() - entry_data["timestamp"] < self.config.cache_ttl:
                    # Valid cache entry, load into memory
                    entry = CacheEntry(
                        key=cache_key,
                        value=entry_data["value"],
                        timestamp=entry_data["timestamp"],
                        ttl=self.config.cache_ttl,
                        access_count=1,
                        last_access=time.time()
                    )
                    self.memory_cache[cache_key] = entry
                    return entry.value
                else:
                    # Expired, remove file
                    cache_file.unlink()
            except Exception as e:
                self._logger.warning(f"Failed to load cache entry {cache_key}: {e}")
                if cache_file.exists():
                    cache_file.unlink()
        
        return None
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache operation result."""
        if self.config.cache_strategy == CacheStrategy.NONE:
            return
        
        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            value=result,
            timestamp=time.time(),
            ttl=self.config.cache_ttl,
            access_count=1,
            last_access=time.time()
        )
        
        # Estimate size
        try:
            entry.size_bytes = len(pickle.dumps(result))
        except:
            entry.size_bytes = sys.getsizeof(result)
        
        # Memory cache
        if self.config.cache_strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
            self._add_to_memory_cache(entry)
        
        # Disk cache
        if self.config.cache_strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
            self._add_to_disk_cache(entry)
    
    def _add_to_memory_cache(self, entry: CacheEntry):
        """Add entry to memory cache with eviction."""
        # Check if we need to evict
        while (self.cache_stats["total_size"] + entry.size_bytes > self.config.max_cache_size 
               and self.memory_cache):
            self._evict_lru_entry()
        
        self.memory_cache[entry.key] = entry
        self.cache_stats["total_size"] += entry.size_bytes
    
    def _add_to_disk_cache(self, entry: CacheEntry):
        """Add entry to disk cache."""
        cache_file = self.cache_dir / f"{entry.key}.cache"
        
        try:
            entry_data = {
                "value": entry.value,
                "timestamp": entry.timestamp,
                "ttl": entry.ttl
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(entry_data, f)
                
        except Exception as e:
            self._logger.warning(f"Failed to cache to disk: {e}")
    
    def _evict_lru_entry(self):
        """Evict least recently used cache entry."""
        if not self.memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(self.memory_cache.keys(), 
                     key=lambda k: self.memory_cache[k].last_access)
        
        entry = self.memory_cache[lru_key]
        del self.memory_cache[lru_key]
        self.cache_stats["total_size"] -= entry.size_bytes
        self.cache_stats["evictions"] += 1
    
    def _determine_execution_strategy(self, commands: List[str], 
                                    dependencies: List[str] = None) -> ExecutionMode:
        """Determine optimal execution strategy."""
        if self.config.execution_mode != ExecutionMode.ADAPTIVE:
            return self.config.execution_mode
        
        # Analyze commands to determine best strategy
        command_text = " ".join(commands).lower()
        
        # I/O intensive operations benefit from threading
        io_keywords = ["curl", "wget", "download", "upload", "sync", "copy", "rsync"]
        if any(keyword in command_text for keyword in io_keywords):
            return ExecutionMode.THREADED
        
        # CPU intensive operations benefit from process parallelism
        cpu_keywords = ["compile", "build", "test", "lint", "format", "analyze"]
        if any(keyword in command_text for keyword in cpu_keywords):
            return ExecutionMode.PROCESS
        
        # Simple operations can run sequentially
        simple_keywords = ["echo", "print", "mkdir", "touch", "ls", "cat"]
        if any(keyword in command_text for keyword in simple_keywords):
            return ExecutionMode.SEQUENTIAL
        
        # Default to threaded for mixed workloads
        return ExecutionMode.THREADED
    
    def _execute_sequential(self, target: str, commands: List[str]) -> Dict[str, Any]:
        """Execute commands sequentially."""
        results = []
        
        for i, command in enumerate(commands):
            if self.config.enable_progress_indicators:
                self._update_progress(target, i, len(commands))
            
            result = self._execute_single_command(command)
            results.append(result)
            
            if result["returncode"] != 0:
                break
        
        return {
            "commands_executed": len(results),
            "results": results,
            "success": all(r["returncode"] == 0 for r in results)
        }
    
    def _execute_threaded(self, target: str, commands: List[str]) -> Dict[str, Any]:
        """Execute commands using thread pool."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_parallel_workers) as executor:
            # Submit all commands
            future_to_command = {
                executor.submit(self._execute_single_command, cmd): cmd 
                for cmd in commands
            }
            
            # Collect results
            for i, future in enumerate(as_completed(future_to_command)):
                if self.config.enable_progress_indicators:
                    self._update_progress(target, i + 1, len(commands))
                
                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "command": future_to_command[future],
                        "returncode": -1,
                        "stdout": "",
                        "stderr": str(e),
                        "duration": 0
                    })
        
        return {
            "commands_executed": len(results),
            "results": results,
            "success": all(r["returncode"] == 0 for r in results)
        }
    
    def _execute_process_parallel(self, target: str, commands: List[str]) -> Dict[str, Any]:
        """Execute commands using process pool."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.max_parallel_workers) as executor:
            # Submit all commands
            future_to_command = {
                executor.submit(self._execute_single_command_process, cmd): cmd 
                for cmd in commands
            }
            
            # Collect results
            for i, future in enumerate(as_completed(future_to_command)):
                if self.config.enable_progress_indicators:
                    self._update_progress(target, i + 1, len(commands))
                
                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "command": future_to_command[future],
                        "returncode": -1,
                        "stdout": "",
                        "stderr": str(e),
                        "duration": 0
                    })
        
        return {
            "commands_executed": len(results),
            "results": results,
            "success": all(r["returncode"] == 0 for r in results)
        }
    
    def _execute_adaptive(self, target: str, commands: List[str], 
                         dependencies: List[str] = None) -> Dict[str, Any]:
        """Execute commands using adaptive strategy."""
        # Group commands by type
        io_commands = []
        cpu_commands = []
        simple_commands = []
        
        for command in commands:
            cmd_lower = command.lower()
            if any(kw in cmd_lower for kw in ["curl", "wget", "download", "upload"]):
                io_commands.append(command)
            elif any(kw in cmd_lower for kw in ["compile", "build", "test", "lint"]):
                cpu_commands.append(command)
            else:
                simple_commands.append(command)
        
        all_results = []
        
        # Execute simple commands sequentially first
        if simple_commands:
            simple_result = self._execute_sequential(f"{target}_simple", simple_commands)
            all_results.extend(simple_result["results"])
        
        # Execute I/O commands with threading
        if io_commands:
            io_result = self._execute_threaded(f"{target}_io", io_commands)
            all_results.extend(io_result["results"])
        
        # Execute CPU commands with process parallelism
        if cpu_commands:
            cpu_result = self._execute_process_parallel(f"{target}_cpu", cpu_commands)
            all_results.extend(cpu_result["results"])
        
        return {
            "commands_executed": len(all_results),
            "results": all_results,
            "success": all(r["returncode"] == 0 for r in all_results),
            "strategy_breakdown": {
                "simple": len(simple_commands),
                "io": len(io_commands),
                "cpu": len(cpu_commands)
            }
        }
    
    def _execute_single_command(self, command: str) -> Dict[str, Any]:
        """Execute a single command and return result."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=self.repository_root
            )
            
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": time.time() - start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {self.config.timeout} seconds",
                "duration": time.time() - start_time
            }
        except Exception as e:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time
            }
    
    @staticmethod
    def _execute_single_command_process(command: str) -> Dict[str, Any]:
        """Execute a single command in a separate process."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            return {
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": time.time() - start_time
            }
            
        except Exception as e:
            return {
                "command": command,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time
            }
    
    def _get_worker_count(self, execution_mode: ExecutionMode) -> int:
        """Get worker count for execution mode."""
        if execution_mode == ExecutionMode.SEQUENTIAL:
            return 1
        else:
            return self.config.max_parallel_workers
    
    def _update_progress(self, target: str, current: int, total: int):
        """Update progress indicator."""
        if not self.config.enable_progress_indicators:
            return
        
        progress = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r⚡ {target}: |{bar}| {progress:.1f}% ({current}/{total})", end='', flush=True)
        
        if current == total:
            print()  # New line when complete
    
    def _load_disk_cache(self):
        """Load existing disk cache entries."""
        if not self.cache_dir.exists():
            return
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    entry_data = pickle.load(f)
                
                # Check if still valid
                if time.time() - entry_data["timestamp"] < self.config.cache_ttl:
                    cache_key = cache_file.stem
                    # Don't load into memory immediately, just validate
                    continue
                else:
                    # Expired, remove
                    cache_file.unlink()
                    
            except Exception:
                # Corrupted cache file, remove
                cache_file.unlink()
    
    def clear_cache(self):
        """Clear all cache entries."""
        self.memory_cache.clear()
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0, "total_size": 0}
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        self._logger.info("🗑️ Cache cleared")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.metrics:
            return {"message": "No performance data available"}
        
        total_operations = len(self.metrics)
        cached_operations = len([m for m in self.metrics if m.cache_hit])
        avg_duration = sum(m.duration for m in self.metrics) / total_operations
        
        return {
            "timestamp": self._get_current_timestamp(),
            "summary": {
                "total_operations": total_operations,
                "cached_operations": cached_operations,
                "cache_hit_rate": cached_operations / total_operations,
                "average_duration": avg_duration,
                "total_time_saved": sum(m.duration for m in self.metrics if m.cache_hit)
            },
            "cache_stats": self.cache_stats,
            "recent_operations": [
                {
                    "operation": m.operation,
                    "duration": m.duration,
                    "cached": m.cache_hit,
                    "workers": m.parallel_workers
                }
                for m in self.metrics[-10:]  # Last 10 operations
            ]
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile Performance Optimizer")
    parser.add_argument("target", help="Target to optimize")
    parser.add_argument("--commands", nargs="*", help="Commands to execute")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--workers", type=int, default=4, help="Max parallel workers")
    parser.add_argument("--cache", choices=["none", "memory", "disk", "hybrid"], 
                       default="hybrid", help="Cache strategy")
    parser.add_argument("--mode", choices=["sequential", "threaded", "process", "adaptive"],
                       default="adaptive", help="Execution mode")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache before execution")
    parser.add_argument("--report", action="store_true", help="Show performance report")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create optimizer
    config = OptimizationConfig(
        max_parallel_workers=args.workers,
        cache_strategy=CacheStrategy(args.cache),
        execution_mode=ExecutionMode(args.mode)
    )
    
    optimizer = MakefilePerformanceOptimizer(args.root, config)
    
    # Clear cache if requested
    if args.clear_cache:
        optimizer.clear_cache()
    
    # Show report if requested
    if args.report:
        report = optimizer.get_performance_report()
        print(json.dumps(report, indent=2))
        return
    
    # Execute target optimization
    if args.commands:
        result = optimizer.optimize_target_execution(args.target, args.commands)
        
        print(f"\n⚡ PERFORMANCE OPTIMIZATION COMPLETE")
        print(f"Target: {result['target']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Cached: {'✅ YES' if result['cached'] else '❌ NO'}")
        print(f"Strategy: {result.get('execution_strategy', 'N/A')}")
        print(f"Success: {'✅ YES' if result['result']['success'] else '❌ NO'}")
        
        if args.verbose:
            print(f"\nDetailed Results:")
            print(json.dumps(result, indent=2, default=str))
    else:
        print("No commands provided for optimization")


if __name__ == "__main__":
    main()