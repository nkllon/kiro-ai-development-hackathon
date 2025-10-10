## Expand the Dev Test Suite

### Objective
Re-enable the highest-value test suites that are currently skipped/failing in `make dev-test`. Use the “Coverage Gap Analysis” section from `reports/dev-test-report.md` to prioritize.

### Suggested Order
1. Restore missing observability/directus tests (now harmonized).
2. Reintroduce `tool_health` and `organization` suites if dependencies permit.
3. Tackle archive-based packages (vonnegut/poe) only if necessary.

### Steps
1. Restore/stub any modules identified as missing from the discovery run.
2. Update `Makefile` `dev-test` target to include the selected directories.
3. Run `make dev-test` and capture the log (`logs/dev_test_run-expanded.log`).
4. Update `reports/dev-test-report.md` with the new results and remaining TODOs.
