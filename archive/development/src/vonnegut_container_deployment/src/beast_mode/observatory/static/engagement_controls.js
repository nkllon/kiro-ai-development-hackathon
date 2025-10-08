/**
 * Engagement Controls JavaScript
 * 
 * Provides interactive controls for the Live Dashboard Engagement System.
 * Handles user interactions, attention tracking, and engagement metrics.
 */

class EngagementControls {
    constructor() {
        this.engagementSocket = null;
        this.attentionSession = null;
        this.interactionCount = 0;
        this.focusStartTime = null;
        this.isEngagementEnabled = false;
        
        // Engagement metrics
        this.metrics = {
            sessionDuration: 0,
            interactions: 0,
            focusTime: 0,
            pageViews: 0,
            animationsTriggered: 0
        };
        
        this.init();
    }
    
    init() {
        this.setupEngagementSocket();
        this.setupAttentionTracking();
        this.setupInteractionTracking();
        this.setupEngagementUI();
        this.startEngagementSession();
    }
    
    setupEngagementSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/engagement`;
            
            this.engagementSocket = new WebSocket(wsUrl);
            
            this.engagementSocket.onopen = () => {
                console.log('🎯 Engagement WebSocket connected');
                this.isEngagementEnabled = true;
                this.updateEngagementStatus('connected');
            };
            
            this.engagementSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleEngagementMessage(data);
            };
            
            this.engagementSocket.onclose = () => {
                console.log('🎯 Engagement WebSocket disconnected');
                this.isEngagementEnabled = false;
                this.updateEngagementStatus('disconnected');
                
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.setupEngagementSocket(), 5000);
            };
            
            this.engagementSocket.onerror = (error) => {
                console.error('🎯 Engagement WebSocket error:', error);
                this.isEngagementEnabled = false;
                this.updateEngagementStatus('error');
            };
            
        } catch (error) {
            console.error('🎯 Failed to setup engagement WebSocket:', error);
            this.isEngagementEnabled = false;
            this.updateEngagementStatus('unavailable');
        }
    }
    
    setupAttentionTracking() {
        // Track page focus/blur events
        window.addEventListener('focus', () => {
            this.focusStartTime = Date.now();
            this.recordFocusEvent('focus');
        });
        
        window.addEventListener('blur', () => {
            if (this.focusStartTime) {
                const focusTime = Date.now() - this.focusStartTime;
                this.metrics.focusTime += focusTime;
                this.focusStartTime = null;
            }
            this.recordFocusEvent('blur');
        });
        
        // Track page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.recordFocusEvent('blur');
            } else {
                this.recordFocusEvent('focus');
            }
        });
        
        // Track mouse movement for attention
        let mouseTimer = null;
        document.addEventListener('mousemove', () => {
            if (mouseTimer) clearTimeout(mouseTimer);
            mouseTimer = setTimeout(() => {
                this.recordInteraction('mouse_idle', 'document', 5000);
            }, 5000);
        });
    }
    
    setupInteractionTracking() {
        // Track clicks on interactive elements
        document.addEventListener('click', (event) => {
            const element = event.target;
            const component = this.getComponentName(element);
            const duration = this.getInteractionDuration(event);
            
            this.recordInteraction('click', component, duration);
            this.metrics.interactions++;
            
            // Special handling for buttons and controls
            if (element.matches('button, .btn, .chart-container, .stat-card')) {
                this.triggerEngagementAnimation('click_feedback', element);
            }
        });
        
        // Track hover events on important elements
        const hoverElements = document.querySelectorAll('.chart-container, .stat-card, .btn');
        hoverElements.forEach(element => {
            let hoverStartTime = null;
            
            element.addEventListener('mouseenter', () => {
                hoverStartTime = Date.now();
                this.triggerEngagementAnimation('hover_highlight', element);
            });
            
            element.addEventListener('mouseleave', () => {
                if (hoverStartTime) {
                    const duration = Date.now() - hoverStartTime;
                    const component = this.getComponentName(element);
                    this.recordInteraction('hover', component, duration);
                }
            });
        });
        
        // Track scroll events
        let scrollTimer = null;
        window.addEventListener('scroll', () => {
            if (scrollTimer) clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                this.recordInteraction('scroll', 'page', window.scrollY);
            }, 100);
        });
        
        // Track keyboard interactions
        document.addEventListener('keydown', (event) => {
            if (event.target.matches('input, textarea')) {
                this.recordInteraction('keyboard', 'input', 1);
            }
        });
    }
    
    setupEngagementUI() {
        // Create engagement controls panel
        const controlsPanel = this.createEngagementControlsPanel();
        document.body.appendChild(controlsPanel);
        
        // Create engagement metrics display
        const metricsDisplay = this.createEngagementMetricsDisplay();
        document.body.appendChild(metricsDisplay);
        
        // Add engagement status indicator
        const statusIndicator = this.createEngagementStatusIndicator();
        document.body.appendChild(statusIndicator);
        
        // Update metrics display every 5 seconds
        setInterval(() => this.updateMetricsDisplay(), 5000);
    }
    
    createEngagementControlsPanel() {
        const panel = document.createElement('div');
        panel.id = 'engagementControlsPanel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(52, 73, 94, 0.95);
            border: 2px solid rgba(52, 152, 219, 0.5);
            border-radius: 12px;
            padding: 15px;
            z-index: 1000;
            backdrop-filter: blur(10px);
            color: #ecf0f1;
            font-size: 14px;
            min-width: 250px;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
        `;
        
