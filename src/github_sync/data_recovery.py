"""
Data recovery and state management for GitHub synchronization.

This module provides synchronization state persistence, data corruption detection,
and recovery mechanisms for synchronized GitHub data.
"""

import os
import json
import sqlite3
import hashlib
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import pickle
import gzip

logger = logging.getLogger(__name__)


class SyncState(Enum):
    """Synchronization states."""
    IDLE = "idle"
    SYNCING = "syncing"
    FAILED = "failed"
    RECOVERING = "recovering"
    CORRUPTED = "corrupted"


class RecoveryAction(Enum):
    """Recovery actions."""
    RETRY = "retry"
    RESTORE_BACKUP = "restore_backup"
    FULL_RESYNC = "full_resync"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class SyncStateInfo:
    """Synchronization state information."""
    repository_id: str
    state: SyncState
    last_sync_time: Optional[datetime]
    last_success_time: Optional[datetime]
    error_count: int
    last_error: Optional[str]
    sync_progress: Dict[str, Any]
    checksum: Optional[str]


@dataclass
class BackupInfo:
    """Backup information."""
    backup_id: str
    repository_id: str
    backup_time: datetime
    backup_path: Path
    data_types: List[str]
    size_bytes: int
    checksum: str


@dataclass
class CorruptionReport:
    """Data corruption report."""
    repository_id: str
    corruption_type: str
    affected_tables: List[str]
    affected_files: List[str]
    detection_time: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'
    recovery_action: RecoveryAction


