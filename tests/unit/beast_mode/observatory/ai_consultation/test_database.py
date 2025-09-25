"""
Unit tests for Database Management System
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from datetime import datetime

from src.beast_mode.observatory.ai_consultation.database import (
    DatabaseManager,
    DatabaseMigrationError,
    initialize_database,
    cleanup_database,
    DATABASE_SCHEMA,
    DATABASE_INDEXES
)
from src.beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    @pytest.fixture
    def temp_migration_dir(self):
        """Create temporary migration directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def db_manager(self, temp_migration_dir):
        """Create DatabaseManager instance with temporary directory"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        return DatabaseManager(
            database_path=db_path,
            migration_dir=temp_migration_dir
        )
    
    def test_database_manager_initialization(self, db_manager):
        """Test database manager initialization"""
        assert db_manager.database_path.endswith('.db')
        assert db_manager.schema_prefix == "ai_consultation_"
        assert db_manager._migration_version == "1.0.0"
    
    def test_get_database_path_from_env(self):
        """Test getting database path from environment"""
        with patch.dict(os.environ, {'AI_CONSULTATION_DATABASE_PATH': '/test/db.sqlite'}):
            manager = DatabaseManager()
            assert manager.database_path == '/test/db.sqlite'
    
    def test_get_database_path_default(self):
        """Test default database path"""
        with patch.dict(os.environ, {}, clear=True):
            manager = DatabaseManager()
            assert 'ai_consultation.db' in manager.database_path
    
    @pytest.mark.asyncio
    async def test_initialize_with_feature_disabled(self, db_manager):
        """Test initialization when feature is disabled"""
        await feature_flags.set_flag(FeatureFlag.RESULTS_STORAGE.value, False)
        
        await db_manager.initialize()
        
        # Should not create tables when feature is disabled
        health = await db_manager.health_check()
        assert health['tables_count'] == 0
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, db_manager):
        """Test health check when database is healthy"""
        await feature_flags.set_flag(FeatureFlag.RESULTS_STORAGE.value, True)
        await db_manager.initialize()
        
        result = await db_manager.health_check()
        
        assert result['status'] == 'healthy'
        assert 'tables_count' in result
        assert 'timestamp' in result
        assert result['tables_count'] > 0
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, db_manager):
        """Test health check when database is unhealthy"""
        # Use invalid database path
        invalid_manager = DatabaseManager(database_path="/invalid/path/db.sqlite")
        
        result = await invalid_manager.health_check()
        
        assert result['status'] == 'unhealthy'
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_backup_data(self, db_manager):
        """Test data backup functionality"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            backup_path = temp_file.name
        
        try:
            # Mock session and query results
            with patch('src.beast_mode.observatory.ai_consultation.database.get_database_session') as mock_session:
                mock_session_instance = AsyncMock()
                mock_session_instance.execute = AsyncMock()
                mock_session_instance.execute.return_value = []
                mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
                mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
                
                result = await db_manager.backup_data(backup_path)
                
                assert result is True
                assert os.path.exists(backup_path)
        
        finally:
            if os.path.exists(backup_path):
                os.unlink(backup_path)
    
    @pytest.mark.asyncio
    async def test_rollback_migration(self, db_manager):
        """Test migration rollback"""
        with patch.object(db_manager.async_engine, 'begin') as mock_begin:
            mock_conn = AsyncMock()
            mock_conn.run_sync = AsyncMock()
            mock_begin.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_begin.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await db_manager.rollback_migration()
            
            assert result is True
            mock_conn.run_sync.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup(self, db_manager):
        """Test database cleanup"""
        with patch.object(db_manager.async_engine, 'dispose') as mock_async_dispose:
            with patch.object(db_manager.sync_engine, 'dispose') as mock_sync_dispose:
                await db_manager.cleanup()
                
                mock_async_dispose.assert_called_once()
                mock_sync_dispose.assert_called_once()


