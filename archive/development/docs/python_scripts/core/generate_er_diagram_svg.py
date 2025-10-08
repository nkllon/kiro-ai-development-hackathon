#!/usr/bin/env python3
"""
Generate ER Diagram SVG from Mermaid
====================================

Converts the Mermaid ER diagram to SVG format.
"""

import subprocess
import sys
from pathlib import Path

def generate_svg_from_mermaid():
    """Generate SVG from Mermaid ER diagram."""
    
    # Mermaid diagram content
    mermaid_content = """
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
"""
    
    # Write Mermaid file
    mermaid_file = Path("persistent_dag_registry.mmd")
    mermaid_file.write_text(mermaid_content)
    
    try:
        # Try to use mermaid-cli if available
        result = subprocess.run([
            "npx", "mermaid-cli", 
            "-i", str(mermaid_file),
            "-o", "persistent_dag_registry_er_diagram.svg"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SVG generated successfully using mermaid-cli")
            return True
        else:
            print(f"❌ mermaid-cli failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ mermaid-cli not available: {e}")
    
    try:
        # Try to use mermaid if available
        result = subprocess.run([
            "mermaid", 
            str(mermaid_file),
            "-o", "persistent_dag_registry_er_diagram.svg"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ SVG generated successfully using mermaid")
            return True
        else:
            print(f"❌ mermaid failed: {result.stderr}")
            
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ mermaid not available: {e}")
    
    # Fallback: Create a simple text-based diagram
    print("📝 Creating text-based ER diagram as fallback...")
    create_text_diagram()
    return False

def create_text_diagram():
    """Create a text-based ER diagram as fallback."""
    text_diagram = """
PERSISTENT DAG REGISTRY - ENTITY RELATIONSHIP DIAGRAM
====================================================

┌─────────────────────────────────────────────────────────┐
│                    REGISTRY_METADATA                    │
├─────────────────────────────────────────────────────────┤
│ id (PK)              │ INTEGER PRIMARY KEY              │
│ registry_id (UK)     │ TEXT UNIQUE NOT NULL             │
│ created_at           │ TEXT NOT NULL                    │
│ last_updated         │ TEXT NOT NULL                    │
│ total_modules        │ INTEGER DEFAULT 0                │
│ is_dag               │ BOOLEAN DEFAULT TRUE              │
└─────────────────────────────────────────────────────────┘
                                │
                                │ 1:1
                                ▼
┌─────────────────────────────────────────────────────────┐
│                        MODULES                          │
├─────────────────────────────────────────────────────────┤
│ module_id (PK)        │ TEXT PRIMARY KEY                │
│ class_name            │ TEXT                            │
│ file_path             │ TEXT                            │
│ line_number           │ INTEGER                         │
│ version               │ TEXT NOT NULL DEFAULT '1.0.0'   │
│ capabilities          │ TEXT (JSON array)               │
│ health_status         │ TEXT DEFAULT 'unknown'          │
│ registered_at         │ TEXT NOT NULL                   │
│ last_updated          │ TEXT NOT NULL                   │
└─────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   DEPENDENCIES  │ │   DEPENDENTS    │ │   AUDIT_LOG     │
    ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
    │ id (PK)         │ │ id (PK)         │ │ id (PK)         │
    │ module_id (FK)  │ │ module_id (FK)  │ │ action          │
    │ dependency_id   │ │ dependent_id    │ │ module_id (FK)  │
    │ (FK)            │ │ (FK)            │ │ details         │
    │ created_at      │ │ created_at      │ │ timestamp       │
    └─────────────────┘ └─────────────────┘ └─────────────────┘

RELATIONSHIPS:
- MODULES ||--o{ DEPENDENCIES : "has dependencies"
- MODULES ||--o{ DEPENDENCIES : "is dependency of"  
- MODULES ||--o{ DEPENDENTS : "has dependents"
- MODULES ||--o{ DEPENDENTS : "is dependent of"
- MODULES ||--o{ AUDIT_LOG : "generates audit entries"

REFERENTIAL INTEGRITY:
- All foreign keys have CASCADE DELETE constraints
- Unique constraints prevent duplicate relationships
- Self-referencing relationships maintain DAG structure
- JSON fields store structured metadata
"""
    
    with open("persistent_dag_registry_er_diagram.txt", "w") as f:
        f.write(text_diagram)
    
    print("✅ Text-based ER diagram created: persistent_dag_registry_er_diagram.txt")

if __name__ == "__main__":
    print("🎨 GENERATING ER DIAGRAM SVG")
    print("=" * 40)
    
    success = generate_svg_from_mermaid()
    
    if success:
        print("\n✅ SVG file created: persistent_dag_registry_er_diagram.svg")
    else:
        print("\n📝 Text diagram created: persistent_dag_registry_er_diagram.txt")
        print("💡 To generate SVG, install mermaid-cli: npm install -g @mermaid-js/mermaid-cli")


