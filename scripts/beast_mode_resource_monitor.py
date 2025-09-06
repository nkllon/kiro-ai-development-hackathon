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
import sys

# Add src to path for Beast Mode imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import Beast Mode billing integration
try:
    from beast_mode.billing import GCPBillingMonitor, UnifiedFinancialMetrics, BillingProviderType
    BEAST_MODE_BILLING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Beast Mode billing not available: {e}")
    BEAST_MODE_BILLING_AVAILABLE = False


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
    
    Tracks everything that costs money or uses resources:
    - LLM token usage and costs
    - GCP billing and cloud resource costs  
    - Network bandwidth and API calls
    - Memory and compute resources
    - Unified financial burn rate and budget tracking
    """
    
    def __init__(self):
        self.data_dir = Path('beast_mode_metrics')
        self.data_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.token_usage_log = self.data_dir / 'token_usage.jsonl'
        self.network_metrics_log = self.data_dir / 'network_metrics.jsonl'
        self.resource_metrics_log = self.data_dir / 'resource_metrics.jsonl'
        self.financial_metrics_log = self.data_dir / 'financial_metrics.jsonl'
        self.gcp_billing_log = self.data_dir / 'gcp_billing.jsonl'
        
        # Current state
        self.current_metrics = {
            'tokens': [],
            'network': None,
            'resources': None,
            'financial': None,
            'gcp_billing': None,
            'unified_financial': None
        }
        
        # Configuration
        self.config = self._load_config()
        
        # Initialize GCP billing monitor if available and enabled
        self.gcp_monitor = None
        if BEAST_MODE_BILLING_AVAILABLE and self.config.get('gcp', {}).get('enabled', False):
            try:
                self.gcp_monitor = GCPBillingMonitor(self.config.get('gcp', {}))
                print("✅ GCP billing integration enabled")
            except Exception as e:
                print(f"⚠️  GCP billing integration failed to initialize: {e}")
        
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
                'cpu_usage_percent': 90.0,
                'gcp_daily_limit': 25.0
            },
            'llm_pricing': {
                'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
                'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
                'claude-3': {'input': 0.015, 'output': 0.075},
                'claude-instant': {'input': 0.0008, 'output': 0.0024}
            },
            'gcp': {
                'enabled': False,
                'billing_account_id': '',
                'project_ids': [],
                'credentials_path': '~/.config/gcp/credentials.json',
                'cache_duration_minutes': 15,
                'cost_attribution': {
                    'development': ['compute', 'storage'],
                    'ai_ml': ['aiplatform', 'ml'],
                    'networking': ['networking', 'cdn']
                },
                'budget_alerts': {
                    'daily_limit_usd': 25.0,
                    'hourly_spike_threshold': 5.0
                }
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
                await self._collect_gcp_billing_metrics()
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
    
    async def _collect_gcp_billing_metrics(self):
        """Collect GCP billing metrics if enabled"""
        if not self.gcp_monitor:
            return
        
        try:
            gcp_metrics = await self.gcp_monitor.collect_billing_metrics()
            self.current_metrics['gcp_billing'] = gcp_metrics
            
            # Log to file
            with open(self.gcp_billing_log, 'a') as f:
                f.write(json.dumps(gcp_metrics.to_dict(), default=str) + '\n')
                
        except Exception as e:
            self.logger.error(f"Failed to collect GCP billing metrics: {e}")
            # Don't fail the entire monitoring loop for GCP issues
    
    async def _collect_financial_metrics(self):
        """Calculate unified financial metrics from all sources"""
        # Calculate costs from recent token usage (LLM costs)
        llm_total_cost = 0.0
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
                            llm_total_cost += cost
                            
                            provider = usage['provider']
                            model = usage['model']
                            
                            cost_by_provider[provider] = cost_by_provider.get(provider, 0) + cost
                            cost_by_model[model] = cost_by_model.get(model, 0) + cost
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        # Add GCP costs if available
        gcp_cost = 0.0
        if self.current_metrics['gcp_billing']:
            gcp_cost = self.current_metrics['gcp_billing'].total_cost_usd
            cost_by_provider['GCP'] = gcp_cost
        
        # Calculate unified totals
        total_cost = llm_total_cost + gcp_cost
        
        # Calculate hourly burn rate (more realistic calculation)
        session_hours = (datetime.now() - self.session_start).total_seconds() / 3600
        
        # For very short sessions, use a more reasonable projection
        if session_hours < 0.1:  # Less than 6 minutes
            # Use daily cost as a more realistic hourly rate estimate
            if self.current_metrics['gcp_billing']:
                hourly_burn_rate = self.current_metrics['gcp_billing'].daily_cost_usd / 24
            else:
                hourly_burn_rate = total_cost * 10  # Conservative 10x projection for short sessions
        else:
            hourly_burn_rate = total_cost / session_hours
        
        # Budget calculations
        daily_budget = self.config['daily_budget_usd']
        budget_remaining = daily_budget - total_cost
        
        # Create unified financial metrics
        if BEAST_MODE_BILLING_AVAILABLE:
            from beast_mode.billing.interfaces import BudgetStatus
            
            # Determine budget status
            utilization = (total_cost / daily_budget) * 100 if daily_budget > 0 else 0
            if utilization >= 100:
                budget_status = BudgetStatus.EXCEEDED
            elif utilization >= 90:
                budget_status = BudgetStatus.CRITICAL
            elif utilization >= 75:
                budget_status = BudgetStatus.WARNING
            else:
                budget_status = BudgetStatus.HEALTHY
            
            unified_metrics = UnifiedFinancialMetrics(
                total_cost_usd=total_cost,
                daily_cost_usd=total_cost,  # Simplified for now
                hourly_burn_rate=hourly_burn_rate,
                budget_limit_usd=daily_budget,
                budget_remaining_usd=budget_remaining,
                budget_status=budget_status,
                cost_by_provider=cost_by_provider,
                cost_by_category={
                    'llm': llm_total_cost,
                    'gcp': gcp_cost,
                    'other': 0.0
                },
                provider_metrics=[],  # Will be populated with actual provider metrics
                cost_attribution=None,  # TODO: Implement cost attribution
                timestamp=datetime.now()
            )
            
            self.current_metrics['unified_financial'] = unified_metrics
        
        # Legacy financial metrics for backward compatibility
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
        print("   BEAST MODE UNIFIED COST MONITOR")
        print("   \"LLMs + GCP + Everything = Total Visibility\"")
        print("═══════════════════════════════════════════════════════════")
        print()
        
        # Unified Financial Status
        unified = self.current_metrics.get('unified_financial')
        financial = self.current_metrics['financial']
        
        if unified:
            print("💸 UNIFIED FINANCIAL STATUS:")
            print(f"   💰 Total Cost: ${unified.total_cost_usd:.4f}")
            
            # Show breakdown by category
            llm_cost = unified.cost_by_category.get('llm', 0)
            gcp_cost = unified.cost_by_category.get('gcp', 0)
            if gcp_cost > 0:
                print(f"       LLM: ${llm_cost:.4f} | GCP: ${gcp_cost:.4f}")
            
            print(f"   🔥 Burn Rate: ${unified.hourly_burn_rate:.4f}/hour")
            print(f"   🎯 Budget: ${unified.budget_remaining_usd:.2f} remaining")
            print(f"   📊 Utilization: {unified.budget_utilization_percent:.1f}%")
            
            # Budget status indicator
            status_emoji = {
                'HEALTHY': '✅',
                'WARNING': '⚠️',
                'CRITICAL': '🔥', 
                'EXCEEDED': '🚨'
            }
            status_name = unified.budget_status.name if hasattr(unified.budget_status, 'name') else str(unified.budget_status)
            print(f"   {status_emoji.get(status_name, '❓')} Status: {status_name}")
            
            if unified.budget_remaining_usd < 0:
                print(f"   🚨 OVER BUDGET by ${abs(unified.budget_remaining_usd):.2f}!")
            
            print()
            
        elif financial:
            # Fallback to legacy financial display
            print("💸 FINANCIAL STATUS:")
            print(f"   💰 Total Cost: ${financial.total_cost_usd:.4f}")
            print(f"   🔥 Burn Rate: ${financial.hourly_burn_rate:.4f}/hour")
            print(f"   🎯 Budget Remaining: ${financial.budget_remaining:.2f}")
            
            if financial.budget_remaining < 0:
                print(f"   🚨 OVER BUDGET by ${abs(financial.budget_remaining):.2f}!")
            
            print()
        
        # GCP Breakdown (if available)
        gcp_billing = self.current_metrics.get('gcp_billing')
        if gcp_billing:
            print("📊 GCP BREAKDOWN:")
            for service, cost in gcp_billing.cost_breakdown.items():
                print(f"   {self._get_service_emoji(service)} {service}: ${cost:.2f}")
            print()
            
            # GCP usage metrics
            if gcp_billing.usage_metrics:
                print("📈 GCP USAGE:")
                usage = gcp_billing.usage_metrics
                if 'compute_hours' in usage:
                    print(f"   🖥️  Compute Hours: {usage['compute_hours']:,}")
                if 'storage_gb' in usage:
                    print(f"   🗄️  Storage: {usage['storage_gb']:,} GB")
                if 'api_calls' in usage:
                    print(f"   📞 API Calls: {usage['api_calls']:,}")
                print()
        
        # Cost by Provider (unified view)
        if unified and unified.cost_by_provider:
            print("📊 COST BY PROVIDER:")
            for provider, cost in unified.cost_by_provider.items():
                print(f"   {provider}: ${cost:.4f}")
            print()
        elif financial and financial.cost_by_provider:
            print("📊 COST BY PROVIDER:")
            for provider, cost in financial.cost_by_provider.items():
                print(f"   {provider}: ${cost:.4f}")
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
        
        # Financial alerts (unified or legacy)
        unified = self.current_metrics.get('unified_financial')
        financial = self.current_metrics['financial']
        
        if unified:
            if unified.hourly_burn_rate > thresholds['hourly_burn_rate']:
                alerts.append(f"🚨 High burn rate: ${unified.hourly_burn_rate:.2f}/hour")
            
            if unified.budget_remaining_usd < 0:
                alerts.append(f"🚨 Over budget by ${abs(unified.budget_remaining_usd):.2f}")
                
            # GCP-specific alerts
            gcp_cost = unified.cost_by_category.get('gcp', 0)
            gcp_limit = thresholds.get('gcp_daily_limit', 25.0)
            if gcp_cost > gcp_limit:
                alerts.append(f"🚨 GCP costs exceed daily limit: ${gcp_cost:.2f} > ${gcp_limit:.2f}")
                
        elif financial:
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
    
    def _get_service_emoji(self, service_name: str) -> str:
        """Get emoji for GCP service"""
        service_emojis = {
            'Compute Engine': '🖥️',
            'Cloud Storage': '🗄️', 
            'AI Platform': '🤖',
            'Networking': '🌐',
            'Cloud Functions': '⚡',
            'Cloud SQL': '🗃️',
            'Kubernetes Engine': '☸️',
            'BigQuery': '📊',
            'Pub/Sub': '📡',
            'Other': '📦'
        }
        return service_emojis.get(service_name, '📦')
    
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