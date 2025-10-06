# Cloudflare 1033 Laboratory Error Page Spore

## Context
The Observatory is a laboratory environment that occasionally triggers Cloudflare's bot protection (Error 1033). Instead of the generic Cloudflare error page, we need a laboratory-themed message that's more informative and on-brand.

## Custom Error Page Content

### HTML Content for Cloudflare Custom Pages → 1033 Argo Tunnel Error

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Observatory Laboratory - Temporarily Unavailable</title>
    <style>
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #00ff41;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            max-width: 600px;
            padding: 2rem;
            border: 2px solid #00ff41;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.3);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 0 0 10px #00ff41;
        }
        .title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .message {
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 2rem;
            color: #cccccc;
        }
        .status {
            font-family: monospace;
            background: #000;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            border-left: 4px solid #ff6b6b;
        }
        .retry {
            color: #00ff41;
            text-decoration: none;
            border: 1px solid #00ff41;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            display: inline-block;
            margin-top: 1rem;
            transition: all 0.3s ease;
        }
        .retry:hover {
            background: #00ff41;
            color: #000;
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔬 🌌</div>
        <h1 class="title">Observatory Laboratory</h1>
        <div class="message">
            <p>The laboratory is temporarily unavailable due to automated security protocols.</p>
            <p>This is a research and development environment where we experiment with AI coordination, WebSocket implementations, and systematic software development methodologies.</p>
        </div>
        <div class="status">
            <strong>STATUS:</strong> Security scan in progress<span class="blink">_</span><br>
            <strong>ERROR:</strong> 1033 - Argo Tunnel Protection<br>
            <strong>RETRY:</strong> Automated in 30 seconds
        </div>
        <p style="color: #888; font-size: 0.9rem;">
            If you're a legitimate researcher or collaborator, please wait a moment and try again.
            The system will automatically restore access once the security scan completes.
        </p>
        <a href="javascript:location.reload()" class="retry">🔄 Retry Access</a>
    </div>
    
    <script>
        // Auto-refresh after 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
        
        // Add some terminal-like effects
        document.addEventListener('DOMContentLoaded', function() {
            const status = document.querySelector('.status');
            let dots = 0;
            setInterval(function() {
                dots = (dots + 1) % 4;
                const loading = '.'.repeat(dots);
                status.innerHTML = status.innerHTML.replace(/\.{0,3}_/, loading + '_');
            }, 500);
        });
    </script>
</body>
</html>
```

## Implementation Instructions

### Via Cloudflare Dashboard:
1. Go to Cloudflare Dashboard → Your Domain → Custom Pages
2. Find "1033 Argo Tunnel error" in the list
3. Click "Customize"
4. Paste the HTML content above
5. Save changes

### Via Cloudflare API (Alternative):
```bash
curl -X PUT "https://api.cloudflare.com/client/v4/zones/{zone_id}/custom_pages/argo_tunnel_error" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{
    "url": null,
    "state": "customized",
    "required_tokens": ["::CAPTCHA_BOX::", "::IM_UNDER_ATTACK::"],
    "preview_target": "preview:argo_tunnel_error",
    "modified_on": null,
    "created_on": null,
    "description": "Laboratory-themed 1033 error page",
    "id": "argo_tunnel_error"
  }'
```

## Features

- **Laboratory Theme**: Matches the Observatory's research environment branding
- **Terminal Aesthetic**: Monospace fonts and green-on-black color scheme
- **Auto-Refresh**: Automatically retries after 30 seconds
- **Informative**: Explains this is a research environment
- **Professional**: Maintains credibility while being more user-friendly than default Cloudflare page
- **Responsive**: Works on mobile and desktop
- **Animated Elements**: Subtle blinking cursor and loading dots for visual interest

## Testing

After implementation, you can test by:
1. Triggering bot protection (rapid requests)
2. Checking that the custom page appears instead of default Cloudflare 1033
3. Verifying auto-refresh functionality works

This provides a much better user experience while maintaining the laboratory/research theme of the Observatory.