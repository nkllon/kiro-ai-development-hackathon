-- Directus Schema Relationships Extension
-- Adds proper relationships between collections to make the CMS useful

-- First, let's add missing columns for relationships
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS specification_id INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS requirement_id INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id INTEGER;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS specification_id INTEGER;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS related_code_file_id INTEGER;

ALTER TABLE code_files ADD COLUMN IF NOT EXISTS specification_id INTEGER;
ALTER TABLE code_files ADD COLUMN IF NOT EXISTS implements_task_id INTEGER;

ALTER TABLE specifications ADD COLUMN IF NOT EXISTS parent_specification_id INTEGER;
ALTER TABLE specifications ADD COLUMN IF NOT EXISTS depends_on_specification_id INTEGER;

-- Create a new requirements table if it doesn't exist
CREATE TABLE IF NOT EXISTS requirements (
    id SERIAL PRIMARY KEY,
    specification_id INTEGER NOT NULL,
    requirement_number VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    user_story TEXT,
    acceptance_criteria JSONB,
    priority INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'draft',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create specification_dependencies table for many-to-many relationships
CREATE TABLE IF NOT EXISTS specification_dependencies (
    id SERIAL PRIMARY KEY,
    specification_id INTEGER NOT NULL,
    depends_on_specification_id INTEGER NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'requires',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(specification_id, depends_on_specification_id)
);

-- Create task_dependencies table for task relationships
CREATE TABLE IF NOT EXISTS task_dependencies (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    depends_on_task_id INTEGER NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'blocks',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id)
);

-- Create code_file_relationships table
CREATE TABLE IF NOT EXISTS code_file_relationships (
    id SERIAL PRIMARY KEY,
    source_file_id INTEGER NOT NULL,
    target_file_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'imports', 'extends', 'implements', 'tests'
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_file_id, target_file_id, relationship_type)
);

-- Add foreign key constraints
ALTER TABLE tasks 
    ADD CONSTRAINT IF NOT EXISTS fk_tasks_specification 
    FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;

ALTER TABLE tasks 
    ADD CONSTRAINT IF NOT EXISTS fk_tasks_requirement 
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE SET NULL;

ALTER TABLE tasks 
    ADD CONSTRAINT IF NOT EXISTS fk_tasks_parent 
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL;

ALTER TABLE documents 
    ADD CONSTRAINT IF NOT EXISTS fk_documents_specification 
    FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;

ALTER TABLE documents 
    ADD CONSTRAINT IF NOT EXISTS fk_documents_code_file 
    FOREIGN KEY (related_code_file_id) REFERENCES code_files(id) ON DELETE SET NULL;

ALTER TABLE code_files 
    ADD CONSTRAINT IF NOT EXISTS fk_code_files_specification 
    FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;

ALTER TABLE code_files 
    ADD CONSTRAINT IF NOT EXISTS fk_code_files_task 
    FOREIGN KEY (implements_task_id) REFERENCES tasks(id) ON DELETE SET NULL;

ALTER TABLE requirements 
    ADD CONSTRAINT IF NOT EXISTS fk_requirements_specification 
    FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE CASCADE;

ALTER TABLE specification_dependencies 
    ADD CONSTRAINT IF NOT EXISTS fk_spec_deps_source 
    FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE CASCADE;

ALTER TABLE specification_dependencies 
    ADD CONSTRAINT IF NOT EXISTS fk_spec_deps_target 
    FOREIGN KEY (depends_on_specification_id) REFERENCES specifications(id) ON DELETE CASCADE;

ALTER TABLE task_dependencies 
    ADD CONSTRAINT IF NOT EXISTS fk_task_deps_source 
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

ALTER TABLE task_dependencies 
    ADD CONSTRAINT IF NOT EXISTS fk_task_deps_target 
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE;

ALTER TABLE code_file_relationships 
    ADD CONSTRAINT IF NOT EXISTS fk_code_rel_source 
    FOREIGN KEY (source_file_id) REFERENCES code_files(id) ON DELETE CASCADE;

ALTER TABLE code_file_relationships 
    ADD CONSTRAINT IF NOT EXISTS fk_code_rel_target 
    FOREIGN KEY (target_file_id) REFERENCES code_files(id) ON DELETE CASCADE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tasks_specification_id ON tasks(specification_id);
CREATE INDEX IF NOT EXISTS idx_tasks_requirement_id ON tasks(requirement_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_documents_specification_id ON documents(specification_id);
CREATE INDEX IF NOT EXISTS idx_code_files_specification_id ON code_files(specification_id);
CREATE INDEX IF NOT EXISTS idx_code_files_task_id ON code_files(implements_task_id);
CREATE INDEX IF NOT EXISTS idx_requirements_specification_id ON requirements(specification_id);
CREATE INDEX IF NOT EXISTS idx_spec_deps_source ON specification_dependencies(specification_id);
CREATE INDEX IF NOT EXISTS idx_spec_deps_target ON specification_dependencies(depends_on_specification_id);
CREATE INDEX IF NOT EXISTS idx_task_deps_source ON task_dependencies(task_id);
CREATE INDEX IF NOT EXISTS idx_task_deps_target ON task_dependencies(depends_on_task_id);

-- Add some sample data to demonstrate relationships
-- Link Integration Orchestrator spec to its tasks
DO $$
DECLARE
    integration_spec_id INTEGER;
    cursor_spec_id INTEGER;
BEGIN
    -- Find the Integration Orchestrator specification
    SELECT id INTO integration_spec_id 
    FROM specifications 
    WHERE spec_name = 'integration-orchestrator-framework' 
    LIMIT 1;
    
    -- Find the AI Cursor Sharing specification  
    SELECT id INTO cursor_spec_id 
    FROM specifications 
    WHERE spec_name = 'ai-driven-cursor-sharing' 
    LIMIT 1;
    
    -- Create a dependency relationship (cursor sharing depends on integration orchestrator)
    IF integration_spec_id IS NOT NULL AND cursor_spec_id IS NOT NULL THEN
        INSERT INTO specification_dependencies (specification_id, depends_on_specification_id, dependency_type)
        VALUES (cursor_spec_id, integration_spec_id, 'builds_upon')
        ON CONFLICT (specification_id, depends_on_specification_id) DO NOTHING;
    END IF;
    
    -- Link code files to specifications
    UPDATE code_files 
    SET specification_id = integration_spec_id 
    WHERE file_path LIKE '%integration_orchestrator%' 
    AND integration_spec_id IS NOT NULL;
    
    UPDATE code_files 
    SET specification_id = cursor_spec_id 
    WHERE file_path LIKE '%cursor_sharing%' 
    AND cursor_spec_id IS NOT NULL;
    
END $$;