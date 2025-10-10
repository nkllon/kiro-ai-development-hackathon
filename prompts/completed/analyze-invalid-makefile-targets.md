## Task: Investigate Invalid Makefile Targets (Read-Only)

### Goal
Understand why `make validate-targets` reports 6 invalid targets and 85 warnings. Produce a structured summary that maps each invalid target to its source file and probable cause (e.g., archived module, renamed dependency, typo).

### References
- `reports/validate-targets-report.md` – contains the raw validation output
- `logs/validate-targets-run.log` – full command log with stack traces
- `docs/recovery/archive-module-index.md` – archive locations for moved recipes

### Constraints
- **Do not modify any files**.
- Focus strictly on discovery and documentation.
- Prefer `rg`, `python3 -m pytest --collect-only`, or `make … --dry-run` for inspections.

### Deliverable
A Markdown snippet summarizing:
1. Each invalid target (name + file/line).
2. Root cause hypothesis (e.g., recipe moved to archive, missing include).
3. Suggested remediation options (restore recipe, update docs, remove target).

Add your findings to `reports/validate-targets-report.md` under a new “Investigation” section.
