# Cloudflare Dashboard Automation for Custom Error Pages

This automation solves the problem that Cloudflare doesn't provide API access for Custom Error Pages - they must be deployed manually through the dashboard. The Playwright automation handles this manual process programmatically.

## Why This Automation?

The existing deployment scripts (`deploy_cloudflare_error_pages.py`, `cloudflare-error-pages-cli.py`) acknowledge that:
- Cloudflare API doesn't support Custom Error Pages
- Manual dashboard deployment is required
- This is a significant limitation for automation

This Playwright solution automates the manual browser interactions needed to deploy error pages.

## Quick Start

### 1. Setup Dependencies
```bash
./deploy-error-page.sh --setup
```

### 2. Deploy Error Page
```bash
./deploy-error-page.sh --deploy
```

## Detailed Usage

### Prerequisites
- **Cloudflare Pro Plan** or higher (required for Custom Error Pages)
- **Python 3.7+** installed
- **Valid Cloudflare account** with access to nkllon.com zone
- **HTML error page file** at `cloudflare/error-pages/1033-enhanced.html`

### Manual Installation
```bash
# Install dependencies
pip3 install -r requirements-automation.txt

# Install Playwright browsers
python3 -m playwright install chromium
```

### Direct Script Usage
```bash
# Interactive mode (prompts for password)
python3 cloudflare-dashboard-automation.py \
    --email your@email.com \
    --interactive \
    --zone nkllon.com \
    --error-code 1033 \
    --html-file cloudflare/error-pages/1033-enhanced.html

# With password (less secure)
python3 cloudflare-dashboard-automation.py \
    --email your@email.com \
    --password your_password \
    --zone nkllon.com

# Headless mode (no browser UI)
python3 cloudflare-dashboard-automation.py \
    --email your@email.com \
    --interactive \
    --headless
```

## How It Works

The automation performs these steps:

1. **🌐 Login to Cloudflare Dashboard**
   - Navigates to https://dash.cloudflare.com/login
   - Enters credentials
   - Handles 2FA if enabled (waits for user completion)

2. **🎯 Navigate to Zone**
   - Finds and clicks the specified zone (nkllon.com)
   - Handles search if zone not immediately visible

3. **🛠️ Find Custom Error Pages**
   - Navigates to Rules → Custom Error Responses
   - Fallback navigation attempts if layout differs

4. **📄 Deploy Error Page**
   - Clicks "Create custom error response"
   - Selects Error 1033
   - Chooses "Custom HTML" option
   - Pastes HTML content from file
   - Previews (optional)
   - Saves deployment

5. **✅ Verify Deployment**
   - Confirms deployment success
   - Checks for "Active" status

## Browser Automation Features

### Visual Mode (Default)
- Opens Chrome browser window
- You can watch the automation in real-time
- Useful for debugging and first-time setup
- Handles 2FA prompts gracefully

### Headless Mode
- Runs without browser UI
- Faster execution
- Good for CI/CD pipelines
- Use `--headless` flag

### Slow Motion
- Slows down automation for better visibility
- Default: 1000ms delay between actions
- Customize with `--slow-mo` parameter

## Error Handling

The automation handles common scenarios:

### Login Issues
- ✅ 2FA prompts (waits for manual completion)
- ✅ Different login page layouts
- ✅ Slow loading times

### Navigation Issues
- ✅ Different dashboard layouts
- ✅ Zone search when not immediately visible
- ✅ Multiple paths to Custom Error Pages

### Plan Limitations
- ❌ Detects if Custom Error Pages not available
- 💡 Provides clear error message about Pro plan requirement

## Testing the Deployment

After successful deployment:

1. **Stop your tunnel** (this triggers 1033 errors)
   ```bash
   make tunnel-stop
   # or
   pkill -f cloudflared
   ```

2. **Test the domains**
   - Visit https://observatory.nkllon.com
   - Visit https://grafana.observatory.nkllon.com
   - Visit https://prometheus.observatory.nkllon.com

3. **Verify custom error page**
   - Should see Observatory branding
   - Should see animated lab rat 🐭
   - Should see 30-second countdown
   - Should see "Retry Now" button
   - Should see technical details in YAML format

4. **Test interactive features**
   - Click "Retry Now" button
   - Press spacebar to retry
   - Try Konami code: ↑↑↓↓←→←→BA

5. **Restore service**
   ```bash
   make tunnel-start
   ```

## Troubleshooting

### "Could not find Custom Error Pages"
- Ensure you have Cloudflare Pro plan or higher
- Check zone permissions
- Try manual navigation to verify feature availability

### "Login failed"
- Verify email/password combination
- Check for 2FA requirements
- Ensure account has zone access

### "HTML file not found"
- Verify `cloudflare/error-pages/1033-enhanced.html` exists
- Check file permissions
- Ensure path is correct

### Browser Issues
- Update Chrome/Chromium: `python3 -m playwright install chromium`
- Try headless mode: `--headless`
- Check system permissions for browser automation

## Integration with Existing Scripts

This automation integrates with the existing deployment ecosystem:

### Validation
- Uses same validation from `deploy_cloudflare_error_pages.py`
- Checks file size, required elements
- Maintains same quality standards

### CLI Compatibility
- Similar command-line interface to `cloudflare-error-pages-cli.py`
- Same configuration options
- Compatible output formats

### Monitoring
- Works with existing monitoring setup
- Cloudflare Analytics still track error page performance
- Same success metrics apply

## Security Considerations

### Credential Handling
- ✅ Interactive password prompt (recommended)
- ⚠️ Command-line password (less secure)
- ❌ No password storage or logging

### Browser Security
- ✅ Uses official Playwright/Chromium
- ✅ No external dependencies in automation
- ✅ Respects browser security policies

### Network Security
- ✅ Only connects to official Cloudflare domains
- ✅ No proxy or MITM requirements
- ✅ Standard HTTPS connections

## Future Enhancements

### Planned Features
- [ ] Multiple error code deployment in single run
- [ ] Bulk zone deployment across multiple domains
- [ ] Screenshot capture for deployment verification
- [ ] Integration with CI/CD pipelines (GitHub Actions)
- [ ] Rollback automation for error page updates

### API Migration
When Cloudflare eventually provides API support for Custom Error Pages:
- The automation can be updated to prefer API calls
- Browser automation becomes fallback method
- Same CLI interface maintained for compatibility

## Files Created

This automation adds these files to your project:

```
cloudflare-dashboard-automation.py    # Main Playwright automation script
requirements-automation.txt           # Python dependencies
deploy-error-page.sh                 # Convenience wrapper script
CLOUDFLARE_AUTOMATION_README.md      # This documentation
```

## Support

For issues with this automation:
1. Check the troubleshooting section above
2. Verify your Cloudflare plan supports Custom Error Pages
3. Test manual deployment through dashboard first
4. Review browser console for JavaScript errors

The automation is designed to be robust and handle various dashboard layouts, but Cloudflare may update their UI over time.