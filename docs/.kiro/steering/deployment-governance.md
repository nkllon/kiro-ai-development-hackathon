# Deployment Governance Steering Rules

## Core Principle

**"Every deployment must be systematic, validated, and leave the system in a better state than before."**

## Mandatory Pre-Deployment Checklist

Before deploying ANY changes:

### 1. Process Cleanup
- [ ] Kill all related existing processes
- [ ] Verify no port conflicts
- [ ] Clean up zombie containers/services

### 2. Cache Management
- [ ] Add version parameters to changed static assets
- [ ] Plan cache invalidation strategy
- [ ] Test cache busting effectiveness

### 3. Architecture Consistency
- [ ] Verify deployment method consistency (container OR host)
- [ ] Validate external service connectivity
- [ ] Check configuration alignment

### 4. Validation Plan
- [ ] Define success criteria
- [ ] Plan endpoint/feature validation
- [ ] Prepare rollback procedure

## Deployment Patterns

### ✅ Good Deployment Pattern
```bash
# 1. Clean slate
pkill -f "service_name"
docker stop $(docker ps -q) 2>/dev/null || true

# 2. Single deployment method
python scripts/start_service_production.py

# 3. Validate
curl -s http://localhost:8888/health
curl -s http://localhost:8888/new-endpoint

# 4. Cache bust if needed
# Update HTML with ?v=YYYYMMDD parameters
```

### ❌ Anti-Pattern to Avoid
```bash
# Multiple processes running
python start_service.py &
docker-compose up -d
python another_start_script.py

# No validation
# No cache busting
# Hope it works
```

## Mathematical Governance Application

### DAG-Based Deployment
1. **Dependencies**: Service A must start before Service B
2. **Validation**: Each step must complete successfully before next
3. **Rollback**: Reverse dependency order for cleanup

### Deterministic Outcomes
- Same deployment steps → Same results
- No "sometimes works" deployments
- Predictable failure modes

## Integration with Existing Systems

### Use Infrastructure Orchestrator
```bash
python scripts/infrastructure_governance_orchestrator.py --execute-next
```

### Apply Mathematical Validation
```bash
python scripts/infrastructure_task_dag_validator.py
```

### Follow Brownfield Safety
- Never break existing functionality
- Graceful degradation on failures
- Comprehensive error handling

## Lessons Learned Integration

When deployment issues occur:
1. **Document the lesson** in `docs/lessons-learned-*.md`
2. **Update requirements** in relevant specs
3. **Create steering rules** to prevent recurrence
4. **Enhance tooling** to automate prevention

## Success Metrics

- **Zero deployment surprises**: Deployments work as expected
- **Fast recovery**: Issues resolved in < 5 minutes
- **Consistent outcomes**: Same steps produce same results
- **Clear diagnostics**: Problems are immediately obvious

## Emergency Procedures

### When Deployment Goes Wrong
1. **Stop everything**: `pkill -f "all_services"`
2. **Assess damage**: Check what's running, what's broken
3. **Single path recovery**: Use ONE deployment method
4. **Validate systematically**: Test each component
5. **Document lessons**: Update steering rules

### Ghostbusters Protocol
When you don't know what's running:
1. **Scan all processes**: `ps aux | grep service_name`
2. **Check all ports**: `lsof -i :PORT`
3. **Hunt containers**: `docker ps -a`
4. **Kill systematically**: Clean slate approach
5. **Rebuild systematically**: Single deployment path

---

*These rules are derived from actual deployment failures and should be followed religiously to prevent chaos.*