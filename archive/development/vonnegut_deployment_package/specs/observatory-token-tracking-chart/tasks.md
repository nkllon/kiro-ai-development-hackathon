# Implementation Plan

- [x] 1. Create TokenChartInitializer class with brownfield safety
  - Implement Chart.js instance creation for multi-metric token visualization
  - Add comprehensive error handling and graceful degradation
  - Create chart configuration with Observatory theme colors for input/output/total tokens
  - Include isolated initialization that won't interfere with existing health chart
  - _Requirements: 1.1, 2.1, 5.1, 5.3_

- [x] 2. Implement token data extraction and windowing functions
  - Create data transformation logic to extract input tokens, output tokens, and total tokens from API response
  - **CRITICAL**: Specify requirement for data store to support windowing functions (e.g., SQL windowing, Redis Streams, or similar) to return 10-minute historical data windows
  - Add logic to append new real-time data points to existing historical window
  - Handle missing or invalid token data with appropriate fallback values
  - **NOTE**: Backend time-series storage implementation is a separate dependency - this task defines the interface requirement
  - _Requirements: 2.2, 2.3, 3.1, 3.2, 3.3_

- [x] 3. Add token chart initialization to dashboard with surgical precision
  - Insert TokenChartInitializer call in separate DOM ready handler to avoid conflicts
  - Wrap all token chart code in try-catch blocks to prevent JavaScript errors
  - Ensure existing Observatory features (health chart, emoji rain) remain completely unaffected
  - Test chart displays real LLM token consumption data with historical context
  - _Requirements: 1.1, 1.2, 5.1, 5.2, 5.4_

- [x] 4. Implement multi-metric visualization and real-time updates
  - Configure chart to display three distinct token metrics (input, output, total) with different colors
  - Add Observatory theme colors (blue for input, orange for output, green for total)
  - Implement time-series display with 50 data point limit and auto-scrolling
  - Add professional hover interactions and responsive design for token count formatting
  - _Requirements: 1.3, 1.4, 2.1, 2.2, 4.1, 4.2, 4.3, 4.4_

- [x] 5. Test brownfield deployment and validate system stability
  - Verify existing Observatory functionality (health chart, emoji rain, WebSocket) remains intact during and after deployment
  - Test token chart updates smoothly with real LLM usage data and historical windowing
  - Confirm chart initialization failures don't break the dashboard or affect other charts
  - Validate error scenarios fail gracefully without impacting existing Observatory features
  - _Requirements: 5.1, 5.2, 5.5, 6.1, 6.2, 6.3_