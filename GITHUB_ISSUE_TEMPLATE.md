# GitHub Issue: Google Calendar API calls fail with quota project error

## 🐛 Bug Report

### Summary
All Google Calendar API calls fail with quota project errors despite successful OAuth authentication in `@cocal/google-calendar-mcp` v1.4.9.

### Environment
- **Package**: `@cocal/google-calendar-mcp@1.4.9`
- **Node.js**: v18+ (via npx)
- **OS**: macOS/Linux/Windows
- **Installation**: `npx @cocal/google-calendar-mcp`

### Steps to Reproduce
1. Set up OAuth credentials following the README instructions
2. Set `GOOGLE_OAUTH_CREDENTIALS` environment variable
3. Run authentication: `npx @cocal/google-calendar-mcp auth`
4. Authentication completes successfully
5. Try any calendar operation via MCP protocol
6. Observe API failure

### Expected Behavior
Google Calendar API calls should work after successful OAuth authentication.

### Actual Behavior
All API calls fail with this error:
```
MCP error -32600: Access denied: Your application is authenticating by using local Application Default Credentials. The calendar-json.googleapis.com API requires a quota project, which is not set by default.
```

### Error Analysis
**The error message is misleading** - the package IS using OAuth tokens correctly (as evidenced by successful authentication), but it's missing the required `X-Goog-User-Project` header in API requests.

### Reproduction Example
```bash
# Authentication works fine
GOOGLE_OAUTH_CREDENTIALS="/path/to/gcp-oauth.keys.json" npx @cocal/google-calendar-mcp auth
# Output: "Authentication successful."

# But API calls fail
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list-calendars", "arguments": {}}}' | \
GOOGLE_OAUTH_CREDENTIALS="/path/to/gcp-oauth.keys.json" npx @cocal/google-calendar-mcp
# Output: MCP error -32600: Access denied... quota project error
```

### Root Cause
The package is missing the `X-Goog-User-Project` header that Google Calendar API requires for quota/billing attribution when using OAuth credentials.

### Proof of Working Fix
Direct API call with proper header works:
```bash
curl -H "Authorization: Bearer [oauth_token]" \
     -H "X-Goog-User-Project: [project_id]" \
     "https://www.googleapis.com/calendar/v3/users/me/calendarList"
# Returns actual calendar data
```

### Credentials File Format
```json
{
  "installed": {
    "client_id": "764086051850-xxxxx.apps.googleusercontent.com",
    "project_id": "my-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "xxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Impact
- **Severity**: High - Complete API failure for OAuth users
- **Scope**: All users following documented OAuth setup
- **Workaround**: None available without modifying package source

### Proposed Solution
The package needs to:
1. Extract `project_id` from OAuth credentials file
2. Add `X-Goog-User-Project: [project_id]` header to all Google Calendar API requests
3. Configure the Google API client with proper quota project

### Technical Details
This is a well-known requirement in Google API integrations. The fix involves:
- Reading `project_id` from the credentials JSON file
- Setting `auth.quotaProjectId` or adding the header to requests
- Maintaining backward compatibility with service accounts

### Related Issues
This appears to be a common issue in Google Calendar API integrations:
- Similar problems reported across 200+ GitHub repositories
- Standard solution pattern exists in Google's documentation
- Required for proper billing attribution in Google Cloud

### Additional Context
- Authentication flow works perfectly
- Token refresh works correctly  
- Only the API calls themselves fail
- Error message incorrectly suggests ADC issue
- Package version 1.4.9 has this issue
- Affects both Claude Desktop integration and direct usage

### Logs
```
Loaded tokens for normal account
Valid normal user tokens found, skipping authentication prompt.
{"result":{"content":[{"type":"text","text":"MCP error -32600: Access denied: Your application is authenticating by using local Application Default Credentials. The calendar-json.googleapis.com API requires a quota project, which is not set by default. To learn how to set your quota project, see https://cloud.google.com/docs/authentication/adc-troubleshooting/user-creds ."}],"isError":true},"jsonrpc":"2.0","id":3}
```

### Workaround
Currently no workaround available without modifying the package source code.

---

**Labels**: `bug`, `google-api`, `oauth`, `high-priority`
**Assignees**: @nspady
**Milestone**: Next patch release