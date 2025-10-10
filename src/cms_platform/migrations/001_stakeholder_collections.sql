-- Migration: Create Stakeholder Collections
-- Date: 2025-10-05T17:47:47.619024
-- Task: 1.1 Enhanced Directus Core Setup


-- Create developers collection
CREATE TABLE IF NOT EXISTS developers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(255) DEFAULT 'developer',
    skills JSONB,
    projects JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for developers
CREATE INDEX IF NOT EXISTS idx_developers_email ON developers(email);
CREATE INDEX IF NOT EXISTS idx_developers_role ON developers(role);
CREATE INDEX IF NOT EXISTS idx_developers_created_at ON developers(created_at);


-- Create devops collection
CREATE TABLE IF NOT EXISTS devops (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(255) DEFAULT 'devops',
    infrastructure JSONB,
    monitoring_tools JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for devops
CREATE INDEX IF NOT EXISTS idx_devops_email ON devops(email);
CREATE INDEX IF NOT EXISTS idx_devops_role ON devops(role);
CREATE INDEX IF NOT EXISTS idx_devops_created_at ON devops(created_at);


-- Create executives collection
CREATE TABLE IF NOT EXISTS executives (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(255) DEFAULT 'executive',
    department VARCHAR(255),
    kpis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for executives
CREATE INDEX IF NOT EXISTS idx_executives_email ON executives(email);
CREATE INDEX IF NOT EXISTS idx_executives_role ON executives(role);
CREATE INDEX IF NOT EXISTS idx_executives_created_at ON executives(created_at);


-- Create architects collection
CREATE TABLE IF NOT EXISTS architects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(255) DEFAULT 'architect',
    specialization VARCHAR(255),
    design_patterns JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for architects
CREATE INDEX IF NOT EXISTS idx_architects_email ON architects(email);
CREATE INDEX IF NOT EXISTS idx_architects_role ON architects(role);
CREATE INDEX IF NOT EXISTS idx_architects_created_at ON architects(created_at);