        panel.innerHTML = `
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; color: #3498db;">🎯 Engagement Controls</h4>
                <button id="toggleEngagementPanel" style="
                    background: none;
                    border: none;
                    color: #95a5a6;
                    cursor: pointer;
                    font-size: 16px;
                ">−</button>
            </div>
            <div id="engagementControlsContent">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <button id="triggerCelebration" class="engagement-btn">🎉 Celebrate</button>
                    <button id="triggerFocus" class="engagement-btn">🎯 Focus Mode</button>
                    <button id="triggerCalm" class="engagement-btn">😌 Calm Mode</button>
                    <button id="triggerEnergy" class="engagement-btn">⚡ Energy Mode</button>
                </div>
                <div style="margin-top: 10px;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="checkbox" id="autoEngagement" checked>
                        <span>Auto Engagement</span>
                    </label>
                </div>
            </div>
        `;
        
        // Add event listeners
        panel.querySelector('#toggleEngagementPanel').addEventListener('click', () => {
            this.toggleEngagementPanel();
        });
        
        panel.querySelector('#triggerCelebration').addEventListener('click', () => {
            this.triggerPersonalityTransition('celebratory', 'manual_trigger');
        });
        
        panel.querySelector('#triggerFocus').addEventListener('click', () => {
            this.triggerPersonalityTransition('focused', 'manual_trigger');
        });
        
        panel.querySelector('#triggerCalm').addEventListener('click', () => {
            this.triggerPersonalityTransition('calm', 'manual_trigger');
        });
        
        panel.querySelector('#triggerEnergy').addEventListener('click', () => {
            this.triggerPersonalityTransition('energetic', 'manual_trigger');
        });
        
        // Show panel after a delay
        setTimeout(() => {
            panel.style.transform = 'translateY(0)';
            panel.style.opacity = '1';
        }, 1000);
        
