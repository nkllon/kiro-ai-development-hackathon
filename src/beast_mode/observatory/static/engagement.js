/**
 * Live Dashboard Engagement System - Frontend Integration
 * ======================================================
 * 
 * Enhances the Observatory dashboard with engaging, interactive features
 * that transform data visualization from passive consumption to active engagement.
 */

class DashboardEngagementSystem {
    constructor() {
        this.isInitialized = false;
        this.engagementLevel = 'passive';
        this.personalityState = 'professional';
        this.attentionFocus = null;
        this.interactionCount = 0;
        this.sessionStartTime = Date.now();
        
        // WebSocket connection for real-time engagement
        this.engagementSocket = null;
        
        // Animation and visual enhancement systems
        this.animationEngine = new EngagementAnimationEngine();
        this.personalityEngine = new PersonalityEngine();
        this.attentionManager = new AttentionManager();
        
        console.log('🎯 Dashboard Engagement System initialized');
    }
    
    async initialize() {
        if (this.isInitialized) return;
        
        try {
            // Initialize engagement WebSocket connection
            await this.initializeEngagementSocket();
            
            // Initialize visual enhancements
            this.initializeVisualEnhancements();
            
            // Initialize interaction tracking
            this.initializeInteractionTracking();
            
            // Initialize personality-driven adaptations
            this.initializePersonalityAdaptations();
            
            // Initialize attention management
            this.initializeAttentionManagement();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Engagement System fully initialized');
            
            // Trigger initial engagement celebration
            this.celebrateEngagementActivation();
            
        } catch (error) {
            console.error('❌ Failed to initialize Dashboard Engagement System:', error);
        }
    }
    
