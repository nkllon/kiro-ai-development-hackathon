/**
 * Observatory Activity Feed Renderer
 * Creates beautiful, interactive displays for real-time system observations
 * Part of the Living Observatory Dashboard - "Ace Reporter" visual system
 */

class ActivityFeedRenderer {
    constructor(containerId = 'activityFeed') {
        this.containerId = containerId;
        this.container = null;
        this.maxEvents = 50;
        this.eventHistory = [];
        this.filterSettings = {
            severity: 'all',
            module: 'all',
            eventType: 'all',
            hideBoringEvents: true // Default to hiding boring events
        };
        
        // Define boring/noisy event types to filter out by default
        this.boringEventTypes = new Set([
            'websocket_connect',
            'websocket_disconnect', 
            'emoji_rain_connect',
            'emoji_rain_disconnect',
            'heartbeat',
            'ping',
            'pong',
            'health_check',
            'status_update',
            'monitoring'
        ]);
        
        // Define boring modules that generate too much noise
        this.boringModules = new Set([
            'EmojiRainEngine',
            'WebSocketManager',
            'HealthChecker',
            'StatusMonitor',
            'MetricsCollector'
        ]);
        this.isAutoScroll = true;
        this.animationQueue = [];
        this.isProcessingQueue = false;
        
        // Event type categories for filtering and styling
        this.eventCategories = {
            'system': {
                color: '#3498db',
                icon: '⚙️',
                types: ['system_health_check', 'startup', 'shutdown']
            },
            'network': {
                color: '#2ecc71',
                icon: '🌐',
                types: ['websocket_connect', 'websocket_disconnect', 'api_request']
            },
            'security': {
                color: '#e74c3c',
                icon: '🛡️',
                types: ['certificate_lock', 'authentication', 'authorization']
            },
            'performance': {
                color: '#f39c12',
                icon: '⚡',
                types: ['performance', 'cache_invalidate', 'database_query']
            },
            'monitoring': {
                color: '#9b59b6',
                icon: '👁️',
                types: ['monitoring', 'metrics_collection', 'health_check']
            }
        };
        
        console.log('🎨 ActivityFeedRenderer initialized - Ready for beautiful observations!');
    }
    
