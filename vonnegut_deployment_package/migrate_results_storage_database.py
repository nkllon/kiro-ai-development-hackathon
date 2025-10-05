#!/usr/bin/env python3
"""
Results Storage Database Migration Script

Creates and manages database schema for consultation results storage.
Includes rollback capabilities and brownfield safety measures.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from beast_mode.observatory.ai_consultation.database import get_database_connection
from beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag

logger = logging.getLogger(__name__)


class ResultsStorageMigration:
    """Database migration manager for results storage"""
    
    def __init__(self):
        self.db = None
        self.migration_history = []
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.db = await get_database_connection()
            await self._create_migration_table()
            await self._load_migration_history()
            logger.info("Migration system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize migration system: {e}")
            raise
    
    async def _create_migration_table(self):
        """Create migration tracking table"""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS results_storage_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                rollback_sql TEXT,
                checksum VARCHAR(64),
                description TEXT
            )
        """)
    
    async def _load_migration_history(self):
        """Load migration history from database"""
        rows = await self.db.fetch("""
            SELECT migration_name, applied_at, description
            FROM results_storage_migrations
            ORDER BY applied_at
        """)
        
        self.migration_history = [
            {
                'name': row['migration_name'],
                'applied_at': row['applied_at'],
                'description': row['description']
            }
            for row in rows
        ]
        
        logger.info(f"Loaded {len(self.migration_history)} previous migrations")
    
    async def _record_migration(self, name: str, rollback_sql: str, description: str):
        """Record a successful migration"""
        await self.db.execute("""
            INSERT INTO results_storage_migrations (migration_name, rollback_sql, description)
            VALUES ($1, $2, $3)
            ON CONFLICT (migration_name) DO NOTHING
        """, name, rollback_sql, description)
    
    async def _is_migration_applied(self, name: str) -> bool:
        """Check if migration has been applied"""
        result = await self.db.fetchval("""
            SELECT COUNT(*) FROM results_storage_migrations WHERE migration_name = $1
        """, name)
        return result > 0
    
    async def migrate_up(self) -> bool:
        """Apply all pending migrations"""
        try:
            logger.info("Starting results storage database migration")
            
            # Check if results storage is enabled
            if not await feature_flags.is_enabled(FeatureFlag.RESULTS_STORAGE):
                logger.info("Results storage is disabled, skipping migration")
                return True
            
            migrations = [
                {
                    'name': '001_create_consultation_results_table',
                    'description': 'Create consultation_results table with indexes',
                    'up_sql': self._get_consultation_results_table_sql(),
                    'down_sql': 'DROP TABLE IF EXISTS consultation_results CASCADE;'
                },
                {
                    'name': '002_create_query_patterns_table',
                    'description': 'Create query_patterns table for similarity detection',
                    'up_sql': self._get_query_patterns_table_sql(),
                    'down_sql': 'DROP TABLE IF EXISTS query_patterns CASCADE;'
                },
                {
                    'name': '003_create_user_history_table',
                    'description': 'Create user_consultation_history table',
                    'up_sql': self._get_user_history_table_sql(),
                    'down_sql': 'DROP TABLE IF EXISTS user_consultation_history CASCADE;'
                },
                {
                    'name': '004_create_knowledge_base_topics_table',
                    'description': 'Create knowledge_base_topics table',
                    'up_sql': self._get_knowledge_base_topics_table_sql(),
                    'down_sql': 'DROP TABLE IF EXISTS knowledge_base_topics CASCADE;'
                },
                {
                    'name': '005_create_indexes',
                    'description': 'Create performance indexes',
                    'up_sql': self._get_indexes_sql(),
                    'down_sql': self._get_drop_indexes_sql()
                },
                {
                    'name': '006_enable_extensions',
                    'description': 'Enable PostgreSQL extensions for full-text search',
                    'up_sql': self._get_extensions_sql(),
                    'down_sql': '-- Extensions are not dropped for safety'
                }
            ]
            
            applied_count = 0
            
            for migration in migrations:
                if await self._is_migration_applied(migration['name']):
                    logger.info(f"Migration {migration['name']} already applied, skipping")
                    continue
                
                logger.info(f"Applying migration: {migration['name']}")
                
                try:
                    # Apply migration in transaction
                    async with self.db.transaction():
                        await self.db.execute(migration['up_sql'])
                        await self._record_migration(
                            migration['name'],
                            migration['down_sql'],
                            migration['description']
                        )
                    
                    applied_count += 1
                    logger.info(f"Successfully applied migration: {migration['name']}")
                    
                except Exception as e:
                    logger.error(f"Failed to apply migration {migration['name']}: {e}")
                    raise
            
            logger.info(f"Migration complete. Applied {applied_count} new migrations.")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    async def migrate_down(self, target_migration: Optional[str] = None) -> bool:
        """Rollback migrations"""
        try:
            logger.info("Starting results storage database rollback")
            
            # Get migrations to rollback
            if target_migration:
                # Rollback to specific migration
                migrations_to_rollback = []
                for migration in reversed(self.migration_history):
                    migrations_to_rollback.append(migration['name'])
                    if migration['name'] == target_migration:
                        break
            else:
                # Rollback all migrations
                migrations_to_rollback = [m['name'] for m in reversed(self.migration_history)]
            
            rollback_count = 0
            
            for migration_name in migrations_to_rollback:
                logger.info(f"Rolling back migration: {migration_name}")
                
                try:
                    # Get rollback SQL
                    rollback_sql = await self.db.fetchval("""
                        SELECT rollback_sql FROM results_storage_migrations 
                        WHERE migration_name = $1
                    """, migration_name)
                    
                    if not rollback_sql or rollback_sql.strip().startswith('--'):
                        logger.warning(f"No rollback SQL for migration {migration_name}, skipping")
                        continue
                    
                    # Apply rollback in transaction
                    async with self.db.transaction():
                        await self.db.execute(rollback_sql)
                        await self.db.execute("""
                            DELETE FROM results_storage_migrations 
                            WHERE migration_name = $1
                        """, migration_name)
                    
                    rollback_count += 1
                    logger.info(f"Successfully rolled back migration: {migration_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to rollback migration {migration_name}: {e}")
                    raise
            
            logger.info(f"Rollback complete. Rolled back {rollback_count} migrations.")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    async def get_migration_status(self) -> Dict:
        """Get current migration status"""
        try:
            total_migrations = 6  # Total number of migrations defined
            applied_migrations = len(self.migration_history)
            
            # Check table existence
            tables_exist = await self._check_tables_exist()
            
            return {
                'total_migrations': total_migrations,
                'applied_migrations': applied_migrations,
                'pending_migrations': total_migrations - applied_migrations,
                'migration_history': self.migration_history,
                'tables_exist': tables_exist,
                'feature_enabled': await feature_flags.is_enabled(FeatureFlag.RESULTS_STORAGE)
            }
            
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {'error': str(e)}
    
    async def _check_tables_exist(self) -> Dict[str, bool]:
        """Check if required tables exist"""
        tables = [
            'consultation_results',
            'query_patterns',
            'user_consultation_history',
            'knowledge_base_topics'
        ]
        
        table_status = {}
        
        for table in tables:
            exists = await self.db.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """, table)
            table_status[table] = exists
        
        return table_status
    
    def _get_consultation_results_table_sql(self) -> str:
        """Get SQL for consultation_results table"""
        return """
            CREATE TABLE IF NOT EXISTS consultation_results (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                result_id VARCHAR(255) UNIQUE NOT NULL,
                query_id VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                query_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                processing_time FLOAT NOT NULL,
                cost FLOAT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                processing_mode VARCHAR(50) NOT NULL,
                metadata JSONB,
                query_hash VARCHAR(64) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            -- Add trigger for updated_at
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            
            DROP TRIGGER IF EXISTS update_consultation_results_updated_at ON consultation_results;
            CREATE TRIGGER update_consultation_results_updated_at
                BEFORE UPDATE ON consultation_results
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """
    
    def _get_query_patterns_table_sql(self) -> str:
        """Get SQL for query_patterns table"""
        return """
            CREATE TABLE IF NOT EXISTS query_patterns (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                pattern_hash VARCHAR(64) UNIQUE NOT NULL,
                normalized_query TEXT NOT NULL,
                query_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                avg_cost FLOAT,
                avg_processing_time FLOAT,
                success_rate FLOAT DEFAULT 1.0
            );
        """
    
    def _get_user_history_table_sql(self) -> str:
        """Get SQL for user_consultation_history table"""
        return """
            CREATE TABLE IF NOT EXISTS user_consultation_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL,
                result_id VARCHAR(255) NOT NULL,
                consultation_date TIMESTAMP WITH TIME ZONE NOT NULL,
                cost FLOAT NOT NULL,
                satisfaction_rating INTEGER,
                feedback TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                FOREIGN KEY (result_id) REFERENCES consultation_results(result_id) ON DELETE CASCADE
            );
        """
    
    def _get_knowledge_base_topics_table_sql(self) -> str:
        """Get SQL for knowledge_base_topics table"""
        return """
            CREATE TABLE IF NOT EXISTS knowledge_base_topics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                topic_name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                query_count INTEGER DEFAULT 0,
                avg_relevance FLOAT DEFAULT 0.0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            DROP TRIGGER IF EXISTS update_knowledge_base_topics_updated_at ON knowledge_base_topics;
            CREATE TRIGGER update_knowledge_base_topics_updated_at
                BEFORE UPDATE ON knowledge_base_topics
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """
    
    def _get_extensions_sql(self) -> str:
        """Get SQL for enabling PostgreSQL extensions"""
        return """
            -- Enable extensions for full-text search and similarity
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
            CREATE EXTENSION IF NOT EXISTS unaccent;
        """
    
    def _get_indexes_sql(self) -> str:
        """Get SQL for creating performance indexes"""
        return """
            -- Indexes for consultation_results table
            CREATE INDEX IF NOT EXISTS idx_consultation_results_user_id ON consultation_results(user_id);
            CREATE INDEX IF NOT EXISTS idx_consultation_results_timestamp ON consultation_results(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_consultation_results_query_hash ON consultation_results(query_hash);
            CREATE INDEX IF NOT EXISTS idx_consultation_results_cost ON consultation_results(cost);
            CREATE INDEX IF NOT EXISTS idx_consultation_results_processing_mode ON consultation_results(processing_mode);
            
            -- Full-text search indexes
            CREATE INDEX IF NOT EXISTS idx_consultation_results_query_text_fts 
                ON consultation_results USING gin(to_tsvector('english', query_text));
            CREATE INDEX IF NOT EXISTS idx_consultation_results_response_text_fts 
                ON consultation_results USING gin(to_tsvector('english', response_text));
            
            -- JSONB metadata index
            CREATE INDEX IF NOT EXISTS idx_consultation_results_metadata 
                ON consultation_results USING gin(metadata);
            
            -- Similarity indexes
            CREATE INDEX IF NOT EXISTS idx_consultation_results_query_text_trgm 
                ON consultation_results USING gin(query_text gin_trgm_ops);
            
            -- Indexes for query_patterns table
            CREATE INDEX IF NOT EXISTS idx_query_patterns_hash ON query_patterns(pattern_hash);
            CREATE INDEX IF NOT EXISTS idx_query_patterns_count ON query_patterns(query_count DESC);
            CREATE INDEX IF NOT EXISTS idx_query_patterns_last_seen ON query_patterns(last_seen DESC);
            CREATE INDEX IF NOT EXISTS idx_query_patterns_normalized_query_trgm 
                ON query_patterns USING gin(normalized_query gin_trgm_ops);
            
            -- Indexes for user_consultation_history table
            CREATE INDEX IF NOT EXISTS idx_user_history_user_id ON user_consultation_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_history_date ON user_consultation_history(consultation_date DESC);
            CREATE INDEX IF NOT EXISTS idx_user_history_cost ON user_consultation_history(cost);
            CREATE INDEX IF NOT EXISTS idx_user_history_result_id ON user_consultation_history(result_id);
            
            -- Indexes for knowledge_base_topics table
            CREATE INDEX IF NOT EXISTS idx_topics_name ON knowledge_base_topics(topic_name);
            CREATE INDEX IF NOT EXISTS idx_topics_count ON knowledge_base_topics(query_count DESC);
            CREATE INDEX IF NOT EXISTS idx_topics_name_trgm 
                ON knowledge_base_topics USING gin(topic_name gin_trgm_ops);
        """
    
    def _get_drop_indexes_sql(self) -> str:
        """Get SQL for dropping indexes"""
        return """
            -- Drop consultation_results indexes
            DROP INDEX IF EXISTS idx_consultation_results_user_id;
            DROP INDEX IF EXISTS idx_consultation_results_timestamp;
            DROP INDEX IF EXISTS idx_consultation_results_query_hash;
            DROP INDEX IF EXISTS idx_consultation_results_cost;
            DROP INDEX IF EXISTS idx_consultation_results_processing_mode;
            DROP INDEX IF EXISTS idx_consultation_results_query_text_fts;
            DROP INDEX IF EXISTS idx_consultation_results_response_text_fts;
            DROP INDEX IF EXISTS idx_consultation_results_metadata;
            DROP INDEX IF EXISTS idx_consultation_results_query_text_trgm;
            
            -- Drop query_patterns indexes
            DROP INDEX IF EXISTS idx_query_patterns_hash;
            DROP INDEX IF EXISTS idx_query_patterns_count;
            DROP INDEX IF EXISTS idx_query_patterns_last_seen;
            DROP INDEX IF EXISTS idx_query_patterns_normalized_query_trgm;
            
            -- Drop user_consultation_history indexes
            DROP INDEX IF EXISTS idx_user_history_user_id;
            DROP INDEX IF EXISTS idx_user_history_date;
            DROP INDEX IF EXISTS idx_user_history_cost;
            DROP INDEX IF EXISTS idx_user_history_result_id;
            
            -- Drop knowledge_base_topics indexes
            DROP INDEX IF EXISTS idx_topics_name;
            DROP INDEX IF EXISTS idx_topics_count;
            DROP INDEX IF EXISTS idx_topics_name_trgm;
        """
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db:
            await self.db.close()


async def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(description='Results Storage Database Migration')
    parser.add_argument('action', choices=['up', 'down', 'status'], 
                       help='Migration action to perform')
    parser.add_argument('--target', help='Target migration for rollback')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    migration = ResultsStorageMigration()
    
    try:
        await migration.initialize()
        
        if args.action == 'up':
            success = await migration.migrate_up()
            sys.exit(0 if success else 1)
            
        elif args.action == 'down':
            success = await migration.migrate_down(args.target)
            sys.exit(0 if success else 1)
            
        elif args.action == 'status':
            status = await migration.get_migration_status()
            print("\nResults Storage Migration Status:")
            print(f"  Feature Enabled: {status.get('feature_enabled', False)}")
            print(f"  Total Migrations: {status.get('total_migrations', 0)}")
            print(f"  Applied Migrations: {status.get('applied_migrations', 0)}")
            print(f"  Pending Migrations: {status.get('pending_migrations', 0)}")
            
            print("\nTable Status:")
            tables = status.get('tables_exist', {})
            for table, exists in tables.items():
                print(f"  {table}: {'✓' if exists else '✗'}")
            
            print("\nMigration History:")
            for migration_info in status.get('migration_history', []):
                print(f"  {migration_info['applied_at'].strftime('%Y-%m-%d %H:%M:%S')} - {migration_info['name']}")
                print(f"    {migration_info['description']}")
            
    except Exception as e:
        logger.error(f"Migration script failed: {e}")
        sys.exit(1)
        
    finally:
        await migration.cleanup()


if __name__ == '__main__':
    asyncio.run(main())