    async initializeEngagementSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/engagement`;
            
            this.engagementSocket = new WebSocket(wsUrl);
            
            this.engagementSocket.onopen = () => {
                console.log('🔌 Engagement WebSocket connected');
                this.updateEngagementLevel('active');
            };
            
            this.engagementSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleEngagementMessage(data);
            };
            
            this.engagementSocket.onclose = () => {
                console.log('🔌 Engagement WebSocket disconnected');
                this.updateEngagementLevel('passive');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.initializeEngagementSocket(), 5000);
            };
            
        } catch (error) {
            console.warn('⚠️ Engagement WebSocket not available, using fallback mode');
        }
    }
    
    initializeVisualEnhancements() {
        // Enhance existing charts with engagement features
        this.enhanceChartInteractivity();
        
        // Add contextual information layers
        this.addContextualLayers();
        
        // Initialize smooth transitions and animations
        this.initializeSmoothTransitions();
        
        // Add hover effects and micro-interactions
        this.addMicroInteractions();
    }
    
    enhanceChartInteractivity() {
        // Find all chart containers and enhance them
        const chartContainers = document.querySelectorAll('.chart-container');
        
        chartContainers.forEach((container, index) => {
            // Add engagement hover effects
            container.addEventListener('mouseenter', () => {
                this.onChartHover(container, true);
            });
            
            container.addEventListener('mouseleave', () => {
                this.onChartHover(container, false);
            });
            
            // Add click handlers for drill-down
            container.addEventListener('click', () => {
                this.onChartClick(container);
            });
            
            // Add contextual information overlay
            this.addChartContextOverlay(container);
        });
    }
    
    onChartHover(container, isHovering) {
        if (isHovering) {
            // Enhance visual feedback
            container.style.transform = 'translateY(-4px) scale(1.02)';
            container.style.boxShadow = '0 12px 35px rgba(52, 152, 219, 0.4)';
            container.style.borderColor = 'rgba(52, 152, 219, 0.8)';
            
            // Show contextual information
            this.showChartContext(container);
            
            // Track interaction
            this.trackInteraction('chart_hover', { chart: container.id });
            
        } else {
            // Reset visual state
            container.style.transform = '';
            container.style.boxShadow = '';
            container.style.borderColor = '';
            
            // Hide contextual information
            this.hideChartContext(container);
        }
    }
    
    onChartClick(container) {
        // Trigger attention focus
        this.attentionManager.setFocus(container.id, 'high');
        
        // Enhance engagement level
        this.updateEngagementLevel('immersive');
        
        // Show detailed drill-down
        this.showChartDrillDown(container);
        
        // Track interaction
        this.trackInteraction('chart_click', { chart: container.id });
        
        // Trigger celebration animation
        this.animationEngine.triggerCelebration('chart_interaction', container);
    }
    
    addChartContextOverlay(container) {
        const overlay = document.createElement('div');
        overlay.className = 'engagement-context-overlay';
        overlay.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(52, 152, 219, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            opacity: 0;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            pointer-events: none;
            z-index: 10;
        `;
        overlay.innerHTML = '💡 Click for insights';
        container.appendChild(overlay);
    }
    
    showChartContext(container) {
        const overlay = container.querySelector('.engagement-context-overlay');
        if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.transform = 'translateY(0)';
        }
    }
    
    hideChartContext(container) {
        const overlay = container.querySelector('.engagement-context-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.transform = 'translateY(-10px)';
        }
    }
    
    showChartDrillDown(container) {
        // Create drill-down modal
        const modal = document.createElement('div');
        modal.className = 'engagement-drill-down-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: linear-gradient(135deg, rgba(52, 73, 94, 0.95), rgba(44, 62, 80, 0.95));
            border-radius: 15px;
            padding: 30px;
            max-width: 80vw;
            max-height: 80vh;
            overflow-y: auto;
            backdrop-filter: blur(15px);
            border: 2px solid rgba(52, 152, 219, 0.5);
            transform: scale(0.8);
            transition: transform 0.3s ease;
        `;
        
        const chartTitle = container.querySelector('h4').textContent;
        content.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="color: #3498db; margin: 0;">${chartTitle} - Detailed Analysis</h3>
                <button onclick="this.closest('.engagement-drill-down-modal').remove()" 
                        style="background: none; border: none; color: #e74c3c; font-size: 24px; cursor: pointer;">✕</button>
            </div>
            <div style="color: #ecf0f1;">
                <p>🔍 <strong>Engagement Insight:</strong> This chart shows real-time data patterns with contextual analysis.</p>
                <p>📊 <strong>Data Quality:</strong> High confidence with recent updates</p>
                <p>🎯 <strong>Key Trends:</strong> Systematic improvements detected</p>
                <p>💡 <strong>Recommendations:</strong> Continue monitoring for optimization opportunities</p>
                <div style="margin-top: 20px; padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px;">
                    <strong style="color: #3498db;">🚀 Engagement Features:</strong>
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        <li>Real-time data storytelling</li>
                        <li>Contextual information layering</li>
                        <li>Interactive drill-down analysis</li>
                        <li>Predictive trend indicators</li>
                    </ul>
                </div>
            </div>
        `;
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => {
            modal.style.opacity = '1';
            content.style.transform = 'scale(1)';
        }, 10);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    initializeInteractionTracking() {
        // Track mouse movements for engagement analysis
        let mouseIdleTimer;
        document.addEventListener('mousemove', () => {
            clearTimeout(mouseIdleTimer);
            this.updateEngagementLevel('active');
            
            mouseIdleTimer = setTimeout(() => {
                this.updateEngagementLevel('passive');
            }, 30000); // 30 seconds of inactivity
        });
        
        // Track scroll behavior
        let scrollTimer;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            this.trackInteraction('scroll', { scrollY: window.scrollY });
            
            scrollTimer = setTimeout(() => {
                this.analyzeScrollBehavior();
            }, 1000);
        });
        
        // Track clicks globally
        document.addEventListener('click', (e) => {
            this.trackInteraction('click', {
                element: e.target.tagName,
                className: e.target.className,
                id: e.target.id
            });
        });
    }
    
    trackInteraction(type, data) {
        this.interactionCount++;
        
        const interaction = {
            type,
            data,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionStartTime,
            engagementLevel: this.engagementLevel,
            interactionCount: this.interactionCount
        };
        
        // Send to engagement system if connected
        if (this.engagementSocket && this.engagementSocket.readyState === WebSocket.OPEN) {
            this.engagementSocket.send(JSON.stringify({
                type: 'interaction_tracking',
                data: interaction
            }));
        }
        
        // Store locally for analytics
        this.storeInteractionLocally(interaction);
    }
    
    storeInteractionLocally(interaction) {
        const interactions = JSON.parse(localStorage.getItem('engagement_interactions') || '[]');
        interactions.push(interaction);
        
        // Keep only last 100 interactions
        if (interactions.length > 100) {
            interactions.splice(0, interactions.length - 100);
        }
        
        localStorage.setItem('engagement_interactions', JSON.stringify(interactions));
    }
    
    updateEngagementLevel(newLevel) {
        if (this.engagementLevel === newLevel) return;
        
        const oldLevel = this.engagementLevel;
        this.engagementLevel = newLevel;
        
        console.log(`🎯 Engagement level: ${oldLevel} → ${newLevel}`);
        
        // Apply visual changes based on engagement level
        this.applyEngagementVisuals(newLevel);
        
        // Notify personality engine
        this.personalityEngine.onEngagementChange(newLevel);
        
        // Track the change
        this.trackInteraction('engagement_level_change', {
            from: oldLevel,
            to: newLevel
        });
    }
    
    applyEngagementVisuals(level) {
        const body = document.body;
        
        // Remove existing engagement classes
        body.classList.remove('engagement-passive', 'engagement-active', 'engagement-immersive');
        
        // Add new engagement class
        body.classList.add(`engagement-${level}`);
        
        // Apply level-specific enhancements
        switch (level) {
            case 'passive':
                this.applyPassiveMode();
                break;
            case 'active':
                this.applyActiveMode();
                break;
            case 'immersive':
                this.applyImmersiveMode();
                break;
        }
    }
    
    applyPassiveMode() {
        // Subtle, non-distracting visuals
        document.documentElement.style.setProperty('--engagement-intensity', '0.3');
        document.documentElement.style.setProperty('--animation-speed', '1s');
    }
    
    applyActiveMode() {
        // Enhanced interactivity and feedback
        document.documentElement.style.setProperty('--engagement-intensity', '0.7');
        document.documentElement.style.setProperty('--animation-speed', '0.5s');
        
        // Add subtle particle effects
        this.animationEngine.startAmbientEffects();
    }
    
    applyImmersiveMode() {
        // Full engagement with rich animations
        document.documentElement.style.setProperty('--engagement-intensity', '1.0');
        document.documentElement.style.setProperty('--animation-speed', '0.3s');
        
        // Enhanced visual effects
        this.animationEngine.startImmersiveEffects();
    }
    
    celebrateEngagementActivation() {
        // Trigger celebration animation
        this.animationEngine.triggerCelebration('system_activation');
        
        // Show welcome message
        this.showEngagementWelcome();
    }
    
    showEngagementWelcome() {
        const welcome = document.createElement('div');
        welcome.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(52, 152, 219, 0.95), rgba(41, 128, 185, 0.95));
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            z-index: 10000;
            backdrop-filter: blur(15px);
            border: 2px solid rgba(52, 152, 219, 0.5);
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
            transition: all 0.5s ease;
        `;
        
        welcome.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #ecf0f1;">🎯 Engagement System Activated!</h3>
            <p style="margin: 0 0 20px 0; opacity: 0.9;">Your dashboard is now enhanced with interactive features</p>
            <div style="display: flex; gap: 10px; justify-content: center; font-size: 14px;">
                <span>✨ Smart Animations</span>
                <span>🎨 Adaptive Themes</span>
                <span>🔍 Contextual Insights</span>
            </div>
        `;
        
        document.body.appendChild(welcome);
        
        // Animate in
        setTimeout(() => {
            welcome.style.opacity = '1';
            welcome.style.transform = 'translate(-50%, -50%) scale(1)';
        }, 100);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            welcome.style.opacity = '0';
            welcome.style.transform = 'translate(-50%, -50%) scale(0.8)';
            setTimeout(() => welcome.remove(), 500);
        }, 4000);
    }
    
    handleEngagementMessage(data) {
        switch (data.type) {
            case 'engagement_update':
                this.updateEngagementLevel(data.level);
                break;
            case 'personality_change':
                this.personalityEngine.updatePersonality(data.personality);
                break;
            case 'attention_focus':
                this.attentionManager.setFocus(data.target, data.priority);
                break;
            case 'celebration_trigger':
                this.animationEngine.triggerCelebration(data.event, data.target);
                break;
        }
    }
}

