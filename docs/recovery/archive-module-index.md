# Archive Module Index

## Purpose

This index tracks where archived Beast Mode modules are located and their contents. Use this when investigating historical implementations or recovering specific functionality.

## Archive Locations by Module

### Organization Module

**All Archive Locations** (21 total):
```
archive/development/vonnegut_deployment_package/beast_mode/organization/
archive/development/src/vonnegut_deployment_package/beast_mode/organization/
archive/development/vonnegut_container_deployment/src/beast_mode/organization/
archive/development/src/vonnegut_container_deployment/src/beast_mode/organization/
archive/development/poe_deployment_20251004_152642/src/beast_mode/organization/
archive/development/src/poe_deployment_20251004_152642/src/beast_mode/organization/
```

**Primary (Most Recent):**
- `archive/development/vonnegut_deployment_package/beast_mode/organization/`

**Contents:**
- `systematic_cleanup_engine*.py` (multiple core/services/part files)
- RDI-compliant implementation
- 60+ associated test files in tests/unit/beast_mode/organization/

**Purpose**: Systematic cleanup and organization management for the Beast Mode framework

### Self-Refactoring Module

**All Archive Locations** (21 total):
```
archive/development/vonnegut_deployment_package/beast_mode/self_refactoring/
archive/development/src/vonnegut_deployment_package/beast_mode/self_refactoring/
archive/development/vonnegut_container_deployment/src/beast_mode/self_refactoring/
archive/development/src/vonnegut_container_deployment/src/beast_mode/self_refactoring/
archive/development/poe_deployment_20251004_152642/src/beast_mode/self_refactoring/
archive/development/src/poe_deployment_20251004_152642/src/beast_mode/self_refactoring/
```

**Primary (Most Recent):**
- `archive/development/vonnegut_deployment_package/beast_mode/self_refactoring/`

**Contents:**
- `bootstrap_orchestrator*.py`
- `validation_engine*.py`
- `migration_manager*.py`
- `execution_strategy.py`
- `parallel_coordinator*.py`
- `dependency_manager.py`

**Purpose**: Self-refactoring and bootstrap orchestration for Beast Mode system evolution

### Testing Module

**All Archive Locations** (21 total):
```
archive/development/docs/vonnegut_deployment_package/testing/  (documentation)
archive/development/src/vonnegut_deployment_package/beast_mode/testing/
archive/development/src/vonnegut_container_deployment/src/beast_mode/testing/
archive/development/poe_deployment_20251004_152642/src/beast_mode/testing/  (missing in some locations)
archive/development/src/poe_deployment_20251004_152642/src/beast_mode/testing/
```

**Primary (Most Recent):**
- `archive/development/src/vonnegut_deployment_package/beast_mode/testing/`

**Note**: Testing module missing from `vonnegut_deployment_package` and `vonnegut_container_deployment` root locations

**Contents:**
- `error_handler*.py` (multiple layers: handlers, validation)
- `performance_monitor*.py`
- `rca_integration*.py` (Root Cause Analysis integration)
- RCA models, processing, and services

**Purpose**: Comprehensive testing framework with RCA integration and performance monitoring

### Tool Health Module

**All Archive Locations** (19 total):
```
archive/development/vonnegut_deployment_package/beast_mode/tool_health/
archive/development/src/vonnegut_deployment_package/beast_mode/tool_health/
archive/development/vonnegut_container_deployment/src/beast_mode/tool_health/
archive/development/src/vonnegut_container_deployment/src/beast_mode/tool_health/
archive/development/poe_deployment_20251004_152642/src/beast_mode/tool_health/
archive/development/src/poe_deployment_20251004_152642/src/beast_mode/tool_health/
```

**Primary (Most Recent):**
- `archive/development/vonnegut_deployment_package/beast_mode/tool_health/`

**Note**: Tool Health module missing from `poe_deployment` root location

**Contents:**
- `tool_health_manager*.py`
- `makefile_health_manager*.py`
- Service and validation layers

**Purpose**: Tool health monitoring and management, including Makefile health

## Related Documentation in Archive

### Design Documents
```
archive/development/docs/vonnegut_deployment_package/design/beast_mode_core/
  - organization_management_design.md
  - self_refactoring_design.md
```

### Requirements
```
archive/development/docs/vonnegut_deployment_package/requirements/beast_mode_core/
  - organization_management_requirements.md
  - self_refactoring_requirements.md
```

