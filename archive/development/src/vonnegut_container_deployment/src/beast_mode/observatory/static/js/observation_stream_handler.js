/**
 * Observatory Observation Stream Handler
 * Captures real-time unstructured observations from Beastly Modules
 * Part of the Living Observatory Dashboard - "Ace Reporter" system
 */

class ObservationStreamHandler {
    constructor() {
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.websocket = null;
        this.eventBuffer = [];
        this.maxBufferSize = 100;
        this.correlationMap = new Map(); // Links events to metric changes
        
        // Event type emoji mapping
        this.emojiMap = {
            'certificate_lock': '🔒',
            'websocket_connect': '🔌',
            'websocket_disconnect': '🔌❌',
            'cache_invalidate': '🗑️',
            'database_query': '🗄️',
            'api_request': '📡',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
            'performance': '⚡',
            'security': '🛡️',
            'deployment': '🚀',
            'backup': '💾',
            'maintenance': '🔧',
            'monitoring': '👁️',
            'default': '📊'
        };
        
        console.log('🎬 ObservationStreamHandler initialized - Ready for live reporting!');
    }
    
    /**
     * Initialize the observation stream connection
     */
    async initialize() {
        try {
            await this.connectWebSocket();
            this.setupEventHandlers();
            this.startHeartbeat();
            console.log('🎬 Observation stream ready - "Ace Reporter" mode activated!');
        } catch (error) {
            console.error('❌ Failed to initialize observation stream:', error);
            this.fallbackToPolling();
        }
    }
    
