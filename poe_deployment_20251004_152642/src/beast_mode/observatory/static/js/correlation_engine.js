/**
 * Observatory Correlation Engine
 * Links events, metrics, and traces to tell the complete system story
 * Part of the Living Observatory Dashboard - "Ace Reporter" correlation system
 */

class CorrelationEngine {
    constructor() {
        this.correlations = new Map(); // correlation_id -> correlation data
        this.eventHistory = []; // Recent events for correlation analysis
        this.metricHistory = []; // Recent metrics for correlation analysis
        this.correlationRules = new Map(); // event_type -> correlation rules
        this.maxHistorySize = 100;
        this.correlationWindow = 30000; // 30 seconds correlation window
        this.confidenceThreshold = 0.7; // Minimum confidence for correlation
        
        // Initialize correlation rules
        this.initializeCorrelationRules();
        
        console.log('🔗 CorrelationEngine initialized - Ready to connect the dots!');
    }
    
    /**
     * Initialize correlation rules for different event types
     */
    initializeCorrelationRules() {
        // WebSocket connection events
        this.correlationRules.set('websocket_connect', {
            expectedMetricChanges: ['connected_clients'],
            timeWindow: 5000, // 5 seconds
            confidence: 0.9,
            description: 'WebSocket connections should increase client count'
        });
        
        this.correlationRules.set('websocket_disconnect', {
            expectedMetricChanges: ['connected_clients'],
            timeWindow: 5000,
            confidence: 0.9,
            description: 'WebSocket disconnections should decrease client count'
        });
        
        // Performance events
        this.correlationRules.set('performance', {
            expectedMetricChanges: ['response_time', 'throughput', 'error_rate'],
            timeWindow: 10000, // 10 seconds
            confidence: 0.8,
            description: 'Performance events should correlate with response metrics'
        });
        
        // Certificate operations
        this.correlationRules.set('certificate_lock', {
            expectedMetricChanges: ['response_time'],
            timeWindow: 15000, // 15 seconds
            confidence: 0.7,
            description: 'Certificate operations may impact response time'
        });
        
        // Cache operations
        this.correlationRules.set('cache_invalidate', {
            expectedMetricChanges: ['response_time', 'database_queries'],
            timeWindow: 20000, // 20 seconds
            confidence: 0.8,
            description: 'Cache invalidation should increase response time and database queries'
        });
        
        // Database operations
        this.correlationRules.set('database_query', {
            expectedMetricChanges: ['response_time', 'database_connections'],
            timeWindow: 5000,
            confidence: 0.8,
            description: 'Database queries should correlate with response time'
        });
    }
    
    /**
     * Add an event to the correlation analysis
     */
    addEvent(event) {
        // Add to event history
        this.eventHistory.unshift({
            ...event,
            timestamp: new Date(event.timestamp).getTime(),
            processed: false
        });
        
        // Trim history
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.pop();
        }
        
        // Process correlations for this event
        this.processEventCorrelations(event);
        
