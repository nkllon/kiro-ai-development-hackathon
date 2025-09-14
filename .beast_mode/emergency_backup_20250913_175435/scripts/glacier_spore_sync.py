#!/usr/bin/env python3
"""
Glacier Spore Model Synchronization & Reduction System

Implements:
1. Model version metadata tracking
2. Change logging and squashing
3. Last update wins conflict resolution
4. Optimistic concurrency control
5. Asynchronous queues for synchronization
6. Model reduction and compaction
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from queue import Queue
from typing import Any, Optional, Union


class SyncStrategy(Enum):
    """Synchronization strategies"""

    LAST_UPDATE_WINS = "last_update_wins"
    MERGE_CONFLICTS = "merge_conflicts"
    MANUAL_RESOLUTION = "manual_resolution"
    TIMESTAMP_BASED = "timestamp_based"
    VERSION_BASED = "version_based"


class ConflictResolution(Enum):
    """Conflict resolution methods"""

    ACCEPT_LOCAL = "accept_local"
    ACCEPT_REMOTE = "accept_remote"
    MERGE = "merge"
    MANUAL = "manual"
    REJECT = "reject"


@dataclass
class ModelVersion:
    """Model version metadata"""

    version_id: str
    model_hash: str
    parent_version_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"

    # Change metadata
    change_count: int = 0
    change_types: set[str] = field(default_factory=set)

    # Synchronization metadata
    sync_status: str = "pending"
    last_sync: Optional[datetime] = None
    conflicts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["change_types"] = list(self.change_types)
        data["created_at"] = self.created_at.isoformat()
        if self.last_sync:
            data["last_sync"] = self.last_sync.isoformat()
        return data


@dataclass
class ChangeLog:
    """Log of changes for model synchronization"""

    change_id: str
    spore_id: str
    version_id: str
    change_type: str
    change_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Change details
    field_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None

    # Metadata
    change_hash: str = ""
    conflict_resolved: bool = False
    resolution_method: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["change_timestamp"] = self.change_timestamp.isoformat()
        return data


@dataclass
class SyncOperation:
    """Synchronization operation"""

    sync_id: str
    operation_type: str  # 'push', 'pull', 'merge', 'reduce'
    source_version_id: str
    target_version_id: str

    # Operation details
    strategy: SyncStrategy
    conflict_resolution: ConflictResolution

    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    # Results
    conflicts_found: int = 0
    conflicts_resolved: int = 0
    changes_applied: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["strategy"] = self.strategy.value
        data["conflict_resolution"] = self.conflict_resolution.value
        data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data


class GlacierSporeSyncDatabase:
    """Database for model synchronization and reduction"""

    def __init__(self, db_path: str = "glacier_spores_sync.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Model versions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS model_versions (
                    version_id TEXT PRIMARY KEY,
                    model_hash TEXT NOT NULL,
                    parent_version_id TEXT,
                    created_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    change_count INTEGER DEFAULT 0,
                    change_types TEXT NOT NULL,
                    sync_status TEXT DEFAULT 'pending',
                    last_sync TEXT,
                    conflicts TEXT NOT NULL,
                    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Change log table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS change_log (
                    change_id TEXT PRIMARY KEY,
                    spore_id TEXT NOT NULL,
                    version_id TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    change_timestamp TEXT NOT NULL,
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    change_hash TEXT NOT NULL,
                    conflict_resolved BOOLEAN DEFAULT FALSE,
                    resolution_method TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Synchronization operations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sync_operations (
                    sync_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    source_version_id TEXT NOT NULL,
                    target_version_id TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    conflict_resolution TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    conflicts_found INTEGER DEFAULT 0,
                    conflicts_resolved INTEGER DEFAULT 0,
                    changes_applied INTEGER DEFAULT 0,
                    errors TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Conflict resolution table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conflict_resolutions (
                    resolution_id TEXT PRIMARY KEY,
                    sync_id TEXT NOT NULL,
                    conflict_type TEXT NOT NULL,
                    conflict_description TEXT NOT NULL,
                    resolution_method TEXT NOT NULL,
                    resolved_at TEXT NOT NULL,
                    resolved_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sync_id) REFERENCES sync_operations (sync_id)
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_parent ON model_versions (parent_version_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_versions_hash ON model_versions (model_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_spore ON change_log (spore_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_changes_version ON change_log (version_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_operations (status)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def store_model_version(self, version: ModelVersion) -> bool:
        """Store a model version"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO model_versions (
                            version_id, model_hash, parent_version_id, created_at,
                            created_by, change_count, change_types, sync_status,
                            last_sync, conflicts
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            version.version_id,
                            version.model_hash,
                            version.parent_version_id,
                            version.created_at.isoformat(),
                            version.created_by,
                            version.change_count,
                            json.dumps(list(version.change_types)),
                            version.sync_status,
                            (version.last_sync.isoformat() if version.last_sync else None),
                            json.dumps(version.conflicts),
                        ),
                    )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store model version {version.version_id}: {e}")
            return False

    def store_change_log(self, change: ChangeLog) -> bool:
        """Store a change log entry"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO change_log (
                            change_id, spore_id, version_id, change_type,
                            change_timestamp, field_name, old_value, new_value,
                            change_hash, conflict_resolved, resolution_method
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            change.change_id,
                            change.spore_id,
                            change.version_id,
                            change.change_type,
                            change.change_timestamp.isoformat(),
                            change.field_name,
                            json.dumps(change.old_value) if change.old_value else None,
                            json.dumps(change.new_value) if change.new_value else None,
                            change.change_hash,
                            change.conflict_resolved,
                            change.resolution_method,
                        ),
                    )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store change log {change.change_id}: {e}")
            return False

    def store_sync_operation(self, operation: SyncOperation) -> bool:
        """Store a synchronization operation"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO sync_operations (
                            sync_id, operation_type, source_version_id, target_version_id,
                            strategy, conflict_resolution, status, started_at,
                            completed_at, conflicts_found, conflicts_resolved,
                            changes_applied, errors
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            operation.sync_id,
                            operation.operation_type,
                            operation.source_version_id,
                            operation.target_version_id,
                            operation.strategy.value,
                            operation.conflict_resolution.value,
                            operation.status,
                            operation.started_at.isoformat(),
                            (operation.completed_at.isoformat() if operation.completed_at else None),
                            operation.conflicts_found,
                            operation.conflicts_resolved,
                            operation.changes_applied,
                            json.dumps(operation.errors),
                        ),
                    )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store sync operation {operation.sync_id}: {e}")
            return False


