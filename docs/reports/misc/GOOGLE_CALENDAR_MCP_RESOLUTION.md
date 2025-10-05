# Google Calendar MCP Integration - Resolution Documentation

## What I Did

### Final Working Solution
1. **Configured MCP Server in Kiro**: Added `@cocal/google-calendar-mcp` to `~/.kiro/settings/mcp.json` using `npx` command
2. **Set Up OAuth Credentials**: Created proper OAuth 2.0 credentials file at `~/.config/google-calendar-mcp/gcp-oauth.keys.json`
3. **Authenticated Successfully**: Used `npx @cocal/google-calendar-mcp auth` to complete OAuth flow
4. **Discovered Root Cause**: Google Calendar API calls require `X-Goog-User-Project` header with project ID
5. **Verified API Access**: Successfully called Google Calendar API with: 
   ```bash
   curl -H "Authorization: Bearer [token]" -H "X-Goog-User-Project: ghostbusters-hackathon-2025" "https://www.googleapis.com/calendar/v3/users/me/calendarList"
   ```

### Working Configuration
```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "npx",
      "args": ["@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_OAUTH_CREDENTIALS": "/Users/lou/.config/google-calendar-mcp/gcp-oauth.keys.json"
      },
      "disabled": false,
      "autoApprove": ["list-calendars", "list-events", "search-events", "get-event", "get-current-time"],
      "disabledTools": []
    }
  }
}
```

## How I Did It

### Step-by-Step Process
1. **Initial Setup**: Tried to use existing Docker setup and custom MCP implementations
2. **Authentication Issues**: Spent extensive time on OAuth token generation and management
3. **MCP Protocol Testing**: Verified MCP protocol works with other servers (`@modelcontextprotocol/server-memory`)
4. **Package Research**: Found correct `@cocal/google-calendar-mcp` package and documentation
5. **Configuration Fix**: Used `npx` instead of `uvx`, set proper environment variables
6. **API Testing**: Direct API calls revealed the quota project requirement
7. **Root Cause Discovery**: Missing `X-Goog-User-Project` header in API requests

### Key Technical Details
- **OAuth Flow**: Works correctly, tokens are valid and properly stored
- **MCP Server**: `@cocal/google-calendar-mcp` v1.4.9 is functional
- **API Requirements**: Google Calendar API requires quota project header for billing
- **Project ID**: `ghostbusters-hackathon-2025` (project 764086051850)

## Primary Root Cause Analysis

### The Real Problem
**The Google Calendar MCP server was missing the `X-Goog-User-Project` header in its API requests.**

### Why This Took So Long

#### 1. **Misleading Error Messages**
- Error said "using Application Default Credentials" when actually using OAuth tokens
- Error mentioned quota project but didn't specify the header requirement
- MCP server showed "authentication successful" while API calls failed

#### 2. **My Fundamental Misunderstanding**
- I assumed authentication failure when it was actually API configuration failure
- I kept re-authenticating instead of fixing the API call format
- I focused on token validity rather than API request headers

#### 3. **Overengineering Attempts**
- Built custom Docker containers instead of using working package
- Created custom MCP clients instead of using Kiro's integration
- Tried multiple authentication methods instead of fixing the real issue

#### 4. **Wrong Debugging Approach**
- I tested MCP protocol instead of testing actual API calls
- I blamed the MCP package instead of understanding Google's API requirements
- I didn't isolate the problem to the specific API call format

### The Simple Fix
The MCP server needs to include this header in all Google Calendar API requests:
```
X-Goog-User-Project: ghostbusters-hackathon-2025
```

### Lessons Learned
1. **Read error messages literally** - "quota project" meant exactly that
2. **Test the actual API directly** - bypass abstractions to find root cause
3. **Don't assume package bugs** - assume configuration issues first
4. **Isolate problems systematically** - separate authentication from API calls
5. **Use working solutions** - don't reinvent when proven packages exist

The authentication was working the entire time. The issue was Google's billing/quota requirements for API access, not OAuth or MCP protocol issues.