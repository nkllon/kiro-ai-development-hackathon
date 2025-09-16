#!/usr/bin/env python3
"""
🚀 IMPORT DEPENDENCY REGISTRY - CIRCULAR IMPORT PREVENTION
========================================================
Focus on what actually breaks: circular imports.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Prevent circular imports while allowing other relationships
"""

import sqlite3
import threading
from typing import Dict, Set, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import ast
import os


@dataclass
class ImportDependency:
    """Import dependency record."""
    importer_module: str
    imported_module: str
    import_type: str  # "direct", "from_import", "relative"
    line_number: int
    created_at: datetime
    is_active: bool = True


class ImportDependencyRegistry:
    """
    Import Dependency Registry - Prevents Circular Imports
    
    Focus: Only track import dependencies and prevent cycles.
    Everything else is free to be non-DAG.
    """
    
    def __init__(self, db_path: str = ".beast_mode/import_registry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for import dependencies."""
        with self._lock:
            # Drop existing database to start fresh
            if self.db_path.exists():
                self.db_path.unlink()
            
            conn = sqlite3.connect(self.db_path)
            try:
                # Import dependencies table
                conn.execute('''
                    CREATE TABLE import_dependencies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        importer_module TEXT NOT NULL,
                        imported_module TEXT NOT NULL,
                        import_type TEXT NOT NULL,
                        line_number INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        is_active BOOLEAN NOT NULL,
                        UNIQUE(importer_module, imported_module, import_type)
                    )
                ''')
                
                # Module metadata table
                conn.execute('''
                    CREATE TABLE modules (
                        module_id TEXT PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        last_scan TEXT NOT NULL,
                        is_active BOOLEAN NOT NULL
                    )
                ''')
                
                # Create indexes
                conn.execute('CREATE INDEX idx_importer ON import_dependencies(importer_module)')
                conn.execute('CREATE INDEX idx_imported ON import_dependencies(imported_module)')
                conn.execute('CREATE INDEX idx_active ON import_dependencies(is_active)')
                
                conn.commit()
            finally:
                conn.close()
    
    def scan_module_imports(self, module_path: str) -> List[ImportDependency]:
        """Scan a module for import statements."""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportDependency(
                            importer_module=module_path,
                            imported_module=alias.name,
                            import_type="direct",
                            line_number=node.lineno,
                            created_at=datetime.now()
                        ))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(ImportDependency(
                            importer_module=module_path,
                            imported_module=node.module,
                            import_type="from_import",
                            line_number=node.lineno,
                            created_at=datetime.now()
                        ))
            
            return imports
            
        except Exception as e:
            print(f"🚨 Error scanning imports in {module_path}: {e}")
            return []
    
    def register_module_imports(self, module_path: str) -> bool:
        """Register all imports for a module."""
        with self._lock:
            try:
                # Scan imports
                imports = self.scan_module_imports(module_path)
                
                # Check for circular dependencies
                for import_dep in imports:
                    if self._would_create_circular_import(import_dep.importer_module, import_dep.imported_module):
                        print(f"🚨 CIRCULAR IMPORT DETECTED: {import_dep.importer_module} imports {import_dep.imported_module}")
                        return False
                
                # Register imports
                conn = sqlite3.connect(self.db_path)
                try:
                    # Clear existing imports for this module
                    conn.execute('''
                        UPDATE import_dependencies 
                        SET is_active = 0 
                        WHERE importer_module = ?
                    ''', (module_path,))
                    
                    # Register new imports
                    for import_dep in imports:
                        conn.execute('''
                            INSERT OR REPLACE INTO import_dependencies
                            (importer_module, imported_module, import_type, line_number, created_at, is_active)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            import_dep.importer_module,
                            import_dep.imported_module,
                            import_dep.import_type,
                            import_dep.line_number,
                            import_dep.created_at.isoformat(),
                            import_dep.is_active
                        ))
                    
                    # Update module metadata
                    conn.execute('''
                        INSERT OR REPLACE INTO modules
                        (module_id, file_path, last_scan, is_active)
                        VALUES (?, ?, ?, ?)
                    ''', (module_path, module_path, datetime.now().isoformat(), True))
                    
                    conn.commit()
                    print(f"✅ Registered {len(imports)} imports for {module_path}")
                    return True
                    
                finally:
                    conn.close()
                    
            except Exception as e:
                print(f"🚨 Error registering imports for {module_path}: {e}")
                return False
    
    def _would_create_circular_import(self, importer: str, imported: str) -> bool:
        """Check if this import would create a circular dependency."""
        if importer == imported:
            return True
        
        # Check if there's already a path from imported back to importer
        return self._has_import_path(imported, importer)
    
    def _has_import_path(self, from_module: str, to_module: str) -> bool:
        """Check if there's an import path from from_module to to_module."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute('''
                WITH RECURSIVE import_path AS (
                    SELECT imported_module FROM import_dependencies 
                    WHERE importer_module = ? AND is_active = 1
                    UNION
                    SELECT id.imported_module FROM import_dependencies id
                    JOIN import_path ip ON id.importer_module = ip.imported_module
                    WHERE id.is_active = 1
                )
                SELECT 1 FROM import_path WHERE imported_module = ?
                LIMIT 1
            ''', (from_module, to_module))
            
            return cursor.fetchone() is not None
            
        finally:
            conn.close()
    
    def get_import_dependencies(self, module_path: str) -> List[ImportDependency]:
        """Get all import dependencies for a module."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute('''
                    SELECT importer_module, imported_module, import_type, line_number, created_at, is_active
                    FROM import_dependencies
                    WHERE importer_module = ? AND is_active = 1
                    ORDER BY line_number
                ''', (module_path,))
                
                dependencies = []
                for row in cursor.fetchall():
                    dependencies.append(ImportDependency(
                        importer_module=row[0],
                        imported_module=row[1],
                        import_type=row[2],
                        line_number=row[3],
                        created_at=datetime.fromisoformat(row[4]),
                        is_active=bool(row[5])
                    ))
                
                return dependencies
                
            finally:
                conn.close()
    
    def get_importers_of(self, module_path: str) -> List[str]:
        """Get all modules that import the given module."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute('''
                    SELECT DISTINCT importer_module
                    FROM import_dependencies
                    WHERE imported_module = ? AND is_active = 1
                ''', (module_path,))
                
                return [row[0] for row in cursor.fetchall()]
                
            finally:
                conn.close()
    
    def validate_no_circular_imports(self) -> bool:
        """Validate that there are no circular imports in the registry."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Check for any circular dependencies
                cursor = conn.execute('''
                    WITH RECURSIVE import_cycle AS (
                        SELECT importer_module, imported_module, 1 as depth
                        FROM import_dependencies
                        WHERE is_active = 1
                        UNION
                        SELECT ic.importer_module, id.imported_module, ic.depth + 1
                        FROM import_cycle ic
                        JOIN import_dependencies id ON ic.imported_module = id.importer_module
                        WHERE id.is_active = 1 AND ic.depth < 100
                    )
                    SELECT 1 FROM import_cycle
                    WHERE importer_module = imported_module
                    LIMIT 1
                ''')
                
                has_cycle = cursor.fetchone() is not None
                return not has_cycle
                
            finally:
                conn.close()
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Total imports
                cursor = conn.execute('SELECT COUNT(*) FROM import_dependencies WHERE is_active = 1')
                total_imports = cursor.fetchone()[0]
                
                # Total modules
                cursor = conn.execute('SELECT COUNT(*) FROM modules WHERE is_active = 1')
                total_modules = cursor.fetchone()[0]
                
                # Circular import check
                has_circular = not self.validate_no_circular_imports()
                
                return {
                    "total_imports": total_imports,
                    "total_modules": total_modules,
                    "has_circular_imports": has_circular,
                    "is_healthy": not has_circular,
                    "database_path": str(self.db_path)
                }
                
            finally:
                conn.close()


# Global import registry instance
import_registry = ImportDependencyRegistry()


def register_module_imports(module_path: str) -> bool:
    """Register imports for a module."""
    return import_registry.register_module_imports(module_path)


def validate_no_circular_imports() -> bool:
    """Validate that there are no circular imports."""
    return import_registry.validate_no_circular_imports()


def get_import_dependencies(module_path: str) -> List[ImportDependency]:
    """Get import dependencies for a module."""
    return import_registry.get_import_dependencies(module_path)


def get_importers_of(module_path: str) -> List[str]:
    """Get modules that import the given module."""
    return import_registry.get_importers_of(module_path)


def get_import_registry_stats() -> Dict[str, Any]:
    """Get import registry statistics."""
    return import_registry.get_registry_stats()


