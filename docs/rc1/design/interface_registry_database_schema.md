# Interface Registry Database Schema Design

## Overview

The Interface Registry requires a robust database schema with transaction support, synchronized logging, and comprehensive interface metadata storage. This design addresses the need for signature analysis, dependency tracking, and high-performance querying.

## Database Technology

**Primary Database**: SQLite with WAL mode for concurrent access
**Backup Database**: PostgreSQL for production scaling
**Cache Layer**: Redis for high-frequency queries
**Logging**: Structured JSON logs with transaction correlation

## Core Schema

### 1. Interfaces Table

```sql
CREATE TABLE interfaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    interface_type TEXT NOT NULL CHECK (interface_type IN ('class', 'function', 'enum', 'module', 'interface', 'dataclass', 'exception')),
    module_path TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'unknown' CHECK (status IN ('active', 'deprecated', 'experimental', 'stable', 'unknown')),
    description TEXT,
    docstring TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed_at TIMESTAMP,
    rdi_compliant BOOLEAN DEFAULT FALSE,
    health_score REAL DEFAULT 1.0,
    
    -- Indexes
    INDEX idx_interface_type (interface_type),
    INDEX idx_module_path (module_path),
    INDEX idx_status (status),
    INDEX idx_rdi_compliant (rdi_compliant),
    INDEX idx_created_at (created_at)
);
```

### 2. Method Signatures Table

```sql
CREATE TABLE method_signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id TEXT NOT NULL,
    method_name TEXT NOT NULL,
    signature TEXT NOT NULL,
    return_type TEXT,
    is_abstract BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    is_static BOOLEAN DEFAULT FALSE,
    is_classmethod BOOLEAN DEFAULT FALSE,
    docstring TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE,
    UNIQUE(interface_id, method_name),
    INDEX idx_interface_id (interface_id),
    INDEX idx_method_name (method_name),
    INDEX idx_return_type (return_type)
);
```

### 3. Method Parameters Table

```sql
CREATE TABLE method_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_signature_id INTEGER NOT NULL,
    parameter_name TEXT NOT NULL,
    parameter_type TEXT,
    default_value TEXT,
    is_required BOOLEAN DEFAULT TRUE,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (method_signature_id) REFERENCES method_signatures(id) ON DELETE CASCADE,
    UNIQUE(method_signature_id, parameter_name),
    INDEX idx_method_signature_id (method_signature_id),
    INDEX idx_parameter_type (parameter_type)
);
```

### 4. Dependencies Table

```sql
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL CHECK (dependency_type IN ('import', 'type', 'inheritance', 'composition', 'usage')),
    dependency_name TEXT NOT NULL,
    dependency_module TEXT,
    dependency_path TEXT,
    is_external BOOLEAN DEFAULT FALSE,
    is_circular BOOLEAN DEFAULT FALSE,
    strength REAL DEFAULT 1.0, -- 0.0 to 1.0, how strong the dependency is
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE,
    INDEX idx_interface_id (interface_id),
    INDEX idx_dependency_type (dependency_type),
    INDEX idx_dependency_name (dependency_name),
    INDEX idx_is_circular (is_circular)
);
```

### 5. Capabilities Table

```sql
CREATE TABLE capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id TEXT NOT NULL,
    capability TEXT NOT NULL CHECK (capability IN ('core_functionality', 'data_processing', 'api_integration', 'file_operations', 'validation', 'monitoring', 'sca_analysis', 'compliance_checking', 'random_attack', 'efficiency_analysis', 'beast_mode')),
    confidence REAL DEFAULT 1.0, -- 0.0 to 1.0, confidence in capability detection
    detected_by TEXT, -- method used to detect capability
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE,
    UNIQUE(interface_id, capability),
    INDEX idx_interface_id (interface_id),
    INDEX idx_capability (capability)
);
```

