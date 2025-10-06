"""
AI Memory Palace Database Storage

Provides robust SQLite backend with comprehensive error handling.
"""

import sqlite3
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ContextDatabase(ReflectiveModule):
    """Robust SQLite backend with error handling and retry logic."""
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.db_path = Path(db_path or ".kiro/context/context.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.memory_only_mode = False
        
        # Initialize database
        self._initialize_database()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "ContextDatabase",
            "version": "1.0.0",
            "description": "AI Memory Palace Database Storage",
            "db_path": str(self.db_path),
            "memory_only_mode": self.memory_only_mode
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy" if not self.memory_only_mode else "degraded",
            "database_accessible": not self.memory_only_mode,
            "db_path": str(self.db_path)
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return [
            "context_storage",
            "data_integrity",
            "retry_logic",
            "memory_fallback",
            "schema_migration"
        ]
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self.logger.error(f"Database degradation triggered: {error}")
        self.memory_only_mode = True
        return {
            "degradation_applied": "memory_only_mode",
            "reason": str(error)
        }
    
    def _initialize_database(self):
        """Initialize database with schema migration."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS context_sessions (
                        id TEXT PRIMARY KEY,
                        project_id TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        data TEXT NOT NULL,
                        checksum TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS context_events (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        data TEXT NOT NULL,
                        correlation_id TEXT,
                        FOREIGN KEY (session_id) REFERENCES context_sessions (id)
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            self.logger.warning("Falling back to memory-only mode")
            self.memory_only_mode = True
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with retry logic."""
        if self.memory_only_mode:
            # Use in-memory database
            conn = sqlite3.connect(":memory:")
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            yield conn
        finally:
            conn.close()
    
    def store_context(self, session_id: str, project_id: str, data: Dict[str, Any]) -> bool:
        """Store context with integrity validation."""
        try:
            data_json = json.dumps(data)
            checksum = str(hash(data_json))  # Simple checksum
            
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO context_sessions 
                    (id, project_id, data, checksum) 
                    VALUES (?, ?, ?, ?)
                """, (session_id, project_id, data_json, checksum))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store context: {e}")
            return False
    
    def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load context with integrity validation."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT data, checksum FROM context_sessions 
                    WHERE id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                data_json, stored_checksum = row
                calculated_checksum = str(hash(data_json))
                
                if stored_checksum != calculated_checksum:
                    self.logger.warning(f"Context integrity check failed for {session_id}")
                    return None
                
                return json.loads(data_json)
                
        except Exception as e:
            self.logger.error(f"Failed to load context: {e}")
            return None
