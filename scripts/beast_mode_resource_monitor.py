#!/usr/bin/env python3
"""
Beast Mode Resource Monitor

Real-time tracking of:
- Token usage and costs across LLM providers
- Network bandwidth and API calls
- Memory and compute resources
- Financial burn rate and budget tracking

"Show me the money and the tokens"
"""

import asyncio
import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import os


@dataclass
class TokenUsage:
    """Token usage tracking"""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime
    request_id: str


@dataclass
class NetworkMetrics:
    """Network usage metrics"""
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    api_calls_count: int
    bandwidth_mbps: float
    timestamp: datetime


@dataclass
class ResourceMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    gpu_usage_percent: Optional[float]
    gpu_memory_used_gb: Optional[float]
    timestamp: datetime


@dataclass
class FinancialMetrics:
    """Financial tracking"""
    total_cost_usd: float
    hourly_burn_rate: float
    daily_budget: float
    budget_remaining: float
    cost_by_provider: Dict[str, float]
    cost_by_model: Dict[str, float]
    timestamp: datetime


class BeastModeResourceMonitor:
    """
    Real-time resource monitoring for Beast Mode operations
    
    Tracks everything that costs money or uses resources
    """
    
    def __init__(self):
        self.data_dir = Path('beast_mode_metrics')
        self.data_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.token_usage_log = self.data_dir / 'token_usage.jsonl'
        self.network_metrics_log = self.data_dir / 'network_metrics.jsonl'
        self.resource_metrics_log = self.data_dir / 'resource_metrics.jsonl'
        self.financial_metrics_log = self.data_dir / 'financial_metrics.jsonl'
        
        # Current state
        self.current_metrics = {
            'tokens': [],
            'network': None,
            'resources': None,
            'financial': None
        }
        
        # Configuration
        self.config = self._load_config()
        
        # Tracking state
        self.session_start = datetime.now()
        self.last_network_stats = psutil.net_io_counters()
        self.api_call_count = 0
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        config_file = self.data_dir / 'monitor_config.json'
        
        default_config = {
            'daily_budget_usd': 50.0,
            'alert_thresholds': {
                'hourly_burn_rate': 5.0,
                'token_cost_per_request': 0.10,
                'memory_usage_percent': 85.0,
                'cpu_usage_percent': 90.0
            },
            'llm_pricing': {
                'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
                'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
                'claude-3': {'input': 0.015, 'output': 0.075},
                'claude-instant': {'input': 0.0008, 'output': 0.0024}
            },
            'update_interval_seconds': 5
        }
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        else:
            config = default_config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        return config
    
    async def start_monitoring(self):
        """Start the resource monitoring loop"""
        print("🚀 Beast Mode Resource Monitor Starting...")
        print(f"📊 Data directory: {self.data_dir}")
        print(f"💰 Daily budget: ${self.config['daily_budget_usd']}")
        print("─" * 60)
        
        try:
            while True:
                # Collect all metrics
                await self._collect_network_metrics()
                await self._collect_resource_metrics()
                await self._collect_financial_metrics()
                
                # Display current status
                await self._display_dashboard()
                
                # Check alerts
                await self._check_alerts()
                
                # Wait for next update
                await asyncio.sleep(self.config['update_interval_seconds'])
                
        except KeyboardInterrupt:
            print("\n🛑 Resource monitoring stopped")
            await self._save_session_summary()
    
    async def _collect_network_metrics(self):
        """Collect network usage metrics"""
        current_stats = psutil.net_io_counters()
        
        # Calculate bandwidth since last check
        time_delta = self.config['update_interval_seconds']
        bytes_sent_delta = current_stats.bytes_sent - self.last_network_stats.bytes_sent
        bytes_recv_delta = current_stats.bytes_recv - self.last_network_stats.bytes_recv
        
        bandwidth_mbps = ((bytes_sent_delta + bytes_recv_delta) * 8) / (time_delta * 1024 * 1024)
        
        metrics = NetworkMetrics(
            bytes_sent=current_stats.bytes_sent,
            bytes_received=current_stats.bytes_recv,
            packets_sent=current_stats.packets_sent,
            packets_received=current_stats.packets_recv,
            api_calls_count=self.api_call_count,
            bandwidth_mbps=bandwidth_mbps,
            timestamp=datetime.now()
        )
        
        self.current_metrics['network'] = metrics
        self.last_network_stats = current_stats
        
        # Log to file
        with open(self.network_metrics_log, 'a') as f:
            f.write(json.dumps(asdict(metrics), default=str) + '\n')
    
    async def _collect_resource_metrics(self):
        """Collect system resource metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU metrics (if available)
        gpu_usage = None
        gpu_memory = None
        
        try:
            # Try to get GPU stats using nvidia-smi
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_data = result.stdout.strip().split(', ')
                gpu_usage = float(gpu_data[0])
                gpu_memory = float(gpu_data[1]) / 1024  # Convert MB to GB
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass  # GPU monitoring not available
        
        metrics = ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_gb=memory.used / (1024**3),
            memory_total_gb=memory.total / (1024**3),
            disk_usage_percent=disk.percent,
            disk_free_gb=disk.free / (1024**3),
            gpu_usage_percent=gpu_usage,
            gpu_memory_used_gb=gpu_memory,
            timestamp=datetime.now()
        )
        
        self.current_metrics['resources'] = metrics
        
        # Log to file
        with open(self.resource_metrics_log, 'a') as f:
            f.write(json.dumps(asdict(metrics), default=str) + '\n')
    
    async def _collect_financial_metrics(self):
        """Calculate financial metrics from token usage"""
        # Calculate costs from recent token usage
        total_cost = 0.0
        cost_by_provider = {}
        cost_by_model = {}
        
        # Read recent token usage (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        if self.token_usage_log.exists():
            with open(self.token_usage_log) as f:
                for line in f:
                    try:
                        usage = json.loads(line)
                        usage_time = datetime.fromisoformat(usage['timestamp'])
                        
                        if usage_time > cutoff_time:
                            cost = usage['cost_usd']
                            total_cost += cost
                            
                            provider = usage['provider']
                            model = usage['model']
                            
                            cost_by_provider[provider] = cost_by_provider.get(provider, 0) + cost
                            cost_by_model[model] = cost_by_model.get(model, 0) + cost
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Calculate hourly burn rate
        session_hours = (datetime.now() - self.session_start).total_seconds() / 3600
        hourly_burn_rate = total_cost / max(session_hours, 0.1)  # Avoid division by zero
        
        # Budget calculations
        daily_budget = self.config['daily_budget_usd']
        budget_remaining = daily_budget - total_cost
        
        metrics = FinancialMetrics(
            total_cost_usd=total_cost,
            hourly_burn_rate=hourly_burn_rate,
            daily_budget=daily_budget,
            budget_remaining=budget_remaining,
            cost_by_provider=cost_by_provider,
            cost_by_model=cost_by_model,
            timestamp=datetime.now()
        )
        
        self.current_metrics['financial'] = metrics
        
        # Log to file
        with open(self.financial_metrics_log, 'a') as f:
            f.write(json.dumps(asdict(metrics), default=str) + '\n')
    
    async def _display_dashboard(self):
        """Display the real-time dashboard"""
        os.system('clear')
        
        print("💰 ═══════════════════════════════════════════════════════════")
        print("   BEAST MODE RESOURCE MONITOR - Show Me The Money!")
        print("   \"Tracking every token, every byte, every dollar\"")
        print("═══════════════════════════════════════════════════════════")
        print()
        
        # Financial Status
        financial = self.current_metrics['financial']
        if financial:
            print("💸 FINANCIAL STATUS:")
            print(f"   💰 Total Cost: ${financial.total_cost_usd:.4f}")
            print(f"   🔥 Burn Rate: ${financial.hourly_burn_rate:.4f}/hour")
            print(f"   🎯 Budget Remaining: ${financial.budget_remaining:.2f}")
            
            if financial.budget_remaining < 0:
                print(f"   🚨 OVER BUDGET by ${abs(financial.budget_remaining):.2f}!")
            
            print()
            
            if financial.cost_by_provider:
                print("   📊 Cost by Provider:")
                for provider, cost in financial.cost_by_provider.items():
                    print(f"      {provider}: ${cost:.4f}")
                print()
        
        # Token Usage (recent)
        recent_tokens = self.current_metrics['tokens'][-5:] if self.current_metrics['tokens'] else []
        if recent_tokens:
            print("🎯 RECENT TOKEN USAGE:")
            for usage in recent_tokens:
                print(f"   {usage.model}: {usage.total_tokens:,} tokens (${usage.cost_usd:.4f})")
            print()
        
        # Network Status
        network = self.current_metrics['network']
        if network:
            print("🌐 NETWORK STATUS:")
            print(f"   📡 Bandwidth: {network.bandwidth_mbps:.2f} Mbps")
            print(f"   📞 API Calls: {network.api_calls_count:,}")
            print(f"   ⬆️  Sent: {network.bytes_sent / (1024**3):.2f} GB")
            print(f"   ⬇️  Received: {network.bytes_received / (1024**3):.2f} GB")
            print()
        
        # Resource Status
        resources = self.current_metrics['resources']
        if resources:
            print("⚡ SYSTEM RESOURCES:")
            print(f"   🧠 CPU: {resources.cpu_percent:.1f}%")
            print(f"   💾 Memory: {resources.memory_percent:.1f}% ({resources.memory_used_gb:.1f}GB/{resources.memory_total_gb:.1f}GB)")
            print(f"   💿 Disk: {resources.disk_usage_percent:.1f}% ({resources.disk_free_gb:.1f}GB free)")
            
            if resources.gpu_usage_percent is not None:
                print(f"   🎮 GPU: {resources.gpu_usage_percent:.1f}% ({resources.gpu_memory_used_gb:.1f}GB)")
            print()
        
        # Session Info
        session_duration = datetime.now() - self.session_start
        print(f"⏱️  Session Duration: {str(session_duration).split('.')[0]}")
        print(f"🔄 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print("Press Ctrl+C to stop monitoring")
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        alerts = []
        thresholds = self.config['alert_thresholds']
        
        # Financial alerts
        financial = self.current_metrics['financial']
        if financial:
            if financial.hourly_burn_rate > thresholds['hourly_burn_rate']:
                alerts.append(f"🚨 High burn rate: ${financial.hourly_burn_rate:.2f}/hour")
            
            if financial.budget_remaining < 0:
                alerts.append(f"🚨 Over budget by ${abs(financial.budget_remaining):.2f}")
        
        # Resource alerts
        resources = self.current_metrics['resources']
        if resources:
            if resources.memory_percent > thresholds['memory_usage_percent']:
                alerts.append(f"🚨 High memory usage: {resources.memory_percent:.1f}%")
            
            if resources.cpu_percent > thresholds['cpu_usage_percent']:
                alerts.append(f"🚨 High CPU usage: {resources.cpu_percent:.1f}%")
        
        # Display alerts
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"   {alert}")
    
    def log_token_usage(self, provider: str, model: str, input_tokens: int, 
                       output_tokens: int, request_id: str = None):
        """Log token usage for cost tracking"""
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        pricing = self.config['llm_pricing'].get(model, {'input': 0.01, 'output': 0.01})
        cost_usd = (input_tokens * pricing['input'] / 1000) + (output_tokens * pricing['output'] / 1000)
        
        usage = TokenUsage(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            timestamp=datetime.now(),
            request_id=request_id or f"req_{int(time.time())}"
        )
        
        # Add to current metrics
        self.current_metrics['tokens'].append(usage)
        
        # Keep only last 100 entries in memory
        if len(self.current_metrics['tokens']) > 100:
            self.current_metrics['tokens'] = self.current_metrics['tokens'][-100:]
        
        # Log to file
        with open(self.token_usage_log, 'a') as f:
            f.write(json.dumps(asdict(usage), default=str) + '\n')
        
        return usage
    
    def log_api_call(self):
        """Log an API call for tracking"""
        self.api_call_count += 1
    
    async def _save_session_summary(self):
        """Save session summary on exit"""
        summary = {
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'session_duration_hours': (datetime.now() - self.session_start).total_seconds() / 3600,
            'final_metrics': {
                'financial': asdict(self.current_metrics['financial']) if self.current_metrics['financial'] else None,
                'network': asdict(self.current_metrics['network']) if self.current_metrics['network'] else None,
                'resources': asdict(self.current_metrics['resources']) if self.current_metrics['resources'] else None
            }
        }
        
        summary_file = self.data_dir / f"session_summary_{int(time.time())}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📊 Session summary saved to: {summary_file}")


async def main():
    """Main entry point"""
    monitor = BeastModeResourceMonitor()
    
    # Simulate some token usage for demo
    monitor.log_token_usage("openai", "gpt-4", 1500, 800, "demo_request_1")
    monitor.log_token_usage("anthropic", "claude-3", 2000, 1200, "demo_request_2")
    monitor.log_api_call()
    monitor.log_api_call()
    
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())