    /**
     * Initialize the activity feed renderer
     */
    initialize() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.log(`📦 Creating activity feed container '${this.containerId}'`);
            this.createMainContainer();
            this.container = document.getElementById(this.containerId);
        }
        
        this.setupContainer();
        this.createFilterControls();
        this.setupEventListeners();
        this.startAnimationProcessor();
        
        console.log('🎨 Activity feed renderer ready!');
        return true;
    }
    
    /**
     * Create the main container for the activity feed
     */
    createMainContainer() {
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
        
        // Create the feed element
        const feedElement = document.createElement('div');
        feedElement.id = this.containerId;
        container.appendChild(feedElement);
        
        document.body.appendChild(container);
        console.log('📦 Activity feed container created and added to DOM');
    }
    
    /**
     * Setup the container with proper styling and structure
     */
    setupContainer() {
        // Add CSS classes for styling
        this.container.classList.add('activity-feed-container');
        
        // Create the main feed area if it doesn't exist
        if (!this.container.querySelector('.feed-content')) {
            this.container.innerHTML = `
                <div class="feed-header">
                    <div class="feed-title">
                        <span class="feed-icon">📰</span>
                        <span class="feed-text">Live Activity Feed</span>
                        <span class="feed-status" id="feedStatus">●</span>
                    </div>
                    <div class="feed-controls">
                        <button class="feed-btn" id="filterBtn" title="Filter events">🔍</button>
                        <button class="feed-btn" id="pauseBtn" title="Pause/Resume">⏸️</button>
                        <button class="feed-btn" id="clearBtn" title="Clear feed">🗑️</button>
                    </div>
                </div>
                <div class="feed-filters" id="feedFilters" style="display: none;">
                    <div class="filter-row">
                        <label>Severity:</label>
                        <select id="severityFilter">
                            <option value="all">All</option>
                            <option value="error">Errors</option>
                            <option value="warning">Warnings</option>
                            <option value="info">Info</option>
                            <option value="success">Success</option>
                        </select>
                    </div>
                    <div class="filter-row">
                        <label>Module:</label>
                        <select id="moduleFilter">
                            <option value="all">All Modules</option>
                        </select>
                    </div>
                    <div class="filter-row">
                        <label>Type:</label>
                        <select id="typeFilter">
                            <option value="all">All Types</option>
                        </select>
                    </div>
                    <div class="filter-row">
                        <label>
                            <input type="checkbox" id="hideBoringEventsToggle" checked>
                            Hide boring events
                        </label>
                    </div>
                </div>
                <div class="feed-content" id="feedContent">
                    <div class="feed-placeholder">
                        <div class="placeholder-icon">📡</div>
                        <div class="placeholder-text">Waiting for observations...</div>
                        <div class="placeholder-subtext">The Ace Reporter is standing by</div>
                    </div>
                </div>
                <div class="feed-footer">
                    <div class="feed-stats">
                        <span id="eventCount">0 events</span>
                        <span class="separator">•</span>
                        <span id="autoScrollStatus">Auto-scroll ON</span>
                    </div>
                </div>
            `;
        }
        
        this.addFeedStyles();
    }
    
    /**
     * Add comprehensive CSS styles for the activity feed
     */
    addFeedStyles() {
        const styleId = 'activity-feed-styles';
        if (document.getElementById(styleId)) return;
        
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .activity-feed-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: rgba(44, 62, 80, 0.95);
                backdrop-filter: blur(15px);
                border: 2px solid rgba(52, 152, 219, 0.3);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
            }
            
            .feed-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                background: rgba(52, 73, 94, 0.8);
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            
            .feed-title {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #3498db;
                font-weight: 600;
                font-size: 14px;
            }
            
            .feed-status {
                color: #2ecc71;
                font-size: 12px;
                animation: pulse 2s infinite;
            }
            
            .feed-controls {
                display: flex;
                gap: 8px;
            }
            
            .feed-btn {
                background: rgba(52, 152, 219, 0.2);
                border: 1px solid rgba(52, 152, 219, 0.5);
                color: #3498db;
                padding: 6px 10px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }
            
            .feed-btn:hover {
                background: rgba(52, 152, 219, 0.4);
                transform: translateY(-1px);
            }
            
            .feed-filters {
                padding: 15px;
                background: rgba(52, 73, 94, 0.6);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                animation: slideDown 0.3s ease-out;
            }
            
            .filter-row {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            .filter-row:last-child {
                margin-bottom: 0;
            }
            
            .filter-row label {
                color: #ecf0f1;
                font-size: 12px;
                min-width: 60px;
            }
            
            .filter-row select {
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                color: #ecf0f1;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                flex: 1;
            }
            
            .feed-content {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                scrollbar-width: thin;
                scrollbar-color: rgba(52, 152, 219, 0.5) transparent;
            }
            
            .feed-content::-webkit-scrollbar {
                width: 6px;
            }
            
            .feed-content::-webkit-scrollbar-track {
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }
            
            .feed-content::-webkit-scrollbar-thumb {
                background: rgba(52, 152, 219, 0.5);
                border-radius: 3px;
            }
            
            .feed-content::-webkit-scrollbar-thumb:hover {
                background: rgba(52, 152, 219, 0.7);
            }
            
            .feed-placeholder {
                text-align: center;
                padding: 40px 20px;
                color: #95a5a6;
            }
            
            .placeholder-icon {
                font-size: 32px;
                margin-bottom: 10px;
                opacity: 0.7;
            }
            
            .placeholder-text {
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 5px;
            }
            
            .placeholder-subtext {
                font-size: 12px;
                opacity: 0.8;
            }
            
            .observation-event {
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }
            
            .observation-event::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                background: var(--event-color, #95a5a6);
                transition: width 0.3s ease;
            }
            
            .observation-event:hover {
                background: rgba(255,255,255,0.1);
                transform: translateX(4px);
            }
            
            .observation-event:hover::before {
                width: 6px;
            }
            
            .event-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 8px;
            }
            
            .event-meta {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .event-emoji {
                font-size: 16px;
                filter: drop-shadow(0 0 2px rgba(0,0,0,0.5));
            }
            
            .event-module {
                font-size: 11px;
                color: #95a5a6;
                font-weight: 500;
                background: rgba(255,255,255,0.1);
                padding: 2px 6px;
                border-radius: 10px;
            }
            
            .event-timestamp {
                font-size: 10px;
                color: #7f8c8d;
                font-family: monospace;
            }
            
            .event-message {
                color: #ecf0f1;
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 6px;
            }
            
            .event-context {
                font-size: 10px;
                color: #95a5a6;
                font-family: monospace;
                background: rgba(0,0,0,0.2);
                padding: 4px 8px;
                border-radius: 4px;
                margin-top: 6px;
            }
            
            .event-severity-error {
                --event-color: #e74c3c;
            }
            
            .event-severity-warning {
                --event-color: #f39c12;
            }
            
            .event-severity-success {
                --event-color: #2ecc71;
            }
            
            .event-severity-info {
                --event-color: #3498db;
            }
            
            .feed-footer {
                padding: 10px 15px;
                background: rgba(52, 73, 94, 0.6);
                border-top: 1px solid rgba(255,255,255,0.1);
            }
            
            .feed-stats {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 11px;
                color: #95a5a6;
            }
            
            .separator {
                opacity: 0.5;
            }
            
            @keyframes slideDown {
                from { max-height: 0; opacity: 0; }
                to { max-height: 200px; opacity: 1; }
            }
            
            @keyframes slideInRight {
                from { transform: translateX(20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .event-new {
                animation: slideInRight 0.4s ease-out;
            }
            
            .event-highlight {
                background: rgba(52, 152, 219, 0.2) !important;
                border: 1px solid rgba(52, 152, 219, 0.5);
            }
        `;
        
        document.head.appendChild(style);
    }
    
    /**
     * Create filter controls and populate with available options
     */
    createFilterControls() {
        // This will be populated as events come in
        this.updateFilterOptions();
    }
    
    /**
     * Setup event listeners for interactive controls
     */
    setupEventListeners() {
        // Filter button
        const filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.toggleFilters());
        }
        
        // Pause/Resume button
        const pauseBtn = document.getElementById('pauseBtn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.togglePause());
        }
        
        // Clear button
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFeed());
        }
        
        // Filter controls
        const severityFilter = document.getElementById('severityFilter');
        const moduleFilter = document.getElementById('moduleFilter');
        const typeFilter = document.getElementById('typeFilter');
        
        if (severityFilter) {
            severityFilter.addEventListener('change', (e) => {
                this.filterSettings.severity = e.target.value;
                this.applyFilters();
            });
        }
        
        if (moduleFilter) {
            moduleFilter.addEventListener('change', (e) => {
                this.filterSettings.module = e.target.value;
                this.applyFilters();
            });
        }
        
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.filterSettings.eventType = e.target.value;
                this.applyFilters();
            });
        }
        
        // Boring events toggle
        const hideBoringEventsToggle = document.getElementById('hideBoringEventsToggle');
        if (hideBoringEventsToggle) {
            hideBoringEventsToggle.addEventListener('change', (e) => {
                this.filterSettings.hideBoringEvents = e.target.checked;
                console.log('🔇 Boring events filtering:', e.target.checked ? 'ON' : 'OFF');
                // Note: This only affects new events, existing events remain filtered
            });
        }
        
        // Auto-scroll detection
        const feedContent = document.getElementById('feedContent');
        if (feedContent) {
            feedContent.addEventListener('scroll', () => {
                const isAtBottom = feedContent.scrollTop + feedContent.clientHeight >= feedContent.scrollHeight - 10;
                this.isAutoScroll = isAtBottom;
                this.updateAutoScrollStatus();
            });
        }
    }
    
    /**
     * Add a new observation event to the feed
     */
    addEvent(event) {
        // Apply boring events filtering
        if (this.filterSettings.hideBoringEvents && this.isBoringEvent(event)) {
            console.debug('🔇 Filtered boring event:', event.message);
            return; // Skip boring events
        }
        
        // Add to history
        this.eventHistory.unshift(event);
        if (this.eventHistory.length > this.maxEvents) {
            this.eventHistory.pop();
        }
        
        // Add to animation queue
        this.animationQueue.push({
            type: 'add',
            event: event,
            timestamp: Date.now()
        });
        
        // Update filter options
        this.updateFilterOptions();
        
        // Update stats
        this.updateStats();
    }
    
    /**
     * Check if an event is considered boring/noisy
     */
    isBoringEvent(event) {
        // Check if event type is boring
        if (this.boringEventTypes.has(event.event_type)) {
            return true;
        }
        
        // Check if module is boring
        if (this.boringModules.has(event.module)) {
            return true;
        }
        
        // Check for specific boring patterns
        const message = event.message?.toLowerCase() || '';
        const boringPatterns = [
            'heartbeat',
            'ping',
            'pong',
            'websocket connection',
            'emoji rain connect',
            'emoji rain disconnect',
            'health check',
            'status update'
        ];
        
        return boringPatterns.some(pattern => message.includes(pattern));
    }
    
    /**
     * Process animation queue for smooth event additions
     */
    async startAnimationProcessor() {
        if (this.isProcessingQueue) return;
        
        this.isProcessingQueue = true;
        
        while (true) {
            if (this.animationQueue.length > 0) {
                const animation = this.animationQueue.shift();
                await this.processAnimation(animation);
                
                // Small delay between animations for smoothness
                await new Promise(resolve => setTimeout(resolve, 100));
            } else {
                // Wait a bit before checking again
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
    }
    
    /**
     * Process individual animation
     */
    async processAnimation(animation) {
        switch (animation.type) {
            case 'add':
                await this.renderEvent(animation.event);
                break;
        }
    }
    
    /**
     * Render a single event in the feed
     */
    async renderEvent(event) {
        const feedContent = document.getElementById('feedContent');
        if (!feedContent) return;
        
        // Remove placeholder if it exists
        const placeholder = feedContent.querySelector('.feed-placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Create event element
        const eventElement = this.createEventElement(event);
        
        // Add to top of feed
        feedContent.insertBefore(eventElement, feedContent.firstChild);
        
        // Remove old events if we have too many
        const events = feedContent.querySelectorAll('.observation-event');
        if (events.length > this.maxEvents) {
            for (let i = this.maxEvents; i < events.length; i++) {
                events[i].remove();
            }
        }
        
        // Auto-scroll if enabled
        if (this.isAutoScroll) {
            feedContent.scrollTop = 0;
        }
        
        // Apply current filters
        this.applyFilters();
    }
    
    /**
     * Create DOM element for an observation event
     */
    createEventElement(event) {
        const eventDiv = document.createElement('div');
        eventDiv.className = `observation-event event-new event-severity-${event.severity || 'info'}`;
        eventDiv.dataset.module = event.module || 'System';
        eventDiv.dataset.eventType = event.event_type || 'unknown';
        eventDiv.dataset.severity = event.severity || 'info';
        
        const timestamp = new Date(event.timestamp).toLocaleTimeString();
        const module = event.module || 'System';
        const emoji = event.emoji || '📊';
        
        eventDiv.innerHTML = `
            <div class="event-header">
                <div class="event-meta">
                    <span class="event-emoji">${emoji}</span>
                    <span class="event-module">${module}</span>
                </div>
                <span class="event-timestamp">${timestamp}</span>
            </div>
            <div class="event-message">${event.message}</div>
            ${event.context ? `
                <div class="event-context">
                    ${this.formatContext(event.context)}
                </div>
            ` : ''}
        `;
        
        // Add click handler for details
        eventDiv.addEventListener('click', () => {
            this.showEventDetails(event);
        });
        
        return eventDiv;
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
        // Highlight the event temporarily
        const eventElements = document.querySelectorAll('.observation-event');
        eventElements.forEach(el => {
            if (el.querySelector('.event-message').textContent === event.message) {
                el.classList.add('event-highlight');
                setTimeout(() => el.classList.remove('event-highlight'), 2000);
            }
        });
        
        console.log('📋 Event details:', event);
        // TODO: Implement modal or sidebar details view
    }
    
    /**
     * Toggle filter panel visibility
     */
    toggleFilters() {
        const filters = document.getElementById('feedFilters');
        const filterBtn = document.getElementById('filterBtn');
        
        if (filters && filterBtn) {
            const isVisible = filters.style.display !== 'none';
            filters.style.display = isVisible ? 'none' : 'block';
            filterBtn.textContent = isVisible ? '🔍' : '🔍✓';
        }
    }
    
    /**
     * Toggle pause/resume functionality
     */
    togglePause() {
        const pauseBtn = document.getElementById('pauseBtn');
        if (pauseBtn) {
            this.isPaused = !this.isPaused;
            pauseBtn.textContent = this.isPaused ? '▶️' : '⏸️';
            pauseBtn.title = this.isPaused ? 'Resume' : 'Pause';
        }
    }
    
    /**
     * Clear the activity feed
     */
    clearFeed() {
        const feedContent = document.getElementById('feedContent');
        if (feedContent) {
            feedContent.innerHTML = `
                <div class="feed-placeholder">
                    <div class="placeholder-icon">📡</div>
                    <div class="placeholder-text">Feed cleared</div>
                    <div class="placeholder-subtext">Waiting for new observations...</div>
                </div>
            `;
        }
        
        this.eventHistory = [];
        this.updateStats();
    }
    
    /**
     * Apply current filter settings
     */
    applyFilters() {
        const events = document.querySelectorAll('.observation-event');
        
        events.forEach(eventEl => {
            const module = eventEl.dataset.module;
            const eventType = eventEl.dataset.eventType;
            const severity = eventEl.dataset.severity;
            
            let visible = true;
            
            if (this.filterSettings.severity !== 'all' && severity !== this.filterSettings.severity) {
                visible = false;
            }
            
            if (this.filterSettings.module !== 'all' && module !== this.filterSettings.module) {
                visible = false;
            }
            
            if (this.filterSettings.eventType !== 'all' && eventType !== this.filterSettings.eventType) {
                visible = false;
            }
            
            eventEl.style.display = visible ? 'block' : 'none';
        });
    }
    
    /**
     * Update filter dropdown options based on available events
     */
    updateFilterOptions() {
        const modules = new Set();
        const eventTypes = new Set();
        
        this.eventHistory.forEach(event => {
            if (event.module) modules.add(event.module);
            if (event.event_type) eventTypes.add(event.event_type);
        });
        
        // Update module filter
        const moduleFilter = document.getElementById('moduleFilter');
        if (moduleFilter) {
            const currentValue = moduleFilter.value;
            moduleFilter.innerHTML = '<option value="all">All Modules</option>';
            
            Array.from(modules).sort().forEach(module => {
                const option = document.createElement('option');
                option.value = module;
                option.textContent = module;
                moduleFilter.appendChild(option);
            });
            
            moduleFilter.value = currentValue;
        }
        
        // Update event type filter
        const typeFilter = document.getElementById('typeFilter');
        if (typeFilter) {
            const currentValue = typeFilter.value;
            typeFilter.innerHTML = '<option value="all">All Types</option>';
            
            Array.from(eventTypes).sort().forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type.replace(/_/g, ' ').toUpperCase();
                typeFilter.appendChild(option);
            });
            
            typeFilter.value = currentValue;
        }
    }
    
    /**
     * Update statistics display
     */
    updateStats() {
        const eventCount = document.getElementById('eventCount');
        if (eventCount) {
            const count = this.eventHistory.length;
            eventCount.textContent = `${count} event${count !== 1 ? 's' : ''}`;
        }
    }
    
    /**
     * Update auto-scroll status display
     */
    updateAutoScrollStatus() {
        const autoScrollStatus = document.getElementById('autoScrollStatus');
        if (autoScrollStatus) {
            autoScrollStatus.textContent = this.isAutoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF';
        }
    }
    
    /**
     * Get current feed statistics
     */
    getStats() {
        return {
            totalEvents: this.eventHistory.length,
            isAutoScroll: this.isAutoScroll,
            isPaused: this.isPaused || false,
            filterSettings: { ...this.filterSettings }
        };
    }
}

// Global instance for integration with ObservationStreamHandler
let activityFeedRenderer = null;

function initializeActivityFeedRenderer() {
    if (!activityFeedRenderer) {
        activityFeedRenderer = new ActivityFeedRenderer();
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                activityFeedRenderer.initialize();
            });
        } else {
            activityFeedRenderer.initialize();
        }
        
        // Add to global scope for debugging and integration
        window.activityFeedRenderer = activityFeedRenderer;
        window.getFeedStats = () => activityFeedRenderer.getStats();
    }
}

// Auto-initialize
console.log('🎨 ActivityFeedRenderer script loaded!');
initializeActivityFeedRenderer();