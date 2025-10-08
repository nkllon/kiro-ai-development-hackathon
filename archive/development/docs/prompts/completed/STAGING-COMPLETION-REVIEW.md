# Staging Directory Completion Review

## Mission

Systematically review every prompt file in the `prompts/staging/` directory to assess completion status, readiness for execution, and identify any gaps or dependencies that need resolution.

## Review Methodology

For each prompt file in staging, assess:

### 1. Completion Status Classification
- **✅ READY**: Complete prompt, ready for immediate execution
- **🔄 IN-PROGRESS**: Partially complete, needs finishing touches
- **📝 DRAFT**: Basic structure exists, needs significant development
- **🚫 BLOCKED**: Cannot proceed due to dependencies or issues
- **❓ UNCLEAR**: Purpose or requirements not well defined

### 2. Execution Readiness Assessment
- **Clear objectives**: Does the prompt have well-defined goals?
- **Actionable instructions**: Are the steps clear and executable?
- **Dependencies identified**: Are all prerequisites documented?
- **Success criteria**: How do we know when it's complete?
- **Resource requirements**: Time estimates, tools needed, etc.

### 3. Priority Classification
- **🔥 CRITICAL**: Blocking other work, must be completed first
- **⚡ HIGH**: Important for project success, should be prioritized
- **📋 MEDIUM**: Valuable but not urgent, can be scheduled
- **🔍 LOW**: Nice to have, can be deferred if needed

## Systematic Review Process

### Phase 1: Inventory and Categorization
Review all 90+ files in `prompts/staging/` and create a comprehensive inventory with:
- File name and purpose
- Completion status (✅🔄📝🚫❓)
- Priority level (🔥⚡📋🔍)
- Dependencies and blockers
- Estimated execution time
- Required resources/tools

### Phase 2: Dependency Analysis
Map dependencies between prompts to identify:
- **Execution order requirements**: Which prompts must run before others
- **Circular dependencies**: Any problematic dependency loops
- **Critical path**: The sequence that determines overall completion time
- **Parallel execution opportunities**: Which prompts can run simultaneously

### Phase 3: Gap Analysis
Identify missing elements:
- **Incomplete prompt chains**: Where are the gaps in the workflow?
- **Missing success criteria**: Which prompts lack clear completion definitions?
- **Resource gaps**: What tools, data, or capabilities are missing?
- **Quality issues**: Which prompts need refinement or clarification?

### Phase 4: Execution Recommendations
Provide actionable recommendations:
- **Immediate actions**: What can be executed right now
- **Preparation needed**: What needs to be completed first
- **Resource allocation**: How to distribute work efficiently
- **Risk mitigation**: How to handle blockers and dependencies

## Expected Deliverables

### 1. Comprehensive Staging Inventory
A detailed spreadsheet/table with all prompts categorized by:
- Completion status
- Priority level
- Dependencies
- Execution time estimates
- Resource requirements

### 2. Dependency Graph
Visual representation of prompt dependencies showing:
- Critical path through all prompts
- Parallel execution opportunities
- Potential bottlenecks
- Circular dependency issues (if any)

### 3. Execution Roadmap
Prioritized plan showing:
- **Phase 1**: Immediate execution candidates (ready now)
- **Phase 2**: Short-term preparation needed (1-2 days)
- **Phase 3**: Medium-term development required (3-7 days)
- **Phase 4**: Long-term or deferred items

### 4. Quality Assessment Report
Analysis of prompt quality including:
- **Well-structured prompts**: Examples of good prompt design
- **Improvement needed**: Prompts requiring refinement
- **Missing elements**: Common gaps across multiple prompts
- **Best practices**: Patterns that should be replicated

### 5. Resource Requirements Summary
Consolidated view of what's needed:
- **Human resources**: Estimated person-hours by skill type
- **Technical resources**: Tools, systems, access requirements
- **Dependencies**: External blockers that need resolution
- **Timeline**: Realistic completion estimates

## Success Criteria

This review is complete when:
- [ ] All 90+ staging prompts have been individually assessed
- [ ] Completion status is clearly documented for each prompt
- [ ] Dependencies are mapped and visualized
- [ ] Execution roadmap is prioritized and actionable
- [ ] Resource requirements are quantified
- [ ] Quality issues are identified with improvement recommendations
- [ ] Next steps are clearly defined for immediate action

## Context and Constraints

### Repository State
- 108 specification directories in `.kiro/specs/`
- Constellation elaboration system with 4-layer architecture
- 22-dimension ontology framework
- CMS Architecture specification available
- Multiple optimization and execution analysis documents

### Governance Requirements
- Follow systematic development governance (Hounds Protocol)
- Maintain mathematical governance (DAG compliance)
- Apply observer-first leadership principles
- Ensure all prompts align with established steering rules

### Quality Standards
- All prompts must have clear success criteria
- Dependencies must be explicitly documented
- Execution time estimates must be realistic
- Resource requirements must be quantified
- Completion definitions must be unambiguous

## Execution Instructions

1. **Start with inventory**: Systematically go through each file in `prompts/staging/`
2. **Apply consistent criteria**: Use the same assessment framework for all prompts
3. **Document thoroughly**: Capture all findings in structured format
4. **Identify patterns**: Look for common issues and best practices
5. **Prioritize actionably**: Focus on what can be executed immediately
6. **Validate dependencies**: Ensure dependency mapping is accurate
7. **Provide recommendations**: Make specific, actionable suggestions

## Output Format

Structure the review as:
```markdown
# Staging Directory Completion Review Results

## Executive Summary
[High-level findings and recommendations]

## Detailed Inventory
[Comprehensive table of all prompts with assessments]

## Dependency Analysis
[Dependency graph and critical path analysis]

## Execution Roadmap
[Prioritized phases with timelines]

## Quality Assessment
[Prompt quality analysis and improvement recommendations]

## Resource Requirements
[Consolidated resource and timeline estimates]

## Immediate Actions
[What can be started right now]

## Next Steps
[Clear action items for moving forward]
```

This review will provide the systematic analysis needed to efficiently process the entire staging directory and move all prompts toward completion.