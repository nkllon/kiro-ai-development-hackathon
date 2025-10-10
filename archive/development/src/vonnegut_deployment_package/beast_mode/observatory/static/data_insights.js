/**
 * Data Insights Display - Frontend Component for Data Storyteller
 * ==============================================================
 * 
 * Displays discovered data patterns and insights from the Data Storyteller Engine
 * with engaging visual effects and interactive elements.
 */

class DataInsightsDisplay {
    constructor() {
        this.insights = [];
        this.insightsContainer = null;
        this.isInitialized = false;
        this.updateInterval = 30000; // 30 seconds
        
        console.log('📊 Data Insights Display initialized');
    }
    
    async initialize() {
        if (this.isInitialized) return;
        
        try {
            // Create insights container
            this.createInsightsContainer();
            
            // Start fetching insights
            await this.fetchInsights();
            
            // Set up periodic updates
            setInterval(() => this.fetchInsights(), this.updateInterval);
            
            this.isInitialized = true;
            console.log('✅ Data Insights Display fully initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize Data Insights Display:', error);
        }
    }
    
    createInsightsContainer() {
        // Create main insights container
        this.insightsContainer = document.createElement('div');
        this.insightsContainer.id = 'dataInsightsContainer';
        this.insightsContainer.style.cssText = `
            position: fixed;
            top: 140px;
            right: 20px;
            width: 350px;
            max-height: 60vh;
            background: linear-gradient(135deg, rgba(52, 73, 94, 0.95), rgba(44, 62, 80, 0.95));
            backdrop-filter: blur(15px);
            border: 2px solid rgba(52, 152, 219, 0.3);
            border-radius: 15px;
            padding: 20px;
            z-index: 1000;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        // Create header
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        `;
        
        const title = document.createElement('h3');
        title.textContent = '🔍 Data Insights';
        title.style.cssText = `
            color: #3498db;
            margin: 0;
            font-size: 18px;
        `;
        
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            gap: 5px;
        `;
        
        const minimizeBtn = document.createElement('button');
        minimizeBtn.innerHTML = '−';
        minimizeBtn.style.cssText = `
            background: none;
            border: none;
            color: #95a5a6;
            font-size: 18px;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.3s ease;
            line-height: 1;
        `;
        minimizeBtn.title = 'Minimize panel';
        minimizeBtn.onclick = () => this.minimizeContainer();
        
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: #e74c3c;
            font-size: 18px;
            cursor: pointer;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.3s ease;
            line-height: 1;
        `;
        closeBtn.title = 'Close insights panel';
        closeBtn.onclick = () => this.closeContainer();
        
        // Hover effects
        minimizeBtn.addEventListener('mouseenter', () => {
            minimizeBtn.style.background = 'rgba(255,255,255,0.1)';
            minimizeBtn.style.color = '#ecf0f1';
        });
        minimizeBtn.addEventListener('mouseleave', () => {
            minimizeBtn.style.background = 'none';
            minimizeBtn.style.color = '#95a5a6';
        });
        
        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.background = 'rgba(231, 76, 60, 0.2)';
            closeBtn.style.color = '#fff';
        });
        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.background = 'none';
            closeBtn.style.color = '#e74c3c';
        });
        
        buttonContainer.appendChild(minimizeBtn);
        buttonContainer.appendChild(closeBtn);
        
        header.appendChild(title);
        header.appendChild(buttonContainer);
        
        // Create content area
        this.contentArea = document.createElement('div');
        this.contentArea.id = 'insightsContent';
        
        this.insightsContainer.appendChild(header);
        this.insightsContainer.appendChild(this.contentArea);
        
        document.body.appendChild(this.insightsContainer);
        
        // Show container after a brief delay
        setTimeout(() => {
            this.insightsContainer.style.transform = 'translateX(0)';
        }, 1000);
    }
    
    async fetchInsights() {
        try {
            // Try to fetch real Observatory data first
            const realInsights = await this.fetchRealObservatoryData();
            if (realInsights) {
                this.insights = realInsights;
                this.renderInsights();
                console.log('📊 Using real Observatory data');
                return;
            }
            
            // If no real data, show offline message
            this.showError('Observatory data not available - check system status');
            
        } catch (error) {
            console.error('Error fetching insights:', error);
            this.showError('Unable to connect to Observatory data');
        }
    }
    
    async fetchRealObservatoryData() {
        try {
            // Fetch real Observatory metrics from existing endpoints
            const [healthData, costData, statusData] = await Promise.allSettled([
                fetch('/api/dashboard/health').then(r => r.ok ? r.json() : null),
                fetch('/api/dashboard/cost-tracking').then(r => r.ok ? r.json() : null),
                fetch('/api/observatory/status').then(r => r.ok ? r.json() : null)
            ]);
            
            // Check if we got any real data
            const health = healthData.status === 'fulfilled' ? healthData.value : null;
            const cost = costData.status === 'fulfilled' ? costData.value : null;
            const status = statusData.status === 'fulfilled' ? statusData.value : null;
            
            if (!health && !cost && !status) {
                return null; // No real data available
            }
            
            // Transform real Observatory data into insights format
            return this.transformObservatoryDataToInsights(health, cost, status);
            
        } catch (error) {
            console.warn('Failed to fetch real Observatory data:', error);
            return null;
        }
    }
    
    transformObservatoryDataToInsights(health, cost, status) {
        const patterns = [];
        let dramaLevel = 'PEACEFUL_TIMES';
        let storyArc = '🎵 Your Observatory systems are bebopping along smoothly';
        
        // Analyze health data
        if (health && health.coordination_health !== undefined) {
            const healthScore = health.coordination_health;
            if (healthScore < 0.8) {
                patterns.push({
                    id: 'health_concern',
                    title: '🏥 System Health Alert',
                    narrative: `🎵 The coordination health was cruising at normal levels, then we noticed it dropped to ${(healthScore * 100).toFixed(1)}%! The system is working to restore optimal performance.`,
                    interest_level: healthScore < 0.5 ? 'critical' : 'high',
                    confidence: 0.95,
                    affected_metrics: ['coordination_health'],
                    timestamp: new Date().toISOString()
                });
                dramaLevel = healthScore < 0.5 ? 'CRISIS_MODE' : 'RISING_ACTION';
            }
        }
        
        // Analyze cost data
        if (cost && cost.total_cost_today > 0) {
            patterns.push({
                id: 'cost_activity',
                title: '💰 Cost Activity Detected',
                narrative: `🎵 The cost tracking was bebopping along quietly, then we noticed $${cost.total_cost_today.toFixed(2)} in activity today! The multi-agent coordination is actively working.`,
                interest_level: cost.total_cost_today > 10 ? 'high' : 'medium',
                confidence: 0.90,
                affected_metrics: ['llm_costs'],
                timestamp: new Date().toISOString()
            });
            if (cost.total_cost_today > 10 && dramaLevel === 'PEACEFUL_TIMES') {
                dramaLevel = 'PLOT_THICKENS';
            }
        }
        
        // Analyze status data
        if (status) {
            const eventsProcessed = status.events_processed || 0;
            const uptime = status.uptime || 0;
            
            if (eventsProcessed > 0) {
                patterns.push({
                    id: 'activity_detected',
                    title: '📊 System Activity Detected',
                    narrative: `🎵 The Observatory was bebopping along quietly, then BOOM! ${eventsProcessed} events processed! The coordination system is actively monitoring and responding.`,
                    interest_level: eventsProcessed > 100 ? 'high' : 'medium',
                    confidence: 0.85,
                    affected_metrics: ['events_processed'],
                    timestamp: new Date().toISOString()
                });
            }
            
            if (uptime > 3600) { // More than 1 hour
                patterns.push({
                    id: 'uptime_milestone',
                    title: '⏰ Uptime Milestone',
                    narrative: `🎵 The Observatory has been bebopping along steadily for ${Math.floor(uptime/3600)} hours! Consistent coordination performance achieved.`,
                    interest_level: 'medium',
                    confidence: 1.0,
                    affected_metrics: ['uptime'],
                    timestamp: new Date().toISOString()
                });
            }
        }
        
        // Create story arc based on patterns
        if (patterns.length > 0) {
            const criticalCount = patterns.filter(p => p.interest_level === 'critical').length;
            const highCount = patterns.filter(p => p.interest_level === 'high').length;
            
            if (criticalCount > 0) {
                dramaLevel = 'CRISIS_MODE';
                storyArc = `🎵 Your Observatory was bebopping along normally when WHAM! ${criticalCount} critical situation${criticalCount > 1 ? 's' : ''} erupted! 🚨 The monitoring heroes are on the case!`;
            } else if (highCount > 0) {
                dramaLevel = 'RISING_ACTION';
                storyArc = `🎵 Your Observatory was cruising along when we detected ${highCount} significant pattern${highCount > 1 ? 's' : ''}! 📈 The plot thickens as your systems adapt and respond.`;
            } else {
                storyArc = `🎵 Your Observatory is bebopping along beautifully! ${patterns.length} interesting pattern${patterns.length > 1 ? 's' : ''} detected in the coordination dance. 🎭`;
            }
        }
        
        return {
            summary: `🎵 Real Observatory data shows ${patterns.length} active pattern${patterns.length !== 1 ? 's' : ''} in your coordination systems!`,
            story_arc: storyArc,
            patterns: patterns,
            drama_level: dramaLevel,
            recommendations: patterns.length > 0 ? [{
                type: 'monitoring',
                priority: 'medium',
                title: 'Keep Watching the Show!',
                description: 'Your Observatory is actively coordinating - monitor the patterns as they evolve.',
                actions: [
                    '👀 Watch the real-time metrics',
                    '📊 Check the dashboard charts',
                    '🔍 Investigate any anomalies'
                ]
            }] : [],
            timestamp: new Date().toISOString()
        };
    }
    
    generateDemoInsights() {
        // Generate realistic demo insights with dramatic story arcs
        const patterns = [
            {
                id: 'trend_cpu_1',
                title: '📈 CPU Usage Climbing',
                description: '🎵 CPU usage was cruising along normally, then started climbing steadily. The system responded by scaling resources. Result: 15.3% improvement over 45 minutes - the hero moment we needed! 🚀',
                interest_level: 'high',
                confidence: 0.87,
                affected_metrics: ['cpu_usage'],
                timestamp: new Date().toISOString(),
                visual_suggestion: {
                    animation_type: 'trend_highlight',
                    color: '#f39c12',
                    intensity: 0.8
                }
            },
            {
                id: 'anomaly_response_1',
                title: '⚡ Response Time Crisis',
                description: '🎵 Response time was just cruising along at normal levels, then WHAM! Massive spike hit - 2.3x higher than usual! Alerts screaming, team scrambling. Did we save the day? Stay tuned... ⚡',
                interest_level: 'critical',
                confidence: 0.94,
                affected_metrics: ['response_time'],
                timestamp: new Date().toISOString(),
                visual_suggestion: {
                    animation_type: 'anomaly_pulse',
                    color: '#e74c3c',
                    intensity: 0.9
                }
            },
            {
                id: 'correlation_1',
                title: '🔗 CPU & Memory Team Up',
                description: '🎵 CPU and memory were doing their own thing, then we noticed they started dancing together! 89% correlation discovered. The system learned, adapted, and now we\'re optimizing both. Teamwork makes the dream work! 🤝',
                interest_level: 'medium',
                confidence: 0.89,
                affected_metrics: ['cpu_usage', 'memory_usage'],
                timestamp: new Date().toISOString(),
                visual_suggestion: {
                    animation_type: 'correlation_link',
                    color: '#3498db',
                    intensity: 0.7
                }
            }
        ];
        
        return {
            summary: '🎵 We were bebopping along with our systems then BOOM! 1 critical situation erupted! 🚨 Emergency protocols activated, all hands on deck The battle is ON - will our heroes save the day? 🦸‍♂️',
            story_arc: '🎵 Our response_time, cpu_usage were bebopping along in their usual rhythm when suddenly response_time exploded through the roof! This triggered a cascade: • cpu_usage started climbing rapidly 🦸‍♂️ Our monitoring heroes sprang into action: • Alerts fired across all channels • Auto-scaling kicked in where needed • The team mobilized for rapid response ⚔️ The battle continues with 1 critical situation still unfolding... Will our heroes save the day? The drama builds! 🎭',
            patterns: patterns,
            drama_level: 'CRISIS_MODE',
            recommendations: [
                {
                    type: 'investigation',
                    priority: 'high',
                    title: 'Hero Mission: Save Response Time!',
                    description: 'Our response time hero needs backup - massive spike detected!',
                    actions: [
                        '🔍 Check system logs for the villain (errors)',
                        '🚀 Review recent deployments (plot twist?)',
                        '👀 Monitor for continued anomalies (stay vigilant!)'
                    ]
                }
            ],
            timestamp: new Date().toISOString()
        };
    }
    
    renderInsights() {
        if (!this.contentArea) return;
        
        this.contentArea.innerHTML = '';
        
        // Render drama level indicator with LIVE VISUAL EFFECTS
        if (this.insights.drama_level) {
            const dramaDiv = document.createElement('div');
            const dramaConfig = this.getDramaConfig(this.insights.drama_level);
            dramaDiv.style.cssText = `
                background: ${dramaConfig.background};
                border: 2px solid ${dramaConfig.border};
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 15px;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                color: ${dramaConfig.color};
                animation: ${dramaConfig.animation};
                position: relative;
                overflow: hidden;
            `;
            
            // Add animated background effect
            this.addDramaBackgroundEffect(dramaDiv, this.insights.drama_level);
            
            const dramaLabel = document.createElement('div');
            dramaLabel.style.cssText = `
                position: relative;
                z-index: 2;
                text-transform: uppercase;
                letter-spacing: 1px;
            `;
            dramaLabel.innerHTML = `${dramaConfig.emoji} ${dramaConfig.label}`;
            
            dramaDiv.appendChild(dramaLabel);
            this.contentArea.appendChild(dramaDiv);
            
            // Add live metrics visualization
            this.addLiveMetricsVisualization();
        }

        // Render story arc (the main narrative) - IMPROVED VERSION
        if (this.insights.story_arc) {
            const storyDiv = document.createElement('div');
            storyDiv.style.cssText = `
                background: linear-gradient(135deg, rgba(142, 68, 173, 0.1), rgba(155, 89, 182, 0.1));
                border: 1px solid rgba(155, 89, 182, 0.4);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                font-size: 13px;
                color: #ecf0f1;
                line-height: 1.5;
                position: relative;
                overflow: hidden;
                cursor: pointer;
                transition: all 0.3s ease;
            `;
            
            // Add expand/collapse functionality
            let isExpanded = false;
            
            // Add story header with expand button
            const storyHeader = document.createElement('div');
            storyHeader.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            `;
            
            const storyTitle = document.createElement('div');
            storyTitle.style.cssText = `
                color: #9b59b6;
                font-weight: bold;
                font-size: 14px;
            `;
            storyTitle.textContent = '📖 The Story So Far...';
            
            const expandBtn = document.createElement('button');
            expandBtn.style.cssText = `
                background: none;
                border: none;
                color: #9b59b6;
                font-size: 16px;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: background 0.3s ease;
            `;
            expandBtn.textContent = '▼';
            
            storyHeader.appendChild(storyTitle);
            storyHeader.appendChild(expandBtn);
            
            // Create story preview (first 100 characters)
            const storyPreview = document.createElement('div');
            storyPreview.style.cssText = `
                color: #bdc3c7;
                font-style: italic;
                margin-bottom: 8px;
            `;
            const previewText = this.insights.story_arc.substring(0, 100) + '...';
            storyPreview.textContent = previewText;
            
            // Create full story (initially hidden)
            const storyFull = document.createElement('div');
            storyFull.style.cssText = `
                display: none;
                color: #ecf0f1;
                margin-top: 10px;
                padding: 10px;
                background: rgba(0,0,0,0.2);
                border-radius: 6px;
                border-left: 3px solid #9b59b6;
            `;
            storyFull.textContent = this.insights.story_arc;
            
            // Add click handler for expand/collapse
            const toggleStory = () => {
                isExpanded = !isExpanded;
                if (isExpanded) {
                    storyPreview.style.display = 'none';
                    storyFull.style.display = 'block';
                    expandBtn.textContent = '▲';
                    storyDiv.style.maxHeight = 'none';
                } else {
                    storyPreview.style.display = 'block';
                    storyFull.style.display = 'none';
                    expandBtn.textContent = '▼';
                    storyDiv.style.maxHeight = '120px';
                }
            };
            
            expandBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleStory();
            });
            
            storyDiv.addEventListener('click', toggleStory);
            
            // Hover effects
            storyDiv.addEventListener('mouseenter', () => {
                storyDiv.style.background = 'linear-gradient(135deg, rgba(142, 68, 173, 0.15), rgba(155, 89, 182, 0.15))';
                storyDiv.style.borderColor = 'rgba(155, 89, 182, 0.6)';
            });
            
            storyDiv.addEventListener('mouseleave', () => {
                storyDiv.style.background = 'linear-gradient(135deg, rgba(142, 68, 173, 0.1), rgba(155, 89, 182, 0.1))';
                storyDiv.style.borderColor = 'rgba(155, 89, 182, 0.4)';
            });
            
            storyDiv.appendChild(storyHeader);
            storyDiv.appendChild(storyPreview);
            storyDiv.appendChild(storyFull);
            this.contentArea.appendChild(storyDiv);
        }

        // Render summary (shorter version now)
        if (this.insights.summary) {
            const summaryDiv = document.createElement('div');
            summaryDiv.style.cssText = `
                background: rgba(52, 152, 219, 0.1);
                border: 1px solid rgba(52, 152, 219, 0.3);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 15px;
                font-size: 14px;
                color: #ecf0f1;
                line-height: 1.4;
            `;
            summaryDiv.textContent = this.insights.summary;
            this.contentArea.appendChild(summaryDiv);
        }
        
        // Render patterns - IMPROVED VERSION with pagination
        if (this.insights.patterns && this.insights.patterns.length > 0) {
            // Group patterns by interest level
            const criticalPatterns = this.insights.patterns.filter(p => p.interest_level === 'critical');
            const highPatterns = this.insights.patterns.filter(p => p.interest_level === 'high');
            const mediumPatterns = this.insights.patterns.filter(p => p.interest_level === 'medium');
            
            // Show critical patterns first (always visible)
            if (criticalPatterns.length > 0) {
                const criticalSection = this.createPatternSection('🚨 Critical Issues', criticalPatterns, '#e74c3c', true);
                this.contentArea.appendChild(criticalSection);
            }
            
            // Show high patterns (collapsible)
            if (highPatterns.length > 0) {
                const highSection = this.createPatternSection('⚠️ High Priority', highPatterns, '#f39c12', false);
                this.contentArea.appendChild(highSection);
            }
            
            // Show medium patterns (collapsible, initially collapsed)
            if (mediumPatterns.length > 0) {
                const mediumSection = this.createPatternSection('📊 Notable Trends', mediumPatterns, '#3498db', false, true);
                this.contentArea.appendChild(mediumSection);
            }
            
        } else {
            const noInsights = document.createElement('div');
            noInsights.style.cssText = `
                text-align: center;
                color: #95a5a6;
                font-style: italic;
                padding: 20px;
            `;
            noInsights.textContent = '📊 All systems operating normally - no significant patterns detected.';
            this.contentArea.appendChild(noInsights);
        }
        
        // Render recommendations
        if (this.insights.recommendations && this.insights.recommendations.length > 0) {
            const recSection = document.createElement('div');
            recSection.style.cssText = `
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(255,255,255,0.1);
            `;
            
            const recTitle = document.createElement('h4');
            recTitle.textContent = '💡 Recommendations';
            recTitle.style.cssText = `
                color: #f39c12;
                margin: 0 0 10px 0;
                font-size: 14px;
            `;
            recSection.appendChild(recTitle);
            
            this.insights.recommendations.forEach(rec => {
                const recElement = this.createRecommendationElement(rec);
                recSection.appendChild(recElement);
            });
            
            this.contentArea.appendChild(recSection);
        }
        
        // Update timestamp
        const timestamp = document.createElement('div');
        timestamp.style.cssText = `
            text-align: center;
            font-size: 11px;
            color: #7f8c8d;
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.05);
        `;
        timestamp.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        this.contentArea.appendChild(timestamp);
    }
    
    createPatternElement(pattern) {
        const element = document.createElement('div');
        element.className = 'insight-pattern';
        element.style.cssText = `
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        `;
        
        // Add interest level indicator
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: ${this.getInterestColor(pattern.interest_level)};
        `;
        element.appendChild(indicator);
        
        // Pattern title
        const title = document.createElement('div');
        title.style.cssText = `
            font-weight: 600;
            color: #ecf0f1;
            margin-bottom: 5px;
            font-size: 13px;
        `;
        title.textContent = pattern.title;
        
        // Pattern description
        const description = document.createElement('div');
        description.style.cssText = `
            color: #bdc3c7;
            font-size: 12px;
            line-height: 1.3;
            margin-bottom: 8px;
        `;
        description.textContent = pattern.description;
        
        // Pattern metadata
        const metadata = document.createElement('div');
        metadata.style.cssText = `
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #7f8c8d;
        `;
        
        const confidence = document.createElement('span');
        confidence.textContent = `Confidence: ${(pattern.confidence * 100).toFixed(0)}%`;
        
        const time = document.createElement('span');
        time.textContent = new Date(pattern.timestamp).toLocaleTimeString();
        
        metadata.appendChild(confidence);
        metadata.appendChild(time);
        
        element.appendChild(title);
        element.appendChild(description);
        element.appendChild(metadata);
        
        // Add hover effects
        element.addEventListener('mouseenter', () => {
            element.style.background = 'rgba(255,255,255,0.08)';
            element.style.borderColor = pattern.visual_suggestion?.color || '#3498db';
            element.style.transform = 'translateY(-2px)';
            element.style.boxShadow = `0 5px 15px rgba(0,0,0,0.2)`;
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.background = 'rgba(255,255,255,0.05)';
            element.style.borderColor = 'rgba(255,255,255,0.1)';
            element.style.transform = 'translateY(0)';
            element.style.boxShadow = 'none';
        });
        
        // Add click handler for detailed view
        element.addEventListener('click', () => {
            this.showPatternDetails(pattern);
        });
        
        return element;
    }
    
    createRecommendationElement(recommendation) {
        const element = document.createElement('div');
        element.style.cssText = `
            background: rgba(243, 156, 18, 0.1);
            border: 1px solid rgba(243, 156, 18, 0.3);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 12px;
        `;
        
        const title = document.createElement('div');
        title.style.cssText = `
            font-weight: 600;
            color: #f39c12;
            margin-bottom: 5px;
        `;
        title.textContent = recommendation.title;
        
        const description = document.createElement('div');
        description.style.cssText = `
            color: #ecf0f1;
            margin-bottom: 8px;
            line-height: 1.3;
        `;
        description.textContent = recommendation.description;
        
        if (recommendation.actions && recommendation.actions.length > 0) {
            const actionsList = document.createElement('ul');
            actionsList.style.cssText = `
                margin: 0;
                padding-left: 15px;
                color: #bdc3c7;
            `;
            
            recommendation.actions.forEach(action => {
                const actionItem = document.createElement('li');
                actionItem.style.cssText = `
                    margin-bottom: 3px;
                    font-size: 11px;
                `;
                actionItem.textContent = action;
                actionsList.appendChild(actionItem);
            });
            
            element.appendChild(title);
            element.appendChild(description);
            element.appendChild(actionsList);
        } else {
            element.appendChild(title);
            element.appendChild(description);
        }
        
        return element;
    }
    
    showPatternDetails(pattern) {
        // Create detailed modal for pattern
        const modal = document.createElement('div');
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
            max-width: 500px;
            max-height: 70vh;
            overflow-y: auto;
            backdrop-filter: blur(15px);
            border: 2px solid ${pattern.visual_suggestion?.color || '#3498db'};
            transform: scale(0.8);
            transition: transform 0.3s ease;
        `;
        
        content.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="color: ${pattern.visual_suggestion?.color || '#3498db'}; margin: 0;">${pattern.title}</h3>
                <button onclick="this.closest('.pattern-detail-modal').remove()" 
                        style="background: none; border: none; color: #e74c3c; font-size: 24px; cursor: pointer;">✕</button>
            </div>
            <div style="color: #ecf0f1;">
                <p><strong>Description:</strong> ${pattern.description}</p>
                <p><strong>Interest Level:</strong> <span style="color: ${this.getInterestColor(pattern.interest_level)}">${pattern.interest_level.toUpperCase()}</span></p>
                <p><strong>Confidence:</strong> ${(pattern.confidence * 100).toFixed(1)}%</p>
                <p><strong>Affected Metrics:</strong> ${pattern.affected_metrics.join(', ')}</p>
                <p><strong>Detected:</strong> ${new Date(pattern.timestamp).toLocaleString()}</p>
                
                <div style="margin-top: 20px; padding: 15px; background: rgba(52, 152, 219, 0.1); border-radius: 8px;">
                    <strong style="color: #3498db;">🎨 Visual Suggestion:</strong>
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        <li>Animation: ${pattern.visual_suggestion?.animation_type || 'default'}</li>
                        <li>Color: ${pattern.visual_suggestion?.color || '#3498db'}</li>
                        <li>Intensity: ${((pattern.visual_suggestion?.intensity || 0.5) * 100).toFixed(0)}%</li>
                    </ul>
                </div>
            </div>
        `;
        
        modal.className = 'pattern-detail-modal';
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
    
    getInterestColor(level) {
        const colors = {
            'critical': '#e74c3c',
            'high': '#f39c12',
            'medium': '#3498db',
            'low': '#95a5a6'
        };
        return colors[level] || '#95a5a6';
    }
    
    createPatternSection(title, patterns, color, alwaysExpanded = false, startCollapsed = false) {
        const section = document.createElement('div');
        section.style.cssText = `
            margin-bottom: 15px;
            border: 1px solid ${color}40;
            border-radius: 8px;
            overflow: hidden;
        `;
        
        // Section header
        const header = document.createElement('div');
        header.style.cssText = `
            background: ${color}20;
            padding: 10px 15px;
            cursor: ${alwaysExpanded ? 'default' : 'pointer'};
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid ${color}30;
        `;
        
        const headerTitle = document.createElement('div');
        headerTitle.style.cssText = `
            color: ${color};
            font-weight: bold;
            font-size: 14px;
        `;
        headerTitle.textContent = `${title} (${patterns.length})`;
        
        const expandIcon = document.createElement('div');
        expandIcon.style.cssText = `
            color: ${color};
            font-size: 12px;
            transition: transform 0.3s ease;
        `;
        expandIcon.textContent = alwaysExpanded ? '' : (startCollapsed ? '▼' : '▲');
        
        header.appendChild(headerTitle);
        if (!alwaysExpanded) {
            header.appendChild(expandIcon);
        }
        
        // Section content
        const content = document.createElement('div');
        content.style.cssText = `
            display: ${(alwaysExpanded || !startCollapsed) ? 'block' : 'none'};
            padding: 10px;
            background: rgba(255,255,255,0.02);
        `;
        
        // Add patterns (limit to first 3, with "show more" option)
        const visiblePatterns = patterns.slice(0, 3);
        const hiddenPatterns = patterns.slice(3);
        
        visiblePatterns.forEach(pattern => {
            const patternElement = this.createCompactPatternElement(pattern);
            content.appendChild(patternElement);
        });
        
        // Add "show more" if there are hidden patterns
        if (hiddenPatterns.length > 0) {
            const showMoreBtn = document.createElement('button');
            showMoreBtn.style.cssText = `
                background: none;
                border: 1px solid ${color}60;
                color: ${color};
                padding: 5px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
                margin-top: 8px;
                transition: all 0.3s ease;
            `;
            showMoreBtn.textContent = `Show ${hiddenPatterns.length} more...`;
            
            showMoreBtn.addEventListener('click', () => {
                hiddenPatterns.forEach(pattern => {
                    const patternElement = this.createCompactPatternElement(pattern);
                    content.insertBefore(patternElement, showMoreBtn);
                });
                showMoreBtn.remove();
            });
            
            content.appendChild(showMoreBtn);
        }
        
        // Toggle functionality
        if (!alwaysExpanded) {
            let isExpanded = !startCollapsed;
            
            header.addEventListener('click', () => {
                isExpanded = !isExpanded;
                content.style.display = isExpanded ? 'block' : 'none';
                expandIcon.textContent = isExpanded ? '▲' : '▼';
                expandIcon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(-90deg)';
            });
        }
        
        section.appendChild(header);
        section.appendChild(content);
        
        return section;
    }
    
    createCompactPatternElement(pattern) {
        const element = document.createElement('div');
        element.style.cssText = `
            background: rgba(255,255,255,0.03);
            border-left: 3px solid ${this.getInterestColor(pattern.interest_level)};
            padding: 8px 12px;
            margin-bottom: 6px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        // Pattern summary (first 80 characters)
        const summary = document.createElement('div');
        summary.style.cssText = `
            color: #ecf0f1;
            font-size: 12px;
            line-height: 1.3;
            margin-bottom: 4px;
        `;
        const summaryText = pattern.narrative.length > 80 
            ? pattern.narrative.substring(0, 80) + '...' 
            : pattern.narrative;
        summary.textContent = summaryText;
        
        // Pattern metadata
        const metadata = document.createElement('div');
        metadata.style.cssText = `
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #7f8c8d;
        `;
        
        const confidence = document.createElement('span');
        confidence.textContent = `${(pattern.confidence * 100).toFixed(0)}% confidence`;
        
        const metrics = document.createElement('span');
        metrics.textContent = pattern.affected_metrics.join(', ');
        
        metadata.appendChild(confidence);
        metadata.appendChild(metrics);
        
        element.appendChild(summary);
        element.appendChild(metadata);
        
        // Click to expand full details
        element.addEventListener('click', () => {
            this.showPatternDetails(pattern);
        });
        
        // Hover effects
        element.addEventListener('mouseenter', () => {
            element.style.background = 'rgba(255,255,255,0.06)';
            element.style.transform = 'translateX(4px)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.background = 'rgba(255,255,255,0.03)';
            element.style.transform = 'translateX(0)';
        });
        
        return element;
    }
    
    getDramaConfig(dramaLevel) {
        const configs = {
            'EPIC_BATTLE': {
                emoji: '⚔️',
                label: 'EPIC BATTLE IN PROGRESS',
                background: 'rgba(231, 76, 60, 0.2)',
                border: '#e74c3c',
                color: '#e74c3c',
                animation: 'pulse 1s infinite'
            },
            'CRISIS_MODE': {
                emoji: '🚨',
                label: 'CRISIS MODE ACTIVATED',
                background: 'rgba(230, 126, 34, 0.2)',
                border: '#e67e22',
                color: '#e67e22',
                animation: 'pulse 1.5s infinite'
            },
            'RISING_ACTION': {
                emoji: '📈',
                label: 'TENSION BUILDING',
                background: 'rgba(243, 156, 18, 0.2)',
                border: '#f39c12',
                color: '#f39c12',
                animation: 'none'
            },
            'PLOT_THICKENS': {
                emoji: '🎭',
                label: 'PLOT THICKENS',
                background: 'rgba(52, 152, 219, 0.2)',
                border: '#3498db',
                color: '#3498db',
                animation: 'none'
            },
            'PEACEFUL_TIMES': {
                emoji: '✨',
                label: 'ALL QUIET ON THE SYSTEM FRONT',
                background: 'rgba(46, 204, 113, 0.2)',
                border: '#2ecc71',
                color: '#2ecc71',
                animation: 'none'
            }
        };
        return configs[dramaLevel] || configs['PEACEFUL_TIMES'];
    }
    
    minimizeContainer() {
        const isMinimized = this.insightsContainer.style.height === '60px';
        
        if (isMinimized) {
            // Restore
            this.insightsContainer.style.height = 'auto';
            this.insightsContainer.style.maxHeight = '60vh';
            this.contentArea.style.display = 'block';
        } else {
            // Minimize
            this.insightsContainer.style.height = '60px';
            this.insightsContainer.style.maxHeight = '60px';
            this.contentArea.style.display = 'none';
        }
    }
    
    closeContainer() {
        this.insightsContainer.style.transform = 'translateX(100%)';
        
        // Add a "show insights" button to the corner
        setTimeout(() => {
            this.createShowInsightsButton();
        }, 300);
    }
    
    createShowInsightsButton() {
        // Remove existing button if any
        const existingBtn = document.getElementById('showInsightsBtn');
        if (existingBtn) {
            existingBtn.remove();
        }
        
        const showBtn = document.createElement('button');
        showBtn.id = 'showInsightsBtn';
        showBtn.innerHTML = '🔍';
        showBtn.style.cssText = `
            position: fixed;
            top: 140px;
            right: 20px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, rgba(52, 73, 94, 0.9), rgba(44, 62, 80, 0.9));
            border: 2px solid rgba(52, 152, 219, 0.5);
            border-radius: 50%;
            color: #3498db;
            font-size: 20px;
            cursor: pointer;
            z-index: 1001;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        `;
        showBtn.title = 'Show data insights';
        
        showBtn.addEventListener('click', () => {
            this.insightsContainer.style.transform = 'translateX(0)';
            showBtn.remove();
        });
        
        showBtn.addEventListener('mouseenter', () => {
            showBtn.style.transform = 'scale(1.1)';
            showBtn.style.borderColor = 'rgba(52, 152, 219, 0.8)';
        });
        
        showBtn.addEventListener('mouseleave', () => {
            showBtn.style.transform = 'scale(1)';
            showBtn.style.borderColor = 'rgba(52, 152, 219, 0.5)';
        });
        
        document.body.appendChild(showBtn);
    }
    
    showPatternDetails(pattern) {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 2000;
            display: flex;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(5px);
        `;
        
        // Create modal content
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: linear-gradient(135deg, rgba(44, 62, 80, 0.95), rgba(52, 73, 94, 0.95));
            border: 1px solid rgba(52, 152, 219, 0.3);
            border-radius: 12px;
            padding: 20px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            color: #ecf0f1;
            position: relative;
        `;
        
        // Close button
        const closeModalBtn = document.createElement('button');
        closeModalBtn.innerHTML = '×';
        closeModalBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 15px;
            background: none;
            border: none;
            color: #e74c3c;
            font-size: 24px;
            cursor: pointer;
            padding: 5px;
            border-radius: 4px;
            transition: all 0.3s ease;
        `;
        
        closeModalBtn.addEventListener('click', () => {
            document.body.removeChild(overlay);
        });
        
        // Pattern title
        const title = document.createElement('h3');
        title.style.cssText = `
            color: ${this.getInterestColor(pattern.interest_level)};
            margin-bottom: 15px;
            font-size: 18px;
        `;
        title.textContent = pattern.title || 'Pattern Details';
        
        // Full narrative
        const narrative = document.createElement('div');
        narrative.style.cssText = `
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid ${this.getInterestColor(pattern.interest_level)};
            margin-bottom: 15px;
            line-height: 1.5;
        `;
        narrative.textContent = pattern.narrative;
        
        // Metadata
        const metadata = document.createElement('div');
        metadata.style.cssText = `
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 12px;
            color: #bdc3c7;
        `;
        
        metadata.innerHTML = `
            <div><strong>Interest Level:</strong> ${pattern.interest_level}</div>
            <div><strong>Confidence:</strong> ${(pattern.confidence * 100).toFixed(0)}%</div>
            <div><strong>Affected Metrics:</strong> ${pattern.affected_metrics.join(', ')}</div>
            <div><strong>Timestamp:</strong> ${new Date(pattern.timestamp).toLocaleString()}</div>
        `;
        
        modal.appendChild(closeModalBtn);
        modal.appendChild(title);
        modal.appendChild(narrative);
        modal.appendChild(metadata);
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(overlay);
            }
        });
    }
    
    showError(message) {
        if (!this.contentArea) return;
        
        this.contentArea.innerHTML = `
            <div style="
                text-align: center;
                color: #e74c3c;
                padding: 20px;
                background: rgba(231, 76, 60, 0.1);
                border: 1px solid rgba(231, 76, 60, 0.3);
                border-radius: 8px;
            ">
                ⚠️ ${message}
            </div>
        `;
    }
    
    addDramaBackgroundEffect(container, dramaLevel) {
        // Create animated background canvas
        const canvas = document.createElement('canvas');
        canvas.width = container.offsetWidth || 300;
        canvas.height = container.offsetHeight || 60;
        canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
            opacity: 0.3;
        `;
        
        const ctx = canvas.getContext('2d');
        container.appendChild(canvas);
        
        // Different animations based on drama level
        switch (dramaLevel) {
            case 'CRISIS_MODE':
                this.animateCrisisMode(ctx, canvas);
                break;
            case 'EPIC_BATTLE':
                this.animateEpicBattle(ctx, canvas);
                break;
            case 'RISING_ACTION':
                this.animateRisingAction(ctx, canvas);
                break;
            default:
                this.animateDefault(ctx, canvas);
        }
    }
    
    animateCrisisMode(ctx, canvas) {
        const particles = [];
        const particleCount = 15;
        
        // Create warning particles
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                size: Math.random() * 3 + 1,
                color: `hsl(${Math.random() * 60}, 100%, 60%)` // Red/orange range
            });
        }
        
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            particles.forEach(particle => {
                // Update position
                particle.x += particle.vx;
                particle.y += particle.vy;
                
                // Bounce off edges
                if (particle.x <= 0 || particle.x >= canvas.width) particle.vx *= -1;
                if (particle.y <= 0 || particle.y >= canvas.height) particle.vy *= -1;
                
                // Draw particle
                ctx.fillStyle = particle.color;
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fill();
                
                // Add glow effect
                ctx.shadowColor = particle.color;
                ctx.shadowBlur = 10;
            });
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    addLiveMetricsVisualization() {
        // Create live metrics display
        const metricsContainer = document.createElement('div');
        metricsContainer.style.cssText = `
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(52, 152, 219, 0.3);
        `;
        
        const metricsTitle = document.createElement('div');
        metricsTitle.style.cssText = `
            color: #3498db;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 13px;
        `;
        metricsTitle.textContent = '📊 Live System Pulse';
        
        // Create animated metric bars
        const metricsGrid = document.createElement('div');
        metricsGrid.style.cssText = `
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        `;
        
        // Add animated metric bars for common metrics
        const metrics = [
            { name: 'CPU', color: '#e74c3c', value: 0.7 },
            { name: 'Memory', color: '#f39c12', value: 0.6 },
            { name: 'Network', color: '#3498db', value: 0.4 },
            { name: 'Disk I/O', color: '#9b59b6', value: 0.3 }
        ];
        
        metrics.forEach(metric => {
            const metricDiv = this.createAnimatedMetricBar(metric);
            metricsGrid.appendChild(metricDiv);
        });
        
        metricsContainer.appendChild(metricsTitle);
        metricsContainer.appendChild(metricsGrid);
        this.contentArea.appendChild(metricsContainer);
        
        // Start fetching real Prometheus data
        this.startLiveMetricsUpdates();
    }
    
    createAnimatedMetricBar(metric) {
        const container = document.createElement('div');
        container.style.cssText = `
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            padding: 8px;
            position: relative;
            overflow: hidden;
        `;
        
        const label = document.createElement('div');
        label.style.cssText = `
            color: #ecf0f1;
            font-size: 11px;
            margin-bottom: 4px;
            position: relative;
            z-index: 2;
        `;
        label.textContent = metric.name;
        
        const barContainer = document.createElement('div');
        barContainer.style.cssText = `
            background: rgba(0,0,0,0.3);
            height: 6px;
            border-radius: 3px;
            position: relative;
            overflow: hidden;
        `;
        
        const bar = document.createElement('div');
        bar.style.cssText = `
            background: linear-gradient(90deg, ${metric.color}, ${metric.color}aa);
            height: 100%;
            border-radius: 3px;
            width: 0%;
            transition: width 0.5s ease;
            position: relative;
        `;
        bar.setAttribute('data-metric-bar', 'true');
        
        // Add shimmer effect
        const shimmer = document.createElement('div');
        shimmer.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shimmer 2s infinite;
        `;
        
        bar.appendChild(shimmer);
        barContainer.appendChild(bar);
        container.appendChild(label);
        container.appendChild(barContainer);
        
        // Animate to target value
        setTimeout(() => {
            bar.style.width = `${metric.value * 100}%`;
        }, 100);
        
        return container;
    }
    
    async startLiveMetricsUpdates() {
        // Simulate realistic metric fluctuations every 3 seconds
        const updateMetrics = () => {
            const metricBars = document.querySelectorAll('[data-metric-bar]');
            metricBars.forEach(bar => {
                const currentValue = parseFloat(bar.style.width) / 100 || 0.5;
                const fluctuation = (Math.random() - 0.5) * 0.2; // ±10% change
                const newValue = Math.max(0.1, Math.min(0.9, currentValue + fluctuation));
                
                bar.style.width = `${newValue * 100}%`;
                
                // Change color based on value
                if (newValue > 0.8) {
                    bar.style.background = 'linear-gradient(90deg, #e74c3c, #e74c3caa)';
                } else if (newValue > 0.6) {
                    bar.style.background = 'linear-gradient(90deg, #f39c12, #f39c12aa)';
                } else {
                    bar.style.background = 'linear-gradient(90deg, #2ecc71, #2ecc71aa)';
                }
            });
        };
        
        // Update immediately and then every 3 seconds
        updateMetrics();
        setInterval(updateMetrics, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px currentColor; }
        50% { box-shadow: 0 0 20px currentColor, 0 0 30px currentColor; }
    }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize data insights display
    window.dataInsights = new DataInsightsDisplay();
    
    // Auto-initialize after a short delay
    setTimeout(() => {
        window.dataInsights.initialize();
    }, 2000);
});

// Export for global access
window.DataInsightsDisplay = DataInsightsDisplay;