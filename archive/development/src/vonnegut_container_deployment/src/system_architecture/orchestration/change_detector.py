#!/usr/bin/env python3
"""
Change Detector - Task 5.1 Component
====================================

Implements automated change detection using file system monitoring
and WebSocket event triggers for infrastructure changes.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability


@dataclass
class ChangeEvent:
    """Represents a detected change event."""
    event_id: str
    event_type: str  # file_change, websocket_event, service_change
    source: str  # file path, websocket endpoint, service name
    change_type: str  # created, modified, deleted, connected, disconnected
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    impact_level: str = "medium"  # low, medium, high, critical
    affected_components: List[str] = field(default_factory=list)


@dataclass
class MonitoringConfig:
    """Configuration for change monitoring."""
    # File system monitoring
    watch_directories: List[Path] = field(default_factory=lambda: [
        Path("src/system_architecture"),
        Path("docs"),
        Path("scripts"),
        Path(".kiro/specs"),
        Path("config")
    ])
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "*.pyc", "*.pyo", "__pycache__", ".git", ".DS_Store", "*.log"
    ])
    
    # WebSocket monitoring
    websocket_endpoints: List[str] = field(default_factory=lambda: [
        "/ws/observatory", "/ws/anomalies", "/ws/emoji-rain", "/ws/doctor-status"
    ])
    websocket_url: str = "ws://localhost:8888"
    
    # Change detection settings
    debounce_interval: float = 5.0  # seconds
    batch_changes: bool = True
    max_batch_size: int = 50
    
    # Impact assessment
    high_impact_patterns: List[str] = field(default_factory=lambda: [
        "*/models/*", "*/core/*", "*/orchestration/*", "*/discovery/*"
    ])
    critical_impact_patterns: List[str] = field(default_factory=lambda: [
        "*/unified_reflective_module.py", "*/documentation_orchestrator.py"
    ])


class FileSystemChangeHandler(FileSystemEventHandler):
    """Handles file system change events."""
    
    def __init__(self, change_detector: 'ChangeDetector'):
        self._change_detector = change_detector
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
    
    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle any file system event."""
        if event.is_directory:
            return
        
        # Filter out ignored patterns
        if self._should_ignore_event(event):
            return
        
        # Create change event
        change_event = ChangeEvent(
            event_id=f"fs_{int(time.time() * 1000)}_{hash(event.src_path) % 10000}",
            event_type="file_change",
            source=event.src_path,
            change_type=event.event_type,
            timestamp=datetime.now(),
            metadata={
                "file_path": event.src_path,
                "is_directory": event.is_directory,
                "event_type": event.event_type
            }
        )
        
        # Assess impact
        change_event.impact_level = self._assess_file_impact(event.src_path)
        change_event.affected_components = self._identify_affected_components(event.src_path)
        
        # Report to change detector
        self._change_detector._handle_change_event(change_event)
    
    def _should_ignore_event(self, event: FileSystemEvent) -> bool:
        """Check if event should be ignored."""
        file_path = Path(event.src_path)
        
        # Check ignore patterns
        for pattern in self._change_detector._config.ignore_patterns:
            if file_path.match(pattern):
                return True
        
        return False
    
    def _assess_file_impact(self, file_path: str) -> str:
        """Assess the impact level of a file change."""
        path = Path(file_path)
        
        # Check critical patterns
        for pattern in self._change_detector._config.critical_impact_patterns:
            if path.match(pattern):
                return "critical"
        
        # Check high impact patterns
        for pattern in self._change_detector._config.high_impact_patterns:
            if path.match(pattern):
                return "high"
        
        # Check file extension for medium impact
        if path.suffix in [".py", ".yaml", ".yml", ".json", ".md"]:
            return "medium"
        
        return "low"
    
    def _identify_affected_components(self, file_path: str) -> List[str]:
        """Identify components affected by file change."""
        path = Path(file_path)
        components = []
        
        # Map file paths to components
        if "orchestration" in path.parts:
            components.append("documentation_orchestrator")
        if "generation" in path.parts:
            components.append("diagram_generator")
        if "discovery" in path.parts:
            components.append("infrastructure_scanner")
        if "analysis" in path.parts:
            components.append("automation_analyzer")
        if "validation" in path.parts:
            components.append("validation_system")
        
        # Add generic component based on directory
        if len(path.parts) > 1:
            components.append(path.parts[1])  # Second level directory
        
        return components


