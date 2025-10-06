
// Observatory HTTP Polling Fallback with Bot Protection
// Generated: 2025-09-26T17:50:15.709823

class ObservatoryPollingFallback {
    constructor() {
        this.baseInterval = 5.0;
        this.maxInterval = 60.0;
        this.backoffMultiplier = 1.5;
        this.jitterFactor = 0.1;
        this.maxRetries = 3;
        this.currentInterval = this.baseInterval;
        this.retryCount = 0;
        this.isPolling = false;
        this.endpoints = {
        "/api/emoji-rain/stats": {
                "interval": 5.0,
                "priority": "high",
                "fallback": true
        },
        "/api/dashboard/all-data": {
                "interval": 10.0,
                "priority": "medium",
                "fallback": true
        },
        "/api/observatory/status": {
                "interval": 15.0,
                "priority": "low",
                "fallback": true
        }
};
        this.activePolls = new Map();
        
        // Bot-safe headers
        this.headers = {
        "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
        "X-Observatory-Client": "internal-polling",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Polling-Reason": "websocket-fallback",
        "X-Observatory-Version": "1.0.0",
        "X-Observatory-Session": "internal-session"
};
        
        console.log('🔧 Observatory Polling Fallback initialized with bot protection');
    }
    
    async startPolling() {
        if (this.isPolling) {
            console.log('⚠️  Polling already active');
            return;
        }
        
        this.isPolling = true;
        console.log('🚀 Starting Observatory polling with bot-safe patterns');
        
        // Start polling for each endpoint
        for (const [endpoint, config] of Object.entries(this.endpoints)) {
            if (config.fallback) {
                this.startEndpointPolling(endpoint, config);
            }
        }
    }
    
    async stopPolling() {
        this.isPolling = false;
        console.log('🛑 Stopping Observatory polling');
        
        // Clear all active polls
        for (const [endpoint, pollId] of this.activePolls) {
            clearInterval(pollId);
        }
        this.activePolls.clear();
    }
    
    startEndpointPolling(endpoint, config) {
        const pollId = setInterval(async () => {
            if (!this.isPolling) {
                clearInterval(pollId);
                return;
            }
            
            try {
                await this.pollEndpoint(endpoint, config);
                this.resetRetryCount();
            } catch (error) {
                console.error(`❌ Polling error for ${endpoint}:`, error);
                this.handlePollingError(endpoint, config);
            }
        }, this.calculateInterval(config.interval));
        
        this.activePolls.set(endpoint, pollId);
        console.log(`📡 Started polling for ${endpoint} with interval ${this.calculateInterval(config.interval)}ms`);
    }
    
    async pollEndpoint(endpoint, config) {
        const url = `${window.location.origin}${endpoint}`;
        
        const response = await fetch(url, {
            method: 'GET',
            headers: this.headers,
            cache: 'no-cache',
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        this.handlePollingResponse(endpoint, data);
        
        return data;
    }
    
    handlePollingResponse(endpoint, data) {
        // Handle successful polling response
        console.log(`✅ Polling success for ${endpoint}:`, data);
        
        // Update dashboard with new data
        this.updateDashboard(endpoint, data);
        
        // Reset retry count on success
        this.resetRetryCount();
    }
    
    handlePollingError(endpoint, config) {
        this.retryCount++;
        
        if (this.retryCount >= this.maxRetries) {
            console.error(`❌ Max retries reached for ${endpoint}, stopping polling`);
            this.stopPolling();
            return;
        }
        
        // Exponential backoff with jitter
        this.currentInterval = Math.min(
            this.currentInterval * this.backoffMultiplier,
            this.maxInterval
        );
        
        const jitter = this.currentInterval * this.jitterFactor * Math.random();
        const finalInterval = this.currentInterval + jitter;
        
        console.log(`⏳ Retrying ${endpoint} in ${finalInterval.toFixed(1)}s (attempt ${this.retryCount}/${this.maxRetries})`);
        
        // Restart polling with new interval
        setTimeout(() => {
            if (this.isPolling) {
                this.startEndpointPolling(endpoint, config);
            }
        }, finalInterval * 1000);
    }
    
    calculateInterval(baseInterval) {
        // Add jitter to prevent thundering herd
        const jitter = baseInterval * this.jitterFactor * Math.random();
        return (baseInterval + jitter) * 1000; // Convert to milliseconds
    }
    
    resetRetryCount() {
        this.retryCount = 0;
        this.currentInterval = this.baseInterval;
    }
    
    updateDashboard(endpoint, data) {
        // Update specific dashboard components based on endpoint
        switch (endpoint) {
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
                console.log(`📊 Dashboard update for ${endpoint}:`, data);
        }
    }
    
    updateEmojiRainStats(data) {
        // Update emoji rain statistics
        if (window.emojiRainManager) {
            window.emojiRainManager.updateStats(data);
        }
    }
    
    updateDashboardData(data) {
        // Update main dashboard data
        if (window.dashboardManager) {
            window.dashboardManager.updateData(data);
        }
    }
    
    updateObservatoryStatus(data) {
        // Update Observatory status indicators
        if (window.statusManager) {
            window.statusManager.updateStatus(data);
        }
    }
    
    // Health check method
    getHealthStatus() {
        return {
            isPolling: this.isPolling,
            activePolls: this.activePolls.size,
            currentInterval: this.currentInterval,
            retryCount: this.retryCount,
            endpoints: Array.from(this.activePolls.keys())
        };
    }
}

// Initialize polling fallback when WebSocket fails
function initializePollingFallback() {
    console.log('🔧 Initializing Observatory polling fallback');
    
    // Check if WebSocket is available
    if (window.WebSocket && window.location.protocol === 'https:') {
        // Try WebSocket first
        const wsUrl = `wss://${window.location.host}/ws/emoji-rain`;
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {
            console.log('✅ WebSocket connected, disabling polling fallback');
            ws.close();
            return; // WebSocket working, no need for polling
        };
        
        ws.onerror = function(error) {
            console.log('❌ WebSocket failed, enabling polling fallback');
            startPollingFallback();
        };
        
        ws.onclose = function() {
            console.log('🔌 WebSocket closed, enabling polling fallback');
            startPollingFallback();
        };
        
        // Timeout after 5 seconds
        setTimeout(() => {
            if (ws.readyState === WebSocket.CONNECTING) {
                console.log('⏰ WebSocket timeout, enabling polling fallback');
                ws.close();
                startPollingFallback();
            }
        }, 5000);
    } else {
        console.log('🔌 WebSocket not available, using polling fallback');
        startPollingFallback();
    }
}

function startPollingFallback() {
    if (!window.observatoryPolling) {
        window.observatoryPolling = new ObservatoryPollingFallback();
        window.observatoryPolling.startPolling();
        
        // Add to global scope for debugging
        window.pollingHealth = () => window.observatoryPolling.getHealthStatus();
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePollingFallback);
} else {
    initializePollingFallback();
}
