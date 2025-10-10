"""
Storage layer for AI Memory Palace context persistence.

Implements SQLite database schema with versioning support and migration system
for persistent storage and retrieval of conversation context.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from .models import SessionContext, ContextEvent


class ContextDatabase:
    """SQLite database for context storage with versioning and migrations"""
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str = ".kiro/context/context.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            # Create schema version table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check current schema version
            current_version = self._get_schema_version(conn)
            
            if current_version < self.SCHEMA_VERSION:
                self._apply_migrations(conn, current_version)
    
    def _get_schema_version(self, conn: sqlite3.Connection) -> int:
        """Get current schema version"""
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    
    def _apply_migrations(self, conn: sqlite3.Connection, from_version: int):
        """Apply database migrations"""
        migrations = {
            0: self._migration_v0_to_v1
        }
        
        for version in range(from_version, self.SCHEMA_VERSION):
            if version in migrations:
                migrations[version](conn)
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (version + 1,)
                )
    
    def _migration_v0_to_v1(self, conn: sqlite3.Connection):
        """Initial schema creation"""
        # Session contexts table
        conn.execute("""
            CREATE TABLE session_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                session_id TEXT NOT NULL UNIQUE,
                timestamp TIMESTAMP NOT NULL,
                context_data TEXT NOT NULL,
                context_size INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Context events table
        conn.execute("""
            CREATE TABLE context_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                correlation_id TEXT NOT NULL,
                event_data TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES session_contexts (session_id)
            )
        """)
        
        # Context versions table for history
        conn.execute("""
            CREATE TABLE context_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                context_data TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES session_contexts (session_id),
                UNIQUE(session_id, version_number)
            )
        """)
        
        # Project metadata table
        conn.execute("""
            CREATE TABLE project_metadata (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                project_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sessions INTEGER DEFAULT 0,
                total_context_size INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX idx_session_contexts_project_id ON session_contexts (project_id)")
        conn.execute("CREATE INDEX idx_session_contexts_timestamp ON session_contexts (timestamp)")
        conn.execute("CREATE INDEX idx_context_events_session_id ON context_events (session_id)")
        conn.execute("CREATE INDEX idx_context_events_timestamp ON context_events (timestamp)")
        conn.execute("CREATE INDEX idx_context_events_correlation_id ON context_events (correlation_id)")
        conn.execute("CREATE INDEX idx_context_versions_session_id ON context_versions (session_id)")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def store_session_context(self, context: SessionContext) -> bool:
        """Store session context with versioning"""
        try:
            context_json = context.to_json()
            checksum = self._calculate_checksum(context_json)
            
            with self.get_connection() as conn:
                # Store or update main context
                conn.execute("""
                    INSERT OR REPLACE INTO session_contexts 
                    (project_id, session_id, timestamp, context_data, context_size, checksum, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    context.project_id,
                    context.session_id,
                    context.timestamp.isoformat(),
                    context_json,
                    len(context_json),
                    checksum
                ))
                
                # Create version entry
                version_number = self._get_next_version_number(conn, context.session_id)
                conn.execute("""
                    INSERT INTO context_versions 
                    (session_id, version_number, context_data, checksum)
                    VALUES (?, ?, ?, ?)
                """, (context.session_id, version_number, context_json, checksum))
                
                # Update project metadata
                self._update_project_metadata(conn, context.project_id, len(context_json))
                
            return True
        except Exception as e:
            print(f"Error storing session context: {e}")
            return False
    
    def load_session_context(self, project_id: str, session_id: Optional[str] = None) -> Optional[SessionContext]:
        """Load session context, latest if session_id not specified"""
        try:
            with self.get_connection() as conn:
                if session_id:
                    cursor = conn.execute("""
                        SELECT context_data, checksum FROM session_contexts 
                        WHERE session_id = ?
                    """, (session_id,))
                else:
                    cursor = conn.execute("""
                        SELECT context_data, checksum FROM session_contexts 
                        WHERE project_id = ? 
                        ORDER BY timestamp DESC LIMIT 1
                    """, (project_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Verify checksum
                context_data = row['context_data']
                stored_checksum = row['checksum']
                calculated_checksum = self._calculate_checksum(context_data)
                
                if stored_checksum != calculated_checksum:
                    print(f"Warning: Context checksum mismatch for session {session_id}")
                
                return SessionContext.from_json(context_data)
                
        except Exception as e:
            print(f"Error loading session context: {e}")
            return None
    
    def store_context_event(self, event: ContextEvent, session_id: str) -> bool:
        """Store individual context event"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO context_events 
                    (event_id, session_id, event_type, timestamp, correlation_id, event_data, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    session_id,
                    event.event_type.value,
                    event.timestamp.isoformat(),
                    event.correlation_id,
                    json.dumps(event.data),
                    json.dumps(event.metadata.to_dict())
                ))
            return True
        except Exception as e:
            print(f"Error storing context event: {e}")
            return False
    
    def get_context_events(self, session_id: str, limit: Optional[int] = None) -> List[ContextEvent]:
        """Get context events for a session"""
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT event_id, event_type, timestamp, correlation_id, event_data, metadata
                    FROM context_events 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC
                """
                params = [session_id]
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                events = []
                
                for row in cursor.fetchall():
                    from .models import ContextEventType, EventMetadata
                    event = ContextEvent(
                        event_id=row['event_id'],
                        event_type=ContextEventType(row['event_type']),
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        correlation_id=row['correlation_id'],
                        data=json.loads(row['event_data']),
                        metadata=EventMetadata.from_dict(json.loads(row['metadata']))
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            print(f"Error getting context events: {e}")
            return []
    
    def list_project_sessions(self, project_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a project"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT session_id, timestamp, context_size, created_at, updated_at
                    FROM session_contexts 
                    WHERE project_id = ? 
                    ORDER BY timestamp DESC
                """, (project_id,))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'session_id': row['session_id'],
                        'timestamp': row['timestamp'],
                        'context_size': row['context_size'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return sessions
                
        except Exception as e:
            print(f"Error listing project sessions: {e}")
            return []
    
    def get_context_versions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a context"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version_number, checksum, created_at
                    FROM context_versions 
                    WHERE session_id = ? 
                    ORDER BY version_number DESC
                """, (session_id,))
                
                versions = []
                for row in cursor.fetchall():
                    versions.append({
                        'version_number': row['version_number'],
                        'checksum': row['checksum'],
                        'created_at': row['created_at']
                    })
                
                return versions
                
        except Exception as e:
            print(f"Error getting context versions: {e}")
            return []
    
    def cleanup_old_contexts(self, retention_days: int = 90) -> int:
        """Clean up old contexts based on retention policy"""
        try:
            cutoff_date = datetime.now().replace(microsecond=0) - \
                         datetime.timedelta(days=retention_days)
            
            with self.get_connection() as conn:
                # Delete old context events
                cursor = conn.execute("""
                    DELETE FROM context_events 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                events_deleted = cursor.rowcount
                
                # Delete old context versions
                cursor = conn.execute("""
                    DELETE FROM context_versions 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                versions_deleted = cursor.rowcount
                
                # Delete old session contexts
                cursor = conn.execute("""
                    DELETE FROM session_contexts 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                contexts_deleted = cursor.rowcount
                
                total_deleted = events_deleted + versions_deleted + contexts_deleted
                print(f"Cleaned up {total_deleted} old context records")
                
                return total_deleted
                
        except Exception as e:
            print(f"Error cleaning up old contexts: {e}")
            return 0
    
    def _get_next_version_number(self, conn: sqlite3.Connection, session_id: str) -> int:
        """Get next version number for a session"""
        cursor = conn.execute("""
            SELECT MAX(version_number) FROM context_versions 
            WHERE session_id = ?
        """, (session_id,))
        result = cursor.fetchone()
        return (result[0] or 0) + 1
    
    def _update_project_metadata(self, conn: sqlite3.Connection, project_id: str, context_size: int):
        """Update project metadata"""
        conn.execute("""
            INSERT OR REPLACE INTO project_metadata 
            (project_id, project_name, project_path, last_accessed, total_sessions, total_context_size)
            VALUES (
                ?, 
                COALESCE((SELECT project_name FROM project_metadata WHERE project_id = ?), ?),
                COALESCE((SELECT project_path FROM project_metadata WHERE project_id = ?), ?),
                CURRENT_TIMESTAMP,
                COALESCE((SELECT total_sessions FROM project_metadata WHERE project_id = ?), 0) + 1,
                COALESCE((SELECT total_context_size FROM project_metadata WHERE project_id = ?), 0) + ?
            )
        """, (project_id, project_id, project_id, project_id, project_id, project_id, project_id, context_size))
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate checksum for data integrity"""
        import hashlib
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Count records in each table
                for table in ['session_contexts', 'context_events', 'context_versions', 'project_metadata']:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Database file size
                stats['database_size_bytes'] = os.path.getsize(self.db_path)
                
                # Schema version
                stats['schema_version'] = self._get_schema_version(conn)
                
                return stats
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}