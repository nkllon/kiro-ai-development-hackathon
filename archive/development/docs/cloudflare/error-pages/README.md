# Cloudflare Custom Error Pages

This directory contains custom error pages for Observatory infrastructure.

## Files

### `1033-enhanced.html` ⭐ RECOMMENDED

**Enhanced, playful, animated error page for when Observatory is down.**

**Features**:
- 🐭 Animated lab rat mascot with frazzled hair
- 💨 Smoke puffs and sparks animation
- 🧪 Wobbling lab equipment
- ⚡ Dynamic particle effects
- 🔄 Auto-refresh countdown (30s)
- 📊 Full technical transparency
- 🎮 Easter eggs (Konami code!)
- 📱 Fully responsive
- ♿ Accessible

**Message**: "Observatory Temporarily Down - We'll Be Back Shortly! No lab animals were harmed in this incident."

**File Size**: ~15KB
**Dependencies**: None (all inline)

### `deploy-error-page.py`

Python script to help deploy error pages to Cloudflare.

**Usage**:
```bash
# Set environment variables
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ZONE_ID="your-zone-id"

# Run deployment
python cloudflare/error-pages/deploy-error-page.py
```

## Quick Start

### Option 1: Manual Deployment (Recommended)

1. **Log in to Cloudflare Dashboard**
   - Visit: https://dash.cloudflare.com/
   - Select zone: `nkllon.com`

2. **Navigate to Custom Error Pages**
   - Click **Rules** → **Custom Error Responses**
   - (Or **Custom Pages** on older UI)

3. **Create New Error Response**
   - Error Code: `1033`
   - Method: Paste HTML or Upload File
   - Content: Copy from `1033-enhanced.html`
   - Save & Deploy

4. **Test**
   ```bash
   # Stop tunnel
   make tunnel-stop

   # Visit site
   open https://observatory.nkllon.com

   # Should see custom error page

   # Restart tunnel
   make tunnel-start
   ```

### Option 2: Automated Deployment

```bash
# Set environment variables (one time)
export CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
export CLOUDFLARE_ZONE_ID="your-zone-id"

# Run deployment script
python cloudflare/error-pages/deploy-error-page.py
```

**Note**: API deployment for 1033 errors may require manual configuration via dashboard.

## Design Philosophy

### Transparency First

Observatory is built on radical transparency, so our error page reflects this:

- **Full technical details** displayed in YAML format
- **Real error codes** shown (1033)
- **Actual infrastructure details** (tunnel ID, IP addresses, services)
- **System status** updated in real-time

### Playful & Human

We believe downtime messages should be:

- **Honest** about what happened
- **Light-hearted** to reduce stress
- **Informative** without being boring
- **Empathetic** to user frustration

Hence: lab rat + "no animals harmed" = memorable + on-brand

### Functional & Beautiful

The error page is not just decoration:

- **Auto-retry** every 30 seconds
- **Manual retry** button with loading state
- **Keyboard shortcuts** (spacebar to retry)
- **Links** to docs, support, GitHub
- **Service information** so users know what's affected

## Customization

### Update Contact Information

Edit these sections in `1033-enhanced.html`:

```html
<!-- Around line 380 -->
<a href="https://github.com/your-org/observatory/issues">📚 Documentation</a>
<a href="mailto:support@nkllon.com">💬 Contact Support</a>

<!-- Around line 540 -->
<a href="https://discord.gg/your-server">💬 Discord</a>
```

### Update Branding

Edit the color scheme:

```css
/* Around line 20 */
background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);

/* Around line 140 */
h1 {
    background: linear-gradient(135deg, #00d4ff 0%, #00a8cc 100%);
}
```

### Update Service Details

Edit technical details section:

```html
<!-- Around line 450 -->
<span class="key">affected_services:</span>
  - <span class="value">observatory.nkllon.com</span>
  - <span class="value">grafana.observatory.nkllon.com</span>
  - <span class="value">prometheus.observatory.nkllon.com</span>
```

### Change Auto-Retry Timing

Edit the countdown timer:

```javascript
// Around line 640
let countdown = 30;  // Change to desired seconds
```

## Testing

### Test Scenarios

1. **Full page load**
   ```bash
   make tunnel-stop
   open https://observatory.nkllon.com
   # Verify page loads and animations work
   ```

2. **Auto-refresh**
   ```bash
   # With tunnel stopped, wait 30 seconds
   # Page should auto-reload
   ```

3. **Manual retry**
   ```bash
   # Click "Retry Now" button
   # Should show loading spinner and reload
   ```

4. **Mobile responsive**
   ```bash
   # Open on mobile device or use browser dev tools
   # Verify layout works on small screens
   ```

5. **Easter eggs**
   ```bash
   # Type Konami code: ↑ ↑ ↓ ↓ ← → ← → B A
   # Lab rat should spin and grow

   # Press Spacebar
   # Should trigger retry
   ```

### Browser Compatibility

Tested on:
- ✅ Chrome 120+
- ✅ Firefox 121+
- ✅ Safari 17+
- ✅ Edge 120+
- ✅ Mobile Safari (iOS 17+)
- ✅ Chrome Mobile (Android 13+)

## Troubleshooting

### Error page not appearing

**Problem**: Still seeing default Cloudflare 1033 page

**Solutions**:
1. Verify custom error page is deployed and active in dashboard
2. Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)
3. Check that error code is exactly `1033`
4. Verify you have Pro plan or higher
5. Wait 5 minutes for edge cache to clear

### Page loads but animations don't work

**Problem**: Static page, no movement

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify browser supports CSS animations
3. Try disabling browser extensions
4. Test in incognito/private mode

### Auto-refresh not working

**Problem**: Page doesn't reload after 30 seconds

**Solutions**:
1. Check browser console for errors
2. Verify JavaScript is enabled
3. Check if service worker is interfering
4. Try manual refresh button instead

### Page looks broken on mobile

**Problem**: Layout issues on small screens

**Solutions**:
1. Clear mobile browser cache
2. Check viewport meta tag is present
3. Verify CSS media queries are working
4. Test in different mobile browsers

## Maintenance

### When to Update

- **Branding changes**: Logo, colors, fonts
- **Contact info changes**: Email, Discord, GitHub links
- **Service changes**: New services, retired services
- **Infrastructure changes**: New tunnel IDs, IP addresses
- **User feedback**: Clarity, helpfulness improvements

### Update Process

1. Edit `1033-enhanced.html` locally
2. Test in browser (open file directly)
3. Commit changes to git
4. Deploy via dashboard or script
5. Test with tunnel stopped
6. Document changes in this README

### Version History

- **v1.0** (2025-09-30): Initial playful lab rat design
  - Animated lab scene
  - Full transparency section
  - Auto-refresh functionality
  - Easter eggs

## Related Documentation

- [Full documentation and design rationale](../../docs/cloudflare-1033-custom-error-page.md)
- [Cloudflare Custom Errors Docs](https://developers.cloudflare.com/rules/custom-errors/)
- [Error 1033 Troubleshooting](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1033/)

## Questions?

- 🐛 Report issues: https://github.com/anthropics/kiro-ai-development-hackathon/issues
- 📧 Email: support@nkllon.com
- 💬 Discord: [Your Discord link]

---

**Made with 🔭 by the Observatory Team**