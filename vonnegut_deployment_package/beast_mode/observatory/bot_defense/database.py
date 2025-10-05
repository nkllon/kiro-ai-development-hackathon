"""
Bot Defense Database Management
Database setup, migrations, and data access layer.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import Attack, BotProfile, DefenseAction, Achievement, BotStatus, AttackType, PREDEFINED_ACHIEVEMENTS
from .config import get_config

logger = logging.getLogger(__name__)

class BotDefenseDatabase:
    """Database manager for bot defense system."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.config = get_config()
        
        if db_path:
            self.db_path = db_path
        elif self.config.database.use_observatory_db:
            # Use Observatory's database directory
            self.db_path = "data/observatory.db"
        else:
            self.db_path = self.config.database.database_url or "data/bot_defense.db"
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.table_prefix = self.config.database.table_prefix
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    async def initialize(self) -> None:
        """Initialize database tables."""
        logger.info("Initializing bot defense database...")
        
        with self._get_connection() as conn:
            # Create attacks table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_prefix}attacks (
                    id TEXT PRIMARY KEY,
                    source_ip TEXT NOT NULL,
                    country TEXT,
                    coordinates_lat REAL,
                    coordinates_lon REAL,
                    endpoint TEXT,
                    user_agent TEXT,
                    method TEXT DEFAULT 'GET',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    attack_type TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    punishment_level INTEGER DEFAULT 0,
                    bandwidth_wasted INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    headers TEXT,
                    query_params TEXT,
                    response_code INTEGER DEFAULT 200,
                    response_size INTEGER DEFAULT 0
                )
            """)
            
            # Create bot profiles table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_prefix}bot_profiles (
                    ip TEXT PRIMARY KEY,
                    country TEXT,
                    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    attack_count INTEGER DEFAULT 0,
                    max_punishment_level INTEGER DEFAULT 0,
                    total_bandwidth_wasted INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    achievements TEXT,
                    most_targeted_endpoints TEXT,
                    user_agents TEXT,
                    attack_patterns TEXT,
                    blocked_at DATETIME,
                    block_reason TEXT,
                    block_duration_hours INTEGER
                )
            """)
            
            # Create defense actions table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_prefix}defense_actions (
                    id TEXT PRIMARY KEY,
                    attack_id TEXT,
                    action_type TEXT,
                    intensity INTEGER DEFAULT 1,
                    success BOOLEAN DEFAULT TRUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    execution_time_ms REAL DEFAULT 0.0,
                    bytes_generated INTEGER DEFAULT 0,
                    cpu_usage_percent REAL DEFAULT 0.0,
                    FOREIGN KEY (attack_id) REFERENCES {self.table_prefix}attacks (id)
                )
            """)
            
            # Create blocked IPs table
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_prefix}blocked_ips (
                    ip TEXT PRIMARY KEY,
                    blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT,
                    final_punishment_level INTEGER,
                    total_bandwidth_wasted INTEGER,
                    block_duration_hours INTEGER DEFAULT 24
                )
            """)
            
            # Create indexes for performance
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}attacks_ip ON {self.table_prefix}attacks (source_ip)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}attacks_timestamp ON {self.table_prefix}attacks (timestamp)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}attacks_status ON {self.table_prefix}attacks (status)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}defense_actions_attack_id ON {self.table_prefix}defense_actions (attack_id)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table_prefix}defense_actions_timestamp ON {self.table_prefix}defense_actions (timestamp)")
            
            conn.commit()
        
        logger.info("Bot defense database initialized successfully")

# Global database instance
_database: Optional[BotDefenseDatabase] = None

def get_database() -> BotDefenseDatabase:
    """Get the global database instance."""
    global _database
    if _database is None:
        _database = BotDefenseDatabase()
    return _database

async def initialize_database() -> None:
    """Initialize the global database."""
    db = get_database()
    await db.initialize()