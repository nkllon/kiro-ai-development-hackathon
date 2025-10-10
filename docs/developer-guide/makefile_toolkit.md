# Makefile Toolkit Module

The `src/makefile_toolkit` package wraps the automation utilities that previously lived as monolithic scripts under `scripts/`. Each component now exposes a reusable API and a thin CLI shim so agents can embed the behaviour in other repositories without copying entire files.

## Components
- `system_tester`: orchestrates the Makefile compliance suite and exposes `MakefileSystemTester` plus a `main()` CLI entrypoint.
- `safety_validator`: provides `MakefileSafetyValidator` for preflight checks and dangerous operation detection.
- `performance_optimizer`: implements `MakefilePerformanceOptimizer` with caching and execution strategy controls.

## Usage
Import the classes directly for programmatic control:

```python
from makefile_toolkit import MakefileSystemTester

summary = MakefileSystemTester().run_all_tests()
```

The legacy executables remain in `scripts/` but now delegate to the shared package:

```bash
python scripts/test_makefile_system.py --type unit
python scripts/makefile_safety_validator.py help
```

When extracting these tools into a standalone repository:
1. Move the `src/makefile_toolkit` package, preserving its module structure.
2. Update entry points (e.g., `pyproject.toml` console scripts) to call the module `main()` functions.
3. Copy any required docs (including this file) and reference them from the new README.

The package depends only on `src.rm_ddd` interfaces and core Python libraries, making it safe to lift without dragging the entire codebase.