        return panel;
    }
    
    createEngagementMetricsDisplay() {
        const display = document.createElement('div');
        display.id = 'engagementMetricsDisplay';
        display.style.cssText = `
            position: fixed;
            top: 140px;
            right: 20px;
            background: rgba(52, 73, 94, 0.95);
            border: 2px solid rgba(46, 204, 113, 0.5);
            border-radius: 12px;
            padding: 15px;
            z-index: 1000;
            backdrop-filter: blur(10px);
            color: #ecf0f1;
            font-size: 12px;
            min-width: 200px;
        `;
        
        display.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #2ecc71;">📊 Engagement Metrics</h4>
            <div id="engagementMetricsContent">
                <div class="metric-row">
                    <span>Session:</span>
                    <span id="sessionDuration">0:00</span>
                </div>
                <div class="metric-row">
                    <span>Interactions:</span>
                    <span id="interactionCount">0</span>
                </div>
                <div class="metric-row">
                    <span>Focus Time:</span>
                    <span id="focusTime">0:00</span>
                </div>
                <div class="metric-row">
                    <span>Animations:</span>
                    <span id="animationCount">0</span>
                </div>
                <div class="metric-row">
                    <span>Engagement Score:</span>
                    <span id="engagementScore">0.0</span>
                </div>
            </div>
        `;
        
        // Add CSS for metric rows
        const style = document.createElement('style');
        style.textContent = `
            .metric-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
                padding: 2px 0;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            .metric-row:last-child {
                border-bottom: none;
                font-weight: bold;
                color: #2ecc71;
            }
            .engagement-btn {
                background: linear-gradient(45deg, #3498db, #2980b9);
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s ease;
            }
            .engagement-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
            }
        `;
        document.head.appendChild(style);
        
        return display;
    }
    
    createEngagementStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'engagementStatusIndicator';
        indicator.style.cssText = `
            position: fixed;
            top: 80px;
            left: 20px;
            background: rgba(149, 165, 166, 0.9);
            border: 2px solid #95a5a6;
            border-radius: 20px;
            padding: 8px 15px;
            z-index: 1001;
            color: white;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        `;
        
        indicator.innerHTML = '🎯 Engagement: Connecting...';
        
        return indicator;
    }
    
    startEngagementSession() {
        this.attentionSession = {
            id: `session_${Date.now()}`,
            startTime: Date.now(),
            userId: `user_${Math.random().toString(36).substr(2, 9)}`
        };
        
        // Send session start to server
        this.sendEngagementMessage({
            type: 'start_attention_session',
            data: {
                sessionId: this.attentionSession.id,
                userId: this.attentionSession.userId,
                pageView: 'engagement_dashboard'
            }
        });
        
        // Update session duration every second
        setInterval(() => {
            if (this.attentionSession) {
                this.metrics.sessionDuration = Date.now() - this.attentionSession.startTime;
            }
        }, 1000);
    }
    
    recordInteraction(eventType, component, duration = null) {
        if (!this.isEngagementEnabled || !this.attentionSession) return;
        
        const interaction = {
            userId: this.attentionSession.userId,
            eventType: eventType,
            component: component,
            duration: duration,
            timestamp: Date.now()
        };
        
        this.sendEngagementMessage({
            type: 'record_interaction',
            data: interaction
        });
        
        this.interactionCount++;
    }
    
    recordFocusEvent(eventType) {
        if (!this.isEngagementEnabled || !this.attentionSession) return;
        
        this.sendEngagementMessage({
            type: 'record_focus_event',
            data: {
                sessionId: this.attentionSession.id,
                eventType: eventType
            }
        });
    }
    
    triggerPersonalityTransition(toMood, trigger) {
        if (!this.isEngagementEnabled) return;
        
        this.sendEngagementMessage({
            type: 'personality_transition',
            data: {
                toMood: toMood,
                trigger: trigger
            }
        });
        
        // Visual feedback
        this.triggerEngagementAnimation('personality_change', document.body);
    }
    
    triggerEngagementAnimation(animationType, element) {
        this.metrics.animationsTriggered++;
        
        // Add visual feedback class
        element.classList.add('engagement-animation');
        
        // Remove class after animation
        setTimeout(() => {
            element.classList.remove('engagement-animation');
        }, 300);
        
        // Record animation event
        this.sendEngagementMessage({
            type: 'record_animation',
            data: {
                animationType: animationType,
                duration: 0.3
            }
        });
    }
    
    handleEngagementMessage(data) {
        switch (data.type) {
            case 'insights_update':
                this.handleInsightsUpdate(data.data);
                break;
            case 'status_update':
                this.handleStatusUpdate(data.data);
                break;
            case 'personality_change':
                this.handlePersonalityChange(data.data);
                break;
            case 'pong':
                // Handle ping response
                break;
            default:
                console.log('🎯 Unknown engagement message:', data);
        }
    }
    
    handleInsightsUpdate(insights) {
        // Update dashboard with new insights
        if (insights.patterns && insights.patterns.length > 0) {
            this.displayInsights(insights.patterns);
        }
    }
    
    handleStatusUpdate(status) {
        console.log('🎯 Engagement status update:', status);
    }
    
    handlePersonalityChange(data) {
        // Apply personality-based visual changes
        this.applyPersonalityTheme(data.mood);
    }
    
    displayInsights(patterns) {
        // Create or update insights display
        let insightsPanel = document.getElementById('engagementInsights');
        if (!insightsPanel) {
            insightsPanel = document.createElement('div');
            insightsPanel.id = 'engagementInsights';
            insightsPanel.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(52, 73, 94, 0.95);
                border: 2px solid rgba(155, 89, 182, 0.5);
                border-radius: 12px;
                padding: 15px;
                z-index: 1000;
                backdrop-filter: blur(10px);
                color: #ecf0f1;
                font-size: 12px;
                max-width: 300px;
                max-height: 200px;
                overflow-y: auto;
            `;
            document.body.appendChild(insightsPanel);
        }
        
        insightsPanel.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #9b59b6;">🧠 Live Insights</h4>
            ${patterns.map(pattern => `
                <div style="margin-bottom: 8px; padding: 6px; background: rgba(155, 89, 182, 0.1); border-radius: 4px;">
                    <strong>${pattern.type}:</strong> ${pattern.description}
                </div>
            `).join('')}
        `;
    }
    
    applyPersonalityTheme(mood) {
        const body = document.body;
        
        // Remove existing personality classes
        body.classList.remove('personality-calm', 'personality-focused', 'personality-celebratory', 'personality-energetic');
        
        // Add new personality class
        body.classList.add(`personality-${mood}`);
        
        // Update visual elements based on mood
        const colors = this.getPersonalityColors(mood);
        document.documentElement.style.setProperty('--personality-primary', colors.primary);
        document.documentElement.style.setProperty('--personality-secondary', colors.secondary);
    }
    
    getPersonalityColors(mood) {
        const colorSchemes = {
            calm: { primary: '#3498db', secondary: '#2980b9' },
            focused: { primary: '#e74c3c', secondary: '#c0392b' },
            celebratory: { primary: '#f39c12', secondary: '#e67e22' },
            energetic: { primary: '#2ecc71', secondary: '#27ae60' }
        };
        
        return colorSchemes[mood] || colorSchemes.calm;
    }
    
    getComponentName(element) {
        // Determine component name from element
        if (element.matches('.chart-container')) return 'chart';
        if (element.matches('.stat-card')) return 'stat_card';
        if (element.matches('.btn, button')) return 'button';
        if (element.matches('.donation-btn')) return 'donation_button';
        if (element.matches('.doctor-status')) return 'doctor_status';
        
        return element.tagName.toLowerCase();
    }
    
    getInteractionDuration(event) {
        // Simple duration calculation based on event type
        return Date.now() - (event.timeStamp || Date.now());
    }
    
    sendEngagementMessage(message) {
        if (this.engagementSocket && this.engagementSocket.readyState === WebSocket.OPEN) {
            this.engagementSocket.send(JSON.stringify(message));
        }
    }
    
    updateEngagementStatus(status) {
        const indicator = document.getElementById('engagementStatusIndicator');
        if (!indicator) return;
        
        const statusConfig = {
            connected: { text: '🎯 Engagement: Active', color: '#2ecc71', border: '#27ae60' },
            disconnected: { text: '🎯 Engagement: Disconnected', color: '#e74c3c', border: '#c0392b' },
            error: { text: '🎯 Engagement: Error', color: '#f39c12', border: '#e67e22' },
            unavailable: { text: '🎯 Engagement: Unavailable', color: '#95a5a6', border: '#7f8c8d' }
        };
        
        const config = statusConfig[status] || statusConfig.unavailable;
        indicator.innerHTML = config.text;
        indicator.style.background = config.color;
        indicator.style.borderColor = config.border;
    }
    
    updateMetricsDisplay() {
        const elements = {
            sessionDuration: document.getElementById('sessionDuration'),
            interactionCount: document.getElementById('interactionCount'),
            focusTime: document.getElementById('focusTime'),
            animationCount: document.getElementById('animationCount'),
            engagementScore: document.getElementById('engagementScore')
        };
        
        if (elements.sessionDuration) {
            elements.sessionDuration.textContent = this.formatDuration(this.metrics.sessionDuration);
        }
        
        if (elements.interactionCount) {
            elements.interactionCount.textContent = this.metrics.interactions;
        }
        
        if (elements.focusTime) {
            elements.focusTime.textContent = this.formatDuration(this.metrics.focusTime);
        }
        
        if (elements.animationCount) {
            elements.animationCount.textContent = this.metrics.animationsTriggered;
        }
        
        if (elements.engagementScore) {
            const score = this.calculateEngagementScore();
            elements.engagementScore.textContent = score.toFixed(1);
        }
    }
    
    calculateEngagementScore() {
        // Simple engagement score calculation
        const sessionMinutes = this.metrics.sessionDuration / (1000 * 60);
        const interactionRate = sessionMinutes > 0 ? this.metrics.interactions / sessionMinutes : 0;
        const focusRatio = this.metrics.sessionDuration > 0 ? this.metrics.focusTime / this.metrics.sessionDuration : 0;
        
        return Math.min(10, (interactionRate * 2) + (focusRatio * 5) + (this.metrics.animationsTriggered * 0.1));
    }
    
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    toggleEngagementPanel() {
        const panel = document.getElementById('engagementControlsPanel');
        const content = document.getElementById('engagementControlsContent');
        const toggle = document.getElementById('toggleEngagementPanel');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            toggle.textContent = '−';
            panel.style.transform = 'translateY(0)';
        } else {
            content.style.display = 'none';
            toggle.textContent = '+';
            panel.style.transform = 'translateY(60px)';
        }
    }
    
    getCurrentPersonalityMood() {
        const currentMood = document.body.className.match(/personality-(\w+)/);
        return currentMood ? currentMood[1].charAt(0).toUpperCase() + currentMood[1].slice(1) : 'Calm';
    }
}

// Add engagement animation styles
const engagementStyles = document.createElement('style');
engagementStyles.textContent = `
    .engagement-animation {
        animation: engagementPulse 0.3s ease-out;
    }
    
    @keyframes engagementPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .personality-calm {
        --personality-filter: hue-rotate(200deg);
    }
    
    .personality-focused {
        --personality-filter: hue-rotate(0deg) saturate(1.2);
    }
    
    .personality-celebratory {
        --personality-filter: hue-rotate(45deg) saturate(1.5);
    }
    
    .personality-energetic {
        --personality-filter: hue-rotate(120deg) saturate(1.3);
    }
    
    body[class*="personality-"] .chart-container {
        filter: var(--personality-filter, none);
        transition: filter 0.5s ease;
    }