    /**
     * Connect to WebSocket for real-time observations
     */
    async connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/observations`;
        
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(wsUrl);
                
                this.websocket.onopen = () => {
                    console.log('🎬 Observation WebSocket connected - Live reporting active!');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.reconnectDelay = 1000;
                    resolve();
                };
                
                this.websocket.onmessage = (event) => {
                    this.handleObservationEvent(JSON.parse(event.data));
                };
                
                this.websocket.onclose = () => {
                    console.log('🔌 Observation WebSocket closed');
                    this.isConnected = false;
                    this.scheduleReconnect();
                };
                
                this.websocket.onerror = (error) => {
                    console.error('❌ Observation WebSocket error:', error);
                    reject(error);
                };
                
                // Timeout after 5 seconds
                setTimeout(() => {
                    if (this.websocket.readyState === WebSocket.CONNECTING) {
                        this.websocket.close();
                        reject(new Error('WebSocket connection timeout'));
                    }
                }, 5000);
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * Handle incoming observation events from Beastly Modules
     */
    handleObservationEvent(event) {
        try {
            // Add timestamp if not present
            if (!event.timestamp) {
                event.timestamp = new Date().toISOString();
            }
            
            // Add emoji if not present
            if (!event.emoji) {
                event.emoji = this.getEmojiForEvent(event);
            }
            
            // Add to buffer
            this.eventBuffer.unshift(event);
            if (this.eventBuffer.length > this.maxBufferSize) {
                this.eventBuffer.pop();
            }
            
            // Update activity feed
            this.updateActivityFeed(event);
            
            // Feed event to correlation engine
            if (window.correlationEngine) {
                window.correlationEngine.addEvent(event);
            }
            
            // Check for metric correlations (legacy)
            this.checkMetricCorrelation(event);
            
            console.log('📰 New observation:', event.message, event.emoji);
            
        } catch (error) {
            console.error('❌ Error handling observation event:', error);
        }
    }
    
    /**
     * Get appropriate emoji for event type
     */
    getEmojiForEvent(event) {
        if (event.event_type && this.emojiMap[event.event_type]) {
            return this.emojiMap[event.event_type];
        }
        
        if (event.severity) {
            switch (event.severity) {
                case 'error': return '❌';
                case 'warning': return '⚠️';
                case 'success': return '✅';
                case 'info': return 'ℹ️';
                default: return this.emojiMap.default;
            }
        }
        
        return this.emojiMap.default;
    }
    
    /**
     * Update the activity feed with new observation
     */
    updateActivityFeed(event) {
        // Use the ActivityFeedRenderer if available
        if (window.activityFeedRenderer) {
            window.activityFeedRenderer.addEvent(event);
        } else {
            // Fallback to basic display
            console.log('📰 Observation (no renderer):', event.message, event.emoji);
        }
    }
    

    
    /**
     * Get color for severity level
     */
    getSeverityColor(severity) {
        switch (severity) {
            case 'error': return '#e74c3c';
            case 'warning': return '#f39c12';
            case 'success': return '#2ecc71';
            case 'info': return '#3498db';
            default: return '#95a5a6';
        }
    }
    
    /**
     * Format context object for display
     */
    formatContext(context) {
        if (typeof context === 'string') return context;
        
        return Object.entries(context)
            .map(([key, value]) => `${key}: ${value}`)
            .join(' • ');
    }
    
    /**
     * Show detailed event information
     */
    showEventDetails(event) {
        // Create modal or expand event details
        console.log('📋 Event details:', event);
        
        // For now, just log to console
        // TODO: Implement modal or sidebar details view
    }
    
    /**
     * Check for correlations between events and metric changes
     */
    checkMetricCorrelation(event) {
        // Store event with correlation ID for later matching
        if (event.correlation_id) {
            this.correlationMap.set(event.correlation_id, {
                event: event,
                timestamp: Date.now()
            });
            
            // Clean up old correlations (older than 5 minutes)
            const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
            for (const [id, data] of this.correlationMap.entries()) {
                if (data.timestamp < fiveMinutesAgo) {
                    this.correlationMap.delete(id);
                }
            }
        }
    }
    
    /**
     * Schedule WebSocket reconnection with exponential backoff
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached, falling back to polling');
            this.fallbackToPolling();
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
        
        console.log(`🔄 Reconnecting observation stream in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            this.connectWebSocket().catch(() => {
                this.scheduleReconnect();
            });
        }, delay);
    }
    
    /**
     * Fallback to HTTP polling when WebSocket fails
     */
    fallbackToPolling() {
        console.log('📡 Falling back to HTTP polling for observations');
        
        // Poll for observations every 10 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/observations/recent', {
                    headers: {
                        'X-Observatory-Client': 'observation-stream',
                        'Accept': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const observations = await response.json();
                    observations.forEach(obs => this.handleObservationEvent(obs));
                }
            } catch (error) {
                console.error('❌ Polling error:', error);
            }
        }, 10000);
    }
    
    /**
     * Setup event handlers for DOM interactions
     */
    setupEventHandlers() {
        // Handle activity feed interactions
        document.addEventListener('DOMContentLoaded', () => {
            this.ensureActivityFeedExists();
        });
    }
    
    /**
     * Ensure activity feed container exists in DOM
     */
    ensureActivityFeedExists() {
        // The ActivityFeedRenderer will handle creating the feed container
        // We just need to make sure it has a place to render
        let activityFeed = document.getElementById('activityFeed');
        if (!activityFeed) {
            // Create a simple container for the ActivityFeedRenderer
            const container = document.createElement('div');
            container.id = 'activityFeedContainer';
            container.style.cssText = `
                position: fixed;
                top: 140px;
                right: 20px;
                width: 380px;
                max-height: 70vh;
                z-index: 999;
            `;
            
            // Create the feed element that ActivityFeedRenderer expects
            container.innerHTML = '<div id="activityFeed"></div>';
            document.body.appendChild(container);
        }
    }
    
    /**
     * Start heartbeat to maintain connection
     */
    startHeartbeat() {
        setInterval(() => {
            if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Ping every 30 seconds
    }
    
    /**
     * Get current observation buffer
     */
    getObservations() {
        return [...this.eventBuffer];
    }
    
    /**
     * Get connection status
     */
    getStatus() {
        return {
            connected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            bufferSize: this.eventBuffer.length,
            correlations: this.correlationMap.size
        };
    }
}

// Initialize observation stream handler
let observationStreamHandler = null;

function initializeObservationStream() {
    if (!observationStreamHandler) {
        observationStreamHandler = new ObservationStreamHandler();
        observationStreamHandler.initialize();
        
        // Add to global scope for debugging
        window.observationStream = observationStreamHandler;
        window.getObservationStatus = () => observationStreamHandler.getStatus();
    }
}

// Auto-initialize when DOM is ready
console.log('📡 ObservationStreamHandler script loaded!');
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeObservationStream);
} else {
    initializeObservationStream();
}