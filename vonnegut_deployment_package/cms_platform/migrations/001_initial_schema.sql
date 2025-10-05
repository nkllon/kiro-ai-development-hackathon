-- CMS Core Data Model - Initial Schema Migration

-- Specifications table
CREATE TABLE IF NOT EXISTS specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    UNIQUE(name, version)
);

-- Code files table
CREATE TABLE IF NOT EXISTS code_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(500) NOT NULL UNIQUE,
    content_hash VARCHAR(64) NOT NULL,
    language VARCHAR(50),
    size_bytes INTEGER,
    specification_id UUID REFERENCES specifications(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    document_type VARCHAR(100),
    specification_id UUID REFERENCES specifications(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(20),
    estimated_effort INTEGER,
    specification_id UUID REFERENCES specifications(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Governance violations table
CREATE TABLE IF NOT EXISTS governance_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_file_id UUID REFERENCES code_files(id),
    rule_id VARCHAR(100) NOT NULL,
    violation_type VARCHAR(50),
    severity VARCHAR(20),
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deployment patterns table
CREATE TABLE IF NOT EXISTS deployment_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(100) NOT NULL,
    description TEXT,
    pattern_type VARCHAR(50),
    success_rate DECIMAL(5,2),
    usage_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Development costs table
CREATE TABLE IF NOT EXISTS development_costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specification_id UUID REFERENCES specifications(id),
    cost_type VARCHAR(50),
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_code_files_spec ON code_files(specification_id);
CREATE INDEX idx_code_files_path ON code_files(file_path);
CREATE INDEX idx_documents_spec ON documents(specification_id);
CREATE INDEX idx_tasks_spec ON tasks(specification_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_violations_file ON governance_violations(code_file_id);
CREATE INDEX idx_violations_resolved ON governance_violations(resolved);

-- Full-text search indexes
CREATE INDEX idx_documents_content ON documents USING gin(to_tsvector('english', content));
CREATE INDEX idx_documents_title ON documents USING gin(to_tsvector('english', title));
