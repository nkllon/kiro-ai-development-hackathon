#!/usr/bin/env python3
"""
AI Consultation Database Migration Script

This script manages database migrations for the AI consultation system,
ensuring safe deployment without affecting existing Observatory data.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from beast_mode.observatory.ai_consultation.database import (
    DatabaseManager, DatabaseMigrationError, initialize_database, cleanup_database
)
from beast_mode.observatory.ai_consultation.feature_flags import feature_flags, FeatureFlag

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_database_status(db_manager: DatabaseManager) -> Dict[str, Any]:
    """Check current database status"""
    try:
        health = await db_manager.health_check()
        return health
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


async def run_migrations(
    database_url: str = None,
    force: bool = False,
    backup: bool = True
) -> bool:
    """
    Run database migrations
    
    Args:
        database_url: Database URL (optional)
        force: Force migration even if database exists
        backup: Create backup before migration
        
    Returns:
        True if successful
    """
    try:
        # Create database manager
        db_manager = DatabaseManager(database_path=database_url)
        
        logger.info("Starting AI consultation database migration")
        
        # Check current status
        logger.info("Checking current database status...")
        status = await check_database_status(db_manager)
        
        if status['status'] == 'healthy' and not force:
            logger.info("Database already exists and is healthy")
            logger.info(f"Tables: {status.get('tables', [])}")
            return True
        
        # Create backup if requested
        if backup and status['status'] == 'healthy':
            backup_path = f"backup_ai_consultation_{int(asyncio.get_event_loop().time())}.json"
            logger.info(f"Creating backup: {backup_path}")
            backup_success = await db_manager.backup_data(backup_path)
            if backup_success:
                logger.info(f"Backup created successfully: {backup_path}")
            else:
                logger.warning("Backup failed, continuing with migration")
        
        # Enable database storage feature
        await feature_flags.set_flag(FeatureFlag.RESULTS_STORAGE.value, True)
        
        # Run migrations
        logger.info("Running database migrations...")
        await db_manager.initialize()
        
        # Verify migration success
        logger.info("Verifying migration...")
        final_status = await check_database_status(db_manager)
        
        if final_status['status'] == 'healthy':
            logger.info("✅ Migration completed successfully!")
            logger.info(f"Created tables: {final_status.get('tables', [])}")
            return True
        else:
            logger.error("❌ Migration verification failed")
            logger.error(f"Status: {final_status}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    
    finally:
        # Cleanup connections
        try:
            await cleanup_database()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


async def rollback_migrations(
    database_url: str = None,
    target_revision: str = None,
    confirm: bool = False
) -> bool:
    """
    Rollback database migrations
    
    Args:
        database_url: Database URL (optional)
        target_revision: Target revision to rollback to
        confirm: Confirm rollback operation
        
    Returns:
        True if successful
    """
    try:
        if not confirm:
            logger.error("Rollback requires --confirm flag for safety")
            return False
        
        # Create database manager
        db_manager = DatabaseManager(database_path=database_url)
        
        logger.info("Starting AI consultation database rollback")
        logger.warning("⚠️  This will remove AI consultation data!")
        
        # Check current status
        status = await check_database_status(db_manager)
        if status['status'] != 'healthy':
            logger.warning("Database is not healthy, proceeding with rollback anyway")
        
        # Create backup before rollback
        backup_path = f"rollback_backup_{int(asyncio.get_event_loop().time())}.json"
        logger.info(f"Creating rollback backup: {backup_path}")
        await db_manager.backup_data(backup_path)
        
        # Perform rollback
        logger.info("Performing rollback...")
        success = await db_manager.rollback_migration(target_revision)
        
        if success:
            logger.info("✅ Rollback completed successfully!")
            
            # Disable database storage feature
            await feature_flags.set_flag(FeatureFlag.RESULTS_STORAGE.value, False)
            
            return True
        else:
            logger.error("❌ Rollback failed")
            return False
    
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        return False
    
    finally:
        # Cleanup connections
        try:
            await cleanup_database()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


async def check_status(database_url: str = None) -> None:
    """Check database status"""
    try:
        db_manager = DatabaseManager(database_path=database_url)
        
        logger.info("Checking AI consultation database status...")
        status = await check_database_status(db_manager)
        
        print("\n" + "="*60)
        print("AI CONSULTATION DATABASE STATUS")
        print("="*60)
        
        if status['status'] == 'healthy':
            print("✅ Status: HEALTHY")
            print(f"📊 Tables: {len(status.get('tables', []))}")
            for table in status.get('tables', []):
                print(f"   - {table}")
            print(f"🕐 Last Check: {status.get('timestamp', 'Unknown')}")
        elif status['status'] == 'unhealthy':
            print("❌ Status: UNHEALTHY")
            print(f"🚨 Error: {status.get('error', 'Unknown error')}")
        else:
            print("⚠️  Status: UNKNOWN")
            print(f"📝 Details: {status}")
        
        print("="*60)
    
    except Exception as e:
        logger.error(f"Status check failed: {e}")
    
    finally:
        try:
            await cleanup_database()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Manage AI consultation database migrations"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run database migrations')
    migrate_parser.add_argument(
        '--database-path',
        help='Database file path (default: from environment)'
    )
    migrate_parser.add_argument(
        '--force',
        action='store_true',
        help='Force migration even if database exists'
    )
    migrate_parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback database migrations')
    rollback_parser.add_argument(
        '--database-path',
        help='Database file path (default: from environment)'
    )
    rollback_parser.add_argument(
        '--target',
        help='Target revision to rollback to'
    )
    rollback_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm rollback operation (required for safety)'
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check database status')
    status_parser.add_argument(
        '--database-path',
        help='Database file path (default: from environment)'
    )
    
    # Verbose logging
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    success = True
    
    if args.command == 'migrate':
        success = await run_migrations(
            database_url=args.database_path,
            force=args.force,
            backup=not args.no_backup
        )
    elif args.command == 'rollback':
        success = await rollback_migrations(
            database_url=args.database_path,
            target_revision=args.target,
            confirm=args.confirm
        )
    elif args.command == 'status':
        await check_status(database_url=args.database_path)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())