# Phase 5a: CMS Requirements Consolidation

## Objective

Consolidate all CMS requirements discovered across Phases 1-4 into a comprehensive, deduplicated set of CMS capabilities and data model requirements.

## Context

**Inputs:**
- Phase 1c: CMS Dependency Discovery outputs
- Phase 2: All CMS dependencies from requirements.md files
- Phase 3: All CMS data models from design.md files
- Phase 4: All CMS integration tasks from tasks.md files

## Task

### 1. CMS Capability Requirements Consolidation

Aggregate all CMS capability requirements from all specs:

```yaml
cms_capabilities:
  search_and_discovery:
    required_by_specs:
      - repository-content-discovery-indexing (CRITICAL)
      - multi-perspective-ghostbusters (HIGH)
      - [...]
    requirements:
      - Full-text search across all content types
      - Semantic search using AI/ML
      - Code pattern matching
      - Sub-500ms response time for 95th percentile
      - Support for 100,000+ indexed items
    priority: CRITICAL

  content_management:
    required_by_specs: [...]
    requirements: [...]
    priority: CRITICAL

  integration_apis:
    required_by_specs: [...]
    requirements: [...]
    priority: HIGH

  [... for all 6 major capability areas ...]
```

### 2. CMS Data Model Consolidation

Merge all data model requirements from all specs into a unified schema:

```yaml
cms_unified_schema:
  collections:
    - name: repository_files
      purpose: "Store metadata for all repository files"
      required_by:
        - repository-content-discovery-indexing
        - artifact-classification
        - [...]
      fields:
        - name: file_path
          type: string
          required: true
          indexed: true
          source_specs:
            - repository-content-discovery-indexing: "Primary key"
            - artifact-classification: "Classification target"
        - name: file_type
          type: enum
          values: [spec, source, doc, config, script, test, analysis]
          required: true
          indexed: true
          source_specs: [...]
        - name: content_hash
          type: string
          required: true
          source_specs: [...]
        - name: last_modified
          type: timestamp
          required: true
          indexed: true
          source_specs: [...]
        - name: metadata
          type: json
          required: false
          source_specs: [...]
      relationships:
        - type: many-to-one
          target: specifications
          field: spec_id
          source_specs: [...]
      estimated_volume: 10000+
      growth_rate: "100-200 files/month"

    - name: specifications
      purpose: "Store spec metadata and dependencies"
      required_by: [...]
      fields: [...]
      relationships: [...]
      estimated_volume: 108 initial, +5-10/month

    [... for all collections ...]

  relationships_graph:
    - specifications.dependencies -> specifications (many-to-many)
    - repository_files.spec_id -> specifications.id (many-to-one)
    - requirements.spec_id -> specifications.id (many-to-one)
    - requirements.depends_on -> requirements.id (many-to-many)
    [... all relationships ...]
```

### 3. Deduplication and Conflict Resolution

Identify and resolve:
- **Duplicate requirements** - Same requirement from multiple specs
- **Conflicting requirements** - Incompatible requirements from different specs
- **Overlapping data models** - Similar fields/collections that should be merged
- **Schema conflicts** - Different types/constraints for same logical entity

Document all resolutions:
```markdown
## Conflict Resolution Log

### Conflict 1: File Type Enumeration

**Conflicting Specs:**
- repository-content-discovery: [spec, source, doc, config]
- artifact-classification: [specification, code, documentation, configuration, script, test, analysis, report]

**Resolution:** Use artifact-classification's more comprehensive enumeration
**Rationale:** More granular classification provides better intelligence
**Affected Specs:** Update repository-content-discovery requirements
```

### 4. Priority Classification

Classify all CMS features by implementation priority:

**CRITICAL (MVP Blocking):**
- Features required for core intelligence operations
- Data models needed for critical path specs
- APIs for essential integrations

**HIGH (Full Constellation):**
- Features needed for complete constellation
- Advanced search capabilities
- Analytics and reporting

**MEDIUM (Enhancement):**
- Nice-to-have features
- Optimization capabilities
- Additional integrations

**LOW (Future):**
- Experimental features
- Advanced analytics
- Future enhancements

### 5. Gap Analysis Against Current CMS Architecture

Compare consolidated requirements against existing CMS Architecture spec:

```markdown
| Requirement | CMS Arch Status | Gap Severity | Remediation |
|-------------|----------------|--------------|-------------|
| Semantic search | MENTIONED | HIGH | Add detailed requirements in R6.1 |
| Repository files collection | MISSING | CRITICAL | Add to data model section |
| GraphQL API | ADDRESSED | - | Already covered in R8.2 |
| [...]  | [...] | [...] | [...] |
```

## Deliverables

### 1. Consolidated CMS Requirements

Create `.kiro/reports/cms-requirements-consolidated.yaml` with:
- All capability requirements deduplicated
- All data model requirements merged
- Priority classifications
- Conflict resolutions documented

### 2. CMS Data Model Schema

Create `.kiro/reports/cms-unified-data-model.yaml` with:
- Complete Directus schema definitions
- All collections and fields
- All relationships
- Volume estimates and growth projections

### 3. CMS Gap Analysis

Create `.kiro/reports/cms-gap-analysis-final.md` identifying:
- Requirements missing from CMS Architecture
- Requirements needing more detail
- Conflicts requiring resolution
- Implementation priorities

### 4. CMS Capability Matrix

Create `.kiro/reports/cms-capability-matrix-final.md` showing:
- All capabilities required
- Specs depending on each capability
- Priority levels
- Implementation complexity estimates

## Validation Criteria

✅ All CMS requirements from Phases 1-4 consolidated
✅ All data models merged with conflict resolution
✅ No duplicate requirements
✅ All conflicts resolved and documented
✅ Priority classifications complete
✅ Gap analysis identifies all missing CMS Architecture content

## Timeline

**Duration:** 1 day
**Dependencies:** Phases 1-4 complete (all requirements, designs, tasks)
**Parallelization:** Sequential (consolidation task)

## Success Metrics

- 100% of CMS requirements consolidated
- 100% of conflicts resolved
- Complete unified data model
- Clear gap analysis for CMS Architecture update
