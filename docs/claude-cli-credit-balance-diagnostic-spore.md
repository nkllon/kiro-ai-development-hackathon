# Claude CLI "Credit Balance Too Low" Diagnostic Spore

## Mission
Analyze and provide solutions for a Claude CLI authentication/subscription issue where valid accounts are being blocked with "Credit balance is too low" error.

## Problem Summary
Claude CLI (version 1.0.127) is returning "Credit balance is too low" error for a user with a valid Claude subscription and proper authentication. The error occurs before any API calls are made, suggesting a local CLI state issue.

## Evidence Collected

### Error Pattern
```json
{
  "type": "result",
  "subtype": "success", 
  "is_error": true,
  "duration_ms": 1639,
  "duration_api_ms": 0,  // ← No API call made
  "num_turns": 1,
  "result": "Credit balance is too low",
  "session_id": "102b84dd-2621-45d3-b17a-30a59e19a11a",
  "total_cost_usd": 0,   // ← No charges
  "usage": {
    "input_tokens": 0,   // ← No tokens used
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "output_tokens": 0
  }
}
```

### Account Status (from ~/.claude.json)
```json
{
  "hasAvailableSubscription": false,  // ← Problem indicator
  "subscriptionNoticeCount": 12,
  "hasOpusPlanDefault": false,
  "recommendedSubscription": "",
  "oauthAccount": {
    "accountUuid": "57c282fd-294b-45d3-9799-32e8c02e39d1",
    "emailAddress": "lou@louspringer.com",
    "organizationUuid": "d1519ebf-6873-44fe-98a5-12d022d6bd0f",
    "displayName": "Lou",
    "organizationRole": "admin"
  }
}
```

### Proof of Valid Subscription
The `claude setup-token` command successfully created a long-lived OAuth token:
```
✓ Long-lived authentication token created successfully!
Your OAuth token (valid for 1 year):
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
```

This proves:
1. ✅ Account authentication is working
2. ✅ Valid Claude subscription exists (token creation requires subscription)
3. ✅ OAuth flow is functional

### BREAKTHROUGH: Real Error Discovered
When user manually ran the same command, got **completely different error**:
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"This credential is only authorized for use with Claude Code and cannot be used for other API requests."},"request_id":"req_011CTZCBKTuqp2Rg4vMvYqm4"}
```

**Key Insight**: The "Credit balance is too low" error was a **subprocess authentication issue**. The real problem is **credential scope limitation**.

### Failed Solutions Attempted
1. **OAuth Token Override**: Setting `CLAUDE_CODE_OAUTH_TOKEN` still produced same error
2. **Config Flag Modification**: Changing `"hasAvailableSubscription": false` to `true` had no effect
3. **Multiple Test Commands**: All commands fail with identical error pattern

### Authentication Architecture Discovery
Claude Code appears to have **two authentication modes**:
1. **Interactive Mode**: For development work (works fine)
2. **Programmatic Mode**: For `--print` and API-style usage (credential restricted)

## Technical Analysis Required

### Key Questions
1. **What triggers the "Credit balance is too low" check in Claude CLI?**
   - Is it checking a local cache/database?
   - Is it making a pre-flight API call we're not seeing?
   - Is it validating against organization vs personal subscription?

2. **Why does `duration_api_ms: 0` but token creation works?**
   - Different authentication paths for different operations?
   - Cached subscription status vs real-time validation?

3. **What's the relationship between these config fields?**
   - `hasAvailableSubscription`
   - `subscriptionNoticeCount` 
   - `recommendedSubscription`
   - Organization role vs personal subscription

### Diagnostic Commands Run
```bash
# All produce same error:
echo "test" | claude --print --output-format json
claude --version  # Works: 1.0.127 (Claude Code)
claude setup-token  # Works: Creates valid OAuth token
claude config list  # Works: Shows basic config
```

### Environment Details
- **OS**: macOS (darwin)
- **Shell**: zsh
- **Claude CLI**: 1.0.127 (Claude Code)
- **Install Method**: global (from config)
- **Account Type**: Organization admin with valid subscription

## Request for Analysis

Please analyze this evidence and provide:

1. **Root Cause Identification**: What's causing the CLI to think there's no subscription?

2. **Diagnostic Steps**: Additional commands or config checks to isolate the issue

3. **Solution Strategies**: Ranked list of potential fixes, from least to most disruptive:
   - Configuration tweaks
   - Cache clearing procedures  
   - Re-authentication methods
   - CLI reinstallation approaches

4. **Workaround Options**: Alternative approaches while fixing the main issue

5. **Prevention**: How to avoid this issue recurring

## Context Notes
- This is blocking AI coordination workflows that depend on Claude CLI
- Cursor CLI works fine as fallback, but has different capabilities
- User has valid subscription and successful web interface access
- Issue appeared suddenly after previous successful CLI usage

## Success Criteria
A solution that allows `echo "test" | claude --print` to return actual Claude response instead of "Credit balance is too low" error.

---
*Spore created: 2025-09-27*  
*Status: Ready for external LLM analysis*  
*Priority: High - blocking production workflows*