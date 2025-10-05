# Get Cloudflare API Token - 2 Minute Setup

## Quick Steps:

1. **Go to**: https://dash.cloudflare.com/profile/api-tokens
2. **Click**: "Create Token"
3. **Use**: "Custom token" template
4. **Set permissions**:
   - Zone:Edit for nkllon.com
   - Zone:Read for nkllon.com
5. **Click**: "Continue to summary" → "Create Token"
6. **Copy the token** (starts with something like `1234abcd...`)

## Use the token:

```bash
export CLOUDFLARE_API_TOKEN="your_token_here"
python3 cloudflare-error-pages-cli.py deploy --interactive
```

**That's it!** Much easier than manual deployment.