# Anti-Duplication System User Guide

## Overview

The Anti-Duplication System prevents duplicate development by enforcing mandatory capability discovery before any new development begins. This system ensures that developers are aware of existing solutions and make informed decisions about whether to build new functionality or enhance existing capabilities.

## How It Works

### 1. Capability Registry
- **Automated Scanning**: Scans your codebase every 4 hours to maintain an up-to-date inventory
- **Semantic Search**: Finds existing capabilities based on intent, not just keywords
- **Real-time Updates**: Registry stays fresh with automatic rescanning

### 2. Discovery Process
- **Problem Analysis**: Analyzes your development request to understand the problem domain
- **Solution Discovery**: Finds existing solutions that might address your needs
- **Overlap Analysis**: Calculates similarity between proposed and existing functionality
- **Gap Identification**: Identifies areas where enhancement might be better than new development

### 3. Development Gate
- **Validation**: Ensures discovery is completed before development proceeds
- **Decision Making**: Approves, blocks, or requires review based on overlap analysis
- **Audit Trail**: Maintains complete record of all decisions for compliance

## Getting Started

### Installation

1. **Install the system**:
   ```bash
   python scripts/install_anti_duplication_hooks.py
   ```

2. **Initial codebase scan**:
   ```python
   from src.anti_duplication import CapabilityRegistry
   
   registry = CapabilityRegistry(".")
   results = registry.scan_codebase()
   print(f"Found {results['capabilities_found']} capabilities")
   ```

### Basic Usage

#### 1. Before Starting Development

```python
from src.anti_duplication import CapabilityDiscoveryEngine, CapabilityRegistry

# Initialize the system
registry = CapabilityRegistry(".")
discovery_engine = CapabilityDiscoveryEngine(registry)

# Discover existing solutions
inventory = discovery_engine.discover_existing_solutions(
    "user authentication and authorization"
)

print(f"Found {len(inventory.existing_solutions)} existing solutions:")
for solution in inventory.existing_solutions:
    print(f"  - {solution.name} ({solution.file_path})")
```

#### 2. Analyze Overlap

```python
# Analyze overlap with your proposed solution
proposed_solution = "Build JWT-based authentication service with role management"
overlap_analysis = discovery_engine.assess_functional_overlap(
    proposed_solution, inventory
)

print(f"Similarity score: {overlap_analysis.functional_similarity_score:.2f}")
print(f"Recommendation: {overlap_analysis.recommendation.value}")

if overlap_analysis.overlapping_capabilities:
    print("Similar existing capabilities:")
    for cap in overlap_analysis.overlapping_capabilities:
        print(f"  - {cap.existing_solution.name}: {cap.similarity_score:.2f} similar")
```

#### 3. Generate Discovery Attestation

```python
from src.anti_duplication.models import DevelopmentRequest

# Create development request
request = DevelopmentRequest(
    problem_statement="Need user authentication system",
    proposed_solution="JWT-based auth service with roles",
    requester="developer_name"
)

# Generate attestation
attestation = discovery_engine.generate_discovery_attestation(
    request, inventory, overlap_analysis,
    justification="Existing solutions don't support our specific role hierarchy"
)

print(f"Attestation valid: {attestation.is_valid}")
print(f"Attestation ID: {attestation.attestation_id}")
```

## Development Workflow Integration

### Git Hooks

The system automatically installs git hooks that validate your commits:

- **Pre-commit**: Checks for discovery attestation on new functionality
- **Pre-push**: Final validation before pushing to remote

### CI/CD Integration

#### GitHub Actions

The system creates a GitHub Actions workflow that:
- Analyzes pull requests for duplicate development
- Comments on PRs with analysis results
- Blocks merging if high overlap is detected

#### Manual CI Integration

For other CI systems, use the CLI:

```bash
# Validate a pull request
python -m anti_duplication.ci_integration --validate-pr

# With specific files
python -m anti_duplication.ci_integration --validate-pr --pr-files file1.py file2.py
```

## Understanding Results

### Similarity Scores

- **0.9-1.0**: Extremely high similarity - likely duplicate
- **0.7-0.9**: High similarity - consider enhancement instead
- **0.5-0.7**: Moderate similarity - review existing solutions
- **0.0-0.5**: Low similarity - new development likely justified

### Recommendations

- **BLOCK**: Don't proceed - use existing solution
- **ENHANCE**: Enhance existing capability instead of building new
- **REVIEW**: Manual review required before proceeding
- **PROCEED**: Low overlap - new development justified

### Discovery Completeness

- **80-100%**: Comprehensive discovery - high confidence in results
- **60-80%**: Good discovery - results are reliable
- **40-60%**: Moderate discovery - consider additional research
- **0-40%**: Limited discovery - may have missed existing solutions

