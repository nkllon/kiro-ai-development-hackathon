"""
Database Connection Utilities

This module provides database connection management with error handling,
connection pooling, and systematic validation for the Directus reconciliation system.
"""

import os
import logging
from typing import Dict, Any, Optional, ContextManager
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class DatabaseConnection:
    """
    Database connection manager with error handling and validation.
    
    Provides systematic database connection management with proper error handling,
    connection validation, and resource cleanup.
    """
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """
        Initialize database connection manager.
        
        Args:
            connection_params: Database connection parameters. If None, uses environment variables.
        """
        self.logger = logging.getLogger(__name__)
        self.connection_params = connection_params or self._get_default_params()
        self._validate_connection_params()
    
    def _get_default_params(self) -> Dict[str, Any]:
        """Get default connection parameters from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_DATABASE', 'directus'),
            'user': os.getenv('DB_USER', 'directus'),
            'password': os.getenv("DB_PASSWORD", ""),
            'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '10'))
        }
    
    def _validate_connection_params(self) -> None:
        """Validate connection parameters are complete and valid."""
        required_params = ['host', 'port', 'database', 'user', 'password']
        
        for param in required_params:
            if param not in self.connection_params or not self.connection_params[param]:
                raise ValueError(f"Missing required database parameter: {param}")
        
        # Validate port is numeric
        if not isinstance(self.connection_params['port'], int):
            raise ValueError("Database port must be an integer")
        
        if self.connection_params['port'] < 1 or self.connection_params['port'] > 65535:
            raise ValueError("Database port must be between 1 and 65535")
    
    @contextmanager
    def get_connection(self, autocommit: bool = False) -> ContextManager[psycopg2.extensions.connection]:
        """
        Get database connection with automatic cleanup.
        
        Args:
            autocommit: Whether to enable autocommit mode
            
        Yields:
            Database connection object
            
        Raises:
            psycopg2.Error: If connection fails
        """
        conn = None
        try:
            self.logger.debug("Establishing database connection")
            conn = psycopg2.connect(**self.connection_params)
            
            if autocommit:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            self.logger.debug("Database connection established successfully")
            yield conn
            
        except psycopg2.Error as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in database connection: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                self.logger.debug("Database connection closed")
    
    @contextmanager
    def get_cursor(self, autocommit: bool = False) -> ContextManager[psycopg2.extensions.cursor]:
        """
        Get database cursor with automatic cleanup.
        
        Args:
            autocommit: Whether to enable autocommit mode
            
        Yields:
            Database cursor object
        """
        with self.get_connection(autocommit=autocommit) as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if not autocommit:
                    conn.commit()
            except Exception:
                if not autocommit:
                    conn.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test database connection and return status information.
        
        Returns:
            Dictionary with connection test results
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                cursor.close()
                
                return {
                    'success': True,
                    'message': 'Database connection successful',
                    'database_version': version,
                    'connection_params': {
                        'host': self.connection_params['host'],
                        'port': self.connection_params['port'],
                        'database': self.connection_params['database'],
                        'user': self.connection_params['user']
                        # Note: password not included for security
                    }
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Database connection failed: {str(e)}',
                'error': str(e)
            }


class ConnectionPool:
    """
    Database connection pool for high-performance applications.
    
    Provides connection pooling with automatic connection management,
    health checking, and resource optimization.
    """
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None, 
                 min_connections: int = 1, max_connections: int = 10):
        """
        Initialize connection pool.
        
        Args:
            connection_params: Database connection parameters
            min_connections: Minimum number of connections to maintain
            max_connections: Maximum number of connections allowed
        """
        self.logger = logging.getLogger(__name__)
        self.connection_params = connection_params or DatabaseConnection()._get_default_params()
        
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_connections,
                max_connections,
                **self.connection_params
            )
            self.logger.info(f"Connection pool created with {min_connections}-{max_connections} connections")
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self) -> ContextManager[psycopg2.extensions.connection]:
        """
        Get connection from pool with automatic return.
        
        Yields:
            Database connection from pool
        """
        conn = None
        try:
            conn = self.pool.getconn()
            if conn:
                yield conn
            else:
                raise Exception("Failed to get connection from pool")
        except Exception as e:
            self.logger.error(f"Connection pool error: {str(e)}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            self.logger.info("All connections in pool closed")
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get connection pool status information.
        
        Returns:
            Dictionary with pool status details
        """
        if not self.pool:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'active',
            'min_connections': self.pool.minconn,
            'max_connections': self.pool.maxconn,
            'available_connections': len(self.pool._pool),
            'used_connections': len(self.pool._used)
        }