# Implementation Plan

- [x] 1. Implement project ID extraction utility
  - Create `extractProjectId` function in `src/auth/utils.ts` to handle multiple credential formats
  - Add support for extracting project_id from both "installed" and direct credential formats
  - Implement error handling for missing or invalid project information
  - Write unit tests for project ID extraction with various credential file formats
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Enhance OAuth client initialization with quota project support
  - Modify `initializeOAuth2Client` function in `src/auth/client.ts` to extract and use project information
  - Add quota project configuration to OAuth2Client initialization
  - Implement fallback behavior when project ID is missing with appropriate warnings
  - Write unit tests for OAuth client initialization with quota project configuration
  - _Requirements: 1.1, 1.2, 3.1, 3.5, 5.1, 5.2_

- [x] 3. Update Google Calendar API client configuration
  - Modify `getCalendar` method in `src/handlers/core/BaseToolHandler.ts` to accept quota project configuration
  - Configure Google Calendar API client with `quotaProjectId` parameter for proper header inclusion
  - Ensure all API calls automatically include `x-goog-user-project` header
  - Write unit tests for API client configuration with quota project headers
  - _Requirements: 1.3, 1.4, 3.2, 3.3_

- [x] 4. Enhance error handling for quota project issues
  - Update `handleGoogleApiError` method to provide specific guidance for quota-related rate limit errors
  - Add `QuotaProjectMissingError` class with detailed troubleshooting information
  - Implement enhanced error messages that distinguish between project-level and user-level rate limits
  - Write unit tests for quota project error handling scenarios
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5. Create comprehensive test suite for quota project functionality
  - Write integration tests for end-to-end quota project flow from credential loading to API calls
  - Add tests for backward compatibility with existing credential files
  - Create test scenarios for missing project information and error handling
  - Implement mock Google API responses to test quota project header inclusion
  - _Requirements: 5.3, 5.4, 5.5_

- [x] 6. Update documentation and troubleshooting guides
  - Add troubleshooting section to README.md explaining quota project requirements
  - Create step-by-step guide for obtaining OAuth credentials with project information
  - Document common quota-related errors and their solutions
  - Add examples of proper credential file formats with project_id
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7. Create feature branch and implement the fix
  - Create `fix/quota-project-header` branch in the forked repository
  - Implement all code changes according to the design specification
  - Ensure all tests pass and maintain backward compatibility
  - Prepare commit messages and pull request documentation
  - _Requirements: All requirements implementation_

- [ ] 8. Test the fix with real Google Calendar API
  - Set up test environment with OAuth credentials containing project information
  - Verify that API calls include proper quota project headers
  - Test rate limiting behavior with and without quota project configuration
  - Validate error handling with various credential file scenarios
  - _Requirements: 1.4, 1.5, 4.1, 4.2_

- [ ] 9. Prepare pull request submission
  - Create comprehensive pull request description with problem statement and solution
  - Include before/after examples showing the fix in action
  - Add testing instructions for maintainers to verify the fix
  - Reference related issues and provide migration guidance for users
  - _Requirements: All requirements validation and documentation_