`;
document.head.appendChild(engagementStyles);

// Global functions for dashboard integration
window.setPersonality = function(mood) {
    if (window.engagementControls) {
        window.engagementControls.triggerPersonalityTransition(mood, 'manual_control');
    }
};

window.updateLiveEngagementMetrics = function() {
    if (window.engagementControls) {
        const metrics = window.engagementControls.metrics;
        
        // Update live metrics display
        const elements = {
            liveSessionDuration: document.getElementById('liveSessionDuration'),
            liveInteractionCount: document.getElementById('liveInteractionCount'),
            liveEngagementScore: document.getElementById('liveEngagementScore'),
            livePersonalityMood: document.getElementById('livePersonalityMood')
        };
        
        if (elements.liveSessionDuration) {
            elements.liveSessionDuration.textContent = window.engagementControls.formatDuration(metrics.sessionDuration);
        }
        
        if (elements.liveInteractionCount) {
            elements.liveInteractionCount.textContent = metrics.interactions;
        }
        
        if (elements.liveEngagementScore) {
            const score = window.engagementControls.calculateEngagementScore();
            elements.liveEngagementScore.textContent = score.toFixed(1);
        }
        
        if (elements.livePersonalityMood) {
            const moodEmojis = {
                calm: '😌',
                focused: '🎯',
                celebratory: '🎉',
                energetic: '⚡'
            };
            
            const currentMood = window.engagementControls.getCurrentPersonalityMood().toLowerCase();
            elements.livePersonalityMood.textContent = moodEmojis[currentMood] || '😌';
        }
    }
};

// Initialize engagement controls when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.engagementControls = new EngagementControls();
        
        // Update live metrics every 2 seconds
        setInterval(window.updateLiveEngagementMetrics, 2000);
    });
} else {
    window.engagementControls = new EngagementControls();
    
    // Update live metrics every 2 seconds
    setInterval(window.updateLiveEngagementMetrics, 2000);
}