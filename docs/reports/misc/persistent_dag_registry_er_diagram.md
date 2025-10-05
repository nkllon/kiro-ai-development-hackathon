# Persistent DAG Registry - Entity Relationship Diagram

## Mermaid ER Diagram

```mermaid
erDiagram
    REGISTRY_METADATA {
        int id PK
        string registry_id UK
        string created_at
        string last_updated
        int total_modules
        boolean is_dag
    }
    
    MODULES {
        string module_id PK
        string class_name
        string file_path
        int line_number
        string version
        string capabilities
        string health_status
        string registered_at
        string last_updated
    }
    
    DEPENDENCIES {
        int id PK
        string module_id FK
        string dependency_id FK
        string created_at
    }
    
    DEPENDENTS {
        int id PK
        string module_id FK
        string dependent_id FK
        string created_at
    }
    
    AUDIT_LOG {
        int id PK
        string action
        string module_id FK
        string details
        string timestamp
    }
    
    %% Relationships
    MODULES ||--o{ DEPENDENCIES : "has dependencies"
    MODULES ||--o{ DEPENDENCIES : "is dependency of"
    MODULES ||--o{ DEPENDENTS : "has dependents"
    MODULES ||--o{ DEPENDENTS : "is dependent of"
    MODULES ||--o{ AUDIT_LOG : "generates audit entries"
    
    %% Self-referencing relationships for DAG structure
    MODULES ||--o{ DEPENDENCIES : "module_id references module_id"
    MODULES ||--o{ DEPENDENCIES : "dependency_id references module_id"
    MODULES ||--o{ DEPENDENTS : "module_id references module_id"
    MODULES ||--o{ DEPENDENTS : "dependent_id references module_id"
```

## Database Schema Details

### REGISTRY_METADATA
- **Primary Key**: `id` (auto-increment)
- **Unique Key**: `registry_id` (registry identifier)
- **Purpose**: Tracks overall registry state and statistics
- **Constraints**: Single row per registry instance

### MODULES
- **Primary Key**: `module_id` (module identifier)
- **Purpose**: Stores module metadata and information
- **Foreign Key**: Self-referencing through dependencies/dependents
- **JSON Fields**: `capabilities` (array of capability strings)

### DEPENDENCIES
- **Primary Key**: `id` (auto-increment)
- **Foreign Keys**: 
  - `module_id` → `MODULES.module_id` (CASCADE DELETE)
  - `dependency_id` → `MODULES.module_id` (CASCADE DELETE)
- **Unique Constraint**: `(module_id, dependency_id)` prevents duplicates
- **Purpose**: Tracks what each module depends on

### DEPENDENTS
- **Primary Key**: `id` (auto-increment)
- **Foreign Keys**:
  - `module_id` → `MODULES.module_id` (CASCADE DELETE)
  - `dependent_id` → `MODULES.module_id` (CASCADE DELETE)
- **Unique Constraint**: `(module_id, dependent_id)` prevents duplicates
- **Purpose**: Reverse lookup for performance (what depends on each module)

### AUDIT_LOG
- **Primary Key**: `id` (auto-increment)
- **Foreign Key**: `module_id` → `MODULES.module_id` (SET NULL on delete)
- **JSON Fields**: `details` (action-specific metadata)
- **Purpose**: Complete audit trail of all registry operations

## Referential Integrity Features

1. **CASCADE DELETE**: Removing a module removes all its dependencies and dependents
2. **FOREIGN KEY CONSTRAINTS**: All references must point to existing modules
3. **UNIQUE CONSTRAINTS**: Prevent duplicate dependency relationships
4. **CHECK CONSTRAINTS**: Ensure data validity (version format, status values)
5. **INDEXES**: Optimized for common queries (dependency lookups, audit trails)

## DAG Enforcement

- **Cycle Detection**: DFS algorithm prevents circular dependencies
- **Bidirectional Tracking**: Both dependencies and dependents maintained
- **Transaction Safety**: All operations wrapped in transactions
- **Validation**: Continuous DAG validation with `validate_dag()` method
