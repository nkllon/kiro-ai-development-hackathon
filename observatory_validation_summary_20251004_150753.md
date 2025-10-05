# Observatory Deployment Validation Report

**Generated:** 2025-10-04T15:07:52.478639

## Summary

- **Total Tests:** 20
- **Passed:** 15
- **Failed:** 5
- **Success Rate:** 75.0%
- **Overall Status:** ❌ FAIL

## Test Results

### ✅ Local Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T15:07:52.485424

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** Status 404
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:52.487329

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** Status 404
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:52.489069

### ✅ Local Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:52.490690

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.27s
- **Timestamp:** 2025-10-04T15:07:52.757204

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.86s
- **Timestamp:** 2025-10-04T15:07:53.617969

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:53.618438

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:53.618456

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:53.618467

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:53.618477

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T15:07:53.618802

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 74077)
- **Timestamp:** 2025-10-04T15:07:53.634790

### ✅ Process Resources PID 74077
- **Status:** PASS
- **Details:** 74077   0.7  0.1   0:00.53
- **Timestamp:** 2025-10-04T15:07:53.637911

### ✅ Tunnel Process
- **Status:** PASS
- **Details:** Cloudflare tunnel running (PIDs: 75730, 75880)
- **Timestamp:** 2025-10-04T15:07:53.652196

### ✅ Performance /health
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T15:07:53.662750

### ✅ Performance /metrics
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T15:07:53.668745

### ✅ Performance /
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T15:07:53.674394

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T15:07:53.684349

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:53.684779

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:53.685097

