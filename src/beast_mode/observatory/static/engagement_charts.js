/**
 * Engagement Charts JavaScript
 * 
 * Provides interactive charts and visualizations for the Live Dashboard Engagement System.
 * Integrates with existing Observatory charts and adds engagement-specific visualizations.
 */

class EngagementCharts {
    constructor() {
        this.charts = {};
        this.engagementData = {
            attentionSessions: [],
            interactions: [],
            personalityChanges: [],
            animationEvents: [],
            healthScores: []
        };
        
        this.init();
    }
    
    init() {
        this.setupEngagementCharts();
        this.startDataCollection();
        this.setupChartInteractions();
    }
    
    setupEngagementCharts() {
        // Add engagement charts to the existing charts grid
        this.addEngagementChartsToGrid();
        
        // Initialize individual charts
        this.initAttentionChart();
        this.initInteractionChart();
        this.initPersonalityChart();
        this.initEngagementHealthChart();
    }
    
    addEngagementChartsToGrid() {
        // Find the charts grid
        const chartsGrid = document.querySelector('.charts-grid');
        if (!chartsGrid) return;
        
        // Create engagement charts section
        const engagementSection = document.createElement('div');
        engagementSection.innerHTML = `
            <div style="grid-column: 1 / -1; margin: 30px 0 20px 0;">
                <h3 style="color: #9b59b6; text-align: center; margin-bottom: 20px;">
                    🎯 Live Engagement Analytics
                </h3>
            </div>
        `;
        
        // Insert engagement section before existing charts
        chartsGrid.insertBefore(engagementSection, chartsGrid.firstChild);
        
        // Add engagement charts
        const engagementCharts = [
            {
                id: 'attentionChart',
                title: '👁️ Attention Tracking',
                description: 'Real-time user attention and focus patterns'
            },
            {
                id: 'interactionChart',
                title: '🖱️ Interaction Patterns',
                description: 'User interaction frequency and types'
            },
            {
                id: 'personalityChart',
                title: '🎭 Personality Transitions',
                description: 'Dashboard personality mood changes over time'
            },
            {
                id: 'engagementHealthChart',
                title: '💚 Engagement Health',
                description: 'Overall engagement system health score'
            }
        ];
        
        engagementCharts.forEach(chart => {
            const chartContainer = this.createChartContainer(chart);
            chartsGrid.appendChild(chartContainer);
        });
    }
    
    createChartContainer(chartConfig) {
        const container = document.createElement('div');
        container.className = 'chart-container engagement-chart';
        container.innerHTML = `
            <h4>
                <span>${chartConfig.title}</span>
                <button class="chart-export-btn" onclick="engagementCharts.exportChart('${chartConfig.id}')">
                    📷 Export
                </button>
            </h4>
            <div class="chart-wrapper">
                <canvas id="${chartConfig.id}"></canvas>
                <div class="chart-loading">Loading engagement data...</div>
            </div>
            <div class="chart-description" style="
                font-size: 0.8em;
                color: #95a5a6;
                margin-top: 8px;
                text-align: center;
            ">
                ${chartConfig.description}
            </div>
        `;
        
        return container;
    }
    
