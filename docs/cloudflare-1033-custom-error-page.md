# Cloudflare 1033 Custom Error Page - Documentation & Design

## Executive Summary

**Problem**: Observatory is currently down, showing Cloudflare Error 1033 (Tunnel Error) with a generic, unfriendly error page.

**Goal**: Create a professional, branded custom error page that provides useful information to visitors when the tunnel is unavailable.

**Approach**: Use Cloudflare's Custom Error Pages feature (available on paid plans) to replace the default 1033 error page with a custom HTML page.

---

## Understanding Error 1033

### What is Error 1033?

Error 1033 indicates that a Cloudflare Tunnel is not connected to Cloudflare's edge network. Specifically:

- **Meaning**: The tunnel daemon (`cloudflared`) is not running or not reachable
- **User Impact**: The backend service (Observatory) is completely unavailable
- **Typical Causes**:
  - `cloudflared` daemon stopped or crashed
  - Network connectivity issues between tunnel and Cloudflare edge
  - Tunnel configuration errors
  - Local service (Observatory on port 8888) not responding

### Current Tunnel Configuration

Based on your `~/.cloudflared/config.yml`:

```yaml
tunnel: observatory-tunnel
credentials-file: ~/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: prometheus.observatory.nkllon.com
    service: http://192.168.1.101:9090

  - hostname: grafana.observatory.nkllon.com
    service: http://192.168.1.101:3000

  - hostname: observatory.nkllon.com
    service: http://192.168.1.101:8888

  - service: http_status:404
```

**Tunnel ID**: `d1e53e43-033f-4994-8f46-c83962ae3785`

**Affected Domains**:
- observatory.nkllon.com
- grafana.observatory.nkllon.com
- prometheus.observatory.nkllon.com

---

## Cloudflare Custom Error Pages Overview

### Available Methods

Cloudflare provides **two methods** for customizing error pages:

#### 1. Custom Error Pages (Simpler, Recommended for 1033)

- **Purpose**: Replace default Cloudflare error pages with custom HTML
- **Availability**: Pro, Business, Enterprise plans
- **Configuration**: Via Cloudflare Dashboard
- **Scope**: Zone-level (applies to all subdomains) or Account-level
- **Supported Errors**: All Cloudflare 1xxx errors, including 1033

#### 2. Custom Error Rules (Advanced)

- **Purpose**: Dynamic error handling with conditional logic
- **Availability**: Pro (25 rules), Business (50 rules), Enterprise (300 rules)
- **Configuration**: Via Rules → Custom Error Rules
- **Use Case**: Different error pages based on URL patterns, user agents, etc.

### Important Limitations

**Cannot customize** the following status codes:
- `500` (Internal Server Error)
- `501` (Not Implemented)
- `503` (Service Unavailable)
- `505` (HTTP Version Not Supported)

**Good news**: Error `1033` is **fully customizable** as it's a Cloudflare-specific tunnel error (1xxx series).

---

## Design Recommendations

### Option 1: Simple Informational Page (Recommended)

**Purpose**: Inform users the service is temporarily unavailable with professional branding.

**Key Elements**:
- Clear, friendly messaging
- Observatory branding/logo
- Estimated time to resolution (if known)
- Status page link or contact information
- Reassurance that data is safe

**Visual Style**:
- Clean, minimal design
- Observatory color scheme (if established)
- Professional typography
- Responsive design for mobile

**Content Tone**:
- Apologetic but professional
- Brief explanation without technical jargon
- Clear next steps for users

#### Example Content:

```
🔭 Observatory Temporarily Unavailable

We're currently experiencing technical difficulties with our
monitoring infrastructure. Our team has been notified and is
working to restore service.

Expected Resolution: [Auto-detect or manual update]

What you can do:
• Check back in a few minutes
• Follow updates at [status page]
• Contact support: [email/link]

Your data and configurations are safe and will be available
once service is restored.

— The Observatory Team
```

