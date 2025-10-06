🚀 Hybrid Service Discovery Deployment Report
==================================================
Deployment Time: 2025-10-05 10:45:15
Duration: 4.8 seconds

📊 Final Service State:
   Total Services: 4
   🌐 Bonjour Services: 4
   📝 /etc/hosts Services: 0
   🐳 Docker Only: 0

🌐 Service URLs:
   🔴 http://grafana.kiro.local:3002 (bonjour)
   🔴 http://prometheus.kiro.local:9000 (bonjour)
   🔴 http://jaeger.kiro.local:8889 (bonjour)
   🔴 http://monitoring.kiro.local:9000 (bonjour)

📋 Deployment Log:
====================
[10:45:15] INFO: 🚀 Starting Hybrid Service Discovery Deployment
[10:45:15] INFO: ============================================================
[10:45:15] INFO: 🔍 Checking system prerequisites...
[10:45:15] INFO: ✅ Docker: 6 containers running
[10:45:15] INFO: ✅ Redis: Connection successful
[10:45:15] INFO: ✅ Bonjour/mDNS: dns-sd available
[10:45:15] INFO: 🔍 Scanning current service state...
[10:45:16] INFO: 📊 Found 4 services:
[10:45:16] INFO:    🌐 Bonjour: 0
[10:45:16] INFO:    📝 /etc/hosts: 0
[10:45:16] INFO:    🐳 Docker only: 4
[10:45:16] WARN: ⚠️  4 port conflicts detected
[10:45:16] INFO: 🔧 Resolving port conflicts...
[10:45:16] INFO: ⚠️  Conflict: grafana:3000 used by /Applications/Docker.app/Contents/MacOS/com.docker.backend
[10:45:16] INFO: 💡 Suggested alternative for grafana: 8889
[10:45:16] INFO: ⚠️  Conflict: prometheus:9090 used by /Applications/Docker.app/Contents/MacOS/com.docker.backend
[10:45:16] INFO: 💡 Suggested alternative for prometheus: 8889
[10:45:16] INFO: ⚠️  Conflict: jaeger:16686 used by /Applications/Docker.app/Contents/MacOS/com.docker.backend
[10:45:16] INFO: 💡 Suggested alternative for jaeger: 8889
[10:45:16] INFO: ⚠️  Conflict: monitoring:8000 used by /Applications/Docker.app/Contents/MacOS/com.docker.backend
[10:45:16] INFO: 💡 Suggested alternative for monitoring: 8889
[10:45:16] INFO: 🐳 Registering Docker services with Bonjour...
[10:45:20] INFO: ✅ Successfully registered 4 services:
[10:45:20] INFO:    🌐 grafana at grafana.kiro.local
[10:45:20] INFO:    🌐 prometheus at prometheus.kiro.local
[10:45:20] INFO:    🌐 jaeger at jaeger.kiro.local
[10:45:20] INFO:    🌐 monitoring at monitoring.kiro.local
[10:45:20] INFO: 🧪 Running system tests...
[10:45:20] INFO: ✅ Service discovery: 4 services found
[10:45:20] INFO: ✅ Port conflict detection: Working
[10:45:20] INFO: ✅ Bonjour registration: 0 services registered
[10:45:20] INFO: 📋 Generating deployment report...
[10:45:20] INFO: 🎉 Hybrid Service Discovery Deployment Complete!
[10:45:20] INFO: ==================================================
[10:45:20] INFO: ✅ Services registered with Bonjour (.kiro.local)
[10:45:20] INFO: ✅ Backward compatibility maintained (.local)
[10:45:20] INFO: ✅ Port conflicts resolved
[10:45:20] INFO: ✅ Admin dashboard ready