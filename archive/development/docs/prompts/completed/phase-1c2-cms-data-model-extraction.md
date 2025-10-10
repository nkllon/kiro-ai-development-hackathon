# Phase 1c2: CMS Data Model Extraction (75-105 min)

## Objective

Extract and formalize the data model requirements for all CMS-dependent specs, creating comprehensive collection and field definitions.

## Task

### 1. Load CMS Dependency Catalog

```bash
cat .kiro/reports/cms-dependency-catalog.json
```

### 2. Extract Data Models

For each spec with CMS dependencies, extract:

**Collection Requirements:**
- Collection name
- Primary fields
- Relationships to other collections
- Indexes needed
- Access patterns

**Example for repository-content-discovery-indexing:**

```yaml
collections:
  repositories:
    fields:
      - name: id
        type: uuid
        primary_key: true
      - name: url
        type: string
        index: true
      - name: name
        type: string
      - name: description
        type: text
      - name: discovered_at
        type: timestamp
      - name: last_scanned
        type: timestamp
    relationships:
      - has_many: files
      - has_many: dependencies

  files:
    fields:
      - name: id
        type: uuid
      - name: repository_id
        type: uuid
        foreign_key: repositories.id
      - name: path
        type: string
      - name: content_hash
        type: string
      - name: size
        type: integer
    relationships:
      - belongs_to: repository
```

### 3. Identify Shared Collections

Which collections are used by multiple specs?
- `metrics` (used by observatory, monitoring, performance)
- `users` (used by auth, permissions, audit)
- `events` (used by logging, analytics, monitoring)

### 4. Create Data Model Catalog

```yaml
cms_data_models:
  core_collections:
    - repositories
    - files
    - specifications
    - metrics
    - events
    - users

  spec_specific_collections:
    - agent_executions (beast-mode)
    - tunnel_configs (cloudflare)
    - discord_messages (discord-bot)

  shared_collections:
    - metrics (15 specs)
    - events (12 specs)
    - users (8 specs)
```

## Deliverables

- `.kiro/reports/cms-data-models.yaml` - Complete data model catalog
- `.kiro/reports/cms-collection-dependencies.json` - Collection relationship graph

## Timeline

**Duration:** 75-105 minutes
**Dependencies:** phase-1c1-cms-dependency-scan
**Enables:** phase-1c3-cms-capability-analysis
