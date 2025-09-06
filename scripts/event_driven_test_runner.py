#!/usr/bin/env python3
"""
Event-Driven Test Runner

Uses Kiro's watchdog facilities to automatically run tests when files change.
Implements systematic test monitoring with real-time feedback.
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Set, Dict, Any
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestEventHandler(FileSystemEventHandler):
    """
    Event handler for file system changes that triggers appropriate tests.
    
    Implements systematic test execution based on file change patterns.
    """
    
    def __init__(self, test_runner):
        self.test_runner = test_runner
        self.debounce_delay = 1.0  # seconds
        self.pending_tests = set()
        self.last_event_time = {}
    
    def on_modified(self, event):
        """Handle file modification events."""
        if isinstance(event, (FileModifiedEvent, FileCreatedEvent)):
            self._handle_file_change(event.src_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        if isinstance(event, FileCreatedEvent):
            self._handle_file_change(event.src_path)
    
    def _handle_file_change(self, file_path: str):
        """Handle file change with debouncing."""
        path = Path(file_path)
        
        # Only process Python files
        if path.suffix != '.py':
            return
        
        # Debounce rapid changes
        now = datetime.now()
        if file_path in self.last_event_time:
            if (now - self.last_event_time[file_path]).total_seconds() < self.debounce_delay:
                return
        
        self.last_event_time[file_path] = now
        
        # Determine what tests to run
        test_files = self._determine_test_files(path)
        
        if test_files:
            logger.info(f"📝 File changed: {path.name}")
            for test_file in test_files:
                self.pending_tests.add(test_file)
            
            # Schedule test execution
            asyncio.create_task(self._run_tests_after_delay())
    
    def _determine_test_files(self, changed_file: Path) -> Set[Path]:
        """Determine which test files to run based on changed file."""
        test_files = set()
        
        # If it's a test file, run it directly
        if 'test_' in changed_file.name or changed_file.name.startswith('test_'):
            test_files.add(changed_file)
        
        # If it's a source file, find corresponding tests
        elif changed_file.parts and 'src' in changed_file.parts:
            # Map source file to test file
            relative_path = changed_file.relative_to(Path('src'))
            
            # Look for corresponding test files
            test_patterns = [
                Path('tests') / 'unit' / relative_path.parent / f"test_{relative_path.stem}.py",
                Path('tests') / 'integration' / relative_path.parent / f"test_{relative_path.stem}.py",
                Path('tests') / f"test_{relative_path.stem}.py"
            ]
            
            for test_pattern in test_patterns:
                if test_pattern.exists():
                    test_files.add(test_pattern)
        
        return test_files
    
    async def _run_tests_after_delay(self):
        """Run pending tests after a short delay to batch changes."""
        await asyncio.sleep(self.debounce_delay)
        
        if self.pending_tests:
            tests_to_run = list(self.pending_tests)
            self.pending_tests.clear()
            
            await self.test_runner.run_tests(tests_to_run)


class SystematicTestRunner:
    """
    Systematic test runner with real-time monitoring and feedback.
    
    Integrates with Kiro's task status system for comprehensive monitoring.
    """
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_history = []
        self.current_task = None
    
    async def run_tests(self, test_files: list):
        """Run specified test files with systematic monitoring."""
        logger.info(f"🧪 Running {len(test_files)} test file(s)")
        
        for test_file in test_files:
            await self._run_single_test_file(test_file)
    
    async def _run_single_test_file(self, test_file: Path):
        """Run a single test file with monitoring."""
        logger.info(f"🔬 Testing: {test_file}")
        
        start_time = datetime.now()
        
        try:
            # Run pytest on the specific file
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(test_file), 
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            duration = datetime.now() - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ Tests passed: {test_file.name} ({duration.total_seconds():.2f}s)")
                self._log_test_success(test_file, duration, result.stdout)
            else:
                logger.error(f"❌ Tests failed: {test_file.name} ({duration.total_seconds():.2f}s)")
                self._log_test_failure(test_file, duration, result.stdout, result.stderr)
        
        except Exception as e:
            logger.error(f"💥 Test execution error: {test_file.name} - {e}")
            self._log_test_error(test_file, str(e))
    
    def _log_test_success(self, test_file: Path, duration, stdout: str):
        """Log successful test execution."""
        # Extract test count from pytest output
        lines = stdout.split('\n')
        summary_line = next((line for line in lines if 'passed' in line and '=' in line), '')
        
        self.test_history.append({
            'file': str(test_file),
            'status': 'passed',
            'duration': duration.total_seconds(),
            'timestamp': datetime.now(),
            'summary': summary_line.strip() if summary_line else 'Tests passed'
        })
    
    def _log_test_failure(self, test_file: Path, duration, stdout: str, stderr: str):
        """Log failed test execution."""
        # Extract failure info
        lines = stdout.split('\n') + stderr.split('\n')
        failure_lines = [line for line in lines if 'FAILED' in line or 'ERROR' in line]
        
        self.test_history.append({
            'file': str(test_file),
            'status': 'failed',
            'duration': duration.total_seconds(),
            'timestamp': datetime.now(),
            'failures': failure_lines[:5],  # First 5 failures
            'output': stdout[-500:] if stdout else stderr[-500:]  # Last 500 chars
        })
        
        # Print failure details
        print(f"\n🔍 Test Failure Details for {test_file.name}:")
        for failure in failure_lines[:3]:
            print(f"   {failure}")
        if len(failure_lines) > 3:
            print(f"   ... and {len(failure_lines) - 3} more failures")
    
    def _log_test_error(self, test_file: Path, error: str):
        """Log test execution error."""
        self.test_history.append({
            'file': str(test_file),
            'status': 'error',
            'timestamp': datetime.now(),
            'error': error
        })
    
    async def run_all_tests(self):
        """Run all tests in the project."""
        logger.info("🚀 Running all tests...")
        
        test_dirs = [
            Path('tests/unit'),
            Path('tests/integration'),
            Path('tests')
        ]
        
        all_test_files = []
        for test_dir in test_dirs:
            if test_dir.exists():
                all_test_files.extend(test_dir.rglob('test_*.py'))
        
        if all_test_files:
            await self.run_tests(all_test_files)
        else:
            logger.warning("No test files found")
    
    def print_test_summary(self):
        """Print summary of recent test results."""
        if not self.test_history:
            print("📊 No tests run yet")
            return
        
        recent_tests = self.test_history[-10:]  # Last 10 tests
        
        passed = sum(1 for t in recent_tests if t['status'] == 'passed')
        failed = sum(1 for t in recent_tests if t['status'] == 'failed')
        errors = sum(1 for t in recent_tests if t['status'] == 'error')
        
        print(f"\n📊 Test Summary (last {len(recent_tests)} runs):")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💥 Errors: {errors}")
        
        if recent_tests:
            avg_duration = sum(t.get('duration', 0) for t in recent_tests) / len(recent_tests)
            print(f"   ⏱️  Average duration: {avg_duration:.2f}s")


class EventDrivenTestMonitor:
    """
    Main event-driven test monitoring system.
    
    Watches for file changes and automatically runs appropriate tests.
    """
    
    def __init__(self):
        self.test_runner = SystematicTestRunner()
        self.observer = Observer()
        self.event_handler = TestEventHandler(self.test_runner)
        
        # Watch directories
        self.watch_paths = [
            Path('src'),
            Path('tests'),
            Path('.')  # For root-level files
        ]
    
    async def start_monitoring(self):
        """Start the event-driven test monitoring."""
        logger.info("🔍 Starting event-driven test monitoring...")
        
        # Set up file system watchers
        for watch_path in self.watch_paths:
            if watch_path.exists():
                self.observer.schedule(
                    self.event_handler, 
                    str(watch_path), 
                    recursive=True
                )
                logger.info(f"👀 Watching: {watch_path}")
        
        # Start the observer
        self.observer.start()
        
        # Run initial test suite
        logger.info("🧪 Running initial test suite...")
        await self.test_runner.run_all_tests()
        
        try:
            # Keep monitoring
            logger.info("✅ Event-driven test monitoring active. Press Ctrl+C to stop.")
            while True:
                await asyncio.sleep(5)
                
                # Print periodic summary
                self.test_runner.print_test_summary()
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping test monitoring...")
        finally:
            self.observer.stop()
            self.observer.join()


async def main():
    """Main entry point for event-driven test runner."""
    monitor = EventDrivenTestMonitor()
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())