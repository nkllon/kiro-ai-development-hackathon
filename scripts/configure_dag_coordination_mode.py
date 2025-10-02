#!/usr/bin/env python3
"""
DAG Coordination Mode Configuration
==================================

Explicit configuration for DAG coordination mode to prevent silent fallbacks
and ensure appropriate mode selection for different deployment scenarios.
"""

import os
import json
import sys
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from src.security.secure_credentials import get_redis_password


class CoordinationMode(Enum):
    """DAG coordination modes."""
    REDIS_REQUIRED = "redis_required"      # Production mode - Redis required
    REDIS_PREFERRED = "redis_preferred"    # Try Redis, explicit fallback
    IN_MEMORY_ONLY = "in_memory_only"      # Development mode - in-memory only
    AUTO_DETECT = "auto_detect"            # Legacy mode - not recommended


@dataclass
class CoordinationConfig:
    """Configuration for DAG coordination."""
    mode: CoordinationMode
    redis_host: str = "192.168.1.119"
    redis_port: int = 6379
    redis_password: str = ""
    allow_fallback: bool = False
    require_confirmation: bool = True
    development_mode: bool = False
    warnings_enabled: bool = True


class DAGCoordinationConfigurator:
    """Configure DAG coordination mode explicitly."""
    
    def __init__(self):
        self.config_file = ".kiro/dag_coordination_config.json"
        self.load_env_vars()
        self.default_config = CoordinationConfig(
            mode=CoordinationMode.REDIS_PREFERRED,
            allow_fallback=True,
            require_confirmation=True,
            redis_password=self.get_redis_password()
        )
    
    def load_env_vars(self):
        """Load environment variables from ~/.env if it exists."""
        home_env = Path.home() / ".env"
        if home_env.exists():
            with open(home_env, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    def get_redis_password(self) -> str:
        """Get Redis password from environment variables."""
        return os.getenv('REDIS_PASSWORD', os.getenv('BEAST_MODE_REDIS_PASSWORD', ''))
    
    def detect_environment(self) -> str:
        """Detect deployment environment."""
        if os.getenv("PRODUCTION") == "true":
            return "production"
        elif os.getenv("DEVELOPMENT") == "true":
            return "development"
        elif os.path.exists(".git"):
            return "development"
        else:
            return "unknown"
    
    def get_recommended_config(self, environment: str) -> CoordinationConfig:
        """Get recommended configuration for environment."""
        if environment == "production":
            return CoordinationConfig(
                mode=CoordinationMode.REDIS_REQUIRED,
                allow_fallback=False,
                require_confirmation=False,
                development_mode=False
            )
        elif environment == "development":
            return CoordinationConfig(
                mode=CoordinationMode.REDIS_PREFERRED,
                allow_fallback=True,
                require_confirmation=True,
                development_mode=True
            )
        else:
            return self.default_config
    
    def create_config_interactive(self) -> CoordinationConfig:
        """Create configuration interactively."""
        print("🔧 DAG Coordination Mode Configuration")
        print("=" * 50)
        
        environment = self.detect_environment()
        print(f"📍 Detected environment: {environment}")
        
        recommended = self.get_recommended_config(environment)
        print(f"💡 Recommended mode: {recommended.mode.value}")
        
        print("\nAvailable coordination modes:")
        print("1. redis_required   - Production mode, Redis mandatory")
        print("2. redis_preferred  - Try Redis, explicit fallback (recommended)")
        print("3. in_memory_only   - Development mode, single-host only")
        print("4. auto_detect      - Legacy mode (not recommended)")
        
        while True:
            choice = input(f"\nSelect mode (1-4) or press Enter for recommended [{recommended.mode.value}]: ").strip()
            
            if not choice:
                config = recommended
                break
            elif choice == "1":
                config = CoordinationConfig(mode=CoordinationMode.REDIS_REQUIRED, allow_fallback=False)
                break
            elif choice == "2":
                config = CoordinationConfig(mode=CoordinationMode.REDIS_PREFERRED, allow_fallback=True, require_confirmation=True)
                break
            elif choice == "3":
                config = CoordinationConfig(mode=CoordinationMode.IN_MEMORY_ONLY, allow_fallback=False, development_mode=True)
                break
            elif choice == "4":
                config = CoordinationConfig(mode=CoordinationMode.AUTO_DETECT, allow_fallback=True)
                print("⚠️  WARNING: auto_detect mode is not recommended for production")
                break
            else:
                print("❌ Invalid choice, please select 1-4")
        
        # Configure Redis settings if needed
        if config.mode in [CoordinationMode.REDIS_REQUIRED, CoordinationMode.REDIS_PREFERRED]:
            print(f"\n🔧 Redis Configuration")
            redis_host = input(f"Redis host [{config.redis_host}]: ").strip() or config.redis_host
            redis_port = input(f"Redis port [{config.redis_port}]: ").strip()
            redis_port = int(redis_port) if redis_port else config.redis_port
            
            # Handle password from environment
            env_password = self.get_redis_password()
            if env_password:
                print(f"Redis password: Using environment variable (REDIS_PASSWORD or BEAST_MODE_REDIS_PASSWORD)")
                config.redis_password = env_password
            else:
                print("⚠️  No Redis password found in environment variables")
                print("   Add REDIS_PASSWORD=your_password to ~/.env")
                redis_password = input("Redis password (will be stored in config): ").strip()
                if redis_password:
                    config.redis_password = redis_password
                    print("💡 Consider adding REDIS_PASSWORD to ~/.env instead")
            
            config.redis_host = redis_host
            config.redis_port = redis_port
        
        return config
    
    def save_config(self, config: CoordinationConfig) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        config_dict = {
            "mode": config.mode.value,
            "redis_host": config.redis_host,
            "redis_port": config.redis_port,
            "redis_password": config.redis_password,
            "allow_fallback": config.allow_fallback,
            "require_confirmation": config.require_confirmation,
            "development_mode": config.development_mode,
            "warnings_enabled": config.warnings_enabled,
            "created_at": "2025-10-02T08:15:00Z",
            "created_by": "dag_coordination_configurator"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"✅ Configuration saved to {self.config_file}")
    
    def load_config(self) -> Optional[CoordinationConfig]:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config_dict = json.load(f)
            
            return CoordinationConfig(
                mode=CoordinationMode(config_dict["mode"]),
                redis_host=config_dict.get("redis_host", "192.168.1.119"),
                redis_port=config_dict.get("redis_port", 6379),
                redis_password=config_dict.get("redis_password") or get_redis_password(),
                allow_fallback=config_dict.get("allow_fallback", False),
                require_confirmation=config_dict.get("require_confirmation", True),
                development_mode=config_dict.get("development_mode", False),
                warnings_enabled=config_dict.get("warnings_enabled", True)
            )
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return None
    
    def display_current_config(self) -> None:
        """Display current configuration."""
        config = self.load_config()
        if not config:
            print("❌ No configuration found")
            return
        
        print("📋 Current DAG Coordination Configuration")
        print("=" * 50)
        print(f"Mode: {config.mode.value}")
        print(f"Redis Host: {config.redis_host}")
        print(f"Redis Port: {config.redis_port}")
        print(f"Allow Fallback: {config.allow_fallback}")
        print(f"Require Confirmation: {config.require_confirmation}")
        print(f"Development Mode: {config.development_mode}")
        print(f"Warnings Enabled: {config.warnings_enabled}")
        
        # Show implications
        print(f"\n💡 Implications:")
        if config.mode == CoordinationMode.REDIS_REQUIRED:
            print("  • DAG execution will fail if Redis is unavailable")
            print("  • Suitable for production environments")
            print("  • Full visibility and multi-host support")
        elif config.mode == CoordinationMode.REDIS_PREFERRED:
            print("  • Will try Redis first, fall back to in-memory with confirmation")
            print("  • Good for development with production-like behavior")
            print("  • Provides warnings about limitations")
        elif config.mode == CoordinationMode.IN_MEMORY_ONLY:
            print("  • Uses in-memory coordination only")
            print("  • Single-host only, no cross-process coordination")
            print("  • Limited visibility and monitoring")
        else:
            print("  • Legacy auto-detection mode")
            print("  • Not recommended for production use")


def main():
    """Main configuration function."""
    configurator = DAGCoordinationConfigurator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "show":
            configurator.display_current_config()
        elif command == "create":
            config = configurator.create_config_interactive()
            configurator.save_config(config)
        elif command == "production":
            config = CoordinationConfig(
                mode=CoordinationMode.REDIS_REQUIRED,
                allow_fallback=False,
                development_mode=False
            )
            configurator.save_config(config)
            print("✅ Production configuration created")
        elif command == "development":
            config = CoordinationConfig(
                mode=CoordinationMode.REDIS_PREFERRED,
                allow_fallback=True,
                require_confirmation=True,
                development_mode=True
            )
            configurator.save_config(config)
            print("✅ Development configuration created")
        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python3 configure_dag_coordination_mode.py [show|create|production|development]")
    else:
        # Interactive mode
        config = configurator.create_config_interactive()
        configurator.save_config(config)


if __name__ == "__main__":
    main()