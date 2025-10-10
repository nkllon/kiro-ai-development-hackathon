# Test RCA Integration Troubleshooting Guide

## Common Issues and Solutions

### RCA Analysis Not Triggering

#### Issue: RCA doesn't run when tests fail
**Symptoms:**
- Tests fail but no RCA analysis starts
- No "🔍 RCA Analysis Starting..." message appears

**Possible Causes & Solutions:**

1. **RCA disabled by environment variable**
   ```bash
   # Check if RCA is disabled
   echo $RCA_ON_FAILURE
   
   # Enable RCA
   export RCA_ON_FAILURE=true
   make test
   ```

2. **Missing RCA engine dependencies**
   ```bash
   # Verify RCA engine is available
   python -c "from src.beast_mode.analysis.rca_engine import RCAEngine; print('RCA Engine available')"
   
   # If missing, reinstall dependencies
   make install
   ```

3. **Insufficient permissions**
   ```bash
   # Check file permissions
   ls -la src/beast_mode/testing/
   
   # Fix permissions if needed
   chmod +x beast
   ```

#### Issue: RCA starts but immediately fails
**Symptoms:**
- "🔍 RCA Analysis Starting..." appears
- Analysis fails with error message

**Solutions:**

1. **Check RCA engine health**
   ```bash
   # Test RCA engine directly
   ./beast rca-health-check
   
   # View detailed logs
   RCA_VERBOSE=true make test
   ```

2. **Verify pattern library**
   ```bash
   # Check pattern library exists
   ls -la patterns/test_rca_patterns.json
   
   # Rebuild if corrupted
   make rca-patterns-rebuild
   ```

### Performance Issues

#### Issue: RCA analysis takes too long
**Symptoms:**
- Analysis exceeds 30-second default timeout
- "Analysis timeout exceeded" messages

**Solutions:**

1. **Increase timeout for complex failures**
   ```bash
   # Increase timeout to 60 seconds
   RCA_TIMEOUT=60 make rca
   ```

2. **Reduce failure analysis scope**
   ```bash
   # Limit number of failures analyzed
   RCA_MAX_FAILURES=3 make test-with-rca
   ```

3. **Check system resources**
   ```bash
   # Monitor resource usage during RCA
   top -p $(pgrep -f "rca")
   
   # Check available memory
   free -h
   ```

#### Issue: Pattern matching is slow
**Symptoms:**
- Long delays during "Pattern matching..." phase
- Sub-second performance requirement not met

**Solutions:**

1. **Clean pattern library**
   ```bash
   # Remove outdated patterns
   make rca-patterns-clean
   
   # Optimize pattern library
   make rca-patterns-optimize
   ```

2. **Disable pattern learning temporarily**
   ```bash
   # Run without pattern learning
   RCA_PATTERN_LEARNING=false make rca
   ```

### Output and Reporting Issues

#### Issue: No RCA output displayed
**Symptoms:**
- RCA analysis completes but no results shown
- Silent failure after analysis

**Solutions:**

1. **Enable verbose output**
   ```bash
   # Get detailed output
   RCA_VERBOSE=true make rca
   ```

2. **Check output redirection**
   ```bash
   # Ensure output isn't redirected
   make test 2>&1 | tee test_output.log
   ```

3. **Generate explicit report**
   ```bash
   # Force report generation
   make rca-report
   ```

#### Issue: Malformed or incomplete reports
**Symptoms:**
- Reports missing sections
- JSON output is invalid
- Markdown formatting broken

**Solutions:**

1. **Verify report generator**
   ```bash
   # Test report generator directly
   python -c "from src.beast_mode.testing.rca_report_generator import RCAReportGenerator; print('Report generator available')"
   ```

2. **Check output format settings**
   ```bash
   # Generate with specific format
   make rca-report FORMAT=json
   make rca-report FORMAT=markdown
   ```

3. **Clear report cache**
   ```bash
   # Remove cached report data
   rm -f /tmp/rca_analysis_*
   ```

### Integration Issues

#### Issue: Make targets not found
**Symptoms:**
- "make: *** No rule to make target 'test-with-rca'"
- "make: *** No rule to make target 'rca'"

**Solutions:**

1. **Verify Makefile integration**
   ```bash
   # Check if testing.mk is included
   grep -n "testing.mk" Makefile
   
   # List available targets
   make help | grep rca
   ```

2. **Update Makefile includes**
   ```bash
   # Ensure proper include
   echo "include makefiles/testing.mk" >> Makefile
   ```

#### Issue: Environment variables not recognized
**Symptoms:**
- Environment variables don't affect RCA behavior
- Settings ignored during execution

**Solutions:**

1. **Check variable export**
   ```bash
   # Verify variables are exported
   export RCA_ON_FAILURE=true
   export RCA_TIMEOUT=45
   env | grep RCA
   ```

2. **Use inline variables**
   ```bash
   # Set variables inline with make command
   RCA_VERBOSE=true RCA_TIMEOUT=60 make rca
   ```

### Test Failure Detection Issues

#### Issue: Test failures not detected
**Symptoms:**
- Tests fail but RCA reports "No failures found"
- RCA analyzes wrong failures

**Solutions:**

1. **Check pytest output format**
   ```bash
   # Verify pytest output is parseable
   pytest --tb=short -v tests/ > test_output.txt
   cat test_output.txt
   ```

2. **Test failure detector directly**
   ```bash
   # Test failure detection
   python -c "
   from src.beast_mode.testing.test_failure_detector import TestFailureDetector
   detector = TestFailureDetector()
   print('Failure detector available')
   "
   ```

