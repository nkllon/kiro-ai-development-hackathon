/**
 * Clean Chart Update Architecture for Beast Mode Observatory
 *
 * Replaces the over-engineered, recursive ObservatoryCharts system with
 * a clean, predictable architecture following Single Responsibility Principle.
 *
 * Architecture: Trigger -> UpdateScheduler -> ChartUpdateCoordinator -> DataAggregator -> ChartRenderer
 */

/**
 * UpdateScheduler: Manages timing and debouncing of update requests
 * Single responsibility: Prevent rapid-fire updates and coordinate timing
 */
class UpdateScheduler {
    constructor(debounceMs = 500) {
        this.debounceMs = debounceMs;
        this.pendingUpdate = null;
        this.updateQueue = [];
        this.isExecuting = false;
    }

    /**
     * Schedule an update with debouncing
     * Multiple rapid calls will be collapsed into a single update
     */
    scheduleUpdate(updateFn) {
        return new Promise((resolve, reject) => {
            this.updateQueue.push({ updateFn, resolve, reject });

            // Clear any pending update and reschedule
            if (this.pendingUpdate) {
                clearTimeout(this.pendingUpdate);
            }

            this.pendingUpdate = setTimeout(() => {
                this.executeBatchUpdate();
            }, this.debounceMs);
        });
    }

    /**
     * Execute the most recent update function for all queued requests
     * Private method - only called by timeout
     */
    async executeBatchUpdate() {
        if (this.isExecuting) {
            return; // Prevent recursive execution
        }

        const queue = [...this.updateQueue];
        this.updateQueue = [];
        this.pendingUpdate = null;
        this.isExecuting = true;

        try {
            // Execute only the most recent update function (debouncing)
            const latestUpdate = queue[queue.length - 1];
            if (latestUpdate) {
                const result = await latestUpdate.updateFn();

                // Resolve all pending promises with the same result
                queue.forEach(({ resolve }) => resolve(result));
            }
        } catch (error) {
            console.error('UpdateScheduler: Batch update failed:', error);
            queue.forEach(({ reject }) => reject(error));
        } finally {
            this.isExecuting = false;
        }
    }

    /**
     * Get scheduler status for debugging
     */
    getStatus() {
        return {
            pendingUpdates: this.updateQueue.length,
            isExecuting: this.isExecuting,
            hasPendingTimeout: this.pendingUpdate !== null
        };
    }
}

/**
 * DataAggregator: Consolidates data from multiple sources into chart-ready format
 * Single responsibility: Fetch and transform data for all charts in one operation
 */
