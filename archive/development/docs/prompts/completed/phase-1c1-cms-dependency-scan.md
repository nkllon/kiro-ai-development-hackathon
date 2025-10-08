# Phase 1c1: CMS Dependency Scan (60-90 min)

## Objective

Scan all specifications to identify explicit and implicit CMS dependencies and requirements.

## Task

### 1. Scan All Spec Files

```bash
find .kiro/specs -name "*.md" -type f
```

### 2. Search for CMS References

Search for keywords:
- "Directus"
- "CMS"
- "content management"
- "content storage"
- "data model"
- "schema"
- "collections"
- "fields"
- "relationships"

### 3. Categorize Dependencies

**Explicit Dependencies:**
- Direct mentions of Directus/CMS
- References to CMS collections
- CMS API requirements
- Schema definitions

**Implicit Dependencies:**
- Data persistence needs
- Content management requirements
- Schema evolution needs
- Relationship management

### 4. Create Dependency Catalog

```json
{
  "cms_dependencies": {
    "explicit": {
      "repository-content-discovery-indexing": {
        "collections": ["repositories", "files", "dependencies"],
        "requirements": ["file indexing", "search", "metadata"]
      },
      "observatory": {
        "collections": ["metrics", "events", "agents"],
        "requirements": ["real-time updates", "time-series"]
      }
    },
    "implicit": {
      "spec-framework": {
        "needs": ["spec metadata", "version tracking"],
        "potential_collections": ["specifications", "versions"]
      }
    }
  }
}
```

## Deliverables

- `.kiro/reports/cms-dependency-catalog.json` - All CMS dependencies
- `.kiro/reports/cms-dependency-summary.md` - Analysis and counts

## Timeline

**Duration:** 60-90 minutes
**Dependencies:** phase-1a-constellation-inventory
**Enables:** phase-1c2-cms-data-model-extraction
