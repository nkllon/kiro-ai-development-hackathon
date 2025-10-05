# Design Document

## Overview

Replace the current recursive, over-engineered chart update system with a clean, predictable architecture based on the Single Responsibility Principle and clear data flow patterns. The new system will use a centralized update coordinator with debounced triggers and synchronous chart operations.

## Architecture

### Core Components

1. **ChartUpdateCoordinator** - Single point of control for all chart updates
2. **DataAggregator** - Consolidates data from multiple sources into chart-ready format
3. **UpdateScheduler** - Manages timing and debouncing of update requests
4. **ChartRenderer** - Handles the actual Chart.js operations synchronously

### Data Flow

```
Triggers (WebSocket, Timer, Manual) 
    ↓
UpdateScheduler (debounce)
    ↓
ChartUpdateCoordinator
    ↓
DataAggregator (single API call)
    ↓
ChartRenderer (synchronous updates)
```

## Components and Interfaces

### ChartUpdateCoordinator

```javascript
class ChartUpdateCoordinator {
    constructor(charts, dataAggregator, scheduler) {
        this.charts = charts;
        this.dataAggregator = dataAggregator;
        this.scheduler = scheduler;
        this.lastUpdateTime = 0;
    }
    
    // Single method for all updates
    async requestUpdate(source = 'unknown') {
        return this.scheduler.scheduleUpdate(() => this.performUpdate(source));
    }
    
    // Private - only called by scheduler
    async performUpdate(source) {
        const data = await this.dataAggregator.fetchAllData();
        this.updateAllCharts(data);
    }
    
    // Synchronous chart updates - no async complexity
    updateAllCharts(data) {
        Object.entries(this.charts).forEach(([name, chart]) => {
            this.updateSingleChart(chart, data[name]);
        });
    }
}
```

### DataAggregator

```javascript
class DataAggregator {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.cache = new Map();
        this.cacheTimeout = 5000; // 5 second cache
    }
    
    // Single API call for all chart data
    async fetchAllData() {
        const cacheKey = 'all-chart-data';
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        
        // One API call, not three separate ones
        const response = await this.apiClient.get('/api/dashboard/all-data');
        const data = this.transformForCharts(response.data);
        
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
        return data;
    }
    
    // Transform API response into chart-ready format
    transformForCharts(rawData) {
        return {
            health: this.transformHealthData(rawData.analytics),
            cost: this.transformCostData(rawData.costs),
            performance: this.transformPerformanceData(rawData.metrics),
            activity: this.transformActivityData(rawData.agents)
        };
    }
}
```

### UpdateScheduler

```javascript
class UpdateScheduler {
    constructor(debounceMs = 500) {
        this.debounceMs = debounceMs;
        this.pendingUpdate = null;
        this.updateQueue = [];
    }
    
    // Debounce multiple rapid update requests
    scheduleUpdate(updateFn) {
        return new Promise((resolve, reject) => {
            this.updateQueue.push({ updateFn, resolve, reject });
            
            if (this.pendingUpdate) {
                clearTimeout(this.pendingUpdate);
            }
            
            this.pendingUpdate = setTimeout(() => {
                this.executeBatchUpdate();
            }, this.debounceMs);
        });
    }
    
    async executeBatchUpdate() {
        const queue = [...this.updateQueue];
        this.updateQueue = [];
        this.pendingUpdate = null;
        
        try {
            // Execute the most recent update function
            const result = await queue[queue.length - 1].updateFn();
            
            // Resolve all pending promises with the same result
            queue.forEach(({ resolve }) => resolve(result));
        } catch (error) {
            queue.forEach(({ reject }) => reject(error));
        }
    }
}
```

## Data Models

### Consolidated API Response

```javascript
{
    analytics: {
        healthScore: 0.95,
        componentCount: 12,
        timestamp: "2024-01-15T10:30:00Z"
    },
    costs: {
        totalCost: 45.67,
        apiCalls: 1234,
        providers: { openai: 30.45, anthropic: 15.22 }
    },
    metrics: {
        responseTime: 245,
        errorRate: 2.1,
        throughput: 156
    },
    agents: {
        active: 4,
        tasks: 23,
        coordination: 0.87
    }
}
```

### Chart Data Format

```javascript
{
    health: {
        labels: ["10:25", "10:26", "10:27", "10:28", "10:29", "10:30"],
        datasets: [{
            label: "Health Score",
            data: [0.92, 0.94, 0.93, 0.95, 0.94, 0.95]
        }]
    },
    // ... other chart data
}
```

## Error Handling

### Graceful Degradation Strategy

1. **API Failures**: Use cached data, display staleness indicator
2. **Chart Rendering Errors**: Skip failed chart, continue with others
3. **Network Issues**: Exponential backoff with max 3 retries
4. **Data Corruption**: Validate data structure, use defaults for missing fields

### Error Recovery

```javascript
class ErrorHandler {
    static async withFallback(operation, fallback) {
        try {
            return await operation();
        } catch (error) {
            console.warn('Operation failed, using fallback:', error.message);
            return fallback();
        }
    }
    
    static validateChartData(data) {
        // Ensure data structure is valid for Chart.js
        return data && data.labels && Array.isArray(data.datasets);
    }
}
```

## Testing Strategy

### Unit Tests

- **ChartUpdateCoordinator**: Mock data aggregator and scheduler
- **DataAggregator**: Mock API responses, test data transformation
- **UpdateScheduler**: Test debouncing behavior with fake timers
- **ChartRenderer**: Mock Chart.js instances, verify update calls

### Integration Tests

- **End-to-End Update Flow**: Trigger update, verify all charts receive data
- **Error Scenarios**: API failures, malformed data, network timeouts
- **Performance**: Measure update latency, memory usage during rapid updates

### Key Learnings for Agent Framework

This mess happened because:

1. **No architectural constraints** - Agent built complex async patterns without design review
2. **Feature creep during implementation** - Started simple, grew into monster
3. **No separation of concerns** - Mixed data fetching, transformation, and rendering
4. **Defensive programming anti-patterns** - Added mutexes instead of fixing root cause
5. **No testing strategy** - Complex code with no way to verify correctness

**Agent Framework Requirements Update Needed:**
- Agents MUST work within predefined architectural patterns
- Complex async operations REQUIRE design review before implementation
- Agents MUST separate data, business logic, and presentation layers
- Error handling MUST be designed upfront, not added defensively
- All non-trivial code MUST include unit tests