#!/usr/bin/env python3
"""
Node A's Solution: Defensive Architecture Config Manager
========================================================

My approach focuses on:
1. Defense in depth - multiple validation layers
2. Immutable config objects with copy-on-write
3. Circuit breaker pattern for self-healing
4. Comprehensive logging and metrics
5. Modular validation rule engine

Architecture Philosophy: "Fail fast, heal smart, monitor everything"
"""

import asyncio
import json
import copy
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Import the challenge framework
from emergent_evolution_challenge import (
    SelfHealingConfigManager, ConfigSourceType, ValidationLevel,
    ConfigValidationRule, ConfigValidationResult, ConfigurationError, ValidationError
)

class CircuitBreakerState:
    """Circuit breaker for self-healing operations."""

    def __init__(self, failure_threshold: int = 3, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False

    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.is_open = True

    def can_attempt_operation(self) -> bool:
        """Check if operation should be attempted."""
        if not self.is_open:
            return True

        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).total_seconds()
            if elapsed > self.timeout_seconds:
                # Half-open state - try one operation
                self.is_open = False
                return True

        return False

@dataclass(frozen=True)  # Immutable config
class ImmutableConfig:
    """Immutable configuration object with validation tracking."""
    data: Dict[str, Any]
    validation_hash: str
    last_validated: datetime
    source_info: Dict[str, Any]

    def get(self, path: str, default=None):
        """Get nested configuration value by dot-notation path."""
        keys = path.split('.')
        value = self.data

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def update(self, updates: Dict[str, Any]) -> 'ImmutableConfig':
        """Create new config with updates (copy-on-write)."""
        new_data = copy.deepcopy(self.data)
        new_data.update(updates)

        return ImmutableConfig(
            data=new_data,
            validation_hash=str(hash(str(new_data))),
            last_validated=datetime.now(),
            source_info=self.source_info
        )

