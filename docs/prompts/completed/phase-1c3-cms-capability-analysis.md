# Phase 1c3: CMS Capability Analysis (60-75 min)

## Objective

Analyze what CMS capabilities (beyond data storage) are needed across all specs - APIs, workflows, permissions, hooks, webhooks.

## Task

### 1. Load Data Models

```bash
cat .kiro/reports/cms-data-models.yaml
```

### 2. Capability Extraction

For each spec with CMS dependencies, identify required capabilities:

**API Requirements:**
- REST endpoints needed
- GraphQL queries/mutations
- Real-time subscriptions
- Batch operations

**Workflow Requirements:**
- Data validation rules
- Automated actions
- State transitions
- Approval workflows

**Permission Requirements:**
- Role-based access control
- Field-level permissions
- Collection-level permissions
- Custom permission logic

**Integration Requirements:**
- Webhooks (outbound notifications)
- Hooks (data lifecycle events)
- External API integrations
- Event streaming

**Example - Repository Discovery Spec:**

```yaml
required_capabilities:
  api:
    - POST /items/repositories (create)
    - GET /items/repositories (list with search)
    - PATCH /items/repositories/:id (update)
    - GraphQL query repositories with filters

  workflows:
    - Auto-update last_scanned on file scan
    - Validate URL format before save
    - Trigger webhook on new repository

  permissions:
    - Read: authenticated users
    - Create: discovery-agent role
    - Update: discovery-agent role
    - Delete: admin only

  integrations:
    - Webhook to notify on new repository
    - Hook: after_create → trigger initial scan
```

### 3. Create Capability Matrix

```json
{
  "capability_matrix": {
    "REST API": {
      "specs_requiring": 45,
      "complexity": "medium"
    },
    "GraphQL": {
      "specs_requiring": 32,
      "complexity": "medium"
    },
    "Real-time Subscriptions": {
      "specs_requiring": 12,
      "complexity": "high"
    },
    "Webhooks": {
      "specs_requiring": 28,
      "complexity": "low"
    },
    "Custom Permissions": {
      "specs_requiring": 38,
      "complexity": "high"
    }
  }
}
```

## Deliverables

- `.kiro/reports/cms-capability-requirements.yaml` - All capability needs
- `.kiro/reports/cms-capability-matrix.json` - Matrix with complexity

## Timeline

**Duration:** 60-75 minutes
**Dependencies:** phase-1c2-cms-data-model-extraction
**Enables:** phase-5a-* (CMS consolidation)
