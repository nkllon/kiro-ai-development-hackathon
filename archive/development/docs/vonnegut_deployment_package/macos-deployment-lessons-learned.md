# macOS Deployment Lessons Learned

## The Problem: macOS Security Restrictions Break LaunchAgents

When deploying services on macOS, LaunchAgents run in a restricted environment that causes common deployment patterns to fail silently or with cryptic errors.

## What Goes Wrong

### 1. PATH Environment Issues
- **Problem**: LaunchAgents don't inherit your shell's PATH
- **Symptom**: `FileNotFoundError: [Errno 2] No such file or directory: 'cloudflared'`
- **Root Cause**: Commands like `cloudflared` aren't found because `/opt/homebrew/bin` isn't in PATH

### 2. Python Virtual Environment Issues
- **Problem**: LaunchAgents can't activate virtual environments the normal way
- **Symptom**: Import errors or wrong Python interpreter used
- **Root Cause**: Virtual environment activation scripts don't work in LaunchAgent context

### 3. Working Directory Assumptions
- **Problem**: LaunchAgents may not start in the expected directory
- **Symptom**: Relative paths fail, config files not found
- **Root Cause**: Working directory isn't guaranteed to be your project root

### 4. Environment Variable Inheritance
- **Problem**: LaunchAgents don't inherit your shell environment
- **Symptom**: Missing HOME, USER, or custom environment variables
- **Root Cause**: LaunchAgents run in minimal environment

## The Solution Pattern

### 1. Always Use Shell Script Wrappers
```bash
#!/bin/bash
# observatory_launcher.sh - Shell wrapper for LaunchAgent

# Explicitly set PATH to include all common locations
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Set required environment variables
export HOME="$HOME"
export USER="$USER"

# Change to project directory (absolute path)
cd "$(dirname "$0")/.."

# Set Python path for imports
export PYTHONPATH="$(pwd)"

# Use full path to Python executable
exec /usr/bin/python3 scripts/your_service.py
```

### 2. LaunchAgent Plist Best Practices
```xml
<!-- Use shell wrapper, not direct Python -->
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>/full/path/to/your/launcher.sh</string>
</array>

<!-- Always set working directory -->
<key>WorkingDirectory</key>
<string>/full/path/to/project</string>

<!-- Set minimal required environment -->
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>HOME</key>
    <string>/Users/username</string>
</dict>
```

### 3. Service Script Hardening
```python
# In your service scripts, use full paths
tunnel_cmd = [
    "/opt/homebrew/bin/cloudflared",  # Not just "cloudflared"
    "tunnel", "run", "observatory-tunnel"
]

# Or detect path dynamically
cloudflared_path = shutil.which('cloudflared') or '/opt/homebrew/bin/cloudflared'
```

## Testing Strategy

### 1. Test the Shell Wrapper Directly
```bash
# This should work before creating LaunchAgent
./scripts/observatory_launcher.sh
```

### 2. Test with Minimal Environment
```bash
# Simulate LaunchAgent environment
env -i PATH="/usr/bin:/bin" HOME="$HOME" ./scripts/observatory_launcher.sh
```

### 3. Check LaunchAgent Logs
```bash
# Always check these after installation
cat logs/service.out.log
cat logs/service.err.log
```

## Common macOS Gotchas

### Homebrew Path Changes
- **Intel Macs**: `/usr/local/bin/cloudflared`
- **Apple Silicon**: `/opt/homebrew/bin/cloudflared`
- **Solution**: Check both paths or use `which` command

### Python Path Issues
- **System Python**: `/usr/bin/python3`
- **Homebrew Python**: `/opt/homebrew/bin/python3`
- **Virtual Environment**: `/path/to/venv/bin/python`
- **Solution**: Use absolute paths, not `python` or `python3`

### File Permissions
- **Problem**: LaunchAgents can't access files without proper permissions
- **Solution**: Ensure scripts are executable (`chmod +x`) and readable

### Security & Privacy Settings
- **Problem**: macOS may block execution of downloaded scripts
- **Solution**: Remove quarantine attributes (`xattr -d com.apple.quarantine file`)

## The Deployment Checklist

Before creating any macOS LaunchAgent:

- [ ] Create shell script wrapper with explicit PATH
- [ ] Use absolute paths for all executables
- [ ] Set working directory explicitly
- [ ] Test wrapper script in minimal environment
- [ ] Use `/bin/bash` as ProgramArguments[0]
- [ ] Set required environment variables in plist
- [ ] Test LaunchAgent installation and check logs
- [ ] Verify service survives reboot

## Never Again Commands

```bash
# The right way to create a macOS service
./scripts/create_shell_wrapper.sh
./scripts/test_wrapper_minimal_env.sh
./scripts/install_launchagent.py
./scripts/test_service_after_reboot.sh
```

## Key Insight

**macOS LaunchAgents are not just "run this command on boot" - they're "run this command in a restricted sandbox with minimal environment."** 

Design for the sandbox, not for your comfortable shell environment.

---

*Never debug LaunchAgent PATH issues again. Always use shell wrappers.*