    initAttentionChart() {
        const ctx = document.getElementById('attentionChart');
        if (!ctx) return;
        
        this.charts.attention = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Active Sessions',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Focus Events',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ecf0f1' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' }
                    },
                    y: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    initInteractionChart() {
        const ctx = document.getElementById('interactionChart');
        if (!ctx) return;
        
        this.charts.interaction = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Clicks', 'Hovers', 'Scrolls', 'Keyboard', 'Focus'],
                datasets: [{
                    label: 'Interactions',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(46, 204, 113, 0.8)',
                        'rgba(155, 89, 182, 0.8)',
                        'rgba(243, 156, 18, 0.8)'
                    ],
                    borderColor: [
                        '#e74c3c',
                        '#3498db',
                        '#2ecc71',
                        '#9b59b6',
                        '#f39c12'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' }
                    },
                    y: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 500,
                    easing: 'easeOutBounce'
                }
            }
        });
    }
    
    initPersonalityChart() {
        const ctx = document.getElementById('personalityChart');
        if (!ctx) return;
        
        this.charts.personality = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Calm', 'Focused', 'Celebratory', 'Energetic'],
                datasets: [{
                    data: [25, 25, 25, 25],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(243, 156, 18, 0.8)',
                        'rgba(46, 204, 113, 0.8)'
                    ],
                    borderColor: [
                        '#3498db',
                        '#e74c3c',
                        '#f39c12',
                        '#2ecc71'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { 
                            color: '#ecf0f1',
                            padding: 15
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1000
                }
            }
        });
    }
    
    initEngagementHealthChart() {
        const ctx = document.getElementById('engagementHealthChart');
        if (!ctx) return;
        
        this.charts.health = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Health Score',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#2ecc71',
                    pointBorderColor: '#27ae60',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ecf0f1' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' }
                    },
                    y: {
                        ticks: { color: '#ecf0f1' },
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        min: 0,
                        max: 10,
                        stepSize: 1
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutCubic'
                }
            }
        });
    }
    
    startDataCollection() {
        // Update charts every 5 seconds
        setInterval(() => {
            this.updateChartsWithLiveData();
        }, 5000);
        
        // Listen for engagement events
        if (window.engagementControls) {
            this.connectToEngagementEvents();
        }
    }
    
    connectToEngagementEvents() {
        // Listen for engagement data updates
        document.addEventListener('engagementDataUpdate', (event) => {
            this.handleEngagementDataUpdate(event.detail);
        });
    }
    
    updateChartsWithLiveData() {
        // Simulate live data updates (in production, this would come from WebSocket)
        this.updateAttentionChart();
        this.updateInteractionChart();
        this.updatePersonalityChart();
        this.updateHealthChart();
    }
    
    updateAttentionChart() {
        if (!this.charts.attention) return;
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString();
        
        // Add new data point
        this.charts.attention.data.labels.push(timeLabel);
        
        // Simulate attention data
        const activeSessions = Math.floor(Math.random() * 5) + 1;
        const focusEvents = Math.floor(Math.random() * 10) + 1;
        
        this.charts.attention.data.datasets[0].data.push(activeSessions);
        this.charts.attention.data.datasets[1].data.push(focusEvents);
        
        // Keep only last 20 data points
        if (this.charts.attention.data.labels.length > 20) {
            this.charts.attention.data.labels.shift();
            this.charts.attention.data.datasets[0].data.shift();
            this.charts.attention.data.datasets[1].data.shift();
        }
        
        this.charts.attention.update('none');
    }
    
    updateInteractionChart() {
        if (!this.charts.interaction) return;
        
        // Get interaction data from engagement controls
        const interactions = window.engagementControls ? 
            window.engagementControls.metrics.interactions : 0;
        
        // Simulate interaction type distribution
        const total = Math.max(interactions, 1);
        this.charts.interaction.data.datasets[0].data = [
            Math.floor(total * 0.4), // Clicks
            Math.floor(total * 0.3), // Hovers
            Math.floor(total * 0.15), // Scrolls
            Math.floor(total * 0.1), // Keyboard
            Math.floor(total * 0.05)  // Focus
        ];
        
        this.charts.interaction.update('none');
    }
    
    updatePersonalityChart() {
        if (!this.charts.personality) return;
        
        // Simulate personality distribution changes
        const moods = ['calm', 'focused', 'celebratory', 'energetic'];
        const currentMood = document.body.className.match(/personality-(\w+)/);
        
        if (currentMood) {
            const moodIndex = moods.indexOf(currentMood[1]);
            if (moodIndex !== -1) {
                // Emphasize current mood
                const data = [20, 20, 20, 20];
                data[moodIndex] = 40;
                this.charts.personality.data.datasets[0].data = data;
                this.charts.personality.update('none');
            }
        }
    }
    
    updateHealthChart() {
        if (!this.charts.health) return;
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString();
        
        // Calculate health score
        const healthScore = window.engagementControls ? 
            window.engagementControls.calculateEngagementScore() : 
            Math.random() * 10;
        
        // Add new data point
        this.charts.health.data.labels.push(timeLabel);
        this.charts.health.data.datasets[0].data.push(healthScore);
        
        // Keep only last 20 data points
        if (this.charts.health.data.labels.length > 20) {
            this.charts.health.data.labels.shift();
            this.charts.health.data.datasets[0].data.shift();
        }
        
        this.charts.health.update('none');
    }
    
    setupChartInteractions() {
        // Add click handlers for engagement charts
        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart && chart.canvas) {
                chart.canvas.addEventListener('click', (event) => {
                    this.handleChartClick(chartKey, event);
                });
            }
        });
    }
    
    handleChartClick(chartKey, event) {
        // Record chart interaction
        if (window.engagementControls) {
            window.engagementControls.recordInteraction('click', `chart_${chartKey}`, 100);
            window.engagementControls.triggerEngagementAnimation('chart_interaction', event.target);
        }
        
        // Show chart details
        this.showChartDetails(chartKey);
    }
    
    showChartDetails(chartKey) {
        const chart = this.charts[chartKey];
        if (!chart) return;
        
        // Create details popup
        const popup = document.createElement('div');
        popup.className = 'chart-details-popup';
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(52, 73, 94, 0.95);
            border: 2px solid rgba(52, 152, 219, 0.5);
            border-radius: 12px;
            padding: 20px;
            z-index: 2000;
            backdrop-filter: blur(15px);
            color: #ecf0f1;
            max-width: 400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        `;
        
        const chartTitles = {
            attention: 'Attention Tracking Details',
            interaction: 'Interaction Patterns Details',
            personality: 'Personality Transitions Details',
            health: 'Engagement Health Details'
        };
        
        popup.innerHTML = `
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #3498db;">${chartTitles[chartKey] || 'Chart Details'}</h3>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: #95a5a6;
                    cursor: pointer;
                    font-size: 18px;
                ">✕</button>
            </div>
            <div id="chartDetailsContent">
                ${this.getChartDetailsContent(chartKey)}
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Remove popup after 10 seconds
        setTimeout(() => {
            if (popup.parentElement) {
                popup.remove();
            }
        }, 10000);
    }
    
    getChartDetailsContent(chartKey) {
        const chart = this.charts[chartKey];
        if (!chart) return 'No data available';
        
        switch (chartKey) {
            case 'attention':
                return `
                    <p><strong>Active Sessions:</strong> ${chart.data.datasets[0].data.slice(-1)[0] || 0}</p>
                    <p><strong>Recent Focus Events:</strong> ${chart.data.datasets[1].data.slice(-1)[0] || 0}</p>
                    <p><strong>Average Session Length:</strong> ${this.calculateAverageSessionLength()}</p>
                `;
            case 'interaction':
                const totalInteractions = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                return `
                    <p><strong>Total Interactions:</strong> ${totalInteractions}</p>
                    <p><strong>Most Common:</strong> ${this.getMostCommonInteraction(chart)}</p>
                    <p><strong>Interaction Rate:</strong> ${this.calculateInteractionRate()}/min</p>
                `;
            case 'personality':
                return `
                    <p><strong>Current Mood:</strong> ${this.getCurrentPersonalityMood()}</p>
                    <p><strong>Mood Changes:</strong> ${this.getMoodChangeCount()}</p>
                    <p><strong>Dominant Mood:</strong> ${this.getDominantMood(chart)}</p>
                `;
            case 'health':
                const currentHealth = chart.data.datasets[0].data.slice(-1)[0] || 0;
                return `
                    <p><strong>Current Score:</strong> ${currentHealth.toFixed(1)}/10</p>
                    <p><strong>Trend:</strong> ${this.getHealthTrend(chart)}</p>
                    <p><strong>Status:</strong> ${this.getHealthStatus(currentHealth)}</p>
                `;
            default:
                return 'Chart details not available';
        }
    }
    
    calculateAverageSessionLength() {
        if (window.engagementControls) {
            const duration = window.engagementControls.metrics.sessionDuration;
            return window.engagementControls.formatDuration(duration);
        }
        return '0:00';
    }
    
    getMostCommonInteraction(chart) {
        const data = chart.data.datasets[0].data;
        const labels = chart.data.labels;
        const maxIndex = data.indexOf(Math.max(...data));
        return labels[maxIndex] || 'None';
    }
    
    calculateInteractionRate() {
        if (window.engagementControls) {
            const sessionMinutes = window.engagementControls.metrics.sessionDuration / (1000 * 60);
            const interactions = window.engagementControls.metrics.interactions;
            return sessionMinutes > 0 ? (interactions / sessionMinutes).toFixed(1) : '0.0';
        }
        return '0.0';
    }
    
    getCurrentPersonalityMood() {
        const currentMood = document.body.className.match(/personality-(\w+)/);
        return currentMood ? currentMood[1].charAt(0).toUpperCase() + currentMood[1].slice(1) : 'Neutral';
    }
    
    getMoodChangeCount() {
        // This would be tracked in a real implementation
        return Math.floor(Math.random() * 5);
    }
    
    getDominantMood(chart) {
        const data = chart.data.datasets[0].data;
        const labels = chart.data.labels;
        const maxIndex = data.indexOf(Math.max(...data));
        return labels[maxIndex] || 'Calm';
    }
    
    getHealthTrend(chart) {
        const data = chart.data.datasets[0].data;
        if (data.length < 2) return 'Stable';
        
        const recent = data.slice(-3);
        const trend = recent[recent.length - 1] - recent[0];
        
        if (trend > 0.5) return '📈 Improving';
        if (trend < -0.5) return '📉 Declining';
        return '➡️ Stable';
    }
    
    getHealthStatus(score) {
        if (score >= 8) return '🟢 Excellent';
        if (score >= 6) return '🟡 Good';
        if (score >= 4) return '🟠 Fair';
        return '🔴 Needs Attention';
    }
    
    exportChart(chartId) {
        const chart = this.charts[chartId.replace('Chart', '')];
        if (!chart) return;
        
        // Create download link
        const link = document.createElement('a');
        link.download = `engagement-${chartId}-${new Date().toISOString().slice(0, 10)}.png`;
        link.href = chart.toBase64Image();
        link.click();
        
        // Record export interaction
        if (window.engagementControls) {
            window.engagementControls.recordInteraction('export', `chart_${chartId}`, 500);
        }
    }
    
    handleEngagementDataUpdate(data) {
        // Handle real-time data updates from WebSocket
        if (data.type === 'metrics_update') {
            this.updateChartsWithRealData(data.metrics);
        }
    }
    
    updateChartsWithRealData(metrics) {
        // Update charts with real engagement metrics
        if (metrics.attention && this.charts.attention) {
            // Update attention chart with real data
        }
        
        if (metrics.interactions && this.charts.interaction) {
            // Update interaction chart with real data
        }
        
        // Continue for other chart types...
    }
}

// Initialize engagement charts when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait for Chart.js to be available
        if (typeof Chart !== 'undefined') {
            window.engagementCharts = new EngagementCharts();
        } else {
            // Wait for Chart.js to load
            const checkChart = setInterval(() => {
                if (typeof Chart !== 'undefined') {
                    clearInterval(checkChart);
                    window.engagementCharts = new EngagementCharts();
                }
            }, 100);
        }
    });
} else {
    if (typeof Chart !== 'undefined') {
        window.engagementCharts = new EngagementCharts();
    }
}