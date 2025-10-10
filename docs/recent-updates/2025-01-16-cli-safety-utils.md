# 2025-01-16 – CLI Safety Utilities Package Extraction

## Summary
- Extracted the emergency CLI validation and safe shell execution helpers into
the new `cli_safety` Python package located under `src/`.
- Added lightweight compatibility shims so existing imports (`emergency_cli_fix`
and `safe_shell_wrapper`) continue to function without change.
- Published packaging metadata under `packages/cli-safety-utils/` so the toolkit
can be released as the standalone `cli-safety-utils` distribution.
- Prepared the repository discovery core modules for publication via
`packages/repo-discovery-core/` with graceful fallbacks.
- Documented the packaging location and usage expectations.

## Release Checklist
- [x] Package metadata available in `packages/cli-safety-utils/pyproject.toml`
- [x] README prepared for PyPI publication
- [x] Compatibility shims keep legacy imports working
- [ ] PyPI publication (run `uv build --project packages/cli-safety-utils` when ready)