### Option 2: Interactive Status Page

**Purpose**: Provide real-time status information and retry capabilities.

**Key Elements**:
- Live status indicator (using external status API)
- Automatic page refresh/retry functionality
- Timeline of recent incidents
- Subscribe to status updates
- Retry button with visual feedback

**Technical Requirements**:
- External status API endpoint (not dependent on Observatory)
- JavaScript for auto-refresh and status checking
- CSS animations for loading states

**Use Case**: Better for frequently visited services where users want to monitor recovery.

### Option 3: Branded Maintenance Page with Context

**Purpose**: Turn downtime into brand-building opportunity.

**Key Elements**:
- Observatory mission statement
- Feature highlights (what users can do when service returns)
- Links to documentation
- Community channels (Discord, GitHub)
- "While you wait" resources

**Use Case**: For planned maintenance or when longer downtimes are expected.

---

## Recommended Approach: Option 1 (Simple Informational Page)

### Rationale

1. **Simplicity**: No external dependencies means it always works
2. **Speed**: Lightweight HTML/CSS loads instantly
3. **Reliability**: No JavaScript means no client-side failures
4. **Accessibility**: Works on all devices and browsers
5. **Professional**: Maintains brand trust during outages

### Design Specifications

#### Visual Design

**Layout**:
```
┌─────────────────────────────────────┐
│         [Observatory Logo]          │
│                                     │
│    🔭 Observatory Temporarily       │
│         Unavailable                 │
│                                     │
│  [Brief explanation of the issue]   │
│                                     │
│  [Expected resolution time]         │
│                                     │
│  [Action items for users]           │
│                                     │
│  [Footer: Status link, contact]     │
└─────────────────────────────────────┘
```