class TestDatabaseTables:
    """Test database table definitions"""
    
    def test_consultation_query_table(self):
        """Test ConsultationQueryTable definition"""
        table = ConsultationQueryTable.__table__
        
        assert table.name == 'ai_consultation_queries'
        assert 'id' in table.columns
        assert 'query_id' in table.columns
        assert 'user_id' in table.columns
        assert 'query_text' in table.columns
        assert 'timestamp' in table.columns
        
        # Check indexes
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_user_timestamp' in index_names
        assert 'idx_session_timestamp' in index_names
        assert 'idx_priority_timestamp' in index_names
    
    def test_consultation_result_table(self):
        """Test ConsultationResultTable definition"""
        table = ConsultationResultTable.__table__
        
        assert table.name == 'ai_consultation_results'
        assert 'id' in table.columns
        assert 'result_id' in table.columns
        assert 'query_id' in table.columns
        assert 'response' in table.columns
        assert 'cost' in table.columns
        assert 'tokens_used' in table.columns
        
        # Check foreign key
        fks = [fk.column.name for fk in table.foreign_keys]
        assert 'query_id' in fks
    
    def test_doctor_status_table(self):
        """Test DoctorStatusTable definition"""
        table = DoctorStatusTable.__table__
        
        assert table.name == 'ai_consultation_doctor_status'
        assert 'id' in table.columns
        assert 'is_available' in table.columns
        assert 'reason' in table.columns
        assert 'cost_budget_remaining' in table.columns
        assert 'daily_usage' in table.columns
        assert 'monthly_usage' in table.columns
    
    def test_queued_query_table(self):
        """Test QueuedQueryTable definition"""
        table = QueuedQueryTable.__table__
        
        assert table.name == 'ai_consultation_queue'
        assert 'id' in table.columns
        assert 'queue_id' in table.columns
        assert 'query_id' in table.columns
        assert 'queued_at' in table.columns
        assert 'priority' in table.columns
        
        # Check indexes
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_priority_queued' in index_names
        assert 'idx_processing_status' in index_names
    
    def test_budget_status_table(self):
        """Test BudgetStatusTable definition"""
        table = BudgetStatusTable.__table__
        
        assert table.name == 'ai_consultation_budget'
        assert 'id' in table.columns
        assert 'date' in table.columns
        assert 'daily_budget' in table.columns
        assert 'monthly_budget' in table.columns
        assert 'daily_spent' in table.columns
        assert 'monthly_spent' in table.columns


class TestDatabaseIntegration:
    """Test database integration functions"""
    
    @pytest.mark.asyncio
    async def test_initialize_database(self):
        """Test database initialization function"""
        with patch('src.beast_mode.observatory.ai_consultation.database.db_manager') as mock_manager:
            mock_manager.initialize = AsyncMock()
            
            await initialize_database()
            
            mock_manager.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_database(self):
        """Test database cleanup function"""
        with patch('src.beast_mode.observatory.ai_consultation.database.db_manager') as mock_manager:
            mock_manager.cleanup = AsyncMock()
            
            await cleanup_database()
            
            mock_manager.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_database_session(self):
        """Test getting database session"""
        from src.beast_mode.observatory.ai_consultation.database import get_database_session
        
        with patch('src.beast_mode.observatory.ai_consultation.database.db_manager') as mock_manager:
            mock_session_factory = MagicMock()
            mock_manager.async_session_factory = mock_session_factory
            
            result = get_database_session()
            
            assert result == mock_session_factory.return_value


class TestDatabaseMigrationError:
    """Test DatabaseMigrationError exception"""
    
    def test_database_migration_error_creation(self):
        """Test creating DatabaseMigrationError"""
        error = DatabaseMigrationError("Migration failed", "v1.0.0")
        
        assert error.message == "Migration failed"
        assert error.error_code == "DATABASE_MIGRATION_ERROR"
        assert error.details["migration_version"] == "v1.0.0"
        assert error.retry_possible is False
    
    def test_database_migration_error_without_version(self):
        """Test creating DatabaseMigrationError without version"""
        error = DatabaseMigrationError("Migration failed")
        
        assert error.message == "Migration failed"
        assert error.details["migration_version"] is None


if __name__ == "__main__":
    pytest.main([__file__])