class DataRecoveryManager:
    """
    Manages data recovery and synchronization state persistence.
    
    This class provides mechanisms for detecting data corruption,
    creating backups, and recovering from various failure scenarios.
    """
    
    def __init__(self, data_dir: str):
        """
        Initialize data recovery manager.
        
        Args:
            data_dir: Directory for storing recovery data
        """
        self.data_dir = Path(data_dir)
        self.state_dir = self.data_dir / "state"
        self.backup_dir = self.data_dir / "backups"
        self.recovery_dir = self.data_dir / "recovery"
        
        # Create directories
        for directory in [self.data_dir, self.state_dir, self.backup_dir, self.recovery_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize state database
        self.state_db_path = self.state_dir / "sync_state.db"
        self._init_state_database()
    
    def _init_state_database(self):
        """Initialize the synchronization state database."""
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sync_states (
                        repository_id TEXT PRIMARY KEY,
                        state TEXT NOT NULL,
                        last_sync_time TEXT,
                        last_success_time TEXT,
                        error_count INTEGER DEFAULT 0,
                        last_error TEXT,
                        sync_progress TEXT,
                        checksum TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS backups (
                        backup_id TEXT PRIMARY KEY,
                        repository_id TEXT NOT NULL,
                        backup_time TEXT NOT NULL,
                        backup_path TEXT NOT NULL,
                        data_types TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        checksum TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS corruption_reports (
                        report_id TEXT PRIMARY KEY,
                        repository_id TEXT NOT NULL,
                        corruption_type TEXT NOT NULL,
                        affected_tables TEXT NOT NULL,
                        affected_files TEXT NOT NULL,
                        detection_time TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        recovery_action TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize state database: {e}")
            raise
    
    def get_sync_state(self, repository_id: str) -> Optional[SyncStateInfo]:
        """
        Get synchronization state for a repository.
        
        Args:
            repository_id: Repository identifier
            
        Returns:
            SyncStateInfo object or None if not found
        """
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sync_states WHERE repository_id = ?",
                    (repository_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Parse datetime fields
                last_sync_time = None
                if row['last_sync_time']:
                    last_sync_time = datetime.fromisoformat(row['last_sync_time'])
                
                last_success_time = None
                if row['last_success_time']:
                    last_success_time = datetime.fromisoformat(row['last_success_time'])
                
                # Parse sync progress
                sync_progress = {}
                if row['sync_progress']:
                    sync_progress = json.loads(row['sync_progress'])
                
                return SyncStateInfo(
                    repository_id=row['repository_id'],
                    state=SyncState(row['state']),
                    last_sync_time=last_sync_time,
                    last_success_time=last_success_time,
                    error_count=row['error_count'],
                    last_error=row['last_error'],
                    sync_progress=sync_progress,
                    checksum=row['checksum']
                )
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get sync state for {repository_id}: {e}")
            return None
    
    def update_sync_state(self, state_info: SyncStateInfo):
        """
        Update synchronization state for a repository.
        
        Args:
            state_info: Updated state information
        """
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                # Convert datetime objects to ISO format
                last_sync_time = None
                if state_info.last_sync_time:
                    last_sync_time = state_info.last_sync_time.isoformat()
                
                last_success_time = None
                if state_info.last_success_time:
                    last_success_time = state_info.last_success_time.isoformat()
                
                # Convert sync progress to JSON
                sync_progress_json = json.dumps(state_info.sync_progress)
                
                conn.execute("""
                    INSERT OR REPLACE INTO sync_states 
                    (repository_id, state, last_sync_time, last_success_time, 
                     error_count, last_error, sync_progress, checksum, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    state_info.repository_id,
                    state_info.state.value,
                    last_sync_time,
                    last_success_time,
                    state_info.error_count,
                    state_info.last_error,
                    sync_progress_json,
                    state_info.checksum
                ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update sync state for {state_info.repository_id}: {e}")
            raise
    
    def create_backup(self, repository_id: str, data_path: Path, 
                     data_types: List[str]) -> Optional[BackupInfo]:
        """
        Create a backup of repository data.
        
        Args:
            repository_id: Repository identifier
            data_path: Path to data to backup
            data_types: Types of data being backed up
            
        Returns:
            BackupInfo object or None if backup failed
        """
        try:
            # Generate backup ID and ensure repository-specific backup directory exists
            backup_id = f"{repository_id.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            repo_backup_dir = self.backup_dir / repository_id.replace('/', '_')
            repo_backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_path = repo_backup_dir / f"{backup_id}.backup"
            
            # Create compressed backup
            with gzip.open(backup_path, 'wb') as backup_file:
                if data_path.is_file():
                    # Backup single file
                    with open(data_path, 'rb') as source_file:
                        shutil.copyfileobj(source_file, backup_file)
                elif data_path.is_dir():
                    # Backup directory structure
                    backup_data = self._serialize_directory(data_path)
                    pickle.dump(backup_data, backup_file)
                else:
                    self.logger.error(f"Invalid data path for backup: {data_path}")
                    return None
            
            # Calculate backup size and checksum
            size_bytes = backup_path.stat().st_size
            checksum = self._calculate_file_checksum(backup_path)
            
            # Create backup info
            backup_info = BackupInfo(
                backup_id=backup_id,
                repository_id=repository_id,
                backup_time=datetime.now(),
                backup_path=backup_path,
                data_types=data_types,
                size_bytes=size_bytes,
                checksum=checksum
            )
            
            # Store backup info in database
            self._store_backup_info(backup_info)
            
            self.logger.info(f"Created backup {backup_id} for repository {repository_id}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {repository_id}: {e}")
            return None
    
    def _serialize_directory(self, directory: Path) -> Dict[str, Any]:
        """
        Serialize directory structure for backup.
        
        Args:
            directory: Directory to serialize
            
        Returns:
            Serialized directory data
        """
        data = {
            'type': 'directory',
            'name': directory.name,
            'files': {},
            'subdirs': {}
        }
        
        for item in directory.iterdir():
            if item.is_file():
                with open(item, 'rb') as f:
                    data['files'][item.name] = f.read()
            elif item.is_dir():
                data['subdirs'][item.name] = self._serialize_directory(item)
        
        return data
    
    def _store_backup_info(self, backup_info: BackupInfo):
        """Store backup information in database."""
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.execute("""
                    INSERT INTO backups 
                    (backup_id, repository_id, backup_time, backup_path, 
                     data_types, size_bytes, checksum)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    backup_info.backup_id,
                    backup_info.repository_id,
                    backup_info.backup_time.isoformat(),
                    str(backup_info.backup_path),
                    json.dumps(backup_info.data_types),
                    backup_info.size_bytes,
                    backup_info.checksum
                ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store backup info: {e}")
            raise
    
    def restore_backup(self, backup_id: str, restore_path: Path) -> bool:
        """
        Restore data from a backup.
        
        Args:
            backup_id: Backup identifier
            restore_path: Path to restore data to
            
        Returns:
            True if restore was successful
        """
        try:
            # Get backup info
            backup_info = self.get_backup_info(backup_id)
            if not backup_info:
                self.logger.error(f"Backup {backup_id} not found")
                return False
            
            # Verify backup integrity
            if not self._verify_backup_integrity(backup_info):
                self.logger.error(f"Backup {backup_id} integrity check failed")
                return False
            
            # Create restore directory
            restore_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore from compressed backup
            with gzip.open(backup_info.backup_path, 'rb') as backup_file:
                if 'directory' in backup_info.data_types:
                    # Restore directory structure
                    backup_data = pickle.load(backup_file)
                    self._restore_directory(backup_data, restore_path)
                else:
                    # Restore single file
                    with open(restore_path, 'wb') as restore_file:
                        shutil.copyfileobj(backup_file, restore_file)
            
            self.logger.info(f"Restored backup {backup_id} to {restore_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_id}: {e}")
            return False
    
    def _restore_directory(self, backup_data: Dict[str, Any], restore_path: Path):
        """
        Restore directory structure from backup data.
        
        Args:
            backup_data: Serialized directory data
            restore_path: Path to restore to
        """
        restore_path.mkdir(parents=True, exist_ok=True)
        
        # Restore files
        for filename, file_data in backup_data.get('files', {}).items():
            file_path = restore_path / filename
            with open(file_path, 'wb') as f:
                f.write(file_data)
        
        # Restore subdirectories
        for dirname, subdir_data in backup_data.get('subdirs', {}).items():
            subdir_path = restore_path / dirname
            self._restore_directory(subdir_data, subdir_path)
    
    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """
        Get backup information.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            BackupInfo object or None if not found
        """
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM backups WHERE backup_id = ?",
                    (backup_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return BackupInfo(
                    backup_id=row['backup_id'],
                    repository_id=row['repository_id'],
                    backup_time=datetime.fromisoformat(row['backup_time']),
                    backup_path=Path(row['backup_path']),
                    data_types=json.loads(row['data_types']),
                    size_bytes=row['size_bytes'],
                    checksum=row['checksum']
                )
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get backup info for {backup_id}: {e}")
            return None
    
    def list_backups(self, repository_id: Optional[str] = None) -> List[BackupInfo]:
        """
        List available backups.
        
        Args:
            repository_id: Optional repository filter
            
        Returns:
            List of BackupInfo objects
        """
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if repository_id:
                    cursor = conn.execute(
                        "SELECT * FROM backups WHERE repository_id = ? ORDER BY backup_time DESC",
                        (repository_id,)
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM backups ORDER BY backup_time DESC"
                    )
                
                backups = []
                for row in cursor.fetchall():
                    backups.append(BackupInfo(
                        backup_id=row['backup_id'],
                        repository_id=row['repository_id'],
                        backup_time=datetime.fromisoformat(row['backup_time']),
                        backup_path=Path(row['backup_path']),
                        data_types=json.loads(row['data_types']),
                        size_bytes=row['size_bytes'],
                        checksum=row['checksum']
                    ))
                
                return backups
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []
    
    def detect_data_corruption(self, repository_id: str, data_path: Path) -> Optional[CorruptionReport]:
        """
        Detect data corruption in repository data.
        
        Args:
            repository_id: Repository identifier
            data_path: Path to data to check
            
        Returns:
            CorruptionReport if corruption detected, None otherwise
        """
        try:
            corruption_issues = []
            affected_tables = []
            affected_files = []
            
            # Check file integrity
            if data_path.is_file():
                if not self._verify_file_integrity(data_path):
                    affected_files.append(str(data_path))
                    corruption_issues.append("file_corruption")
            
            # Check database integrity if SQLite database
            if data_path.suffix == '.db':
                db_issues = self._check_database_integrity(data_path)
                if db_issues:
                    affected_tables.extend(db_issues)
                    corruption_issues.append("database_corruption")
            
            # Check directory structure
            if data_path.is_dir():
                structure_issues = self._check_directory_structure(data_path)
                if structure_issues:
                    affected_files.extend(structure_issues)
                    corruption_issues.append("structure_corruption")
            
            # If no corruption detected
            if not corruption_issues:
                return None
            
            # Determine severity and recovery action
            severity = self._assess_corruption_severity(corruption_issues, affected_tables, affected_files)
            recovery_action = self._determine_recovery_action(severity, corruption_issues)
            
            # Create corruption report
            report = CorruptionReport(
                repository_id=repository_id,
                corruption_type=", ".join(corruption_issues),
                affected_tables=affected_tables,
                affected_files=affected_files,
                detection_time=datetime.now(),
                severity=severity,
                recovery_action=recovery_action
            )
            
            # Store corruption report
            self._store_corruption_report(report)
            
            self.logger.warning(f"Data corruption detected for {repository_id}: {report.corruption_type}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error detecting corruption for {repository_id}: {e}")
            return None
    
    def _verify_file_integrity(self, file_path: Path) -> bool:
        """Verify file integrity using basic checks."""
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False
            
            # Try to read the file
            with open(file_path, 'rb') as f:
                f.read(1024)  # Read first 1KB to check accessibility
            
            return True
            
        except Exception:
            return False
    
    def _check_database_integrity(self, db_path: Path) -> List[str]:
        """Check SQLite database integrity."""
        affected_tables = []
        
        try:
            with sqlite3.connect(db_path) as conn:
                # Run integrity check
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                
                if result and result[0] != "ok":
                    # Get list of tables
                    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    affected_tables.extend(tables)
                
        except sqlite3.Error:
            # If we can't even connect, assume all tables are affected
            affected_tables.append("all_tables")
        
        return affected_tables
    
    def _check_directory_structure(self, dir_path: Path) -> List[str]:
        """Check directory structure for issues."""
        issues = []
        
        try:
            # Check if directory is accessible
            if not dir_path.exists() or not dir_path.is_dir():
                issues.append(str(dir_path))
                return issues
            
            # Check for empty directories that should have content
            if not any(dir_path.iterdir()):
                issues.append(f"{dir_path} (empty)")
            
            # Check for permission issues
            for item in dir_path.rglob("*"):
                if not os.access(item, os.R_OK):
                    issues.append(f"{item} (permission_denied)")
        
        except Exception as e:
            issues.append(f"{dir_path} (access_error: {e})")
        
        return issues
    
    def _assess_corruption_severity(self, corruption_issues: List[str], 
                                  affected_tables: List[str], 
                                  affected_files: List[str]) -> str:
        """Assess the severity of data corruption."""
        # Critical: Database corruption or many files affected
        if "database_corruption" in corruption_issues or len(affected_files) > 10:
            return "critical"
        
        # High: Multiple types of corruption
        if len(corruption_issues) > 1:
            return "high"
        
        # Medium: Single type affecting multiple files
        if len(affected_files) > 3:
            return "medium"
        
        # Low: Minor issues
        return "low"
    
    def _determine_recovery_action(self, severity: str, corruption_issues: List[str]) -> RecoveryAction:
        """Determine appropriate recovery action."""
        if severity == "critical":
            return RecoveryAction.FULL_RESYNC
        elif severity == "high":
            return RecoveryAction.RESTORE_BACKUP
        elif "database_corruption" in corruption_issues:
            return RecoveryAction.RESTORE_BACKUP
        else:
            return RecoveryAction.RETRY
    
    def _store_corruption_report(self, report: CorruptionReport):
        """Store corruption report in database."""
        try:
            report_id = f"{report.repository_id}_{report.detection_time.strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.state_db_path) as conn:
                conn.execute("""
                    INSERT INTO corruption_reports 
                    (report_id, repository_id, corruption_type, affected_tables, 
                     affected_files, detection_time, severity, recovery_action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id,
                    report.repository_id,
                    report.corruption_type,
                    json.dumps(report.affected_tables),
                    json.dumps(report.affected_files),
                    report.detection_time.isoformat(),
                    report.severity,
                    report.recovery_action.value
                ))
                
                conn.commit()
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store corruption report: {e}")
    
    def _verify_backup_integrity(self, backup_info: BackupInfo) -> bool:
        """Verify backup file integrity."""
        try:
            # Check if backup file exists
            if not backup_info.backup_path.exists():
                return False
            
            # Verify checksum
            current_checksum = self._calculate_file_checksum(backup_info.backup_path)
            if current_checksum != backup_info.checksum:
                return False
            
            # Try to open the backup file
            with gzip.open(backup_info.backup_path, 'rb') as f:
                f.read(1024)  # Read first 1KB to verify it's readable
            
            return True
            
        except Exception:
            return False
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """
        Clean up old backups beyond retention period.
        
        Args:
            retention_days: Number of days to retain backups
            
        Returns:
            Number of backups cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with sqlite3.connect(self.state_db_path) as conn:
                # Get old backups
                cursor = conn.execute(
                    "SELECT backup_id, backup_path FROM backups WHERE backup_time < ?",
                    (cutoff_date.isoformat(),)
                )
                old_backups = cursor.fetchall()
                
                cleaned_count = 0
                for backup_id, backup_path in old_backups:
                    try:
                        # Remove backup file
                        Path(backup_path).unlink(missing_ok=True)
                        
                        # Remove from database
                        conn.execute("DELETE FROM backups WHERE backup_id = ?", (backup_id,))
                        cleaned_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to clean up backup {backup_id}: {e}")
                
                conn.commit()
                
                if cleaned_count > 0:
                    self.logger.info(f"Cleaned up {cleaned_count} old backups")
                
                return cleaned_count
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def get_recovery_status(self, repository_id: str) -> Dict[str, Any]:
        """
        Get comprehensive recovery status for a repository.
        
        Args:
            repository_id: Repository identifier
            
        Returns:
            Dictionary with recovery status information
        """
        sync_state = self.get_sync_state(repository_id)
        backups = self.list_backups(repository_id)
        
        # Get recent corruption reports
        try:
            with sqlite3.connect(self.state_db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM corruption_reports 
                    WHERE repository_id = ? AND resolved = FALSE
                    ORDER BY detection_time DESC LIMIT 5
                """, (repository_id,))
                
                corruption_reports = []
                for row in cursor.fetchall():
                    corruption_reports.append({
                        'corruption_type': row['corruption_type'],
                        'severity': row['severity'],
                        'detection_time': row['detection_time'],
                        'recovery_action': row['recovery_action']
                    })
        
        except sqlite3.Error:
            corruption_reports = []
        
        return {
            'repository_id': repository_id,
            'sync_state': sync_state.state.value if sync_state else 'unknown',
            'last_sync': sync_state.last_sync_time.isoformat() if sync_state and sync_state.last_sync_time else None,
            'last_success': sync_state.last_success_time.isoformat() if sync_state and sync_state.last_success_time else None,
            'error_count': sync_state.error_count if sync_state else 0,
            'backup_count': len(backups),
            'latest_backup': backups[0].backup_time.isoformat() if backups else None,
            'corruption_reports': corruption_reports,
            'recovery_needed': len(corruption_reports) > 0 or (sync_state and sync_state.state in [SyncState.FAILED, SyncState.CORRUPTED])
        }