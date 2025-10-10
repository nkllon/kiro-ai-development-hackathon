# CLI Safety Utilities

This package bundles the hardened shell-safety helpers extracted from the
Kiro AI Development Hackathon toolkit. It provides:

- `EmergencyCLIFix`: static validation and sanitisation helpers that prevent
  quote-related deadlocks and partial commands from reaching the shell.
- `SafeShellWrapper`: a minimal wrapper around `subprocess.run` that always
  validates and sanitises commands before execution.

## Installation

```bash
pip install cli-safety-utils
```

## Usage

```python
from cli_safety import EmergencyCLIFix, safe_run

ok, stdout, stderr = safe_run("echo 'hello'")
```

The utilities are intentionally dependency-light and support Python 3.9+
projects that need robust command execution from agents or automation flows.