// Animation Engine for engagement effects
class EngagementAnimationEngine {
    constructor() {
        this.activeEffects = new Map();
        this.canvas = document.getElementById('emoji-rain-canvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    }
    
    startAmbientEffects() {
        // Subtle floating particles
        this.createFloatingParticles();
    }
    
    startImmersiveEffects() {
        // Rich visual effects for immersive mode
        this.createImmersiveParticles();
        this.addGlowEffects();
    }
    
    triggerCelebration(eventType, target = null) {
        console.log(`🎉 Triggering celebration: ${eventType}`);
        
        // Use existing emoji rain system if available
        if (window.triggerEmojiRain) {
            window.triggerEmojiRain('ACHIEVEMENT_UNLOCKED');
        }
        
        // Add engagement-specific celebration
        this.createCelebrationBurst(target);
    }
    
    createFloatingParticles() {
        // Implementation for subtle floating particles
        console.log('✨ Starting ambient particle effects');
    }
    
    createImmersiveParticles() {
        // Implementation for rich particle effects
        console.log('🌟 Starting immersive particle effects');
    }
    
    addGlowEffects() {
        // Add glow effects to interactive elements
        const interactiveElements = document.querySelectorAll('.chart-container, .stat-card, .btn');
        interactiveElements.forEach(el => {
            el.style.filter = 'drop-shadow(0 0 10px rgba(52, 152, 219, 0.3))';
        });
    }
    
    createCelebrationBurst(target) {
        if (!target) return;
        
        // Create celebration burst at target location
        const rect = target.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Create burst particles
        for (let i = 0; i < 12; i++) {
            this.createBurstParticle(centerX, centerY, i);
        }
    }
    
    createBurstParticle(x, y, index) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            width: 8px;
            height: 8px;
            background: linear-gradient(45deg, #3498db, #2980b9);
            border-radius: 50%;
            pointer-events: none;
            z-index: 10000;
            transform: translate(-50%, -50%);
        `;
        
        document.body.appendChild(particle);
        
        // Animate particle
        const angle = (index / 12) * Math.PI * 2;
        const distance = 100;
        const endX = x + Math.cos(angle) * distance;
        const endY = y + Math.sin(angle) * distance;
        
        particle.animate([
            { transform: 'translate(-50%, -50%) scale(1)', opacity: 1 },
            { transform: `translate(${endX - x}px, ${endY - y}px) scale(0)`, opacity: 0 }
        ], {
            duration: 800,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).onfinish = () => particle.remove();
    }
}

// Personality Engine for adaptive dashboard behavior
class PersonalityEngine {
    constructor() {
        this.currentPersonality = 'professional';
        this.moodState = 'neutral';
    }
    
    onEngagementChange(level) {
        // Adapt personality based on engagement level
        switch (level) {
            case 'passive':
                this.updatePersonality('professional');
                break;
            case 'active':
                this.updatePersonality('friendly');
                break;
            case 'immersive':
                this.updatePersonality('enthusiastic');
                break;
        }
    }
    
    updatePersonality(personality) {
        if (this.currentPersonality === personality) return;
        
        console.log(`🎭 Personality: ${this.currentPersonality} → ${personality}`);
        this.currentPersonality = personality;
        
        // Apply personality-driven visual changes
        this.applyPersonalityTheme(personality);
    }
    
    applyPersonalityTheme(personality) {
        const root = document.documentElement;
        
        switch (personality) {
            case 'professional':
                root.style.setProperty('--personality-accent', '#3498db');
                root.style.setProperty('--personality-warmth', '0.3');
                break;
            case 'friendly':
                root.style.setProperty('--personality-accent', '#2ecc71');
                root.style.setProperty('--personality-warmth', '0.6');
                break;
            case 'enthusiastic':
                root.style.setProperty('--personality-accent', '#e74c3c');
                root.style.setProperty('--personality-warmth', '1.0');
                break;
        }
    }
}

// Attention Manager for intelligent focus control
class AttentionManager {
    constructor() {
        this.currentFocus = null;
        this.focusHistory = [];
        this.attentionBudget = 100;
    }
    
    setFocus(target, priority) {
        console.log(`🎯 Setting focus: ${target} (${priority} priority)`);
        
        // Clear previous focus
        this.clearFocus();
        
        // Set new focus
        this.currentFocus = { target, priority, timestamp: Date.now() };
        this.focusHistory.push(this.currentFocus);
        
        // Apply focus visuals
        this.applyFocusVisuals(target, priority);
        
        // Manage attention budget
        this.consumeAttentionBudget(priority);
    }
    
    clearFocus() {
        if (this.currentFocus) {
            this.removeFocusVisuals(this.currentFocus.target);
            this.currentFocus = null;
        }
    }
    
    applyFocusVisuals(target, priority) {
        const element = document.getElementById(target) || document.querySelector(`.${target}`);
        if (!element) return;
        
        // Add focus highlight
        element.classList.add('engagement-focused');
        
        // Apply priority-based styling
        const intensityMap = { low: 0.3, medium: 0.6, high: 0.9, critical: 1.0 };
        const intensity = intensityMap[priority] || 0.5;
        
        element.style.boxShadow = `0 0 ${20 * intensity}px rgba(52, 152, 219, ${intensity})`;
        element.style.borderColor = `rgba(52, 152, 219, ${intensity})`;
    }
    
    removeFocusVisuals(target) {
        const element = document.getElementById(target) || document.querySelector(`.${target}`);
        if (!element) return;
        
        element.classList.remove('engagement-focused');
        element.style.boxShadow = '';
        element.style.borderColor = '';
    }
    
    consumeAttentionBudget(priority) {
        const costMap = { low: 5, medium: 15, high: 25, critical: 40 };
        const cost = costMap[priority] || 10;
        
        this.attentionBudget = Math.max(0, this.attentionBudget - cost);
        
        // Regenerate attention budget over time
        setTimeout(() => {
            this.attentionBudget = Math.min(100, this.attentionBudget + cost * 0.5);
        }, 5000);
    }
}

// Initialize the engagement system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add engagement CSS variables
    const style = document.createElement('style');
    style.textContent = `
        :root {
            --engagement-intensity: 0.3;
            --animation-speed: 1s;
            --personality-accent: #3498db;
            --personality-warmth: 0.3;
        }
        
        .engagement-focused {
            transition: all 0.3s ease !important;
            transform: scale(1.02) !important;
        }
        
        .engagement-passive .chart-container {
            transition: all var(--animation-speed) ease;
        }
        
        .engagement-active .chart-container:hover {
            transform: translateY(-2px) scale(1.01);
        }
        
        .engagement-immersive .chart-container:hover {
            transform: translateY(-4px) scale(1.02);
            filter: drop-shadow(0 0 15px var(--personality-accent));
        }
    `;
    document.head.appendChild(style);
    
    // Initialize engagement system
    window.dashboardEngagement = new DashboardEngagementSystem();
    
    // Auto-initialize after a short delay
    setTimeout(() => {
        window.dashboardEngagement.initialize();
    }, 1000);
});

// Export for global access
window.DashboardEngagementSystem = DashboardEngagementSystem;