class DataAggregator {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.cache = new Map();
        this.cacheTimeout = 5000; // 5 second cache to prevent excessive API calls
    }

    /**
     * Single API call for all chart data
     * Returns consolidated data for all charts
     */
    async fetchAllData() {
        const cacheKey = 'all-chart-data';
        const cached = this.cache.get(cacheKey);

        // Use cached data if still fresh
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }

        try {
            // Single API call instead of multiple separate calls
            const response = await this.apiClient.get('/api/dashboard/all-data');

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status}`);
            }

            const rawData = await response.json();
            const transformedData = this.transformForCharts(rawData);

            // Cache the transformed data
            this.cache.set(cacheKey, {
                data: transformedData,
                timestamp: Date.now()
            });

            return transformedData;

        } catch (error) {
            console.error('DataAggregator: Failed to fetch data:', error);

            // Return cached data if available, otherwise return empty data structure
            if (cached) {
                console.warn('DataAggregator: Using stale cached data due to API failure');
                return cached.data;
            }

            return this.getEmptyDataStructure();
        }
    }

    /**
     * Transform API response into chart-ready format
     * Single transformation point for all chart data
     */
    transformForCharts(rawData) {
        return {
            health: this.transformHealthData(rawData.analytics),
            cost: this.transformCostData(rawData.costs),
            performance: this.transformPerformanceData(rawData.metrics),
            activity: this.transformActivityData(rawData.agents)
        };
    }

    /**
     * Transform health analytics data for chart consumption
     */
    transformHealthData(analytics) {
        if (!analytics) return this.getEmptyChartData();

        const currentTime = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        return {
            labels: [currentTime],
            datasets: [{
                label: 'Health Score',
                data: [analytics.healthScore || 0],
                borderColor: '#2ecc71',
                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }, {
                label: 'Component Count',
                data: [analytics.componentCount || 0],
                borderColor: '#17a2b8',
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
            }]
        };
    }

    /**
     * Transform cost data for chart consumption
     */
    transformCostData(costs) {
        if (!costs) return this.getEmptyChartData();

        const currentTime = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        return {
            labels: [currentTime],
            datasets: [{
                label: 'Total Cost ($)',
                data: [costs.totalCost || 0],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.2)',
                borderWidth: 2,
                fill: true
            }, {
                label: 'API Calls',
                data: [costs.apiCalls || 0],
                borderColor: '#f39c12',
                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
            }]
        };
    }

    /**
     * Transform performance metrics for chart consumption
     */
    transformPerformanceData(metrics) {
        if (!metrics) return this.getEmptyChartData();

        const currentTime = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        return {
            labels: [currentTime],
            datasets: [{
                label: 'Response Time (ms)',
                data: [metrics.responseTime || 0],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                fill: true
            }, {
                label: 'Error Rate (%)',
                data: [metrics.errorRate || 0],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
            }]
        };
    }

    /**
     * Transform agent activity data for chart consumption
     */
    transformActivityData(agents) {
        if (!agents) return this.getEmptyChartData();

        const currentTime = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        return {
            labels: [currentTime],
            datasets: [{
                label: 'Active Agents',
                data: [agents.active || 0],
                borderColor: '#9b59b6',
                backgroundColor: 'rgba(155, 89, 182, 0.2)',
                borderWidth: 2,
                fill: true
            }, {
                label: 'Tasks',
                data: [agents.tasks || 0],
                borderColor: '#1abc9c',
                backgroundColor: 'rgba(26, 188, 156, 0.1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
            }]
        };
    }

    /**
     * Get empty data structure for error cases
     */
    getEmptyDataStructure() {
        return {
            health: this.getEmptyChartData(),
            cost: this.getEmptyChartData(),
            performance: this.getEmptyChartData(),
            activity: this.getEmptyChartData()
        };
    }

    /**
     * Get empty chart data structure
     */
    getEmptyChartData() {
        return {
            labels: [],
            datasets: []
        };
    }

    /**
     * Clear cache (useful for testing or manual refresh)
     */
    clearCache() {
        this.cache.clear();
    }
}

/**
 * ChartRenderer: Handles the actual Chart.js operations synchronously
 * Single responsibility: Update Chart.js instances with new data
 */
class ChartRenderer {
    constructor(charts) {
        this.charts = charts; // Chart.js instances keyed by chart name
        this.maxDataPoints = 50; // Keep last 50 data points for performance
    }

    /**
     * Update a single chart with new data
     * Synchronous operation - no async complexity
     */
    updateChart(chartName, newData) {
        const chart = this.charts[chartName];

        if (!chart) {
            console.warn(`ChartRenderer: Chart '${chartName}' not found`);
            return false;
        }

        if (!this.validateChartData(newData)) {
            console.warn(`ChartRenderer: Invalid data for chart '${chartName}'`);
            return false;
        }

        try {
            // Update chart data - append new data points and trim old ones
            this.appendChartData(chart, newData);

            // Trigger chart update
            chart.update('none'); // No animation for performance

            return true;
        } catch (error) {
            console.error(`ChartRenderer: Failed to update chart '${chartName}':`, error);
            return false;
        }
    }

    /**
     * Update all charts with data from DataAggregator
     * Synchronous batch operation
     */
    updateAllCharts(allData) {
        const results = {};

        Object.entries(allData).forEach(([chartName, data]) => {
            results[chartName] = this.updateChart(chartName, data);
        });

        const successCount = Object.values(results).filter(Boolean).length;
        const totalCount = Object.keys(results).length;

        console.log(`ChartRenderer: Updated ${successCount}/${totalCount} charts successfully`);

        return results;
    }

    /**
     * Append new data to chart while maintaining data point limit
     */
    appendChartData(chart, newData) {
        // Add new labels
        if (newData.labels && newData.labels.length > 0) {
            chart.data.labels.push(...newData.labels);

            // Trim old labels if exceeding max data points
            if (chart.data.labels.length > this.maxDataPoints) {
                const excess = chart.data.labels.length - this.maxDataPoints;
                chart.data.labels.splice(0, excess);
            }
        }

        // Add new data to each dataset
        newData.datasets.forEach((newDataset, index) => {
            if (chart.data.datasets[index] && newDataset.data) {
                chart.data.datasets[index].data.push(...newDataset.data);

                // Trim old data points if exceeding max
                if (chart.data.datasets[index].data.length > this.maxDataPoints) {
                    const excess = chart.data.datasets[index].data.length - this.maxDataPoints;
                    chart.data.datasets[index].data.splice(0, excess);
                }
            }
        });
    }

    /**
     * Validate chart data structure
     */
    validateChartData(data) {
        return data &&
               data.labels &&
               Array.isArray(data.labels) &&
               data.datasets &&
               Array.isArray(data.datasets);
    }

    /**
     * Get renderer status for debugging
     */
    getStatus() {
        const chartStatus = {};

        Object.entries(this.charts).forEach(([name, chart]) => {
            chartStatus[name] = {
                exists: !!chart,
                dataPoints: chart?.data?.labels?.length || 0,
                datasets: chart?.data?.datasets?.length || 0
            };
        });

        return chartStatus;
    }
}

/**
 * ChartUpdateCoordinator: Single point of control for all chart updates
 * Single responsibility: Orchestrate the complete update flow
 */
class ChartUpdateCoordinator {
    constructor(charts, apiClient, options = {}) {
        // Core dependencies
        this.charts = charts;
        this.dataAggregator = new DataAggregator(apiClient);
        this.chartRenderer = new ChartRenderer(charts);
        this.scheduler = new UpdateScheduler(options.debounceMs || 500);

        // State tracking
        this.lastUpdateTime = 0;
        this.updateCount = 0;
        this.errorCount = 0;

        console.log('ChartUpdateCoordinator: Initialized with clean architecture');
    }

    /**
     * Single method for all chart updates
     * This is the ONLY public method that should be called to update charts
     */
    async requestUpdate(source = 'unknown') {
        console.log(`ChartUpdateCoordinator: Update requested from ${source}`);

        try {
            return await this.scheduler.scheduleUpdate(() => this.performUpdate(source));
        } catch (error) {
            console.error('ChartUpdateCoordinator: Update request failed:', error);
            this.errorCount++;
            throw error;
        }
    }

    /**
     * Private method - only called by scheduler
     * Performs the actual update operation
     */
    async performUpdate(source) {
        const startTime = Date.now();

        try {
            console.log(`ChartUpdateCoordinator: Performing update (source: ${source})`);

            // Step 1: Fetch all data in single operation
            const allData = await this.dataAggregator.fetchAllData();

            // Step 2: Update all charts synchronously
            const updateResults = this.chartRenderer.updateAllCharts(allData);

            // Step 3: Update tracking
            this.lastUpdateTime = Date.now();
            this.updateCount++;

            const duration = Date.now() - startTime;
            console.log(`ChartUpdateCoordinator: Update completed in ${duration}ms`);

            return {
                success: true,
                source,
                duration,
                updateResults,
                timestamp: this.lastUpdateTime
            };

        } catch (error) {
            console.error('ChartUpdateCoordinator: Update failed:', error);
            this.errorCount++;

            return {
                success: false,
                source,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    /**
     * Get coordinator status for debugging and monitoring
     */
    getStatus() {
        return {
            updateCount: this.updateCount,
            errorCount: this.errorCount,
            lastUpdateTime: this.lastUpdateTime,
            scheduler: this.scheduler.getStatus(),
            chartRenderer: this.chartRenderer.getStatus()
        };
    }

    /**
     * Manual data refresh (clears cache and forces update)
     */
    async forceRefresh() {
        console.log('ChartUpdateCoordinator: Force refresh requested');
        this.dataAggregator.clearCache();
        return await this.requestUpdate('manual-refresh');
    }
}

/**
 * ErrorHandler: Centralized error handling utilities
 * Single responsibility: Provide consistent error handling patterns
 */
class ErrorHandler {
    /**
     * Execute operation with fallback on failure
     */
    static async withFallback(operation, fallback) {
        try {
            return await operation();
        } catch (error) {
            console.warn('ErrorHandler: Operation failed, using fallback:', error.message);
            return await fallback();
        }
    }

    /**
     * Validate chart data structure
     */
    static validateChartData(data) {
        return data &&
               data.labels &&
               Array.isArray(data.labels) &&
               data.datasets &&
               Array.isArray(data.datasets);
    }

    /**
     * Create safe API client with error handling
     */
    static createSafeApiClient(baseUrl = '') {
        return {
            async get(url) {
                try {
                    const response = await fetch(baseUrl + url, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    return response;
                } catch (error) {
                    console.error(`ErrorHandler: API request to ${url} failed:`, error);
                    throw error;
                }
            }
        };
    }
}

// Export classes for use in the dashboard
window.ChartArchitecture = {
    ChartUpdateCoordinator,
    DataAggregator,
    UpdateScheduler,
    ChartRenderer,
    ErrorHandler
};

console.log('📊 Clean Chart Architecture loaded successfully');