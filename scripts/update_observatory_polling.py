#!/usr/bin/env python3
"""
Update Observatory HTTP Polling Implementation

This script updates the Observatory dashboard to use bot-safe headers
and intelligent polling patterns to prevent triggering bot protection.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_polling_config():
    """Load polling configuration from generated files"""
    config_dir = Path("config/bot_protection")
    
    with open(config_dir / "http_polling_headers.json", "r") as f:
        headers = json.load(f)
    
    with open(config_dir / "polling_strategy.json", "r") as f:
        strategy = json.load(f)
    
    return headers, strategy

def generate_updated_polling_js(headers: Dict[str, str], strategy: Dict[str, Any]):
    """Generate updated JavaScript for Observatory polling"""
    
    js_code = f"""
// Observatory HTTP Polling Fallback with Bot Protection
// Generated: {datetime.now().isoformat()}

class ObservatoryPollingFallback {{
    constructor() {{
        this.baseInterval = {strategy['base_interval']};
        this.maxInterval = {strategy['max_interval']};
        this.backoffMultiplier = {strategy['backoff_multiplier']};
        this.jitterFactor = {strategy['jitter_factor']};
        this.maxRetries = {strategy['max_retries']};
        this.currentInterval = this.baseInterval;
        this.retryCount = 0;
        this.isPolling = false;
        this.endpoints = {json.dumps(strategy['endpoints'], indent=8)};
        this.activePolls = new Map();
        
        // Bot-safe headers
        this.headers = {json.dumps(headers, indent=8)};
        
        console.log('🔧 Observatory Polling Fallback initialized with bot protection');
    }}
    
    async startPolling() {{
        if (this.isPolling) {{
            console.log('⚠️  Polling already active');
            return;
        }}
        
        this.isPolling = true;
        console.log('🚀 Starting Observatory polling with bot-safe patterns');
        
        // Start polling for each endpoint
        for (const [endpoint, config] of Object.entries(this.endpoints)) {{
            if (config.fallback) {{
                this.startEndpointPolling(endpoint, config);
            }}
        }}
    }}
    
    async stopPolling() {{
        this.isPolling = false;
        console.log('🛑 Stopping Observatory polling');
        
        // Clear all active polls
        for (const [endpoint, pollId] of this.activePolls) {{
            clearInterval(pollId);
        }}
        this.activePolls.clear();
    }}
    
    startEndpointPolling(endpoint, config) {{
        const pollId = setInterval(async () => {{
            if (!this.isPolling) {{
                clearInterval(pollId);
                return;
            }}
            
            try {{
                await this.pollEndpoint(endpoint, config);
                this.resetRetryCount();
            }} catch (error) {{
                console.error(`❌ Polling error for ${{endpoint}}:`, error);
                this.handlePollingError(endpoint, config);
            }}
        }}, this.calculateInterval(config.interval));
        
        this.activePolls.set(endpoint, pollId);
        console.log(`📡 Started polling for ${{endpoint}} with interval ${{this.calculateInterval(config.interval)}}ms`);
    }}
    
    async pollEndpoint(endpoint, config) {{
        const url = `${{window.location.origin}}${{endpoint}}`;
        
        const response = await fetch(url, {{
            method: 'GET',
            headers: this.headers,
            cache: 'no-cache',
            credentials: 'same-origin'
        }});
        
        if (!response.ok) {{
            throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
        }}
        
        const data = await response.json();
        this.handlePollingResponse(endpoint, data);
        
        return data;
    }}
    
    handlePollingResponse(endpoint, data) {{
        // Handle successful polling response
        console.log(`✅ Polling success for ${{endpoint}}:`, data);
        
        // Update dashboard with new data
        this.updateDashboard(endpoint, data);
        
        // Reset retry count on success
        this.resetRetryCount();
    }}
    
    handlePollingError(endpoint, config) {{
        this.retryCount++;
        
        if (this.retryCount >= this.maxRetries) {{
            console.error(`❌ Max retries reached for ${{endpoint}}, stopping polling`);
            this.stopPolling();
            return;
        }}
        
        // Exponential backoff with jitter
        this.currentInterval = Math.min(
            this.currentInterval * this.backoffMultiplier,
            this.maxInterval
        );
        
        const jitter = this.currentInterval * this.jitterFactor * Math.random();
        const finalInterval = this.currentInterval + jitter;
        
        console.log(`⏳ Retrying ${{endpoint}} in ${{finalInterval.toFixed(1)}}s (attempt ${{this.retryCount}}/${{this.maxRetries}})`);
        
        // Restart polling with new interval
        setTimeout(() => {{
            if (this.isPolling) {{
                this.startEndpointPolling(endpoint, config);
            }}
        }}, finalInterval * 1000);
    }}
    
    calculateInterval(baseInterval) {{
        // Add jitter to prevent thundering herd
        const jitter = baseInterval * this.jitterFactor * Math.random();
        return (baseInterval + jitter) * 1000; // Convert to milliseconds
    }}
    
