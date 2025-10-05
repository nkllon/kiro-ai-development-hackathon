# Observatory Deployment Validation Report

**Generated:** 2025-10-04T14:08:34.712766

## Summary

- **Total Tests:** 20
- **Passed:** 7
- **Failed:** 13
- **Success Rate:** 35.0%
- **Overall Status:** ❌ FAIL

## Test Results

### ❌ Local Health endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a199160>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T14:08:34.717282

### ❌ Local Readiness endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /ready (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a199b50>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T14:08:34.718084

### ❌ Local Metrics endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: /metrics (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a1ea550>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T14:08:34.718785

### ❌ Local Dashboard endpoint
- **Status:** FAIL
- **Details:** HTTPConnectionPool(host='localhost', port=8888): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x10a130400>: Failed to establish a new connection: [Errno 61] Connection refused'))
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T14:08:34.719705

### ❌ External Health endpoint
- **Status:** FAIL
- **Details:** Status 530
- **Duration:** 0.10s
- **Timestamp:** 2025-10-04T14:08:34.819572

### ❌ External Dashboard endpoint
- **Status:** FAIL
- **Details:** Status 530
- **Duration:** 0.13s
- **Timestamp:** 2025-10-04T14:08:34.948109

### ✅ Data Directory metrics
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T14:08:34.948469

### ✅ Data Directory dashboards
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T14:08:34.948481

### ✅ Data Directory logs
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T14:08:34.948489

### ✅ Data Directory config
- **Status:** PASS
- **Details:** Directory exists and is accessible
- **Timestamp:** 2025-10-04T14:08:34.948497

### ✅ Data Write Permissions
- **Status:** PASS
- **Details:** Can write to data directories
- **Timestamp:** 2025-10-04T14:08:34.948905

### ✅ Process Running
- **Status:** PASS
- **Details:** Observatory process found (PIDs: 46011)
- **Timestamp:** 2025-10-04T14:08:34.963287

### ✅ Process Resources PID 46011
- **Status:** PASS
- **Details:** 46011   0.0  0.4   0:00.47
- **Timestamp:** 2025-10-04T14:08:34.966648

### ❌ Tunnel Process
- **Status:** FAIL
- **Details:** No Cloudflare tunnel process found
- **Timestamp:** 2025-10-04T14:08:34.982329

### ❌ Performance /health
- **Status:** FAIL
- **Details:** Avg response time: 2.00s (target: <1.0s)
- **Timestamp:** 2025-10-04T14:08:34.995653

### ❌ Performance /metrics
- **Status:** FAIL
- **Details:** Avg response time: 3.00s (target: <2.0s)
- **Timestamp:** 2025-10-04T14:08:35.006534

### ❌ Performance /
- **Status:** FAIL
- **Details:** Avg response time: 4.00s (target: <3.0s)
- **Timestamp:** 2025-10-04T14:08:35.015980

### ❌ WebSocket /ws/observatory
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.06s
- **Timestamp:** 2025-10-04T14:08:35.074876

### ❌ WebSocket /ws/emoji-rain
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.00s
- **Timestamp:** 2025-10-04T14:08:35.076643

### ❌ WebSocket /ws/anomalies
- **Status:** FAIL
- **Details:** create_connection() got an unexpected keyword argument 'timeout'
- **Duration:** 0.01s
- **Timestamp:** 2025-10-04T14:08:35.085461