class DefensiveConfigManager(SelfHealingConfigManager):
    """
    Node A's Implementation: Defensive Architecture Approach

    Key Features:
    - Immutable config objects
    - Circuit breaker pattern
    - Multi-layer validation
    - Comprehensive error tracking
    - Smart caching with invalidation
    """

    def __init__(self, config_source: ConfigSourceType, validation_level: ValidationLevel = ValidationLevel.STRICT):
        super().__init__(config_source, validation_level)

        # Defensive components
        self.circuit_breaker = CircuitBreakerState()
        self.config_cache = {}
        self.validation_cache = {}
        self.healing_strategies = {}
        self.metrics = {
            'loads': 0, 'validations': 0, 'heals': 0, 'errors': 0,
            'cache_hits': 0, 'cache_misses': 0
        }

        # Initialize healing strategies
        self._setup_healing_strategies()

    def _setup_healing_strategies(self):
        """Set up self-healing strategies for common issues."""
        self.healing_strategies = {
            'missing_required': self._heal_missing_field,
            'invalid_type': self._heal_invalid_type,
            'out_of_range': self._heal_range_violation,
            'malformed_data': self._heal_generic_error  # Use generic for now
        }

    async def load_configuration(self, source_params: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration with defensive error handling."""
        start_time = time.time()

        if not self.circuit_breaker.can_attempt_operation():
            self.logger.warning("Circuit breaker open, using cached config")
            return self._get_cached_or_default_config()

        try:
            self.metrics['loads'] += 1

            # Load based on source type
            if self.config_source == ConfigSourceType.FILE:
                config_data = await self._load_from_file(source_params)
            elif self.config_source == ConfigSourceType.MEMORY:
                config_data = source_params.get('data', {})
            else:
                # For other sources, use provided data
                config_data = source_params.get('data', {})

            # Create immutable config object
            immutable_config = ImmutableConfig(
                data=config_data,
                validation_hash=str(hash(str(config_data))),
                last_validated=datetime.now(),
                source_info={'source': self.config_source.value, 'params': source_params}
            )

            # Cache the successful result
            cache_key = self._get_cache_key(source_params)
            self.config_cache[cache_key] = immutable_config

            self.circuit_breaker.record_success()

            # Track performance
            duration = (time.time() - start_time) * 1000
            self.performance_metrics.append(duration)
            self.operations_count += 1

            return config_data

        except Exception as e:
            self.circuit_breaker.record_failure()
            self.errors_encountered += 1
            self.metrics['errors'] += 1
            self.logger.error(f"Config load failed: {e}")

            # Return cached or default config
            return self._get_cached_or_default_config()

    async def _load_from_file(self, source_params: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration from file with error handling."""
        file_path = source_params.get('path', 'config.json')

        try:
            if not Path(file_path).exists():
                self.logger.warning(f"Config file not found: {file_path}")
                return {}

            with open(file_path, 'r') as f:
                return json.load(f)

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error reading config file: {e}")
            return {}

    def _get_cached_or_default_config(self) -> Dict[str, Any]:
        """Get cached config or safe defaults."""
        if self.config_cache:
            # Return the most recent cached config
            latest = max(self.config_cache.values(), key=lambda c: c.last_validated)
            self.metrics['cache_hits'] += 1
            return latest.data

        # Return safe defaults
        self.metrics['cache_misses'] += 1
        return {'app_name': 'default_app', 'port': 8080, 'debug': False}

    def _get_cache_key(self, source_params: Dict[str, Any]) -> str:
        """Generate cache key for source parameters."""
        return str(hash(str(sorted(source_params.items()))))

    async def validate_configuration(self, config: Dict[str, Any], rules: List[ConfigValidationRule]) -> ConfigValidationResult:
        """Multi-layer validation with caching."""
        start_time = time.time()
        self.metrics['validations'] += 1

        # Check validation cache
        config_hash = str(hash(str(config)))
        rules_hash = str(hash(str([(r.field_path, r.rule_type) for r in rules])))
        cache_key = f"{config_hash}_{rules_hash}"

        if cache_key in self.validation_cache:
            self.metrics['cache_hits'] += 1
            return self.validation_cache[cache_key]

        errors = []
        warnings = []
        auto_fixes_applied = []

        # Validate each rule
        for rule in rules:
            try:
                result = await self._validate_single_rule(config, rule)

                if result['errors']:
                    errors.extend(result['errors'])
                if result['warnings']:
                    warnings.extend(result['warnings'])
                if result['fixes']:
                    auto_fixes_applied.extend(result['fixes'])

            except Exception as e:
                errors.append(f"Validation rule error for {rule.field_path}: {e}")
                self.logger.error(f"Rule validation failed: {e}")

        # Calculate systematic score
        total_rules = len(rules)
        passed_rules = total_rules - len(errors)
        base_score = passed_rules / total_rules if total_rules > 0 else 1.0

        # Bonus for auto-fixes
        auto_fix_bonus = min(0.1, len(auto_fixes_applied) * 0.02)
        systematic_score = min(1.0, base_score + auto_fix_bonus)

        result = ConfigValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            auto_fixes_applied=auto_fixes_applied,
            systematic_score=systematic_score
        )

        # Cache the result
        self.validation_cache[cache_key] = result

        # Track performance
        duration = (time.time() - start_time) * 1000
        self.performance_metrics.append(duration)
        self.operations_count += 1

        return result

    async def _validate_single_rule(self, config: Dict[str, Any], rule: ConfigValidationRule) -> Dict[str, List[str]]:
        """Validate a single configuration rule."""
        value = self._get_nested_value(config, rule.field_path)
        result = {'errors': [], 'warnings': [], 'fixes': []}

        if rule.rule_type == 'required':
            if value is None or (isinstance(value, str) and not value):
                result['errors'].append(rule.error_message)

        elif rule.rule_type == 'type':
            expected_type = rule.parameters.get('expected')
            if value is not None and expected_type and not isinstance(value, expected_type):
                result['errors'].append(rule.error_message)

        elif rule.rule_type == 'range':
            if isinstance(value, (int, float)):
                min_val = rule.parameters.get('min')
                max_val = rule.parameters.get('max')

                if min_val is not None and value < min_val:
                    result['errors'].append(rule.error_message)
                elif max_val is not None and value > max_val:
                    result['errors'].append(rule.error_message)

        return result

    def _get_nested_value(self, config: Dict[str, Any], path: str):
        """Get nested configuration value by dot-notation path."""
        keys = path.split('.')
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    async def auto_heal_configuration(self, config: Dict[str, Any], validation_result: ConfigValidationResult) -> Dict[str, Any]:
        """Auto-heal configuration issues using strategic patterns."""
        if validation_result.is_valid:
            return config

        start_time = time.time()
        self.metrics['heals'] += 1

        healed_config = copy.deepcopy(config)
        fixes_applied = []

        # Apply healing strategies
        for error in validation_result.errors:
            try:
                # Determine healing strategy based on error pattern
                if 'required' in error.lower():
                    fix_result = await self._heal_missing_field(healed_config, error)
                elif 'type' in error.lower() or 'boolean' in error.lower():
                    fix_result = await self._heal_invalid_type(healed_config, error)
                elif 'range' in error.lower() or 'between' in error.lower():
                    fix_result = await self._heal_range_violation(healed_config, error)
                else:
                    fix_result = await self._heal_generic_error(healed_config, error)

                if fix_result:
                    fixes_applied.append(fix_result)
                    self.auto_fixes_applied += 1

            except Exception as e:
                self.logger.error(f"Healing failed for error '{error}': {e}")

        # Track performance
        duration = (time.time() - start_time) * 1000
        self.performance_metrics.append(duration)
        self.operations_count += 1

        self.logger.info(f"Applied {len(fixes_applied)} auto-fixes")
        return healed_config

    async def _heal_missing_field(self, config: Dict[str, Any], error: str) -> Optional[str]:
        """Heal missing required fields."""
        # Common field defaults
        defaults = {
            'app_name': 'default_app',
            'port': 8080,
            'debug': False,
            'database.host': 'localhost',
            'database.port': 5432
        }

        for field, default_value in defaults.items():
            if field in error or field.split('.')[-1] in error:
                self._set_nested_value(config, field, default_value)
                return f"Set {field} = {default_value}"

        return None

    async def _heal_invalid_type(self, config: Dict[str, Any], error: str) -> Optional[str]:
        """Heal invalid type issues."""
        # Type coercion strategies
        if 'debug' in error and 'boolean' in error:
            # Find and fix debug field
            if 'debug' in config:
                old_value = config['debug']
                if isinstance(old_value, str):
                    config['debug'] = old_value.lower() in ['true', '1', 'yes', 'on']
                else:
                    config['debug'] = bool(old_value)
                return f"Converted debug from {old_value} to {config['debug']}"

        return None

    async def _heal_range_violation(self, config: Dict[str, Any], error: str) -> Optional[str]:
        """Heal range violation issues."""
        if 'port' in error:
            if 'port' in config:
                old_value = config['port']
                # Clamp to valid range
                if config['port'] > 65535:
                    config['port'] = 8080
                elif config['port'] < 1000:
                    config['port'] = 8080
                return f"Fixed port from {old_value} to {config['port']}"

        return None

    async def _heal_generic_error(self, config: Dict[str, Any], error: str) -> Optional[str]:
        """Generic healing for unspecified errors."""
        # Log for analysis but don't change anything
        self.logger.warning(f"No specific healing strategy for: {error}")
        return None

    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any):
        """Set nested configuration value by dot-notation path."""
        keys = path.split('.')
        current = config

        # Navigate to parent
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set final value
        current[keys[-1]] = value

    async def persist_configuration(self, config: Dict[str, Any], target_params: Dict[str, Any]) -> bool:
        """Persist configuration with validation."""
        try:
            if self.config_source == ConfigSourceType.FILE:
                file_path = target_params.get('path', 'config.json')
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=2)
                return True

            # For other sources, just return success (mock)
            return True

        except Exception as e:
            self.logger.error(f"Failed to persist config: {e}")
            return False

    async def monitor_configuration_health(self) -> Dict[str, Any]:
        """Monitor configuration health and metrics."""
        return {
            'source_type': self.config_source.value,
            'validation_level': self.validation_level.value,
            'circuit_breaker_open': self.circuit_breaker.is_open,
            'failure_count': self.circuit_breaker.failure_count,
            'cache_size': len(self.config_cache),
            'metrics': self.metrics,
            'systematic_score': self.calculate_systematic_score(),
            'operations_count': self.operations_count,
            'errors_encountered': self.errors_encountered,
            'auto_fixes_applied': self.auto_fixes_applied
        }