**Color Palette** (suggestions based on Observatory theme):
- Primary: Deep space blue (#1a1f35)
- Accent: Observatory cyan (#00d4ff)
- Text: Light gray on dark (#e0e0e0)
- Warning: Warm amber (#ff9800)

**Typography**:
- Headings: Sans-serif, 24-32px
- Body: Sans-serif, 16-18px
- Monospace for technical details (optional)

**Iconography**:
- Telescope emoji (🔭) or custom SVG logo
- Subtle background: Constellation pattern or gradient

#### Content Strategy

**Headline**: Clear and concise
- ✅ "Observatory Temporarily Unavailable"
- ❌ "Error 1033: Argo Tunnel Connection Failed"

**Body**: User-focused, not technical
- ✅ "We're experiencing technical difficulties"
- ❌ "The cloudflared daemon is not responding to edge requests"

**Call to Action**: Give users options
- Check back in X minutes
- Visit status page
- Contact support
- Explore documentation

**Tone**: Professional yet human
- Acknowledge the inconvenience
- Take responsibility
- Provide reassurance
- Set expectations

#### Responsive Design

**Desktop (>768px)**:
- Centered content, max-width 600px
- Large logo and typography
- Generous whitespace

**Mobile (<768px)**:
- Full-width content with padding
- Scaled-down logo
- Larger tap targets for links

**Accessibility**:
- WCAG 2.1 AA compliant contrast ratios
- Semantic HTML structure
- Alt text for images
- Screen reader friendly

---

## Implementation Options

### Method A: Cloudflare Dashboard (Recommended)

**Steps**:
1. Log in to Cloudflare Dashboard
2. Select zone: `nkllon.com`
3. Navigate to **Rules** → **Custom Error Responses**
4. Create new Error Page for status code `1033`
5. Upload custom HTML file
6. Save and deploy

**Pros**:
- Simple point-and-click interface
- Immediate preview
- Easy to update
- No CLI required

**Cons**:
- Must have Pro plan or higher
- Requires dashboard access

### Method B: Cloudflare API (Automated)

**Steps**:
1. Create custom HTML file locally
2. Use Cloudflare API to upload error page
3. Configure error page for zone
4. Automate updates via script

**Pros**:
- Scriptable and version-controlled
- Can be integrated into CI/CD
- Consistent with infrastructure-as-code

**Cons**:
- Requires API token
- More complex setup
- Need to handle API authentication

### Method C: Workers (Advanced)

**Steps**:
1. Create Cloudflare Worker
2. Intercept 1033 errors
3. Return custom HTML response
4. Deploy worker to route

**Pros**:
- Dynamic content possible
- Can include logic (e.g., status checks)
- Most flexible option

**Cons**:
- Requires Workers plan
- More complex maintenance
- Adds latency

---

## Recommended Implementation Plan

### Phase 1: Quick Win (1-2 hours)

**Goal**: Replace generic 1033 page with basic branded page

**Tasks**:
1. ✅ **Design simple HTML page**
   - Use template below
   - Customize with Observatory branding
   - Test locally in browser

2. ✅ **Create custom error page in Cloudflare Dashboard**
   - Navigate to Rules → Custom Error Responses
   - Upload HTML (or paste inline)
   - Configure for error code 1033
   - Set scope: Zone-level (nkllon.com)

3. ✅ **Test the error page**
   - Stop tunnel: `make tunnel-stop`
   - Visit observatory.nkllon.com
   - Verify custom page appears
   - Test on mobile device

4. ✅ **Document the process**
   - Add to runbook
   - Include screenshots
   - Note any gotchas

**Deliverable**: Professional error page visible when Observatory is down

### Phase 2: Enhancement (4-6 hours)

**Goal**: Add polish and functionality

**Tasks**:
1. **Improve design**
   - Add Observatory logo/branding
   - Enhance visual design with CSS
   - Add animations or micro-interactions
   - Optimize for all screen sizes

2. **Add useful content**
   - Status page link (if available)
   - Documentation links
   - Community/support contacts
   - Explanation of Observatory features

3. **Optional: Add JavaScript**
   - Auto-refresh every 30 seconds
   - Retry button with countdown
   - Show timestamp of outage
   - Local storage for visit count

4. **Create assets**
   - Upload images to Cloudflare (or external CDN)
   - Minify CSS/JS
   - Test cross-browser compatibility

**Deliverable**: Polished, professional error page with brand consistency

### Phase 3: Automation (2-3 hours)

**Goal**: Make updates scriptable and version-controlled

**Tasks**:
1. **Version control**
   - Add custom error page HTML to git
   - Create dedicated directory: `cloudflare/error-pages/`
   - Track changes over time

2. **Create deployment script**
   - Python script using Cloudflare API
   - Upload error page programmatically
   - Include in Makefile: `make deploy-error-pages`

3. **CI/CD integration**
   - Automatically deploy on merge to main
   - Validate HTML before deployment
   - Notify on successful deployment

4. **Testing**
   - Add automated tests for error page
   - Verify correct HTTP status codes
   - Check content and styling

**Deliverable**: Automated, maintainable error page deployment

---

## Sample HTML Templates

### Enhanced Template (Playful & Animated - RECOMMENDED)

**Location**: `cloudflare/error-pages/1033-enhanced.html`

This enhanced version features:
- 🐭 **Animated lab rat mascot** with frazzled hair
- 💨 **Smoke puffs and sparks** for incident atmosphere
- 🧪 **Wobbling lab equipment** (beakers and flasks)
- ⚡ **Dynamic particle effects** in background
- 🔄 **Auto-refresh countdown** (30 seconds)
- 📊 **Full technical transparency** in YAML format
- 🎮 **Easter eggs** (Konami code, spacebar retry)
- 📱 **Fully responsive** with mobile optimization
- ♿ **Accessible** with semantic HTML

**Key Features**:
- **Playful Tone**: "No lab animals were harmed in this incident"
- **Real-time Status**: Live countdown timer with auto-retry
- **Information Architecture**: 3-column grid showing actions, features, and services
- **Visual Storytelling**: Lab scene sets the mood immediately
- **Complete Transparency**: Full technical details in monospace YAML format
- **Interactive Elements**: Retry button with loading spinner, keyboard shortcuts

**File Size**: ~15KB (well within limits)
**Dependencies**: None (all inline CSS/JS)
**Browser Support**: All modern browsers + graceful degradation

### Basic Template (Minimal Starting Point)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatory - Temporarily Unavailable</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1a1f35 0%, #2d3561 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 600px;
            text-align: center;
            background: rgba(255, 255, 255, 0.05);
            padding: 40px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .icon {
            font-size: 64px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        h1 {
            font-size: 28px;
            margin-bottom: 16px;
            color: #00d4ff;
        }

        .message {
            font-size: 18px;
            margin-bottom: 24px;
            color: #b0b0b0;
        }

        .details {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 8px;
            margin: 24px 0;
            text-align: left;
        }

        .details h2 {
            font-size: 16px;
            color: #00d4ff;
            margin-bottom: 12px;
        }

        .details ul {
            list-style: none;
            padding-left: 0;
        }

        .details li {
            padding: 8px 0;
            padding-left: 24px;
            position: relative;
        }

        .details li:before {
            content: "→";
            position: absolute;
            left: 0;
            color: #00d4ff;
        }

        .footer {
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 14px;
            color: #808080;
        }

        .footer a {
            color: #00d4ff;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .container {
                padding: 30px 20px;
            }

            h1 {
                font-size: 24px;
            }

            .message {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔭</div>
        <h1>Observatory Temporarily Unavailable</h1>
        <p class="message">
            We're currently experiencing technical difficulties with our monitoring infrastructure.
            Our team has been notified and is working to restore service.
        </p>

        <div class="details">
            <h2>What you can do:</h2>
            <ul>
                <li>Try refreshing this page in a few minutes</li>
                <li>Check our status page for updates</li>
                <li>Contact support if you need immediate assistance</li>
            </ul>
        </div>

        <div class="details">
            <h2>Technical Details:</h2>
            <ul>
                <li>Error Code: 1033 (Tunnel Connection Error)</li>
                <li>Service: Observatory Monitoring</li>
                <li>Your data and configurations are safe</li>
            </ul>
        </div>

        <div class="footer">
            <p>
                Need help?
                <a href="https://github.com/your-org/observatory/issues">Report an issue</a> |
                <a href="mailto:support@nkllon.com">Contact Support</a>
            </p>
            <p style="margin-top: 12px;">
                <small>Observatory - Beast Mode Observability Framework</small>
            </p>
        </div>
    </div>
</body>
</html>
```

---

## Configuration Steps (Detailed)

### Via Cloudflare Dashboard

1. **Access Cloudflare Dashboard**
   - Navigate to: https://dash.cloudflare.com/
   - Select your account
   - Select zone: `nkllon.com`

2. **Navigate to Custom Error Pages**
   - Click **Rules** in left sidebar
   - Select **Custom Error Responses** (or **Custom Pages** on older UI)
   - Note: If you don't see this option, verify your plan includes Custom Error Pages (Pro+)

3. **Create Error Page**
   - Click **Create custom error response** or **+ Add error page**
   - Select error code: `1033` from dropdown
   - Choose method:
     - **Option A**: Paste HTML directly into text area
     - **Option B**: Upload HTML file
   - Preview the page
   - Click **Save** or **Deploy**

4. **Verify Configuration**
   - Error page should now be listed in dashboard
   - Note the scope (Zone-level vs Account-level)
   - Check that status is "Active"

5. **Test**
   - Stop your tunnel: `cloudflared tunnel stop observatory-tunnel`
   - Visit: https://observatory.nkllon.com
   - Verify custom error page appears
   - Test all affected subdomains:
     - https://grafana.observatory.nkllon.com
     - https://prometheus.observatory.nkllon.com

6. **Restart Tunnel**
   - Start tunnel: `make tunnel-start` (or equivalent command)
   - Verify normal service resumes

### Via Cloudflare API (Advanced)

```bash
# Set variables
ZONE_ID="your-zone-id"
API_TOKEN="your-api-token"
ERROR_PAGE_FILE="cloudflare/error-pages/1033.html"

# Upload error page
curl -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/custom_pages/basic_challenge" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "url": "https://your-cdn.com/error-pages/1033.html",
    "state": "customized"
  }'
```

**Note**: For 1033 errors specifically, you may need to use the Custom Error Rules API endpoint instead of custom_pages.

---

## Testing Strategy

### Test Scenarios

1. **Tunnel Completely Down**
   - Stop cloudflared daemon
   - Visit all three domains
   - Verify custom page appears
   - Check from different locations/devices

2. **Tunnel Starting Up**
   - Start tunnel while page is open
   - Refresh to verify normal service resumes
   - No broken links or cached error page

3. **Partial Outage**
   - Stop only Observatory service (port 8888)
   - Check if error handling differs
   - Verify appropriate error for each scenario

4. **Browser Compatibility**
   - Test on Chrome, Firefox, Safari, Edge
   - Test on mobile browsers (iOS Safari, Chrome)
   - Verify rendering on older browsers

5. **Network Conditions**
   - Test on slow connections (3G)
   - Verify page loads quickly
   - Check that external resources load or degrade gracefully

### Testing Checklist

- [ ] Custom page appears for error 1033
- [ ] Page renders correctly on desktop
- [ ] Page renders correctly on mobile
- [ ] All links work correctly
- [ ] No JavaScript errors in console
- [ ] CSS loads properly
- [ ] Images/logos display correctly
- [ ] Contact information is accurate
- [ ] Normal service resumes when tunnel starts
- [ ] No caching issues (error page not stuck)

---

## Maintenance & Updates

### When to Update Error Page

- Branding changes (logo, colors, fonts)
- Contact information changes
- New status page or support channels
- User feedback on clarity or helpfulness
- Regular reviews (quarterly recommended)

### Version Control

```
cloudflare/
  error-pages/
    1033.html              # Current version
    1033-v2.html          # Previous version
    README.md             # Documentation
    assets/
      logo.svg
      styles.css          # External CSS if needed
    scripts/
      deploy.py           # Deployment script
```

### Deployment Process

1. Make changes to `1033.html`
2. Test locally in browser
3. Commit to version control
4. Run deployment script or manual upload
5. Test in production
6. Document changes in changelog

---

## Cost Considerations

### Cloudflare Plan Requirements

**Free Plan**: ❌ Custom Error Pages not available
**Pro Plan** ($20/month): ✅ 25 custom error rules/pages
**Business Plan** ($200/month): ✅ 50 custom error rules/pages
**Enterprise Plan**: ✅ 300 custom error rules/pages

**Current Plan Status**: Check your Cloudflare dashboard to verify you have Pro or higher for `nkllon.com` zone.

### Resource Limits

- **HTML Size**: Keep under 100KB for fast loading
- **External Resources**: Minimize external dependencies
- **Image Size**: Optimize all images (<50KB recommended)
- **Total Page Weight**: Target <150KB for optimal performance

---

## Alternative Solutions (If Custom Error Pages Unavailable)

### 1. Cloudflare Workers

Deploy a Worker that intercepts 1033 errors:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  try {
    const response = await fetch(request)

    // If we get a 1033 error page (detect by content)
    if (response.status === 530) {
      return new Response(customErrorHTML, {
        status: 530,
        headers: {
          'content-type': 'text/html;charset=UTF-8',
        },
      })
    }

    return response
  } catch (error) {
    return new Response(customErrorHTML, {
      status: 530,
      headers: {
        'content-type': 'text/html;charset=UTF-8',
      },
    })
  }
}

const customErrorHTML = `<!DOCTYPE html>...`
```

**Cost**: Workers plan ($5/month for 10M requests)

### 2. Failover to Static Site

- Deploy static "Observatory Down" page to Cloudflare Pages
- Update DNS CNAME to point to Pages when tunnel is down
- Manual process but no plan upgrade required

### 3. Status Page Service

- Use external status page (e.g., status.io, statuspage.io)
- Redirect to status page during outages
- More expensive but professionally managed

---

## Success Metrics

### User Experience

- ✅ Users see branded, professional page instead of generic error
- ✅ Users understand what happened and what to do next
- ✅ Users can contact support or find more information
- ✅ Mobile users have good experience

### Technical

- ✅ Error page loads in <1 second
- ✅ Error page works on all browsers
- ✅ Updates can be deployed in <5 minutes
- ✅ Page is accessible and WCAG compliant

### Business

- ✅ Maintains brand trust during outages
- ✅ Reduces support inquiries about "broken" site
- ✅ Provides clear communication channel
- ✅ Professional appearance for potential customers/partners

---

## Next Steps

### Immediate (Today)

1. ✅ **Verify Cloudflare plan** includes Custom Error Pages
2. ✅ **Create HTML** using template above
3. ✅ **Upload to Cloudflare** via dashboard
4. ✅ **Test** by stopping tunnel

### Short-term (This Week)

1. ⏳ **Enhance design** with Observatory branding
2. ⏳ **Add real contact information** and links
3. ⏳ **Test across devices** and browsers
4. ⏳ **Document process** in runbook

### Long-term (This Month)

1. 🔮 **Automate deployment** via API
2. 🔮 **Version control** error pages
3. 🔮 **Create error pages** for other scenarios (404, 502, etc.)
4. 🔮 **Monitor usage** and gather feedback

---

## Resources & References

### Cloudflare Documentation

- [Custom Errors Overview](https://developers.cloudflare.com/rules/custom-errors/)
- [Error 1033 Troubleshooting](https://developers.cloudflare.com/support/troubleshooting/http-status-codes/cloudflare-1xxx-errors/error-1033/)
- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

### Design Inspiration

- GitHub error pages
- Netlify error pages
- Vercel error pages
- Heroku error pages

### Tools

- HTML/CSS validators
- Accessibility checkers (WAVE, axe DevTools)
- Mobile responsiveness testers
- Browser testing services (BrowserStack, CrossBrowserTesting)

---

## Questions & Troubleshooting

### Q: Will this affect normal traffic?

**A**: No. Custom error pages only appear when the specified error occurs. Normal traffic sees your regular Observatory interface.

### Q: Can I use external CSS/JS?

**A**: Yes, but consider reliability. If external resources fail, your error page may break. Inline CSS/JS is more reliable.

### Q: How quickly does the error page update after deployment?

**A**: Typically within 1-5 minutes globally due to Cloudflare's edge caching.

### Q: Can I have different error pages for different subdomains?

**A**: With Custom Error Rules (advanced), yes. Basic Error Pages apply zone-wide.

### Q: What if I don't have a Pro plan?

**A**: Consider Cloudflare Workers (cheaper) or manual failover to static site.

---

## Conclusion

Implementing a custom 1033 error page for Observatory is straightforward and provides significant value:

✅ **Professional brand image** during outages
✅ **Clear communication** with users
✅ **Reduced support burden** through self-service information
✅ **Better user experience** than generic error pages

**Recommended approach**: Start with the simple HTML template, deploy via Cloudflare Dashboard, then iterate based on feedback.

**Time investment**: 1-2 hours for basic implementation, 4-6 hours for polished version.

**ROI**: High - significantly improves perception during inevitable downtime.

---

**Document Version**: 1.0
**Last Updated**: 2025-09-30
**Owner**: Observatory Team
**Review Cycle**: Quarterly