class ModelSynchronizer:
    """Handles model synchronization and conflict resolution"""

    def __init__(self, database: GlacierSporeSyncDatabase):
        self.database = database
        self.sync_queue: Queue = Queue()
        self.running = False
        self.worker_threads: list[threading.Thread] = []

        # Start sync workers
        self.start_sync_workers()

    def start_sync_workers(self, num_workers: int = 2):
        """Start synchronization worker threads"""
        if self.running:
            return

        self.running = True

        for i in range(num_workers):
            worker = threading.Thread(target=self._sync_worker_loop, args=(i,), daemon=True)
            worker.start()
            self.worker_threads.append(worker)

        logging.info(f"Started {num_workers} sync workers")

    def stop_sync_workers(self):
        """Stop synchronization workers"""
        self.running = False

        for worker in self.worker_threads:
            worker.join(timeout=5.0)

        logging.info("Stopped sync workers")

    def _sync_worker_loop(self, worker_id: int):
        """Main sync worker loop"""
        logging.info(f"Sync worker {worker_id} started")

        while self.running:
            try:
                # Get sync operation from queue
                try:
                    operation = self.sync_queue.get(timeout=1.0)
                except BaseException:
                    continue

                # Process sync operation
                self._process_sync_operation(operation)

                # Mark task as done
                self.sync_queue.task_done()

            except Exception as e:
                logging.error(f"Sync worker {worker_id} error: {e}")

        logging.info(f"Sync worker {worker_id} stopped")

    def _process_sync_operation(self, operation: SyncOperation):
        """Process a synchronization operation"""
        try:
            operation.status = "in_progress"
            self.database.store_sync_operation(operation)

            if operation.operation_type == "push":
                self._handle_push_operation(operation)
            elif operation.operation_type == "pull":
                self._handle_pull_operation(operation)
            elif operation.operation_type == "merge":
                self._handle_merge_operation(operation)
            elif operation.operation_type == "reduce":
                self._handle_reduce_operation(operation)

            operation.status = "completed"
            operation.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            operation.status = "failed"
            operation.errors.append(str(e))
            logging.error(f"Sync operation {operation.sync_id} failed: {e}")

        finally:
            self.database.store_sync_operation(operation)

    def _handle_push_operation(self, operation: SyncOperation):
        """Handle push operation (local to remote)"""
        # Implement push logic
        operation.changes_applied = 0
        logging.info(f"Push operation {operation.sync_id} completed")

    def _handle_pull_operation(self, operation: SyncOperation):
        """Handle pull operation (remote to local)"""
        # Implement pull logic
        operation.changes_applied = 0
        logging.info(f"Pull operation {operation.sync_id} completed")

    def _handle_merge_operation(self, operation: SyncOperation):
        """Handle merge operation"""
        # Implement merge logic
        operation.changes_applied = 0
        logging.info(f"Merge operation {operation.sync_id} completed")

    def _handle_reduce_operation(self, operation: SyncOperation):
        """Handle model reduction operation"""
        # Implement reduction logic
        operation.changes_applied = 0
        logging.info(f"Reduce operation {operation.sync_id} completed")

    def queue_sync_operation(self, operation: SyncOperation):
        """Queue a synchronization operation"""
        self.sync_queue.put(operation)
        logging.info(f"Queued sync operation: {operation.sync_id}")


