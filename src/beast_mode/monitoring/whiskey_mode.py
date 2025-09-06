"""
Whiskey Mode Terminal Dashboard

Beautiful ambient terminal display for casual monitoring while having a drink.
"I'm having a whiskey, I'll watch for flips"
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.tree import Tree
from rich.rule import Rule

from ..core.interfaces import ReflectiveModule
from .events import Event, TestResultEvent, HubrisPreventionEvent


class WhiskeyModeStatus(Enum):
    """Status states for Whiskey Mode display"""
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class TestMetrics:
    """Test execution metrics for display"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    execution_time: float = 0.0
    last_run: Optional[datetime] = None


@dataclass
class SystemHealth:
    """System health metrics"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    test_velocity: float = 0.0  # tests per minute
    uptime: timedelta = timedelta()


class WhiskeyModeDisplay(ReflectiveModule):
    """
    Beautiful terminal dashboard for ambient monitoring.
    
    Features:
    - Live test matrix with satisfying animations
    - Hubris prevention status panel
    - System health sparklines
    - Mama Discovery Protocol alerts
    """
    
    def __init__(self):
        super().__init__()
        self.console = Console()
        self.layout = Layout()
        self.status = WhiskeyModeStatus.STARTING
        self.test_metrics = TestMetrics()
        self.system_health = SystemHealth()
        self.hubris_alerts: List[str] = []
        self.mama_discoveries: List[str] = []
        self.live_display: Optional[Live] = None
        
        # Animation state
        self.cascade_frames = []
        self.pulse_phase = 0.0
        self.last_update = datetime.now()
        
        self._setup_layout()
    
    def _setup_layout(self) -> None:
        """Initialize the terminal layout structure"""
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        self.layout["left"].split_column(
            Layout(name="test_matrix", ratio=3),
            Layout(name="system_health", ratio=1)
        )
        
        self.layout["right"].split_column(
            Layout(name="hubris_panel", ratio=1),
            Layout(name="mama_panel", ratio=1)
        )
    
    def _create_header(self) -> Panel:
        """Create the header panel with title and status"""
        title = Text("🥃 WHISKEY MODE", style="bold magenta")
        subtitle = Text("Beast Mode Monitoring Dashboard", style="dim")
        
        status_color = {
            WhiskeyModeStatus.STARTING: "yellow",
            WhiskeyModeStatus.ACTIVE: "green",
            WhiskeyModeStatus.PAUSED: "orange",
            WhiskeyModeStatus.ERROR: "red"
        }[self.status]
        
        status_text = Text(f"● {self.status.value.upper()}", style=f"bold {status_color}")
        
        header_content = Columns([
            Align.left(title),
            Align.center(subtitle),
            Align.right(status_text)
        ])
        
        return Panel(header_content, style="bright_blue")
    
    def _create_test_matrix(self) -> Panel:
        """Create the live test results matrix with animations"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Test Suite", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Count", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Trend", justify="center")
        
        # Add test results with animations
        if self.test_metrics.total_tests > 0:
            pass_rate = (self.test_metrics.passed_tests / self.test_metrics.total_tests) * 100
            
            # Animated status based on pass rate
            if pass_rate >= 95:
                status = Text("✨ EXCELLENT", style="bold green")
                trend = self._create_sparkline([95, 96, 97, 98, pass_rate], "green")
            elif pass_rate >= 80:
                status = Text("✅ GOOD", style="green")
                trend = self._create_sparkline([80, 85, 90, 95, pass_rate], "yellow")
            else:
                status = Text("⚠️  NEEDS ATTENTION", style="bold red")
                trend = self._create_sparkline([60, 65, 70, 75, pass_rate], "red")
            
            table.add_row(
                "All Tests",
                status,
                f"{self.test_metrics.passed_tests}/{self.test_metrics.total_tests}",
                f"{self.test_metrics.execution_time:.1f}s",
                trend
            )
            
            # Add individual test suites (mock data for demo)
            test_suites = [
                ("Unit Tests", 45, 2, 0.8),
                ("Integration Tests", 12, 0, 2.3),
                ("Hubris Prevention", 8, 0, 0.5),
                ("Beast Mode Core", 23, 1, 1.2)
            ]
            
            for suite_name, passed, failed, time in test_suites:
                total = passed + failed
                if total > 0:
                    suite_pass_rate = (passed / total) * 100
                    if suite_pass_rate == 100:
                        suite_status = Text("✅", style="green")
                    elif suite_pass_rate >= 80:
                        suite_status = Text("⚠️", style="yellow")
                    else:
                        suite_status = Text("❌", style="red")
                    
                    table.add_row(
                        f"  {suite_name}",
                        suite_status,
                        f"{passed}/{total}",
                        f"{time:.1f}s",
                        self._create_mini_sparkline(suite_pass_rate)
                    )
        else:
            table.add_row(
                "No tests run yet",
                Text("⏳ WAITING", style="dim"),
                "-",
                "-",
                "-"
            )
        
        return Panel(table, title="🧪 Test Results Matrix", border_style="green")
    
    def _create_sparkline(self, values: List[float], color: str) -> Text:
        """Create a sparkline chart from values"""
        if not values:
            return Text("─" * 8, style="dim")
        
        # Normalize values to 0-7 range for block characters
        min_val, max_val = min(values), max(values)
        if max_val == min_val:
            normalized = [4] * len(values)
        else:
            normalized = [int((v - min_val) / (max_val - min_val) * 7) for v in values]
        
        # Block characters for different heights
        blocks = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        sparkline = "".join(blocks[min(n, 7)] for n in normalized)
        return Text(sparkline, style=color)
    
    def _create_mini_sparkline(self, value: float) -> Text:
        """Create a mini sparkline for individual test suites"""
        # Simple trend indicator based on value
        if value >= 95:
            return Text("📈", style="green")
        elif value >= 80:
            return Text("📊", style="yellow")
        else:
            return Text("📉", style="red")
    
    def _create_system_health(self) -> Panel:
        """Create system health panel with sparklines"""
        health_table = Table(show_header=False, box=None)
        health_table.add_column("Metric", style="cyan")
        health_table.add_column("Value", justify="right")
        health_table.add_column("Trend", justify="center")
        
        # CPU with pulse animation
        cpu_color = "green" if self.system_health.cpu_percent < 70 else "yellow" if self.system_health.cpu_percent < 90 else "red"
        cpu_sparkline = self._create_sparkline([45, 52, 48, 55, self.system_health.cpu_percent], cpu_color)
        
        health_table.add_row(
            "CPU",
            f"{self.system_health.cpu_percent:.1f}%",
            cpu_sparkline
        )
        
        # Memory
        mem_color = "green" if self.system_health.memory_percent < 80 else "yellow" if self.system_health.memory_percent < 95 else "red"
        mem_sparkline = self._create_sparkline([60, 65, 62, 68, self.system_health.memory_percent], mem_color)
        
        health_table.add_row(
            "Memory",
            f"{self.system_health.memory_percent:.1f}%",
            mem_sparkline
        )
        
        # Test Velocity
        velocity_sparkline = self._create_sparkline([12, 15, 18, 16, self.system_health.test_velocity], "cyan")
        
        health_table.add_row(
            "Test Velocity",
            f"{self.system_health.test_velocity:.1f}/min",
            velocity_sparkline
        )
        
        return Panel(health_table, title="📊 System Health", border_style="cyan")
    
    def _create_hubris_panel(self) -> Panel:
        """Create hubris prevention monitoring panel"""
        if not self.hubris_alerts:
            content = Text("🛡️  All systems nominal\nNo hubris detected", style="dim green")
        else:
            content = Text("\n".join([
                "⚠️  Hubris Prevention Active",
                "",
                *self.hubris_alerts[-3:]  # Show last 3 alerts
            ]), style="yellow")
        
        return Panel(content, title="🛡️  Hubris Prevention", border_style="yellow")
    
    def _create_mama_panel(self) -> Panel:
        """Create Mama Discovery Protocol panel"""
        if not self.mama_discoveries:
            content = Text("👸 Mama Discovery Protocol\nStandby mode", style="dim")
        else:
            content = Text("\n".join([
                "👸 Mama Discovery Active",
                "",
                *self.mama_discoveries[-2:]  # Show last 2 discoveries
            ]), style="magenta")
        
        return Panel(content, title="👸 Mama Discovery", border_style="magenta")
    
    def _create_footer(self) -> Panel:
        """Create footer with controls and timestamp"""
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        
        controls = Text("Press 'q' to quit • 'p' to pause • 'r' to refresh", style="dim")
        time_text = Text(f"Last update: {timestamp}", style="dim")
        
        footer_content = Columns([
            Align.left(controls),
            Align.right(time_text)
        ])
        
        return Panel(footer_content, style="dim")
    
    def _update_display(self) -> Layout:
        """Update the complete display layout"""
        self.layout["header"].update(self._create_header())
        self.layout["test_matrix"].update(self._create_test_matrix())
        self.layout["system_health"].update(self._create_system_health())
        self.layout["hubris_panel"].update(self._create_hubris_panel())
        self.layout["mama_panel"].update(self._create_mama_panel())
        self.layout["footer"].update(self._create_footer())
        
        return self.layout
    
    async def start_display(self) -> None:
        """Start the live terminal display"""
        self.status = WhiskeyModeStatus.ACTIVE
        
        with Live(self._update_display(), refresh_per_second=4, screen=True) as live:
            self.live_display = live
            
            try:
                while self.status == WhiskeyModeStatus.ACTIVE:
                    # Update pulse animation
                    self.pulse_phase += 0.1
                    if self.pulse_phase > 2 * 3.14159:
                        self.pulse_phase = 0.0
                    
                    # Update display
                    live.update(self._update_display())
                    
                    # Sleep for smooth animation
                    await asyncio.sleep(0.25)
                    
            except KeyboardInterrupt:
                self.status = WhiskeyModeStatus.PAUSED
            finally:
                self.live_display = None
    
    def update_test_results(self, results: Dict[str, Any]) -> None:
        """Update test results from external source"""
        self.test_metrics.total_tests = results.get('total', 0)
        self.test_metrics.passed_tests = results.get('passed', 0)
        self.test_metrics.failed_tests = results.get('failed', 0)
        self.test_metrics.skipped_tests = results.get('skipped', 0)
        self.test_metrics.execution_time = results.get('duration', 0.0)
        self.test_metrics.last_run = datetime.now()
    
    def show_hubris_alert(self, alert: str) -> None:
        """Display hubris prevention alert"""
        timestamp = datetime.now().strftime("%H:%M")
        self.hubris_alerts.append(f"[{timestamp}] {alert}")
        
        # Keep only last 10 alerts
        if len(self.hubris_alerts) > 10:
            self.hubris_alerts = self.hubris_alerts[-10:]
    
    def display_mama_discovery(self, discovery: str) -> None:
        """Display Mama Discovery Protocol activation"""
        timestamp = datetime.now().strftime("%H:%M")
        self.mama_discoveries.append(f"[{timestamp}] {discovery}")
        
        # Keep only last 5 discoveries
        if len(self.mama_discoveries) > 5:
            self.mama_discoveries = self.mama_discoveries[-5:]
    
    def update_system_health(self, health: Dict[str, float]) -> None:
        """Update system health metrics"""
        self.system_health.cpu_percent = health.get('cpu', 0.0)
        self.system_health.memory_percent = health.get('memory', 0.0)
        self.system_health.test_velocity = health.get('test_velocity', 0.0)
    
    # ReflectiveModule interface
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the Whiskey Mode display"""
        return {
            "status": self.status.value,
            "active": self.live_display is not None,
            "last_update": self.last_update.isoformat(),
            "test_metrics": {
                "total": self.test_metrics.total_tests,
                "passed": self.test_metrics.passed_tests,
                "failed": self.test_metrics.failed_tests
            }
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "display_fps": 4,
            "memory_usage": "low",
            "cpu_usage": "minimal"
        }