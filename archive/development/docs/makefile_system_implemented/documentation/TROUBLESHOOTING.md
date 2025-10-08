# Makefile System Troubleshooting

## Common Issues

### Target not found

**Problem:** `make: *** No rule to make target 'target-name'. Stop.`

**Solution:**
1. Check if target name is correct
2. Run `make help` to see available targets
3. Check if target is in the correct Makefile

### Variable not defined

**Problem:** `make: *** missing separator. Stop.`

**Solution:**
1. Check variable definition syntax
2. Ensure no spaces around `=`
3. Check for missing quotes

### Permission denied

**Problem:** `Permission denied` errors

**Solution:**
1. Check file permissions
2. Ensure scripts are executable
3. Check directory permissions