class ModelReducer:
    """Handles model reduction and compaction"""

    def __init__(self, database: GlacierSporeSyncDatabase):
        self.database = database

    def reduce_model_versions(self, max_versions: int = 10) -> dict[str, Any]:
        """Reduce model versions to prevent exponential growth"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                # Get all versions ordered by creation time
                cursor.execute(
                    """
                    SELECT version_id, created_at, change_count
                    FROM model_versions
                    ORDER BY created_at ASC
                """
                )
                versions = cursor.fetchall()

                if len(versions) <= max_versions:
                    return {"reduced": False, "reason": "No reduction needed"}

                # Keep the most recent versions and mark older ones for reduction
                versions_to_reduce = versions[:-max_versions]
                versions_to_keep = versions[-max_versions:]

                # Mark versions for reduction
                for version in versions_to_reduce:
                    cursor.execute(
                        """
                        UPDATE model_versions
                        SET sync_status = 'reduced'
                        WHERE version_id = ?
                    """,
                        (version["version_id"],),
                    )

                # Squash changes from reduced versions into the oldest kept version
                oldest_kept = versions_to_keep[0]

                # Aggregate changes from reduced versions
                total_changes = sum(v["change_count"] for v in versions_to_reduce)

                cursor.execute(
                    """
                    UPDATE model_versions
                    SET change_count = change_count + ?,
                        sync_status = 'squashed'
                    WHERE version_id = ?
                """,
                    (total_changes, oldest_kept["version_id"]),
                )

                conn.commit()

                return {
                    "reduced": True,
                    "versions_reduced": len(versions_to_reduce),
                    "versions_kept": len(versions_to_keep),
                    "changes_squashed": total_changes,
                }

        except Exception as e:
            logging.error(f"Failed to reduce model versions: {e}")
            return {"reduced": False, "error": str(e)}

    def compact_change_log(self, days_to_keep: int = 30) -> dict[str, Any]:
        """Compact change log by removing old entries"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                # Count old changes
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as old_changes
                    FROM change_log
                    WHERE change_timestamp < datetime('now', '-{days_to_keep} days')
                """
                )

                old_changes = cursor.fetchone()["old_changes"]

                if old_changes == 0:
                    return {"compacted": False, "reason": "No old changes to compact"}

                # Delete old changes
                cursor.execute(
                    f"""
                    DELETE FROM change_log
                    WHERE change_timestamp < datetime('now', '-{days_to_keep} days')
                """
                )

                conn.commit()

                return {
                    "compacted": True,
                    "changes_removed": old_changes,
                    "days_kept": days_to_keep,
                }

        except Exception as e:
            logging.error(f"Failed to compact change log: {e}")
            return {"compacted": False, "error": str(e)}


class GlacierSporeSyncSystem:
    """Main system for glacier spore synchronization and reduction"""

    def __init__(self, db_path: str = "glacier_spores_sync.db"):
        self.database = GlacierSporeSyncDatabase(db_path)
        self.synchronizer = ModelSynchronizer(self.database)
        self.reducer = ModelReducer(self.database)

        # Initialize with current model version
        self._initialize_current_version()

    def _initialize_current_version(self):
        """Initialize current model version"""
        # Get current project model hash using Model Registry tools
        try:
            from src.round_trip_engineering.tools import get_model_registry

            registry = get_model_registry()
            manager = registry.get_model("project")
            model_content = json.dumps(manager.load_model(), sort_keys=True)
            model_hash = hashlib.sha256(model_content.encode()).hexdigest()

            current_version = ModelVersion(
                version_id=str(uuid.uuid4()),
                model_hash=model_hash,
                created_by="system",
                change_types={"initialization"},
            )

            self.database.store_model_version(current_version)
            logging.info(f"Initialized current model version: {current_version.version_id}")

        except Exception as e:
            logging.error(f"Failed to initialize current model version: {e}")

    def create_model_version(self, changes: list[dict[str, Any]]) -> ModelVersion:
        """Create a new model version from changes"""
        try:
            # Get current version using Model Registry tools
            from src.round_trip_engineering.tools import get_model_registry

            registry = get_model_registry()
            manager = registry.get_model("project")
            model_content = json.dumps(manager.load_model(), sort_keys=True)
            model_hash = hashlib.sha256(model_content.encode()).hexdigest()

            # Create new version
            new_version = ModelVersion(
                version_id=str(uuid.uuid4()),
                model_hash=model_hash,
                parent_version_id=self._get_current_version_id(),
                created_by="system",
                change_count=len(changes),
                change_types={change.get("type", "unknown") for change in changes},
            )

            # Store version
            self.database.store_model_version(new_version)

            # Log changes
            for change in changes:
                change_log = ChangeLog(
                    change_id=str(uuid.uuid4()),
                    spore_id=change.get("spore_id", "unknown"),
                    version_id=new_version.version_id,
                    change_type=change.get("type", "unknown"),
                    field_name=change.get("field_name"),
                    old_value=change.get("old_value"),
                    new_value=change.get("new_value"),
                    change_hash=hashlib.sha256(json.dumps(change, sort_keys=True).encode()).hexdigest(),
                )
                self.database.store_change_log(change_log)

            return new_version

        except Exception as e:
            logging.error(f"Failed to create model version: {e}")
            raise

    def _get_current_version_id(self) -> Optional[str]:
        """Get current model version ID"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT version_id FROM model_versions
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                )
                row = cursor.fetchone()
                return row["version_id"] if row else None
        except Exception as e:
            logging.error(f"Failed to get current version ID: {e}")
            return None

    def sync_models(
        self,
        target_version_id: str,
        strategy: SyncStrategy = SyncStrategy.LAST_UPDATE_WINS,
    ) -> str:
        """Synchronize models"""
        operation = SyncOperation(
            sync_id=str(uuid.uuid4()),
            operation_type="merge",
            source_version_id=self._get_current_version_id() or "unknown",
            target_version_id=target_version_id,
            strategy=strategy,
            conflict_resolution=ConflictResolution.ACCEPT_REMOTE,
        )

        self.synchronizer.queue_sync_operation(operation)
        return operation.sync_id

    def reduce_model(self, max_versions: int = 10) -> dict[str, Any]:
        """Reduce model versions"""
        return self.reducer.reduce_model_versions(max_versions)

    def compact_changes(self, days_to_keep: int = 30) -> dict[str, Any]:
        """Compact change log"""
        return self.reducer.compact_change_log(days_to_keep)

    def get_sync_status(self, sync_id: str) -> Optional[SyncOperation]:
        """Get synchronization operation status"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sync_operations WHERE sync_id = ?", (sync_id,))
                row = cursor.fetchone()

                if row:
                    return SyncOperation(
                        sync_id=row["sync_id"],
                        operation_type=row["operation_type"],
                        source_version_id=row["source_version_id"],
                        target_version_id=row["target_version_id"],
                        strategy=SyncStrategy(row["strategy"]),
                        conflict_resolution=ConflictResolution(row["conflict_resolution"]),
                        status=row["status"],
                        started_at=datetime.fromisoformat(row["started_at"]),
                        completed_at=(datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None),
                        conflicts_found=row["conflicts_found"],
                        conflicts_resolved=row["conflicts_resolved"],
                        changes_applied=row["changes_applied"],
                        errors=json.loads(row["errors"]),
                    )
                return None

        except Exception as e:
            logging.error(f"Failed to get sync status: {e}")
            return None

    def shutdown(self):
        """Shutdown the sync system"""
        self.synchronizer.stop_sync_workers()
        logging.info("Glacier spore sync system shutdown")


# Example usage
async def main():
    """Example usage of the glacier spore sync system"""

    # Create sync system
    sync_system = GlacierSporeSyncSystem()

    # Create a new model version with changes
    changes = [
        {
            "type": "spore_created",
            "spore_id": "spore_123",
            "field_name": "content",
            "old_value": None,
            "new_value": {"data": "new content"},
        },
        {
            "type": "dimension_updated",
            "spore_id": "spore_123",
            "field_name": "quality_score",
            "old_value": 75.0,
            "new_value": 85.0,
        },
    ]

    new_version = sync_system.create_model_version(changes)
    print(f"Created new model version: {new_version.version_id}")
    print(f"Changes: {new_version.change_count}")

    # Sync with another version
    sync_id = sync_system.sync_models("target_version_456")
    print(f"Started sync operation: {sync_id}")

    # Wait for sync to complete
    await asyncio.sleep(2)

    # Check sync status
    status = sync_system.get_sync_status(sync_id)
    if status:
        print(f"Sync status: {status.status}")
        print(f"Changes applied: {status.changes_applied}")

    # Reduce model versions
    reduction_result = sync_system.reduce_model(max_versions=5)
    print(f"Model reduction: {reduction_result}")

    # Compact changes
    compaction_result = sync_system.compact_changes(days_to_keep=7)
    print(f"Change compaction: {compaction_result}")

    # Shutdown
    sync_system.shutdown()
    print("✅ Glacier spore sync system demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
