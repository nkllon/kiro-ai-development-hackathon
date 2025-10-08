# Requirements Document

## Introduction

**BROWNFIELD SYSTEM WARNING**: The Observatory is currently live and operational with real users accessing it via public Cloudflare tunnel. This specification addresses the surgical addition of Chart.js initialization for ONLY the LLM Token Tracking chart without disrupting existing functionality.

This specification builds on the successful Health Chart implementation pattern to add real-time token consumption visualization. Token tracking provides accurate resource consumption metrics that are more reliable than estimated costs, which vary based on enterprise discounts, volume pricing, and provider-specific pricing models.

The goal is to implement one working token tracking chart in complete isolation, ensuring the existing Observatory remains fully functional throughout the implementation process.

## Requirements

### Requirement 1: LLM Token Tracking Chart Implementation

**User Story:** As a developer monitoring Beast Mode LLM usage, I want to see real-time token consumption trends showing input tokens, output tokens, and total usage over time, so that I can understand actual resource consumption patterns and optimize LLM API usage.

#### Acceptance Criteria

1. WHEN the Observatory dashboard loads THEN the "💰 LLM Cost Tracking" chart container SHALL display a functional Chart.js line chart showing token consumption instead of "Loading cost data..." message
2. WHEN token usage data is available THEN the chart SHALL display input tokens, output tokens, and total tokens on the Y-axis and time on the X-axis with appropriate scaling and labels
3. WHEN new token data arrives via WebSocket or HTTP polling THEN the chart SHALL update smoothly using the established HealthChartInitializer pattern
4. WHEN the chart updates THEN it SHALL maintain the last 50 data points and automatically scroll to show the most recent data
5. IF token data is unavailable THEN the chart SHALL display a clear "No token data available" message with appropriate styling

### Requirement 2: Multi-Metric Token Visualization

**User Story:** As a system administrator monitoring LLM costs, I want to see the breakdown between input tokens (what we send) and output tokens (what models generate), so that I can identify whether high usage comes from large prompts or verbose model responses.

#### Acceptance Criteria

1. WHEN displaying token data THEN the chart SHALL show three distinct metrics: input tokens, output tokens, and total tokens as separate lines
2. WHEN token consumption varies THEN input and output tokens SHALL be visually distinguishable with different colors and line styles
3. WHEN hovering over data points THEN tooltips SHALL show exact token counts for input, output, and total with timestamps
4. WHEN token usage spikes occur THEN the chart SHALL clearly show which component (input vs output) is driving the increase
5. IF only partial token data is available THEN the chart SHALL display available metrics and indicate missing data appropriately

### Requirement 3: Data Source Integration with Existing Observatory

**User Story:** As a system operator, I want the token chart to display real LLM usage data from the Observatory's cost tracking engine, so that the visualization reflects actual system token consumption rather than mock data.

#### Acceptance Criteria

1. WHEN the chart requests data THEN it SHALL use the existing `/api/dashboard/all-data` endpoint and extract token data from the costs section
2. WHEN processing API responses THEN the chart SHALL extract input tokens, output tokens, and API call counts from the consolidated data structure
3. WHEN token data is missing or invalid THEN the chart SHALL handle gracefully and display appropriate fallback values
4. WHEN the cost tracking engine is unavailable THEN the chart SHALL show connection status and retry automatically
5. IF no historical token data exists THEN the chart SHALL start with current data and build history over time

### Requirement 4: Visual Design and Professional Integration

**User Story:** As a user viewing the Observatory, I want the token chart to match the existing dashboard aesthetic and provide clear, professional visualization of LLM resource consumption, so that it feels integrated with the overall Observatory experience.

#### Acceptance Criteria

