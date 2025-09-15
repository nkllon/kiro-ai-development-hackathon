#!/usr/bin/env python3
"""
Concurrent Processing Engine
===========================

Advanced concurrent processing engine for the Beast Mode framework.
Provides parallel execution, task scheduling, and resource management
for optimal performance and throughput.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Concurrent processing for performance optimization
"""

import sys
import os
import time
import asyncio
import logging
import threading
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import queue
import weakref
from pathlib import Path


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ProcessingMode(Enum):
    """Processing modes for different workloads."""

    CPU_INTENSIVE = "cpu_intensive"
    IO_INTENSIVE = "io_intensive"
    MIXED = "mixed"
    PARALLEL = "parallel"


@dataclass
class Task:
    """Task definition for concurrent processing."""

    id: str
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingMetrics:
    """Processing performance metrics."""

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    average_execution_time: float = 0.0
    throughput_tasks_per_second: float = 0.0
    active_workers: int = 0
    queue_size: int = 0
    resource_utilization: float = 0.0


class ConcurrentProcessingEngine:
    """
    Advanced concurrent processing engine.

    Provides parallel execution, intelligent task scheduling, and resource
    management for optimal performance across different workload types.
    """

    def __init__(
        self,
        max_workers: int = 4,
        processing_mode: ProcessingMode = ProcessingMode.MIXED,
        enable_async: bool = True,
    ):
        """Initialize the concurrent processing engine."""
        self.max_workers = max_workers
        self.processing_mode = processing_mode
        self.enable_async = enable_async

        self.logger = self._setup_logging()

        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []

        # Execution pools
        self.thread_pool = None
        self.process_pool = None
        self.async_loop = None
        self.async_tasks: Dict[str, asyncio.Task] = {}

        # Metrics and monitoring
        self.metrics = ProcessingMetrics()
        self.start_time = datetime.now()

        # Threading and synchronization
        self.shutdown_event = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        self.metrics_lock = threading.Lock()

        # Initialize execution pools
        self._initialize_execution_pools()

        # Start worker threads
        self._start_worker_threads()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for concurrent processing."""
        logger = logging.getLogger("concurrent_processing_engine")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _initialize_execution_pools(self):
        """Initialize execution pools based on processing mode."""
        if self.processing_mode == ProcessingMode.CPU_INTENSIVE:
            # Use process pool for CPU-intensive tasks
            self.process_pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=max(1, self.max_workers // 2)
            )
            self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=max(1, self.max_workers // 4)
            )
        elif self.processing_mode == ProcessingMode.IO_INTENSIVE:
            # Use thread pool for I/O-intensive tasks
            self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers * 2
            )
        else:  # MIXED or PARALLEL
            # Use both pools
            self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )
            self.process_pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=max(1, self.max_workers // 2)
            )

        self.logger.info(
            f"Initialized execution pools for {self.processing_mode.value} mode"
        )

    def _start_worker_threads(self):
        """Start worker threads for task processing."""
        for i in range(self.max_workers):
            worker_thread = threading.Thread(
                target=self._worker_loop, name=f"Worker-{i}", daemon=True
            )
            worker_thread.start()
            self.worker_threads.append(worker_thread)

        self.logger.info(f"Started {self.max_workers} worker threads")

    def _worker_loop(self):
        """Worker thread loop for processing tasks."""
        while not self.shutdown_event.is_set():
            try:
                # Get next task from queue
                priority, task_id = self.task_queue.get(timeout=1)

                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    self._execute_task(task)

                self.task_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Worker thread error: {e}")

    def submit_task(
        self,
        task_id: str,
        name: str,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout_seconds: Optional[int] = None,
        max_retries: int = 3,
        dependencies: List[str] = None,
    ) -> str:
        """
        Submit a task for concurrent processing.

        Returns:
            Task ID for tracking
        """
        task = Task(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            dependencies=dependencies or [],
        )

        # Store task
        self.tasks[task_id] = task

        # Add to priority queue
        priority_value = task.priority.value
        self.task_queue.put((priority_value, task_id))

        # Update metrics
        with self.metrics_lock:
            self.metrics.total_tasks += 1
            self.metrics.queue_size = self.task_queue.qsize()

        self.logger.info(f"Submitted task: {task_id} ({name})")
        return task_id

    def _execute_task(self, task: Task):
        """Execute a single task."""
        task.started_at = datetime.now()
        task.status = TaskStatus.RUNNING

        # Update metrics
        with self.metrics_lock:
            self.metrics.active_workers += 1
            self.metrics.queue_size = self.task_queue.qsize()

        try:
            # Check dependencies
            if not self._check_dependencies(task):
                task.status = TaskStatus.PENDING
                self.task_queue.put((task.priority.value, task.id))
                return

            # Execute task based on processing mode
            if self.processing_mode == ProcessingMode.CPU_INTENSIVE:
                result = self._execute_cpu_intensive_task(task)
            elif self.processing_mode == ProcessingMode.IO_INTENSIVE:
                result = self._execute_io_intensive_task(task)
            else:  # MIXED or PARALLEL
                result = self._execute_mixed_task(task)

            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

            # Update metrics
            execution_time = (task.completed_at - task.started_at).total_seconds()
            with self.metrics_lock:
                self.metrics.completed_tasks += 1
                self.metrics.average_execution_time = (
                    self.metrics.average_execution_time
                    * (self.metrics.completed_tasks - 1)
                    + execution_time
                ) / self.metrics.completed_tasks
                self._update_throughput()

            self.completed_tasks.append(task)
            self.logger.info(f"Task completed: {task.id} in {execution_time:.2f}s")

        except Exception as e:
            # Task failed
            task.error = e
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                self.task_queue.put((task.priority.value, task.id))
                self.logger.warning(
                    f"Task failed, retrying ({task.retry_count}/{task.max_retries}): {task.id}"
                )
            else:
                # Max retries exceeded
                with self.metrics_lock:
                    self.metrics.failed_tasks += 1

                self.failed_tasks.append(task)
                self.logger.error(
                    f"Task failed after {task.max_retries} retries: {task.id} - {e}"
                )

        finally:
            # Update metrics
            with self.metrics_lock:
                self.metrics.active_workers -= 1

    def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False

            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def _execute_cpu_intensive_task(self, task: Task) -> Any:
        """Execute CPU-intensive task using process pool."""
        if self.process_pool:
            future = self.process_pool.submit(task.function, *task.args, **task.kwargs)

            if task.timeout_seconds:
                return future.result(timeout=task.timeout_seconds)
            else:
                return future.result()
        else:
            # Fallback to thread pool
            return self._execute_io_intensive_task(task)

    def _execute_io_intensive_task(self, task: Task) -> Any:
        """Execute I/O-intensive task using thread pool."""
        if self.thread_pool:
            future = self.thread_pool.submit(task.function, *task.args, **task.kwargs)

            if task.timeout_seconds:
                return future.result(timeout=task.timeout_seconds)
            else:
                return future.result()
        else:
            # Fallback to direct execution
            return task.function(*task.args, **task.kwargs)

    def _execute_mixed_task(self, task: Task) -> Any:
        """Execute mixed workload task."""
        # Determine if task is CPU or I/O intensive
        if self._is_cpu_intensive_task(task):
            return self._execute_cpu_intensive_task(task)
        else:
            return self._execute_io_intensive_task(task)

    def _is_cpu_intensive_task(self, task: Task) -> bool:
        """Determine if task is CPU-intensive."""
        # Simple heuristic based on task name and metadata
        cpu_indicators = ["compute", "calculate", "process", "analyze", "transform"]
        io_indicators = ["read", "write", "fetch", "download", "upload", "network"]

        task_name_lower = task.name.lower()

        cpu_score = sum(
            1 for indicator in cpu_indicators if indicator in task_name_lower
        )
        io_score = sum(1 for indicator in io_indicators if indicator in task_name_lower)

        return cpu_score > io_score

    def _update_throughput(self):
        """Update throughput metrics."""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 0:
            self.metrics.throughput_tasks_per_second = (
                self.metrics.completed_tasks / elapsed_time
            )

    async def submit_async_task(
        self,
        task_id: str,
        name: str,
        async_function: Callable[[], Awaitable[Any]],
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout_seconds: Optional[int] = None,
    ) -> str:
        """
        Submit an async task for concurrent processing.

        Returns:
            Task ID for tracking
        """
        if not self.enable_async:
            raise RuntimeError("Async processing is disabled")

        # Create async task
        if not self.async_loop:
            self.async_loop = asyncio.get_event_loop()

        async_task = self.async_loop.create_task(
            self._execute_async_task(task_id, name, async_function, timeout_seconds)
        )

        self.async_tasks[task_id] = async_task

        self.logger.info(f"Submitted async task: {task_id} ({name})")
        return task_id

    async def _execute_async_task(
        self,
        task_id: str,
        name: str,
        async_function: Callable[[], Awaitable[Any]],
        timeout_seconds: Optional[int] = None,
    ) -> Any:
        """Execute an async task."""
        try:
            if timeout_seconds:
                return await asyncio.wait_for(async_function(), timeout=timeout_seconds)
            else:
                return await async_function()
        except Exception as e:
            self.logger.error(f"Async task failed: {task_id} - {e}")
            raise

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a task to complete and return its result."""
        start_time = time.time()

        while True:
            if task_id in self.tasks:
                task = self.tasks[task_id]

                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise task.error or Exception(f"Task {task_id} failed")
                elif task.status == TaskStatus.CANCELLED:
                    raise Exception(f"Task {task_id} was cancelled")

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")

            time.sleep(0.1)

    async def wait_for_async_task(
        self, task_id: str, timeout: Optional[float] = None
    ) -> Any:
        """Wait for an async task to complete and return its result."""
        if task_id not in self.async_tasks:
            raise ValueError(f"Async task {task_id} not found")

        async_task = self.async_tasks[task_id]

        try:
            if timeout:
                return await asyncio.wait_for(async_task, timeout=timeout)
            else:
                return await async_task
        finally:
            # Clean up
            if task_id in self.async_tasks:
                del self.async_tasks[task_id]

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]

            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()

                with self.metrics_lock:
                    self.metrics.cancelled_tasks += 1

                self.logger.info(f"Cancelled task: {task_id}")
                return True

        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None

    def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.COMPLETED:
                return task.result
            else:
                raise Exception(
                    f"Task {task_id} is not completed (status: {task.status.value})"
                )
        raise ValueError(f"Task {task_id} not found")

    def wait_for_all_tasks(self, timeout: Optional[float] = None) -> bool:
        """Wait for all pending tasks to complete."""
        start_time = time.time()

        while True:
            # Check if all tasks are completed
            pending_tasks = [
                task
                for task in self.tasks.values()
                if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
            ]

            if not pending_tasks:
                return True

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                return False

            time.sleep(0.1)

    def get_processing_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics."""
        with self.metrics_lock:
            return ProcessingMetrics(
                total_tasks=self.metrics.total_tasks,
                completed_tasks=self.metrics.completed_tasks,
                failed_tasks=self.metrics.failed_tasks,
                cancelled_tasks=self.metrics.cancelled_tasks,
                average_execution_time=self.metrics.average_execution_time,
                throughput_tasks_per_second=self.metrics.throughput_tasks_per_second,
                active_workers=self.metrics.active_workers,
                queue_size=self.metrics.queue_size,
                resource_utilization=self.metrics.resource_utilization,
            )

    def generate_processing_report(self) -> str:
        """Generate comprehensive processing report."""
        report = []
        report.append("=" * 80)
        report.append("CONCURRENT PROCESSING ENGINE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        metrics = self.get_processing_metrics()

        report.append("PROCESSING CONFIGURATION:")
        report.append(f"  Max Workers: {self.max_workers}")
        report.append(f"  Processing Mode: {self.processing_mode.value}")
        report.append(
            f"  Async Processing: {'Enabled' if self.enable_async else 'Disabled'}"
        )
        report.append("")

        report.append("TASK STATISTICS:")
        report.append(f"  Total Tasks: {metrics.total_tasks}")
        report.append(f"  Completed Tasks: {metrics.completed_tasks}")
        report.append(f"  Failed Tasks: {metrics.failed_tasks}")
        report.append(f"  Cancelled Tasks: {metrics.cancelled_tasks}")
        report.append(
            f"  Success Rate: {(metrics.completed_tasks / metrics.total_tasks * 100) if metrics.total_tasks > 0 else 0:.1f}%"
        )
        report.append("")

        report.append("PERFORMANCE METRICS:")
        report.append(
            f"  Average Execution Time: {metrics.average_execution_time:.2f}s"
        )
        report.append(
            f"  Throughput: {metrics.throughput_tasks_per_second:.2f} tasks/sec"
        )
        report.append(f"  Active Workers: {metrics.active_workers}")
        report.append(f"  Queue Size: {metrics.queue_size}")
        report.append("")

        # Task status breakdown
        status_counts = {}
        for task in self.tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        if status_counts:
            report.append("TASK STATUS BREAKDOWN:")
            for status, count in status_counts.items():
                report.append(f"  {status.title()}: {count}")
            report.append("")

        return "\n".join(report)

    def shutdown(self, wait: bool = True):
        """Shutdown the processing engine."""
        self.logger.info("Shutting down concurrent processing engine...")

        # Signal shutdown
        self.shutdown_event.set()

        # Cancel pending tasks
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED

        # Wait for workers to finish
        if wait:
            for worker_thread in self.worker_threads:
                worker_thread.join(timeout=5)

        # Shutdown execution pools
        if self.thread_pool:
            self.thread_pool.shutdown(wait=wait)

        if self.process_pool:
            self.process_pool.shutdown(wait=wait)

        # Cancel async tasks
        if self.async_tasks:
            for async_task in self.async_tasks.values():
                async_task.cancel()

        self.logger.info("Concurrent processing engine shutdown complete")


def main():
    """Main function for testing the concurrent processing engine."""
    engine = ConcurrentProcessingEngine(
        max_workers=4, processing_mode=ProcessingMode.MIXED
    )

    print("Testing Concurrent Processing Engine...")

    # Test CPU-intensive task
    def cpu_task(n):
        time.sleep(0.1)  # Simulate work
        return sum(range(n))

    # Test I/O-intensive task
    def io_task(filename):
        time.sleep(0.1)  # Simulate I/O
        return f"Processed {filename}"

    # Submit tasks
    task_ids = []
    for i in range(10):
        if i % 2 == 0:
            task_id = engine.submit_task(
                f"cpu_task_{i}",
                f"CPU Task {i}",
                cpu_task,
                args=(1000,),
                priority=TaskPriority.HIGH if i < 5 else TaskPriority.MEDIUM,
            )
        else:
            task_id = engine.submit_task(
                f"io_task_{i}",
                f"I/O Task {i}",
                io_task,
                args=(f"file_{i}.txt",),
                priority=TaskPriority.MEDIUM,
            )
        task_ids.append(task_id)

    # Wait for completion
    print("Waiting for tasks to complete...")
    engine.wait_for_all_tasks(timeout=30)

    # Get results
    print("\nTask Results:")
    for task_id in task_ids:
        try:
            result = engine.get_task_result(task_id)
            print(f"  {task_id}: {result}")
        except Exception as e:
            print(f"  {task_id}: Error - {e}")

    # Generate report
    print("\n" + engine.generate_processing_report())

    # Shutdown
    engine.shutdown()


if __name__ == "__main__":
    main()
