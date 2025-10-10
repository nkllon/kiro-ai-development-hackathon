"""
Database Management for AI Consultation System

Provides database migration and backward compatibility patterns for safely
adding AI consultation features to existing Observatory database.

This implementation uses a simplified SQLite approach without SQLAlchemy,
focusing on migration patterns and brownfield deployment safety.
"""

import asyncio
import logging
import os
import sqlite3
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import hashlib
import uuid

from .exceptions import ConsultationError
from .models import (
    ConsultationQuery, ConsultationResult, DoctorStatus, 
    QueuedQuery, BudgetStatus, CostAnalytics
)
from .feature_flags import feature_flags, FeatureFlag

logger = logging.getLogger(__name__)


class DatabaseMigrationError(ConsultationError):
    """Raised when database migration encounters errors"""
    
    def __init__(self, message: str, migration_version: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_MIGRATION_ERROR",
            details={"migration_version": migration_version},
            retry_possible=False
        )


# Database schema definitions
DATABASE_SCHEMA = {
    'ai_consultation_queries': '''
        CREATE TABLE IF NOT EXISTS ai_consultation_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id TEXT UNIQUE NOT NULL,
            user_id TEXT NOT NULL,
            query_text TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            context_snapshot TEXT,
            email_notification TEXT,
            priority TEXT NOT NULL DEFAULT 'normal',
            processing_mode TEXT,
            session_id TEXT
        )
    ''',
    'ai_consultation_results': '''
        CREATE TABLE IF NOT EXISTS ai_consultation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id TEXT UNIQUE NOT NULL,
            query_id TEXT NOT NULL,
            response TEXT NOT NULL,
            processing_mode TEXT NOT NULL,
            cost REAL NOT NULL DEFAULT 0.0,
            tokens_used INTEGER NOT NULL DEFAULT 0,
            processing_time REAL NOT NULL DEFAULT 0.0,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            confidence_score REAL,
            error_message TEXT,
            retry_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (query_id) REFERENCES ai_consultation_queries (query_id)
        )
    ''',
    'ai_consultation_doctor_status': '''
        CREATE TABLE IF NOT EXISTS ai_consultation_doctor_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_available BOOLEAN NOT NULL DEFAULT 0,
            reason TEXT NOT NULL,
            cost_budget_remaining REAL NOT NULL DEFAULT 0.0,
            daily_usage REAL NOT NULL DEFAULT 0.0,
            monthly_usage REAL NOT NULL DEFAULT 0.0,
            last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            next_budget_reset DATETIME,
            active_sessions INTEGER NOT NULL DEFAULT 0,
            queue_length INTEGER NOT NULL DEFAULT 0
        )
    ''',
    'ai_consultation_queue': '''
        CREATE TABLE IF NOT EXISTS ai_consultation_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            queue_id TEXT UNIQUE NOT NULL,
            query_id TEXT NOT NULL,
            queued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            priority TEXT NOT NULL DEFAULT 'normal',
            estimated_cost REAL NOT NULL DEFAULT 0.0,
            retry_count INTEGER NOT NULL DEFAULT 0,
            max_retries INTEGER NOT NULL DEFAULT 3,
            processing_started_at DATETIME,
            FOREIGN KEY (query_id) REFERENCES ai_consultation_queries (query_id)
        )
    ''',
    'ai_consultation_budget': '''
        CREATE TABLE IF NOT EXISTS ai_consultation_budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            daily_budget REAL NOT NULL DEFAULT 0.0,
            monthly_budget REAL NOT NULL DEFAULT 0.0,
            daily_spent REAL NOT NULL DEFAULT 0.0,
            monthly_spent REAL NOT NULL DEFAULT 0.0,
            cost_per_token REAL NOT NULL DEFAULT 0.0001,
            last_reset DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    '''
}

