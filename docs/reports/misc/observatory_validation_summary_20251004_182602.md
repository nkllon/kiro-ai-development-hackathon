# Observatory Deployment Validation Report

**Generated:** 2025-10-04T18:26:01.981835

## Summary

- **Total Tests:** 20
- **Passed:** 7
- **Failed:** 13
- **Success Rate:** 35.0%
- **Overall Status:** ❌ FAIL

## Test Results

### ❌ Local Health endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a785130>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T18:26:01.987815

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /ready (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a785b20>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:01.988866

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a7d5520>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:01.990071

### ❌ Local Dashboard endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a71eee0>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:01.990911

### ✅ External Health endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.34s
- **Timestamp:** 2025-10-04T18:26:02.335864

### ✅ External Dashboard endpoint
- **Status:** PASS
- **Details:** Status 200
- **Duration:** 0.54s
- **Timestamp:** 2025-10-04T18:26:02.875757

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:26:02.876390

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:26:02.876408

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:26:02.876452

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T18:26:02.876471

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T18:26:02.877352

### ❌ Process Running
- **Status:** FAIL
- **Details:** No Observatory process found
- **Timestamp:** 2025-10-04T18:26:02.894026

### ❌ Tunnel Process
- **Status:** FAIL
- **Details:** No Cloudflare tunnel process found
- **Timestamp:** 2025-10-04T18:26:02.906700

### ❌ Performance /health
- **Status:** FAIL
- **Details:** Avg response time: 2.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T18:26:02.911412

### ❌ Performance /metrics
- **Status:** FAIL
- **Details:** Avg response time: 3.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T18:26:02.915313

### ❌ Performance /
- **Status:** FAIL
- **Details:** Avg response time: 4.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T18:26:02.923995

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.02s
- **Timestamp:** 2025-10-04T18:26:02.940221

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:02.940905

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:02.941692

### ❌ WebSocket /ws/doctor-status
- **Status:** FAIL
- **Details:** Multiple exceptions: [Errno 61] Connect call failed ('::1', 8888, 0, 0), [Errno 61] Connect call failed ('127.0.0.1', 8888)
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T18:26:02.942854

