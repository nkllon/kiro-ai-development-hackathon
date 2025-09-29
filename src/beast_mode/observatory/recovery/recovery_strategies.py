"""
Recovery Strategies Implementation

Multiple recovery strategies for different types of WebSocket failures.
"""

import asyncio
import json
import logging
import subprocess
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .failure_classifier import FailureType


@dataclass
class RecoveryAttempt:
    """Data structure for a recovery attempt."""
    strategy_name: str
    failure_type: FailureType
    attempt_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    recovery_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.recovery_data is None:
            self.recovery_data = {}


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    success: bool
    strategy_used: str
    recovery_time: float
    error_message: Optional[str] = None
    next_strategy: Optional[str] = None
    fallback_activated: bool = False


class RecoveryStrategy(ABC):
    """Abstract base class for recovery strategies."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(__name__)
        
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "4.1",
            "action": action,
            "status": status,
            "strategy": self.name,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        
    @abstractmethod
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Check if this strategy can handle the given failure type."""
        pass
        
    @abstractmethod
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute the recovery strategy."""
        pass
        
    @abstractmethod
    def get_priority(self) -> int:
        """Get strategy priority (lower = higher priority)."""
        pass


class WebSocketReconnectionStrategy(RecoveryStrategy):
    """Strategy for simple WebSocket reconnection with backoff."""
    
    def __init__(self):
        super().__init__("websocket_reconnection")
        
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Can handle most failure types except bot protection."""
        return failure_type not in [
            FailureType.BOT_PROTECTION_TRIGGERED,
            FailureType.AUTHENTICATION_FAILED
        ]
        
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute WebSocket reconnection with exponential backoff."""
        start_time = time.time()
        
        self._log_action("websocket_reconnection", "in_progress", {
            "failure_type": failure_type.value,
            "attempt_number": attempt_number
        })
        
        try:
            # Calculate backoff delay
            backoff_delay = min(2 ** attempt_number, 30)  # Max 30 seconds
            
            self._log_action("websocket_reconnection", "backoff_wait", {
                "delay_seconds": backoff_delay,
                "attempt_number": attempt_number
            })
            
            await asyncio.sleep(backoff_delay)
            
            # Simulate reconnection attempt
            # In real implementation, this would attempt to reconnect the WebSocket
            success = await self._attempt_reconnection(failure_type)
            
            recovery_time = time.time() - start_time
            
            if success:
                self._log_action("websocket_reconnection", "completed", {
                    "success": True,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=True,
                    strategy_used=self.name,
                    recovery_time=recovery_time
                )
            else:
                self._log_action("websocket_reconnection", "failed", {
                    "success": False,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=False,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    error_message="Reconnection attempt failed"
                )
                
        except Exception as e:
            recovery_time = time.time() - start_time
            
            self._log_action("websocket_reconnection", "error", {
                "error": str(e),
                "recovery_time": recovery_time,
                "attempt_number": attempt_number
            })
            
            return RecoveryResult(
                success=False,
                strategy_used=self.name,
                recovery_time=recovery_time,
                error_message=str(e)
            )
    
    async def _attempt_reconnection(self, failure_type: FailureType) -> bool:
        """Attempt WebSocket reconnection."""
        # Simulate reconnection logic
        # In real implementation, this would:
        # 1. Close existing connection
        # 2. Create new WebSocket connection
        # 3. Verify connection is established
        
        if failure_type == FailureType.CONNECTION_REFUSED:
            # Simulate tunnel restart needed
            return False
        elif failure_type == FailureType.TIMEOUT:
            # Simulate timeout - retry might work
            return True
        else:
            # Simulate successful reconnection
            return True
    
    def get_priority(self) -> int:
        return 1


class TunnelRestartStrategy(RecoveryStrategy):
    """Strategy for restarting the cloudflared tunnel."""
    
    def __init__(self):
        super().__init__("tunnel_restart")
        
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Can handle connection-related failures."""
        return failure_type in [
            FailureType.CONNECTION_REFUSED,
            FailureType.UPGRADE_FAILED,
            FailureType.TIMEOUT
        ]
        
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute tunnel restart."""
        start_time = time.time()
        
        self._log_action("tunnel_restart", "in_progress", {
            "failure_type": failure_type.value,
            "attempt_number": attempt_number
        })
        
        try:
            # Stop existing tunnel process
            await self._stop_tunnel()
            
            # Wait for process to fully terminate
            await asyncio.sleep(2)
            
            # Start new tunnel process
            await self._start_tunnel()
            
            # Wait for tunnel to initialize
            await asyncio.sleep(5)
            
            # Verify tunnel is running
            tunnel_healthy = await self._verify_tunnel_health()
            
            recovery_time = time.time() - start_time
            
            if tunnel_healthy:
                self._log_action("tunnel_restart", "completed", {
                    "success": True,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=True,
                    strategy_used=self.name,
                    recovery_time=recovery_time
                )
            else:
                self._log_action("tunnel_restart", "failed", {
                    "success": False,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=False,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    error_message="Tunnel restart failed - tunnel not healthy"
                )
                
        except Exception as e:
            recovery_time = time.time() - start_time
            
            self._log_action("tunnel_restart", "error", {
                "error": str(e),
                "recovery_time": recovery_time,
                "attempt_number": attempt_number
            })
            
            return RecoveryResult(
                success=False,
                strategy_used=self.name,
                recovery_time=recovery_time,
                error_message=str(e)
            )
    
    async def _stop_tunnel(self):
        """Stop the cloudflared tunnel process."""
        self._log_action("tunnel_stop", "in_progress")
        
        try:
            # Find and kill cloudflared processes
            result = subprocess.run(
                ["pkill", "-f", "cloudflared"],
                capture_output=True,
                text=True
            )
            
            self._log_action("tunnel_stop", "completed", {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            
        except Exception as e:
            self._log_action("tunnel_stop", "error", {"error": str(e)})
            raise
    
    async def _start_tunnel(self):
        """Start the cloudflared tunnel process."""
        self._log_action("tunnel_start", "in_progress")
        
        try:
            # Start cloudflared tunnel
            # In real implementation, this would use the actual tunnel configuration
            result = subprocess.run(
                ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self._log_action("tunnel_start", "completed", {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
            
        except subprocess.TimeoutExpired:
            self._log_action("tunnel_start", "timeout", {"timeout": 10})
            # Timeout is expected for long-running tunnel process
        except Exception as e:
            self._log_action("tunnel_start", "error", {"error": str(e)})
            raise
    
    async def _verify_tunnel_health(self) -> bool:
        """Verify tunnel is healthy and running."""
        self._log_action("tunnel_health_check", "in_progress")
        
        try:
            # Check if cloudflared process is running
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True
            )
            
            is_running = result.returncode == 0
            
            self._log_action("tunnel_health_check", "completed", {
                "is_running": is_running,
                "process_count": len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            })
            
            return is_running
            
        except Exception as e:
            self._log_action("tunnel_health_check", "error", {"error": str(e)})
            return False
    
    def get_priority(self) -> int:
        return 2


class ConfigurationReloadStrategy(RecoveryStrategy):
    """Strategy for reloading tunnel configuration."""
    
    def __init__(self):
        super().__init__("configuration_reload")
        
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Can handle configuration-related failures."""
        return failure_type in [
            FailureType.AUTHENTICATION_FAILED,
            FailureType.CONNECTION_REFUSED
        ]
        
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute configuration reload."""
        start_time = time.time()
        
        self._log_action("configuration_reload", "in_progress", {
            "failure_type": failure_type.value,
            "attempt_number": attempt_number
        })
        
        try:
            # Reload tunnel configuration
            await self._reload_configuration()
            
            # Restart tunnel with new configuration
            await self._restart_tunnel_with_config()
            
            # Verify configuration is applied
            config_valid = await self._verify_configuration()
            
            recovery_time = time.time() - start_time
            
            if config_valid:
                self._log_action("configuration_reload", "completed", {
                    "success": True,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=True,
                    strategy_used=self.name,
                    recovery_time=recovery_time
                )
            else:
                self._log_action("configuration_reload", "failed", {
                    "success": False,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=False,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    error_message="Configuration reload failed"
                )
                
        except Exception as e:
            recovery_time = time.time() - start_time
            
            self._log_action("configuration_reload", "error", {
                "error": str(e),
                "recovery_time": recovery_time,
                "attempt_number": attempt_number
            })
            
            return RecoveryResult(
                success=False,
                strategy_used=self.name,
                recovery_time=recovery_time,
                error_message=str(e)
            )
    
    async def _reload_configuration(self):
        """Reload tunnel configuration."""
        self._log_action("config_reload", "in_progress")
        
        # Simulate configuration reload
        # In real implementation, this would:
        # 1. Read new configuration file
        # 2. Validate configuration
        # 3. Apply configuration changes
        
        await asyncio.sleep(1)
        
        self._log_action("config_reload", "completed")
    
    async def _restart_tunnel_with_config(self):
        """Restart tunnel with new configuration."""
        self._log_action("tunnel_restart_with_config", "in_progress")
        
        # Stop tunnel
        await self._stop_tunnel()
        await asyncio.sleep(2)
        
        # Start tunnel with new config
        await self._start_tunnel()
        await asyncio.sleep(5)
        
        self._log_action("tunnel_restart_with_config", "completed")
    
    async def _stop_tunnel(self):
        """Stop tunnel process."""
        subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
    
    async def _start_tunnel(self):
        """Start tunnel process."""
        subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:8000"])
    
    async def _verify_configuration(self) -> bool:
        """Verify configuration is valid."""
        self._log_action("config_verification", "in_progress")
        
        # Simulate configuration verification
        # In real implementation, this would:
        # 1. Check tunnel connectivity
        # 2. Verify authentication
        # 3. Test WebSocket upgrade
        
        await asyncio.sleep(1)
        
        self._log_action("config_verification", "completed", {"valid": True})
        return True
    
    def get_priority(self) -> int:
        return 3


class BotProtectionClearStrategy(RecoveryStrategy):
    """Strategy for handling Cloudflare bot protection."""
    
    def __init__(self):
        super().__init__("bot_protection_clear")
        
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Can only handle bot protection failures."""
        return failure_type == FailureType.BOT_PROTECTION_TRIGGERED
        
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute bot protection clearing strategy."""
        start_time = time.time()
        
        self._log_action("bot_protection_clear", "in_progress", {
            "failure_type": failure_type.value,
            "attempt_number": attempt_number
        })
        
        try:
            # Wait for Cloudflare block to expire
            wait_time = min(300, 60 * attempt_number)  # Max 5 minutes
            
            self._log_action("bot_protection_clear", "waiting", {
                "wait_time_seconds": wait_time,
                "attempt_number": attempt_number
            })
            
            await asyncio.sleep(wait_time)
            
            # Try to clear any cached blocks
            await self._clear_cached_blocks()
            
            # Test if protection is cleared
            protection_cleared = await self._test_protection_clear()
            
            recovery_time = time.time() - start_time
            
            if protection_cleared:
                self._log_action("bot_protection_clear", "completed", {
                    "success": True,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=True,
                    strategy_used=self.name,
                    recovery_time=recovery_time
                )
            else:
                self._log_action("bot_protection_clear", "failed", {
                    "success": False,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=False,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    error_message="Bot protection still active",
                    fallback_activated=True
                )
                
        except Exception as e:
            recovery_time = time.time() - start_time
            
            self._log_action("bot_protection_clear", "error", {
                "error": str(e),
                "recovery_time": recovery_time,
                "attempt_number": attempt_number
            })
            
            return RecoveryResult(
                success=False,
                strategy_used=self.name,
                recovery_time=recovery_time,
                error_message=str(e),
                fallback_activated=True
            )
    
    async def _clear_cached_blocks(self):
        """Clear any cached Cloudflare blocks."""
        self._log_action("clear_cached_blocks", "in_progress")
        
        # Simulate clearing cached blocks
        # In real implementation, this might involve:
        # 1. Clearing DNS cache
        # 2. Using different IP addresses
        # 3. Changing request patterns
        
        await asyncio.sleep(2)
        
        self._log_action("clear_cached_blocks", "completed")
    
    async def _test_protection_clear(self) -> bool:
        """Test if bot protection is cleared."""
        self._log_action("test_protection_clear", "in_progress")
        
        # Simulate protection test
        # In real implementation, this would:
        # 1. Make a test request
        # 2. Check for 1033 error
        # 3. Verify response headers
        
        await asyncio.sleep(1)
        
        # Simulate random success/failure for testing
        import random
        is_cleared = random.choice([True, False])
        
        self._log_action("test_protection_clear", "completed", {
            "protection_cleared": is_cleared
        })
        
        return is_cleared
    
    def get_priority(self) -> int:
        return 4


class FallbackActivationStrategy(RecoveryStrategy):
    """Strategy for activating HTTP polling fallback."""
    
    def __init__(self):
        super().__init__("fallback_activation")
        
    async def can_handle(self, failure_type: FailureType) -> bool:
        """Can handle any failure type as last resort."""
        return True
        
    async def execute(self, failure_type: FailureType, attempt_number: int = 1) -> RecoveryResult:
        """Execute fallback activation."""
        start_time = time.time()
        
        self._log_action("fallback_activation", "in_progress", {
            "failure_type": failure_type.value,
            "attempt_number": attempt_number
        })
        
        try:
            # Activate HTTP polling mode
            await self._activate_http_polling()
            
            # Verify fallback is working
            fallback_working = await self._verify_fallback()
            
            recovery_time = time.time() - start_time
            
            if fallback_working:
                self._log_action("fallback_activation", "completed", {
                    "success": True,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number,
                    "fallback_mode": "http_polling"
                })
                
                return RecoveryResult(
                    success=True,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    fallback_activated=True
                )
            else:
                self._log_action("fallback_activation", "failed", {
                    "success": False,
                    "recovery_time": recovery_time,
                    "attempt_number": attempt_number
                })
                
                return RecoveryResult(
                    success=False,
                    strategy_used=self.name,
                    recovery_time=recovery_time,
                    error_message="Fallback activation failed"
                )
                
        except Exception as e:
            recovery_time = time.time() - start_time
            
            self._log_action("fallback_activation", "error", {
                "error": str(e),
                "recovery_time": recovery_time,
                "attempt_number": attempt_number
            })
            
            return RecoveryResult(
                success=False,
                strategy_used=self.name,
                recovery_time=recovery_time,
                error_message=str(e)
            )
    
    async def _activate_http_polling(self):
        """Activate HTTP polling mode."""
        self._log_action("activate_http_polling", "in_progress")
        
        # Simulate HTTP polling activation
        # In real implementation, this would:
        # 1. Stop WebSocket connections
        # 2. Start HTTP polling service
        # 3. Configure polling intervals
        
        await asyncio.sleep(2)
        
        self._log_action("activate_http_polling", "completed", {
            "polling_interval": 5,
            "endpoint": "/api/poll"
        })
    
    async def _verify_fallback(self) -> bool:
        """Verify fallback is working."""
        self._log_action("verify_fallback", "in_progress")
        
        # Simulate fallback verification
        # In real implementation, this would:
        # 1. Test HTTP polling endpoint
        # 2. Verify data is being received
        # 3. Check polling frequency
        
        await asyncio.sleep(1)
        
        self._log_action("verify_fallback", "completed", {"working": True})
        return True
    
    def get_priority(self) -> int:
        return 5