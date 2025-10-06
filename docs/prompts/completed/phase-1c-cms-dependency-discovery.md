# Phase 1c: CMS Dependency Discovery

## Objective

Systematically discover all explicit and implicit CMS dependencies across the repository constellation, analyzing which specifications require CMS capabilities and what specific CMS features they need.

## Context

**Known CMS Dependencies:**
- Repository Content Discovery & Indexing (Requirement 30 - explicit CMS integration)
- CMS Architecture (defines the CMS system itself)
- Directus-related specs (CMS implementation)

**CMS Capabilities (from CMS Architecture):**
1. **Search and Discovery** - Multi-modal search, semantic search, code pattern matching
2. **Content Management** - Automated ingestion, lifecycle management, version control
3. **Integration** - Development tool integration, APIs, webhooks
4. **Analytics** - Usage analytics, business intelligence
5. **Security** - Authentication, authorization, data protection
6. **Performance** - Response times, scalability, caching

## Task

### 1. Explicit CMS Dependency Discovery

Scan all requirements.md, design.md, and tasks.md files for explicit mentions of:
- "CMS", "Directus", "content management"
- "centralized storage", "data persistence"
- "search", "indexing", "discovery"
- "API", "GraphQL", "REST"
- References to CMS Architecture spec

For each explicit reference, document:
```json
{
  "spec_name": "repository-content-discovery-indexing",
  "dependency_type": "EXPLICIT",
  "file_location": "requirements.md:30",
  "requirement_text": "Requirement 30: CMS Integration for Data Storage",
  "cms_capabilities_needed": [
    "Centralized data storage",
    "RESTful API access",
    "Real-time synchronization",
    "Search and query capabilities"
  ],
  "criticality": "CRITICAL",
  "rationale": "Core intelligence data must persist across system restarts"
}
```

### 2. Implicit CMS Dependency Discovery

Analyze all specs for implicit CMS needs based on patterns:

**Pattern 1: Data Persistence Needs**
- Phrases like "store", "persist", "save", "retrieve", "query"
- Requirements for data to survive system restarts
- Need for historical data or audit trails

**Pattern 2: Search and Discovery Needs**
- Requirements for finding or searching content
- Need to correlate or relate different pieces of information
- Pattern matching or similarity detection

**Pattern 3: Multi-User/Multi-Agent Coordination**
- Shared state requirements
- Coordination between different systems or agents
- Need for centralized truth or consensus

**Pattern 4: Reporting and Analytics**
- Dashboard or visualization requirements
- Metrics collection and aggregation
- Historical trend analysis

**Pattern 5: API/Integration Requirements**
- External system integration needs
- Programmatic access to data
- Webhook or event-driven patterns

### 3. CMS Capability Requirements Matrix

For each spec with CMS dependencies, map to specific CMS capabilities:

```markdown
| Spec | Search | Content Mgmt | Integration | Analytics | Security | Performance |
|------|--------|--------------|-------------|-----------|----------|-------------|
| repository-discovery | ✅ HIGH | ✅ HIGH | ✅ MEDIUM | ✅ MEDIUM | ⬜ LOW | ✅ HIGH |
| system-health | ⬜ LOW | ✅ MEDIUM | ✅ HIGH | ✅ HIGH | ⬜ LOW | ✅ MEDIUM |
```

**Priority Levels:**
- **✅ HIGH:** Critical dependency, spec cannot function without this capability
- **✅ MEDIUM:** Important dependency, workarounds possible but suboptimal
- **⬜ LOW:** Nice-to-have, provides additional value
- **❌ N/A:** Not needed for this spec

### 4. CMS Feature Gap Analysis

Compare required CMS capabilities against CMS Architecture specification:
- **Covered:** CMS Architecture already addresses this requirement
- **Partial:** CMS Architecture mentions this but needs more detail
- **Missing:** CMS Architecture does not address this requirement

### 5. CMS Data Model Requirements

For each spec with CMS dependencies, identify the data model needs:
- **Collections/Tables:** What entities need to be stored?
- **Relationships:** How do entities relate to each other?
- **Schema Requirements:** Required fields, types, validation
- **Access Patterns:** How will data be queried and accessed?
- **Volume Estimates:** Expected data volumes

