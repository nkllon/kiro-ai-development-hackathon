# Restore Missing Beast Mode Modules

## Goal
Bring back framework modules that the latest cleanup moved to `archive/…` so the current `make dev-test` baseline stops failing during import/collection.

## Actions
Run the following checkout from the repo root (use the last commit before the cleanup, `2fc465fd`):

```bash
git checkout 2fc465fd -- \
  src/beast_mode/organization \
  src/beast_mode/self_refactoring \
  src/beast_mode/testing \
  src/beast_mode/tool_health \
  src/beast_mode/observatory/ai_consultation/visual_regression.py
```

If any command reports “pathspec did not match,” make sure you’re still on `rc1-patch` and that `2fc465fd` exists locally (`git fetch origin` if needed).

## After Restoring
1. Run `make dev-test > logs/dev_test_run.log 2>&1`.
2. If further ModuleNotFound errors appear, note the module and re-run `git checkout 2fc465fd -- <missing path>`.
3. Let the primary agent know once `make dev-test` completes (pass or fail) so we can capture the last-known-good baseline.***
