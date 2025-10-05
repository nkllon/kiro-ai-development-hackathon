# Claude Code Deployment Prompt: Cloudflare Custom Error Pages

## Mission
Deploy custom error pages to Cloudflare Dashboard using browser automation since their API doesn't support Custom Error Pages yet.

## Context
We spent 2 hours building a "fully automated" CLI deployment system only to discover Cloudflare doesn't have an API for Custom Error Pages. Time to use OSA and Chrome automation to actually automate the manual process!

## What You Need to Do

### 1. Open Cloudflare Dashboard
- Navigate to: https://dash.cloudflare.com/
- Log in (credentials will be needed)
- Select zone: `nkllon.com`

### 2. Navigate to Custom Error Pages
- Click "Rules" in left sidebar
- Click "Custom Error Responses"
- Click "Create custom error response"

### 3. Configure Error Page
- Error code: Select `1033` from dropdown
- Response type: Select `Custom HTML`
- HTML content: Copy from file `cloudflare/error-pages/1033-enhanced.html`

### 4. Deploy
- Click "Save"
- Wait for deployment confirmation
- Verify status shows "Active"

## Files Available
- **HTML File**: `cloudflare/error-pages/1033-enhanced.html` (22.9KB, validated)
- **API Token**: `NbkULd9bJ3UK9yhHDahYq5LBwMkHEgq4mVy0h4QV` (for login if needed)
- **Zone**: nkllon.com (Pro plan, supports Custom Error Pages)

## What the Error Page Contains
- Animated lab rat mascot 🐭 with smoke and sparks
- Observatory branding with space gradient
- 30-second auto-refresh countdown
- Interactive "Retry Now" button with spinner
- Konami code Easter egg (↑↑↓↓←→←→BA)
- Full technical transparency with tunnel ID
- Mobile-responsive design

## Testing After Deployment
The tunnel is currently down (perfect timing!), so you can immediately test:
- Visit: https://observatory.nkllon.com
- Should see custom error page instead of generic "error code: 1033"
- Test interactive features (countdown, retry button, Easter egg)

## Success Criteria
- Custom error page appears for Error 1033
- All three Observatory domains show the custom page:
  - observatory.nkllon.com
  - grafana.observatory.nkllon.com  
  - prometheus.observatory.nkllon.com
- Interactive features work (countdown, retry button)
- Page is mobile-responsive

## The Irony
We built an entire "automated deployment system" with:
- Rich CLI with progress bars
- CI/CD pipelines
- Docker containers
- GitHub Actions workflows
- Comprehensive validation
- API client wrappers

Only to discover Cloudflare's API doesn't support this feature! 😂

So now we're asking you to automate the manual process that our "automation" system tells users to do manually. Meta-automation!

## Expected Outcome
After deployment, users visiting Observatory domains while the tunnel is down will see a professional, branded error page with the lab rat mascot instead of the generic Cloudflare error message.

---

**TL;DR**: Click through Cloudflare Dashboard to upload our custom error page HTML because their API is apparently still in 2005. The tunnel is down so you can test immediately! 🚀