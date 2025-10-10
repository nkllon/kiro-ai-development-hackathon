-- Directus Beast Mode Integration Database Initialization
-- This script sets up the initial database configuration for Directus with Beast Mode integration

-- Create extensions for better performance and functionality
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance on common Directus operations
-- These will be created after Directus initializes its schema

-- Beast Mode specific database optimizations
-- Set up connection pooling and performance parameters
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Create a function to log Beast Mode integration events
CREATE OR REPLACE FUNCTION log_beast_mode_event(
    event_type TEXT,
    event_data JSONB DEFAULT '{}'::JSONB
) RETURNS VOID AS $$
BEGIN
    -- This function can be used by Directus to log Beast Mode integration events
    -- Implementation can be extended based on specific logging requirements
    RAISE NOTICE 'Beast Mode Event: % - %', event_type, event_data;
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT EXECUTE ON FUNCTION log_beast_mode_event(TEXT, JSONB) TO directus;