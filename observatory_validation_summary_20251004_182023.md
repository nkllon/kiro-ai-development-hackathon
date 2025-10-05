# Observatory Deployment Validation Report

**Generated:** 2025-10-04T18:20:22.640046

## Summary

- **Total Tests:** 21
- **Passed:** 9
- **Failed:** 12
- **Success Rate:** 42.9%
- **Overall Status:** ❌ FAIL

## Test Results

### ❌ Local Health endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a569130>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:22.645061

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /ready (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a569b20>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:22.646040

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a5b9520>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:22.646760

### ❌ Local Dashboard endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a501ee0>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:22.647555

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.12s
- **Timestamp:** 2025-10-04T18:20:22.762696

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.59s
- **Timestamp:** 2025-10-04T18:20:23.355818

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:20:23.356290

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:20:23.356304

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:20:23.356315

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:20:23.356324

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T18:20:23.357229

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 67774)
- **Timestamp:** 2025-10-04T18:20:23.377208

### ✅ Process Resources PID 67774
- **Status:** PASS
- **Details:** 67774   0.0  0.0   0:00.02
- **Timestamp:** 2025-10-04T18:20:23.382939

### ❌ Tunnel Process
- **Status:** FAIL
- **Details:** No Cloudflare tunnel process found
- **Timestamp:** 2025-10-04T18:20:23.396229

### ❌ Performance /health
- **Status:** FAIL
- **Details:** Avg response time: 2.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T18:20:23.401847

### ❌ Performance /metrics
- **Status:** FAIL
- **Details:** Avg response time: 3.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T18:20:23.405739

### ❌ Performance /
- **Status:** FAIL
- **Details:** Avg response time: 4.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T18:20:23.409994

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.03s
- **Timestamp:** 2025-10-04T18:20:23.440553

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:23.441271

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:23.441821

### ❌ WebSocket /ws/doctor-status
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:20:23.442463