## Best Practices

### 1. Write Clear Problem Statements

**Good**: "Need real-time WebSocket communication for live chat with message persistence and user presence tracking"

**Bad**: "Need WebSocket stuff"

### 2. Provide Detailed Proposed Solutions

**Good**: "Build FastAPI WebSocket handler with Redis for message queuing, PostgreSQL for persistence, and JWT authentication"

**Bad**: "Make chat work"

### 3. Justify New Development

When overlap is detected, provide clear justification:
- What specific requirements aren't met by existing solutions?
- Why enhancement isn't feasible?
- What unique value does the new solution provide?

### 4. Regular Registry Maintenance

- Registry automatically scans every 4 hours
- Force rescan after major changes: `registry.scan_codebase()`
- Monitor registry health: `registry.validate_freshness()`

## Troubleshooting

### Common Issues

#### "Registry is stale" Error

```python
# Force registry rescan
registry = CapabilityRegistry(".")
results = registry.scan_codebase()
print(f"Rescanned {results['files_scanned']} files")
```

#### "Discovery attestation invalid" Error

Check attestation validity:
```python
print(f"Completeness score: {attestation.discovery_completeness_score}")
print(f"Overlap analysis completed: {attestation.overlap_analysis_completed}")
print(f"Enhancement justified: {attestation.enhancement_vs_new_justified}")
```

#### Git Hook Failures

Bypass for emergencies (triggers mandatory review):
```bash
git commit --no-verify -m "Emergency fix - review required"
```

### Performance Issues

#### Slow Registry Scanning

- Exclude unnecessary directories in `.gitignore`
- Registry automatically skips common build/cache directories
- Consider running scans during off-hours

#### Slow Semantic Search

- Registry uses SQLite FTS for fast text search
- Search performance improves as registry learns from usage
- Consider more specific search terms

## Emergency Procedures

### Emergency Override

When critical issues require bypassing the system:

```python
from src.anti_duplication import DevelopmentGate

gate = DevelopmentGate(discovery_engine)
decision = gate.emergency_override(
    request,
    override_reason="Critical production outage requires immediate fix",
    override_authority="incident_commander"
)
```

**Important**: Emergency overrides trigger mandatory review within 48 hours.

### System Bypass

For git operations:
```bash
# Bypass pre-commit hook
git commit --no-verify -m "Emergency commit"

# Bypass pre-push hook  
git push --no-verify
```

**Warning**: Bypasses are logged and require post-incident review.

## Monitoring and Metrics

### System Health

```python
# Check registry health
freshness = registry.validate_freshness()
print(f"Registry fresh: {freshness['is_fresh']}")
print(f"Last scan: {freshness['last_scan']}")
print(f"Capabilities: {freshness['capabilities_count']}")

# Check gate statistics
stats = gate.get_gate_statistics()
print(f"Total decisions: {stats['total_decisions']}")
print(f"Blocked: {stats['blocked']}")
print(f"Emergency overrides: {stats['emergency_overrides']}")
```

### Audit Trail

```python
# Get audit trail for specific request
audit_entries = gate.get_audit_trail(request_id)
for entry in audit_entries:
    print(f"{entry.timestamp}: {entry.event_type} by {entry.actor}")

# Get all audit entries
all_entries = gate.get_audit_trail()
print(f"Total audit entries: {len(all_entries)}")
```

## Configuration

### Registry Configuration

```python
# Custom configuration
registry = CapabilityRegistry(
    codebase_root="./src",
    db_path="./custom_registry.db"
)

# Custom similarity threshold
discovery_engine.similarity_threshold = 0.8  # Default: 0.7
```

### Gate Configuration

```python
# Custom gate settings
gate.require_manual_review_threshold = 0.9  # Default: 0.8
gate.emergency_override_enabled = False     # Default: True
```

## Support

### Getting Help

1. **Check the logs**: System logs all operations with detailed error messages
2. **Validate system health**: Use health check functions to identify issues
3. **Review audit trail**: Check audit logs for decision history
4. **Emergency procedures**: Use override capabilities for critical situations

### Common Questions

**Q: Can I disable the system temporarily?**
A: Use `--no-verify` for git operations, but this triggers mandatory review.

**Q: How accurate is the similarity detection?**
A: Current implementation uses text-based similarity. Accuracy improves with better problem descriptions.

**Q: What happens if I ignore the recommendations?**
A: System logs all decisions. Ignoring recommendations may trigger review processes.

**Q: Can I customize the similarity threshold?**
A: Yes, adjust `discovery_engine.similarity_threshold` (default: 0.7).

This system is designed to prevent duplicate development while maintaining developer productivity. When in doubt, the system errs on the side of discovery and collaboration rather than blocking development.