### Testing Documentation
```
archive/development/docs/vonnegut_deployment_package/testing/
  - Various testing specifications and guides
```

### Other Resources
```
archive/development/docs/vonnegut_deployment_package/other/misc/
  - unified_testing_rca_framework_spec.md
```

## Historical Test Evidence

Preserved test execution records:
```
archive/development/test_evidence/
  - 512 JSON files with test execution results
  - Historical baseline data
```

## Quick Access Commands

### List all archived modules
```bash
find archive/development -type f -path "*beast_mode/organization/*.py" | head -20
find archive/development -type f -path "*beast_mode/self_refactoring/*.py" | head -20
find archive/development -type f -path "*beast_mode/testing/*.py" | head -20
find archive/development -type f -path "*beast_mode/tool_health/*.py" | head -20
```

### Count files per module
```bash
find archive/development -path "*beast_mode/organization/*.py" | wc -l
find archive/development -path "*beast_mode/self_refactoring/*.py" | wc -l
find archive/development -path "*beast_mode/testing/*.py" | wc -l
find archive/development -path "*beast_mode/tool_health/*.py" | wc -l
```

### Search for specific functionality
```bash
# Find all files containing "systematic cleanup"
grep -r "systematic.*cleanup" archive/development/*/beast_mode/organization/

# Find RCA integration
grep -r "class.*RCA" archive/development/*/beast_mode/testing/

# Find bootstrap orchestrator
grep -r "class.*Bootstrap" archive/development/*/beast_mode/self_refactoring/
```

### Compare versions
```bash
# Compare organization module between two archive locations
diff -r archive/development/vonnegut_deployment_package/beast_mode/organization/ \
        archive/development/src/vonnegut_container_deployment/src/beast_mode/organization/

# Show which version is newer (by file modification time)
ls -lt archive/development/vonnegut_deployment_package/beast_mode/organization/*.py | head -5
ls -lt archive/development/src/vonnegut_container_deployment/src/beast_mode/organization/*.py | head -5
```

## File Name Patterns

### Core/Services Split Pattern
Many modules follow this pattern:
```
<module>_core.py              # Core functionality
<module>_core_core.py         # Even more core (nested)
<module>_services.py          # Service layer
<module>_services_core.py     # Service core
<module>_validation.py        # Validation layer
```

### Part Files Pattern
Large modules were split into numbered parts:
```
<module>_services_core_core_part_1.py
<module>_services_core_core_part_2.py
...
<module>_services_core_core_part_32.py
```

**Note**: Many `*_part_*.py` files were deleted in commit `4cf1dcee` ("Phase 2: Core Implementation Complete")

## Restoration Guidelines

### From Git History (Recommended)
```bash
# Restore from last known-good commit
git checkout 2fc465fd -- src/beast_mode/<module_name>
```

### From Archive (Alternative)
```bash
# Copy from archive (use with caution - may have different versions)
cp -r archive/development/vonnegut_deployment_package/beast_mode/<module_name> \
      src/beast_mode/
```

### Verification After Restoration
```bash
# Check imports
python3 -c "from src.beast_mode.<module_name> import *"

# Run associated tests
pytest tests/unit/beast_mode/<module_name>/ -v

# Check RDI compliance
python3 scripts/rdi_compliance_checker.py src/beast_mode/<module_name>/
```

## Archive Statistics

Generated: 2025-10-09

```bash
# Total Python files in archived beast_mode modules
find archive/development -path "*beast_mode/organization/*.py" -o \
                         -path "*beast_mode/self_refactoring/*.py" -o \
                         -path "*beast_mode/testing/*.py" -o \
                         -path "*beast_mode/tool_health/*.py" | wc -l
# Result: TBD (run command to populate)

# Total size of archived modules
du -sh archive/development/vonnegut_deployment_package/beast_mode/
# Result: TBD (run command to populate)
```

## Related Files

- **Restoration Guide**: `docs/recovery/beast-mode-module-restoration-guide.md`
- **File Relocations**: `docs/file_relocations.md`
- **RDI Analysis**: `docs/summary/analysis/RDI_ANALYSIS_REPORT.md`

## Maintenance

Update this index when:
- New modules are archived
- Archive structure changes
- Restoration procedures are updated
- New archive locations are created

**Last Updated**: 2025-10-09
**Maintained By**: Development Team

