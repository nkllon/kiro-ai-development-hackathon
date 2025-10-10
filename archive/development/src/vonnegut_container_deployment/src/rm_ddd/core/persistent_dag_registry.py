#!/usr/bin/env python3
"""
Persistent DAG Registry with SQLite and Referential Integrity
============================================================

A persistent registry that enforces DAG structure and prevents circular dependencies
with full referential integrity constraints using SQLite.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Replace in-memory registry with persistent SQLite-based registry
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Set, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ModuleDependency:
    """Module dependency tracking with full metadata."""
    module_id: str
    dependencies: Set[str]
    dependents: Set[str]
    registered_at: datetime
    version: str = "1.0.0"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    class_name: Optional[str] = None
    capabilities: List[str] = None
    health_status: str = "unknown"
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class PersistentDAGRegistry:
    """
    Persistent DAG Registry with SQLite backend and referential integrity.
    
    Features:
    - SQLite persistence with ACID compliance
    - Foreign key constraints and referential integrity
    - DAG enforcement with cycle detection
    - Bidirectional dependency tracking
    - Full audit trail and metadata
    - Transaction safety
    """
    
    def __init__(self, db_path: str = ".beast_mode/registry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_id = f"persistent_dag_registry_{uuid.uuid4().hex[:8]}"
        self.created_at = datetime.now()
        
        # Initialize database with proper schema
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with proper schema and constraints."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Enable WAL mode for better concurrency
            
            # Registry metadata table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS registry_metadata (
                    id INTEGER PRIMARY KEY,
                    registry_id TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    total_modules INTEGER DEFAULT 0,
                    is_dag BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Modules table with referential integrity
            conn.execute("""
                CREATE TABLE IF NOT EXISTS modules (
                    module_id TEXT PRIMARY KEY,
                    class_name TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    version TEXT NOT NULL DEFAULT '1.0.0',
                    capabilities TEXT,  -- JSON array
                    health_status TEXT DEFAULT 'unknown',
                    registered_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE
                )
            """)
            
            # Dependencies table with foreign key constraints
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id TEXT NOT NULL,
                    dependency_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE,
                    FOREIGN KEY (dependency_id) REFERENCES modules(module_id) ON DELETE CASCADE,
                    UNIQUE(module_id, dependency_id)
                )
            """)
            
            # Dependents table (reverse lookup for performance)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dependents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id TEXT NOT NULL,
                    dependent_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE,
                    FOREIGN KEY (dependent_id) REFERENCES modules(module_id) ON DELETE CASCADE,
                    UNIQUE(module_id, dependent_id)
                )
            """)
            
            # Audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    module_id TEXT,
                    details TEXT,  -- JSON
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_module ON dependencies(module_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_dep ON dependencies(dependency_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependents_module ON dependents(module_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_dependents_dep ON dependents(dependent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")
            
            # Insert initial registry metadata
            conn.execute("""
                INSERT OR REPLACE INTO registry_metadata 
                (registry_id, created_at, last_updated, total_modules, is_dag)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.registry_id,
                self.created_at.isoformat(),
                datetime.now().isoformat(),
                0,
                True
            ))
            
            conn.commit()
    
    def register_module(self, module_id: str, dependencies: Set[str] = None, 
                       file_path: str = None, line_number: int = None,
                       class_name: str = None, capabilities: List[str] = None) -> bool:
        """
        Register a module with DAG validation and referential integrity.
        
        Returns:
            bool: True if registration successful, False if would create cycle
        """
        dependencies = dependencies or set()
        capabilities = capabilities or []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Check if registration would create a circular dependency
                if self._would_create_cycle(conn, module_id, dependencies):
                    self._log_audit(conn, "REGISTRATION_REJECTED", module_id, 
                                  {"reason": "circular_dependency", "dependencies": list(dependencies)})
                    return False
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Register the module
                conn.execute("""
                    INSERT OR REPLACE INTO modules 
                    (module_id, class_name, file_path, line_number, version, 
                     capabilities, health_status, registered_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    module_id,
                    class_name,
                    file_path,
                    line_number,
                    "1.0.0",
                    json.dumps(capabilities),
                    "healthy",
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                # Clear existing dependencies
                conn.execute("DELETE FROM dependencies WHERE module_id = ?", (module_id,))
                conn.execute("DELETE FROM dependents WHERE dependent_id = ?", (module_id,))
                
                # Add new dependencies
                for dep in dependencies:
                    conn.execute("""
                        INSERT INTO dependencies (module_id, dependency_id, created_at)
                        VALUES (?, ?, ?)
                    """, (module_id, dep, datetime.now().isoformat()))
                    
                    # Add reverse dependency (dependents)
                    conn.execute("""
                        INSERT INTO dependents (module_id, dependent_id, created_at)
                        VALUES (?, ?, ?)
                    """, (dep, module_id, datetime.now().isoformat()))
                
                # Update registry metadata
                self._update_registry_stats(conn)
                
                # Log successful registration
                self._log_audit(conn, "MODULE_REGISTERED", module_id, 
                              {"dependencies": list(dependencies), "capabilities": capabilities})
                
                conn.commit()
                return True
                
        except sqlite3.IntegrityError as e:
            self._log_audit(conn, "REGISTRATION_FAILED", module_id, 
                          {"error": str(e), "reason": "integrity_violation"})
            return False
        except Exception as e:
            self._log_audit(conn, "REGISTRATION_ERROR", module_id, 
                          {"error": str(e), "reason": "unknown_error"})
            return False
    
    def _would_create_cycle(self, conn: sqlite3.Connection, module_id: str, 
                           dependencies: Set[str]) -> bool:
        """Check if adding this module would create a circular dependency."""
        # Create temporary dependency graph
        temp_deps = {}
        
        # Get all existing dependencies
        cursor = conn.execute("SELECT module_id, dependency_id FROM dependencies")
        for row in cursor:
            if row[0] not in temp_deps:
                temp_deps[row[0]] = set()
            temp_deps[row[0]].add(row[1])
        
        # Add the new module's dependencies
        temp_deps[module_id] = dependencies
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in temp_deps.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        # Check all nodes for cycles
        for node in temp_deps:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def get_dependencies(self, module_id: str) -> Set[str]:
        """Get dependencies for a module."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT dependency_id FROM dependencies WHERE module_id = ?", 
                (module_id,)
            )
            return {row[0] for row in cursor}
    
    def get_dependents(self, module_id: str) -> Set[str]:
        """Get dependents for a module."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT dependent_id FROM dependents WHERE module_id = ?", 
                (module_id,)
            )
            return {row[0] for row in cursor}
    
    def get_module_with_most_dependents(self) -> Tuple[str, int]:
        """Get the module with the most dependents."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT module_id, COUNT(*) as dependent_count
                FROM dependents 
                GROUP BY module_id 
                ORDER BY dependent_count DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None, 0
    
    def validate_dag(self) -> bool:
        """Validate that the entire registry is a DAG (no cycles)."""
        with sqlite3.connect(self.db_path) as conn:
            # Get all dependencies
            cursor = conn.execute("SELECT module_id, dependency_id FROM dependencies")
            dependency_graph = {}
            for row in cursor:
                if row[0] not in dependency_graph:
                    dependency_graph[row[0]] = set()
                dependency_graph[row[0]].add(row[1])
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in dependency_graph.get(node, set()):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            for node in dependency_graph:
                if node not in visited:
                    if has_cycle(node):
                        return False
            
            return True
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Get basic stats
            cursor = conn.execute("SELECT * FROM registry_metadata LIMIT 1")
            metadata = cursor.fetchone()
            
            # Get module count
            cursor = conn.execute("SELECT COUNT(*) FROM modules")
            module_count = cursor.fetchone()[0]
            
            # Get dependency count
            cursor = conn.execute("SELECT COUNT(*) FROM dependencies")
            dependency_count = cursor.fetchone()[0]
            
            # Get most dependent module
            most_dependent_module, most_dependent_count = self.get_module_with_most_dependents()
            
            return {
                "registry_id": metadata[1] if metadata else self.registry_id,
                "total_modules": module_count,
                "total_dependencies": dependency_count,
                "is_dag": self.validate_dag(),
                "most_dependent_module": most_dependent_module,
                "most_dependent_count": most_dependent_count,
                "created_at": metadata[2] if metadata else self.created_at.isoformat(),
                "last_updated": metadata[3] if metadata else datetime.now().isoformat()
            }
    
    def _update_registry_stats(self, conn: sqlite3.Connection):
        """Update registry statistics."""
        cursor = conn.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        
        is_dag = self.validate_dag()
        
        conn.execute("""
            UPDATE registry_metadata 
            SET total_modules = ?, is_dag = ?, last_updated = ?
            WHERE registry_id = ?
        """, (module_count, is_dag, datetime.now().isoformat(), self.registry_id))
    
    def _log_audit(self, conn: sqlite3.Connection, action: str, module_id: str, details: Dict):
        """Log audit trail."""
        conn.execute("""
            INSERT INTO audit_log (action, module_id, details, timestamp)
            VALUES (?, ?, ?, ?)
        """, (action, module_id, json.dumps(details), datetime.now().isoformat()))
    
    def remove_module(self, module_id: str) -> bool:
        """Remove a module and update all dependent relationships."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("BEGIN TRANSACTION")
                
                # Remove from dependencies table
                conn.execute("DELETE FROM dependencies WHERE module_id = ?", (module_id,))
                
                # Remove from dependents table
                conn.execute("DELETE FROM dependents WHERE dependent_id = ?", (module_id,))
                conn.execute("DELETE FROM dependents WHERE module_id = ?", (module_id,))
                
                # Remove from modules table
                conn.execute("DELETE FROM modules WHERE module_id = ?", (module_id,))
                
                # Update registry stats
                self._update_registry_stats(conn)
                
                # Log removal
                self._log_audit(conn, "MODULE_REMOVED", module_id, {})
                
                conn.commit()
                return True
                
        except Exception as e:
            self._log_audit(conn, "REMOVAL_ERROR", module_id, {"error": str(e)})
            return False
    
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT action, module_id, details, timestamp 
                FROM audit_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    "action": row[0],
                    "module_id": row[1],
                    "details": json.loads(row[2]) if row[2] else {},
                    "timestamp": row[3]
                }
                for row in cursor
            ]


# Global persistent registry instance
persistent_dag_registry = PersistentDAGRegistry()


def register_module_persistently(module_id: str, dependencies: Set[str] = None, 
                                file_path: str = None, line_number: int = None,
                                class_name: str = None, capabilities: List[str] = None) -> bool:
    """Safely register a module with persistent DAG validation."""
    return persistent_dag_registry.register_module(
        module_id, dependencies, file_path, line_number, class_name, capabilities
    )


def get_persistent_dag_validation() -> bool:
    """Check if the persistent registry is a valid DAG."""
    return persistent_dag_registry.validate_dag()


def get_persistent_registry_stats() -> Dict[str, Any]:
    """Get persistent DAG registry statistics."""
    return persistent_dag_registry.get_registry_stats()


def get_module_with_most_dependents() -> Tuple[str, int]:
    """Get the module with the most dependents from persistent registry."""
    return persistent_dag_registry.get_module_with_most_dependents()