# Test Node A's Implementation
async def test_node_a_solution():
    """Test Node A's defensive architecture solution."""
    print("🔧 Testing Node A's Defensive Architecture Solution")
    print("="*60)

    # Import the tester
    from emergent_evolution_challenge import ConfigManagerChallengeTester

    # Create Node A's implementation
    manager = DefensiveConfigManager(ConfigSourceType.MEMORY, ValidationLevel.STRICT)

    # Create and run tests
    tester = ConfigManagerChallengeTester()
    results = await tester.test_implementation(manager)

    # Display results
    print(f"\n🎯 Node A Results:")
    print(f"   Implementation: {results['implementation']}")
    print(f"   Final Score: {results['final_systematic_score']:.3f}")
    print(f"   Target Met: {'✅ YES' if results['passes_target'] else '❌ NO'}")

    print(f"\n📊 Scenario Breakdown:")
    for scenario in results['scenario_results']:
        score = scenario.get('score', 0.0)
        duration = scenario.get('duration_ms', 0.0)
        print(f"   {scenario['scenario']:20}: {score:.3f} ({duration:.1f}ms)")

    # Display architectural insights
    health = await manager.monitor_configuration_health()
    print(f"\n🏗️  Architectural Insights:")
    print(f"   Circuit Breaker: {'Open' if health['circuit_breaker_open'] else 'Closed'}")
    print(f"   Cache Efficiency: {health['metrics']['cache_hits']}/{health['metrics']['cache_hits'] + health['metrics']['cache_misses']}")
    print(f"   Auto-Fixes: {health['auto_fixes_applied']}")
    print(f"   Error Rate: {health['errors_encountered']}/{health['operations_count']}")

    return results

if __name__ == "__main__":
    # Test Node A's solution
    results = asyncio.run(test_node_a_solution())
    print(f"\n✅ Node A testing complete: {results['final_systematic_score']:.3f}")