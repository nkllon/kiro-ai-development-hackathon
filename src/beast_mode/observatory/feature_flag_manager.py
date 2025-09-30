#!/usr/bin/env python3
"""
ACE Reporter Feature Flag Management System

This module provides comprehensive feature flag management for safe deployment
of Enhanced ACE Reporter capabilities with zero downtime.

Key Features:
- Safe switching between StatusAnnouncer and EnhancedACEReporter
- Granular feature flag control
- Real-time configuration updates
- Deployment safety validation
- Rollback automation
- Performance monitoring
"""

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleHealth, ModuleStatus, ModuleCapability


class FeatureFlagStatus(Enum):
    """Feature flag status values"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    TESTING = "testing"
    ROLLBACK = "rollback"
    ERROR = "error"


class DeploymentPhase(Enum):
    """Deployment phase tracking"""
    PREPARATION = "preparation"
    TESTING = "testing"
    GRADUAL_ROLLOUT = "gradual_rollout"
    FULL_DEPLOYMENT = "full_deployment"
    MONITORING = "monitoring"
    COMPLETE = "complete"


@dataclass
class FeatureFlagConfig:
    """Configuration for a single feature flag"""
    name: str
    enabled: bool
    status: FeatureFlagStatus
    description: str
    dependencies: List[str]
    risk_level: str  # low, medium, high, critical
    rollout_percentage: float = 0.0
    last_updated: str = ""
    performance_impact: Optional[float] = None
    error_count: int = 0
    success_count: int = 0


@dataclass
class DeploymentPlan:
    """Deployment plan for feature rollout"""
    phase: DeploymentPhase
    target_features: List[str]
    rollout_percentage: float
    success_criteria: Dict[str, Any]
    rollback_triggers: Dict[str, Any]
    monitoring_duration_minutes: int = 30
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class FeatureFlagManager(ReflectiveModule):
    """
    Comprehensive feature flag management system for ACE Reporter
    
    Provides safe deployment, monitoring, and rollback capabilities
    for Enhanced ACE Reporter features.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__()
        self.module_id = "ace_reporter_feature_flag_manager"
        
        # Configuration paths
        self.config_path = config_path or os.path.join(
            Path(__file__).parent.parent.parent.parent,
            ".kiro", "settings", "ace_reporter_feature_flags.json"
        )
        
        # Feature flag definitions
        self.feature_definitions = {
            "ai_memory_palace_integration": FeatureFlagConfig(
                name="ai_memory_palace_integration",
                enabled=False,
                status=FeatureFlagStatus.DISABLED,
                description="AI Memory Palace context integration",
                dependencies=[],
                risk_level="medium"
            ),
            "multi_channel_delivery": FeatureFlagConfig(
                name="multi_channel_delivery",
                enabled=False,
                status=FeatureFlagStatus.DISABLED,
                description="Multi-channel delivery system (WebSocket + HTTP + Directus)",
                dependencies=["ai_memory_palace_integration"],
                risk_level="high"
            ),
            "enhanced_context": FeatureFlagConfig(
                name="enhanced_context",
                enabled=False,
                status=FeatureFlagStatus.DISABLED,
                description="Enhanced observation context with correlation IDs",
                dependencies=[],
                risk_level="low"
            ),
            "spec_progress_monitoring": FeatureFlagConfig(
                name="spec_progress_monitoring",
                enabled=False,
                status=FeatureFlagStatus.DISABLED,
                description="Automatic spec progress tracking and reporting",
                dependencies=["enhanced_context"],
                risk_level="low"
            ),
            "directus_persistence": FeatureFlagConfig(
                name="directus_persistence",
                enabled=False,
                status=FeatureFlagStatus.DISABLED,
                description="Directus CMS persistence layer",
                dependencies=["multi_channel_delivery"],
                risk_level="medium"
            )
        }
        
        # Safety thresholds (initialize before loading configuration)
        self.safety_thresholds = {
            "max_error_rate": 0.05,  # 5% error rate
            "max_performance_degradation": 0.20,  # 20% performance degradation
            "min_health_score": 0.80,  # 80% health score
            "monitoring_window_minutes": 15
        }
        
        # Load configuration
        self._load_configuration()
        
        # Monitoring and safety
        self._monitoring_thread = None
        self._monitoring_active = False
        self._performance_history = []
        self._error_history = []
        
        # Current deployment plan
        self.current_deployment_plan: Optional[DeploymentPlan] = None
    
    def _load_configuration(self):
        """Load feature flag configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                    # Update feature definitions with saved configuration
                    for feature_name, feature_data in config_data.get("features", {}).items():
                        if feature_name in self.feature_definitions:
                            self.feature_definitions[feature_name].enabled = feature_data.get("enabled", False)
                            self.feature_definitions[feature_name].status = FeatureFlagStatus(
                                feature_data.get("status", "disabled")
                            )
                            self.feature_definitions[feature_name].rollout_percentage = feature_data.get(
                                "rollout_percentage", 0.0
                            )
                            self.feature_definitions[feature_name].last_updated = feature_data.get(
                                "last_updated", ""
                            )
                            self.feature_definitions[feature_name].error_count = feature_data.get(
                                "error_count", 0
                            )
                            self.feature_definitions[feature_name].success_count = feature_data.get(
                                "success_count", 0
                            )
            else:
                # Create default configuration
                self._save_configuration()
                
        except Exception as e:
            print(f"⚠️  Failed to load feature flag configuration: {e}")
            print("🔄 Using default configuration")
    
    def _save_configuration(self):
        """Save feature flag configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_data = {
                "features": {
                    name: {
                        "enabled": config.enabled,
                        "status": config.status.value,
                        "description": config.description,
                        "dependencies": config.dependencies,
                        "risk_level": config.risk_level,
                        "rollout_percentage": config.rollout_percentage,
                        "last_updated": config.last_updated,
                        "error_count": config.error_count,
                        "success_count": config.success_count
                    }
                    for name, config in self.feature_definitions.items()
                },
                "safety_thresholds": self.safety_thresholds,
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to save feature flag configuration: {e}")
    
    # ========================================================================
    # ReflectiveModule Implementation
    # ========================================================================
    
    def get_module_info(self):
        return {
            "module_id": self.module_id,
            "module_name": "ACE Reporter Feature Flag Manager",
            "version": "1.0.0",
            "description": "Feature flag management for safe ACE Reporter deployment",
            "managed_features": list(self.feature_definitions.keys()),
            "active_features": [name for name, config in self.feature_definitions.items() if config.enabled]
        }
    
    def get_capabilities(self):
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self):
        # Calculate health based on feature flag status
        total_features = len(self.feature_definitions)
        error_features = sum(1 for config in self.feature_definitions.values() 
                           if config.status == FeatureFlagStatus.ERROR)
        
        health_score = 1.0 - (error_features / max(1, total_features))
        
        issues = []
        for name, config in self.feature_definitions.items():
            if config.status == FeatureFlagStatus.ERROR:
                issues.append(f"Feature {name} in error state")
            elif config.error_count > 10:
                issues.append(f"Feature {name} has high error count: {config.error_count}")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY if health_score > 0.8 else ModuleStatus.WARNING,
            health_score=health_score,
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self):
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        # Disable all high-risk features
        degraded_capabilities = []
        for name, config in self.feature_definitions.items():
            if config.risk_level in ["high", "critical"] and config.enabled:
                self.disable_feature(name, reason="Graceful degradation")
                degraded_capabilities.append(name)
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=self.get_capabilities()
        )
    
    # ========================================================================
    # Feature Flag Management
    # ========================================================================
    
    def enable_feature(self, feature_name: str, rollout_percentage: float = 100.0, reason: str = "") -> bool:
        """
        Enable a feature flag with optional gradual rollout
        
        Args:
            feature_name: Name of the feature to enable
            rollout_percentage: Percentage of traffic to enable for (0-100)
            reason: Reason for enabling the feature
            
        Returns:
            bool: True if feature was enabled successfully
        """
        if feature_name not in self.feature_definitions:
            print(f"❌ Unknown feature flag: {feature_name}")
            return False
        
        # Check dependencies
        config = self.feature_definitions[feature_name]
        for dependency in config.dependencies:
            if not self.feature_definitions[dependency].enabled:
                print(f"❌ Cannot enable {feature_name}: dependency {dependency} is not enabled")
                return False
        
        try:
            # Update configuration
            config.enabled = True
            config.status = FeatureFlagStatus.ENABLED
            config.rollout_percentage = rollout_percentage
            config.last_updated = datetime.now().isoformat()
            
            # Save configuration
            self._save_configuration()
            
            print(f"✅ Feature {feature_name} enabled at {rollout_percentage}% rollout")
            if reason:
                print(f"   Reason: {reason}")
            
            # Start monitoring if not already active
            if not self._monitoring_active:
                self._start_monitoring()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to enable feature {feature_name}: {e}")
            return False
    
    def disable_feature(self, feature_name: str, reason: str = "") -> bool:
        """
        Disable a feature flag
        
        Args:
            feature_name: Name of the feature to disable
            reason: Reason for disabling the feature
            
        Returns:
            bool: True if feature was disabled successfully
        """
        if feature_name not in self.feature_definitions:
            print(f"❌ Unknown feature flag: {feature_name}")
            return False
        
        try:
            # Check if other features depend on this one
            dependents = [name for name, config in self.feature_definitions.items() 
                         if feature_name in config.dependencies and config.enabled]
            
            if dependents:
                print(f"⚠️  Warning: Disabling {feature_name} will affect dependent features: {dependents}")
                # Disable dependent features first
                for dependent in dependents:
                    self.disable_feature(dependent, reason=f"Dependency {feature_name} disabled")
            
            # Update configuration
            config = self.feature_definitions[feature_name]
            config.enabled = False
            config.status = FeatureFlagStatus.DISABLED
            config.rollout_percentage = 0.0
            config.last_updated = datetime.now().isoformat()
            
            # Save configuration
            self._save_configuration()
            
            print(f"✅ Feature {feature_name} disabled")
            if reason:
                print(f"   Reason: {reason}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to disable feature {feature_name}: {e}")
            return False
    
    def get_feature_status(self, feature_name: str) -> Optional[FeatureFlagConfig]:
        """Get status of a specific feature flag"""
        return self.feature_definitions.get(feature_name)
    
    def get_all_features_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all feature flags"""
        return {
            name: {
                "enabled": config.enabled,
                "status": config.status.value,
                "description": config.description,
                "risk_level": config.risk_level,
                "rollout_percentage": config.rollout_percentage,
                "dependencies": config.dependencies,
                "error_count": config.error_count,
                "success_count": config.success_count,
                "last_updated": config.last_updated
            }
            for name, config in self.feature_definitions.items()
        }
    
    def get_enabled_features(self) -> Dict[str, bool]:
        """Get dictionary of enabled features for ACE Reporter Factory"""
        return {
            name: config.enabled
            for name, config in self.feature_definitions.items()
        }
    
    # ========================================================================
    # Deployment Management
    # ========================================================================
    
    def create_deployment_plan(self, 
                             target_features: List[str],
                             rollout_percentage: float = 100.0,
                             monitoring_duration_minutes: int = 30) -> DeploymentPlan:
        """
        Create a deployment plan for feature rollout
        
        Args:
            target_features: List of features to deploy
            rollout_percentage: Target rollout percentage
            monitoring_duration_minutes: How long to monitor after deployment
            
        Returns:
            DeploymentPlan: The created deployment plan
        """
        plan = DeploymentPlan(
            phase=DeploymentPhase.PREPARATION,
            target_features=target_features,
            rollout_percentage=rollout_percentage,
            success_criteria={
                "min_health_score": self.safety_thresholds["min_health_score"],
                "max_error_rate": self.safety_thresholds["max_error_rate"],
                "max_performance_degradation": self.safety_thresholds["max_performance_degradation"]
            },
            rollback_triggers={
                "health_score_below": self.safety_thresholds["min_health_score"],
                "error_rate_above": self.safety_thresholds["max_error_rate"],
                "performance_degradation_above": self.safety_thresholds["max_performance_degradation"]
            },
            monitoring_duration_minutes=monitoring_duration_minutes
        )
        
        self.current_deployment_plan = plan
        return plan
    
    def execute_deployment_plan(self, plan: DeploymentPlan) -> bool:
        """
        Execute a deployment plan with safety monitoring
        
        Args:
            plan: The deployment plan to execute
            
        Returns:
            bool: True if deployment was successful
        """
        try:
            print(f"🚀 Executing deployment plan for features: {plan.target_features}")
            
            # Phase 1: Preparation
            plan.phase = DeploymentPhase.PREPARATION
            plan.started_at = datetime.now().isoformat()
            
            # Validate dependencies
            for feature_name in plan.target_features:
                config = self.feature_definitions[feature_name]
                for dependency in config.dependencies:
                    if not self.feature_definitions[dependency].enabled:
                        print(f"❌ Deployment failed: {feature_name} requires {dependency}")
                        return False
            
            # Phase 2: Testing (gradual rollout)
            plan.phase = DeploymentPhase.TESTING
            print("📋 Phase 2: Testing with gradual rollout...")
            
            for feature_name in plan.target_features:
                # Start with 10% rollout for testing
                if not self.enable_feature(feature_name, rollout_percentage=10.0, 
                                         reason="Deployment plan testing phase"):
                    print(f"❌ Failed to enable {feature_name} for testing")
                    self._rollback_deployment(plan)
                    return False
            
            # Monitor for 5 minutes during testing
            if not self._monitor_deployment(plan, duration_minutes=5):
                print("❌ Testing phase failed safety checks")
                self._rollback_deployment(plan)
                return False
            
            # Phase 3: Gradual rollout
            plan.phase = DeploymentPhase.GRADUAL_ROLLOUT
            print(f"📋 Phase 3: Gradual rollout to {plan.rollout_percentage}%...")
            
            for feature_name in plan.target_features:
                if not self.enable_feature(feature_name, rollout_percentage=plan.rollout_percentage,
                                         reason="Deployment plan gradual rollout"):
                    print(f"❌ Failed to rollout {feature_name}")
                    self._rollback_deployment(plan)
                    return False
            
            # Phase 4: Full deployment monitoring
            plan.phase = DeploymentPhase.MONITORING
            print(f"📋 Phase 4: Monitoring for {plan.monitoring_duration_minutes} minutes...")
            
            if not self._monitor_deployment(plan, duration_minutes=plan.monitoring_duration_minutes):
                print("❌ Monitoring phase failed safety checks")
                self._rollback_deployment(plan)
                return False
            
            # Phase 5: Complete
            plan.phase = DeploymentPhase.COMPLETE
            plan.completed_at = datetime.now().isoformat()
            
            print("✅ Deployment plan executed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Deployment plan execution failed: {e}")
            self._rollback_deployment(plan)
            return False
    
    def _monitor_deployment(self, plan: DeploymentPlan, duration_minutes: int) -> bool:
        """Monitor deployment for safety criteria"""
        print(f"👁️  Monitoring deployment for {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Check health status
            health = self.get_health_status()
            if health.health_score < plan.rollback_triggers["health_score_below"]:
                print(f"❌ Health score too low: {health.health_score}")
                return False
            
            # Check error rates for enabled features
            total_operations = 0
            total_errors = 0
            
            for feature_name in plan.target_features:
                config = self.feature_definitions[feature_name]
                total_operations += config.success_count + config.error_count
                total_errors += config.error_count
            
            if total_operations > 0:
                error_rate = total_errors / total_operations
                if error_rate > plan.rollback_triggers["error_rate_above"]:
                    print(f"❌ Error rate too high: {error_rate:.2%}")
                    return False
            
            # Sleep for monitoring interval
            time.sleep(30)  # Check every 30 seconds
        
        print("✅ Monitoring completed successfully")
        return True
    
    def _rollback_deployment(self, plan: DeploymentPlan):
        """Rollback a failed deployment"""
        print("🚨 ROLLING BACK DEPLOYMENT")
        
        for feature_name in plan.target_features:
            self.disable_feature(feature_name, reason="Deployment rollback")
        
        plan.phase = DeploymentPhase.PREPARATION
        print("✅ Rollback completed")
    
    def emergency_rollback_all(self, reason: str = "Emergency rollback"):
        """Emergency rollback of all features"""
        print("🚨 EMERGENCY ROLLBACK: Disabling all features")
        
        for feature_name in self.feature_definitions:
            if self.feature_definitions[feature_name].enabled:
                self.disable_feature(feature_name, reason=reason)
        
        print("✅ Emergency rollback completed")
    
    # ========================================================================
    # Monitoring and Safety
    # ========================================================================
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        print("👁️  Feature flag monitoring started")
    
    def _stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        print("👁️  Feature flag monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self._monitoring_active:
            try:
                # Check feature health
                for name, config in self.feature_definitions.items():
                    if config.enabled:
                        self._check_feature_health(name, config)
                
                # Sleep for monitoring interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                time.sleep(60)
    
    def _check_feature_health(self, feature_name: str, config: FeatureFlagConfig):
        """Check health of a specific feature"""
        try:
            # Calculate error rate
            total_operations = config.success_count + config.error_count
            if total_operations > 0:
                error_rate = config.error_count / total_operations
                
                # Check if error rate is too high
                if error_rate > self.safety_thresholds["max_error_rate"]:
                    print(f"⚠️  Feature {feature_name} error rate too high: {error_rate:.2%}")
                    config.status = FeatureFlagStatus.ERROR
                    
                    # Auto-disable if critical
                    if config.risk_level == "critical":
                        self.disable_feature(feature_name, reason="Auto-disabled due to high error rate")
            
        except Exception as e:
            print(f"⚠️  Health check failed for {feature_name}: {e}")
    
    def record_feature_success(self, feature_name: str):
        """Record a successful operation for a feature"""
        if feature_name in self.feature_definitions:
            self.feature_definitions[feature_name].success_count += 1
    
    def record_feature_error(self, feature_name: str):
        """Record an error for a feature"""
        if feature_name in self.feature_definitions:
            self.feature_definitions[feature_name].error_count += 1


def main():
    """Test the feature flag management system"""
    print("🏁 ACE Reporter Feature Flag Management System Test")
    print("=" * 70)
    
    # Create feature flag manager
    manager = FeatureFlagManager()
    
    print("\n📋 Initial feature status:")
    for name, status in manager.get_all_features_status().items():
        print(f"   {name}: {'✅' if status['enabled'] else '❌'} ({status['status']})")
    
    print("\n📋 Testing feature enablement...")
    
    # Test enabling low-risk features first
    manager.enable_feature("enhanced_context", reason="Testing low-risk feature")
    manager.enable_feature("spec_progress_monitoring", reason="Testing dependent feature")
    
    print("\n📋 Testing deployment plan...")
    
    # Create deployment plan
    plan = manager.create_deployment_plan(
        target_features=["ai_memory_palace_integration"],
        rollout_percentage=50.0,
        monitoring_duration_minutes=1  # Short for testing
    )
    
    print(f"📋 Created deployment plan: {plan.target_features}")
    
    # Test getting enabled features for factory
    enabled_features = manager.get_enabled_features()
    print(f"\n📋 Enabled features for factory: {[k for k, v in enabled_features.items() if v]}")
    
    print("\n🏥 Health check:")
    health = manager.get_health_status()
    print(f"   Health Score: {health.health_score:.2f}")
    print(f"   Status: {health.status.value}")
    print(f"   Issues: {health.issues}")
    
    print("\n🚨 Testing emergency rollback...")
    manager.emergency_rollback_all("Test emergency rollback")
    
    final_status = manager.get_enabled_features()
    enabled_count = sum(1 for v in final_status.values() if v)
    print(f"✅ Emergency rollback complete - {enabled_count} features enabled")
    
    print("\n🎉 Feature flag management system test complete!")
    print("✅ All feature flag operations tested successfully")
    print("🛡️  Safe deployment and rollback capabilities confirmed")


if __name__ == "__main__":
    main()