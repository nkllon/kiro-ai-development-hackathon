#!/usr/bin/env python3
"""
Glacier Schema Discovery System

This system creates persistent, queryable schemas for each discovery
that can be post-processed via triggers for long-term analysis.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Optional


class SchemaType(Enum):
    """Types of schemas we can discover"""

    REPOSITORY = "repository"
    CODE_STRUCTURE = "code_structure"
    DEPENDENCIES = "dependencies"
    QUALITY_METRICS = "quality_metrics"
    SECURITY_PATTERNS = "security_patterns"
    PERFORMANCE_PATTERNS = "performance_patterns"
    ARCHITECTURE_PATTERNS = "architecture_patterns"
    TESTING_PATTERNS = "testing_patterns"
    DEPLOYMENT_PATTERNS = "deployment_patterns"
    DOCUMENTATION_PATTERNS = "documentation_patterns"


class TriggerType(Enum):
    """Types of triggers for post-processing"""

    IMMEDIATE = "immediate"  # Process immediately after discovery
    SCHEDULED = "scheduled"  # Process on schedule
    EVENT_DRIVEN = "event_driven"  # Process on specific events
    BATCH = "batch"  # Process in batches
    CONDITIONAL = "conditional"  # Process when conditions are met


@dataclass
class DiscoverySchema:
    """Base schema for any discovery"""

    # Core identification
    schema_id: str
    schema_type: SchemaType
    source_url: str
    discovery_timestamp: datetime

    # Content and metadata
    content_hash: str
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    # Processing state
    processed: bool = False
    processing_timestamp: Optional[datetime] = None
    processing_errors: list[str] = field(default_factory=list)

    # Relationships
    parent_schema_id: Optional[str] = None
    child_schema_ids: list[str] = field(default_factory=list)

    # Versioning
    version: int = 1
    previous_version_id: Optional[str] = None

    # Tags and classification
    tags: set[str] = field(default_factory=set)
    confidence_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["schema_type"] = self.schema_type.value
        data["tags"] = list(self.tags)
        data["discovery_timestamp"] = self.discovery_timestamp.isoformat()
        if self.processing_timestamp:
            data["processing_timestamp"] = self.processing_timestamp.isoformat()
        return data


@dataclass
class ProcessingTrigger:
    """Trigger for post-processing schemas"""

    trigger_id: str
    trigger_type: TriggerType
    schema_type: SchemaType
    conditions: dict[str, Any]

    # Processing configuration
    processor_function: str  # Name of function to call
    processor_config: dict[str, Any] = field(default_factory=dict)

    # Scheduling
    schedule_cron: Optional[str] = None  # Cron expression for scheduled triggers
    batch_size: Optional[int] = None  # For batch processing
    delay_seconds: Optional[int] = None  # For delayed processing

    # State
    active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data["trigger_type"] = self.trigger_type.value
        data["schema_type"] = self.schema_type.value
        if self.last_triggered:
            data["last_triggered"] = self.last_triggered.isoformat()
        return data


class GlacierSchemaDatabase:
    """SQLite database for storing glacier schemas"""

    def __init__(self, db_path: str = "glacier_schemas.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Schemas table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schemas (
                    schema_id TEXT PRIMARY KEY,
                    schema_type TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    discovery_timestamp TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    processing_timestamp TEXT,
                    processing_errors TEXT NOT NULL,
                    parent_schema_id TEXT,
                    child_schema_ids TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    previous_version_id TEXT,
                    tags TEXT NOT NULL,
                    confidence_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Triggers table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS triggers (
                    trigger_id TEXT PRIMARY KEY,
                    trigger_type TEXT NOT NULL,
                    schema_type TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    processor_function TEXT NOT NULL,
                    processor_config TEXT NOT NULL,
                    schedule_cron TEXT,
                    batch_size INTEGER,
                    delay_seconds INTEGER,
                    active BOOLEAN DEFAULT TRUE,
                    last_triggered TEXT,
                    trigger_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Processing queue table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_queue (
                    queue_id TEXT PRIMARY KEY,
                    schema_id TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    scheduled_time TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (schema_id) REFERENCES schemas (schema_id),
                    FOREIGN KEY (trigger_id) REFERENCES triggers (trigger_id)
                )
            """
            )

            # Processing history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS processing_history (
                    history_id TEXT PRIMARY KEY,
                    schema_id TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    processor_function TEXT NOT NULL,
                    processor_config TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    success BOOLEAN,
                    result TEXT,
                    errors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (schema_id) REFERENCES schemas (schema_id),
                    FOREIGN KEY (trigger_id) REFERENCES triggers (trigger_id)
                )
            """
            )

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_type ON schemas (schema_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_processed ON schemas (processed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_timestamp ON schemas (discovery_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_triggers_type ON triggers (trigger_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON processing_queue (status)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable row access by name
        try:
            yield conn
        finally:
            conn.close()

    def store_schema(self, schema: DiscoverySchema) -> bool:
        """Store a schema in the database"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Check if schema already exists
                    cursor.execute(
                        "SELECT schema_id FROM schemas WHERE schema_id = ?",
                        (schema.schema_id,),
                    )

                    if cursor.fetchone():
                        # Update existing schema
                        cursor.execute(
                            """
                            UPDATE schemas SET
                                content = ?,
                                metadata = ?,
                                processed = ?,
                                processing_timestamp = ?,
                                processing_errors = ?,
                                child_schema_ids = ?,
                                version = ?,
                                previous_version_id = ?,
                                tags = ?,
                                confidence_score = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE schema_id = ?
                        """,
                            (
                                json.dumps(schema.content),
                                json.dumps(schema.metadata),
                                schema.processed,
                                (schema.processing_timestamp.isoformat() if schema.processing_timestamp else None),
                                json.dumps(schema.processing_errors),
                                json.dumps(schema.child_schema_ids),
                                schema.version,
                                schema.previous_version_id,
                                json.dumps(list(schema.tags)),
                                schema.confidence_score,
                                schema.schema_id,
                            ),
                        )
                    else:
                        # Insert new schema
                        cursor.execute(
                            """
                            INSERT INTO schemas (
                                schema_id, schema_type, source_url, discovery_timestamp,
                                content_hash, content, metadata, processed, processing_timestamp,
                                processing_errors, parent_schema_id, child_schema_ids,
                                version, previous_version_id, tags, confidence_score
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                schema.schema_id,
                                schema.schema_type.value,
                                schema.source_url,
                                schema.discovery_timestamp.isoformat(),
                                schema.content_hash,
                                json.dumps(schema.content),
                                json.dumps(schema.metadata),
                                schema.processed,
                                (schema.processing_timestamp.isoformat() if schema.processing_timestamp else None),
                                json.dumps(schema.processing_errors),
                                schema.parent_schema_id,
                                json.dumps(schema.child_schema_ids),
                                schema.version,
                                schema.previous_version_id,
                                json.dumps(list(schema.tags)),
                                schema.confidence_score,
                            ),
                        )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store schema {schema.schema_id}: {e}")
            return False

    def get_schema(self, schema_id: str) -> Optional[DiscoverySchema]:
        """Retrieve a schema from the database"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM schemas WHERE schema_id = ?", (schema_id,))
                row = cursor.fetchone()

                if row:
                    return self._row_to_schema(row)
                return None

        except Exception as e:
            logging.error(f"Failed to retrieve schema {schema_id}: {e}")
            return None

    def _row_to_schema(self, row) -> DiscoverySchema:
        """Convert database row to DiscoverySchema object"""
        return DiscoverySchema(
            schema_id=row["schema_id"],
            schema_type=SchemaType(row["schema_type"]),
            source_url=row["source_url"],
            discovery_timestamp=datetime.fromisoformat(row["discovery_timestamp"]),
            content_hash=row["content_hash"],
            content=json.loads(row["content"]),
            metadata=json.loads(row["metadata"]),
            processed=bool(row["processed"]),
            processing_timestamp=(datetime.fromisoformat(row["processing_timestamp"]) if row["processing_timestamp"] else None),
            processing_errors=json.loads(row["processing_errors"]),
            parent_schema_id=row["parent_schema_id"],
            child_schema_ids=json.loads(row["child_schema_ids"]),
            version=row["version"],
            previous_version_id=row["previous_version_id"],
            tags=set(json.loads(row["tags"])),
            confidence_score=row["confidence_score"],
        )

    def query_schemas(
        self,
        schema_type: Optional[SchemaType] = None,
        processed: Optional[bool] = None,
        tags: Optional[set[str]] = None,
        limit: Optional[int] = None,
    ) -> list[DiscoverySchema]:
        """Query schemas with filters"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM schemas WHERE 1=1"
                params = []

                if schema_type:
                    query += " AND schema_type = ?"
                    params.append(schema_type.value)

                if processed is not None:
                    query += " AND processed = ?"
                    params.append(processed)

                if tags:
                    # Simple tag matching - could be enhanced with JSON functions
                    tag_conditions = []
                    for tag in tags:
                        tag_conditions.append("tags LIKE ?")
                        params.append(f"%{tag}%")
                    query += f" AND ({' OR '.join(tag_conditions)})"

                query += " ORDER BY discovery_timestamp DESC"

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_schema(row) for row in rows]

        except Exception as e:
            logging.error(f"Failed to query schemas: {e}")
            return []

    def store_trigger(self, trigger: ProcessingTrigger) -> bool:
        """Store a processing trigger"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO triggers (
                            trigger_id, trigger_type, schema_type, conditions,
                            processor_function, processor_config, schedule_cron,
                            batch_size, delay_seconds, active, last_triggered, trigger_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            trigger.trigger_id,
                            trigger.trigger_type.value,
                            trigger.schema_type.value,
                            json.dumps(trigger.conditions),
                            trigger.processor_function,
                            json.dumps(trigger.processor_config),
                            trigger.schedule_cron,
                            trigger.batch_size,
                            trigger.delay_seconds,
                            trigger.active,
                            (trigger.last_triggered.isoformat() if trigger.last_triggered else None),
                            trigger.trigger_count,
                        ),
                    )

                    conn.commit()
                    return True

        except Exception as e:
            logging.error(f"Failed to store trigger {trigger.trigger_id}: {e}")
            return False

    def get_triggers(self, schema_type: Optional[SchemaType] = None, active_only: bool = True) -> list[ProcessingTrigger]:
        """Get processing triggers"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM triggers WHERE 1=1"
                params = []

                if schema_type:
                    query += " AND schema_type = ?"
                    params.append(schema_type.value)

                if active_only:
                    query += " AND active = TRUE"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                triggers = []
                for row in rows:
                    trigger = ProcessingTrigger(
                        trigger_id=row["trigger_id"],
                        trigger_type=TriggerType(row["trigger_type"]),
                        schema_type=SchemaType(row["schema_type"]),
                        conditions=json.loads(row["conditions"]),
                        processor_function=row["processor_function"],
                        processor_config=json.loads(row["processor_config"]),
                        schedule_cron=row["schedule_cron"],
                        batch_size=row["batch_size"],
                        delay_seconds=row["delay_seconds"],
                        active=bool(row["active"]),
                        last_triggered=(datetime.fromisoformat(row["last_triggered"]) if row["last_triggered"] else None),
                        trigger_count=row["trigger_count"],
                    )
                    triggers.append(trigger)

                return triggers

        except Exception as e:
            logging.error(f"Failed to get triggers: {e}")
            return []


class GlacierSchemaProcessor:
    """Processor for post-processing glacier schemas"""

    def __init__(self, database: GlacierSchemaDatabase):
        self.database = database
        self.processors: dict[str, Callable] = {}
        self.processing_queue: Queue = Queue()
        self.running = False
        self.worker_threads: list[threading.Thread] = []

        # Register default processors
        self._register_default_processors()

    def _register_default_processors(self):
        """Register default processing functions"""
        self.register_processor("analyze_code_complexity", self._analyze_code_complexity)
        self.register_processor("detect_security_patterns", self._detect_security_patterns)
        self.register_processor("analyze_dependencies", self._analyze_dependencies)
        self.register_processor("generate_quality_report", self._generate_quality_report)
        self.register_processor("extract_architecture_patterns", self._extract_architecture_patterns)

    def register_processor(self, name: str, processor_func: Callable):
        """Register a processing function"""
        self.processors[name] = processor_func
        logging.info(f"Registered processor: {name}")

    def start_processing(self, num_workers: int = 3):
        """Start the processing workers"""
        if self.running:
            return

        self.running = True

        # Start worker threads
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.worker_threads.append(worker)

        # Start trigger monitor
        trigger_monitor = threading.Thread(target=self._trigger_monitor_loop, daemon=True)
        trigger_monitor.start()

        logging.info(f"Started glacier schema processor with {num_workers} workers")

    def stop_processing(self):
        """Stop the processing workers"""
        self.running = False

        # Wait for workers to finish
        for worker in self.worker_threads:
            worker.join(timeout=5.0)

        logging.info("Stopped glacier schema processor")

    def _worker_loop(self, worker_id: int):
        """Main worker loop for processing schemas"""
        logging.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get item from queue with timeout
                try:
                    queue_item = self.processing_queue.get(timeout=1.0)
                except BaseException:
                    continue

                schema_id, trigger_id = queue_item

                # Process the schema
                self._process_schema(schema_id, trigger_id)

                # Mark task as done
                self.processing_queue.task_done()

            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")

        logging.info(f"Worker {worker_id} stopped")

    def _trigger_monitor_loop(self):
        """Monitor for triggers that need to be activated"""
        logging.info("Trigger monitor started")

        while self.running:
            try:
                # Check for immediate triggers
                self._check_immediate_triggers()

                # Check for scheduled triggers
                self._check_scheduled_triggers()

                # Check for conditional triggers
                self._check_conditional_triggers()

                # Sleep before next check
                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logging.error(f"Trigger monitor error: {e}")

        logging.info("Trigger monitor stopped")

    def _check_immediate_triggers(self):
        """Check for immediate triggers"""
        triggers = self.database.get_triggers(active_only=True)

        for trigger in triggers:
            if trigger.trigger_type == TriggerType.IMMEDIATE:
                # Find unprocessed schemas for this trigger
                schemas = self.database.query_schemas(schema_type=trigger.schema_type, processed=False)

                for schema in schemas:
                    self._queue_processing(schema.schema_id, trigger.trigger_id)

    def _check_scheduled_triggers(self):
        """Check for scheduled triggers"""
        # TODO: Implement cron-based scheduling

    def _check_conditional_triggers(self):
        """Check for conditional triggers"""
        triggers = self.database.get_triggers(active_only=True)

        for trigger in triggers:
            if trigger.trigger_type == TriggerType.CONDITIONAL:
                if self._evaluate_conditions(trigger.conditions):
                    # Find schemas that match conditions
                    schemas = self.database.query_schemas(schema_type=trigger.schema_type, processed=False)

                    for schema in schemas:
                        if self._schema_matches_conditions(schema, trigger.conditions):
                            self._queue_processing(schema.schema_id, trigger.trigger_id)

    def _evaluate_conditions(self, conditions: dict[str, Any]) -> bool:
        """Evaluate trigger conditions"""
        # Simple condition evaluation - could be enhanced
        return True  # Placeholder

    def _schema_matches_conditions(self, schema: DiscoverySchema, conditions: dict[str, Any]) -> bool:
        """Check if schema matches trigger conditions"""
        # Simple condition matching - could be enhanced
        return True  # Placeholder

    def _queue_processing(self, schema_id: str, trigger_id: str):
        """Queue a schema for processing"""
        self.processing_queue.put((schema_id, trigger_id))
        logging.info(f"Queued schema {schema_id} for processing with trigger {trigger_id}")

    def _process_schema(self, schema_id: str, trigger_id: str):
        """Process a schema with a specific trigger"""
        try:
            # Get schema and trigger
            schema = self.database.get_schema(schema_id)
            if not schema:
                logging.error(f"Schema {schema_id} not found")
                return

            # Get processor function
            trigger = next(
                (t for t in self.database.get_triggers() if t.trigger_id == trigger_id),
                None,
            )
            if not trigger:
                logging.error(f"Trigger {trigger_id} not found")
                return

            processor_func = self.processors.get(trigger.processor_function)
            if not processor_func:
                logging.error(f"Processor {trigger.processor_function} not found")
                return

            # Process the schema
            start_time = time.time()
            result = processor_func(schema, trigger.processor_config)
            end_time = time.time()

            # Update schema
            schema.processed = True
            schema.processing_timestamp = datetime.now(timezone.utc)
            if not result.get("success", False):
                schema.processing_errors.append(result.get("error", "Unknown error"))

            # Store updated schema
            self.database.store_schema(schema)

            # Log processing result
            logging.info(f"Processed schema {schema_id} with {trigger.processor_function} in {end_time - start_time:.2f}s")

        except Exception as e:
            logging.error(f"Failed to process schema {schema_id}: {e}")

    # Default processor implementations
    def _analyze_code_complexity(self, schema: DiscoverySchema, config: dict[str, Any]) -> dict[str, Any]:
        """Analyze code complexity from schema"""
        try:
            # Extract code-related information
            content = schema.content

            # Calculate complexity metrics
            complexity_score = 0.0
            metrics = {}

            if "functions" in content:
                metrics["function_count"] = len(content["functions"])
                complexity_score += min(metrics["function_count"] * 0.1, 10.0)

            if "classes" in content:
                metrics["class_count"] = len(content["classes"])
                complexity_score += min(metrics["class_count"] * 0.2, 10.0)

            if "lines_of_code" in content:
                metrics["lines_of_code"] = content["lines_of_code"]
                complexity_score += min(metrics["lines_of_code"] / 100, 20.0)

            # Normalize score
            complexity_score = min(100.0, complexity_score)

            return {
                "success": True,
                "complexity_score": complexity_score,
                "metrics": metrics,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _detect_security_patterns(self, schema: DiscoverySchema, config: dict[str, Any]) -> dict[str, Any]:
        """Detect security patterns from schema"""
        try:
            content = schema.content
            security_issues = []

            # Check for common security issues
            if "imports" in content:
                dangerous_imports = ["pickle", "eval", "exec", "subprocess"]
                for imp in content["imports"]:
                    if any(dangerous in imp.lower() for dangerous in dangerous_imports):
                        security_issues.append(f"Dangerous import: {imp}")

            if "functions" in content:
                dangerous_functions = ["eval", "exec", "os.system", "subprocess.call"]
                for func in content["functions"]:
                    if any(dangerous in func.lower() for dangerous in dangerous_functions):
                        security_issues.append(f"Dangerous function: {func}")

            return {
                "success": True,
                "security_issues": security_issues,
                "security_score": max(0, 100 - len(security_issues) * 10),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_dependencies(self, schema: DiscoverySchema, config: dict[str, Any]) -> dict[str, Any]:
        """Analyze dependencies from schema"""
        try:
            content = schema.content
            dependencies = []

            if "dependencies" in content:
                dependencies = content["dependencies"]

            return {
                "success": True,
                "dependency_count": len(dependencies),
                "dependencies": dependencies,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_quality_report(self, schema: DiscoverySchema, config: dict[str, Any]) -> dict[str, Any]:
        """Generate quality report from schema"""
        try:
            content = schema.content
            quality_score = 0.0
            issues = []

            # Check various quality aspects
            if "test_files" in content:
                quality_score += 20.0
            else:
                issues.append("No test files found")

            if "documentation" in content:
                quality_score += 15.0
            else:
                issues.append("No documentation found")

            if "ci_cd" in content:
                quality_score += 15.0
            else:
                issues.append("No CI/CD configuration")

            return {"success": True, "quality_score": quality_score, "issues": issues}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_architecture_patterns(self, schema: DiscoverySchema, config: dict[str, Any]) -> dict[str, Any]:
        """Extract architecture patterns from schema"""
        try:
            content = schema.content
            patterns = []

            # Detect common patterns
            if "layers" in content:
                patterns.append("Layered Architecture")

            if "microservices" in content:
                patterns.append("Microservices")

            if "monolith" in content:
                patterns.append("Monolithic")

            return {
                "success": True,
                "patterns": patterns,
                "pattern_count": len(patterns),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class GlacierSchemaDiscovery:
    """Main class for glacier schema discovery system"""

    def __init__(self, db_path: str = "glacier_schemas.db"):
        self.database = GlacierSchemaDatabase(db_path)
        self.processor = GlacierSchemaProcessor(self.database)

        # Start processing
        self.processor.start_processing()

    def create_repository_schema(self, repo_url: str, analysis_data: dict[str, Any]) -> DiscoverySchema:
        """Create a glacier schema for repository discovery"""

        # Generate schema ID
        content_str = json.dumps(analysis_data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        schema_id = f"repo_{content_hash[:16]}"

        # Create schema
        schema = DiscoverySchema(
            schema_id=schema_id,
            schema_type=SchemaType.REPOSITORY,
            source_url=repo_url,
            discovery_timestamp=datetime.now(timezone.utc),
            content_hash=content_hash,
            content=analysis_data,
            metadata={
                "analysis_tool": "comprehensive_github_discovery",
                "analysis_version": "1.0.0",
            },
            tags={"repository", "github", "discovery"},
            confidence_score=0.9,
        )

        # Store in database
        self.database.store_schema(schema)

        # Create child schemas for different aspects
        self._create_child_schemas(schema, analysis_data)

        return schema

    def _create_child_schemas(self, parent_schema: DiscoverySchema, analysis_data: dict[str, Any]):
        """Create child schemas for different aspects of the analysis"""

        # Code structure schema
        if "artifact_summary" in analysis_data:
            code_schema = DiscoverySchema(
                schema_id=f"{parent_schema.schema_id}_code",
                schema_type=SchemaType.CODE_STRUCTURE,
                source_url=parent_schema.source_url,
                discovery_timestamp=datetime.now(timezone.utc),
                content_hash=hashlib.sha256(json.dumps(analysis_data["artifact_summary"], sort_keys=True).encode()).hexdigest(),
                content=analysis_data["artifact_summary"],
                metadata={"parent_schema": parent_schema.schema_id},
                parent_schema_id=parent_schema.schema_id,
                tags={"code", "structure", "artifacts"},
                confidence_score=0.8,
            )
            self.database.store_schema(code_schema)
            parent_schema.child_schema_ids.append(code_schema.schema_id)

        # Dependencies schema
        if "detected_schemas" in analysis_data:
            deps_schema = DiscoverySchema(
                schema_id=f"{parent_schema.schema_id}_deps",
                schema_type=SchemaType.DEPENDENCIES,
                source_url=parent_schema.source_url,
                discovery_timestamp=datetime.now(timezone.utc),
                content_hash=hashlib.sha256(json.dumps(analysis_data["detected_schemas"], sort_keys=True).encode()).hexdigest(),
                content=analysis_data["detected_schemas"],
                metadata={"parent_schema": parent_schema.schema_id},
                parent_schema_id=parent_schema.schema_id,
                tags={"dependencies", "packages", "libraries"},
                confidence_score=0.8,
            )
            self.database.store_schema(deps_schema)
            parent_schema.child_schema_ids.append(deps_schema.schema_id)

        # Quality metrics schema
        quality_schema = DiscoverySchema(
            schema_id=f"{parent_schema.schema_id}_quality",
            schema_type=SchemaType.QUALITY_METRICS,
            source_url=parent_schema.source_url,
            discovery_timestamp=datetime.now(timezone.utc),
            content_hash=hashlib.sha256(
                json.dumps(
                    {
                        "quality_score": analysis_data.get("quality_score", 0),
                        "quality_issues": analysis_data.get("quality_issues", []),
                        "recommendations": analysis_data.get("recommendations", []),
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            content={
                "quality_score": analysis_data.get("quality_score", 0),
                "quality_issues": analysis_data.get("quality_issues", []),
                "recommendations": analysis_data.get("recommendations", []),
            },
            metadata={"parent_schema": parent_schema.schema_id},
            parent_schema_id=parent_schema.schema_id,
            tags={"quality", "metrics", "analysis"},
            confidence_score=0.9,
        )
        self.database.store_schema(quality_schema)
        parent_schema.child_schema_ids.append(quality_schema.schema_id)

        # Update parent schema
        self.database.store_schema(parent_schema)

    def add_processing_trigger(self, trigger: ProcessingTrigger):
        """Add a processing trigger"""
        self.database.store_trigger(trigger)
        logging.info(f"Added processing trigger: {trigger.trigger_id}")

    def query_schemas(self, **kwargs) -> list[DiscoverySchema]:
        """Query schemas with filters"""
        return self.database.query_schemas(**kwargs)

    def get_schema(self, schema_id: str) -> Optional[DiscoverySchema]:
        """Get a specific schema"""
        return self.database.get_schema(schema_id)

    def shutdown(self):
        """Shutdown the discovery system"""
        self.processor.stop_processing()
        logging.info("Glacier schema discovery system shutdown")


# Example usage and testing
async def main():
    """Example usage of the glacier schema discovery system"""

    # Create discovery system
    discovery = GlacierSchemaDiscovery()

    # Add some processing triggers
    immediate_trigger = ProcessingTrigger(
        trigger_id="immediate_quality_analysis",
        trigger_type=TriggerType.IMMEDIATE,
        schema_type=SchemaType.REPOSITORY,
        conditions={},
        processor_function="generate_quality_report",
        processor_config={},
    )
    discovery.add_processing_trigger(immediate_trigger)

    security_trigger = ProcessingTrigger(
        trigger_id="security_analysis",
        trigger_type=TriggerType.IMMEDIATE,
        schema_type=SchemaType.CODE_STRUCTURE,
        conditions={},
        processor_function="detect_security_patterns",
        processor_config={},
    )
    discovery.add_processing_trigger(security_trigger)

    # Example: Create a schema from analysis data
    sample_analysis = {
        "repo_name": "test-repo",
        "language": "Python",
        "total_files": 150,
        "artifact_summary": {
            "python": {"count": 50, "total_size": 102400},
            "markdown": {"count": 10, "total_size": 25600},
        },
        "detected_schemas": {
            "dependencies": {"type": "python", "files": ["requirements.txt"]},
            "testing": {"type": "pytest", "files": ["test_*.py"]},
        },
        "quality_score": 85.0,
        "quality_issues": ["Missing CI/CD"],
        "recommendations": ["Add GitHub Actions workflow"],
    }

    schema = discovery.create_repository_schema("https://github.com/test/repo", sample_analysis)
    print(f"Created schema: {schema.schema_id}")

    # Wait for processing
    await asyncio.sleep(5)

    # Query processed schemas
    processed_schemas = discovery.query_schemas(processed=True)
    print(f"Processed schemas: {len(processed_schemas)}")

    # Shutdown
    discovery.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