3. **Check test output parsing**
   ```bash
   # Enable debug mode for failure detection
   DEBUG_FAILURE_DETECTION=true make test
   ```

#### Issue: Incorrect failure analysis
**Symptoms:**
- RCA analyzes wrong root causes
- Suggested fixes don't match actual problems

**Solutions:**

1. **Verify test context extraction**
   ```bash
   # Check if test context is properly extracted
   RCA_VERBOSE=true make rca-task TASK=specific_failing_test
   ```

2. **Update pattern library**
   ```bash
   # Refresh patterns for better matching
   make rca-patterns-update
   ```

3. **Manual failure specification**
   ```bash
   # Provide specific failure context
   make rca-task TASK=test_name ERROR_TYPE=assertion
   ```

## Error Messages and Solutions

### "RCA Engine initialization failed"
**Cause:** RCA engine dependencies missing or corrupted
**Solution:**
```bash
# Reinstall Beast Mode dependencies
make clean
make install

# Verify installation
python -c "import src.beast_mode.analysis.rca_engine"
```

### "Pattern library not found or corrupted"
**Cause:** Pattern library file missing or invalid JSON
**Solution:**
```bash
# Rebuild pattern library
make rca-patterns-rebuild

# Verify pattern library
python -c "import json; json.load(open('patterns/test_rca_patterns.json'))"
```

### "Analysis timeout exceeded (30s)"
**Cause:** Complex failure analysis taking too long
**Solution:**
```bash
# Increase timeout
RCA_TIMEOUT=60 make rca

# Or reduce analysis scope
RCA_MAX_FAILURES=1 make rca
```

### "No test failures found to analyze"
**Cause:** Failure detection not working or no recent failures
**Solution:**
```bash
# Run tests first to generate failures
make test

# Then run RCA
make rca

# Or analyze specific test
make rca-task TASK=failing_test_name
```

### "Permission denied accessing pattern library"
**Cause:** File permission issues
**Solution:**
```bash
# Fix pattern library permissions
chmod 644 patterns/test_rca_patterns.json
chmod 755 patterns/

# Verify access
ls -la patterns/
```

## Debugging Techniques

### Enable Debug Logging
```bash
# Enable all debug output
DEBUG=true RCA_VERBOSE=true make test-with-rca

# Enable specific debug categories
DEBUG_RCA=true make rca
DEBUG_PATTERNS=true make rca
DEBUG_FAILURE_DETECTION=true make test
```

### Manual Component Testing
```bash
# Test individual components
python -c "
from src.beast_mode.testing.test_failure_detector import TestFailureDetector
from src.beast_mode.testing.rca_integration import TestRCAIntegrator
from src.beast_mode.testing.rca_report_generator import RCAReportGenerator

# Test each component
detector = TestFailureDetector()
integrator = TestRCAIntegrator()
reporter = RCAReportGenerator()
print('All components loaded successfully')
"
```

### Check System Dependencies
```bash
# Verify Python environment
python --version
which python

# Check required packages
pip list | grep -E "(pytest|beast-mode)"

# Verify make version
make --version
```

### Log Analysis
```bash
# Check RCA logs
tail -f logs/rca_analysis.log

# Check test execution logs
tail -f logs/test_execution.log

# Check pattern matching logs
tail -f logs/pattern_matching.log
```

## Performance Troubleshooting

### Memory Issues
```bash
# Monitor memory usage during RCA
watch -n 1 'ps aux | grep rca'

# Check for memory leaks
valgrind --tool=memcheck python -m pytest tests/test_rca_integration.py
```

### CPU Usage Issues
```bash
# Profile RCA execution
python -m cProfile -o rca_profile.stats -c "
from src.beast_mode.testing.rca_integration import TestRCAIntegrator
integrator = TestRCAIntegrator()
# Run analysis
"

# Analyze profile
python -c "
import pstats
p = pstats.Stats('rca_profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

### Disk I/O Issues
```bash
# Monitor disk usage during RCA
iotop -p $(pgrep -f rca)

# Check temporary file usage
du -sh /tmp/rca_*
```

## Getting Help

### Collect Diagnostic Information
```bash
# Generate diagnostic report
./beast rca-diagnostics > rca_diagnostics.txt

# Include system information
uname -a >> rca_diagnostics.txt
python --version >> rca_diagnostics.txt
make --version >> rca_diagnostics.txt
```

### Report Issues
When reporting issues, include:

1. **Error messages** (full stack traces)
2. **Environment details** (OS, Python version, make version)
3. **Configuration** (environment variables, config files)
4. **Steps to reproduce** (exact commands used)
5. **Expected vs actual behavior**
6. **Diagnostic report** (from above command)

### Community Resources
- **Documentation:** `docs/test-rca-integration.md`
- **Developer Guide:** `docs/test-rca-developer-guide.md`
- **Example Usage:** `examples/test_rca_integration_demo.py`
- **Test Suite:** `tests/test_rca_integration_*.py`

## Prevention

### Regular Maintenance
```bash
# Weekly pattern library cleanup
make rca-patterns-clean

# Monthly pattern library optimization
make rca-patterns-optimize

# Quarterly full system check
./beast rca-health-check --comprehensive
```

### Monitoring Setup
```bash
# Add RCA health monitoring to CI/CD
echo "make rca-health-check" >> .github/workflows/test.yml

# Set up log rotation for RCA logs
logrotate -f /etc/logrotate.d/rca-logs
```

### Best Practices
1. **Keep pattern library updated** with regular cleanup
2. **Monitor RCA performance** and adjust timeouts as needed
3. **Test RCA integration** in development environment before production
4. **Document custom patterns** and configurations
5. **Regular backup** of pattern library and configurations