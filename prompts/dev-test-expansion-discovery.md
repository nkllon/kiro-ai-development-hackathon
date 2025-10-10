## Task: Map Missing Coverage for `make dev-test`

### Goal
Document which test suites remain disabled/missing compared to the historical 1,244-test baseline. Produce a checklist that shows:
- Suites currently executed (43 tests)
- Suites skipped or failing due to import errors (use `logs/dev_test_run.log` history)
- Dependencies required to re-enable each suite (modules, services, env vars)

### Suggested Commands (Read-Only)
- `cat logs/dev_test_run.log` to confirm current scope.
- `python3 -m pytest tests -m \"not slow\" --collect-only` (capture but do **not** run) to list available tests.
- `rg "skipif" tests/` to identify intentionally skipped suites.
- `ls archive/development/tests` to find archived counterparts.

### Constraints
- No file edits or pytest executions beyond `--collect-only`.
- Capture findings in notes; we will decide on actions later.

### Deliverable
Add a new section “Coverage Gap Analysis” to `reports/dev-test-report.md` that includes:
1. Table of test directories with status (enabled/disabled/blocked).
2. Dependencies needed to reactivate each blocked suite.
3. Recommended next steps ranked by effort vs. impact.