1. WHEN displaying the chart THEN it SHALL use colors consistent with the Observatory theme (blue for input tokens, orange for output tokens, green for total)
2. WHEN showing token counts THEN the chart SHALL use appropriate Y-axis scaling with clear grid lines and labels formatted as "K" for thousands, "M" for millions
3. WHEN displaying time data THEN the X-axis SHALL show readable time labels that update appropriately as data scrolls
4. WHEN the chart is interactive THEN users SHALL be able to hover for detailed token breakdowns and zoom/pan if appropriate
5. IF the chart container is resized THEN the chart SHALL respond appropriately and maintain readability

### Requirement 5: Brownfield Safety and Isolation

**User Story:** As a system operator with a live Observatory system, I want the token chart implementation to be completely isolated and fail-safe, so that any issues with the new chart don't impact existing Observatory functionality or user experience.

#### Acceptance Criteria

1. WHEN chart initialization fails THEN the existing Observatory SHALL continue operating normally with all other features intact including the working health chart
2. WHEN chart updates encounter errors THEN the failure SHALL be contained to the chart container only without affecting WebSocket connections, emoji rain, or other dashboard features
3. WHEN implementing chart code THEN it SHALL be wrapped in try-catch blocks to prevent JavaScript errors from breaking the entire dashboard
4. WHEN the chart is loading THEN existing Observatory features SHALL remain responsive and functional
5. IF Chart.js or chart architecture fails THEN the chart container SHALL gracefully display the existing "Loading..." message without console errors or user disruption

### Requirement 6: Performance and Resource Efficiency

**User Story:** As a system administrator, I want the token chart to perform efficiently and handle token data updates gracefully, so that monitoring LLM usage doesn't itself consume significant resources.

#### Acceptance Criteria

1. WHEN updating chart data THEN the operation SHALL complete within 100ms to maintain smooth real-time updates
2. WHEN handling large token datasets THEN the chart SHALL limit data points to 50 maximum to prevent performance degradation
3. WHEN WebSocket connections fail THEN the chart SHALL continue updating via HTTP polling fallback without user intervention
4. WHEN rapid token updates occur THEN the established debouncing system SHALL prevent excessive re-renders
5. IF token data processing fails THEN the system SHALL display a clear error message and fallback to text-based token display

## Success Criteria

The implementation is complete when:

1. **Functional Chart**: The token chart container displays a working Chart.js line chart with real token consumption data
2. **Multi-Metric Display**: The chart shows input tokens, output tokens, and total tokens as distinct, clearly labeled lines
3. **Real Data**: The chart displays actual LLM token consumption from the Observatory's cost tracking engine
4. **Visual Integration**: The chart matches the Observatory's design aesthetic and user experience
5. **Performance**: Chart updates are smooth and don't impact overall Observatory performance
6. **Error Handling**: All failure modes are handled gracefully with appropriate user feedback

## Anti-Patterns to Avoid

**CRITICAL BROWNFIELD CONSTRAINTS** - The following will break the live system:

1. **Modifying Existing Code**: Don't change any existing Observatory functionality - only ADD token chart initialization
2. **Global JavaScript Changes**: Don't modify existing event handlers, WebSocket code, or emoji rain systems
3. **Breaking Changes to APIs**: Don't modify existing API endpoints or data structures
4. **Uncaught Exceptions**: Don't allow chart errors to propagate and break the dashboard
5. **Resource Conflicts**: Don't interfere with existing Chart.js usage or canvas elements

**Chart Implementation Constraints**:

6. **Duplicate Class Declarations**: Don't create another HealthChartInitializer - create TokenChartInitializer
7. **Complex Dependencies**: Don't depend on Agent 1's architecture - use direct API calls like the health chart
8. **Hardcoded Data**: Don't use mock data - integrate with real Observatory token tracking
9. **Performance Issues**: Don't create memory leaks or excessive update cycles
10. **Visual Inconsistency**: Don't break the established Observatory design patterns

## Dependencies

- Successful Health Chart implementation (already working)
- Observatory cost tracking engine (already implemented)
- `/api/dashboard/all-data` endpoint (already implemented)
- Chart.js library (already loaded in dashboard HTML)
- WebSocket/HTTP polling infrastructure (already implemented)
- Existing brownfield safety patterns (established by health chart)