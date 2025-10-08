#!/usr/bin/env python3
"""
Documentation Orchestrator - Phase 5 Task 5.1

Coordinates all discovery, analysis, and generation components into unified workflows
with CMS integration, change detection, and automated validation.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import time
from dataclasses import dataclass, asdict

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation workflows."""
    cms_url: str = "http://localhost:8055"
    fallback_config_path: str = "config/documentation_config.json"
    refresh_interval_hours: int = 1
    staleness_threshold_hours: int = 24
    accuracy_threshold: float = 0.95
    enable_real_time_updates: bool = True
    enable_websocket_triggers: bool = True
    max_concurrent_generations: int = 5


@dataclass
class DocumentationTask:
    """Represents a documentation generation task."""
    task_id: str
    task_type: str  # 'discovery', 'analysis', 'generation', 'validation'
    component: str
    priority: int = 1
    created_at: datetime = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class DocumentationOrchestrator(ReflectiveModule):
    """
    Orchestrates all documentation generation workflows with CMS integration,
    change detection, and automated validation.
    """
    
    def __init__(self, config: Optional[DocumentationConfig] = None):
        super().__init__()
        self.config = config or DocumentationConfig()
        self.task_queue: List[DocumentationTask] = []
        self.running_tasks: Dict[str, DocumentationTask] = {}
        self.completed_tasks: Dict[str, DocumentationTask] = {}
        self.cms_available = False
        self.last_cms_check = None
        self.file_hashes: Dict[str, str] = {}
        self.last_generation_time = None
        
        # Initialize metrics
        self.metrics.update({
            'tasks_queued': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'cms_connection_status': 0,
            'last_generation_duration': 0,
            'accuracy_score': 0.0,
            'staleness_alerts': 0
        })
        
        self.logger.info("DocumentationOrchestrator initialized", 
                        extra={"correlation_id": self.generate_correlation_id()})
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the orchestrator with CMS connection and configuration."""
        correlation_id = self.generate_correlation_id()
        
        try:
            # Check CMS availability
            await self._check_cms_availability()
            
            # Load configuration
            config_data = await self._load_configuration()
            
            # Initialize file monitoring
            await self._initialize_file_monitoring()
            
            # Start background tasks
            asyncio.create_task(self._background_orchestration_loop())
            asyncio.create_task(self._staleness_monitoring_loop())
            
            self.logger.info("DocumentationOrchestrator initialized successfully",
                           extra={"correlation_id": correlation_id})
            
            return {
                "status": "initialized",
                "cms_available": self.cms_available,
                "config": asdict(self.config),
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DocumentationOrchestrator: {e}",
                            extra={"correlation_id": correlation_id})
            return {
                "status": "failed",
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _check_cms_availability(self) -> bool:
        """Check if Directus CMS is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.cms_url}/server/ping", 
                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        text = await response.text()
                        self.cms_available = "pong" in text.lower()
                    else:
                        self.cms_available = False
            
            self.metrics['cms_connection_status'] = 1 if self.cms_available else 0
            self.last_cms_check = datetime.utcnow()
            
            self.logger.info(f"CMS availability check: {'available' if self.cms_available else 'unavailable'}")
            return self.cms_available
            
        except Exception as e:
            self.cms_available = False
            self.metrics['cms_connection_status'] = 0
            self.logger.warning(f"CMS availability check failed: {e}")
            return False
    
    async def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from CMS or fallback to file-based config."""
        if self.cms_available:
            try:
                return await self._load_cms_configuration()
            except Exception as e:
                self.logger.warning(f"Failed to load CMS configuration: {e}")
        
        # Fallback to file-based configuration
        return await self._load_file_configuration()
    
    async def _load_cms_configuration(self) -> Dict[str, Any]:
        """Load configuration from Directus CMS."""
        try:
            async with aiohttp.ClientSession() as session:
                # Get documentation configuration from CMS
                async with session.get(
                    f"{self.config.cms_url}/items/documentation_config",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info("Configuration loaded from CMS")
                        return data.get('data', {})
                    else:
                        raise Exception(f"CMS returned status {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to load CMS configuration: {e}")
            raise
    
    async def _load_file_configuration(self) -> Dict[str, Any]:
        """Load configuration from file-based fallback."""
        config_path = Path(self.config.fallback_config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                self.logger.info("Configuration loaded from file fallback")
                return config_data
            except Exception as e:
                self.logger.error(f"Failed to load file configuration: {e}")
        
        # Return default configuration
        default_config = {
            "workflows": {
                "discovery": {"enabled": True, "interval_minutes": 60},
                "analysis": {"enabled": True, "interval_minutes": 30},
                "generation": {"enabled": True, "interval_minutes": 15},
                "validation": {"enabled": True, "interval_minutes": 5}
            },
            "thresholds": {
                "accuracy_minimum": 0.95,
                "staleness_hours": 24,
                "refresh_interval_hours": 1
            }
        }
        
        self.logger.info("Using default configuration")
        return default_config
    
    async def _initialize_file_monitoring(self):
        """Initialize file system monitoring for change detection."""
        try:
            # Monitor key directories for changes
            monitor_paths = [
                "src/system_architecture/",
                "docs/",
                ".kiro/specs/system-architecture-wiring-diagram/",
                "deployment/observatory/"
            ]
            
            for path in monitor_paths:
                if Path(path).exists():
                    await self._calculate_directory_hash(path)
            
            self.logger.info("File monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize file monitoring: {e}")
    
    async def _calculate_directory_hash(self, directory: str) -> str:
        """Calculate hash of directory contents for change detection."""
        try:
            hash_md5 = hashlib.md5()
            
            for root, dirs, files in os.walk(directory):
                # Sort to ensure consistent hashing
                dirs.sort()
                files.sort()
                
                for file in files:
                    if file.endswith(('.py', '.md', '.yml', '.yaml', '.json')):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'rb') as f:
                                hash_md5.update(f.read())
                        except Exception:
                            continue  # Skip files that can't be read
            
            directory_hash = hash_md5.hexdigest()
            self.file_hashes[directory] = directory_hash
            return directory_hash
            
        except Exception as e:
            self.logger.error(f"Failed to calculate directory hash for {directory}: {e}")
            return ""
    
    async def queue_documentation_task(self, task_type: str, component: str, 
                                     priority: int = 1) -> str:
        """Queue a documentation generation task."""
        task_id = f"{task_type}_{component}_{int(time.time())}"
        
        task = DocumentationTask(
            task_id=task_id,
            task_type=task_type,
            component=component,
            priority=priority
        )
        
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
        
        self.metrics['tasks_queued'] += 1
        
        self.logger.info(f"Queued documentation task: {task_id}",
                        extra={"task_type": task_type, "component": component})
        
        return task_id
    
    async def _background_orchestration_loop(self):
        """Background loop for processing documentation tasks."""
        while True:
            try:
                await self._process_task_queue()
                await self._check_for_changes()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_task_queue(self):
        """Process queued documentation tasks."""
        if not self.task_queue:
            return
        
        # Limit concurrent tasks
        if len(self.running_tasks) >= self.config.max_concurrent_generations:
            return
        
        # Get next task
        task = self.task_queue.pop(0)
        self.running_tasks[task.task_id] = task
        task.status = "running"
        
        try:
            # Execute the task
            start_time = time.time()
            result = await self._execute_documentation_task(task)
            duration = time.time() - start_time
            
            # Update task status
            task.status = "completed"
            task.result = result
            self.completed_tasks[task.task_id] = task
            
            # Update metrics
            self.metrics['tasks_completed'] += 1
            self.metrics['last_generation_duration'] = duration
            
            self.logger.info(f"Completed documentation task: {task.task_id}",
                           extra={"duration": duration})
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.metrics['tasks_failed'] += 1
            
            self.logger.error(f"Failed documentation task: {task.task_id}: {e}")
        
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task.task_id, None)
    
    async def _execute_documentation_task(self, task: DocumentationTask) -> Dict[str, Any]:
        """Execute a specific documentation task."""
        correlation_id = self.generate_correlation_id()
        
        if task.task_type == "discovery":
            return await self._execute_discovery_task(task, correlation_id)
        elif task.task_type == "analysis":
            return await self._execute_analysis_task(task, correlation_id)
        elif task.task_type == "generation":
            return await self._execute_generation_task(task, correlation_id)
        elif task.task_type == "validation":
            return await self._execute_validation_task(task, correlation_id)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    async def _execute_discovery_task(self, task: DocumentationTask, 
                                    correlation_id: str) -> Dict[str, Any]:
        """Execute infrastructure discovery task."""
        # This would integrate with existing discovery components
        return {
            "task_id": task.task_id,
            "component": task.component,
            "discovery_results": "placeholder_for_actual_discovery",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_analysis_task(self, task: DocumentationTask, 
                                   correlation_id: str) -> Dict[str, Any]:
        """Execute relationship analysis task."""
        # This would integrate with existing analysis components
        return {
            "task_id": task.task_id,
            "component": task.component,
            "analysis_results": "placeholder_for_actual_analysis",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_generation_task(self, task: DocumentationTask, 
                                     correlation_id: str) -> Dict[str, Any]:
        """Execute documentation generation task."""
        # This would integrate with existing generation components
        return {
            "task_id": task.task_id,
            "component": task.component,
            "generation_results": "placeholder_for_actual_generation",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_validation_task(self, task: DocumentationTask, 
                                     correlation_id: str) -> Dict[str, Any]:
        """Execute documentation validation task."""
        # This would integrate with validation components
        return {
            "task_id": task.task_id,
            "component": task.component,
            "validation_results": "placeholder_for_actual_validation",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_for_changes(self):
        """Check for file system changes and trigger regeneration."""
        try:
            changes_detected = False
            
            for directory in self.file_hashes.keys():
                if Path(directory).exists():
                    new_hash = await self._calculate_directory_hash(directory)
                    if new_hash != self.file_hashes.get(directory):
                        changes_detected = True
                        self.logger.info(f"Changes detected in {directory}")
                        
                        # Queue regeneration tasks
                        await self.queue_documentation_task("generation", directory, priority=2)
            
            if changes_detected:
                self.last_generation_time = datetime.utcnow()
                
        except Exception as e:
            self.logger.error(f"Error checking for changes: {e}")
    
    async def _staleness_monitoring_loop(self):
        """Monitor for stale documentation and send alerts."""
        while True:
            try:
                await self._check_documentation_staleness()
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in staleness monitoring: {e}")
                await asyncio.sleep(3600)
    
    async def _check_documentation_staleness(self):
        """Check for stale documentation and trigger alerts."""
        try:
            staleness_threshold = timedelta(hours=self.config.staleness_threshold_hours)
            current_time = datetime.utcnow()
            
            if (self.last_generation_time and 
                current_time - self.last_generation_time > staleness_threshold):
                
                self.metrics['staleness_alerts'] += 1
                
                self.logger.warning("Documentation staleness detected",
                                  extra={
                                      "last_generation": self.last_generation_time.isoformat(),
                                      "threshold_hours": self.config.staleness_threshold_hours
                                  })
                
                # Queue refresh tasks
                await self.queue_documentation_task("discovery", "all", priority=3)
                await self.queue_documentation_task("generation", "all", priority=3)
                
        except Exception as e:
            self.logger.error(f"Error checking documentation staleness: {e}")
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status."""
        return {
            "status": "running",
            "cms_available": self.cms_available,
            "last_cms_check": self.last_cms_check.isoformat() if self.last_cms_check else None,
            "queued_tasks": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "last_generation": self.last_generation_time.isoformat() if self.last_generation_time else None,
            "metrics": self.metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def trigger_full_regeneration(self) -> Dict[str, Any]:
        """Trigger full documentation regeneration."""
        correlation_id = self.generate_correlation_id()
        
        try:
            # Queue all regeneration tasks
            components = ["discovery", "analysis", "generation", "validation"]
            task_ids = []
            
            for component in components:
                task_id = await self.queue_documentation_task(component, "all", priority=5)
                task_ids.append(task_id)
            
            self.logger.info("Full documentation regeneration triggered",
                           extra={"correlation_id": correlation_id, "task_ids": task_ids})
            
            return {
                "status": "triggered",
                "task_ids": task_ids,
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to trigger full regeneration: {e}",
                            extra={"correlation_id": correlation_id})
            return {
                "status": "failed",
                "error": str(e),
                "correlation_id": correlation_id
            }


# Health endpoint integration
async def create_documentation_orchestrator() -> DocumentationOrchestrator:
    """Factory function to create and initialize DocumentationOrchestrator."""
    orchestrator = DocumentationOrchestrator()
    await orchestrator.initialize()
    return orchestrator


if __name__ == "__main__":
    async def main():
        orchestrator = await create_documentation_orchestrator()
        
        # Example usage
        status = await orchestrator.get_orchestration_status()
        print(f"Orchestrator Status: {json.dumps(status, indent=2)}")
        
        # Trigger a test task
        task_id = await orchestrator.queue_documentation_task("discovery", "test_component")
        print(f"Queued task: {task_id}")
        
        # Wait a bit and check status again
        await asyncio.sleep(5)
        status = await orchestrator.get_orchestration_status()
        print(f"Updated Status: {json.dumps(status, indent=2)}")
    
    asyncio.run(main())