class ChangeDetector(ReflectiveModule):
    """
    Automated change detection using file system monitoring and WebSocket events.
    
    Monitors infrastructure changes and triggers documentation updates
    with configurable debouncing and impact assessment.
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        super().__init__()
        self.module_id = "ChangeDetector"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or MonitoringConfig()
        
        # File system monitoring
        self._observer: Optional[Observer] = None
        self._file_handler = FileSystemChangeHandler(self)
        
        # Change tracking
        self._pending_changes: List[ChangeEvent] = []
        self._processed_changes: List[ChangeEvent] = []
        self._change_lock = threading.Lock()
        
        # Debouncing
        self._debounce_timer: Optional[threading.Timer] = None
        self._batched_changes: List[ChangeEvent] = []
        
        # Callbacks
        self._change_callbacks: List[Callable[[List[ChangeEvent]], None]] = []
        
        # Metrics
        self._total_changes_detected = 0
        self._changes_by_type: Dict[str, int] = {}
        self._changes_by_impact: Dict[str, int] = {}
        
        # State
        self._is_monitoring = False
        
        self._logger.info("ChangeDetector initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def start_monitoring(self) -> None:
        """Start change monitoring."""
        self._logger.info("Starting change monitoring...")
        
        if self._is_monitoring:
            self._logger.warning("Change monitoring already active")
            return
        
        # Start file system monitoring
        self._observer = Observer()
        
        for watch_dir in self._config.watch_directories:
            if watch_dir.exists():
                self._observer.schedule(
                    self._file_handler,
                    str(watch_dir),
                    recursive=True
                )
                self._logger.info(f"Watching directory: {watch_dir}")
            else:
                self._logger.warning(f"Watch directory does not exist: {watch_dir}")
        
        self._observer.start()
        self._is_monitoring = True
        
        self._logger.info("Change monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop change monitoring."""
        self._logger.info("Stopping change monitoring...")
        
        if not self._is_monitoring:
            return
        
        # Stop file system monitoring
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        
        # Cancel debounce timer
        if self._debounce_timer:
            self._debounce_timer.cancel()
            self._debounce_timer = None
        
        self._is_monitoring = False
        
        self._logger.info("Change monitoring stopped")
    
    def _handle_change_event(self, change_event: ChangeEvent) -> None:
        """Handle a detected change event."""
        with self._change_lock:
            self._total_changes_detected += 1
            
            # Update metrics
            self._changes_by_type[change_event.change_type] = (
                self._changes_by_type.get(change_event.change_type, 0) + 1
            )
            self._changes_by_impact[change_event.impact_level] = (
                self._changes_by_impact.get(change_event.impact_level, 0) + 1
            )
            
            if self._config.batch_changes:
                # Add to batch
                self._batched_changes.append(change_event)
                
                # Reset debounce timer
                if self._debounce_timer:
                    self._debounce_timer.cancel()
                
                self._debounce_timer = threading.Timer(
                    self._config.debounce_interval,
                    self._process_batched_changes
                )
                self._debounce_timer.start()
                
                # Process immediately if batch is full
                if len(self._batched_changes) >= self._config.max_batch_size:
                    if self._debounce_timer:
                        self._debounce_timer.cancel()
                    self._process_batched_changes()
            else:
                # Process immediately
                self._process_change_events([change_event])
    
    def _process_batched_changes(self) -> None:
        """Process batched changes."""
        with self._change_lock:
            if not self._batched_changes:
                return
            
            changes_to_process = self._batched_changes.copy()
            self._batched_changes.clear()
            
            if self._debounce_timer:
                self._debounce_timer = None
        
        self._process_change_events(changes_to_process)
    
    def _process_change_events(self, changes: List[ChangeEvent]) -> None:
        """Process a list of change events."""
        if not changes:
            return
        
        self._logger.info(f"Processing {len(changes)} change events")
        
        # Deduplicate and merge similar changes
        processed_changes = self._deduplicate_changes(changes)
        
        # Add to pending changes
        with self._change_lock:
            self._pending_changes.extend(processed_changes)
            self._processed_changes.extend(processed_changes)
        
        # Notify callbacks
        for callback in self._change_callbacks:
            try:
                callback(processed_changes)
            except Exception as e:
                self._logger.error(f"Error in change callback: {e}")
        
        self._logger.info(f"Processed {len(processed_changes)} unique changes")
    
    def _deduplicate_changes(self, changes: List[ChangeEvent]) -> List[ChangeEvent]:
        """Deduplicate and merge similar changes."""
        # Group changes by source
        changes_by_source: Dict[str, List[ChangeEvent]] = {}
        for change in changes:
            if change.source not in changes_by_source:
                changes_by_source[change.source] = []
            changes_by_source[change.source].append(change)
        
        deduplicated = []
        for source, source_changes in changes_by_source.items():
            if len(source_changes) == 1:
                deduplicated.append(source_changes[0])
            else:
                # Merge multiple changes for same source
                merged_change = self._merge_changes(source_changes)
                deduplicated.append(merged_change)
        
        return deduplicated
    
    def _merge_changes(self, changes: List[ChangeEvent]) -> ChangeEvent:
        """Merge multiple changes for the same source."""
        if not changes:
            raise ValueError("Cannot merge empty change list")
        
        if len(changes) == 1:
            return changes[0]
        
        # Use the latest change as base
        latest_change = max(changes, key=lambda c: c.timestamp)
        
        # Merge metadata
        merged_metadata = {}
        for change in changes:
            merged_metadata.update(change.metadata)
        
        # Merge affected components
        affected_components = set()
        for change in changes:
            affected_components.update(change.affected_components)
        
        # Determine highest impact level
        impact_levels = ["low", "medium", "high", "critical"]
        highest_impact = max(
            (change.impact_level for change in changes),
            key=lambda level: impact_levels.index(level)
        )
        
        return ChangeEvent(
            event_id=f"merged_{int(time.time() * 1000)}",
            event_type=latest_change.event_type,
            source=latest_change.source,
            change_type="modified",  # Merged changes are considered modifications
            timestamp=latest_change.timestamp,
            metadata=merged_metadata,
            impact_level=highest_impact,
            affected_components=list(affected_components)
        )
    
    def get_pending_changes(self) -> List[ChangeEvent]:
        """Get and clear pending changes."""
        with self._change_lock:
            pending = self._pending_changes.copy()
            self._pending_changes.clear()
            return pending
    
    def get_recent_changes(self, hours: int = 24) -> List[ChangeEvent]:
        """Get changes from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._change_lock:
            return [
                change for change in self._processed_changes
                if change.timestamp > cutoff_time
            ]
    
    def add_change_callback(self, callback: Callable[[List[ChangeEvent]], None]) -> None:
        """Add callback for change events."""
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[List[ChangeEvent]], None]) -> None:
        """Remove change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def force_change_detection(self, source: str, change_type: str, impact_level: str = "medium") -> None:
        """Force a change detection event."""
        change_event = ChangeEvent(
            event_id=f"forced_{int(time.time() * 1000)}",
            event_type="manual",
            source=source,
            change_type=change_type,
            timestamp=datetime.now(),
            impact_level=impact_level,
            metadata={"forced": True}
        )
        
        self._handle_change_event(change_event)
    
    def get_change_statistics(self) -> Dict[str, Any]:
        """Get change detection statistics."""
        return {
            "total_changes_detected": self._total_changes_detected,
            "changes_by_type": self._changes_by_type.copy(),
            "changes_by_impact": self._changes_by_impact.copy(),
            "pending_changes": len(self._pending_changes),
            "processed_changes": len(self._processed_changes),
            "is_monitoring": self._is_monitoring,
            "watched_directories": [str(d) for d in self._config.watch_directories],
            "active_callbacks": len(self._change_callbacks)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """ReflectiveModule health status implementation."""
        return {
            "status": "healthy" if self._is_monitoring else "stopped",
            "monitoring": {
                "active": self._is_monitoring,
                "watched_directories": len([d for d in self._config.watch_directories if d.exists()]),
                "total_directories": len(self._config.watch_directories),
                "observer_running": self._observer is not None and self._observer.is_alive() if self._observer else False
            },
            "changes": {
                "total_detected": self._total_changes_detected,
                "pending": len(self._pending_changes),
                "processed": len(self._processed_changes)
            },
            "callbacks": {
                "registered": len(self._change_callbacks)
            }
        }
    
    def get_metrics(self) -> Dict[str, float]:
        """ReflectiveModule metrics implementation."""
        return {
            "change_detection_total": float(self._total_changes_detected),
            "change_detection_pending": float(len(self._pending_changes)),
            "change_detection_processed": float(len(self._processed_changes)),
            "change_detection_callbacks": float(len(self._change_callbacks)),
            "change_detection_monitoring": 1.0 if self._is_monitoring else 0.0,
            **{
                f"change_detection_type_{change_type}": float(count)
                for change_type, count in self._changes_by_type.items()
            },
            **{
                f"change_detection_impact_{impact}": float(count)
                for impact, count in self._changes_by_impact.items()
            }
        }#!/usr/bin/env python3
"""
Change Detector - Phase 5 Task 5.1 Component

Monitors file system changes and triggers documentation updates
with intelligent change classification and debouncing.
"""

import os
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ChangeEvent:
    """Represents a file system change event."""
    file_path: str
    event_type: str  # 'created', 'modified', 'deleted'
    timestamp: datetime
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    change_category: Optional[str] = None  # 'source', 'config', 'docs', 'specs'
    affected_components: List[str] = None
    priority: int = 3  # 1=highest, 5=lowest


@dataclass
class ChangePattern:
    """Defines patterns for change detection and classification."""
    pattern: str  # glob pattern
    category: str
    affected_components: List[str]
    priority: int
    debounce_seconds: float = 2.0
    ignore_extensions: List[str] = None


class IntelligentFileSystemHandler(FileSystemEventHandler):
    """Enhanced file system event handler with intelligent change detection."""
    
    def __init__(self, change_detector: 'ChangeDetector'):
        self.change_detector = change_detector
        self.pending_events: Dict[str, ChangeEvent] = {}
        self.file_hashes: Dict[str, str] = {}
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        self._handle_event(event.src_path, 'modified')
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        self._handle_event(event.src_path, 'created')
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        if event.is_directory:
            return
        
        self._handle_event(event.src_path, 'deleted')
    
    def _handle_event(self, file_path: str, event_type: str):
        """Handle a file system event with intelligent processing."""
        try:
            # Create change event
            change_event = ChangeEvent(
                file_path=file_path,
                event_type=event_type,
                timestamp=datetime.now()
            )
            
            # Calculate file hash and size for non-deleted files
            if event_type != 'deleted' and os.path.exists(file_path):
                change_event.file_hash = self._calculate_file_hash(file_path)
                change_event.file_size = os.path.getsize(file_path)
                
                # Check if file actually changed
                if file_path in self.file_hashes:
                    if self.file_hashes[file_path] == change_event.file_hash:
                        # File hasn't actually changed, ignore
                        return
                
                self.file_hashes[file_path] = change_event.file_hash
            elif event_type == 'deleted':
                # Remove from hash cache
                self.file_hashes.pop(file_path, None)
            
            # Classify the change
            self._classify_change(change_event)
            
            # Check if we should ignore this change
            if self._should_ignore_change(change_event):
                return
            
            # Handle debouncing
            self._handle_debounced_event(change_event)
            
        except Exception as e:
            self.change_detector.logger.error(f"Error handling file event {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _classify_change(self, change_event: ChangeEvent):
        """Classify the change event based on file path and patterns."""
        file_path = change_event.file_path
        
        # Find matching pattern
        for pattern in self.change_detector.change_patterns:
            if self._matches_pattern(file_path, pattern.pattern):
                change_event.change_category = pattern.category
                change_event.affected_components = pattern.affected_components.copy()
                change_event.priority = pattern.priority
                return
        
        # Default classification
        change_event.change_category = 'unknown'
        change_event.affected_components = []
        change_event.priority = 5
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def _should_ignore_change(self, change_event: ChangeEvent) -> bool:
        """Determine if a change should be ignored."""
        file_path = change_event.file_path
        
        # Ignore temporary files
        if any(file_path.endswith(ext) for ext in ['.tmp', '.swp', '.bak', '~']):
            return True
        
        # Ignore hidden files (except .kiro)
        if '/.git/' in file_path or file_path.startswith('.') and not file_path.startswith('.kiro'):
            return True
        
        # Ignore compiled files
        if any(file_path.endswith(ext) for ext in ['.pyc', '.pyo', '__pycache__']):
            return True
        
        # Ignore log files
        if file_path.endswith('.log') or '/logs/' in file_path:
            return True
        
        return False
    
    def _handle_debounced_event(self, change_event: ChangeEvent):
        """Handle event with debouncing to avoid rapid-fire updates."""
        file_path = change_event.file_path
        
        # Get debounce time for this file type
        debounce_time = 2.0  # default
        for pattern in self.change_detector.change_patterns:
            if self._matches_pattern(file_path, pattern.pattern):
                debounce_time = pattern.debounce_seconds
                break
        
        # Check if we have a pending event for this file
        if file_path in self.pending_events:
            existing_event = self.pending_events[file_path]
            time_diff = (change_event.timestamp - existing_event.timestamp).total_seconds()
            
            if time_diff < debounce_time:
                # Update the pending event
                self.pending_events[file_path] = change_event
                return
        
        # Store as pending and schedule processing
        self.pending_events[file_path] = change_event
        
        # Schedule processing after debounce time
        import asyncio
        asyncio.create_task(self._process_debounced_event(file_path, debounce_time))
    
    async def _process_debounced_event(self, file_path: str, debounce_time: float):
        """Process a debounced event after the debounce period."""
        await asyncio.sleep(debounce_time)
        
        if file_path in self.pending_events:
            change_event = self.pending_events.pop(file_path)
            await self.change_detector.process_change_event(change_event)


class ChangeDetector(ReflectiveModule):
    """
    Intelligent change detection system for documentation updates.
    
    Monitors file system changes, classifies them by impact, and triggers
    appropriate documentation generation tasks with debouncing and filtering.
    """
    
    def __init__(self):
        super().__init__()
        self.observer: Optional[Observer] = None
        self.change_patterns: List[ChangePattern] = []
        self.change_callbacks: List[Callable[[ChangeEvent], None]] = []
        self.change_history: List[ChangeEvent] = []
        self.max_history_size = 1000
        self.monitoring_active = False
        
        # Initialize change patterns
        self._initialize_change_patterns()
        
        # Register capabilities
        self.register_capability('change_detection', {
            'description': 'Intelligent file system change detection and classification',
            'patterns_configured': len(self.change_patterns),
            'monitoring_active': self.monitoring_active
        })
    
    def _initialize_change_patterns(self):
        """Initialize change detection patterns."""
        self.change_patterns = [
            # Source code changes
            ChangePattern(
                pattern='src/system_architecture/discovery/*.py',
                category='discovery_source',
                affected_components=['InfrastructureDiscoverer', 'ServiceDiscoveryScanner', 'ObservatoryWebSocketClient'],
                priority=1,
                debounce_seconds=3.0
            ),
            ChangePattern(
                pattern='src/system_architecture/analysis/*.py',
                category='analysis_source',
                affected_components=['RelationshipMapper', 'DataFlowMapper', 'AutomationChainAnalyzer'],
                priority=1,
                debounce_seconds=3.0
            ),
            ChangePattern(
                pattern='src/system_architecture/generation/*.py',
                category='generation_source',
                affected_components=['DiagramGenerator', 'SequenceDiagramGenerator', 'NetworkTopologyVisualizer'],
                priority=2,
                debounce_seconds=3.0
            ),
            ChangePattern(
                pattern='src/system_architecture/orchestration/*.py',
                category='orchestration_source',
                affected_components=['DocumentationOrchestrator', 'ChangeDetector'],
                priority=1,
                debounce_seconds=3.0
            ),
            
            # Configuration changes
            ChangePattern(
                pattern='.kiro/specs/**/*.md',
                category='specifications',
                affected_components=['InfrastructureDiscoverer', 'RelationshipMapper'],
                priority=1,
                debounce_seconds=5.0
            ),
            ChangePattern(
                pattern='*.yml',
                category='configuration',
                affected_components=['ServiceDiscoveryScanner', 'NetworkTopologyVisualizer'],
                priority=2,
                debounce_seconds=5.0
            ),
            ChangePattern(
                pattern='*.yaml',
                category='configuration',
                affected_components=['ServiceDiscoveryScanner', 'NetworkTopologyVisualizer'],
                priority=2,
                debounce_seconds=5.0
            ),
            ChangePattern(
                pattern='Makefile',
                category='automation',
                affected_components=['AutomationChainAnalyzer'],
                priority=2,
                debounce_seconds=5.0
            ),
            
            # Documentation changes
            ChangePattern(
                pattern='docs/**/*.md',
                category='documentation',
                affected_components=['RealTimeValidator', 'AccuracyMonitor'],
                priority=3,
                debounce_seconds=10.0
            ),
            ChangePattern(
                pattern='README.md',
                category='documentation',
                affected_components=['RealTimeValidator'],
                priority=3,
                debounce_seconds=10.0
            ),
            
            # Script changes
            ChangePattern(
                pattern='scripts/*.py',
                category='automation_scripts',
                affected_components=['AutomationChainAnalyzer', 'ServiceDiscoveryScanner'],
                priority=2,
                debounce_seconds=5.0
            ),
            ChangePattern(
                pattern='scripts/*.sh',
                category='automation_scripts',
                affected_components=['AutomationChainAnalyzer'],
                priority=2,
                debounce_seconds=5.0
            ),
            
            # Generated files (lower priority)
            ChangePattern(
                pattern='generated/**/*',
                category='generated',
                affected_components=['RealTimeValidator'],
                priority=4,
                debounce_seconds=15.0
            ),
            ChangePattern(
                pattern='*.svg',
                category='generated_diagrams',
                affected_components=['RealTimeValidator'],
                priority=4,
                debounce_seconds=15.0
            ),
            ChangePattern(
                pattern='*.html',
                category='generated_docs',
                affected_components=['RealTimeValidator'],
                priority=4,
                debounce_seconds=15.0
            )
        ]
    
    async def start_monitoring(self, watch_paths: List[str]) -> Dict[str, Any]:
        """Start file system monitoring."""
        try:
            if self.monitoring_active:
                return {'status': 'already_running'}
            
            self.observer = Observer()
            event_handler = IntelligentFileSystemHandler(self)
            
            monitored_paths = []
            for path in watch_paths:
                if os.path.exists(path):
                    self.observer.schedule(event_handler, path, recursive=True)
                    monitored_paths.append(path)
                    self.logger.info(f"Monitoring {path} for changes")
                else:
                    self.logger.warning(f"Path {path} does not exist, skipping")
            
            self.observer.start()
            self.monitoring_active = True
            
            self.logger.info(f"Change detection started, monitoring {len(monitored_paths)} paths")
            return {
                'status': 'started',
                'monitored_paths': monitored_paths,
                'patterns_configured': len(self.change_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start change monitoring: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop file system monitoring."""
        try:
            if not self.monitoring_active:
                return {'status': 'not_running'}
            
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.monitoring_active = False
            self.logger.info("Change detection stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            self.logger.error(f"Error stopping change monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def add_change_callback(self, callback: Callable[[ChangeEvent], None]):
        """Add a callback function to be called when changes are detected."""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[ChangeEvent], None]):
        """Remove a change callback."""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    async def process_change_event(self, change_event: ChangeEvent):
        """Process a change event and notify callbacks."""
        try:
            # Add to history
            self.change_history.append(change_event)
            
            # Trim history if too large
            if len(self.change_history) > self.max_history_size:
                self.change_history = self.change_history[-self.max_history_size:]
            
            self.logger.info(
                f"Processing change: {change_event.file_path} "
                f"({change_event.event_type}, {change_event.change_category}, "
                f"priority={change_event.priority})"
            )
            
            # Notify callbacks
            for callback in self.change_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(change_event)
                    else:
                        callback(change_event)
                except Exception as e:
                    self.logger.error(f"Error in change callback: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing change event: {e}")
    
    def get_change_history(self, limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get change history with optional filtering."""
        history = self.change_history
        
        # Filter by category if specified
        if category:
            history = [event for event in history if event.change_category == category]
        
        # Apply limit
        if limit:
            history = history[-limit:]
        
        return [asdict(event) for event in history]
    
    def get_change_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected changes."""
        if not self.change_history:
            return {'total_changes': 0}
        
        # Count by category
        category_counts = {}
        event_type_counts = {}
        priority_counts = {}
        
        for event in self.change_history:
            # Category counts
            category = event.change_category or 'unknown'
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Event type counts
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
            
            # Priority counts
            priority_counts[event.priority] = priority_counts.get(event.priority, 0) + 1
        
        # Recent activity (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_changes = [event for event in self.change_history if event.timestamp > one_hour_ago]
        
        return {
            'total_changes': len(self.change_history),
            'recent_changes_1h': len(recent_changes),
            'category_counts': category_counts,
            'event_type_counts': event_type_counts,
            'priority_counts': priority_counts,
            'oldest_change': self.change_history[0].timestamp.isoformat() if self.change_history else None,
            'newest_change': self.change_history[-1].timestamp.isoformat() if self.change_history else None
        }
    
    def add_change_pattern(self, pattern: ChangePattern):
        """Add a new change detection pattern."""
        self.change_patterns.append(pattern)
        self.logger.info(f"Added change pattern: {pattern.pattern} -> {pattern.category}")
    
    def remove_change_pattern(self, pattern_str: str):
        """Remove a change detection pattern."""
        self.change_patterns = [p for p in self.change_patterns if p.pattern != pattern_str]
        self.logger.info(f"Removed change pattern: {pattern_str}")
    
    def get_change_patterns(self) -> List[Dict[str, Any]]:
        """Get all configured change patterns."""
        return [asdict(pattern) for pattern in self.change_patterns]
    
    async def simulate_change(self, file_path: str, event_type: str = 'modified') -> Dict[str, Any]:
        """Simulate a change event for testing purposes."""
        change_event = ChangeEvent(
            file_path=file_path,
            event_type=event_type,
            timestamp=datetime.now()
        )
        
        # Classify the simulated change
        for pattern in self.change_patterns:
            if self._matches_pattern(file_path, pattern.pattern):
                change_event.change_category = pattern.category
                change_event.affected_components = pattern.affected_components.copy()
                change_event.priority = pattern.priority
                break
        
        await self.process_change_event(change_event)
        
        return {
            'simulated_change': asdict(change_event),
            'callbacks_notified': len(self.change_callbacks)
        }
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            'status': 'healthy',
            'monitoring_active': self.monitoring_active,
            'observer_alive': self.observer.is_alive() if self.observer else False,
            'patterns_configured': len(self.change_patterns),
            'callbacks_registered': len(self.change_callbacks),
            'changes_detected': len(self.change_history)
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'monitoring_active': self.monitoring_active,
            'patterns_configured': len(self.change_patterns) > 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get change detection metrics."""
        stats = self.get_change_statistics()
        return {
            'change_detector_total_changes': stats['total_changes'],
            'change_detector_recent_changes_1h': stats['recent_changes_1h'],
            'change_detector_monitoring_active': 1 if self.monitoring_active else 0,
            'change_detector_patterns_configured': len(self.change_patterns),
            'change_detector_callbacks_registered': len(self.change_callbacks)
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create change detector
        detector = ChangeDetector()
        
        # Add a callback to handle changes
        async def handle_change(change_event: ChangeEvent):
            print(f"Change detected: {change_event.file_path} ({change_event.change_category})")
        
        detector.add_change_callback(handle_change)
        
        # Start monitoring
        watch_paths = ['src', 'docs', '.kiro', 'scripts']
        result = await detector.start_monitoring(watch_paths)
        print(f"Monitoring started: {result}")
        
        # Simulate some changes
        await detector.simulate_change('src/system_architecture/discovery/test.py', 'modified')
        await detector.simulate_change('.kiro/specs/test.md', 'created')
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Get statistics
        stats = detector.get_change_statistics()
        print(f"Statistics: {stats}")
        
        # Stop monitoring
        await detector.stop_monitoring()
    
    import asyncio
    asyncio.run(main())