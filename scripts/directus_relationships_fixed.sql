-- Directus Schema Relationships Extension (Fixed)
-- Adds proper relationships between collections

-- Add foreign key constraints (with error handling)
DO $$
BEGIN
    -- Tasks to Specifications
    BEGIN
        ALTER TABLE tasks ADD CONSTRAINT fk_tasks_specification 
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
    -- Documents to Specifications  
    BEGIN
        ALTER TABLE documents ADD CONSTRAINT fk_documents_specification 
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
    -- Code Files to Specifications
    BEGIN
        ALTER TABLE code_files ADD CONSTRAINT fk_code_files_specification 
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
    -- Requirements to Specifications
    BEGIN
        ALTER TABLE requirements ADD CONSTRAINT fk_requirements_specification 
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE CASCADE;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
    -- Specification Dependencies
    BEGIN
        ALTER TABLE specification_dependencies ADD CONSTRAINT fk_spec_deps_source 
        FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE CASCADE;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
    BEGIN
        ALTER TABLE specification_dependencies ADD CONSTRAINT fk_spec_deps_target 
        FOREIGN KEY (depends_on_specification_id) REFERENCES specifications(id) ON DELETE CASCADE;
    EXCEPTION WHEN duplicate_object THEN
        -- Constraint already exists, skip
    END;
    
END $$;

-- Now let's configure Directus to recognize these relationships
-- We need to add the relationship configurations to Directus

-- Update some sample data to show relationships
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'integration-orchestrator-framework' 
    LIMIT 1
)
WHERE file_path LIKE '%integration_orchestrator%';

UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'ai-driven-cursor-sharing' 
    LIMIT 1
)
WHERE file_path LIKE '%cursor_sharing%';