    resetRetryCount() {{
        this.retryCount = 0;
        this.currentInterval = this.baseInterval;
    }}
    
    updateDashboard(endpoint, data) {{
        // Update specific dashboard components based on endpoint
        switch (endpoint) {{
            case '/api/emoji-rain/stats':
                this.updateEmojiRainStats(data);
                break;
            case '/api/dashboard/all-data':
                this.updateDashboardData(data);
                break;
            case '/api/observatory/status':
                this.updateObservatoryStatus(data);
                break;
            default:
                console.log(`📊 Dashboard update for ${{endpoint}}:`, data);
        }}
    }}
    
    updateEmojiRainStats(data) {{
        // Update emoji rain statistics
        if (window.emojiRainManager) {{
            window.emojiRainManager.updateStats(data);
        }}
    }}
    
    updateDashboardData(data) {{
        // Update main dashboard data
        if (window.dashboardManager) {{
            window.dashboardManager.updateData(data);
        }}
    }}
    
    updateObservatoryStatus(data) {{
        // Update Observatory status indicators
        if (window.statusManager) {{
            window.statusManager.updateStatus(data);
        }}
    }}
    
    // Health check method
    getHealthStatus() {{
        return {{
            isPolling: this.isPolling,
            activePolls: this.activePolls.size,
            currentInterval: this.currentInterval,
            retryCount: this.retryCount,
            endpoints: Array.from(this.activePolls.keys())
        }};
    }}
}}

// Initialize polling fallback when WebSocket fails
function initializePollingFallback() {{
    console.log('🔧 Initializing Observatory polling fallback');
    
    // Check if WebSocket is available
    if (window.WebSocket && window.location.protocol === 'https:') {{
        // Try WebSocket first
        const wsUrl = `wss://${{window.location.host}}/ws/emoji-rain`;
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {{
            console.log('✅ WebSocket connected, disabling polling fallback');
            ws.close();
            return; // WebSocket working, no need for polling
        }};
        
        ws.onerror = function(error) {{
            console.log('❌ WebSocket failed, enabling polling fallback');
            startPollingFallback();
        }};
        
        ws.onclose = function() {{
            console.log('🔌 WebSocket closed, enabling polling fallback');
            startPollingFallback();
        }};
        
        // Timeout after 5 seconds
        setTimeout(() => {{
            if (ws.readyState === WebSocket.CONNECTING) {{
                console.log('⏰ WebSocket timeout, enabling polling fallback');
                ws.close();
                startPollingFallback();
            }}
        }}, 5000);
    }} else {{
        console.log('🔌 WebSocket not available, using polling fallback');
        startPollingFallback();
    }}
}}

function startPollingFallback() {{
    if (!window.observatoryPolling) {{
        window.observatoryPolling = new ObservatoryPollingFallback();
        window.observatoryPolling.startPolling();
        
        // Add to global scope for debugging
        window.pollingHealth = () => window.observatoryPolling.getHealthStatus();
    }}
}}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initializePollingFallback);
}} else {{
    initializePollingFallback();
}}
"""
    
    return js_code

def main():
    """Main script to update Observatory polling"""
    print("🔧 Observatory HTTP Polling Update")
    print("=" * 50)
    
    try:
        # Load configuration
        headers, strategy = load_polling_config()
        print("✅ Loaded polling configuration")
        
        # Generate updated JavaScript
        js_code = generate_updated_polling_js(headers, strategy)
        
        # Save updated JavaScript
        output_dir = Path("src/beast_mode/observatory/static/js")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "observatory_polling_fallback.js", "w") as f:
            f.write(js_code)
        
        print(f"✅ Updated polling JavaScript saved to {output_dir}/observatory_polling_fallback.js")
        
        # Generate HTML snippet for inclusion
        html_snippet = f"""
<!-- Observatory HTTP Polling Fallback -->
<script src="/static/js/observatory_polling_fallback.js"></script>
<script>
// Initialize polling fallback
document.addEventListener('DOMContentLoaded', function() {{
    console.log('🔧 Observatory polling fallback loaded');
}});
</script>
"""
        
        with open(output_dir / "polling_fallback_snippet.html", "w") as f:
            f.write(html_snippet)
        
        print(f"✅ HTML snippet saved to {output_dir}/polling_fallback_snippet.html")
        
        print(f"\n📋 Implementation Summary:")
        print(f"   • Bot-safe headers configured")
        print(f"   • Intelligent polling strategy implemented")
        print(f"   • Exponential backoff with jitter")
        print(f"   • Rate limiting compliance")
        print(f"   • WebSocket fallback detection")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Include polling_fallback_snippet.html in Observatory dashboard")
        print(f"   2. Test polling fallback functionality")
        print(f"   3. Monitor for bot protection triggers")
        print(f"   4. Verify WebSocket connectivity through tunnel")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error updating Observatory polling: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

