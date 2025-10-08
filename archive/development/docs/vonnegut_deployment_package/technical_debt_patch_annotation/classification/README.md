# Technical Debt Classification and Impact Assessment

This module implements comprehensive technical debt classification algorithms, severity assessment, component-level debt aggregation, and automated alerting for patch management and cleanup prioritization.

## Components

### DebtClassifier
Main technical debt classification system with automated alerting capabilities.

**Key Features:**
- Comprehensive patch classification and assessment
- Automated threshold-based alerting
- Alert management (acknowledgment, clearing)
- Integration with impact assessment engine

### ImpactAssessmentEngine
Engine for assessing technical debt impact and generating insights.

**Key Features:**
- Component impact assessment
- Maintenance burden calculation
- Debt hotspot detection
- Risk assessment generation

## Data Models

### ComponentImpact
Assessment of technical debt impact on a specific component including:
- Patch count and distribution by severity
- Total debt score and maintenance burden
- Risk factors and recommended actions
- Component type classification

### DebtHotspot
Identification of high-debt areas requiring immediate attention:
- Hotspot types: high_concentration, critical_patches, aging_debt
- Severity scoring and priority recommendations
- Business and technical risk assessment

### MaintenanceBurden
Assessment of ongoing maintenance cost for patches:
- Daily maintenance cost calculation
- Complexity and integration factors
- Testing overhead and documentation debt
- Burden categorization (low, moderate, high, severe)

### RiskAssessment
Overall technical debt risk profile for the system:
- Total debt score and risk level
- Top risk factors and components at risk
- Recommended actions and cleanup timeline

## Requirements Compliance

This implementation addresses all requirements 2.1-2.5:

### Requirement 2.1: Technical Debt Severity Levels ✓
- Supports all severity levels: Low, Medium, High, Critical
- Proper enum-based classification system

### Requirement 2.2: Architectural Impact and Maintenance Burden ✓
- Severity assessment considers architectural impact through bypass type multipliers
- Maintenance burden calculation includes complexity, integration dependencies, testing overhead
- Component type classification affects impact scoring

### Requirement 2.3: Core System Priority Flagging ✓
- Automatic component type classification based on naming patterns
- Core systems receive higher priority in recommendations
- Risk multipliers applied based on component criticality

### Requirement 2.4: Component-Level Aggregation ✓
- Patches grouped by component for impact assessment
- Aggregated debt scoring and patch distribution analysis
- Component-specific recommendations and risk factors

### Requirement 2.5: Automated Threshold-Based Alerts ✓
- Configurable alert thresholds for various metrics
- Multiple alert types: component debt score, critical patch count, total patches, overdue patches
- Alert severity levels: INFO, WARNING, CRITICAL, EMERGENCY
- Alert management with acknowledgment and clearing capabilities

## Usage Examples

### Basic Classification
```python
from debt_classifier import DebtClassifier

classifier = DebtClassifier()
results = classifier.classify_patches(patches)
print(f"Risk Level: {results['risk_assessment']['risk_level']}")
```

### Component Impact Analysis
```python
from debt_classifier import ImpactAssessmentEngine

engine = ImpactAssessmentEngine()
impact = engine.assess_component_impact("api_service", component_patches)
print(f"Debt Score: {impact.total_debt_score}")
```

### Alert Management
```python
# Get active alerts
alerts = classifier.get_active_alerts()

# Acknowledge an alert
classifier.acknowledge_alert(alert_id)

# Clear acknowledged alerts
cleared_count = classifier.clear_acknowledged_alerts()
```

## Configuration

The system supports configuration through a config dictionary:

```python
config = {
    'alert_thresholds': {
        'component_debt_score': 15.0,
        'critical_patch_count': 2,
        'total_patch_count': 20,
        'overdue_patch_count': 5,
        'maintenance_burden_score': 25.0
    },
    'notifications_enabled': True,
    'notification_channels': ['log']
}
```

## Testing

Run the demo to see the system in action:
```bash
python3 demo_debt_classification.py
```

Run requirements compliance tests:
```bash
python3 test_requirements_compliance.py
```

## Integration

This module integrates with:
- **ReflectiveModule pattern** for observability and health monitoring
- **Core models** for patch annotation data structures
- **Prometheus metrics** for monitoring and alerting
- **Structured logging** for audit trails

The classification system provides the foundation for systematic technical debt management and cleanup prioritization.