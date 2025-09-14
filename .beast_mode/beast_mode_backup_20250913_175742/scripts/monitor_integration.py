#!/usr/bin/env python3
"""
Beast Mode Monitor Integration

Hooks the resource monitor into existing Beast Mode systems
to automatically track token usage and costs
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import Beast Mode modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from beast_mode_resource_monitor import BeastModeResourceMonitor


class MonitorIntegration:
    """
    Integration layer that connects resource monitoring
    to existing Beast Mode systems
    """
    
    def __init__(self):
        self.monitor = BeastModeResourceMonitor()
        self.integration_active = False
    
    async def start_integrated_monitoring(self):
        """Start monitoring with integration hooks"""
        print("🔗 Starting Beast Mode Integrated Monitoring...")
        
        # Start the resource monitor in the background
        monitor_task = asyncio.create_task(self.monitor.start_monitoring())
        
        # Start integration hooks
        integration_task = asyncio.create_task(self._run_integration_hooks())
        
        try:
            await asyncio.gather(monitor_task, integration_task)
        except KeyboardInterrupt:
            print("\n🛑 Integrated monitoring stopped")
    
    async def _run_integration_hooks(self):
        """Run integration hooks to capture real usage"""
        self.integration_active = True
        
        while self.integration_active:
            # Check for Kiro API usage (mock for now)
            await self._check_kiro_usage()
            
            # Check for test execution
            await self._check_test_execution()
            
            # Check for file operations
            await self._check_file_operations()
            
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def _check_kiro_usage(self):
        """Check for Kiro IDE API usage"""
        # In a real implementation, this would hook into Kiro's API calls
        # For now, simulate some usage
        
        # Look for .kiro directory activity as a proxy
        kiro_dir = Path('.kiro')
        if kiro_dir.exists():
            # Count recent file modifications
            recent_files = []
            for file_path in kiro_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        mtime = file_path.stat().st_mtime
                        if (asyncio.get_event_loop().time() - mtime) < 60:  # Modified in last minute
                            recent_files.append(file_path)
                    except OSError:
                        continue
            
            if recent_files:
                # Simulate token usage for file operations
                for file_path in recent_files[:3]:  # Limit to avoid spam
                    # Estimate tokens based on file size
                    try:
                        file_size = file_path.stat().st_size
                        estimated_tokens = min(file_size // 4, 2000)  # Rough estimate
                        
                        if estimated_tokens > 100:  # Only log significant usage
                            self.monitor.log_token_usage(
                                provider="kiro",
                                model="kiro-assistant",
                                input_tokens=estimated_tokens,
                                output_tokens=estimated_tokens // 2,
                                request_id=f"file_op_{file_path.name}"
                            )
                            self.monitor.log_api_call()
                    except OSError:
                        continue
    
    async def _check_test_execution(self):
        """Check for test execution and log as API usage"""
        # Look for pytest cache or test output
        test_indicators = [
            Path('.pytest_cache'),
            Path('__pycache__'),
            Path('tests/__pycache__')
        ]
        
        for indicator in test_indicators:
            if indicator.exists():
                try:
                    mtime = indicator.stat().st_mtime
                    if (asyncio.get_event_loop().time() - mtime) < 30:  # Modified in last 30 seconds
                        # Log test execution as resource usage
                        self.monitor.log_token_usage(
                            provider="pytest",
                            model="test-execution",
                            input_tokens=500,
                            output_tokens=200,
                            request_id=f"test_run_{int(asyncio.get_event_loop().time())}"
                        )
                        self.monitor.log_api_call()
                        break
                except OSError:
                    continue
    
    async def _check_file_operations(self):
        """Check for significant file operations"""
        # Look for recently modified Python files
        python_files = list(Path('.').rglob('*.py'))
        
        recent_modifications = 0
        for py_file in python_files:
            try:
                mtime = py_file.stat().st_mtime
                if (asyncio.get_event_loop().time() - mtime) < 60:  # Modified in last minute
                    recent_modifications += 1
            except OSError:
                continue
        
        if recent_modifications > 5:  # Significant activity
            # Log as development activity
            self.monitor.log_token_usage(
                provider="development",
                model="code-generation",
                input_tokens=1000,
                output_tokens=500,
                request_id=f"dev_activity_{int(asyncio.get_event_loop().time())}"
            )
            self.monitor.log_api_call()


async def main():
    """Main entry point for integrated monitoring"""
    integration = MonitorIntegration()
    await integration.start_integrated_monitoring()


if __name__ == "__main__":
    asyncio.run(main())