Example:
```yaml
spec: repository-content-discovery-indexing
cms_data_model:
  collections:
    - name: repository_files
      fields:
        - file_path (string, required, indexed)
        - file_type (enum, required)
        - content_hash (string, required)
        - last_modified (timestamp, required)
        - metadata (json, optional)
      estimated_rows: 10000+

    - name: specifications
      fields:
        - spec_name (string, required, unique)
        - requirements_count (integer)
        - dependencies (array of spec references)
        - status (enum)
      estimated_rows: 108

  relationships:
    - specifications.dependencies -> specifications.spec_name (many-to-many)
    - repository_files.spec_id -> specifications.id (many-to-one)
```

## Deliverables

### 1. CMS Dependency Catalog

Create `.kiro/reports/cms-dependency-catalog.json` with:
- All specs with CMS dependencies (explicit and implicit)
- Specific CMS capabilities needed per spec
- Criticality and rationale for each dependency
- Current satisfaction status (covered/partial/missing)

### 2. CMS Capability Requirements Matrix

Create `.kiro/reports/cms-capability-requirements-matrix.md` showing which specs need which CMS capabilities.

### 3. CMS Data Model Consolidation

Create `.kiro/reports/cms-data-model-requirements.yaml` with:
- All required collections/tables
- Complete schema definitions
- Relationship mappings
- Access patterns and queries
- Volume estimates

### 4. CMS Feature Gap Report

Create `.kiro/reports/cms-feature-gap-report.md` identifying:
- CMS requirements not addressed in CMS Architecture spec
- Incomplete or under-specified CMS features
- Conflicting CMS requirements across specs
- Priority recommendations for CMS Architecture updates

### 5. CMS Criticality Analysis

Create `.kiro/reports/cms-criticality-analysis.md` analyzing:
- Which constellation layers have highest CMS dependency
- Critical path specs blocked by CMS availability
- Minimum viable CMS features for MVP constellation
- CMS implementation priority roadmap

## Validation Criteria

✅ All 108 specs analyzed for CMS dependencies
✅ Both explicit and implicit dependencies identified
✅ CMS capability requirements matrix complete
✅ Data model requirements documented for all CMS-dependent specs
✅ Gap analysis identifies missing CMS Architecture requirements
✅ Criticality analysis identifies CMS blocking dependencies

## CMS Dependency Classification

**CRITICAL (Blocking):** Spec cannot be implemented without this CMS capability
**HIGH (Degraded):** Spec can be partially implemented but with significant limitations
**MEDIUM (Workaround):** Spec can work around CMS absence but suboptimally
**LOW (Enhancement):** CMS provides additional value but not required
**NONE:** Spec has no CMS dependencies

## Output Format

**Primary Outputs:**
- `.kiro/reports/cms-dependency-catalog.json`
- `.kiro/reports/cms-capability-requirements-matrix.md`
- `.kiro/reports/cms-data-model-requirements.yaml`
- `.kiro/reports/cms-feature-gap-report.md`
- `.kiro/reports/cms-criticality-analysis.md`

**Summary Statistics:**
```
Total Specs Analyzed: 108
Specs with CMS Dependencies: X
  - CRITICAL: X specs
  - HIGH: X specs
  - MEDIUM: X specs
  - LOW: X specs

CMS Capabilities Usage:
  - Search & Discovery: X specs (Y critical)
  - Content Management: X specs (Y critical)
  - Integration: X specs (Y critical)
  - Analytics: X specs (Y critical)
  - Security: X specs (Y critical)
  - Performance: X specs (Y critical)

CMS Architecture Gaps: X missing features
Critical Path Blocked by CMS: [Yes/No]
Minimum Viable CMS Features: X capabilities
```

## Timeline

**Estimated Duration:** 6-8 hours
**Parallelization:** Can run in parallel with Phase 1a, 1b, 1d
**Dependencies:** None (read-only analysis)

## Success Metrics

- 100% of specs analyzed for CMS dependencies
- Both explicit and implicit dependencies captured
- Complete data model requirements documented
- All CMS gaps identified and prioritized
- Clear CMS implementation roadmap
