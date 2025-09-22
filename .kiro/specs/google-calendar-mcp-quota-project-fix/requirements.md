# Requirements Document

## Introduction

This specification defines the requirements for fixing a critical bug in the Google Calendar MCP server where OAuth users encounter "User Rate Limit Exceeded" errors due to missing quota project headers in Google API calls. This fix addresses a fundamental issue where API requests are not properly attributed to the correct Google Cloud Project for quota management.

The bug affects all OAuth users of the google-calendar-mcp package and prevents proper calendar operations when using OAuth 2.0 authentication flow.

## Requirements

### Requirement 1: Quota Project Header Implementation

**User Story:** As an OAuth user of the Google Calendar MCP, I want API calls to include proper quota project headers so that my requests are attributed to the correct Google Cloud Project and don't encounter rate limit errors.

#### Acceptance Criteria

1. WHEN OAuth credentials are loaded THEN the system SHALL extract the project ID from the credentials file
2. WHEN Google Calendar API calls are made THEN they SHALL include the `x-goog-user-project` header with the correct project ID
3. WHEN the project ID is missing from credentials THEN the system SHALL provide a clear error message with troubleshooting guidance
4. WHEN API calls are made with quota project headers THEN they SHALL be properly attributed to the user's Google Cloud Project quota
5. WHEN rate limiting occurs THEN it SHALL be based on the user's project quota, not shared quota pools

### Requirement 2: Credential Project ID Extraction

**User Story:** As a developer, I want the system to automatically extract project IDs from OAuth credential files so that quota project headers are configured without manual intervention.

#### Acceptance Criteria

1. WHEN OAuth credentials are in "installed" format THEN the system SHALL extract project_id from the installed object
2. WHEN OAuth credentials are in direct format THEN the system SHALL extract project_id from the root level
3. WHEN project_id is missing from credentials THEN the system SHALL provide guidance on obtaining proper credentials
4. WHEN credentials are validated THEN project_id SHALL be included in the validation process
5. WHEN multiple credential formats are supported THEN project_id extraction SHALL work consistently across all formats

### Requirement 3: Google API Client Configuration

**User Story:** As a system administrator, I want Google API clients to be properly configured with quota project information so that all calendar operations respect project-level quotas.

#### Acceptance Criteria

1. WHEN Google Calendar API client is initialized THEN it SHALL be configured with the quota project ID
2. WHEN API requests are made THEN the client SHALL automatically include quota project headers
3. WHEN multiple API operations occur THEN all SHALL consistently use the same quota project configuration
4. WHEN client configuration fails THEN the system SHALL provide clear error messages and recovery guidance
5. WHEN quota project is configured THEN it SHALL be logged for debugging purposes (without exposing sensitive data)

### Requirement 4: Error Handling and Diagnostics

**User Story:** As a user experiencing quota issues, I want clear error messages and diagnostic information so that I can understand and resolve quota-related problems.

#### Acceptance Criteria

1. WHEN quota project configuration fails THEN the system SHALL provide specific error messages about missing project information
2. WHEN rate limit errors occur THEN the system SHALL distinguish between project-level and user-level rate limits
3. WHEN troubleshooting is needed THEN the system SHALL provide guidance on verifying Google Cloud Project configuration
4. WHEN credentials are invalid THEN error messages SHALL include steps to obtain proper OAuth credentials with project information
5. WHEN debugging quota issues THEN the system SHALL log quota project configuration status without exposing sensitive credentials

### Requirement 5: Backward Compatibility

**User Story:** As an existing user of the Google Calendar MCP, I want the quota project fix to work with my existing credential files so that I don't need to reconfigure my setup.

#### Acceptance Criteria

1. WHEN existing credential files are used THEN the system SHALL attempt to extract project information without breaking existing functionality
2. WHEN project information is unavailable THEN the system SHALL fall back gracefully with appropriate warnings
3. WHEN credential file formats vary THEN the system SHALL handle multiple formats consistently
4. WHEN upgrading to the fixed version THEN existing users SHALL receive clear guidance about any required credential updates
5. WHEN migration is needed THEN the system SHALL provide step-by-step instructions for updating credentials

### Requirement 6: Documentation and Troubleshooting

**User Story:** As a user setting up Google Calendar MCP, I want comprehensive documentation about quota project configuration so that I can avoid and resolve quota-related issues.

#### Acceptance Criteria

1. WHEN setting up OAuth credentials THEN documentation SHALL explain the importance of project information in credential files
2. WHEN troubleshooting quota errors THEN users SHALL have access to step-by-step diagnostic procedures
3. WHEN credential files are missing project information THEN the system SHALL provide links to Google Cloud Console instructions
4. WHEN quota limits are reached THEN documentation SHALL explain how to monitor and increase project quotas
5. WHEN common issues occur THEN troubleshooting guides SHALL provide specific solutions for quota project problems