# Database indexes for performance
DATABASE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_queries_user_timestamp ON ai_consultation_queries (user_id, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_queries_session_timestamp ON ai_consultation_queries (session_id, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_queries_priority_timestamp ON ai_consultation_queries (priority, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_results_query_timestamp ON ai_consultation_results (query_id, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_results_cost_timestamp ON ai_consultation_results (cost, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_results_processing_mode ON ai_consultation_results (processing_mode, timestamp)',
    'CREATE INDEX IF NOT EXISTS idx_queue_priority_queued ON ai_consultation_queue (priority, queued_at)',
    'CREATE INDEX IF NOT EXISTS idx_queue_processing_status ON ai_consultation_queue (processing_started_at, queued_at)',
    'CREATE INDEX IF NOT EXISTS idx_budget_date ON ai_consultation_budget (date)'
]


class DatabaseManager:
    """
    Manages database connections and migrations for AI consultation system
    
    Provides safe database operations that don't interfere with existing
    Observatory database structures. Uses SQLite with async support.
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        migration_dir: str = "migrations/ai_consultation",
        schema_prefix: str = "ai_consultation_"
    ):
        self.database_path = database_path or self._get_database_path()
        self.migration_dir = Path(migration_dir)
        self.schema_prefix = schema_prefix
        self._connection_pool = []
        self._migration_version = "1.0.0"
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
    
    def _get_database_path(self) -> str:
        """Get database path from environment or default"""
        return os.getenv(
            'AI_CONSULTATION_DATABASE_PATH',
            os.path.join('data', 'ai_consultation.db')
        )
    
    async def initialize(self) -> None:
        """Initialize database and run migrations"""
        try:
            logger.info(f"Initializing AI consultation database at {self.database_path}")
            
            # Check if feature is enabled
            if not await feature_flags.is_enabled(FeatureFlag.RESULTS_STORAGE):
                logger.info("Database storage is disabled via feature flag")
                return
            
            # Create migration directory if it doesn't exist
            self.migration_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if this is a brownfield deployment
            await self._check_brownfield_safety()
            
            # Run migrations
            await self._run_migrations()
            
            # Initialize default data
            await self._initialize_default_data()
            
            logger.info("AI consultation database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseMigrationError(f"Database initialization failed: {str(e)}")
    
    async def _check_brownfield_safety(self) -> None:
        """Check if deployment is safe in brownfield environment"""
        try:
            # Check if database file exists
            if os.path.exists(self.database_path):
                logger.info("Existing database detected - performing brownfield safety check")
                
                async with aiosqlite.connect(self.database_path) as db:
                    # Check for existing Observatory tables
                    cursor = await db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'ai_consultation_%'"
                    )
                    existing_tables = await cursor.fetchall()
                    
                    if existing_tables:
                        logger.info(f"Found {len(existing_tables)} existing tables - using safe deployment mode")
                        
                        # Check for table name conflicts
                        cursor = await db.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_consultation_%'"
                        )
                        ai_tables = await cursor.fetchall()
                        
                        if ai_tables:
                            logger.info(f"Found {len(ai_tables)} existing AI consultation tables")
                        
                        # Verify we can read from existing tables (basic connectivity test)
                        await db.execute("SELECT 1")
                        
                        logger.info("Brownfield safety check passed")
                    else:
                        logger.info("No existing tables found - proceeding with fresh installation")
            else:
                logger.info("New database - proceeding with fresh installation")
                
        except Exception as e:
            logger.error(f"Brownfield safety check failed: {e}")
            raise DatabaseMigrationError(f"Brownfield safety check failed: {str(e)}")
    
    async def _get_migration_version(self) -> Optional[str]:
        """Get current migration version from database"""
        try:
            async with aiosqlite.connect(self.database_path) as db:
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='ai_consultation_migration_history'"
                )
                table_exists = await cursor.fetchone()
                
                if table_exists:
                    cursor = await db.execute(
                        "SELECT version FROM ai_consultation_migration_history ORDER BY applied_at DESC LIMIT 1"
                    )
                    result = await cursor.fetchone()
                    return result[0] if result else None
                
                return None
        except Exception as e:
            logger.warning(f"Could not get migration version: {e}")
            return None
    
    async def _record_migration(self, migration_id: str, version: str, execution_time: float) -> None:
        """Record migration in history table"""
        try:
            async with aiosqlite.connect(self.database_path) as db:
                await db.execute("""
                    INSERT INTO ai_consultation_migration_history 
                    (migration_id, version, applied_at, execution_time_ms)
                    VALUES (?, ?, ?, ?)
                """, (migration_id, version, datetime.utcnow().isoformat(), execution_time))
                await db.commit()
        except Exception as e:
            logger.warning(f"Could not record migration: {e}")
    
    async def _run_migrations(self) -> None:
        """Run database migrations"""
        start_time = datetime.utcnow()
        
        try:
            async with aiosqlite.connect(self.database_path) as db:
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys = ON")
                
                # Create migration history table first
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS ai_consultation_migration_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        migration_id TEXT UNIQUE NOT NULL,
                        version TEXT NOT NULL,
                        applied_at TEXT NOT NULL,
                        execution_time_ms REAL NOT NULL
                    )
                """)
                
                # Check current migration version
                current_version = await self._get_migration_version()
                logger.info(f"Current migration version: {current_version or 'none'}")
                
                # Run migrations if needed
                if current_version != self._migration_version:
                    logger.info(f"Running migrations to version {self._migration_version}")
                    
                    # Create all tables
                    for table_name, schema_sql in DATABASE_SCHEMA.items():
                        await db.execute(schema_sql)
                        logger.debug(f"Created table: {table_name}")
                    
                    # Create indexes
                    for index_sql in DATABASE_INDEXES:
                        await db.execute(index_sql)
                        logger.debug(f"Created index: {index_sql[:50]}...")
                    
                    await db.commit()
                    
                    # Record migration
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    await self._record_migration(
                        f"migration_{self._migration_version}",
                        self._migration_version,
                        execution_time
                    )
                    
                    logger.info(f"Database migrations completed in {execution_time:.2f}ms")
                else:
                    logger.info("Database is up to date")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise DatabaseMigrationError(f"Migration failed: {str(e)}")
    
    async def _initialize_default_data(self) -> None:
        """Initialize default data"""
        try:
            async with aiosqlite.connect(self.database_path) as db:
                # Check if doctor status exists
                cursor = await db.execute("SELECT COUNT(*) FROM ai_consultation_doctor_status")
                count = (await cursor.fetchone())[0]
                
                if count == 0:
                    # Create default doctor status
                    await db.execute("""
                        INSERT INTO ai_consultation_doctor_status 
                        (is_available, reason, cost_budget_remaining, daily_usage, monthly_usage, last_updated)
                        VALUES (0, 'manual', 100.0, 0.0, 0.0, ?)
                    """, (datetime.utcnow().isoformat(),))
                    
                    await db.commit()
                    logger.info("Created default doctor status")
                
                # Check if budget exists
                cursor = await db.execute("SELECT COUNT(*) FROM ai_consultation_budget")
                count = (await cursor.fetchone())[0]
                
                if count == 0:
                    # Create default budget
                    await db.execute("""
                        INSERT INTO ai_consultation_budget 
                        (daily_budget, monthly_budget, daily_spent, monthly_spent, cost_per_token, last_reset)
                        VALUES (10.0, 100.0, 0.0, 0.0, 0.0001, ?)
                    """, (datetime.utcnow().isoformat(),))
                    
                    await db.commit()
                    logger.info("Created default budget")
        
        except Exception as e:
            logger.warning(f"Failed to initialize default data: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        try:
            async with aiosqlite.connect(self.database_path) as db:
                # Test basic connectivity
                cursor = await db.execute("SELECT 1")
                await cursor.fetchone()
                
                # Check table existence
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_consultation_%'"
                )
                ai_tables = [row[0] for row in await cursor.fetchall()]
                
                # Get database size
                db_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
                
                # Get migration version
                migration_version = await self._get_migration_version()
                
                return {
                    'status': 'healthy',
                    'database_path': self.database_path,
                    'database_size_bytes': db_size,
                    'tables_count': len(ai_tables),
                    'tables': ai_tables,
                    'migration_version': migration_version,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'database_path': self.database_path,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def backup_data(self, backup_path: str) -> bool:
        """Create backup of AI consultation data"""
        try:
            backup_data = {
                'backup_timestamp': datetime.utcnow().isoformat(),
                'migration_version': await self._get_migration_version(),
                'tables': {}
            }
            
            async with aiosqlite.connect(self.database_path) as db:
                # Get all AI consultation tables
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_consultation_%'"
                )
                tables = [row[0] for row in await cursor.fetchall()]
                
                # Backup each table
                for table_name in tables:
                    cursor = await db.execute(f"SELECT * FROM {table_name}")
                    columns = [description[0] for description in cursor.description]
                    rows = await cursor.fetchall()
                    
                    backup_data['tables'][table_name] = {
                        'columns': columns,
                        'rows': [dict(zip(columns, row)) for row in rows]
                    }
                    
                    logger.debug(f"Backed up {len(rows)} rows from {table_name}")
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Write backup file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, default=str, indent=2)
            
            logger.info(f"Database backup created: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def rollback_migration(self, target_version: Optional[str] = None) -> bool:
        """Rollback database migration"""
        try:
            logger.info(f"Rolling back migration to: {target_version or 'clean state'}")
            
            # Create backup before rollback
            backup_path = f"backups/pre_rollback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            await self.backup_data(backup_path)
            logger.info(f"Created pre-rollback backup: {backup_path}")
            
            async with aiosqlite.connect(self.database_path) as db:
                if target_version is None:
                    # Complete rollback - drop all AI consultation tables
                    cursor = await db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_consultation_%'"
                    )
                    tables = [row[0] for row in await cursor.fetchall()]
                    
                    # Drop tables in reverse dependency order
                    drop_order = [
                        'ai_consultation_queue',
                        'ai_consultation_results', 
                        'ai_consultation_queries',
                        'ai_consultation_budget',
                        'ai_consultation_doctor_status',
                        'ai_consultation_migration_history'
                    ]
                    
                    for table_name in drop_order:
                        if table_name in tables:
                            await db.execute(f"DROP TABLE IF EXISTS {table_name}")
                            logger.info(f"Dropped table: {table_name}")
                    
                    await db.commit()
                    logger.info("Complete rollback completed")
                else:
                    # Partial rollback to specific version (not implemented yet)
                    logger.warning(f"Partial rollback to {target_version} not implemented")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def get_connection(self):
        """Get database connection"""
        return aiosqlite.connect(self.database_path)
    
    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        async with aiosqlite.connect(self.database_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update/insert/delete and return affected rows"""
        async with aiosqlite.connect(self.database_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount
    
    async def cleanup(self) -> None:
        """Cleanup database connections"""
        try:
            # SQLite connections are automatically cleaned up
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Global database manager instance
db_manager = DatabaseManager()


async def get_database_connection():
    """Get database connection"""
    return await db_manager.get_connection()


async def initialize_database() -> None:
    """Initialize database with migrations"""
    await db_manager.initialize()


async def cleanup_database() -> None:
    """Cleanup database connections"""
    await db_manager.cleanup()