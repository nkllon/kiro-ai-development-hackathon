-- Repository Discovery Directus Schema Extension
-- Generated: 2025-09-18T12:05:16.492476
-- Extends existing 5-collection pattern with repository content

-- Create repository_items table
CREATE TABLE repository_items (id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    path VARCHAR(1000) NOT NULL,
    name VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64),
    file_size INTEGER,
    mime_type VARCHAR(100),
    encoding VARCHAR(50),
    is_binary BOOLEAN NOT NULL DEFAULT False,
    line_count INTEGER,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id)
);

-- Indexes for repository_items
CREATE INDEX idx_repository_items_item_type ON repository_items(item_type);
CREATE INDEX idx_repository_items_path ON repository_items(path);
CREATE INDEX idx_repository_items_content_hash ON repository_items(content_hash);

-- Create specifications table
CREATE TABLE specifications (id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    repository_item_id UUID NOT NULL,
    spec_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    priority INTEGER NOT NULL DEFAULT 3,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id)
);

-- Indexes for specifications
CREATE INDEX idx_specifications_status ON specifications(status);
CREATE INDEX idx_specifications_priority ON specifications(priority);

-- Foreign key constraints for specifications
ALTER TABLE specifications ADD CONSTRAINT fk_specifications_repository_item_id FOREIGN KEY (repository_item_id) REFERENCES repository_items(id) ON UPDATE CASCADE ON DELETE CASCADE;

-- Create requirements table
CREATE TABLE requirements (id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    specification_id UUID NOT NULL,
    requirement_number VARCHAR(50) NOT NULL,
    user_story TEXT NOT NULL,
    acceptance_criteria JSONB NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id)
);

-- Indexes for requirements
CREATE INDEX idx_requirements_spec_id ON requirements(specification_id);
CREATE INDEX idx_requirements_status ON requirements(status);

-- Foreign key constraints for requirements
ALTER TABLE requirements ADD CONSTRAINT fk_requirements_specification_id FOREIGN KEY (specification_id) REFERENCES specifications(id) ON UPDATE CASCADE ON DELETE CASCADE;

-- Create analysis_artifacts table
CREATE TABLE analysis_artifacts (id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    repository_item_id UUID,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL DEFAULT 1.0,
    generated_by VARCHAR(100),
    correlation_id VARCHAR(100),
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id)
);

-- Indexes for analysis_artifacts
CREATE INDEX idx_analysis_artifacts_type ON analysis_artifacts(analysis_type);
CREATE INDEX idx_analysis_artifacts_correlation ON analysis_artifacts(correlation_id);

-- Foreign key constraints for analysis_artifacts
ALTER TABLE analysis_artifacts ADD CONSTRAINT fk_analysis_artifacts_repository_item_id FOREIGN KEY (repository_item_id) REFERENCES repository_items(id) ON UPDATE CASCADE ON DELETE SET NULL;

-- Create operation_traces table
CREATE TABLE operation_traces (id UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    trace_id VARCHAR(255) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    component_name VARCHAR(255) NOT NULL,
    duration_ms DECIMAL(10,3),
    input_parameters JSONB,
    output_result JSONB,
    error_info JSONB,
    correlation_id VARCHAR(255) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_created UUID REFERENCES directus_users(id),
    user_updated UUID REFERENCES directus_users(id)
);

-- Indexes for operation_traces
CREATE INDEX idx_operation_traces_trace_id ON operation_traces(trace_id);
CREATE INDEX idx_operation_traces_operation ON operation_traces(operation_name);
CREATE INDEX idx_operation_traces_correlation ON operation_traces(correlation_id);
