# Phase 5a1: CMS Data Model Consolidation (90-120 min)

## Objective

Consolidate all CMS data model requirements from Phase 2 requirements into comprehensive schema definition.

## Task

### 1. Load All CMS Analyses

```bash
cat .kiro/reports/cms-data-models.yaml
cat .kiro/reports/cms-capability-requirements.yaml
```

### 2. Scan Phase 2 Requirements for CMS Needs

```bash
find .kiro/specs -name "requirements.md" -exec grep -l "CMS Requirements" {} \;
```

### 3. Extract All Data Models

For each spec with CMS requirements, extract:
- Collection definitions
- Field specifications
- Relationships
- Indexes
- Validation rules

### 4. Consolidate and Deduplicate

Merge collections that serve same purpose:
- Multiple specs might define similar "metrics" collections
- Merge into single comprehensive collection
- Document which specs use each collection

### 5. Create Master Schema

```yaml
cms_master_schema:
  collections:
    repositories:
      fields:
        - {name: id, type: uuid, primary: true}
        - {name: url, type: string, index: true, unique: true}
        - {name: name, type: string}
        - {name: description, type: text}
        - {name: discovered_at, type: timestamp}
        - {name: last_scanned, type: timestamp}
      relationships:
        - {type: has_many, collection: files}
        - {type: has_many, collection: dependencies}
      used_by:
        - repository-content-discovery-indexing
        - repository-constellation

    # Continue for all collections
```

## Deliverables

- `.kiro/specs/cms-architecture/cms-master-schema.yaml` - Complete schema
- `.kiro/reports/cms-collection-usage-matrix.json` - Which specs use which collections

## Timeline

**Duration:** 90-120 minutes
**Dependencies:** Phase 2 complete, phase-1c3-cms-capability-analysis
**Enables:** phase-5a2-cms-api-consolidation
