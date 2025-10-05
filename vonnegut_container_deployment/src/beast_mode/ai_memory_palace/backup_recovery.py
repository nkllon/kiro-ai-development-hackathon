"""
Backup and Recovery System for AI Memory Palace.

Provides automatic context backup, corruption detection, recovery mechanisms,
and CLI tools for context validation and repair.
"""

import json
import asyncio
import shutil
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import uuid
import sqlite3
import threading
import time
from dataclasses import dataclass
from enum import Enum

from src.beast_mode.core.beastly_module import BeastlyModule
from .models import SessionContext, ContextEvent, ValidationSeverity
from .context_registry import ContextRegistry
from .context_validator import ContextValidator
from .storage import ContextStorage


class BackupType(Enum):
    """Types of context backups"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"


class RecoveryStrategy(Enum):
    """Context recovery strategies"""
    RESTORE_LATEST = "restore_latest"
    RESTORE_SPECIFIC = "restore_specific"
    MERGE_BACKUPS = "merge_backups"
    REBUILD_FROM_EVENTS = "rebuild_from_events"


@dataclass
class BackupMetadata:
    """Metadata for context backups"""
    backup_id: str
    project_id: str
    session_id: str
    backup_type: BackupType
    timestamp: datetime
    size_bytes: int
    checksum: str
    compression_ratio: float
    validation_status: str
    backup_path: Path
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "backup_type": self.backup_type.value,
            "timestamp": self.timestamp.isoformat(),
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "compression_ratio": self.compression_ratio,
            "validation_status": self.validation_status,
            "backup_path": str(self.backup_path)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        return cls(
            backup_id=data["backup_id"],
            project_id=data["project_id"],
            session_id=data["session_id"],
            backup_type=BackupType(data["backup_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            size_bytes=data["size_bytes"],
            checksum=data["checksum"],
            compression_ratio=data["compression_ratio"],
            validation_status=data["validation_status"],
            backup_path=Path(data["backup_path"])
        )


class ContextBackupManager(BeastlyModule):
    """Manages automatic context backups and recovery operations"""
    
    def __init__(self, storage: ContextStorage, validator: ContextValidator, 
                 backup_dir: Optional[Path] = None):
        super().__init__()
        
        self.storage = storage
        self.validator = validator
        
        # Setup backup directory
        self.backup_dir = backup_dir or Path.home() / ".kiro" / "context_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup metadata database
        self.metadata_db = self.backup_dir / "backup_metadata.db"
        self._init_metadata_db()
        
        # Backup configuration
        self.max_backups_per_project = 50
        self.backup_retention_days = 30
        self.auto_backup_interval = 300  # 5 minutes
        self.compression_enabled = True
        
        # Background backup thread
        self._backup_thread = None
        self._backup_stop_event = threading.Event()
        
        # Backup metrics
        self._backups_created = 0
        self._recoveries_performed = 0
        self._corruptions_detected = 0
        self._auto_repairs_successful = 0
        
        self.logger.info("🛡️ ContextBackupManager initialized")
    
    def start_automatic_backup(self):
        """Start automatic backup background process"""
        if self._backup_thread and self._backup_thread.is_alive():
            self.logger.warning("Automatic backup already running")
            return
        
        self._backup_stop_event.clear()
        self._backup_thread = threading.Thread(target=self._backup_worker, daemon=True)
        self._backup_thread.start()
        
        self.logger.info("🔄 Automatic backup started")
    
    def stop_automatic_backup(self):
        """Stop automatic backup background process"""
        if self._backup_thread:
            self._backup_stop_event.set()
            self._backup_thread.join(timeout=5)
            
        self.logger.info("⏹️ Automatic backup stopped")
    
    def create_backup(self, project_id: str, session_id: Optional[str] = None, 
                     backup_type: BackupType = BackupType.MANUAL) -> Optional[BackupMetadata]:
        """Create a context backup"""
        try:
            self._backups_created += 1
            
            # Load context to backup
            context = self.storage.load_context(project_id, session_id)
            if not context:
                self.logger.error(f"Context not found for backup: {project_id}")
                return None
            
            # Generate backup metadata
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            # Create backup directory structure
            project_backup_dir = self.backup_dir / project_id
            project_backup_dir.mkdir(exist_ok=True)
            
            # Serialize context data
            context_data = context.to_dict()
            context_json = json.dumps(context_data, indent=2)
            
            # Calculate checksum before compression
            checksum = hashlib.sha256(context_json.encode()).hexdigest()
            
            # Compress if enabled
            if self.compression_enabled:
                backup_filename = f"{backup_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json.gz"
                backup_path = project_backup_dir / backup_filename
                
                with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                    f.write(context_json)
                
                compression_ratio = len(context_json) / backup_path.stat().st_size
            else:
                backup_filename = f"{backup_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = project_backup_dir / backup_filename
                
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(context_json)
                
                compression_ratio = 1.0
            
            # Validate backup integrity
            validation_status = self._validate_backup(backup_path, checksum)
            
            # Create backup metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                project_id=project_id,
                session_id=context.session_id,
                backup_type=backup_type,
                timestamp=timestamp,
                size_bytes=backup_path.stat().st_size,
                checksum=checksum,
                compression_ratio=compression_ratio,
                validation_status=validation_status,
                backup_path=backup_path
            )
            
            # Store metadata
            self._store_backup_metadata(metadata)
            
            # Cleanup old backups
            self._cleanup_old_backups(project_id)
            
            # Emit backup observation
            self.emit_observation({
                "type": "context_backup_created",
                "backup_id": backup_id,
                "project_id": project_id,
                "session_id": context.session_id,
                "backup_type": backup_type.value,
                "size_bytes": metadata.size_bytes,
                "compression_ratio": compression_ratio,
                "validation_status": validation_status,
                "backup_timestamp": timestamp.isoformat()
            })
            
            self.logger.info(f"💾 Context backup created: {backup_id}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"💥 Backup creation error: {e}")
            return None
    
    def list_backups(self, project_id: str, limit: int = 20) -> List[BackupMetadata]:
        """List available backups for a project"""
        try:
            with sqlite3.connect(self.metadata_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT backup_data FROM backup_metadata 
                    WHERE project_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (project_id, limit))
                
                backups = []
                for row in cursor.fetchall():
                    backup_data = json.loads(row[0])
                    backups.append(BackupMetadata.from_dict(backup_data))
                
                return backups
                
        except Exception as e:
            self.logger.error(f"💥 Error listing backups: {e}")
            return []
    
    def restore_context(self, backup_id: str, strategy: RecoveryStrategy = RecoveryStrategy.RESTORE_LATEST) -> bool:
        """Restore context from backup"""
        try:
            self._recoveries_performed += 1
            
            # Get backup metadata
            metadata = self._get_backup_metadata(backup_id)
            if not metadata:
                self.logger.error(f"Backup not found: {backup_id}")
                return False
            
            # Load backup data
            context_data = self._load_backup_data(metadata)
            if not context_data:
                self.logger.error(f"Failed to load backup data: {backup_id}")
                return False
            
            # Validate backup integrity
            if not self._verify_backup_integrity(metadata, context_data):
                self.logger.error(f"Backup integrity check failed: {backup_id}")
                return False
            
            # Create context from backup data
            restored_context = SessionContext.from_dict(context_data)
            
            # Apply recovery strategy
            if strategy == RecoveryStrategy.RESTORE_LATEST:
                # Direct restore - replace current context
                success = self.storage.store_context(restored_context)
            
            elif strategy == RecoveryStrategy.MERGE_BACKUPS:
                # Merge with current context if exists
                current_context = self.storage.load_context(metadata.project_id)
                if current_context:
                    merged_context = self._merge_contexts(current_context, restored_context)
                    success = self.storage.store_context(merged_context)
                else:
                    success = self.storage.store_context(restored_context)
            
            elif strategy == RecoveryStrategy.REBUILD_FROM_EVENTS:
                # Rebuild context from event history
                rebuilt_context = self._rebuild_context_from_events(restored_context)
                success = self.storage.store_context(rebuilt_context)
            
            else:
                success = self.storage.store_context(restored_context)
            
            if success:
                # Emit recovery observation
                self.emit_observation({
                    "type": "context_restored_from_backup",
                    "backup_id": backup_id,
                    "project_id": metadata.project_id,
                    "session_id": metadata.session_id,
                    "recovery_strategy": strategy.value,
                    "restore_timestamp": datetime.now().isoformat()
                })
                
                self.logger.info(f"🔄 Context restored from backup: {backup_id}")
                return True
            else:
                self.logger.error(f"Failed to store restored context: {backup_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"💥 Context restore error: {e}")
            return False
    
    def detect_corruption(self, project_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Detect context corruption and suggest recovery options"""
        try:
            corruption_report = {
                "project_id": project_id,
                "session_id": session_id,
                "corruption_detected": False,
                "corruption_types": [],
                "severity": "none",
                "recovery_options": [],
                "recommended_action": "none",
                "detection_timestamp": datetime.now().isoformat()
            }
            
            # Load context for analysis
            context = self.storage.load_context(project_id, session_id)
            if not context:
                corruption_report.update({
                    "corruption_detected": True,
                    "corruption_types": ["missing_context"],
                    "severity": "critical",
                    "recommended_action": "restore_from_backup"
                })
                return corruption_report
            
            # Run validation to detect issues
            validation_result = self.validator.validate_context_integrity(context)
            
            if not validation_result.is_valid:
                self._corruptions_detected += 1
                
                corruption_types = []
                severity = "low"
                
                # Analyze validation errors
                for error in validation_result.errors:
                    if error.severity == ValidationSeverity.CRITICAL:
                        corruption_types.append(f"critical_{error.code}")
                        severity = "critical"
                    elif error.severity == ValidationSeverity.ERROR:
                        corruption_types.append(f"error_{error.code}")
                        if severity != "critical":
                            severity = "high"
                    elif error.severity == ValidationSeverity.WARNING:
                        corruption_types.append(f"warning_{error.code}")
                        if severity not in ["critical", "high"]:
                            severity = "medium"
                
                # Determine recovery options
                recovery_options = self._determine_recovery_options(project_id, corruption_types)
                
                # Recommend action based on severity
                if severity == "critical":
                    recommended_action = "restore_from_backup"
                elif severity == "high":
                    recommended_action = "attempt_auto_repair"
                elif severity == "medium":
                    recommended_action = "manual_review"
                else:
                    recommended_action = "monitor"
                
                corruption_report.update({
                    "corruption_detected": True,
                    "corruption_types": corruption_types,
                    "severity": severity,
                    "recovery_options": recovery_options,
                    "recommended_action": recommended_action,
                    "validation_errors": len(validation_result.errors),
                    "validation_warnings": len(validation_result.warnings)
                })
            
            return corruption_report
            
        except Exception as e:
            self.logger.error(f"💥 Corruption detection error: {e}")
            return {
                "project_id": project_id,
                "corruption_detected": True,
                "corruption_types": ["detection_error"],
                "severity": "unknown",
                "error": str(e)
            }
    
    def attempt_auto_repair(self, project_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Attempt automatic context repair"""
        try:
            repair_report = {
                "project_id": project_id,
                "session_id": session_id,
                "repair_attempted": True,
                "repair_successful": False,
                "repairs_applied": [],
                "remaining_issues": [],
                "repair_timestamp": datetime.now().isoformat()
            }
            
            # Load context
            context = self.storage.load_context(project_id, session_id)
            if not context:
                repair_report["repair_successful"] = False
                repair_report["remaining_issues"] = ["context_not_found"]
                return repair_report
            
            # Run validation to identify issues
            validation_result = self.validator.validate_context_integrity(context)
            
            repairs_applied = []
            
            # Apply automatic repairs
            for error in validation_result.errors:
                if error.code == "missing_timestamps":
                    # Repair missing timestamps
                    self._repair_missing_timestamps(context)
                    repairs_applied.append("missing_timestamps")
                
                elif error.code == "invalid_session_id":
                    # Repair invalid session ID
                    context.session_id = str(uuid.uuid4())
                    repairs_applied.append("invalid_session_id")
                
                elif error.code == "corrupted_conversation_history":
                    # Repair corrupted conversation entries
                    self._repair_conversation_history(context)
                    repairs_applied.append("corrupted_conversation_history")
                
                elif error.code == "invalid_project_state":
                    # Repair project state issues
                    self._repair_project_state(context)
                    repairs_applied.append("invalid_project_state")
            
            # Store repaired context
            if repairs_applied:
                success = self.storage.store_context(context)
                if success:
                    self._auto_repairs_successful += 1
                    
                    # Create backup of repaired context
                    self.create_backup(project_id, context.session_id, BackupType.EMERGENCY)
                    
                    # Re-validate to check remaining issues
                    post_repair_validation = self.validator.validate_context_integrity(context)
                    
                    repair_report.update({
                        "repair_successful": post_repair_validation.is_valid,
                        "repairs_applied": repairs_applied,
                        "remaining_issues": [e.code for e in post_repair_validation.errors]
                    })
                    
                    # Emit repair observation
                    self.emit_observation({
                        "type": "context_auto_repair_completed",
                        "project_id": project_id,
                        "session_id": context.session_id,
                        "repairs_applied": repairs_applied,
                        "repair_successful": post_repair_validation.is_valid,
                        "remaining_issues": len(post_repair_validation.errors),
                        "repair_timestamp": datetime.now().isoformat()
                    })
                    
                    self.logger.info(f"🔧 Auto-repair completed for {project_id}: {len(repairs_applied)} repairs")
                else:
                    repair_report["repair_successful"] = False
                    repair_report["remaining_issues"] = ["storage_error"]
            
            return repair_report
            
        except Exception as e:
            self.logger.error(f"💥 Auto-repair error: {e}")
            return {
                "project_id": project_id,
                "repair_attempted": True,
                "repair_successful": False,
                "error": str(e)
            }
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        try:
            with sqlite3.connect(self.metadata_db) as conn:
                cursor = conn.cursor()
                
                # Total backups
                cursor.execute("SELECT COUNT(*) FROM backup_metadata")
                total_backups = cursor.fetchone()[0]
                
                # Backups by type
                cursor.execute("""
                    SELECT backup_type, COUNT(*) 
                    FROM backup_metadata 
                    GROUP BY backup_type
                """)
                backups_by_type = dict(cursor.fetchall())
                
                # Recent backup activity
                cursor.execute("""
                    SELECT COUNT(*) FROM backup_metadata 
                    WHERE timestamp > datetime('now', '-24 hours')
                """)
                recent_backups = cursor.fetchone()[0]
                
                # Storage usage
                cursor.execute("SELECT SUM(size_bytes) FROM backup_metadata")
                total_storage_bytes = cursor.fetchone()[0] or 0
                
                return {
                    "total_backups": total_backups,
                    "backups_by_type": backups_by_type,
                    "recent_backups_24h": recent_backups,
                    "total_storage_mb": round(total_storage_bytes / 1024 / 1024, 2),
                    "backups_created": self._backups_created,
                    "recoveries_performed": self._recoveries_performed,
                    "corruptions_detected": self._corruptions_detected,
                    "auto_repairs_successful": self._auto_repairs_successful,
                    "backup_directory": str(self.backup_dir),
                    "auto_backup_enabled": self._backup_thread and self._backup_thread.is_alive()
                }
                
        except Exception as e:
            self.logger.error(f"💥 Error getting backup statistics: {e}")
            return {"error": str(e)}
    
    def _init_metadata_db(self):
        """Initialize backup metadata database"""
        with sqlite3.connect(self.metadata_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_metadata (
                    backup_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    compression_ratio REAL NOT NULL,
                    validation_status TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    backup_data TEXT NOT NULL
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_timestamp ON backup_metadata(project_id, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_backup_type ON backup_metadata(backup_type)")
    
    def _backup_worker(self):
        """Background worker for automatic backups"""
        while not self._backup_stop_event.wait(self.auto_backup_interval):
            try:
                # Get list of active projects (this would integrate with project detection)
                active_projects = self._get_active_projects()
                
                for project_id in active_projects:
                    # Check if backup is needed
                    if self._should_create_backup(project_id):
                        self.create_backup(project_id, backup_type=BackupType.AUTOMATIC)
                
            except Exception as e:
                self.logger.error(f"�u Backup worker error: {e}")
    
    def _get_active_projects(self) -> List[str]:
        """Get list of active projects that need backup"""
        # This would integrate with project detection system
        # For now, return projects that have recent context activity
        try:
            active_projects = []
            
            # Scan for projects with recent context files
            context_dirs = [d for d in self.storage.storage_dir.iterdir() if d.is_dir()]
            
            for project_dir in context_dirs:
                project_id = project_dir.name
                context_files = list(project_dir.glob("*.json"))
                
                if context_files:
                    # Check if any context file was modified recently
                    recent_activity = any(
                        (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).total_seconds() < 3600
                        for f in context_files
                    )
                    
                    if recent_activity:
                        active_projects.append(project_id)
            
            return active_projects
            
        except Exception as e:
            self.logger.error(f"� Er ror getting active projects: {e}")
            return []
    
    def _should_create_backup(self, project_id: str) -> bool:
        """Check if a backup should be created for a project"""
        try:
            # Get latest backup for project
            backups = self.list_backups(project_id, limit=1)
            
            if not backups:
                return True  # No backups exist
            
            latest_backup = backups[0]
            
            # Check if enough time has passed since last backup
            time_since_backup = datetime.now() - latest_backup.timestamp
            
            if time_since_backup.total_seconds() > self.auto_backup_interval:
                return True
            
            # Check if context has changed significantly since last backup
            current_context = self.storage.load_context(project_id)
            if current_context:
                current_checksum = self._calculate_context_checksum(current_context)
                if current_checksum != latest_backup.checksum:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"💥 Error checking backup need: {e}")
            return False
    
    def _calculate_context_checksum(self, context: SessionContext) -> str:
        """Calculate checksum for context data"""
        context_json = json.dumps(context.to_dict(), sort_keys=True)
        return hashlib.sha256(context_json.encode()).hexdigest()
    
    def _validate_backup(self, backup_path: Path, expected_checksum: str) -> str:
        """Validate backup file integrity"""
        try:
            # Load backup data
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    backup_data = f.read()
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
            
            # Calculate checksum
            actual_checksum = hashlib.sha256(backup_data.encode()).hexdigest()
            
            if actual_checksum == expected_checksum:
                return "valid"
            else:
                return "checksum_mismatch"
                
        except Exception as e:
            self.logger.error(f"💥 Backup validation error: {e}")
            return "validation_error"
    
    def _store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in database"""
        with sqlite3.connect(self.metadata_db) as conn:
            conn.execute("""
                INSERT INTO backup_metadata 
                (backup_id, project_id, session_id, backup_type, timestamp, 
                 size_bytes, checksum, compression_ratio, validation_status, 
                 backup_path, backup_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.backup_id,
                metadata.project_id,
                metadata.session_id,
                metadata.backup_type.value,
                metadata.timestamp.isoformat(),
                metadata.size_bytes,
                metadata.checksum,
                metadata.compression_ratio,
                metadata.validation_status,
                str(metadata.backup_path),
                json.dumps(metadata.to_dict())
            ))
    
    def _get_backup_metadata(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata by ID"""
        try:
            with sqlite3.connect(self.metadata_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT backup_data FROM backup_metadata 
                    WHERE backup_id = ?
                """, (backup_id,))
                
                row = cursor.fetchone()
                if row:
                    backup_data = json.loads(row[0])
                    return BackupMetadata.from_dict(backup_data)
                
                return None
                
        except Exception as e:
            self.logger.error(f"💥 Error getting backup metadata: {e}")
            return None
    
    def _load_backup_data(self, metadata: BackupMetadata) -> Optional[Dict[str, Any]]:
        """Load context data from backup file"""
        try:
            if not metadata.backup_path.exists():
                self.logger.error(f"Backup file not found: {metadata.backup_path}")
                return None
            
            if metadata.backup_path.suffix == '.gz':
                with gzip.open(metadata.backup_path, 'rt', encoding='utf-8') as f:
                    backup_data = f.read()
            else:
                with open(metadata.backup_path, 'r', encoding='utf-8') as f:
                    backup_data = f.read()
            
            return json.loads(backup_data)
            
        except Exception as e:
            self.logger.error(f"💥 Error loading backup data: {e}")
            return None
    
    def _verify_backup_integrity(self, metadata: BackupMetadata, context_data: Dict[str, Any]) -> bool:
        """Verify backup data integrity"""
        try:
            # Calculate checksum of loaded data
            context_json = json.dumps(context_data, sort_keys=True)
            actual_checksum = hashlib.sha256(context_json.encode()).hexdigest()
            
            return actual_checksum == metadata.checksum
            
        except Exception as e:
            self.logger.error(f"💥 Backup integrity verification error: {e}")
            return False
    
    def _cleanup_old_backups(self, project_id: str):
        """Clean up old backups based on retention policy"""
        try:
            backups = self.list_backups(project_id, limit=1000)  # Get all backups
            
            # Remove backups older than retention period
            cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
            old_backups = [b for b in backups if b.timestamp < cutoff_date]
            
            # Remove excess backups beyond max count
            if len(backups) > self.max_backups_per_project:
                excess_backups = backups[self.max_backups_per_project:]
                old_backups.extend(excess_backups)
            
            # Delete old backup files and metadata
            for backup in old_backups:
                try:
                    if backup.backup_path.exists():
                        backup.backup_path.unlink()
                    
                    # Remove from metadata database
                    with sqlite3.connect(self.metadata_db) as conn:
                        conn.execute("DELETE FROM backup_metadata WHERE backup_id = ?", (backup.backup_id,))
                    
                    self.logger.debug(f"🗑️ Cleaned up old backup: {backup.backup_id}")
                    
                except Exception as e:
                    self.logger.error(f"💥 Error cleaning up backup {backup.backup_id}: {e}")
            
        except Exception as e:
            self.logger.error(f"💥 Backup cleanup error: {e}")
    
    def _determine_recovery_options(self, project_id: str, corruption_types: List[str]) -> List[str]:
        """Determine available recovery options based on corruption types"""
        options = []
        
        # Always offer backup restore if backups exist
        backups = self.list_backups(project_id, limit=1)
        if backups:
            options.append("restore_from_latest_backup")
            options.append("restore_from_specific_backup")
        
        # Offer auto-repair for repairable issues
        repairable_types = ["missing_timestamps", "invalid_session_id", "corrupted_conversation_history"]
        if any(corruption_type.split('_', 1)[-1] in repairable_types for corruption_type in corruption_types):
            options.append("attempt_auto_repair")
        
        # Offer manual repair tools
        options.append("manual_repair_tools")
        
        # Offer context rebuild from events
        options.append("rebuild_from_events")
        
        return options
    
    def _merge_contexts(self, current: SessionContext, backup: SessionContext) -> SessionContext:
        """Merge current context with backup context"""
        # This is a simplified merge - would need more sophisticated logic
        merged = current
        
        # Merge conversation history (keep unique events)
        existing_event_ids = {event.event_id for event in current.conversation_history}
        for event in backup.conversation_history:
            if event.event_id not in existing_event_ids:
                merged.conversation_history.append(event)
        
        # Sort by timestamp
        merged.conversation_history.sort(key=lambda x: x.timestamp)
        
        return merged
    
    def _rebuild_context_from_events(self, context: SessionContext) -> SessionContext:
        """Rebuild context from event history"""
        # This would implement sophisticated context rebuilding logic
        # For now, just return the context as-is
        return context
    
    def _repair_missing_timestamps(self, context: SessionContext):
        """Repair missing timestamps in context"""
        current_time = datetime.now()
        
        for i, event in enumerate(context.conversation_history):
            if not hasattr(event, 'timestamp') or not event.timestamp:
                # Assign incremental timestamps
                event.timestamp = current_time - timedelta(minutes=len(context.conversation_history) - i)
    
    def _repair_conversation_history(self, context: SessionContext):
        """Repair corrupted conversation history"""
        # Remove invalid entries
        valid_events = []
        for event in context.conversation_history:
            if hasattr(event, 'content') and event.content and hasattr(event, 'timestamp'):
                valid_events.append(event)
        
        context.conversation_history = valid_events
    
    def _repair_project_state(self, context: SessionContext):
        """Repair invalid project state"""
        if not hasattr(context, 'project_state') or not context.project_state:
            from .models import ProjectState
            context.project_state = ProjectState(
                current_directory=".",
                running_services=[],
                recent_changes=[],
                environment_variables={},
                git_status={}
            )
    
    def _estimate_compression_potential(self, context: SessionContext) -> float:
        """Estimate compression potential for context"""
        context_json = json.dumps(context.to_dict())
        
        # Simple estimation based on repetitive content
        unique_chars = len(set(context_json))
        total_chars = len(context_json)
        
        if total_chars == 0:
            return 1.0
        
        # Rough compression ratio estimate
        return min(3.0, max(1.0, total_chars / unique_chars / 10))


class ContextRecoveryCLI(BeastlyModule):
    """Command-line interface for context recovery operations"""
    
    def __init__(self, backup_manager: ContextBackupManager):
        super().__init__()
        self.backup_manager = backup_manager
        self.logger.info("🛠️ ContextRecoveryCLI initialized")
    
    def run_recovery_wizard(self, project_id: str) -> Dict[str, Any]:
        """Run interactive recovery wizard"""
        try:
            wizard_result = {
                "project_id": project_id,
                "steps_completed": [],
                "recovery_successful": False,
                "wizard_timestamp": datetime.now().isoformat()
            }
            
            # Step 1: Detect corruption
            self.logger.info("🔍 Step 1: Detecting corruption...")
            corruption_report = self.backup_manager.detect_corruption(project_id)
            wizard_result["steps_completed"].append("corruption_detection")
            wizard_result["corruption_report"] = corruption_report
            
            if not corruption_report["corruption_detected"]:
                wizard_result["recovery_successful"] = True
                wizard_result["message"] = "No corruption detected - context is healthy"
                return wizard_result
            
            # Step 2: List recovery options
            self.logger.info("🔧 Step 2: Analyzing recovery options...")
            recovery_options = corruption_report.get("recovery_options", [])
            wizard_result["steps_completed"].append("options_analysis")
            wizard_result["recovery_options"] = recovery_options
            
            # Step 3: Attempt automatic recovery
            if "attempt_auto_repair" in recovery_options:
                self.logger.info("🤖 Step 3: Attempting automatic repair...")
                repair_result = self.backup_manager.attempt_auto_repair(project_id)
                wizard_result["steps_completed"].append("auto_repair")
                wizard_result["repair_result"] = repair_result
                
                if repair_result.get("repair_successful"):
                    wizard_result["recovery_successful"] = True
                    wizard_result["message"] = "Automatic repair successful"
                    return wizard_result
            
            # Step 4: Backup restore if auto-repair failed
            if "restore_from_latest_backup" in recovery_options:
                self.logger.info("💾 Step 4: Restoring from latest backup...")
                backups = self.backup_manager.list_backups(project_id, limit=1)
                
                if backups:
                    restore_success = self.backup_manager.restore_context(
                        backups[0].backup_id, 
                        RecoveryStrategy.RESTORE_LATEST
                    )
                    wizard_result["steps_completed"].append("backup_restore")
                    wizard_result["restore_successful"] = restore_success
                    
                    if restore_success:
                        wizard_result["recovery_successful"] = True
                        wizard_result["message"] = "Recovery successful via backup restore"
                        return wizard_result
            
            # Recovery failed
            wizard_result["recovery_successful"] = False
            wizard_result["message"] = "Automatic recovery failed - manual intervention required"
            
            return wizard_result
            
        except Exception as e:
            self.logger.error(f"💥 Recovery wizard error: {e}")
            return {
                "project_id": project_id,
                "recovery_successful": False,
                "error": str(e)
            }
    
    def generate_recovery_report(self, project_id: str) -> str:
        """Generate comprehensive recovery report"""
        try:
            report_lines = []
            report_lines.append(f"# Context Recovery Report")
            report_lines.append(f"**Project:** {project_id}")
            report_lines.append(f"**Generated:** {datetime.now().isoformat()}")
            report_lines.append("")
            
            # Corruption analysis
            corruption_report = self.backup_manager.detect_corruption(project_id)
            report_lines.append("## Corruption Analysis")
            report_lines.append(f"- **Corruption Detected:** {corruption_report['corruption_detected']}")
            report_lines.append(f"- **Severity:** {corruption_report.get('severity', 'unknown')}")
            
            if corruption_report.get("corruption_types"):
                report_lines.append("- **Corruption Types:**")
                for corruption_type in corruption_report["corruption_types"]:
                    report_lines.append(f"  - {corruption_type}")
            
            report_lines.append("")
            
            # Available backups
            backups = self.backup_manager.list_backups(project_id, limit=10)
            report_lines.append("## Available Backups")
            
            if backups:
                for backup in backups:
                    report_lines.append(f"- **{backup.backup_id[:8]}** ({backup.backup_type.value})")
                    report_lines.append(f"  - Created: {backup.timestamp.isoformat()}")
                    report_lines.append(f"  - Size: {backup.size_bytes / 1024 / 1024:.2f} MB")
                    report_lines.append(f"  - Status: {backup.validation_status}")
            else:
                report_lines.append("- No backups available")
            
            report_lines.append("")
            
            # Recovery recommendations
            report_lines.append("## Recovery Recommendations")
            recommended_action = corruption_report.get("recommended_action", "none")
            
            if recommended_action == "restore_from_backup":
                report_lines.append("1. **Restore from latest backup** (recommended)")
                report_lines.append("2. Attempt automatic repair")
                report_lines.append("3. Manual recovery tools")
            elif recommended_action == "attempt_auto_repair":
                report_lines.append("1. **Attempt automatic repair** (recommended)")
                report_lines.append("2. Restore from backup if repair fails")
                report_lines.append("3. Manual recovery tools")
            else:
                report_lines.append("1. Monitor context health")
                report_lines.append("2. Create backup for safety")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"Error generating recovery report: {e}"


# CLI Tools Integration
class BackupRecoveryTools:
    """Collection of backup and recovery CLI tools"""
    
    def __init__(self, backup_manager: ContextBackupManager):
        self.backup_manager = backup_manager
        self.cli = ContextRecoveryCLI(backup_manager)
    
    def backup_context(self, project_id: str, backup_type: str = "manual") -> Dict[str, Any]:
        """CLI tool to create context backup"""
        backup_type_enum = BackupType(backup_type.lower())
        metadata = self.backup_manager.create_backup(project_id, backup_type=backup_type_enum)
        
        if metadata:
            return {
                "success": True,
                "backup_id": metadata.backup_id,
                "size_mb": round(metadata.size_bytes / 1024 / 1024, 2),
                "compression_ratio": metadata.compression_ratio
            }
        else:
            return {"success": False, "error": "Backup creation failed"}
    
    def list_backups(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """CLI tool to list available backups"""
        backups = self.backup_manager.list_backups(project_id, limit)
        
        return [
            {
                "backup_id": backup.backup_id[:8],
                "full_backup_id": backup.backup_id,
                "type": backup.backup_type.value,
                "created": backup.timestamp.isoformat(),
                "size_mb": round(backup.size_bytes / 1024 / 1024, 2),
                "status": backup.validation_status
            }
            for backup in backups
        ]
    
    def restore_context(self, backup_id: str, strategy: str = "restore_latest") -> Dict[str, Any]:
        """CLI tool to restore context from backup"""
        strategy_enum = RecoveryStrategy(strategy.lower())
        success = self.backup_manager.restore_context(backup_id, strategy_enum)
        
        return {
            "success": success,
            "backup_id": backup_id,
            "strategy": strategy
        }
    
    def check_corruption(self, project_id: str) -> Dict[str, Any]:
        """CLI tool to check for context corruption"""
        return self.backup_manager.detect_corruption(project_id)
    
    def auto_repair(self, project_id: str) -> Dict[str, Any]:
        """CLI tool to attempt automatic repair"""
        return self.backup_manager.attempt_auto_repair(project_id)
    
    def recovery_wizard(self, project_id: str) -> Dict[str, Any]:
        """CLI tool to run recovery wizard"""
        return self.cli.run_recovery_wizard(project_id)
    
    def backup_stats(self) -> Dict[str, Any]:
        """CLI tool to get backup system statistics"""
        return self.backup_manager.get_backup_statistics()