#!/usr/bin/env python3
"""
Glacier Spore System - Self-Describing Messages with Embedded Schemata

Every object is a message that contains:
1. Self-describing schemata
2. Dimensional metadata
3. Relationship vectors
4. Processing instructions
5. Content hash for integrity

This creates a dimension-aware system that can:
- Count dimensions across all spores
- Analyze orphaned dimensions
- Track relationship patterns
- Enable post-processing via triggers
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import Any, Dict, List, Optional, Set, Tuple, Union


class SporeType(Enum):
    """Types of glacier spores"""

    DISCOVERY = "discovery"  # Repository discovery
    ANALYSIS = "analysis"  # Code analysis
    METRIC = "metric"  # Quality/metrics
    PATTERN = "pattern"  # Detected patterns
    RELATIONSHIP = "relationship"  # Relationship data
    TRIGGER = "trigger"  # Processing trigger
    EVENT = "event"  # System events
    DIMENSION = "dimension"  # Dimension definition
    SCHEMA = "schema"  # Schema definition
    PROCESSOR = "processor"  # Processor definition


class DimensionType(Enum):
    """Types of dimensions in the system"""

    TEMPORAL = "temporal"  # Time-based
    SPATIAL = "spatial"  # Location-based
    SEMANTIC = "semantic"  # Meaning-based
    STRUCTURAL = "structural"  # Code structure
    QUALITY = "quality"  # Quality metrics
    SECURITY = "security"  # Security aspects
    PERFORMANCE = "performance"  # Performance metrics
    DEPENDENCY = "dependency"  # Dependencies
    ARCHITECTURE = "architecture"  # Architecture patterns
    TECHNOLOGY = "technology"  # Technology stack


@dataclass
class Dimension:
    """A dimension in the glacier spore system"""

    dimension_id: str
    dimension_type: DimensionType
    name: str
    description: str

    # Dimensional properties
    cardinality: Optional[int] = None  # Number of distinct values
    range_min: Optional[Union[int, float, str]] = None
    range_max: Optional[Union[int, float, str]] = None
    unit: Optional[str] = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: set[str] = field(default_factory=set)

    # Relationships
    parent_dimension_id: Optional[str] = None
    child_dimension_ids: list[str] = field(default_factory=list)

    # Usage tracking
    usage_count: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["dimension_type"] = self.dimension_type.value
        data["tags"] = list(self.tags)
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        if self.last_used:
            data["last_used"] = self.last_used.isoformat()
        return data


@dataclass
class GlacierSpore:
    """
    A glacier spore - a self-describing message with embedded schemata

    Every spore contains:
    1. Self-describing metadata
    2. Embedded schemata
    3. Dimensional vectors
    4. Processing instructions
    5. Content integrity
    """

    # Core identification
    spore_id: str
    spore_type: SporeType
    content_hash: str

    # Self-describing schemata
    embedded_schema: dict[str, Any]  # Schema that describes this spore
    content_schema: dict[str, Any]  # Schema for the content

    # Content and data
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    # Dimensional vectors
    dimensions: dict[str, Any] = field(default_factory=dict)  # Dimension values
    dimension_refs: list[str] = field(default_factory=list)  # Referenced dimension IDs

    # Processing instructions
    processing_triggers: list[str] = field(default_factory=list)
    processor_requirements: dict[str, Any] = field(default_factory=dict)

    # Relationships
    parent_spore_id: Optional[str] = None
    child_spore_ids: list[str] = field(default_factory=list)
    related_spore_ids: list[str] = field(default_factory=list)

    # Temporal metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    last_processed: Optional[datetime] = None

    # Processing state
    processed: bool = False
    processing_errors: list[str] = field(default_factory=list)
    processing_history: list[dict[str, Any]] = field(default_factory=list)

    # Integrity and validation
    validation_checksum: Optional[str] = None
    signature: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["spore_type"] = self.spore_type.value
        data["created_at"] = self.created_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        if self.last_processed:
            data["last_processed"] = self.last_processed.isoformat()
        return data

    def get_dimension_value(self, dimension_name: str) -> Optional[Any]:
        """Get value for a specific dimension"""
        return self.dimensions.get(dimension_name)

    def set_dimension_value(self, dimension_name: str, value: Any):
        """Set value for a specific dimension"""
        self.dimensions[dimension_name] = value

    def add_processing_trigger(self, trigger_id: str):
        """Add a processing trigger"""
        if trigger_id not in self.processing_triggers:
            self.processing_triggers.append(trigger_id)

    def validate_integrity(self) -> bool:
        """Validate spore integrity"""
        # Check content hash
        content_str = json.dumps(self.content, sort_keys=True)
        calculated_hash = hashlib.sha256(content_str.encode()).hexdigest()

        if calculated_hash != self.content_hash:
            return False

        # Check validation checksum if present
        if self.validation_checksum:
            # Additional validation logic here
            pass

        return True


class GlacierSporeDatabase:
    """Database for storing glacier spores and dimensions"""

    def __init__(self, db_path: str = "glacier_spores.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Dimensions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dimensions (
                    dimension_id TEXT PRIMARY KEY,
                    dimension_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    cardinality INTEGER,
                    range_min TEXT,
                    range_max TEXT,
                    unit TEXT,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    parent_dimension_id TEXT,
                    child_dimension_ids TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TEXT,
                    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Spores table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS spores (
                    spore_id TEXT PRIMARY KEY,
                    spore_type TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    embedded_schema TEXT NOT NULL,
                    content_schema TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    dimensions TEXT NOT NULL,
                    dimension_refs TEXT NOT NULL,
                    processing_triggers TEXT NOT NULL,
                    processor_requirements TEXT NOT NULL,
                    parent_spore_id TEXT,
                    child_spore_ids TEXT NOT NULL,
                    related_spore_ids TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_processed TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    processing_errors TEXT NOT NULL,
                    processing_history TEXT NOT NULL,
                    validation_checksum TEXT,
                    signature TEXT,
                    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Dimension usage tracking
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dimension_usage (
                    usage_id TEXT PRIMARY KEY,
                    dimension_id TEXT NOT NULL,
                    spore_id TEXT NOT NULL,
                    usage_type TEXT NOT NULL,
                    usage_timestamp TEXT NOT NULL,
                    usage_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dimension_id) REFERENCES dimensions (dimension_id),
                    FOREIGN KEY (spore_id) REFERENCES spores (spore_id)
                )
            """
            )

            # Processing triggers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_triggers (
                    trigger_id TEXT PRIMARY KEY,
                    trigger_type TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    processor_function TEXT NOT NULL,
                    processor_config TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spores_type ON spores (spore_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spores_processed ON spores (processed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spores_created ON spores (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dimensions_type ON dimensions (dimension_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dimensions_name ON dimensions (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dimension_usage_dim ON dimension_usage (dimension_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dimension_usage_spore ON dimension_usage (spore_id)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def store_dimension(self, dimension: Dimension) -> bool:
        """Store a dimension"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO dimensions (
                            dimension_id, dimension_type, name, description,
                            cardinality, range_min, range_max, unit,
                            created_at, last_updated, tags,
                            parent_dimension_id, child_dimension_ids,
                            usage_count, last_used
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            dimension.dimension_id,
                            dimension.dimension_type.value,
                            dimension.name,
                            dimension.description,
                            dimension.cardinality,
                            str(dimension.range_min) if dimension.range_min else None,
                            str(dimension.range_min) if dimension.range_max else None,
                            dimension.unit,
                            dimension.created_at.isoformat(),
                            dimension.last_updated.isoformat(),
                            json.dumps(list(dimension.tags)),
                            dimension.parent_dimension_id,
                            json.dumps(dimension.child_dimension_ids),
                            dimension.usage_count,
                            (dimension.last_used.isoformat() if dimension.last_used else None),
                        ),
                    )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store dimension {dimension.dimension_id}: {e}")
            return False

    def store_spore(self, spore: GlacierSpore) -> bool:
        """Store a glacier spore"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO spores (
                            spore_id, spore_type, content_hash, embedded_schema,
                            content_schema, content, metadata, dimensions,
                            dimension_refs, processing_triggers, processor_requirements,
                            parent_spore_id, child_spore_ids, related_spore_ids,
                            created_at, expires_at, last_processed, processed,
                            processing_errors, processing_history, validation_checksum, signature
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            spore.spore_id,
                            spore.spore_type.value,
                            spore.content_hash,
                            json.dumps(spore.embedded_schema),
                            json.dumps(spore.content_schema),
                            json.dumps(spore.content),
                            json.dumps(spore.metadata),
                            json.dumps(spore.dimensions),
                            json.dumps(spore.dimension_refs),
                            json.dumps(spore.processing_triggers),
                            json.dumps(spore.processor_requirements),
                            spore.parent_spore_id,
                            json.dumps(spore.child_spore_ids),
                            json.dumps(spore.related_spore_ids),
                            spore.created_at.isoformat(),
                            spore.expires_at.isoformat() if spore.expires_at else None,
                            (spore.last_processed.isoformat() if spore.last_processed else None),
                            spore.processed,
                            json.dumps(spore.processing_errors),
                            json.dumps(spore.processing_history),
                            spore.validation_checksum,
                            spore.signature,
                        ),
                    )

                    # Track dimension usage
                    self._track_dimension_usage(spore, conn)

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store spore {spore.spore_id}: {e}")
            return False

    def _track_dimension_usage(self, spore: GlacierSpore, conn):
        """Track dimension usage for a spore"""
        cursor = conn.cursor()

        for dimension_name, dimension_value in spore.dimensions.items():
            # Find dimension ID by name
            cursor.execute("SELECT dimension_id FROM dimensions WHERE name = ?", (dimension_name,))
            row = cursor.fetchone()

            if row:
                dimension_id = row["dimension_id"]

                # Record usage
                usage_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO dimension_usage (
                        usage_id, dimension_id, spore_id, usage_type,
                        usage_timestamp, usage_context
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        usage_id,
                        dimension_id,
                        spore.spore_id,
                        "value_set",
                        spore.created_at.isoformat(),
                        json.dumps({"spore_type": spore.spore_type.value}),
                    ),
                )

                # Update dimension usage count
                cursor.execute(
                    """
                    UPDATE dimensions SET
                        usage_count = usage_count + 1,
                        last_used = ?,
                        updated_at_db = CURRENT_TIMESTAMP
                    WHERE dimension_id = ?
                """,
                    (spore.created_at.isoformat(), dimension_id),
                )

    def get_dimension(self, dimension_id: str) -> Optional[Dimension]:
        """Get a dimension by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM dimensions WHERE dimension_id = ?", (dimension_id,))
                row = cursor.fetchone()

                if row:
                    return self._row_to_dimension(row)
                return None

        except Exception as e:
            logging.error(f"Failed to get dimension {dimension_id}: {e}")
            return None

    def get_spore(self, spore_id: str) -> Optional[GlacierSpore]:
        """Get a spore by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM spores WHERE spore_id = ?", (spore_id,))
                row = cursor.fetchone()

                if row:
                    return self._row_to_spore(row)
                return None

        except Exception as e:
            logging.error(f"Failed to get spore {spore_id}: {e}")
            return None

    def _row_to_dimension(self, row) -> Dimension:
        """Convert database row to Dimension object"""
        return Dimension(
            dimension_id=row["dimension_id"],
            dimension_type=DimensionType(row["dimension_type"]),
            name=row["name"],
            description=row["description"],
            cardinality=row["cardinality"],
            range_min=row["range_min"],
            range_max=row["range_max"],
            unit=row["unit"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_updated=datetime.fromisoformat(row["last_updated"]),
            tags=set(json.loads(row["tags"])),
            parent_dimension_id=row["parent_dimension_id"],
            child_dimension_ids=json.loads(row["child_dimension_ids"]),
            usage_count=row["usage_count"],
            last_used=(datetime.fromisoformat(row["last_used"]) if row["last_used"] else None),
        )

    def _row_to_spore(self, row) -> GlacierSpore:
        """Convert database row to GlacierSpore object"""
        return GlacierSpore(
            spore_id=row["spore_id"],
            spore_type=SporeType(row["spore_type"]),
            content_hash=row["content_hash"],
            embedded_schema=json.loads(row["embedded_schema"]),
            content_schema=json.loads(row["content_schema"]),
            content=json.loads(row["content"]),
            metadata=json.loads(row["metadata"]),
            dimensions=json.loads(row["dimensions"]),
            dimension_refs=json.loads(row["dimension_refs"]),
            processing_triggers=json.loads(row["processing_triggers"]),
            processor_requirements=json.loads(row["processor_requirements"]),
            parent_spore_id=row["parent_spore_id"],
            child_spore_ids=json.loads(row["child_spore_ids"]),
            related_spore_ids=json.loads(row["related_spore_ids"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=(datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None),
            last_processed=(datetime.fromisoformat(row["last_processed"]) if row["last_processed"] else None),
            processed=bool(row["processed"]),
            processing_errors=json.loads(row["processing_errors"]),
            processing_history=json.loads(row["processing_history"]),
            validation_checksum=row["validation_checksum"],
            signature=row["signature"],
        )

    def query_dimensions(
        self,
        dimension_type: Optional[DimensionType] = None,
        tags: Optional[set[str]] = None,
        min_usage: Optional[int] = None,
    ) -> list[Dimension]:
        """Query dimensions with filters"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM dimensions WHERE 1=1"
                params = []

                if dimension_type:
                    query += " AND dimension_type = ?"
                    params.append(dimension_type.value)

                if tags:
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    query += f" AND ({' OR '.join(tag_conditions)})"

                if min_usage is not None:
                    query += " AND usage_count >= ?"
                    params.append(min_usage)

                query += " ORDER BY usage_count DESC, last_used DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_dimension(row) for row in rows]

        except Exception as e:
            logging.error(f"Failed to query dimensions: {e}")
            return []

    def query_spores(
        self,
        spore_type: Optional[SporeType] = None,
        processed: Optional[bool] = None,
        dimensions: Optional[dict[str, Any]] = None,
    ) -> list[GlacierSpore]:
        """Query spores with filters"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM spores WHERE 1=1"
                params = []

                if spore_type:
                    query += " AND spore_type = ?"
                    params.append(spore_type.value)

                if processed is not None:
                    query += " AND processed = ?"
                    params.append(processed)

                if dimensions:
                    # Simple dimension filtering - could be enhanced
                    for dim_name, dim_value in dimensions.items():
                        query += " AND dimensions LIKE ?"
                        params.append(f"%{dim_name}%")

                query += " ORDER BY created_at DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_spore(row) for row in rows]

        except Exception as e:
            logging.error(f"Failed to query spores: {e}")
            return []


class DimensionAnalyzer:
    """Analyzes dimensions across the glacier spore system"""

    def __init__(self, database: GlacierSporeDatabase):
        self.database = database

    def count_dimensions(self) -> dict[str, Any]:
        """Count all dimensions in the system"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                # Total dimensions
                cursor.execute("SELECT COUNT(*) as total FROM dimensions")
                total_dimensions = cursor.fetchone()["total"]

                # Dimensions by type
                cursor.execute(
                    """
                    SELECT dimension_type, COUNT(*) as count
                    FROM dimensions
                    GROUP BY dimension_type
                """
                )
                dimensions_by_type = {row["dimension_type"]: row["count"] for row in cursor.fetchall()}

                # Usage statistics
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_used,
                        AVG(usage_count) as avg_usage,
                        MAX(usage_count) as max_usage,
                        MIN(usage_count) as min_usage
                    FROM dimensions
                    WHERE usage_count > 0
                """
                )
                usage_stats = cursor.fetchone()

                # Recent activity
                cursor.execute(
                    """
                    SELECT COUNT(*) as recent_activity
                    FROM dimensions
                    WHERE last_used > datetime('now', '-7 days')
                """
                )
                recent_activity = cursor.fetchone()["recent_activity"]

                return {
                    "total_dimensions": total_dimensions,
                    "dimensions_by_type": dimensions_by_type,
                    "usage_statistics": {
                        "total_used": usage_stats["total_used"],
                        "average_usage": usage_stats["avg_usage"],
                        "max_usage": usage_stats["max_usage"],
                        "min_usage": usage_stats["min_usage"],
                    },
                    "recent_activity": recent_activity,
                }

        except Exception as e:
            logging.error(f"Failed to count dimensions: {e}")
            return {}

    def find_orphaned_dimensions(self, min_age_days: int = 30) -> list[Dimension]:
        """Find dimensions that haven't been used recently"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                # Find dimensions not used in the specified period
                cursor.execute(
                    f"""
                    SELECT d.*
                    FROM dimensions d
                    WHERE (d.last_used IS NULL OR d.last_used < datetime('now', '-{min_age_days} days'))
                    AND d.usage_count > 0
                    ORDER BY d.last_used ASC NULLS FIRST, d.usage_count DESC
                """
                )

                rows = cursor.fetchall()
                return [self.database._row_to_dimension(row) for row in rows]

        except Exception as e:
            logging.error(f"Failed to find orphaned dimensions: {e}")
            return []

    def analyze_dimension_relationships(self) -> dict[str, Any]:
        """Analyze relationships between dimensions"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                # Parent-child relationships
                cursor.execute(
                    """
                    SELECT
                        parent_dimension_id,
                        COUNT(*) as child_count
                    FROM dimensions
                    WHERE parent_dimension_id IS NOT NULL
                    GROUP BY parent_dimension_id
                """
                )
                parent_child_stats = {row["parent_dimension_id"]: row["child_count"] for row in cursor.fetchall()}

                # Orphaned dimensions (no parent)
                cursor.execute(
                    """
                    SELECT COUNT(*) as orphaned_count
                    FROM dimensions
                    WHERE parent_dimension_id IS NULL
                """
                )
                orphaned_count = cursor.fetchone()["orphaned_count"]

                # Circular reference detection (simplified)
                cursor.execute(
                    """
                    SELECT COUNT(*) as potential_circular
                    FROM dimensions d1
                    JOIN dimensions d2 ON d1.dimension_id = d2.parent_dimension_id
                    WHERE d2.dimension_id = d1.parent_dimension_id
                """
                )
                potential_circular = cursor.fetchone()["potential_circular"]

                return {
                    "parent_child_relationships": parent_child_stats,
                    "orphaned_dimensions": orphaned_count,
                    "potential_circular_references": potential_circular,
                }

        except Exception as e:
            logging.error(f"Failed to analyze dimension relationships: {e}")
            return {}

    def get_dimension_usage_timeline(self, dimension_id: str, days: int = 30) -> list[dict[str, Any]]:
        """Get usage timeline for a specific dimension"""
        try:
            with self.database._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"""
                    SELECT
                        DATE(usage_timestamp) as date,
                        COUNT(*) as usage_count,
                        GROUP_CONCAT(DISTINCT usage_type) as usage_types
                    FROM dimension_usage
                    WHERE dimension_id = ?
                    AND usage_timestamp > datetime('now', '-{days} days')
                    GROUP BY DATE(usage_timestamp)
                    ORDER BY date DESC
                """,
                    (dimension_id,),
                )

                rows = cursor.fetchall()
                return [
                    {
                        "date": row["date"],
                        "usage_count": row["usage_count"],
                        "usage_types": (row["usage_types"].split(",") if row["usage_types"] else []),
                    }
                    for row in rows
                ]

        except Exception as e:
            logging.error(f"Failed to get dimension usage timeline: {e}")
            return []


class GlacierSporeSystem:
    """Main system for managing glacier spores"""

    def __init__(self, db_path: str = "glacier_spores.db"):
        self.database = GlacierSporeDatabase(db_path)
        self.dimension_analyzer = DimensionAnalyzer(self.database)

        # Initialize default dimensions
        self._initialize_default_dimensions()

    def _initialize_default_dimensions(self):
        """Initialize default dimensions in the system"""
        default_dimensions = [
            Dimension(
                dimension_id="time_created",
                dimension_type=DimensionType.TEMPORAL,
                name="Time Created",
                description="When the spore was created",
                unit="ISO timestamp",
                tags={"temporal", "creation", "metadata"},
            ),
            Dimension(
                dimension_id="spore_type",
                dimension_type=DimensionType.STRUCTURAL,
                name="Spore Type",
                description="Type of the glacier spore",
                tags={"structural", "classification", "metadata"},
            ),
            Dimension(
                dimension_id="content_size",
                dimension_type=DimensionType.STRUCTURAL,
                name="Content Size",
                description="Size of the spore content",
                unit="bytes",
                tags={"structural", "size", "metadata"},
            ),
            Dimension(
                dimension_id="processing_status",
                dimension_type=DimensionType.STRUCTURAL,
                name="Processing Status",
                description="Current processing status of the spore",
                tags={"structural", "status", "processing"},
            ),
            Dimension(
                dimension_id="quality_score",
                dimension_type=DimensionType.QUALITY,
                name="Quality Score",
                description="Quality assessment score",
                range_min=0.0,
                range_max=100.0,
                unit="percentage",
                tags={"quality", "assessment", "metrics"},
            ),
        ]

        for dimension in default_dimensions:
            self.database.store_dimension(dimension)

    def create_discovery_spore(self, repo_url: str, analysis_data: dict[str, Any]) -> GlacierSpore:
        """Create a discovery spore from repository analysis"""

        # Generate content hash
        content_str = json.dumps(analysis_data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()

        # Create embedded schema
        embedded_schema = {
            "type": "discovery_spore",
            "version": "1.0.0",
            "properties": {
                "repo_url": {"type": "string", "format": "uri"},
                "repo_name": {"type": "string"},
                "language": {"type": "string"},
                "total_files": {"type": "integer"},
                "quality_score": {"type": "number", "minimum": 0, "maximum": 100},
            },
            "required": ["repo_url", "repo_name", "total_files"],
        }

        # Create content schema
        content_schema = {
            "type": "object",
            "properties": {
                "artifact_summary": {"type": "object"},
                "detected_schemas": {"type": "object"},
                "quality_issues": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}},
            },
        }

        # Create spore
        spore = GlacierSpore(
            spore_id=f"discovery_{content_hash[:16]}",
            spore_type=SporeType.DISCOVERY,
            content_hash=content_hash,
            embedded_schema=embedded_schema,
            content_schema=content_schema,
            content=analysis_data,
            metadata={
                "source": "github_discovery",
                "analysis_tool": "comprehensive_github_discovery",
                "analysis_version": "1.0.0",
            },
            dimensions={
                "time_created": datetime.now(timezone.utc).isoformat(),
                "spore_type": "discovery",
                "content_size": len(content_str.encode()),
                "processing_status": "pending",
                "quality_score": analysis_data.get("quality_score", 0.0),
            },
            processing_triggers=[
                "quality_analysis",
                "security_scan",
                "dependency_analysis",
            ],
        )

        # Store spore
        self.database.store_spore(spore)

        return spore

    def get_dimension_analysis(self) -> dict[str, Any]:
        """Get comprehensive dimension analysis"""
        return {
            "dimension_count": self.dimension_analyzer.count_dimensions(),
            "orphaned_dimensions": len(self.dimension_analyzer.find_orphaned_dimensions()),
            "relationships": self.dimension_analyzer.analyze_dimension_relationships(),
        }

    def find_orphaned_dimensions(self, min_age_days: int = 30) -> list[Dimension]:
        """Find orphaned dimensions"""
        return self.dimension_analyzer.find_orphaned_dimensions(min_age_days)

    def get_dimension_usage_timeline(self, dimension_id: str, days: int = 30) -> list[dict[str, Any]]:
        """Get usage timeline for a dimension"""
        return self.dimension_analyzer.get_dimension_usage_timeline(dimension_id, days)


# Example usage
async def main():
    """Example usage of the glacier spore system"""

    # Create system
    system = GlacierSporeSystem()

    # Create a sample discovery spore
    sample_analysis = {
        "repo_name": "test-repo",
        "language": "Python",
        "total_files": 150,
        "quality_score": 85.0,
        "artifact_summary": {
            "python": {"count": 50, "total_size": 102400},
            "markdown": {"count": 10, "total_size": 25600},
        },
        "detected_schemas": {
            "dependencies": {"type": "python", "files": ["requirements.txt"]},
            "testing": {"type": "pytest", "files": ["test_*.py"]},
        },
        "quality_issues": ["Missing CI/CD"],
        "recommendations": ["Add GitHub Actions workflow"],
    }

    spore = system.create_discovery_spore("https://github.com/test/repo", sample_analysis)
    print(f"Created discovery spore: {spore.spore_id}")

    # Analyze dimensions
    analysis = system.get_dimension_analysis()
    print(f"\nDimension Analysis:")
    print(f"  Total dimensions: {analysis['dimension_count']['total_dimensions']}")
    print(f"  Orphaned dimensions: {analysis['orphaned_dimensions']}")

    # Find orphaned dimensions
    orphaned = system.find_orphaned_dimensions(min_age_days=1)
    print(f"\nOrphaned dimensions (unused in 1 day): {len(orphaned)}")
    for dim in orphaned[:3]:  # Show first 3
        print(f"  - {dim.name} (last used: {dim.last_used})")

    print(f"\n✅ Glacier spore system demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
