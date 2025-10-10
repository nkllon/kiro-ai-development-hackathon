# Observatory Deployment Validation Report

**Generated:** 2025-10-04T15:36:31.460349

## Summary

- **Total Tests:** 21
- **Passed:** 21
- **Failed:** 0
- **Success Rate:** 100.0%
- **Overall Status:** ✅ PASS

## Test Results

### ✅ Local Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 5.77s
- **Timestamp:** 2025-10-04T15:36:37.230025

### ✅ Local Readiness endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T15:36:37.237126

### ✅ Local Metrics endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:37.241533

### ✅ Local Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.03s
- **Timestamp:** 2025-10-04T15:36:37.267627

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.19s
- **Timestamp:** 2025-10-04T15:36:37.453973

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.35s
- **Timestamp:** 2025-10-04T15:36:37.803580

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:37.803987

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:37.804002

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:37.804013

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:36:37.804022

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T15:36:37.804276

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 76994)
- **Timestamp:** 2025-10-04T15:36:37.818422

### ✅ Process Resources PID 76994
- **Status:** PASS
- **Details:** 76994  12.7  0.5   0:28.73
- **Timestamp:** 2025-10-04T15:36:37.821233

### ✅ Tunnel Process
- **Status:** PASS
- **Details:** Cloudflare tunnel running (PIDs: 82792)
- **Timestamp:** 2025-10-04T15:36:37.832938

### ✅ Performance /health
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T15:36:37.843766

### ✅ Performance /metrics
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T15:36:37.857236

### ✅ Performance /
- **Status:** PASS
- **Details:** Avg response time: 0.02s (target: <3.0s)
- **Timestamp:** 2025-10-04T15:36:37.958301

### ✅ WebSocket /ws/observatory
- **Status:** PASS
- **Details:** Connection and message exchange successful
- **Duration:** 0.02s
- **Timestamp:** 2025-10-04T15:36:37.973687

### ✅ WebSocket /ws/emoji-rain
- **Status:** PASS
- **Details:** Connection and message exchange successful
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:37.976222

### ✅ WebSocket /ws/anomalies
- **Status:** PASS
- **Details:** Connection and message exchange successful
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:37.979274

### ✅ WebSocket /ws/doctor-status
- **Status:** PASS
- **Details:** Connection and message exchange successful
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:36:37.984605

