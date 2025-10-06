#!/usr/bin/env python3
"""
Create HTML with Mermaid ER Diagram
==================================

Creates an HTML file with embedded Mermaid diagram that can be viewed in browser.
"""

def create_html_with_mermaid():
    """Create HTML file with Mermaid ER diagram."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persistent DAG Registry - ER Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .mermaid {
            text-align: center;
            margin: 20px 0;
        }
        .info {
            background: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .stat-title {
            font-weight: bold;
            color: #007bff;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.2em;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗄️ Persistent DAG Registry - Entity Relationship Diagram</h1>
        
        <div class="info">
            <h3>📊 Database Schema Overview</h3>
            <p>This diagram shows the complete entity relationship structure of the Persistent DAG Registry with full referential integrity constraints.</p>
        </div>
        
        <div class="mermaid">
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
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">Total Tables</div>
                <div class="stat-value">5</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Foreign Keys</div>
                <div class="stat-value">8</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Unique Constraints</div>
                <div class="stat-value">3</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Cascade Deletes</div>
                <div class="stat-value">4</div>
            </div>
        </div>
        
        <div class="info">
            <h3>🔗 Referential Integrity Features</h3>
            <ul>
                <li><strong>CASCADE DELETE:</strong> Removing a module removes all its dependencies and dependents</li>
                <li><strong>FOREIGN KEY CONSTRAINTS:</strong> All references must point to existing modules</li>
                <li><strong>UNIQUE CONSTRAINTS:</strong> Prevent duplicate dependency relationships</li>
                <li><strong>CHECK CONSTRAINTS:</strong> Ensure data validity (version format, status values)</li>
                <li><strong>INDEXES:</strong> Optimized for common queries (dependency lookups, audit trails)</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>🎯 DAG Enforcement</h3>
            <ul>
                <li><strong>Cycle Detection:</strong> DFS algorithm prevents circular dependencies</li>
                <li><strong>Bidirectional Tracking:</strong> Both dependencies and dependents maintained</li>
                <li><strong>Transaction Safety:</strong> All operations wrapped in transactions</li>
                <li><strong>Validation:</strong> Continuous DAG validation with validate_dag() method</li>
            </ul>
        </div>
    </div>
    
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            er: {
                fontSize: 12,
                fontFamily: 'Arial, sans-serif'
            }
        });
    </script>
</body>
</html>
"""
    
    with open("persistent_dag_registry_er_diagram.html", "w") as f:
        f.write(html_content)
    
    print("✅ HTML file created: persistent_dag_registry_er_diagram.html")
    print("🌐 Open in browser to view the interactive ER diagram")
    print("📊 The diagram shows the complete database schema with referential integrity")

if __name__ == "__main__":
    create_html_with_mermaid()


