# Observatory Deployment Validation Report

**Generated:** 2025-10-04T15:36:10.743089

## Summary

- **Total Tests:** 21
- **Passed:** 17
- **Failed:** 4
- **Success Rate:** 81.0%
- **Overall Status:** ❌ FAIL

## Test Results

### ✅ Local Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 1.75s
- **Timestamp:** 2025-10-04T15:36:12.488590

### ✅ Local Readiness endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:12.492012

### ✅ Local Metrics endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T15:36:12.498855

### ✅ Local Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.03s
- **Timestamp:** 2025-10-04T15:36:12.532413

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.22s
- **Timestamp:** 2025-10-04T15:36:12.749937

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.47s
- **Timestamp:** 2025-10-04T15:36:13.221518

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:13.222576

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:13.222632

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:13.222658

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:13.222685

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T15:36:13.223196

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 76994)
- **Timestamp:** 2025-10-04T15:36:13.265335

### ✅ Process Resources PID 76994
- **Status:** PASS
- **Details:** 76994  12.1  0.6   0:28.24
- **Timestamp:** 2025-10-04T15:36:13.273314

### ✅ Tunnel Process
- **Status:** PASS
- **Details:** Cloudflare tunnel running (PIDs: 82792)
- **Timestamp:** 2025-10-04T15:36:13.298174

### ✅ Performance /health
- **Status:** PASS
- **Details:** Avg response time: 0.01s (target: <1.0s)
- **Timestamp:** 2025-10-04T15:36:13.330974

### ✅ Performance /metrics
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T15:36:13.353479

### ✅ Performance /
- **Status:** PASS
- **Details:** Avg response time: 0.82s (target: <3.0s)
- **Timestamp:** 2025-10-04T15:36:17.470649

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.02s
- **Timestamp:** 2025-10-04T15:36:17.494942

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:17.495527

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:17.496060

### ❌ WebSocket /ws/doctor-status
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:17.496547

