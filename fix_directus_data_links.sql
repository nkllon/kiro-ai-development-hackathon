-- Fix Directus Data Links
-- Directly update the database to create relationships

-- Link Integration Orchestrator code files
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'integration-orchestrator-framework' 
    LIMIT 1
)
WHERE file_path LIKE '%integration_orchestrator%' 
   OR file_path LIKE '%integration-orchestrator%'
   OR file_name LIKE '%integration_orchestrator%';

-- Link AI Cursor Sharing code files  
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'ai-driven-cursor-sharing' 
    LIMIT 1
)
WHERE file_path LIKE '%cursor_sharing%' 
   OR file_path LIKE '%cursor-sharing%'
   OR file_name LIKE '%cursor_sharing%';

-- Link GPT5 Context Calibration code files
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'gpt5-context-calibration-system' 
    LIMIT 1
)
WHERE file_path LIKE '%gpt5%' 
   OR file_path LIKE '%context_calibration%'
   OR file_name LIKE '%gpt5%';

-- Link Beast Mode core files
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'beast-mode-core' 
    LIMIT 1
)
WHERE file_path LIKE '%beast_mode/core%' 
   OR file_path LIKE '%beast_mode/__init__%'
   OR file_name = 'core.py';

-- Link monitoring system files
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'prometheus-monitoring-system-repair' 
    LIMIT 1
)
WHERE file_path LIKE '%monitoring%' 
   OR file_path LIKE '%prometheus%'
   OR file_name LIKE '%monitoring%';

-- Link makefile system files
UPDATE code_files 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'systematic-makefile-management' 
    LIMIT 1
)
WHERE file_path LIKE '%makefile%' 
   OR file_name LIKE '%makefile%'
   OR file_name LIKE 'Makefile%';

-- Link documents to specifications based on file paths
UPDATE documents 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'integration-orchestrator-framework' 
    LIMIT 1
)
WHERE title LIKE '%integration%orchestrator%' 
   OR title LIKE '%integration-orchestrator%';

UPDATE documents 
SET specification_id = (
    SELECT id FROM specifications 
    WHERE spec_name = 'ai-driven-cursor-sharing' 
    LIMIT 1
)
WHERE title LIKE '%cursor%sharing%' 
   OR title LIKE '%cursor-sharing%';

-- Create some sample tasks for the Integration Orchestrator
INSERT INTO tasks (title, description, status, priority, specification_id)
SELECT 
    'Set up project structure and core interfaces',
    'Create directory structure for discovery, patterns, anti-reinvention, and composition components',
    'completed',
    1,
    id
FROM specifications 
WHERE spec_name = 'integration-orchestrator-framework'
LIMIT 1;

INSERT INTO tasks (title, description, status, priority, specification_id)
SELECT 
    'Implement capability discovery system',
    'Create ecosystem capability scanner and overlap detection',
    'completed',
    1,
    id
FROM specifications 
WHERE spec_name = 'integration-orchestrator-framework'
LIMIT 1;

INSERT INTO tasks (title, description, status, priority, specification_id)
SELECT 
    'Build pattern registry system',
    'Create reusable integration patterns and templates',
    'completed',
    1,
    id
FROM specifications 
WHERE spec_name = 'integration-orchestrator-framework'
LIMIT 1;

-- Create tasks for AI Cursor Sharing
INSERT INTO tasks (title, description, status, priority, specification_id)
SELECT 
    'Implement cursor event capture using existing APIs',
    'Connect to existing macOS accessibility infrastructure',
    'completed',
    1,
    id
FROM specifications 
WHERE spec_name = 'ai-driven-cursor-sharing'
LIMIT 1;

INSERT INTO tasks (title, description, status, priority, specification_id)
SELECT 
    'Develop AI behavioral pattern recognition engine',
    'Create real-time cursor movement pattern recognition',
    'completed',
    1,
    id
FROM specifications 
WHERE spec_name = 'ai-driven-cursor-sharing'
LIMIT 1;

-- Show results
SELECT 
    s.spec_name,
    COUNT(DISTINCT cf.id) as code_files_count,
    COUNT(DISTINCT d.id) as documents_count,
    COUNT(DISTINCT t.id) as tasks_count
FROM specifications s
LEFT JOIN code_files cf ON cf.specification_id = s.id
LEFT JOIN documents d ON d.specification_id = s.id  
LEFT JOIN tasks t ON t.specification_id = s.id
GROUP BY s.id, s.spec_name
HAVING COUNT(DISTINCT cf.id) > 0 OR COUNT(DISTINCT d.id) > 0 OR COUNT(DISTINCT t.id) > 0
ORDER BY (COUNT(DISTINCT cf.id) + COUNT(DISTINCT d.id) + COUNT(DISTINCT t.id)) DESC
LIMIT 10;