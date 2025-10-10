# Directus Interface Registry Schema Design

## Overview

This design shows how to model our interface registry using Directus, leveraging its built-in versioning, audit logging, and database-first approach.

## Database Schema (Directus Collections)

### 1. Interfaces Collection

```sql
-- Directus will auto-generate this from our existing database
CREATE TABLE interfaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    interface_type ENUM('class', 'function', 'enum', 'module', 'interface', 'dataclass', 'exception') NOT NULL,
    module_path VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    line_number INTEGER NOT NULL,
    version VARCHAR(50) DEFAULT '1.0.0',
    status ENUM('active', 'deprecated', 'experimental', 'stable', 'unknown') DEFAULT 'unknown',
    description TEXT,
    docstring TEXT,
    rdi_compliant BOOLEAN DEFAULT FALSE,
    health_score DECIMAL(3,2) DEFAULT 1.0,
    
    -- Directus built-in fields
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id),
    
    -- Indexes
    INDEX idx_interface_type (interface_type),
    INDEX idx_module_path (module_path),
    INDEX idx_status (status),
    INDEX idx_rdi_compliant (rdi_compliant)
);
```

### 2. Method Signatures Collection

```sql
CREATE TABLE method_signatures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interface_id UUID NOT NULL REFERENCES interfaces(id) ON DELETE CASCADE,
    method_name VARCHAR(255) NOT NULL,
    signature TEXT NOT NULL,
    return_type VARCHAR(255),
    is_abstract BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    is_static BOOLEAN DEFAULT FALSE,
    is_classmethod BOOLEAN DEFAULT FALSE,
    docstring TEXT,
    line_number INTEGER,
    
    -- Directus built-in fields
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id),
    
    UNIQUE(interface_id, method_name),
    INDEX idx_interface_id (interface_id),
    INDEX idx_method_name (method_name),
    INDEX idx_return_type (return_type)
);
```

### 3. Method Parameters Collection

```sql
CREATE TABLE method_parameters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    method_signature_id UUID NOT NULL REFERENCES method_signatures(id) ON DELETE CASCADE,
    parameter_name VARCHAR(255) NOT NULL,
    parameter_type VARCHAR(255),
    default_value TEXT,
    is_required BOOLEAN DEFAULT TRUE,
    position INTEGER NOT NULL,
    
    -- Directus built-in fields
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id),
    
    UNIQUE(method_signature_id, parameter_name),
    INDEX idx_method_signature_id (method_signature_id),
    INDEX idx_parameter_type (parameter_type)
);
```

### 4. Dependencies Collection

```sql
CREATE TABLE dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interface_id UUID NOT NULL REFERENCES interfaces(id) ON DELETE CASCADE,
    dependency_type ENUM('import', 'type', 'inheritance', 'composition', 'usage') NOT NULL,
    dependency_name VARCHAR(500) NOT NULL,
    dependency_module VARCHAR(500),
    dependency_path VARCHAR(1000),
    is_external BOOLEAN DEFAULT FALSE,
    is_circular BOOLEAN DEFAULT FALSE,
    strength DECIMAL(3,2) DEFAULT 1.0,
    
    -- Directus built-in fields
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id),
    
    INDEX idx_interface_id (interface_id),
    INDEX idx_dependency_type (dependency_type),
    INDEX idx_dependency_name (dependency_name),
    INDEX idx_is_circular (is_circular)
);
```

### 5. Capabilities Collection

```sql
CREATE TABLE capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interface_id UUID NOT NULL REFERENCES interfaces(id) ON DELETE CASCADE,
    capability ENUM('core_functionality', 'data_processing', 'api_integration', 'file_operations', 'validation', 'monitoring', 'sca_analysis', 'compliance_checking', 'random_attack', 'efficiency_analysis', 'beast_mode') NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    detected_by VARCHAR(255),
    
    -- Directus built-in fields
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id),
    
    UNIQUE(interface_id, capability),
    INDEX idx_interface_id (interface_id),
    INDEX idx_capability (capability)
);
```

## Directus Configuration

### Collection Settings

```yaml
# Directus Collections Configuration
collections:
  interfaces:
    display_template: "{{name}} ({{interface_type}})"
    sort_field: "name"
    archive_field: "status"
    archive_value: "archived"
    unarchive_value: "active"
    versioning: true  # Built-in versioning!
    audit_log: true   # Built-in audit logging!
    
  method_signatures:
    display_template: "{{method_name}}({{signature}})"
    sort_field: "method_name"
    versioning: true
    audit_log: true
    
  dependencies:
    display_template: "{{dependency_name}} ({{dependency_type}})"
    sort_field: "dependency_name"
    versioning: true
    audit_log: true
```

### Relationships