        console.log('🔗 Event added to correlation analysis:', event.message);
    }
    
    /**
     * Add metrics data to the correlation analysis
     */
    addMetrics(metrics) {
        const timestamp = Date.now();
        
        // Add to metric history
        this.metricHistory.unshift({
            ...metrics,
            timestamp: timestamp
        });
        
        // Trim history
        if (this.metricHistory.length > this.maxHistorySize) {
            this.metricHistory.pop();
        }
        
        // Process correlations with recent events
        this.processMetricCorrelations(metrics, timestamp);
    }
    
    /**
     * Process correlations for a new event
     */
    processEventCorrelations(event) {
        const eventTime = new Date(event.timestamp).getTime();
        const correlationRule = this.correlationRules.get(event.event_type);
        
        if (!correlationRule) {
            return; // No correlation rules for this event type
        }
        
        // Look for metric changes within the time window
        const relevantMetrics = this.metricHistory.filter(metric => {
            const timeDiff = Math.abs(metric.timestamp - eventTime);
            return timeDiff <= correlationRule.timeWindow;
        });
        
        if (relevantMetrics.length < 2) {
            return; // Need at least 2 metric points for comparison
        }
        
        // Analyze metric changes
        const correlations = this.analyzeMetricChanges(
            event, 
            relevantMetrics, 
            correlationRule
        );
        
        if (correlations.length > 0) {
            this.createCorrelation(event, correlations, correlationRule);
        }
    }
    
    /**
     * Process correlations for new metrics
     */
    processMetricCorrelations(metrics, timestamp) {
        // Look for recent unprocessed events
        const recentEvents = this.eventHistory.filter(event => {
            const timeDiff = Math.abs(timestamp - event.timestamp);
            return timeDiff <= this.correlationWindow && !event.processed;
        });
        
        recentEvents.forEach(event => {
            const correlationRule = this.correlationRules.get(event.event_type);
            if (correlationRule) {
                const relevantMetrics = this.metricHistory.slice(0, 5); // Last 5 metric points
                const correlations = this.analyzeMetricChanges(event, relevantMetrics, correlationRule);
                
                if (correlations.length > 0) {
                    this.createCorrelation(event, correlations, correlationRule);
                    event.processed = true;
                }
            }
        });
    }
    
    /**
     * Analyze metric changes around an event
     */
    analyzeMetricChanges(event, metrics, rule) {
        if (metrics.length < 2) return [];
        
        const correlations = [];
        const eventTime = new Date(event.timestamp).getTime();
        
        // Sort metrics by timestamp
        metrics.sort((a, b) => a.timestamp - b.timestamp);
        
        // Find metrics before and after the event
        const beforeMetrics = metrics.filter(m => m.timestamp < eventTime);
        const afterMetrics = metrics.filter(m => m.timestamp >= eventTime);
        
        if (beforeMetrics.length === 0 || afterMetrics.length === 0) {
            return [];
        }
        
        const beforeMetric = beforeMetrics[beforeMetrics.length - 1]; // Closest before
        const afterMetric = afterMetrics[0]; // Closest after
        
        // Analyze each expected metric change
        rule.expectedMetricChanges.forEach(metricName => {
            const beforeValue = this.getMetricValue(beforeMetric, metricName);
            const afterValue = this.getMetricValue(afterMetric, metricName);
            
            if (beforeValue !== null && afterValue !== null) {
                const change = afterValue - beforeValue;
                const percentChange = beforeValue !== 0 ? (change / beforeValue) * 100 : 0;
                
                // Determine if this is a significant change
                const significance = this.calculateSignificance(change, percentChange, metricName);
                
                if (significance.isSignificant) {
                    correlations.push({
                        metricName: metricName,
                        beforeValue: beforeValue,
                        afterValue: afterValue,
                        change: change,
                        percentChange: percentChange,
                        significance: significance,
                        confidence: this.calculateConfidence(significance, rule)
                    });
                }
            }
        });
        
        return correlations;
    }
    
    /**
     * Get metric value by name from metrics object
     */
    getMetricValue(metrics, metricName) {
        // Handle nested metric paths
        const path = metricName.split('.');
        let value = metrics;
        
        for (const key of path) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return null;
            }
        }
        
        return typeof value === 'number' ? value : null;
    }
    
    /**
     * Calculate significance of a metric change
     */
    calculateSignificance(change, percentChange, metricName) {
        const absChange = Math.abs(change);
        const absPercentChange = Math.abs(percentChange);
        
        // Define significance thresholds by metric type
        const thresholds = {
            'response_time': { absolute: 50, percent: 10 }, // 50ms or 10%
            'error_rate': { absolute: 1, percent: 5 }, // 1% or 5%
            'throughput': { absolute: 10, percent: 15 }, // 10 ops/sec or 15%
            'connected_clients': { absolute: 1, percent: 0 }, // Any change
            'database_queries': { absolute: 5, percent: 20 }, // 5 queries or 20%
            'database_connections': { absolute: 1, percent: 0 }, // Any change
            'default': { absolute: 1, percent: 5 } // Default thresholds
        };
        
        const threshold = thresholds[metricName] || thresholds.default;
        
        const isSignificant = absChange >= threshold.absolute || absPercentChange >= threshold.percent;
        
        return {
            isSignificant: isSignificant,
            magnitude: absPercentChange > 50 ? 'high' : absPercentChange > 20 ? 'medium' : 'low',
            direction: change > 0 ? 'increase' : 'decrease'
        };
    }
    
    /**
     * Calculate confidence score for a correlation
     */
    calculateConfidence(significance, rule) {
        let confidence = rule.confidence;
        
        // Adjust confidence based on significance magnitude
        if (significance.magnitude === 'high') {
            confidence = Math.min(1.0, confidence + 0.1);
        } else if (significance.magnitude === 'low') {
            confidence = Math.max(0.1, confidence - 0.1);
        }
        
        return confidence;
    }
    
    /**
     * Create a correlation record
     */
    createCorrelation(event, correlations, rule) {
        const correlationId = `corr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const correlation = {
            id: correlationId,
            event: event,
            correlations: correlations,
            rule: rule,
            timestamp: Date.now(),
            confidence: this.calculateOverallConfidence(correlations),
            story: this.generateCorrelationStory(event, correlations, rule)
        };
        
        // Only store high-confidence correlations
        if (correlation.confidence >= this.confidenceThreshold) {
            this.correlations.set(correlationId, correlation);
            this.notifyCorrelationFound(correlation);
            
            console.log('🎯 High-confidence correlation found:', correlation.story);
        }
    }
    
    /**
     * Calculate overall confidence from individual correlations
     */
    calculateOverallConfidence(correlations) {
        if (correlations.length === 0) return 0;
        
        const avgConfidence = correlations.reduce((sum, corr) => sum + corr.confidence, 0) / correlations.length;
        const significantCount = correlations.filter(corr => corr.significance.magnitude !== 'low').length;
        const significanceBonus = (significantCount / correlations.length) * 0.2;
        
        return Math.min(1.0, avgConfidence + significanceBonus);
    }
    
    /**
     * Generate a human-readable story for the correlation
     */
    generateCorrelationStory(event, correlations, rule) {
        const eventDescription = event.message || `${event.event_type} event`;
        const correlationDescriptions = correlations.map(corr => {
            const direction = corr.significance.direction;
            const magnitude = corr.significance.magnitude;
            const metricName = corr.metricName.replace(/_/g, ' ');
            const percentChange = Math.abs(corr.percentChange).toFixed(1);
            
            return `${metricName} ${direction}d by ${percentChange}% (${magnitude} impact)`;
        });
        
        if (correlationDescriptions.length === 1) {
            return `📊 "${eventDescription}" caused ${correlationDescriptions[0]}`;
        } else {
            const lastCorr = correlationDescriptions.pop();
            return `📊 "${eventDescription}" caused ${correlationDescriptions.join(', ')} and ${lastCorr}`;
        }
    }
    
    /**
     * Notify other components about a correlation
     */
    notifyCorrelationFound(correlation) {
        // Dispatch custom event for other components to listen to
        const event = new CustomEvent('correlationFound', {
            detail: correlation
        });
        document.dispatchEvent(event);
        
        // Update activity feed with correlation info
        if (window.activityFeedRenderer) {
            this.addCorrelationToActivityFeed(correlation);
        }
    }
    
    /**
     * Add correlation information to the activity feed
     */
    addCorrelationToActivityFeed(correlation) {
        const correlationEvent = {
            timestamp: new Date(correlation.timestamp).toISOString(),
            module: 'CorrelationEngine',
            event_type: 'correlation_found',
            message: correlation.story,
            emoji: '🎯',
            severity: 'info',
            context: {
                correlation_id: correlation.id,
                confidence: (correlation.confidence * 100).toFixed(1) + '%',
                original_event: correlation.event.message
            }
        };
        
        window.activityFeedRenderer.addEvent(correlationEvent);
    }
    
    /**
     * Get correlations for a specific event
     */
    getCorrelationsForEvent(eventId) {
        const correlations = [];
        for (const [id, correlation] of this.correlations) {
            if (correlation.event.correlation_id === eventId || 
                correlation.event.event_id === eventId) {
                correlations.push(correlation);
            }
        }
        return correlations;
    }
    
    /**
     * Get recent high-confidence correlations
     */
    getRecentCorrelations(limit = 10) {
        const recent = Array.from(this.correlations.values())
            .sort((a, b) => b.timestamp - a.timestamp)
            .slice(0, limit);
        
        return recent;
    }
    
    /**
     * Get correlation statistics
     */
    getStats() {
        const totalCorrelations = this.correlations.size;
        const highConfidence = Array.from(this.correlations.values())
            .filter(corr => corr.confidence >= 0.9).length;
        const mediumConfidence = Array.from(this.correlations.values())
            .filter(corr => corr.confidence >= 0.7 && corr.confidence < 0.9).length;
        
        return {
            totalCorrelations: totalCorrelations,
            highConfidence: highConfidence,
            mediumConfidence: mediumConfidence,
            eventHistory: this.eventHistory.length,
            metricHistory: this.metricHistory.length,
            correlationRules: this.correlationRules.size
        };
    }
    
    /**
     * Clear old correlations and history
     */
    cleanup() {
        const cutoffTime = Date.now() - (24 * 60 * 60 * 1000); // 24 hours ago
        
        // Remove old correlations
        for (const [id, correlation] of this.correlations) {
            if (correlation.timestamp < cutoffTime) {
                this.correlations.delete(id);
            }
        }
        
        // Trim event history
        this.eventHistory = this.eventHistory.filter(event => 
            event.timestamp > cutoffTime
        );
        
        // Trim metric history
        this.metricHistory = this.metricHistory.filter(metric => 
            metric.timestamp > cutoffTime
        );
        
        console.log('🧹 CorrelationEngine cleanup completed');
    }
}

// Global instance for integration with other components
let correlationEngine = null;

function initializeCorrelationEngine() {
    if (!correlationEngine) {
        correlationEngine = new CorrelationEngine();
        
        // Start periodic cleanup
        setInterval(() => {
            correlationEngine.cleanup();
        }, 60 * 60 * 1000); // Every hour
        
        // Add to global scope for debugging and integration
        window.correlationEngine = correlationEngine;
        window.getCorrelationStats = () => correlationEngine.getStats();
        
        console.log('🔗 CorrelationEngine ready for connecting the dots!');
    }
}

// Auto-initialize when DOM is ready
console.log('🔗 CorrelationEngine script loaded!');
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCorrelationEngine);
} else {
    initializeCorrelationEngine();
}