# Observatory Deployment Validation Report

**Generated:** 2025-10-04T15:07:51.923697

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
- **Timestamp:** 2025-10-04T15:07:51.936038

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** Status 404
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:51.940422

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** Status 404
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:51.943931

### ✅ Local Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:51.947503

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.37s
- **Timestamp:** 2025-10-04T15:07:52.316533

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.41s
- **Timestamp:** 2025-10-04T15:07:52.730399

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:52.732234

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:52.732267

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:52.732318

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:07:52.732345

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T15:07:52.732791

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 74077)
- **Timestamp:** 2025-10-04T15:07:52.771156

### ✅ Process Resources PID 74077
- **Status:** PASS
- **Details:** 74077   1.1  0.1   0:00.51
- **Timestamp:** 2025-10-04T15:07:52.778580

### ✅ Tunnel Process
- **Status:** PASS
- **Details:** Cloudflare tunnel running (PIDs: 75730, 75880)
- **Timestamp:** 2025-10-04T15:07:52.809022

### ✅ Performance /health
- **Status:** PASS
- **Details:** Avg response time: 0.01s (target: <1.0s)
- **Timestamp:** 2025-10-04T15:07:52.839158

### ✅ Performance /metrics
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T15:07:52.860529

### ✅ Performance /
- **Status:** PASS
- **Details:** Avg response time: 0.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T15:07:52.874686

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.02s
- **Timestamp:** 2025-10-04T15:07:52.893635

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:52.894394

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:07:52.894810

