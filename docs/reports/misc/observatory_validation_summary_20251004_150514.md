# Observatory Deployment Validation Report

**Generated:** 2025-10-04T15:05:12.112412

## Summary

- **Total Tests:** 20
- **Passed:** 7
- **Failed:** 13
- **Success Rate:** 35.0%
- **Overall Status:** ❌ FAIL

## Test Results

### ❌ Local Health endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1082fd190>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.05s
- **Timestamp:** 2025-10-04T15:05:12.164969

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /ready (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x1082fdb80>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:05:12.168167

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10834f580>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:05:12.170814

### ❌ Local Dashboard endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x108294f40>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:05:12.173432

### ❌ External Health endpoint
- **Status:** FAIL
- **Details:** Status 502
- **Duration:** 1.88s
- **Timestamp:** 2025-10-04T15:05:14.055888

### ❌ External Dashboard endpoint
- **Status:** FAIL
- **Details:** Status 502
- **Duration:** 0.28s
- **Timestamp:** 2025-10-04T15:05:14.339471

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:05:14.339894

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:05:14.339911

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:05:14.339922

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T15:05:14.339931

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T15:05:14.340189

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 71089)
- **Timestamp:** 2025-10-04T15:05:14.353827

### ✅ Process Resources PID 71089
- **Status:** PASS
- **Details:** 71089   0.0  0.2   0:00.42
- **Timestamp:** 2025-10-04T15:05:14.358608

### ❌ Tunnel Process
- **Status:** FAIL
- **Details:** No Cloudflare tunnel process found
- **Timestamp:** 2025-10-04T15:05:14.372590

### ❌ Performance /health
- **Status:** FAIL
- **Details:** Avg response time: 2.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T15:05:14.378420

### ❌ Performance /metrics
- **Status:** FAIL
- **Details:** Avg response time: 3.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T15:05:14.382777

### ❌ Performance /
- **Status:** FAIL
- **Details:** Avg response time: 4.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T15:05:14.397211

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.02s
- **Timestamp:** 2025-10-04T15:05:14.419894

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:05:14.420213

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T15:05:14.420502

