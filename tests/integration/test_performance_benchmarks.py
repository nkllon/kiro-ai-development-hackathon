"""
Performance Benchmark Tests

Validates that the refactored implementation doesn't introduce performance regressions.
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import patch, AsyncMock, Mock

from src.beast_mode.messaging.unified_client import BeastModeClient
from src.beast_mode.messaging.daemon_client import BeastModeClient as DaemonClient
from src.beast_mode.messaging.models import BeastModeMessage, MessageType


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.fixture
    def mock_fast_transport(self):
        """Mock transport optimized for speed testing"""
        transport = AsyncMock()
        transport.initialize.return_value = True
        transport.start_daemon.return_value = True
        transport.stop_daemon.return_value = None
        transport.send_message.return_value = True
        transport.subscribe.return_value = True
        transport.get_status.return_value = {'connected': True}
        transport.get_capabilities.return_value = {'reliable_delivery': True}
        return transport
    
    @pytest.fixture
    def mock_fast_shared_state(self):
        """Mock shared state optimized for speed testing"""
        shared_state = AsyncMock()
        shared_state.initialize.return_value = True
        shared_state.update_agent_state.return_value = True
        shared_state.remove_agent_state.return_value = True
        shared_state.increment_counter.return_value = 1
        shared_state.shutdown.return_value = None
        return shared_state
    
    @pytest.mark.asyncio
    async def test_client_startup_performance(self, mock_fast_transport, mock_fast_shared_state):
        """Test client startup time performance"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                # Benchmark startup time
                startup_times = []
                
                for i in range(10):
                    client = BeastModeClient(f'perf_test_{i}')
                    
                    start_time = time.time()
                    await client.start()
                    startup_time = time.time() - start_time
                    startup_times.append(startup_time)
                    
                    await client.stop()
                
                # Calculate statistics
                avg_startup = statistics.mean(startup_times)
                max_startup = max(startup_times)
                
                print(f"\n📊 Startup Performance:")
                print(f"   Average: {avg_startup:.3f}s")
                print(f"   Maximum: {max_startup:.3f}s")
                
                # Performance assertions (with mocks, should be very fast)
                assert avg_startup < 0.1, f"Average startup too slow: {avg_startup:.3f}s"
                assert max_startup < 0.2, f"Maximum startup too slow: {max_startup:.3f}s"
    
    @pytest.mark.asyncio
    async def test_message_sending_performance(self, mock_fast_transport, mock_fast_shared_state):
        """Test message sending performance"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                client = BeastModeClient('perf_sender')
                await client.start()
                
                try:
                    # Create test message
                    message = BeastModeMessage(
                        type=MessageType.SIMPLE_MESSAGE,
                        source='perf_sender',
                        payload={'text': 'performance test message'}
                    )
                    
                    # Benchmark message sending
                    message_counts = [10, 50, 100]
                    
                    for count in message_counts:
                        start_time = time.time()
                        
                        for _ in range(count):
                            await client.send_message(message)
                        
                        total_time = time.time() - start_time
                        messages_per_second = count / total_time if total_time > 0 else float('inf')
                        
                        print(f"\n📊 Message Sending Performance ({count} messages):")
                        print(f"   Total time: {total_time:.3f}s")
                        print(f"   Messages/sec: {messages_per_second:.1f}")
                        
                        # Performance assertions
                        assert messages_per_second > 100, f"Message sending too slow: {messages_per_second:.1f} msg/s"
                
                finally:
                    await client.stop()
    
    @pytest.mark.asyncio
    async def test_message_handling_performance(self, mock_fast_transport, mock_fast_shared_state):
        """Test message handling performance"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                client = BeastModeClient('perf_handler')
                await client.start()
                
                try:
                    # Set up handler
                    handled_messages = []
                    
                    def fast_handler(message):
                        handled_messages.append(message)
                    
                    client.register_handler(MessageType.SIMPLE_MESSAGE, fast_handler)
                    
                    # Create test messages
                    test_messages = [
                        BeastModeMessage(
                            type=MessageType.SIMPLE_MESSAGE,
                            source='test_sender',
                            payload={'text': f'message {i}'}
                        )
                        for i in range(100)
                    ]
                    
                    # Benchmark message handling
                    start_time = time.time()
                    
                    for message in test_messages:
                        await client._handle_message(message)
                    
                    total_time = time.time() - start_time
                    messages_per_second = len(test_messages) / total_time if total_time > 0 else float('inf')
                    
                    print(f"\n📊 Message Handling Performance:")
                    print(f"   Messages handled: {len(handled_messages)}")
                    print(f"   Total time: {total_time:.3f}s")
                    print(f"   Messages/sec: {messages_per_second:.1f}")
                    
                    # Performance assertions
                    assert len(handled_messages) == len(test_messages)
                    assert messages_per_second > 500, f"Message handling too slow: {messages_per_second:.1f} msg/s"
                
                finally:
                    await client.stop()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, mock_fast_transport, mock_fast_shared_state):
        """Test performance under concurrent operations"""
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                # Create multiple clients
                clients = []
                for i in range(5):
                    client = BeastModeClient(f'concurrent_{i}')
                    await client.start()
                    clients.append(client)
                
                try:
                    # Concurrent message sending
                    async def send_messages(client, count):
                        for i in range(count):
                            message = BeastModeMessage(
                                type=MessageType.SIMPLE_MESSAGE,
                                source=client.agent_id,
                                payload={'text': f'concurrent message {i}'}
                            )
                            await client.send_message(message)
                    
                    # Benchmark concurrent operations
                    start_time = time.time()
                    
                    tasks = [send_messages(client, 20) for client in clients]
                    await asyncio.gather(*tasks)
                    
                    total_time = time.time() - start_time
                    total_messages = len(clients) * 20
                    messages_per_second = total_messages / total_time if total_time > 0 else float('inf')
                    
                    print(f"\n📊 Concurrent Operations Performance:")
                    print(f"   Clients: {len(clients)}")
                    print(f"   Total messages: {total_messages}")
                    print(f"   Total time: {total_time:.3f}s")
                    print(f"   Messages/sec: {messages_per_second:.1f}")
                    
                    # Performance assertions
                    assert messages_per_second > 50, f"Concurrent operations too slow: {messages_per_second:.1f} msg/s"
                
                finally:
                    for client in clients:
                        await client.stop()
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, mock_fast_transport, mock_fast_shared_state):
        """Test that memory usage remains stable during operations"""
        import gc
        import sys
        
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                client = BeastModeClient('memory_test')
                await client.start()
                
                try:
                    # Get initial memory usage
                    gc.collect()
                    initial_objects = len(gc.get_objects())
                    
                    # Perform many operations
                    for i in range(1000):
                        message = BeastModeMessage(
                            type=MessageType.SIMPLE_MESSAGE,
                            source='memory_test',
                            payload={'text': f'memory test {i}'}
                        )
                        await client.send_message(message)
                        
                        # Simulate message handling
                        await client._handle_message(message)
                    
                    # Check memory usage after operations
                    gc.collect()
                    final_objects = len(gc.get_objects())
                    
                    object_growth = final_objects - initial_objects
                    growth_percentage = (object_growth / initial_objects) * 100
                    
                    print(f"\n📊 Memory Usage:")
                    print(f"   Initial objects: {initial_objects}")
                    print(f"   Final objects: {final_objects}")
                    print(f"   Growth: {object_growth} objects ({growth_percentage:.1f}%)")
                    
                    # Memory assertions (should not grow excessively)
                    assert growth_percentage < 50, f"Memory growth too high: {growth_percentage:.1f}%"
                
                finally:
                    await client.stop()
    
    def test_daemon_client_performance_baseline(self):
        """Test daemon client performance as baseline"""
        with patch('src.beast_mode.messaging.daemon_client.BeastModeDaemon') as mock_daemon_class:
            mock_daemon = Mock()
            mock_daemon.start_daemon.return_value = True
            mock_daemon.send_message.return_value = None
            mock_daemon.check_mail.return_value = []
            mock_daemon.get_status.return_value = {'is_running': True}
            mock_daemon_class.return_value = mock_daemon
            
            # Benchmark daemon client operations
            client = DaemonClient('baseline_test')
            
            # Startup time
            start_time = time.time()
            client.start()
            startup_time = time.time() - start_time
            
            # Message sending
            message = BeastModeMessage(
                type=MessageType.SIMPLE_MESSAGE,
                source='baseline_test',
                payload={'text': 'baseline test'}
            )
            
            start_time = time.time()
            for _ in range(100):
                client.send_message(message)
            send_time = time.time() - start_time
            
            messages_per_second = 100 / send_time if send_time > 0 else float('inf')
            
            print(f"\n📊 Daemon Client Baseline:")
            print(f"   Startup time: {startup_time:.3f}s")
            print(f"   Send rate: {messages_per_second:.1f} msg/s")
            
            client.stop()
            
            # Store baseline for comparison
            return {
                'startup_time': startup_time,
                'send_rate': messages_per_second
            }
    
    @pytest.mark.asyncio
    async def test_performance_comparison(self, mock_fast_transport, mock_fast_shared_state):
        """Compare unified client performance to daemon client baseline"""
        # Get baseline performance
        baseline = self.test_daemon_client_performance_baseline()
        
        # Test unified client performance
        with patch('src.beast_mode.messaging.unified_client.TransportFactory') as mock_factory:
            with patch('src.beast_mode.messaging.unified_client.BeastModeSharedState') as mock_state_class:
                mock_factory.create_transport.return_value = mock_fast_transport
                mock_state_class.return_value = mock_fast_shared_state
                
                client = BeastModeClient('comparison_test')
                
                # Startup time
                start_time = time.time()
                await client.start()
                startup_time = time.time() - start_time
                
                # Message sending
                message = BeastModeMessage(
                    type=MessageType.SIMPLE_MESSAGE,
                    source='comparison_test',
                    payload={'text': 'comparison test'}
                )
                
                start_time = time.time()
                for _ in range(100):
                    await client.send_message(message)
                send_time = time.time() - start_time
                
                messages_per_second = 100 / send_time if send_time > 0 else float('inf')
                
                await client.stop()
                
                print(f"\n📊 Performance Comparison:")
                print(f"   Daemon Client - Startup: {baseline['startup_time']:.3f}s, Send: {baseline['send_rate']:.1f} msg/s")
                print(f"   Unified Client - Startup: {startup_time:.3f}s, Send: {messages_per_second:.1f} msg/s")
                
                # Performance should be comparable (within 2x)
                startup_ratio = startup_time / baseline['startup_time'] if baseline['startup_time'] > 0 else 1
                send_ratio = baseline['send_rate'] / messages_per_second if messages_per_second > 0 else 1
                
                print(f"   Startup ratio: {startup_ratio:.2f}x")
                print(f"   Send ratio: {send_ratio:.2f}x")
                
                # Assertions (unified client should be reasonably close to baseline)
                assert startup_ratio < 3.0, f"Startup too slow compared to baseline: {startup_ratio:.2f}x"
                assert send_ratio < 2.0, f"Sending too slow compared to baseline: {send_ratio:.2f}x"