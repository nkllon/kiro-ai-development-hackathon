-- Directus Database Initialization Script
-- This script sets up the initial database structure for Directus CMS
-- with the systematic schema design for repository content management

-- Enable necessary PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user with proper permissions (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'directus') THEN
        CREATE ROLE directus WITH LOGIN PASSWORD 'directus';
    END IF;
END
$$;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE directus TO directus;
GRANT ALL ON SCHEMA public TO directus;

-- Set up connection limits and security
ALTER ROLE directus CONNECTION LIMIT 50;

-- Create custom schema for repository content (separate from Directus system tables)
CREATE SCHEMA IF NOT EXISTS repository_content;
GRANT ALL ON SCHEMA repository_content TO directus;

-- Repository Content Tables with Consistent INTEGER IDs
-- These tables will be managed by our SchemaManager

-- Specifications table
CREATE TABLE IF NOT EXISTS repository_content.specifications (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code Files table
CREATE TABLE IF NOT EXISTS repository_content.code_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    specification_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (specification_id) REFERENCES repository_content.specifications(id) ON DELETE SET NULL
);

-- Documents table
CREATE TABLE IF NOT EXISTS repository_content.documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    document_type VARCHAR(50), -- 'requirements', 'design', 'tasks'
    specification_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (specification_id) REFERENCES repository_content.specifications(id) ON DELETE SET NULL
);

-- Tasks table
CREATE TABLE IF NOT EXISTS repository_content.tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'not_started',
    specification_id INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (specification_id) REFERENCES repository_content.specifications(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_specifications_name ON repository_content.specifications(name);
CREATE INDEX IF NOT EXISTS idx_specifications_status ON repository_content.specifications(status);

CREATE INDEX IF NOT EXISTS idx_code_files_spec_id ON repository_content.code_files(specification_id);
CREATE INDEX IF NOT EXISTS idx_code_files_path ON repository_content.code_files(file_path);

CREATE INDEX IF NOT EXISTS idx_documents_spec_id ON repository_content.documents(specification_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON repository_content.documents(document_type);

CREATE INDEX IF NOT EXISTS idx_tasks_spec_id ON repository_content.tasks(specification_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON repository_content.tasks(status);

-- Create updated_date trigger function
CREATE OR REPLACE FUNCTION update_updated_date_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for specifications table
DROP TRIGGER IF EXISTS update_specifications_updated_date ON repository_content.specifications;
CREATE TRIGGER update_specifications_updated_date
    BEFORE UPDATE ON repository_content.specifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_date_column();

-- Grant permissions on repository content schema
GRANT ALL ON ALL TABLES IN SCHEMA repository_content TO directus;
GRANT ALL ON ALL SEQUENCES IN SCHEMA repository_content TO directus;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA repository_content TO directus;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA repository_content GRANT ALL ON TABLES TO directus;
ALTER DEFAULT PRIVILEGES IN SCHEMA repository_content GRANT ALL ON SEQUENCES TO directus;
ALTER DEFAULT PRIVILEGES IN SCHEMA repository_content GRANT ALL ON FUNCTIONS TO directus;

-- Insert initial test data for validation (3 specifications as per requirements)
INSERT INTO repository_content.specifications (name, description, status) VALUES
    ('integration-orchestrator-framework', 'Systematic integration framework implementing "Don''t Reinvent Shit" principle', 'active'),
    ('ai-driven-cursor-sharing', 'AI-enhanced cursor sharing system with real-time coordination', 'active'),
    ('gpt5-context-calibration-system', 'AI capability assessment and context injection framework', 'active')
ON CONFLICT (name) DO NOTHING;

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'Directus database initialization completed successfully';
    RAISE NOTICE 'Repository content schema created with % specifications', 
        (SELECT COUNT(*) FROM repository_content.specifications);
END
$$;