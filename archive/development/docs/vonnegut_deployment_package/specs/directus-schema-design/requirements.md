# Requirements Document

## Introduction

The Directus Schema Design provides a clean, minimal database schema with proper referential integrity for managing repository content. This focused specification addresses only the database schema design and relationship structure, ensuring a solid foundation before any application logic or UI configuration.

This spec is intentionally limited to database schema concerns only, following the single responsibility principle to prevent the scope creep and implementation complexity that led to previous failures.

## Requirements

### Requirement 1

**User Story:** As a database administrator, I want a clean database schema with consistent data types, so that all foreign key relationships work correctly without type mismatches.

#### Acceptance Criteria

1. WHEN the schema is created THEN all ID fields SHALL use INTEGER type consistently (no UUID/INTEGER mixing)
2. WHEN foreign key constraints are defined THEN they SHALL reference compatible data types only
3. WHEN tables are created THEN they SHALL include proper primary keys, indexes, and constraints
4. WHEN the schema is validated THEN it SHALL pass referential integrity checks
5. WHEN constraints are applied THEN they SHALL succeed without type mismatch errors

### Requirement 2

**User Story:** As a content manager, I want exactly 4 core collections with clear relationships, so that I can manage specifications, their code files, documents, and tasks.

#### Acceptance Criteria

1. WHEN the schema is created THEN it SHALL include exactly 4 collections: specifications, code_files, documents, tasks
2. WHEN specifications table is created THEN it SHALL have fields: id, name, description, status, created_date
3. WHEN code_files table is created THEN it SHALL have fields: id, file_name, file_path, specification_id, created_date
4. WHEN documents table is created THEN it SHALL have fields: id, title, content, specification_id, created_date
5. WHEN tasks table is created THEN it SHALL have fields: id, title, description, specification_id, status, created_date

### Requirement 3

**User Story:** As a system architect, I want simple many-to-one relationships only, so that the schema is easy to understand and maintain without complex junction tables.

#### Acceptance Criteria

1. WHEN relationships are defined THEN code_files SHALL have many-to-one relationship to specifications
2. WHEN relationships are defined THEN documents SHALL have many-to-one relationship to specifications
3. WHEN relationships are defined THEN tasks SHALL have many-to-one relationship to specifications
4. WHEN foreign keys are created THEN they SHALL use ON DELETE SET NULL for data preservation
5. WHEN the schema is complete THEN it SHALL have exactly 3 foreign key relationships and no junction tables

### Requirement 4

**User Story:** As a database validator, I want comprehensive schema validation, so that the database structure is correct before any data is added.

#### Acceptance Criteria

1. WHEN the schema is applied THEN the system SHALL validate all tables exist with correct structure
2. WHEN foreign keys are created THEN the system SHALL test each constraint with sample data
3. WHEN indexes are applied THEN the system SHALL verify they improve query performance
4. WHEN validation completes THEN the system SHALL provide a comprehensive schema report
5. WHEN validation fails THEN the system SHALL rollback changes and provide clear error messages

### Requirement 5

**User Story:** As a quality assurance user, I want the schema to be tested with exactly 3 sample specifications, so that relationships can be verified with minimal, controlled data.

#### Acceptance Criteria

1. WHEN sample data is added THEN it SHALL include exactly 3 specifications: Integration Orchestrator, AI Cursor Sharing, GPT-5 Context Calibration
2. WHEN code files are linked THEN each specification SHALL have 2-3 related code files for testing
3. WHEN documents are linked THEN each specification SHALL have 1-2 related documents for testing
4. WHEN tasks are linked THEN each specification SHALL have 2-3 related tasks for testing
5. WHEN relationships are tested THEN the system SHALL verify bidirectional navigation works for all sample data