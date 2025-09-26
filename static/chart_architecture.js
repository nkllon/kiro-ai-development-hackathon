// Chart Architecture Configuration for Beast Mode Observatory
console.log('Chart Architecture loaded');

// Dashboard configuration
const DASHBOARD_CONFIG = {
    refreshInterval: 5000,
    maxDataPoints: 100,
    theme: 'dark'
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing dashboard charts...');
    initializeCharts();
});

function initializeCharts() {
    // Health status chart
    createHealthChart();
    // Metrics charts
    createMetricsCharts();
    // Real-time updates
    startRealTimeUpdates();
}

console.log('Chart architecture script loaded successfully');
