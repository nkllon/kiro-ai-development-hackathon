# Beast Mode Task List Requirements

## Critical Requirement: Beast Mode Formatted Task Lists

**⚠️ IMPORTANT**: The Beast Mode DAG executor can ONLY execute task lists that are formatted in Beast Mode hierarchical structure. Standard sequential task lists (1, 2, 3) will not work with Beast Mode parallel execution.

## Beast Mode Task Format Requirements

### 1. Hierarchical Numbering
Tasks must use hierarchical numbering to enable parallel execution:
- ✅ **Correct**: `1.1`, `1.2`, `2.1`, `3.1`, `3.2`
- ❌ **Incorrect**: `1`, `2`, `3`, `4`, `5`

### 2. Required Task Line Format
Each task line must follow this exact pattern:
```markdown
- [status] number title [hash-id] optional-annotations
```

**Examples:**
```markdown
- [ ] 1.1 Implement ContentScanner [cs-a7f3] ⚡ PARALLEL
- [-] 1.2 Implement ContentClassifier [cc-b8e4] ⚡ PARALLEL  
- [x] 2.1 Implement ContentInventoryManager [cim-c9f5] 🔄 SEQUENTIAL ✅ COMPLETED
```

### 3. Status Characters
- `[ ]` - Not started
- `[-]` - In progress  
- `[x]` - Completed
- `[!]` - Failed
- `[#]` - Blocked

### 4. Hash IDs
Each task must have a unique hash ID in brackets:
- Format: `[prefix-hash]` (e.g., `[cs-a7f3]`, `[cc-b8e4]`)
- Purpose: Enables task tracking and correlation across systems
- **New Requirement**: Hash IDs were not required in legacy format but are mandatory for Beast Mode

### 5. Parallel Execution Annotations
Optional but recommended annotations:
- `⚡ PARALLEL` - Can execute in parallel with other tasks in same phase
- `🔄 SEQUENTIAL` - Must execute sequentially after dependencies
- `✅ COMPLETED` - Visual indicator of completion status

## Parallel Execution Structure

### Phase-Based Organization
Tasks should be organized into phases that enable parallel execution:

```markdown
### Phase 1: Parallel Foundation ⚡ PARALLEL EXECUTION
- [ ] 1.1 Task A [hash-a] ⚡ PARALLEL
- [ ] 1.2 Task B [hash-b] ⚡ PARALLEL

### Phase 2: Sequential Integration 🔄 SEQUENTIAL  
- [ ] 2.1 Task C [hash-c] 🔄 SEQUENTIAL (depends on 1.1, 1.2)

### Phase 3: Parallel Analysis ⚡ PARALLEL EXECUTION
- [ ] 3.1 Task D [hash-d] ⚡ PARALLEL
- [ ] 3.2 Task E [hash-e] ⚡ PARALLEL
```

### Dependency Declaration
Dependencies should be clearly declared:
```markdown
- [ ] 2.1 Implement ContentInventoryManager [cim-c9f5] 🔄 SEQUENTIAL (depends on 1.1, 1.2)
  - **Dependencies**: ContentScanner (1.1), ContentClassifier (1.2)
```

## Conversion Process

### Converting Legacy Task Lists to Beast Mode

1. **Analyze Dependencies**: Identify which tasks can run in parallel
2. **Create Phases**: Group parallel tasks into phases
3. **Assign Hierarchical Numbers**: Use phase.task numbering (1.1, 1.2, 2.1)
4. **Add Hash IDs**: Generate unique hash IDs for each task
5. **Add Annotations**: Mark parallel vs sequential execution
6. **Validate**: Test with Beast Mode DAG executor

### Example Conversion

**Before (Legacy Format):**
```markdown
- [ ] 1. Implement Scanner
- [ ] 2. Implement Classifier  
- [ ] 3. Implement Manager
```

**After (Beast Mode Format):**
```markdown
### Phase 1: Parallel Discovery ⚡ PARALLEL EXECUTION
- [ ] 1.1 Implement Scanner [scan-a1b2] ⚡ PARALLEL
- [ ] 1.2 Implement Classifier [class-c3d4] ⚡ PARALLEL

### Phase 2: Sequential Integration 🔄 SEQUENTIAL
- [ ] 2.1 Implement Manager [mgr-e5f6] 🔄 SEQUENTIAL (depends on 1.1, 1.2)
```

## Benefits of Beast Mode Format

### Parallel Execution
- **Time Reduction**: Up to 50% faster execution through parallelization
- **Resource Utilization**: Better use of available compute resources
- **Dependency Management**: Clear dependency tracking and validation

### Enhanced Tracking
- **Hash IDs**: Unique identification for correlation across systems
- **Status Visualization**: Clear visual indicators of progress
- **Execution Waves**: Organized execution in dependency-aware waves

### Systematic Approach
- **Physics-Informed**: Respects real-world constraints and dependencies
- **PDCA Integration**: Supports systematic Plan-Do-Check-Act cycles
- **Beast Mode Compliance**: Enables full Beast Mode framework capabilities

## Migration Strategy

### For Existing Specs
1. **Audit Current Format**: Check if tasks use sequential (1,2,3) or hierarchical (1.1,1.2) numbering
2. **Dependency Analysis**: Map out actual dependencies between tasks
3. **Parallel Opportunity Identification**: Find tasks that can execute simultaneously
4. **Systematic Conversion**: Apply Beast Mode format systematically
5. **Validation**: Test with Beast Mode DAG executor

### For New Specs
- **Always use Beast Mode format** from the beginning
- **Design for parallelization** during requirements and design phases
- **Include hash IDs** in initial task creation
- **Plan execution waves** as part of implementation planning

## Tools and Automation

### Beast Mode Task Converter
A systematic tool should be created to:
- Parse legacy task lists
- Analyze dependencies automatically
- Generate Beast Mode formatted task lists
- Validate format compatibility
- Provide conversion reports

### Integration with Spec Workflow
- **Requirements Phase**: Consider parallel execution opportunities
- **Design Phase**: Design for parallel implementation
- **Task Phase**: Generate Beast Mode formatted task lists
- **Execution Phase**: Use Beast Mode DAG executor for optimal performance

This requirement ensures that the Beast Mode framework can deliver its full systematic and performance benefits through proper task list formatting and parallel execution capabilities.