```yaml
# Directus Relationships
relationships:
  - collection: interfaces
    field: method_signatures
    related_collection: method_signatures
    type: one-to-many
    
  - collection: method_signatures
    field: parameters
    related_collection: method_parameters
    type: one-to-many
    
  - collection: interfaces
    field: dependencies
    related_collection: dependencies
    type: one-to-many
    
  - collection: interfaces
    field: capabilities
    related_collection: capabilities
    type: one-to-many
```

## Directus Features We Get for Free

### 1. Built-in Versioning
- **What it does**: Every change creates a new version
- **For Interface Registry**: Track interface changes over time
- **API**: `GET /interfaces/{id}/versions` - Get all versions
- **API**: `POST /interfaces/{id}/revert` - Revert to previous version

### 2. Built-in Audit Logging
- **What it does**: Logs every create, update, delete operation
- **For Interface Registry**: Complete change history
- **API**: `GET /interfaces/{id}/audit` - Get audit trail
- **API**: `GET /audit` - Get system-wide audit log

### 3. Auto-Generated APIs
- **REST API**: `GET /interfaces`, `POST /interfaces`, `PUT /interfaces/{id}`
- **GraphQL API**: Complex queries for interface relationships
- **WebSocket API**: Real-time updates when interfaces change

### 4. User Management & Permissions
- **Roles**: Admin, Developer, Viewer
- **Permissions**: Who can create/update/delete interfaces
- **API Keys**: For programmatic access

### 5. Backup & Migration
- **Export**: `GET /interfaces/export` - Export all interfaces
- **Import**: `POST /interfaces/import` - Import interfaces
- **Snapshots**: Database-level backups

## Interface Registry API Examples

### REST API Queries

```bash
# Get all interfaces
GET /interfaces

# Get interfaces by type
GET /interfaces?filter[interface_type][_eq]=class

# Get interfaces with dependencies
GET /interfaces?fields=*,dependencies.*

# Get method signatures for an interface
GET /interfaces/{id}?fields=*,method_signatures.*

# Search interfaces by name
GET /interfaces?filter[name][_contains]=ReflectiveModule
```

### GraphQL Queries

```graphql
# Get interface with full details
query GetInterface($id: ID!) {
  interfaces_by_id(id: $id) {
    id
    name
    interface_type
    method_signatures {
      method_name
      signature
      return_type
      parameters {
        parameter_name
        parameter_type
        is_required
      }
    }
    dependencies {
      dependency_name
      dependency_type
      is_circular
    }
    capabilities {
      capability
      confidence
    }
  }
}

# Search interfaces by capability
query SearchByCapability($capability: String!) {
  interfaces(filter: {capabilities: {capability: {_eq: $capability}}}) {
    id
    name
    interface_type
  }
}
```

### WebSocket Real-time Updates

```javascript
// Listen for interface changes
const ws = new WebSocket('ws://localhost:8055/websocket');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'interfaces' && data.action === 'create') {
    console.log('New interface registered:', data.data);
  }
};
```

## Migration from Current Registry

### 1. Export Current Data
```python
# Export from current registry
from src.rm_ddd.core.interface_registry import InterfaceRegistry
import json

registry = InterfaceRegistry('.')
interfaces = registry.get_all_interfaces()

# Convert to Directus format
directus_data = []
for interface in interfaces:
    directus_data.append({
        'name': interface.name,
        'interface_type': interface.interface_type.value,
        'module_path': interface.module_path,
        'file_path': interface.file_path,
        'line_number': interface.line_number,
        'version': interface.version,
        'status': interface.status.value,
        'description': interface.description,
        'rdi_compliant': interface.rdi_compliant,
        'health_score': interface.health_score
    })

# Export to JSON
with open('interfaces_export.json', 'w') as f:
    json.dump(directus_data, f, indent=2)
```

### 2. Import to Directus
```bash
# Import via Directus API
curl -X POST http://localhost:8055/interfaces/import \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d @interfaces_export.json
```

## Benefits of Directus Approach

### 1. **Zero Custom Development** for Core Features
- ✅ Versioning - Built-in
- ✅ Audit logging - Built-in  
- ✅ User management - Built-in
- ✅ API generation - Built-in
- ✅ Real-time updates - Built-in

### 2. **Database-First** - Works with Existing Schema
- ✅ No data migration needed
- ✅ Keep existing SQLite/PostgreSQL
- ✅ Directus just adds a layer on top

### 3. **Resilience & Recovery**
- ✅ Built-in backup/restore
- ✅ Version rollback
- ✅ Audit trail for debugging
- ✅ User permissions for safety

### 4. **Developer Experience**
- ✅ Auto-generated APIs
- ✅ GraphQL for complex queries
- ✅ WebSocket for real-time updates
- ✅ Admin UI for manual management

This gives us a robust, production-ready interface registry with minimal custom development!
