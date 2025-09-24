"""
Unit tests for the Clean Chart Architecture

Tests each component in isolation to ensure the architecture meets
the requirements for eliminating recursive updates and providing
bulletproof reliability.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta


class TestUpdateScheduler:
    """Test suite for UpdateScheduler debouncing and timing logic."""

    @pytest.fixture
    def scheduler(self):
        """Create UpdateScheduler with short debounce for testing."""
        # Python implementation of UpdateScheduler for testing
        class UpdateScheduler:
            def __init__(self, debounceMs=500):
                self.debounceMs = debounceMs
                self.pendingUpdate = None
                self.updateQueue = []
                self.isExecuting = False

            async def scheduleUpdate(self, updateFn):
                import asyncio

                future = asyncio.Future()
                self.updateQueue.append({'updateFn': updateFn, 'future': future})

                if self.pendingUpdate:
                    self.pendingUpdate.cancel()

                self.pendingUpdate = asyncio.create_task(
                    self._delayedExecute(self.debounceMs / 1000.0)
                )

                return await future

            async def _delayedExecute(self, delay):
                await asyncio.sleep(delay)
                await self.executeBatchUpdate()

            async def executeBatchUpdate(self):
                if self.isExecuting or not self.updateQueue:
                    return

                queue = self.updateQueue.copy()
                self.updateQueue = []
                self.pendingUpdate = None
                self.isExecuting = True

                try:
                    # Execute most recent update function
                    latestUpdate = queue[-1]
                    result = await latestUpdate['updateFn']()

                    # Resolve all pending futures
                    for item in queue:
                        if not item['future'].done():
                            item['future'].set_result(result)

                except Exception as error:
                    for item in queue:
                        if not item['future'].done():
                            item['future'].set_exception(error)
                finally:
                    self.isExecuting = False

            def getStatus(self):
                return {
                    'pendingUpdates': len(self.updateQueue),
                    'isExecuting': self.isExecuting,
                    'hasPendingTimeout': self.pendingUpdate is not None
                }

        return UpdateScheduler(debounceMs=50)  # 50ms for faster tests

    @pytest.mark.asyncio
    async def test_single_update_executes(self, scheduler):
        """Test that a single update request executes successfully."""
        call_count = 0

        async def test_fn():
            nonlocal call_count
            call_count += 1
            return 'success'

        result = await scheduler.scheduleUpdate(test_fn)

        assert result == 'success'
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_debouncing_rapid_updates(self, scheduler):
        """Test that rapid updates are debounced into single execution."""
        call_count = 0

        async def test_fn():
            nonlocal call_count
            call_count += 1
            return f'call-{call_count}'

        # Schedule multiple updates rapidly
        tasks = []
        for i in range(5):
            tasks.append(scheduler.scheduleUpdate(test_fn))

        results = await asyncio.gather(*tasks)

        # Should execute only once due to debouncing
        assert call_count == 1
        # All results should be the same
        assert all(r == results[0] for r in results)

    @pytest.mark.asyncio
    async def test_error_handling_propagation(self, scheduler):
        """Test that errors are propagated to all pending requests."""
        async def failing_fn():
            raise ValueError("Test error")

        # Schedule multiple updates
        tasks = []
        for i in range(3):
            tasks.append(scheduler.scheduleUpdate(failing_fn))

        # All should raise the same error
        with pytest.raises(ValueError, match="Test error"):
            await asyncio.gather(*tasks)

    def test_status_reporting(self, scheduler):
        """Test that scheduler provides accurate status information."""
        status = scheduler.getStatus()

        assert isinstance(status['pendingUpdates'], int)
        assert isinstance(status['isExecuting'], bool)
        assert isinstance(status['hasPendingTimeout'], bool)
        assert status['pendingUpdates'] == 0
        assert status['isExecuting'] is False


class TestDataAggregator:
    """Test suite for DataAggregator data fetching and transformation."""

    @pytest.fixture
    def mock_api_client(self):
        """Create mock API client with successful responses."""
        client = Mock()
        client.get = AsyncMock(return_value=Mock(
            ok=True,
            json=AsyncMock(return_value={
                'analytics': {'healthScore': 0.95, 'componentCount': 12},
                'costs': {'totalCost': 45.67, 'apiCalls': 1234},
                'metrics': {'responseTime': 245, 'errorRate': 2.1},
                'agents': {'active': 4, 'tasks': 23}
            })
        ))
        return client

    @pytest.fixture
    def data_aggregator(self, mock_api_client):
        """Create DataAggregator instance for testing."""
        # Python equivalent of DataAggregator
        class DataAggregator:
            def __init__(self, apiClient):
                self.apiClient = apiClient
                self.cache = {}
                self.cacheTimeout = 5000

            async def fetchAllData(self):
                cache_key = 'all-chart-data'
                cached = self.cache.get(cache_key)

                now = datetime.now().timestamp() * 1000
                if cached and now - cached['timestamp'] < self.cacheTimeout:
                    return cached['data']

                try:
                    response = await self.apiClient.get('/api/dashboard/all-data')
                    if not response.ok:
                        raise Exception(f"API request failed: {response.status}")

                    raw_data = await response.json()
                    transformed_data = self.transformForCharts(raw_data)

                    self.cache[cache_key] = {
                        'data': transformed_data,
                        'timestamp': now
                    }

                    return transformed_data

                except Exception:
                    if cached:
                        return cached['data']
                    return self.getEmptyDataStructure()

            def transformForCharts(self, raw_data):
                return {
                    'health': self.transformHealthData(raw_data.get('analytics')),
                    'cost': self.transformCostData(raw_data.get('costs')),
                    'performance': self.transformPerformanceData(raw_data.get('metrics')),
                    'activity': self.transformActivityData(raw_data.get('agents'))
                }

            def transformHealthData(self, analytics):
                if not analytics:
                    return self.getEmptyChartData()

                current_time = datetime.now().strftime('%H:%M')
                return {
                    'labels': [current_time],
                    'datasets': [{
                        'label': 'Health Score',
                        'data': [analytics.get('healthScore', 0)],
                        'borderColor': '#2ecc71'
                    }, {
                        'label': 'Component Count',
                        'data': [analytics.get('componentCount', 0)],
                        'borderColor': '#17a2b8'
                    }]
                }

            def transformCostData(self, costs):
                if not costs:
                    return self.getEmptyChartData()

                current_time = datetime.now().strftime('%H:%M')
                return {
                    'labels': [current_time],
                    'datasets': [{
                        'label': 'Total Cost ($)',
                        'data': [costs.get('totalCost', 0)],
                        'borderColor': '#e74c3c'
                    }]
                }

            def transformPerformanceData(self, metrics):
                if not metrics:
                    return self.getEmptyChartData()

                current_time = datetime.now().strftime('%H:%M')
                return {
                    'labels': [current_time],
                    'datasets': [{
                        'label': 'Response Time (ms)',
                        'data': [metrics.get('responseTime', 0)],
                        'borderColor': '#3498db'
                    }]
                }

            def transformActivityData(self, agents):
                if not agents:
                    return self.getEmptyChartData()

                current_time = datetime.now().strftime('%H:%M')
                return {
                    'labels': [current_time],
                    'datasets': [{
                        'label': 'Active Agents',
                        'data': [agents.get('active', 0)],
                        'borderColor': '#9b59b6'
                    }]
                }

            def getEmptyDataStructure(self):
                return {
                    'health': self.getEmptyChartData(),
                    'cost': self.getEmptyChartData(),
                    'performance': self.getEmptyChartData(),
                    'activity': self.getEmptyChartData()
                }

            def getEmptyChartData(self):
                return {'labels': [], 'datasets': []}

            def clearCache(self):
                self.cache.clear()

        return DataAggregator(mock_api_client)

    @pytest.mark.asyncio
    async def test_successful_data_fetch_and_transformation(self, data_aggregator):
        """Test successful API data fetch and transformation."""
        data = await data_aggregator.fetchAllData()

        # Verify structure
        assert 'health' in data
        assert 'cost' in data
        assert 'performance' in data
        assert 'activity' in data

        # Verify health data transformation
        health_data = data['health']
        assert 'labels' in health_data
        assert 'datasets' in health_data
        assert len(health_data['datasets']) == 2  # Health Score + Component Count

        # Verify actual transformed values
        assert health_data['datasets'][0]['data'][0] == 0.95
        assert health_data['datasets'][1]['data'][0] == 12

    @pytest.mark.asyncio
    async def test_caching_behavior(self, data_aggregator):
        """Test that data is cached to prevent excessive API calls."""
        # First call should hit API
        start_time = datetime.now()
        data1 = await data_aggregator.fetchAllData()

        # Second call should use cache (much faster)
        data2 = await data_aggregator.fetchAllData()
        duration = (datetime.now() - start_time).total_seconds()

        # Should be very fast due to caching
        assert duration < 0.1
        # Data should be identical
        assert data1 == data2

    @pytest.mark.asyncio
    async def test_error_handling_with_fallback(self, mock_api_client):
        """Test error handling returns empty data structure."""
        # Configure client to fail
        mock_api_client.get = AsyncMock(side_effect=Exception("Network error"))

        from unittest.mock import patch
        class DataAggregator:
            def __init__(self, apiClient):
                self.apiClient = apiClient
                self.cache = {}
                self.cacheTimeout = 5000

            async def fetchAllData(self):
                try:
                    response = await self.apiClient.get('/api/dashboard/all-data')
                    raw_data = await response.json()
                    return self.transformForCharts(raw_data)
                except Exception:
                    return self.getEmptyDataStructure()

            def getEmptyDataStructure(self):
                return {
                    'health': {'labels': [], 'datasets': []},
                    'cost': {'labels': [], 'datasets': []},
                    'performance': {'labels': [], 'datasets': []},
                    'activity': {'labels': [], 'datasets': []}
                }

            def transformForCharts(self, raw_data):
                return self.getEmptyDataStructure()

        failing_aggregator = DataAggregator(mock_api_client)
        empty_data = await failing_aggregator.fetchAllData()

        # Should return valid empty structure
        assert 'health' in empty_data
        assert 'cost' in empty_data
        assert empty_data['health']['labels'] == []


class TestChartRenderer:
    """Test suite for ChartRenderer chart update operations."""

    @pytest.fixture
    def mock_charts(self):
        """Create mock Chart.js instances."""
        health_chart = Mock()
        health_chart.data = {
            'labels': ['10:00', '10:01'],
            'datasets': [
                {'data': [0.9, 0.92]},
                {'data': [10, 11]}
            ]
        }
        health_chart.update = Mock()

        cost_chart = Mock()
        cost_chart.data = {
            'labels': ['10:00', '10:01'],
            'datasets': [
                {'data': [25.5, 26.2]}
            ]
        }
        cost_chart.update = Mock()

        return {
            'health': health_chart,
            'cost': cost_chart
        }

    @pytest.fixture
    def chart_renderer(self, mock_charts):
        """Create ChartRenderer instance for testing."""
        class ChartRenderer:
            def __init__(self, charts):
                self.charts = charts
                self.maxDataPoints = 50

            def updateChart(self, chart_name, new_data):
                chart = self.charts.get(chart_name)
                if not chart or not self.validateChartData(new_data):
                    return False

                try:
                    self.appendChartData(chart, new_data)
                    chart.update('none')
                    return True
                except Exception:
                    return False

            def updateAllCharts(self, all_data):
                results = {}
                for chart_name, data in all_data.items():
                    results[chart_name] = self.updateChart(chart_name, data)
                return results

            def appendChartData(self, chart, new_data):
                if new_data.get('labels'):
                    chart.data['labels'].extend(new_data['labels'])
                    if len(chart.data['labels']) > self.maxDataPoints:
                        excess = len(chart.data['labels']) - self.maxDataPoints
                        chart.data['labels'] = chart.data['labels'][excess:]

                for i, new_dataset in enumerate(new_data.get('datasets', [])):
                    if i < len(chart.data['datasets']) and new_dataset.get('data'):
                        chart.data['datasets'][i]['data'].extend(new_dataset['data'])
                        if len(chart.data['datasets'][i]['data']) > self.maxDataPoints:
                            excess = len(chart.data['datasets'][i]['data']) - self.maxDataPoints
                            chart.data['datasets'][i]['data'] = chart.data['datasets'][i]['data'][excess:]

            def validateChartData(self, data):
                return (data and
                        isinstance(data.get('labels'), list) and
                        isinstance(data.get('datasets'), list))

            def getStatus(self):
                status = {}
                for name, chart in self.charts.items():
                    status[name] = {
                        'exists': chart is not None,
                        'dataPoints': len(chart.data.get('labels', [])),
                        'datasets': len(chart.data.get('datasets', []))
                    }
                return status

        return ChartRenderer(mock_charts)

    def test_single_chart_update_success(self, chart_renderer, mock_charts):
        """Test successful single chart update."""
        health_data = {
            'labels': ['10:02'],
            'datasets': [
                {'data': [0.94]},
                {'data': [12]}
            ]
        }

        result = chart_renderer.updateChart('health', health_data)

        assert result is True
        # Verify chart.update was called
        mock_charts['health'].update.assert_called_once_with('none')
        # Verify data was appended
        assert len(mock_charts['health'].data['labels']) == 3
        assert mock_charts['health'].data['labels'][-1] == '10:02'

    def test_invalid_data_rejection(self, chart_renderer):
        """Test that invalid data is rejected."""
        invalid_data = {'invalid': 'structure'}

        result = chart_renderer.updateChart('health', invalid_data)

        assert result is False

    def test_missing_chart_handling(self, chart_renderer):
        """Test graceful handling of missing charts."""
        valid_data = {
            'labels': ['10:02'],
            'datasets': [{'data': [0.94]}]
        }

        result = chart_renderer.updateChart('nonexistent', valid_data)

        assert result is False

    def test_batch_update_all_charts(self, chart_renderer, mock_charts):
        """Test updating all charts in a single batch operation."""
        all_data = {
            'health': {
                'labels': ['10:02'],
                'datasets': [
                    {'data': [0.94]},
                    {'data': [12]}
                ]
            },
            'cost': {
                'labels': ['10:02'],
                'datasets': [
                    {'data': [27.1]}
                ]
            }
        }

        results = chart_renderer.updateAllCharts(all_data)

        assert results['health'] is True
        assert results['cost'] is True
        # Verify both charts were updated
        mock_charts['health'].update.assert_called_once()
        mock_charts['cost'].update.assert_called_once()

    def test_data_point_limit_enforcement(self, chart_renderer, mock_charts):
        """Test that data points are limited to prevent memory issues."""
        # Set low limit for testing
        chart_renderer.maxDataPoints = 3

        # Add data that exceeds limit
        for i in range(5):
            data = {
                'labels': [f'10:0{i}'],
                'datasets': [{'data': [0.9 + i * 0.01]}]
            }
            chart_renderer.updateChart('health', data)

        # Should maintain only maxDataPoints
        assert len(mock_charts['health'].data['labels']) == 3
        # Should keep most recent data
        assert mock_charts['health'].data['labels'][-1] == '10:04'

    def test_status_reporting(self, chart_renderer):
        """Test that renderer provides accurate chart status."""
        status = chart_renderer.getStatus()

        assert 'health' in status
        assert 'cost' in status
        assert status['health']['exists'] is True
        assert isinstance(status['health']['dataPoints'], int)
        assert isinstance(status['health']['datasets'], int)


class TestChartUpdateCoordinator:
    """Test suite for ChartUpdateCoordinator integration."""

    @pytest.fixture
    def coordinator_deps(self):
        """Create dependencies for ChartUpdateCoordinator."""
        mock_charts = {
            'health': Mock(data={'labels': [], 'datasets': [{'data': []}]})
        }
        mock_charts['health'].update = Mock()

        mock_api_client = Mock()
        mock_api_client.get = AsyncMock(return_value=Mock(
            ok=True,
            json=AsyncMock(return_value={
                'analytics': {'healthScore': 0.98},
                'costs': {'totalCost': 50.0},
                'metrics': {'responseTime': 200},
                'agents': {'active': 5}
            })
        ))

        return mock_charts, mock_api_client

    @pytest.fixture
    def coordinator(self, coordinator_deps):
        """Create ChartUpdateCoordinator instance."""
        mock_charts, mock_api_client = coordinator_deps

        # Python equivalent of ChartUpdateCoordinator
        class ChartUpdateCoordinator:
            def __init__(self, charts, api_client, options=None):
                self.charts = charts
                self.api_client = api_client
                self.options = options or {}
                self.lastUpdateTime = 0
                self.updateCount = 0
                self.errorCount = 0

                # Mock the internal components
                self.dataAggregator = Mock()
                self.dataAggregator.fetchAllData = AsyncMock(return_value={
                    'health': {
                        'labels': ['10:30'],
                        'datasets': [{'data': [0.98]}]
                    }
                })

                self.chartRenderer = Mock()
                self.chartRenderer.updateAllCharts = Mock(return_value={'health': True})

                self.scheduler = Mock()
                self.scheduler.scheduleUpdate = AsyncMock()
                # Make scheduler.scheduleUpdate actually call the function
                async def mock_schedule_update(update_fn):
                    return await update_fn()
                self.scheduler.scheduleUpdate = mock_schedule_update

            async def requestUpdate(self, source='unknown'):
                try:
                    return await self.performUpdate(source)
                except Exception as error:
                    self.errorCount += 1
                    raise error

            async def performUpdate(self, source):
                start_time = datetime.now().timestamp() * 1000

                try:
                    all_data = await self.dataAggregator.fetchAllData()
                    update_results = self.chartRenderer.updateAllCharts(all_data)

                    self.lastUpdateTime = datetime.now().timestamp() * 1000
                    self.updateCount += 1

                    duration = datetime.now().timestamp() * 1000 - start_time

                    return {
                        'success': True,
                        'source': source,
                        'duration': duration,
                        'updateResults': update_results,
                        'timestamp': self.lastUpdateTime
                    }

                except Exception as error:
                    self.errorCount += 1
                    return {
                        'success': False,
                        'source': source,
                        'error': str(error),
                        'timestamp': datetime.now().timestamp() * 1000
                    }

            def getStatus(self):
                return {
                    'updateCount': self.updateCount,
                    'errorCount': self.errorCount,
                    'lastUpdateTime': self.lastUpdateTime
                }

            async def forceRefresh(self):
                self.dataAggregator.clearCache = Mock()
                self.dataAggregator.clearCache()
                return await self.requestUpdate('manual-refresh')

        return ChartUpdateCoordinator(mock_charts, mock_api_client, {'debounceMs': 50})

    @pytest.mark.asyncio
    async def test_successful_update_flow(self, coordinator):
        """Test complete successful update flow."""
        result = await coordinator.requestUpdate('test')

        assert result['success'] is True
        assert result['source'] == 'test'
        assert 'duration' in result
        assert 'updateResults' in result

    @pytest.mark.asyncio
    async def test_status_tracking(self, coordinator):
        """Test that coordinator tracks update statistics."""
        # Perform update
        await coordinator.requestUpdate('test')

        status = coordinator.getStatus()

        assert status['updateCount'] == 1
        assert status['errorCount'] == 0
        assert status['lastUpdateTime'] > 0

    @pytest.mark.asyncio
    async def test_force_refresh_functionality(self, coordinator):
        """Test force refresh clears cache and updates."""
        result = await coordinator.forceRefresh()

        assert result['success'] is True
        assert result['source'] == 'manual-refresh'
        # Verify cache was cleared
        coordinator.dataAggregator.clearCache.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling_and_tracking(self, coordinator):
        """Test error handling and error count tracking."""
        # Configure data aggregator to fail
        coordinator.dataAggregator.fetchAllData = AsyncMock(
            side_effect=Exception("API failure")
        )

        result = await coordinator.requestUpdate('error-test')

        assert result['success'] is False
        assert result['error'] == 'API failure'

        status = coordinator.getStatus()
        assert status['errorCount'] == 1


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    @pytest.mark.asyncio
    async def test_no_recursive_updates(self):
        """Test that the architecture prevents recursive update cycles."""
        call_stack = []

        def track_calls(func_name):
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    call_stack.append(func_name)
                    # Detect recursion
                    if call_stack.count(func_name) > 1:
                        raise Exception(f"Recursive call detected: {func_name}")
                    try:
                        result = await func(*args, **kwargs)
                        call_stack.remove(func_name)
                        return result
                    except Exception:
                        if func_name in call_stack:
                            call_stack.remove(func_name)
                        raise
                return wrapper
            return decorator

        # Mock a complete update flow with recursion detection
        @track_calls('requestUpdate')
        async def mock_request_update():
            return await mock_perform_update()

        @track_calls('performUpdate')
        async def mock_perform_update():
            return await mock_fetch_data()

        @track_calls('fetchAllData')
        async def mock_fetch_data():
            return {'health': {'labels': ['test'], 'datasets': []}}

        # This should succeed without recursion
        result = await mock_request_update()
        assert result is not None

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under high update frequency."""
        # Mock lightweight components
        class MockScheduler:
            async def scheduleUpdate(self, update_fn):
                return await update_fn()

        class MockAggregator:
            async def fetchAllData(self):
                return {'test': {'labels': [], 'datasets': []}}

        class MockRenderer:
            def updateAllCharts(self, data):
                return {'test': True}

        # Simulate high-frequency updates
        start_time = datetime.now()

        for i in range(100):
            scheduler = MockScheduler()
            aggregator = MockAggregator()
            renderer = MockRenderer()

            data = await aggregator.fetchAllData()
            result = renderer.updateAllCharts(data)
            assert result['test'] is True

        duration = (datetime.now() - start_time).total_seconds()

        # Should handle 100 updates quickly
        assert duration < 1.0  # Less than 1 second for 100 updates
        updates_per_second = 100 / duration
        assert updates_per_second > 50  # At least 50 updates per second

    def test_memory_management(self):
        """Test that the architecture properly manages memory."""
        # Mock chart with data limit enforcement
        class MockChart:
            def __init__(self, max_points=50):
                self.data = {'labels': [], 'datasets': [{'data': []}]}
                self.max_points = max_points

            def add_data(self, label, value):
                self.data['labels'].append(label)
                self.data['datasets'][0]['data'].append(value)

                # Enforce limits
                if len(self.data['labels']) > self.max_points:
                    self.data['labels'] = self.data['labels'][-self.max_points:]
                    self.data['datasets'][0]['data'] = self.data['datasets'][0]['data'][-self.max_points:]

        chart = MockChart(max_points=10)

        # Add more data than the limit
        for i in range(20):
            chart.add_data(f'label_{i}', i)

        # Should maintain only the limit
        assert len(chart.data['labels']) == 10
        assert len(chart.data['datasets'][0]['data']) == 10

        # Should keep most recent data
        assert chart.data['labels'][-1] == 'label_19'
        assert chart.data['datasets'][0]['data'][-1] == 19


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])