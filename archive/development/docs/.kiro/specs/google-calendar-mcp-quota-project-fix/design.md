# Design Document

## Overview

This design addresses the critical quota project header bug in the Google Calendar MCP server by implementing proper project ID extraction from OAuth credentials and configuring Google API clients with quota project headers. The solution ensures that all API requests are properly attributed to the user's Google Cloud Project for quota management.

## Architecture

### Core Components

1. **Project ID Extractor** - Utility function to extract project IDs from various OAuth credential formats
2. **Enhanced OAuth Client Factory** - Modified client initialization with quota project configuration
3. **API Client Configuration** - Updated Google Calendar API client setup with proper headers
4. **Error Handling Enhancement** - Improved error messages for quota-related issues

### Data Flow

```
OAuth Credentials File → Project ID Extraction → API Client Configuration → Google Calendar API Calls (with quota headers)
```

## Components and Interfaces

### 1. Project ID Extraction Utility

**Location:** `src/auth/utils.ts`

```typescript
interface ProjectIdExtractionResult {
  projectId: string | null;
  source: 'installed' | 'direct' | 'missing';
}

function extractProjectId(credentials: OAuthCredentials): ProjectIdExtractionResult
```

**Responsibilities:**
- Extract project ID from OAuth credential files
- Handle multiple credential file formats (installed vs direct)
- Provide clear indication of extraction source or failure

### 2. Enhanced OAuth Client Factory

**Location:** `src/auth/client.ts`

```typescript
interface QuotaProjectConfig {
  projectId: string;
  clientId: string;
  clientSecret: string;
  redirectUris: string[];
}

function initializeOAuth2ClientWithQuotaProject(): Promise<OAuth2Client>
```

**Responsibilities:**
- Load credentials and extract project information
- Initialize OAuth2Client with quota project configuration
- Provide enhanced error handling for missing project information

### 3. Google Calendar API Client Configuration

**Location:** `src/handlers/core/BaseToolHandler.ts`

```typescript
protected getCalendar(auth: OAuth2Client, quotaProjectId?: string): calendar_v3.Calendar
```

**Responsibilities:**
- Configure Google Calendar API client with quota project headers
- Ensure all API calls include proper project attribution
- Maintain backward compatibility with existing implementations

### 4. Enhanced Error Handling

**Location:** `src/handlers/core/BaseToolHandler.ts`

**Responsibilities:**
- Provide specific error messages for quota project issues
- Distinguish between different types of rate limiting errors
- Include troubleshooting guidance in error responses

## Data Models

### OAuth Credentials with Project Information

```typescript
interface OAuthCredentials {
  client_id: string;
  client_secret: string;
  redirect_uris: string[];
  project_id?: string; // Optional for backward compatibility
}

interface InstalledCredentials {
  installed: {
    client_id: string;
    client_secret: string;
    redirect_uris: string[];
    project_id: string;
    auth_uri: string;
    token_uri: string;
  };
}
```

### Quota Project Configuration

```typescript
interface QuotaProjectConfig {
  projectId: string;
  isConfigured: boolean;
  source: 'credentials' | 'environment' | 'fallback';
}
```

## Error Handling

### Project ID Missing Error

```typescript
class QuotaProjectMissingError extends Error {
  constructor(credentialPath: string) {
    super(`
Quota project information missing from OAuth credentials.

Current credential file: ${credentialPath}

To fix this issue:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Select your project or create a new one
3. Enable the Google Calendar API
4. Go to "Credentials" → "OAuth 2.0 Client IDs"
5. Download the credential file (it should include project_id)
6. Replace your current credential file

The credential file should contain project_id information for proper quota attribution.
    `);
  }
}
```

### Rate Limit Error Enhancement

```typescript
protected handleGoogleApiError(error: unknown): never {
  if (error instanceof GaxiosError && error.response?.status === 429) {
    const errorMessage = error.response?.data?.error?.message || '';
    
    if (errorMessage.includes('User Rate Limit Exceeded')) {
      throw new McpError(
        ErrorCode.InvalidRequest,
        `Rate limit exceeded. This may be due to missing quota project configuration. 
        
Ensure your OAuth credentials include project_id information.
See troubleshooting guide: [link to documentation]

Original error: ${errorMessage}`
      );
    }
  }
  // ... existing error handling
}
```

## Testing Strategy

### Unit Tests

1. **Project ID Extraction Tests**
   - Test extraction from "installed" format credentials
   - Test extraction from direct format credentials
   - Test handling of missing project information
   - Test error cases and edge conditions

2. **OAuth Client Configuration Tests**
   - Test client initialization with project information
   - Test fallback behavior when project ID is missing
   - Test error handling for invalid credentials

3. **API Client Configuration Tests**
   - Test Google Calendar client configuration with quota project
   - Test header inclusion in API requests
   - Test backward compatibility with existing code

### Integration Tests

1. **End-to-End Quota Project Flow**
   - Test complete flow from credential loading to API calls
   - Verify quota project headers are included in actual API requests
   - Test with different credential file formats

2. **Error Scenario Testing**
   - Test behavior with missing project information
   - Test rate limit error handling and messaging
   - Test credential validation with project requirements

### Manual Testing

1. **Real API Testing**
   - Test with actual Google Calendar API using OAuth credentials
   - Verify quota attribution in Google Cloud Console
   - Test rate limiting behavior with and without quota project headers

## Implementation Approach

### Phase 1: Project ID Extraction
1. Implement `extractProjectId` utility function
2. Add unit tests for project ID extraction
3. Update credential loading to include project information

### Phase 2: OAuth Client Enhancement
1. Modify `initializeOAuth2Client` to handle quota project configuration
2. Add error handling for missing project information
3. Implement backward compatibility measures

### Phase 3: API Client Configuration
1. Update `getCalendar` method to accept quota project configuration
2. Configure Google Calendar client with proper headers
3. Ensure all handlers use the updated client configuration

### Phase 4: Error Handling and Documentation
1. Enhance error messages for quota-related issues
2. Add troubleshooting guidance to error responses
3. Update documentation with quota project setup instructions

## Security Considerations

1. **Credential Security**
   - Project ID is not sensitive information but should be handled consistently with other credential data
   - Ensure project ID is not logged in plain text in production environments
   - Maintain existing security practices for credential file handling

2. **API Security**
   - Quota project headers do not introduce additional security risks
   - Maintain existing OAuth 2.0 security practices
   - Ensure proper token handling and refresh mechanisms

## Performance Impact

1. **Minimal Overhead**
   - Project ID extraction occurs once during client initialization
   - Header addition has negligible performance impact
   - No additional API calls required

2. **Improved Reliability**
   - Proper quota attribution reduces likelihood of rate limiting errors
   - Better error handling improves user experience
   - Reduced support burden from quota-related issues

## Backward Compatibility

1. **Graceful Degradation**
   - System continues to function with credentials lacking project information
   - Clear warnings provided when project ID is missing
   - Existing credential files remain functional

2. **Migration Path**
   - Users can update credentials at their convenience
   - System provides guidance for obtaining proper credentials
   - No breaking changes to existing API interfaces