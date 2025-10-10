## Fix Invalid Makefile Targets

### Goal
Implement the remediation plan for the six failing targets identified in `reports/validate-targets-report.md`. Update the Makefile/doc references to match the actual recipes we want to support.

### Steps
1. Read the “Investigation” section in `reports/validate-targets-report.md` (added by the analysis agent).
2. For each invalid target:
   - Decide whether to restore the recipe, replace the command with a working alias, or remove the obsolete target.
   - Adjust docs that reference the invalid command.
3. Run `make validate-targets` to confirm the error count drops to zero (capture log).

### Constraints
Be deliberate; some recipes may need restoration from `archive/` rather than deletion. Document any targets you intentionally keep disabled (with reasons) back in the report.
