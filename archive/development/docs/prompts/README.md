# Prompt Processing Workflow

## Directory Structure

```
prompts/
├── staging/           # New prompt files awaiting processing
├── in-progress/       # Currently executing tasks with agent tracking
├── complete/          # Successfully completed tasks
└── README.md         # This documentation
```

## Task Lifecycle

### 1. Staging
- Place new prompt files in `prompts/staging/`
- Supported formats: `.md`, `.txt`
- Hook automatically detects new files

### 2. In-Progress Processing
- Agent generates unique ID: `agent-{timestamp}-{random}`
- File moved to `prompts/in-progress/{original-name}-{agent-id}.md`
- Metadata header added with execution tracking
- Real-time progress updates logged

### 3. Completion
- Task validation and deliverable verification
- Completion summary added to file
- File moved to `prompts/complete/{original-name}-{agent-id}-completed-{timestamp}.md`

## Agent Identification Format

Each executing agent gets a unique identifier:
- **Format**: `agent-{unix-timestamp}-{6-char-random}`
- **Example**: `agent-1738012345-xk7m2p`
- **Purpose**: Track concurrent executions and prevent conflicts

## Metadata Headers

### In-Progress Header
```markdown
---
Agent-ID: agent-1738012345-xk7m2p
Start-Time: 2025-01-27T10:30:45Z
Status: in-progress
Original-File: my-task.md
---
```

### Completion Addition
```markdown
## Completion Summary
- **Completion Time**: 2025-01-27T11:15:22Z
- **Status**: completed
- **Deliverables**: [List of created files]
- **Validation**: All requirements verified
- **Agent Notes**: [Important notes]
```

## Usage

1. **Create Prompt**: Place `.md` or `.txt` file in `prompts/staging/`
2. **Trigger Hook**: Use Kiro's hook system to process the file
3. **Monitor Progress**: Check `prompts/in-progress/` for execution status
4. **Review Results**: Find completed tasks in `prompts/complete/`

## Benefits

- **Audit Trail**: Complete tracking of all task executions
- **Concurrent Safety**: Unique agent IDs prevent conflicts
- **Progress Visibility**: Real-time status updates
- **Knowledge Preservation**: All execution details preserved
- **Systematic Processing**: Consistent workflow for all tasks

## Governance Compliance

This workflow follows the steering rules for:
- **Systematic Development**: Structured task processing
- **Observer Mode**: Complete audit trails
- **Mathematical Governance**: Deterministic agent identification
- **Safety Protocols**: Proper error handling and validation