### 6. Tags Table

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    tag_type TEXT DEFAULT 'user' CHECK (tag_type IN ('user', 'auto', 'system', 'domain')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE,
    UNIQUE(interface_id, tag),
    INDEX idx_interface_id (interface_id),
    INDEX idx_tag (tag),
    INDEX idx_tag_type (tag_type)
);
```

### 7. Transactions Table

```sql
CREATE TABLE transactions (
    id TEXT PRIMARY KEY, -- UUID
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('register', 'update', 'delete', 'analyze', 'discover')),
    interface_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed', 'rolled_back')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSON, -- Additional transaction context
    created_by TEXT DEFAULT 'system',
    
    INDEX idx_status (status),
    INDEX idx_transaction_type (transaction_type),
    INDEX idx_started_at (started_at),
    INDEX idx_interface_id (interface_id)
);
```

### 8. Audit Log Table

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT,
    interface_id TEXT,
    action TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    old_values JSON,
    new_values JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT DEFAULT 'system',
    
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_interface_id (interface_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp)
);
```

### 9. Health Metrics Table

```sql
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (interface_id) REFERENCES interfaces(id) ON DELETE CASCADE,
    INDEX idx_interface_id (interface_id),
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp)
);
```

## Transaction Management

### Transaction Lifecycle

1. **Begin Transaction**: Generate UUID, insert into transactions table
2. **Execute Operations**: All changes within transaction scope
3. **Audit Logging**: Every change logged to audit_log table
4. **Commit/Rollback**: Update transaction status, cleanup on failure

### Synchronized Logging

```python
class TransactionLogger:
    def __init__(self, db_connection):
        self.db = db_connection
        self.current_transaction = None
    
    def begin_transaction(self, transaction_type: str, interface_id: str = None) -> str:
        transaction_id = str(uuid.uuid4())
        self.current_transaction = transaction_id
        
        self.db.execute("""
            INSERT INTO transactions (id, transaction_type, interface_id, status)
            VALUES (?, ?, ?, 'in_progress')
        """, (transaction_id, transaction_type, interface_id))
        
        return transaction_id
    
    def log_change(self, action: str, table_name: str, record_id: str, 
                   old_values: dict = None, new_values: dict = None):
        if not self.current_transaction:
            raise RuntimeError("No active transaction")
        
        self.db.execute("""
            INSERT INTO audit_log (transaction_id, interface_id, action, table_name, record_id, old_values, new_values)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.current_transaction, None, action, table_name, record_id, 
              json.dumps(old_values) if old_values else None,
              json.dumps(new_values) if new_values else None))
    
    def commit_transaction(self):
        if self.current_transaction:
            self.db.execute("""
                UPDATE transactions SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (self.current_transaction,))
            self.current_transaction = None
    
    def rollback_transaction(self, error_message: str = None):
        if self.current_transaction:
            self.db.execute("""
                UPDATE transactions SET status = 'failed', completed_at = CURRENT_TIMESTAMP, error_message = ?
                WHERE id = ?
            """, (error_message, self.current_transaction))
            self.current_transaction = None
```

## Performance Optimizations

### Indexes
- Primary indexes on all foreign keys
- Composite indexes for common query patterns
- Partial indexes for filtered queries

### Caching Strategy
- Redis cache for frequently accessed interfaces
- Method signature cache for type analysis
- Dependency graph cache for relationship queries

### Query Optimization
- Prepared statements for common operations
- Batch operations for bulk updates
- Connection pooling for concurrent access

## Migration Strategy

### Version 1.0: Basic Schema
- Core tables (interfaces, method_signatures, dependencies)
- Basic transaction support
- Simple audit logging

### Version 2.0: Enhanced Analysis
- Method parameters table
- Capabilities detection
- Health metrics tracking

### Version 3.0: Advanced Features
- Circular dependency detection
- Performance analytics
- Machine learning integration

## Security Considerations

- Row-level security for multi-tenant scenarios
- Encrypted sensitive metadata
- Access control for audit logs
- SQL injection prevention
- Data retention policies

This schema provides a robust foundation for the interface registry with full transaction support, comprehensive logging, and scalable architecture.
