# Atomic Pattern Quick Reference Card

## The Magic Command ✨
```bash
python src/spec_framework/cli/prepare_spec_cli.py prepare [spec_path] | tee logfile.log
```

## Generated Scripts 📜

### 1. Prelaunch Validation
```bash
python3 scripts/[spec]/[spec]_prelaunch_check_v2.py
```
**Purpose**: Validate infrastructure readiness

### 2. Launch Execution  
```bash
python3 scripts/[spec]/[spec]_launch_v2.py
```
**Purpose**: Execute with parallel DAG orchestration

### 3. Background Management
```bash
./scripts/[spec]/[spec]_background_launch_v2.sh run     # Start
./scripts/[spec]/[spec]_background_launch_v2.sh status  # Check
./scripts/[spec]/[spec]_background_launch_v2.sh logs    # View
./scripts/[spec]/[spec]_background_launch_v2.sh stop    # Stop
```
**Purpose**: Long-running execution management

## Common Flags 🚩
- `--allow-warnings` - Proceed despite warnings
- `--strategy aggressive` - Maximum parallelization  
- `--output [dir]` - Custom output directory

## Success Indicators ✅
- 90%+ efficiency gain
- 95%+ validation confidence
- All 3 scripts generated
- Complete audit trail
- No critical failures

## Troubleshooting 🔧
1. Check all spec files exist
2. Verify Beast Mode infrastructure
3. Ensure sufficient resources
4. Look for circular dependencies
5. Validate Python environment

## Quick Diagnostics 🩺
```bash
# Check pattern status
python src/spec_framework/cli/prepare_spec_cli.py status [spec_path]

# Analyze specification
python src/spec_framework/cli/prepare_spec_cli.py analyze [spec_path]

# Test Beast Mode
python -c "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule"
```

## Example Usage 🎯
```bash
# Simple API example
python src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/example-simple-api | tee simple-prep.log

# Complex system example  
python src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/example-complex-system | tee complex-prep.log
```

## Makefile Integration 🔨
```makefile
prepare-spec:
	python src/spec_framework/cli/prepare_spec_cli.py prepare .kiro/specs/$(SPEC) | tee logs/$(SPEC)-prep.log

execute-spec:
	python3 scripts/$(SPEC)/$(SPEC)_launch_v2.py
```

---
**Remember**: Always use `| tee logfile.log` for complete audit trails! 📝