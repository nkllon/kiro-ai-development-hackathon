"""
Database Connection Utilities for Directus CMS

Provides systematic database connection management with error handling,
connection pooling, and health monitoring for the Directus CMS system.

Requirements Addressed:
- 1.1: Database connection utilities with error handling
- 4.2: Prevent schema inconsistencies with proper connection management
- 9.4: Structured logging with correlation IDs
"""

import os
import logging
import time
from typing import Dict, Any, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

try:
    import psycopg2
    from psycopg2 import pool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


class ConnectionStatus(Enum):
    """Database connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CONNECTING = "connecting"


@dataclass
class ConnectionConfig:
    """Database connection configuration"""
    database_type: DatabaseType
    host: str = "localhost"
    port: int = 5432
    database: str = "directus"
    username: str = "directus"
    password: str = field(default_factory=lambda: os.getenv("DIRECTUS_DB_PASSWORD", ""))
    connection_url: str = None
    pool_size: int = 5
    max_overflow: int = 10
    timeout: int = 30


@dataclass
class ConnectionHealth:
    """Database connection health information"""
    status: ConnectionStatus
    response_time_ms: float
    active_connections: int
    total_connections: int
    error_message: Optional[str] = None
    last_check: str = None


class DatabaseConnectionManager:
    """
    Systematic database connection management with error handling and monitoring
    
    Provides:
    - Connection pooling for PostgreSQL
    - Automatic reconnection on failure
    - Health monitoring and metrics
    - Structured logging with correlation IDs
    - Transaction management with rollback capability
    """
    
    def __init__(self, config: ConnectionConfig, correlation_id: str = None):
        """
        Initialize database connection manager
        
        Args:
            config: Database connection configuration
            correlation_id: Correlation ID for logging
        """
        self.config = config
        self.correlation_id = correlation_id or "db_conn"
        self.connection_pool = None
        self.single_connection = None
        self.status = ConnectionStatus.DISCONNECTED
        
        self._logger = logging.getLogger(f"database_utils.{self.correlation_id}")
        self._connection_attempts = 0
        self._last_error = None
        
        # Validate database type availability
        if config.database_type == DatabaseType.POSTGRESQL and not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL support not available. Install with: pip install psycopg2-binary")
        
        if config.database_type == DatabaseType.SQLITE and not SQLITE_AVAILABLE:
            raise ImportError("SQLite support not available")
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection or connection pool"""
        try:
            self.status = ConnectionStatus.CONNECTING
            self._connection_attempts += 1
            
            if self.config.database_type == DatabaseType.POSTGRESQL:
                self._initialize_postgresql_pool()
            elif self.config.database_type == DatabaseType.SQLITE:
                self._initialize_sqlite_connection()
            else:
                raise ValueError(f"Unsupported database type: {self.config.database_type}")
            
            self.status = ConnectionStatus.CONNECTED
            self._logger.info(
                f"Database connection established",
                extra={
                    "correlation_id": self.correlation_id,
                    "database_type": self.config.database_type.value,
                    "attempt": self._connection_attempts
                }
            )
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self._last_error = str(e)
            self._logger.error(
                f"Database connection failed: {e}",
                extra={
                    "correlation_id": self.correlation_id,
                    "database_type": self.config.database_type.value,
                    "attempt": self._connection_attempts,
                    "error": str(e)
                }
            )
            raise
    
    def _initialize_postgresql_pool(self):
        """Initialize PostgreSQL connection pool"""
        connection_url = self.config.connection_url or self._build_postgresql_url()
        
        self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=self.config.pool_size,
            dsn=connection_url
        )
        
        # Test connection
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
    
    def _initialize_sqlite_connection(self):
        """Initialize SQLite connection"""
        db_path = self.config.connection_url or self.config.database
        if db_path.startswith("sqlite://"):
            db_path = db_path.replace("sqlite://", "")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        
        self.single_connection = sqlite3.connect(
            db_path,
            timeout=self.config.timeout,
            check_same_thread=False
        )
        
        # Enable foreign key constraints
        self.single_connection.execute("PRAGMA foreign_keys = ON")
        
        # Test connection
        cursor = self.single_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
    
    def _build_postgresql_url(self) -> str:
        """Build PostgreSQL connection URL from config"""
        return (
            f"postgresql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection with automatic cleanup
        
        Yields:
            Database connection object
        """
        connection = None
        try:
            if self.config.database_type == DatabaseType.POSTGRESQL:
                if not self.connection_pool:
                    raise Exception("Connection pool not initialized")
                connection = self.connection_pool.getconn()
            else:  # SQLite
                if not self.single_connection:
                    raise Exception("SQLite connection not initialized")
                connection = self.single_connection
            
            yield connection
            
        except Exception as e:
            self._logger.error(
                f"Database connection error: {e}",
                extra={
                    "correlation_id": self.correlation_id,
                    "error": str(e)
                }
            )
            
            # Rollback transaction on error
            if connection:
                try:
                    connection.rollback()
                except Exception:
                    pass
            
            raise
        finally:
            # Return connection to pool (PostgreSQL only)
            if connection and self.config.database_type == DatabaseType.POSTGRESQL:
                try:
                    self.connection_pool.putconn(connection)
                except Exception as e:
                    self._logger.warning(f"Error returning connection to pool: {e}")
    
    @contextmanager
    def get_transaction(self, autocommit: bool = True):
        """
        Get database transaction with automatic commit/rollback
        
        Args:
            autocommit: Whether to automatically commit on success
            
        Yields:
            Database connection with transaction
        """
        with self.get_connection() as connection:
            try:
                # Start transaction
                if self.config.database_type == DatabaseType.POSTGRESQL:
                    connection.autocommit = False
                
                yield connection
                
                # Commit transaction on success
                if autocommit:
                    connection.commit()
                    self._logger.debug(
                        "Transaction committed",
                        extra={"correlation_id": self.correlation_id}
                    )
                
            except Exception as e:
                # Rollback transaction on error
                try:
                    connection.rollback()
                    self._logger.warning(
                        f"Transaction rolled back due to error: {e}",
                        extra={
                            "correlation_id": self.correlation_id,
                            "error": str(e)
                        }
                    )
                except Exception as rollback_error:
                    self._logger.error(
                        f"Rollback failed: {rollback_error}",
                        extra={"correlation_id": self.correlation_id}
                    )
                
                raise
            finally:
                # Reset autocommit for PostgreSQL
                if self.config.database_type == DatabaseType.POSTGRESQL:
                    try:
                        connection.autocommit = True
                    except Exception:
                        pass
    
    def execute_query(self, query: str, params: tuple = None, fetch_results: bool = True) -> Optional[list]:
        """
        Execute SQL query with error handling and logging
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_results: Whether to fetch and return results
            
        Returns:
            Query results if fetch_results is True, None otherwise
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                results = None
                if fetch_results:
                    results = cursor.fetchall()
                
                cursor.close()
                
                execution_time = (time.time() - start_time) * 1000
                self._logger.debug(
                    f"Query executed successfully",
                    extra={
                        "correlation_id": self.correlation_id,
                        "query": query[:100] + "..." if len(query) > 100 else query,
                        "execution_time_ms": execution_time,
                        "result_count": len(results) if results else 0
                    }
                )
                
                return results
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._logger.error(
                f"Query execution failed: {e}",
                extra={
                    "correlation_id": self.correlation_id,
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "execution_time_ms": execution_time,
                    "error": str(e)
                }
            )
            raise
    
    def check_health(self) -> ConnectionHealth:
        """
        Check database connection health
        
        Returns:
            ConnectionHealth with status and metrics
        """
        start_time = time.time()
        
        try:
            # Test connection with simple query
            self.execute_query("SELECT 1", fetch_results=True)
            
            response_time = (time.time() - start_time) * 1000
            
            # Get connection pool stats
            active_connections = 0
            total_connections = 0
            
            if self.config.database_type == DatabaseType.POSTGRESQL and self.connection_pool:
                # PostgreSQL pool stats (approximate)
                total_connections = self.config.pool_size
                # Note: psycopg2 doesn't provide easy access to active connection count
                active_connections = 1  # Approximate
            elif self.config.database_type == DatabaseType.SQLITE:
                total_connections = 1
                active_connections = 1 if self.single_connection else 0
            
            return ConnectionHealth(
                status=ConnectionStatus.CONNECTED,
                response_time_ms=response_time,
                active_connections=active_connections,
                total_connections=total_connections,
                last_check=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return ConnectionHealth(
                status=ConnectionStatus.ERROR,
                response_time_ms=response_time,
                active_connections=0,
                total_connections=0,
                error_message=str(e),
                last_check=time.strftime("%Y-%m-%d %H:%M:%S")
            )
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to database
        
        Returns:
            True if reconnection successful, False otherwise
        """
        try:
            self._logger.info(
                "Attempting database reconnection",
                extra={"correlation_id": self.correlation_id}
            )
            
            # Close existing connections
            self.close()
            
            # Reinitialize connection
            self._initialize_connection()
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Database reconnection failed: {e}",
                extra={
                    "correlation_id": self.correlation_id,
                    "error": str(e)
                }
            )
            return False
    
    def close(self):
        """Close database connections"""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                self.connection_pool = None
            
            if self.single_connection:
                self.single_connection.close()
                self.single_connection = None
            
            self.status = ConnectionStatus.DISCONNECTED
            
            self._logger.info(
                "Database connections closed",
                extra={"correlation_id": self.correlation_id}
            )
            
        except Exception as e:
            self._logger.error(
                f"Error closing database connections: {e}",
                extra={
                    "correlation_id": self.correlation_id,
                    "error": str(e)
                }
            )
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information and statistics"""
        health = self.check_health()
        
        return {
            "database_type": self.config.database_type.value,
            "status": self.status.value,
            "health": {
                "status": health.status.value,
                "response_time_ms": health.response_time_ms,
                "active_connections": health.active_connections,
                "total_connections": health.total_connections,
                "error_message": health.error_message,
                "last_check": health.last_check
            },
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "pool_size": self.config.pool_size,
                "timeout": self.config.timeout
            },
            "statistics": {
                "connection_attempts": self._connection_attempts,
                "last_error": self._last_error
            }
        }
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.close()
        except Exception:
            pass


def create_connection_manager(
    database_url: str = None,
    database_type: str = "postgresql",
    correlation_id: str = None
) -> DatabaseConnectionManager:
    """
    Factory function to create database connection manager
    
    Args:
        database_url: Database connection URL
        database_type: Type of database (postgresql, sqlite)
        correlation_id: Correlation ID for logging
        
    Returns:
        Configured DatabaseConnectionManager instance
    """
    # Parse database URL or use environment variables
    if not database_url:
        database_url = os.getenv(
            "DATABASE_URL",
            "        os.getenv('DIRECTUS_DATABASE_URL', 'postgresql://directus:directus@localhost:5432/directus')"
        )
    
    # Create configuration
    config = ConnectionConfig(
        database_type=DatabaseType(database_type),
        connection_url=database_url,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        timeout=int(os.getenv("DB_TIMEOUT", "30"))
    )
    
    return DatabaseConnectionManager(config, correlation_id)