"""
Capability Registry - Real-time system capability inventory.
"""

import ast
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import (
    ExistingSolution, CapabilityType, CapabilityInventory,
    CapabilityGap, EnhancementOpportunity
)


class CapabilityRegistry:
    """
    Real-time system capability inventory.
    
    Maintains an up-to-date registry of all capabilities in the codebase
    through automated scanning and semantic analysis.
    """
    
    def __init__(self, codebase_root: Path, db_path: Optional[Path] = None):
        """Initialize the capability registry."""
        self.codebase_root = Path(codebase_root)
        self.db_path = db_path or (self.codebase_root / ".anti_duplication" / "registry.db")
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Registry state
        self.last_scan_time: Optional[datetime] = None
        self.scan_in_progress = False
        
        self.logger.info(f"CapabilityRegistry initialized for {self.codebase_root}")
    
    def _init_database(self) -> None:
        """Initialize the SQLite database for capability storage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS capabilities (
                    solution_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    file_path TEXT NOT NULL,
                    capability_type TEXT NOT NULL,
                    functionality_summary TEXT,
                    usage_examples TEXT,  -- JSON array
                    dependencies TEXT,    -- JSON array
                    last_modified TIMESTAMP,
                    maintainer TEXT,
                    documentation_url TEXT,
                    content_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    scan_id TEXT PRIMARY KEY,
                    scan_start TIMESTAMP,
                    scan_end TIMESTAMP,
                    files_scanned INTEGER,
                    capabilities_found INTEGER,
                    errors_encountered INTEGER,
                    scan_duration_seconds REAL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities_type 
                ON capabilities(capability_type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities_file_path 
                ON capabilities(file_path)
            """)
            
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS capabilities_fts 
                USING fts5(name, description, functionality_summary, content=capabilities)
            """)
    
    def scan_codebase(self) -> Dict[str, Any]:
        """
        Perform comprehensive codebase scan to update capability registry.
        
        Returns:
            Dict containing scan results and statistics
        """
        if self.scan_in_progress:
            return {"error": "Scan already in progress"}
        
        self.scan_in_progress = True
        scan_start = datetime.utcnow()
        scan_id = f"scan_{int(scan_start.timestamp())}"
        
        try:
            self.logger.info(f"Starting codebase scan: {scan_id}")
            
            # Find all Python files
            python_files = list(self.codebase_root.rglob("*.py"))
            python_files = [f for f in python_files if not self._should_skip_file(f)]
            
            self.logger.info(f"Found {len(python_files)} Python files to scan")
            
            # Scan files in parallel
            capabilities_found = []
            errors_encountered = 0
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_file = {
                    executor.submit(self._scan_python_file, file_path): file_path
                    for file_path in python_files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        file_capabilities = future.result()
                        capabilities_found.extend(file_capabilities)
                    except Exception as e:
                        self.logger.error(f"Error scanning {file_path}: {e}")
                        errors_encountered += 1
            
            # Update database
            self._update_capabilities_database(capabilities_found)
            
            # Update FTS index
            self._update_fts_index()
            
            scan_end = datetime.utcnow()
            scan_duration = (scan_end - scan_start).total_seconds()
            
            # Record scan history
            self._record_scan_history(
                scan_id, scan_start, scan_end, len(python_files),
                len(capabilities_found), errors_encountered, scan_duration
            )
            
            self.last_scan_time = scan_end
            
            result = {
                "scan_id": scan_id,
                "files_scanned": len(python_files),
                "capabilities_found": len(capabilities_found),
                "errors_encountered": errors_encountered,
                "scan_duration_seconds": scan_duration,
                "scan_completed": scan_end.isoformat()
            }
            
            self.logger.info(f"Scan completed: {result}")
            return result
            
        finally:
            self.scan_in_progress = False
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during scanning."""
        skip_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            ".tox",
            "build",
            "dist",
            ".egg-info"
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _scan_python_file(self, file_path: Path) -> List[ExistingSolution]:
        """
        Scan a single Python file for capabilities.
        
        Args:
            file_path: Path to the Python file to scan
            
        Returns:
            List of capabilities found in the file
        """
        capabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract file-level information
            file_stats = file_path.stat()
            relative_path = str(file_path.relative_to(self.codebase_root))
            
            # Find classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    capability = self._extract_class_capability(
                        node, content, relative_path, file_stats.st_mtime
                    )
                    if capability:
                        capabilities.append(capability)
                
                elif isinstance(node, ast.FunctionDef):
                    # Only include top-level functions (not methods)
                    if isinstance(node.parent if hasattr(node, 'parent') else None, ast.Module):
                        capability = self._extract_function_capability(
                            node, content, relative_path, file_stats.st_mtime
                        )
                        if capability:
                            capabilities.append(capability)
        
        except Exception as e:
            self.logger.debug(f"Error parsing {file_path}: {e}")
            # Don't raise - just skip problematic files
        
        return capabilities
    
    def _extract_class_capability(
        self, 
        node: ast.ClassDef, 
        content: str, 
        file_path: str,
        last_modified: float
    ) -> Optional[ExistingSolution]:
        """Extract capability information from a class definition."""
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extract method names
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        
        # Generate functionality summary
        functionality_summary = f"Class with {len(methods)} methods"
        if methods:
            functionality_summary += f": {', '.join(methods[:5])}"
            if len(methods) > 5:
                functionality_summary += f" and {len(methods) - 5} more"
        
        return ExistingSolution(
            name=node.name,
            description=docstring.split('\n')[0] if docstring else "",
            file_path=file_path,
            capability_type=CapabilityType.CLASS,
            functionality_summary=functionality_summary,
            usage_examples=[],  # Could be extracted from docstring examples
            dependencies=self._extract_dependencies(content),
            last_modified=datetime.fromtimestamp(last_modified)
        )
    
    def _extract_function_capability(
        self, 
        node: ast.FunctionDef, 
        content: str, 
        file_path: str,
        last_modified: float
    ) -> Optional[ExistingSolution]:
        """Extract capability information from a function definition."""
        
        # Skip private functions and test functions
        if node.name.startswith('_') or node.name.startswith('test_'):
            return None
        
        # Get docstring
        docstring = ast.get_docstring(node) or ""
        
        # Extract arguments
        args = [arg.arg for arg in node.args.args]
        functionality_summary = f"Function with {len(args)} parameters"
        if args:
            functionality_summary += f": {', '.join(args[:3])}"
            if len(args) > 3:
                functionality_summary += f" and {len(args) - 3} more"
        
        return ExistingSolution(
            name=node.name,
            description=docstring.split('\n')[0] if docstring else "",
            file_path=file_path,
            capability_type=CapabilityType.FUNCTION,
            functionality_summary=functionality_summary,
            usage_examples=[],  # Could be extracted from docstring examples
            dependencies=self._extract_dependencies(content),
            last_modified=datetime.fromtimestamp(last_modified)
        )
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract import dependencies from file content."""
        dependencies = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
        except:
            pass  # Skip if parsing fails
        
        return list(set(dependencies))  # Remove duplicates
    
    def _update_capabilities_database(self, capabilities: List[ExistingSolution]) -> None:
        """Update the database with discovered capabilities."""
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing capabilities
            conn.execute("DELETE FROM capabilities")
            
            # Insert new capabilities
            for cap in capabilities:
                conn.execute("""
                    INSERT INTO capabilities (
                        solution_id, name, description, file_path, capability_type,
                        functionality_summary, usage_examples, dependencies,
                        last_modified, maintainer, documentation_url, content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cap.solution_id,
                    cap.name,
                    cap.description,
                    cap.file_path,
                    cap.capability_type.value,
                    cap.functionality_summary,
                    json.dumps(cap.usage_examples),
                    json.dumps(cap.dependencies),
                    cap.last_modified,
                    cap.maintainer,
                    cap.documentation_url,
                    self._calculate_content_hash(cap)
                ))
    
    def _update_fts_index(self) -> None:
        """Update the full-text search index."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM capabilities_fts")
            conn.execute("""
                INSERT INTO capabilities_fts(name, description, functionality_summary)
                SELECT name, description, functionality_summary FROM capabilities
            """)
    
    def _calculate_content_hash(self, capability: ExistingSolution) -> str:
        """Calculate hash of capability content for change detection."""
        content = f"{capability.name}|{capability.description}|{capability.functionality_summary}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _record_scan_history(
        self, scan_id: str, scan_start: datetime, scan_end: datetime,
        files_scanned: int, capabilities_found: int, errors_encountered: int,
        scan_duration: float
    ) -> None:
        """Record scan history in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scan_history (
                    scan_id, scan_start, scan_end, files_scanned,
                    capabilities_found, errors_encountered, scan_duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id, scan_start, scan_end, files_scanned,
                capabilities_found, errors_encountered, scan_duration
            ))
    
    def semantic_search(self, intent: str, limit: int = 10) -> List[ExistingSolution]:
        """
        Search for capabilities based on intent using semantic matching.
        
        Args:
            intent: Description of what the user wants to accomplish
            limit: Maximum number of results to return
            
        Returns:
            List of matching capabilities
        """
        capabilities = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Use FTS for text search
            cursor = conn.execute("""
                SELECT c.* FROM capabilities c
                JOIN capabilities_fts fts ON c.rowid = fts.rowid
                WHERE capabilities_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (intent, limit))
            
            for row in cursor.fetchall():
                capability = self._row_to_capability(row)
                capabilities.append(capability)
        
        return capabilities
    
    def _row_to_capability(self, row) -> ExistingSolution:
        """Convert database row to ExistingSolution object."""
        return ExistingSolution(
            solution_id=row[0],
            name=row[1],
            description=row[2] or "",
            file_path=row[3],
            capability_type=CapabilityType(row[4]),
            functionality_summary=row[5] or "",
            usage_examples=json.loads(row[6]) if row[6] else [],
            dependencies=json.loads(row[7]) if row[7] else [],
            last_modified=datetime.fromisoformat(row[8]) if row[8] else None,
            maintainer=row[9],
            documentation_url=row[10]
        )
    
    def validate_freshness(self) -> Dict[str, Any]:
        """
        Validate that the registry is fresh and complete.
        
        Returns:
            Registry health information
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get latest scan info
            cursor = conn.execute("""
                SELECT scan_end, capabilities_found 
                FROM scan_history 
                ORDER BY scan_end DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                return {
                    "is_fresh": False,
                    "last_scan": None,
                    "age_hours": float('inf'),
                    "capabilities_count": 0,
                    "recommendation": "Initial scan required"
                }
            
            last_scan = datetime.fromisoformat(row[0])
            capabilities_count = row[1]
            age_hours = (datetime.utcnow() - last_scan).total_seconds() / 3600
            
            is_fresh = age_hours < 4  # Fresh if scanned within 4 hours
            
            return {
                "is_fresh": is_fresh,
                "last_scan": last_scan.isoformat(),
                "age_hours": age_hours,
                "capabilities_count": capabilities_count,
                "recommendation": "Registry is fresh" if is_fresh else "Rescan recommended"
            }
    
    def get_capability_by_id(self, solution_id: str) -> Optional[ExistingSolution]:
        """Get a specific capability by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM capabilities WHERE solution_id = ?",
                (solution_id,)
            )
            row = cursor.fetchone()
            return self._row_to_capability(row) if row else None
    
    def get_capabilities_by_type(self, capability_type: CapabilityType) -> List[ExistingSolution]:
        """Get all capabilities of a specific type."""
        capabilities = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM capabilities WHERE capability_type = ?",
                (capability_type.value,)
            )
            
            for row in cursor.fetchall():
                capabilities.append(self._row_to_capability(row))
        
        return capabilities
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total capabilities
            cursor = conn.execute("SELECT COUNT(*) FROM capabilities")
            total_capabilities = cursor.fetchone()[0]
            
            # Capabilities by type
            cursor = conn.execute("""
                SELECT capability_type, COUNT(*) 
                FROM capabilities 
                GROUP BY capability_type
            """)
            by_type = dict(cursor.fetchall())
            
            # Recent scan info
            cursor = conn.execute("""
                SELECT scan_end, files_scanned, scan_duration_seconds
                FROM scan_history 
                ORDER BY scan_end DESC 
                LIMIT 1
            """)
            scan_info = cursor.fetchone()
            
            return {
                "total_capabilities": total_capabilities,
                "capabilities_by_type": by_type,
                "last_scan": scan_info[0] if scan_info else None,
                "files_scanned": scan_info[1] if scan_info else 0,
                "last_scan_duration": scan_info[2] if scan_info else 0
            }