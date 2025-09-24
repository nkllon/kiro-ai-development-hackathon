# Beast Mode Framework: Quick Start Tutorial

## Welcome to Beast Mode! 🚀

This tutorial will get you up and running with the Beast Mode Framework in under 30 minutes. You'll learn how to set up your environment, create your first tasks, and deploy a basic application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Your First Task](#your-first-task)
4. [Building a Simple Application](#building-a-simple-application)
5. [Testing and Monitoring](#testing-and-monitoring)
6. [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:
- Python 3.9 or higher
- Redis server (local or remote)
- Git (for cloning the repository)
- Basic familiarity with async Python programming

### System Requirements
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free disk space
- **OS**: Linux, macOS, or Windows with WSL2

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/kiro-ai-development-hackathon.git
cd kiro-ai-development-hackathon
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
make venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Or on Windows
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
make install

# Verify installation
python -c "from beast_mode.core import ReflectiveModule; print('✅ Beast Mode installed successfully!')"
```

### Step 4: Start Redis Server

```bash
# If using Docker
docker run -d -p 6379:6379 redis:latest

# Or if installed locally
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

## Your First Task

Let's create and execute your first Beast Mode task!

### Step 1: Create a Simple Task

Create a file called `my_first_task.py`:

```python
# my_first_task.py
import asyncio
from beast_mode.task_queue import TaskQueueManager
from beast_mode.task_queue.models import TaskBase
from typing import Dict, Any

class WelcomeTask(TaskBase):
    """A simple welcome task"""

    task_type: str = "welcome"
    username: str

    def __init__(self, username: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.task_type = "welcome"

async def main():
    # Configuration for Beast Mode
    config = {
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        "persistence": {
            "hot_ttl": 3600,  # 1 hour
            "warm_ttl": 86400  # 24 hours
        },
        "escalation": {
            "levels": 4,
            "base_timeout": 30
        }
    }

    # Initialize the task queue
    queue_manager = TaskQueueManager(config)
    await queue_manager.initialize()

    print("🚀 Beast Mode Task Queue initialized!")

    # Create and submit a task
    task = WelcomeTask(username="Developer")
    task_id = await queue_manager.submit_task(task)

    print(f"📝 Task submitted with ID: {task_id}")

    # Wait for task completion (in real apps, you'd use callbacks)
    await asyncio.sleep(2)

    # Check task status
    status = await queue_manager.get_task_status(task_id)
    print(f"✅ Task status: {status}")

    # Clean up
    await queue_manager.cleanup()
    print("🧹 Cleanup complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Run Your First Task

```bash
python my_first_task.py
```

You should see output like:
```
🚀 Beast Mode Task Queue initialized!
📝 Task submitted with ID: task_abc123xyz
✅ Task status: TaskStatus.COMPLETED
🧹 Cleanup complete!
```

**Congratulations! 🎉 You've just executed your first Beast Mode task!**

## Building a Simple Application

Now let's build a more realistic application - a simple image processing service.

### Step 1: Create the Image Processing Task

Create `image_processor.py`:

```python
# image_processor.py
import asyncio
import hashlib
from typing import Dict, Any, Optional
from beast_mode.task_queue import TaskQueueManager, TaskRegistry
from beast_mode.task_queue.models import TaskBase, TaskStatus
from beast_mode.core import ReflectiveModule

class ImageProcessingTask(TaskBase):
    """Task for processing images"""

    task_type: str = "image_processing"
    image_url: str
    operations: list = []  # ["resize", "rotate", "filter"]
    output_format: str = "jpg"

    def generate_cache_key(self) -> str:
        """Generate a cache key based on task parameters"""
        content = f"{self.image_url}_{self.operations}_{self.output_format}"
        return f"img_cache_{hashlib.md5(content.encode()).hexdigest()}"

@TaskRegistry.register("image_processing")
class ImageProcessingHandler(ReflectiveModule):
    """Handler for image processing tasks"""

    def __init__(self):
        super().__init__()
        self.processed_count = 0

    async def execute(self, task: ImageProcessingTask) -> Dict[str, Any]:
        """Execute image processing task"""

        print(f"🖼️  Processing image: {task.image_url}")
        print(f"📋 Operations: {', '.join(task.operations)}")

        # Simulate image processing (replace with actual image processing logic)
        await asyncio.sleep(2)  # Simulate processing time

        self.processed_count += 1

        # Generate result
        result = {
            "status": "success",
            "processed_image_url": f"processed_{task.image_url}",
            "operations_applied": task.operations,
            "output_format": task.output_format,
            "processing_time": 2.0,
            "cache_key": task.generate_cache_key()
        }

        print(f"✅ Image processing complete! Total processed: {self.processed_count}")
        return result

    def health_check(self) -> Dict[str, Any]:
        """Return health status"""
        return {
            "status": "healthy",
            "processed_count": self.processed_count,
            "service": "image_processing"
        }

class ImageProcessingService(ReflectiveModule):
    """Main service for coordinating image processing"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.queue_manager: Optional[TaskQueueManager] = None
        self.handler = ImageProcessingHandler()

    async def start(self):
        """Start the image processing service"""
        print("🏁 Starting Image Processing Service...")

        # Initialize task queue
        self.queue_manager = TaskQueueManager(self.config)
        await self.queue_manager.initialize()

        # Register our handler
        self.queue_manager.register_handler("image_processing", self.handler)

        print("✅ Image Processing Service is ready!")

    async def process_image(
        self,
        image_url: str,
        operations: list,
        output_format: str = "jpg"
    ) -> str:
        """Submit an image processing task"""

        if not self.queue_manager:
            raise RuntimeError("Service not started. Call start() first.")

        task = ImageProcessingTask(
            image_url=image_url,
            operations=operations,
            output_format=output_format
        )

        task_id = await self.queue_manager.submit_task(task)
        print(f"📤 Submitted image processing task: {task_id}")
        return task_id

    async def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a processing task"""
        if not self.queue_manager:
            return None

        return await self.queue_manager.get_task_result(task_id)

    async def stop(self):
        """Stop the service and clean up"""
        if self.queue_manager:
            await self.queue_manager.cleanup()
        print("🛑 Image Processing Service stopped")

    def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            "status": "healthy",
            "service": "image_processing_service",
            "handler_health": self.handler.health_check(),
            "queue_healthy": self.queue_manager is not None
        }

async def demo_application():
    """Demo of the image processing application"""

    # Configuration
    config = {
        "redis": {"host": "localhost", "port": 6379},
        "persistence": {"hot_ttl": 3600, "warm_ttl": 86400},
        "escalation": {"levels": 4, "base_timeout": 60}
    }

    # Create and start service
    service = ImageProcessingService(config)
    await service.start()

    try:
        # Submit several image processing tasks
        tasks = [
            ("https://example.com/image1.jpg", ["resize", "rotate"], "png"),
            ("https://example.com/image2.jpg", ["filter", "enhance"], "jpg"),
            ("https://example.com/image3.jpg", ["resize", "watermark"], "webp"),
        ]

        task_ids = []
        for image_url, operations, fmt in tasks:
            task_id = await service.process_image(image_url, operations, fmt)
            task_ids.append(task_id)

        print(f"\n🔄 Submitted {len(task_ids)} tasks. Waiting for completion...")

        # Wait for tasks to complete
        await asyncio.sleep(5)

        # Check results
        print("\n📊 Task Results:")
        for i, task_id in enumerate(task_ids):
            result = await service.get_result(task_id)
            if result:
                print(f"Task {i+1}: ✅ {result['status']}")
                print(f"  Output: {result.get('processed_image_url', 'N/A')}")
            else:
                print(f"Task {i+1}: ⏳ Still processing...")

        # Health check
        health = service.health_check()
        print(f"\n❤️  Service Health: {health['status']}")
        print(f"🔢 Images Processed: {health['handler_health']['processed_count']}")

    finally:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(demo_application())
```

### Step 2: Run the Application

```bash
python image_processor.py
```

Expected output:
```
🏁 Starting Image Processing Service...
✅ Image Processing Service is ready!
📤 Submitted image processing task: task_img_001
📤 Submitted image processing task: task_img_002
📤 Submitted image processing task: task_img_003

🔄 Submitted 3 tasks. Waiting for completion...
🖼️  Processing image: https://example.com/image1.jpg
📋 Operations: resize, rotate
✅ Image processing complete! Total processed: 1
🖼️  Processing image: https://example.com/image2.jpg
📋 Operations: filter, enhance
✅ Image processing complete! Total processed: 2
🖼️  Processing image: https://example.com/image3.jpg
📋 Operations: resize, watermark
✅ Image processing complete! Total processed: 3

📊 Task Results:
Task 1: ✅ success
  Output: processed_https://example.com/image1.jpg
Task 2: ✅ success
  Output: processed_https://example.com/image2.jpg
Task 3: ✅ success
  Output: processed_https://example.com/image3.jpg

❤️  Service Health: healthy
🔢 Images Processed: 3
🛑 Image Processing Service stopped
```

## Testing and Monitoring

### Step 1: Run the Built-in Tests

```bash
# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run all tests with coverage
make coverage
```

### Step 2: Monitor Your Application

Create a monitoring script `monitor.py`:

```python
# monitor.py
import asyncio
import time
from beast_mode.monitoring import HealthChecker
from beast_mode.task_queue import TaskQueueManager

async def monitor_system():
    """Monitor the Beast Mode system"""

    config = {
        "redis": {"host": "localhost", "port": 6379},
        "monitoring": {"check_interval": 5}
    }

    health_checker = HealthChecker(config)
    queue_manager = TaskQueueManager(config)

    await queue_manager.initialize()

    print("📊 Starting Beast Mode System Monitor...")
    print("Press Ctrl+C to stop monitoring\n")

    try:
        while True:
            # Check system health
            health_status = await health_checker.comprehensive_health_check()

            print(f"🕐 {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Overall Health: {'✅ HEALTHY' if health_status['overall_healthy'] else '❌ UNHEALTHY'}")
            print(f"Redis: {'🟢 UP' if health_status['redis']['status'] == 'healthy' else '🔴 DOWN'}")
            print(f"Task Queue: {'🟢 READY' if health_status['task_queue']['ready'] else '🔴 NOT READY'}")
            print(f"Active Tasks: {health_status['task_queue'].get('active_tasks', 0)}")
            print(f"Memory Usage: {health_status['system']['memory_percent']:.1f}%")
            print("-" * 50)

            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\n🛑 Stopping monitor...")
    finally:
        await queue_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(monitor_system())
```

Run the monitor:
```bash
python monitor.py
```

### Step 3: Load Testing

Create a simple load test `load_test.py`:

```python
# load_test.py
import asyncio
import time
import random
from beast_mode.task_queue import TaskQueueManager
from beast_mode.task_queue.models import TaskBase

class LoadTestTask(TaskBase):
    task_type: str = "load_test"
    payload: dict = {}

    def __init__(self, task_id: str, **kwargs):
        super().__init__(**kwargs)
        self.task_type = "load_test"
        self.payload = {"task_id": task_id, "timestamp": time.time()}

async def load_test(num_tasks: int = 100, concurrency: int = 10):
    """Run a load test with specified parameters"""

    config = {
        "redis": {"host": "localhost", "port": 6379},
        "persistence": {"hot_ttl": 3600}
    }

    queue_manager = TaskQueueManager(config)
    await queue_manager.initialize()

    print(f"🚀 Starting load test: {num_tasks} tasks with {concurrency} concurrent workers")

    start_time = time.time()

    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)

    async def submit_task(task_num: int):
        async with semaphore:
            task = LoadTestTask(task_id=f"load_test_{task_num}")
            task_id = await queue_manager.submit_task(task)

            # Simulate some processing delay
            await asyncio.sleep(random.uniform(0.1, 0.5))

            return task_id

    # Submit all tasks concurrently
    tasks = [submit_task(i) for i in range(num_tasks)]
    task_ids = await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time

    print(f"✅ Load test completed!")
    print(f"📊 Results:")
    print(f"   Tasks: {len(task_ids)}")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Throughput: {len(task_ids) / duration:.2f} tasks/second")
    print(f"   Average latency: {duration / len(task_ids) * 1000:.2f} ms")

    await queue_manager.cleanup()

if __name__ == "__main__":
    # Run with different parameters
    asyncio.run(load_test(num_tasks=50, concurrency=5))
```

Run the load test:
```bash
python load_test.py
```

## Next Steps

Congratulations! You've successfully:
✅ Installed Beast Mode Framework
✅ Created your first task
✅ Built a complete application
✅ Set up monitoring and testing

### Where to Go From Here

1. **Explore Advanced Features**
   - Read the [Advanced Implementation Guide](beast-mode-implementation-guide.md)
   - Study the [API Reference](beast-mode-api-reference.md)
   - Check out [Video Tutorials](beast-mode-video-scripts.md)

2. **Build Real Applications**
   - Integrate with your existing systems
   - Implement custom task types
   - Set up production deployment

3. **Join the Community**
   - GitHub: [Issues and Discussions](https://github.com/your-org/kiro-ai-development-hackathon/issues)
   - Discord: [Beast Mode Community](https://discord.gg/beast-mode)
   - Documentation: [Full Documentation](https://docs.beast-mode.dev)

4. **Contribute**
   - Report bugs or suggest features
   - Submit pull requests
   - Help improve documentation

## Common Gotchas and Tips

### 🐛 Troubleshooting Tips

**Redis Connection Issues:**
```bash
# Check if Redis is running
redis-cli ping

# If using Docker, ensure port mapping
docker run -d -p 6379:6379 redis:latest
```

**Task Not Completing:**
- Check Redis logs for errors
- Verify task handler registration
- Ensure async/await syntax is correct

**Performance Issues:**
- Monitor Redis memory usage
- Check Python async event loop
- Profile your task handlers

### 💡 Pro Tips

1. **Always use async/await** for I/O operations
2. **Register task handlers** before submitting tasks
3. **Monitor memory usage** in production
4. **Use caching** for expensive operations
5. **Implement health checks** for all components

## Getting Help

If you run into issues:

1. Check the [Troubleshooting Guide](beast-mode-troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/your-org/kiro-ai-development-hackathon/issues)
3. Join our [Discord Community](https://discord.gg/beast-mode)
4. Email support: support@beast-mode.dev

---

**Happy coding with Beast Mode! 🚀**

*This tutorial was generated by Documentation Agent Gamma - your friendly documentation companion!*