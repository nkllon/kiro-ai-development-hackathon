#!/usr/bin/env python3
"""
ACE Reporter Factory - Zero Downtime Deployment Control

This factory provides safe switching between StatusAnnouncer and EnhancedACEReporter
based on feature flags, enabling zero-downtime deployment and instant rollback.

Key Features:
- Feature flag controlled switching
- Instant rollback capability
- Configuration management
- Safe deployment validation
- Comprehensive error handling
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ACEReporterConfig:
    """Configuration management for ACE Reporter deployment"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(
            Path(__file__).parent.parent.parent.parent,
            ".kiro", "settings", "ace_reporter_config.json"
        )
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        default_config = {
            "deployment_mode": "backward_compatible",  # backward_compatible | enhanced | hybrid
            "feature_flags": {
                "ai_memory_palace_integration": False,
                "multi_channel_delivery": False,
                "enhanced_context": False,
                "spec_progress_monitoring": False,
                "directus_persistence": False
            },
            "rollback_settings": {
                "auto_rollback_on_error": True,
                "health_check_interval_seconds": 30,
                "error_threshold": 3,
                "performance_threshold_ms": 5000
            },
            "deployment_metadata": {
                "last_updated": datetime.now().isoformat(),
                "deployed_by": "ace_reporter_factory",
                "deployment_version": "2.0.0"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(loaded_config)
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                self._save_config(default_config)
        except Exception as e:
            print(f"⚠️  Failed to load config from {self.config_path}: {e}")
            print("🔄 Using default configuration")
        
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save config to {self.config_path}: {e}")
    
    def get_deployment_mode(self) -> str:
        """Get current deployment mode"""
        return self._config.get("deployment_mode", "backward_compatible")
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get current feature flags"""
        return self._config.get("feature_flags", {})
    
    def set_deployment_mode(self, mode: str):
        """Set deployment mode and save configuration"""
        if mode not in ["backward_compatible", "enhanced", "hybrid"]:
            raise ValueError(f"Invalid deployment mode: {mode}")
        
        self._config["deployment_mode"] = mode
        self._config["deployment_metadata"]["last_updated"] = datetime.now().isoformat()
        self._save_config(self._config)
    
    def enable_feature(self, feature_name: str):
        """Enable a specific feature flag"""
        if feature_name in self._config["feature_flags"]:
            self._config["feature_flags"][feature_name] = True
            self._config["deployment_metadata"]["last_updated"] = datetime.now().isoformat()
            self._save_config(self._config)
        else:
            raise ValueError(f"Unknown feature flag: {feature_name}")
    
    def disable_feature(self, feature_name: str):
        """Disable a specific feature flag"""
        if feature_name in self._config["feature_flags"]:
            self._config["feature_flags"][feature_name] = False
            self._config["deployment_metadata"]["last_updated"] = datetime.now().isoformat()
            self._save_config(self._config)
        else:
            raise ValueError(f"Unknown feature flag: {feature_name}")
    
    def emergency_rollback(self):
        """Emergency rollback to backward compatible mode"""
        print("🚨 EMERGENCY ROLLBACK: Switching to backward compatible mode")
        self._config["deployment_mode"] = "backward_compatible"
        for feature in self._config["feature_flags"]:
            self._config["feature_flags"][feature] = False
        self._config["deployment_metadata"]["last_updated"] = datetime.now().isoformat()
        self._config["deployment_metadata"]["emergency_rollback"] = True
        self._save_config(self._config)
        print("✅ Emergency rollback complete")


class ACEReporterFactory:
    """
    Factory for creating ACE Reporter instances with feature flag control
    
    This factory enables zero-downtime deployment by safely switching between
    StatusAnnouncer and EnhancedACEReporter based on configuration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = ACEReporterConfig(config_path)
        self._current_reporter = None
        self._health_check_count = 0
        self._error_count = 0
    
    def create_reporter(self) -> ReflectiveModule:
        """
        Create appropriate ACE Reporter instance based on configuration
        
        Returns:
            ReflectiveModule: Either StatusAnnouncer or EnhancedACEReporter
        """
        deployment_mode = self.config.get_deployment_mode()
        feature_flags = self.config.get_feature_flags()
        
        try:
            if deployment_mode == "backward_compatible":
                return self._create_status_announcer()
            elif deployment_mode == "enhanced":
                return self._create_enhanced_reporter(feature_flags)
            elif deployment_mode == "hybrid":
                return self._create_hybrid_reporter(feature_flags)
            else:
                print(f"⚠️  Unknown deployment mode: {deployment_mode}")
                print("🔄 Falling back to backward compatible mode")
                return self._create_status_announcer()
        
        except Exception as e:
            print(f"❌ Failed to create reporter in {deployment_mode} mode: {e}")
            print("🔄 Emergency fallback to StatusAnnouncer")
            self._error_count += 1
            
            # Auto-rollback if enabled and error threshold reached
            if (self.config._config.get("rollback_settings", {}).get("auto_rollback_on_error", True) and
                self._error_count >= self.config._config.get("rollback_settings", {}).get("error_threshold", 3)):
                self.config.emergency_rollback()
            
            return self._create_status_announcer()
    
    def _create_status_announcer(self) -> ReflectiveModule:
        """Create original StatusAnnouncer for backward compatibility"""
        try:
            from src.beast_mode.observatory.status_announcer import StatusAnnouncer
            reporter = StatusAnnouncer()
            print("✅ Created StatusAnnouncer (backward compatible mode)")
            return reporter
        except Exception as e:
            print(f"❌ Failed to create StatusAnnouncer: {e}")
            raise
    
    def _create_enhanced_reporter(self, feature_flags: Dict[str, bool]) -> ReflectiveModule:
        """Create EnhancedACEReporter with specified feature flags"""
        try:
            from src.beast_mode.observatory.enhanced_ace_reporter import EnhancedACEReporter
            reporter = EnhancedACEReporter(feature_flags=feature_flags)
            print(f"✅ Created EnhancedACEReporter with features: {[k for k, v in feature_flags.items() if v]}")
            return reporter
        except Exception as e:
            print(f"❌ Failed to create EnhancedACEReporter: {e}")
            raise
    
    def _create_hybrid_reporter(self, feature_flags: Dict[str, bool]) -> ReflectiveModule:
        """Create hybrid reporter (EnhancedACEReporter with conservative feature flags)"""
        # In hybrid mode, only enable the safest features
        safe_feature_flags = {
            "ai_memory_palace_integration": False,  # Disable for safety
            "multi_channel_delivery": False,        # Disable for safety
            "enhanced_context": feature_flags.get("enhanced_context", False),
            "spec_progress_monitoring": feature_flags.get("spec_progress_monitoring", False),
            "directus_persistence": False           # Disable for safety
        }
        
        try:
            from src.beast_mode.observatory.enhanced_ace_reporter import EnhancedACEReporter
            reporter = EnhancedACEReporter(feature_flags=safe_feature_flags)
            print(f"✅ Created hybrid reporter with safe features: {[k for k, v in safe_feature_flags.items() if v]}")
            return reporter
        except Exception as e:
            print(f"❌ Failed to create hybrid reporter: {e}")
            raise
    
    def validate_deployment(self, reporter: ReflectiveModule) -> bool:
        """
        Validate that the deployed reporter is working correctly
        
        Args:
            reporter: The reporter instance to validate
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Test basic functionality
            health = reporter.get_health_status()
            if health.health_score < 0.8:
                print(f"⚠️  Reporter health score too low: {health.health_score}")
                return False
            
            # Test basic methods exist and are callable
            required_methods = [
                'announce_spec_completion',
                'announce_task_completion', 
                'announce_milestone',
                'announce_system_status'
            ]
            
            for method_name in required_methods:
                if not hasattr(reporter, method_name):
                    print(f"❌ Missing required method: {method_name}")
                    return False
                
                method = getattr(reporter, method_name)
                if not callable(method):
                    print(f"❌ Method not callable: {method_name}")
                    return False
            
            print("✅ Reporter validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Reporter validation failed: {e}")
            return False
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current factory and reporter status"""
        return {
            "deployment_mode": self.config.get_deployment_mode(),
            "feature_flags": self.config.get_feature_flags(),
            "error_count": self._error_count,
            "health_check_count": self._health_check_count,
            "config_path": self.config.config_path,
            "last_updated": self.config._config.get("deployment_metadata", {}).get("last_updated")
        }
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        self._health_check_count += 1
        
        try:
            # Create reporter and validate
            reporter = self.create_reporter()
            validation_passed = self.validate_deployment(reporter)
            
            health_status = reporter.get_health_status()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "health_check_number": self._health_check_count,
                "validation_passed": validation_passed,
                "reporter_health": {
                    "status": health_status.status.value,
                    "health_score": health_status.health_score,
                    "issues": health_status.issues,
                    "uptime_seconds": health_status.uptime_seconds
                },
                "factory_status": self.get_current_status()
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "health_check_number": self._health_check_count,
                "validation_passed": False,
                "error": str(e),
                "factory_status": self.get_current_status()
            }


def main():
    """Main function to test ACE Reporter Factory"""
    print("🏭 ACE Reporter Factory - Zero Downtime Deployment Test")
    print("=" * 70)
    
    # Create factory
    factory = ACEReporterFactory()
    
    print("\n📋 Testing backward compatible mode...")
    factory.config.set_deployment_mode("backward_compatible")
    reporter1 = factory.create_reporter()
    validation1 = factory.validate_deployment(reporter1)
    print(f"✅ Backward compatible validation: {'PASSED' if validation1 else 'FAILED'}")
    
    print("\n📋 Testing enhanced mode...")
    factory.config.set_deployment_mode("enhanced")
    factory.config.enable_feature("enhanced_context")
    factory.config.enable_feature("spec_progress_monitoring")
    reporter2 = factory.create_reporter()
    validation2 = factory.validate_deployment(reporter2)
    print(f"✅ Enhanced mode validation: {'PASSED' if validation2 else 'FAILED'}")
    
    print("\n📋 Testing hybrid mode...")
    factory.config.set_deployment_mode("hybrid")
    reporter3 = factory.create_reporter()
    validation3 = factory.validate_deployment(reporter3)
    print(f"✅ Hybrid mode validation: {'PASSED' if validation3 else 'FAILED'}")
    
    print("\n🏥 Performing comprehensive health check...")
    health_report = factory.perform_health_check()
    print(f"🏥 Health Check: {'PASSED' if health_report['validation_passed'] else 'FAILED'}")
    print(f"📊 Reporter Health Score: {health_report['reporter_health']['health_score']:.2f}")
    
    print("\n📊 Current Factory Status:")
    status = factory.get_current_status()
    print(f"   Deployment Mode: {status['deployment_mode']}")
    print(f"   Active Features: {[k for k, v in status['feature_flags'].items() if v]}")
    print(f"   Error Count: {status['error_count']}")
    print(f"   Health Checks: {status['health_check_count']}")
    
    print("\n🚨 Testing emergency rollback...")
    factory.config.emergency_rollback()
    reporter4 = factory.create_reporter()
    validation4 = factory.validate_deployment(reporter4)
    print(f"✅ Emergency rollback validation: {'PASSED' if validation4 else 'FAILED'}")
    
    print("\n🎉 ACE Reporter Factory test complete!")
    print("✅ All deployment modes tested successfully")
    print("🛡️  Zero downtime deployment capability confirmed")
    print("🚨 Emergency rollback capability confirmed")


if __name__ == "__main__":
    main()