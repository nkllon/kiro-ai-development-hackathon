# Spec Reconciliation Data Models Documentation

## Overview

This document provides comprehensive documentation for all data models used in the Spec Consistency and Technical Debt Reconciliation System. The models are designed to support the PCOR (Preventive Corrective Action Request) approach for eliminating spec fragmentation while implementing systematic prevention mechanisms.

## Model Categories

### Core Analysis Models

These models represent the primary analysis artifacts used throughout the reconciliation process.

#### SpecAnalysis
**Purpose**: Comprehensive analysis of a single specification
**Usage**: Generated during spec analysis to identify overlaps, conflicts, and consolidation opportunities

```python
spec_analysis = SpecAnalysis(
    spec_id="user-authentication-spec",
    overlapping_specs=["oauth-spec", "session-management-spec"],
    conflicting_requirements=[conflict_report],
    terminology_issues=[terminology_issue],
    consolidation_opportunities=[consolidation_opportunity]
)

# Get analysis insights
overlap_count = spec_analysis.get_overlap_count()
critical_issues = spec_analysis.get_critical_issues_count()
```

**Key Methods**:
- `get_overlap_count()`: Returns number of overlapping specs
- `get_critical_issues_count()`: Returns count of critical issues requiring immediate attention

#### ConsolidationPlan
**Purpose**: Detailed plan for consolidating multiple specs into unified specifications
**Usage**: Created by SpecConsolidator to guide the consolidation process

```python
plan = ConsolidationPlan(
    target_specs=["auth-spec-1", "auth-spec-2"],
    unified_spec_name="unified-authentication-spec",
    requirement_mapping={"REQ-001": "UNIFIED-REQ-001"},
    estimated_effort=40
)

# Plan analysis
duration_days = plan.get_estimated_duration_days()  # 5.0 days
migration_steps = plan.get_total_migration_steps()
```

**Key Methods**:
- `get_total_migration_steps()`: Returns number of migration steps
- `get_estimated_duration_days()`: Converts effort hours to days (8 hours/day)

#### PreventionControl
**Purpose**: Configuration for prevention mechanisms to avoid future fragmentation
**Usage**: Defines governance controls, validation rules, and monitoring

```python
control = PreventionControl(
    control_type=PreventionType.GOVERNANCE,
    trigger_conditions=[trigger_condition],
    validation_rules=[validation_rule],
    name="Overlap Prevention Control"
)

# Check if control should trigger
context = {"overlap_percentage": 0.7}
should_trigger = control.is_triggered(context)
```

**Key Methods**:
- `is_triggered(context)`: Evaluates if control should activate based on context

### Overlap and Conflict Analysis Models

#### OverlapAnalysis
**Purpose**: Comprehensive analysis of overlaps between multiple specs
**Usage**: Generated during multi-spec analysis to identify consolidation opportunities

```python
analysis = OverlapAnalysis(
    spec_pairs=[("spec-a", "spec-b"), ("spec-b", "spec-c")],
    functional_overlaps={"authentication": ["spec-a", "spec-b"]},
    risk_assessment={"spec-a-spec-b": 0.8}
)

# Analysis insights
highest_risk_pairs = analysis.get_highest_risk_pairs()
```

**Key Methods**:
- `get_highest_risk_pairs()`: Returns spec pairs sorted by consolidation risk

#### ConsolidationOpportunity
**Purpose**: Represents a specific opportunity for spec consolidation
**Usage**: Identified during overlap analysis to prioritize consolidation efforts

```python
opportunity = ConsolidationOpportunity(
    target_specs=["spec-1", "spec-2"],
    overlap_percentage=0.75,
    consolidation_type="merge",
    effort_estimate=32,
    risk_level="medium"
)

# Priority calculation
priority_score = opportunity.calculate_priority_score()
```

**Key Methods**:
- `calculate_priority_score()`: Calculates priority based on overlap, effort, and risk

### Conflict and Issue Models

#### ConflictReport
**Purpose**: Documents conflicts between specifications
**Usage**: Generated during conflict detection to track resolution progress

```python
conflict = ConflictReport(
    conflicting_specs=["spec-a", "spec-b"],
    conflict_type="interface_mismatch",
    severity=OverlapSeverity.HIGH,
    description="Conflicting interface definitions",
    suggested_resolution="Standardize on spec-a interface"
)
```

#### TerminologyIssue
**Purpose**: Tracks terminology consistency issues
**Usage**: Identified during terminology validation

```python
issue = TerminologyIssue(
    term="user_account",
    conflicting_definitions={
        "spec-a": "A registered user with authentication credentials",
        "spec-b": "An account holder with billing information"
    },
    severity=DriftSeverity.MEDIUM,
    recommended_unified_definition="A registered user with authentication and account management capabilities"
)
```

#### InterfaceIssue
**Purpose**: Tracks interface consistency issues
**Usage**: Identified during interface compliance checking

```python
issue = InterfaceIssue(
    interface_name="UserRepository",
    conflicting_definitions={
        "spec-a": "interface UserRepository { findById(id: string): User }",
        "spec-b": "interface UserRepository { getUser(userId: number): UserEntity }"
    },
    severity=DriftSeverity.HIGH,
    recommended_standard_interface="interface UserRepository { findById(id: string): User }"
)
```

### Traceability Models

#### TraceabilityLink
**Purpose**: Links original requirements to consolidated requirements
**Usage**: Maintains traceability during consolidation process

```python
link = TraceabilityLink(
    original_spec="legacy-spec",
    original_requirement_id="REQ-001",
    consolidated_spec="unified-spec",
    consolidated_requirement_id="UNIFIED-REQ-001",
    transformation_type="merged",
    rationale="Combined with similar requirement from another spec",
    confidence_score=0.95
)
```

#### TraceabilityMap
**Purpose**: Complete traceability mapping for a consolidation
**Usage**: Tracks all requirement transformations during consolidation

```python
traceability_map = TraceabilityMap(
    consolidation_id="consolidation-001",
    links=[link1, link2],
    impact_analysis={"authentication": ["spec-a", "spec-b"]},
    validation_status={"REQ-001": True, "REQ-002": True}
)

# Completeness tracking
completeness = traceability_map.update_completeness_score()
```

**Key Methods**:
- `update_completeness_score()`: Calculates completeness based on validation status

### Monitoring and Drift Models

#### DriftDetection
**Purpose**: Represents detected drift in specifications
**Usage**: Generated by continuous monitoring to identify consistency degradation

```python
drift = DriftDetection(
    drift_type="terminology_inconsistency",
    severity=DriftSeverity.MEDIUM,
    affected_specs=["spec-a", "spec-b"],
    description="New terminology variations detected",
    detected_at=datetime.now(),
    metrics_before={"consistency_score": 0.95},
    metrics_after={"consistency_score": 0.82}
)

# Drift analysis
magnitude = drift.calculate_drift_magnitude()
```

**Key Methods**:
- `calculate_drift_magnitude()`: Calculates magnitude of drift based on metrics

#### DriftReport
**Purpose**: Comprehensive drift analysis report
**Usage**: Generated periodically to summarize drift status

```python
drift_report = DriftReport(
    report_id="drift-report-001",
    generated_at=datetime.now(),
    overall_drift_score=0.7,
    detected_drifts=[drift1, drift2]
)

# Report analysis
critical_drifts = drift_report.get_critical_drifts()
summary = drift_report.get_drift_summary()
```

**Key Methods**:
- `get_critical_drifts()`: Returns only critical severity drifts
- `get_drift_summary()`: Returns count of drifts by severity level

### Control and Workflow Models

#### TriggerCondition
**Purpose**: Defines conditions that trigger prevention controls
**Usage**: Used in PreventionControl to define when controls activate

```python
condition = TriggerCondition(
    condition_type="threshold",
    condition_expression="consistency_score < 0.8",
    parameters={
        "metric": "consistency_score",
        "threshold": 0.8,
        "operator": "<"
    }
)

# Condition evaluation
context = {"consistency_score": 0.7}
is_triggered = condition.evaluate(context)  # True
```

**Key Methods**:
- `evaluate(context)`: Evaluates condition against provided context

#### ValidationRule
**Purpose**: Defines rules for validating spec content
**Usage**: Used in consistency validation to enforce standards

```python
rule = ValidationRule(
    rule_type="terminology",
    rule_expression="deprecated_term_1|deprecated_term_2",
    error_message="Use of deprecated terminology detected",
    severity="warning"
)

# Content validation
is_valid, message = rule.validate_content("This uses deprecated_term_1")
```

**Key Methods**:
- `validate_content(content)`: Validates content against rule

#### EnforcementAction
**Purpose**: Defines actions to enforce compliance
**Usage**: Executed when validation rules are violated

```python
action = EnforcementAction(
    action_type="warn",
    description="Issue warning for policy violation"
)

# Action execution
result = action.execute(context)
```

**Key Methods**:
- `execute(context)`: Executes the enforcement action

#### MonitoringMetric
**Purpose**: Tracks metrics for monitoring prevention control effectiveness
**Usage**: Used to measure and track system health

```python
metric = MonitoringMetric(
    metric_name="consistency_score",
    metric_type="gauge",
    description="Overall consistency score",
    target_value=0.95
)

# Metric management
metric.update_value(0.92)
is_within_target = metric.is_within_target()  # True
```

**Key Methods**:
- `update_value(new_value)`: Updates metric value and timestamp
- `is_within_target()`: Checks if current value meets target (within 10% tolerance)

### Consistency and Validation Models

#### TerminologyReport
**Purpose**: Reports on terminology consistency across specs
**Usage**: Generated during terminology validation

```python
report = TerminologyReport(
    consistent_terms={"user", "account", "service"},
    inconsistent_terms={"login": ["signin", "logon"]},
    new_terms={"oauth_token"},
    deprecated_terms={"legacy_auth"}
)

# Consistency analysis
score = report.calculate_consistency_score()
```

**Key Methods**:
- `calculate_consistency_score()`: Calculates consistency score based on term ratios

#### ConsistencyMetrics
**Purpose**: Overall consistency metrics for a set of specifications
**Usage**: Generated to assess overall system consistency

```python
metrics = ConsistencyMetrics(
    terminology_score=0.85,
    interface_score=0.90,
    pattern_score=0.80
)

# Overall assessment
overall_score = metrics.calculate_overall_score()
consistency_level = metrics.consistency_level  # ConsistencyLevel.GOOD
```

**Key Methods**:
- `calculate_overall_score()`: Calculates weighted average and determines consistency level

### Workflow Models

#### CorrectionWorkflow
**Purpose**: Automated correction workflow for detected issues
**Usage**: Manages execution of automated corrections

```python
workflow = CorrectionWorkflow(
    workflow_id="workflow-001",
    correction_type="terminology_standardization",
    target_specs=["spec-a", "spec-b"],
    correction_steps=["Identify conflicts", "Apply corrections", "Validate results"]
)

# Workflow management
workflow.add_log_entry("Starting workflow execution")
can_retry = workflow.can_retry()
```

**Key Methods**:
- `add_log_entry(message)`: Adds timestamped entry to execution log
- `can_retry()`: Checks if workflow can be retried (not exceeded max retries)

#### ArchitecturalDecision
**Purpose**: Documents architectural decisions for validation
**Usage**: Tracks architectural decisions and their compliance

```python
decision = ArchitecturalDecision(
    decision_id="ADR-001",
    title="Standardize Authentication Interface",
    description="All authentication services must implement IAuthenticationService",
    rationale="Ensures consistent authentication patterns across services",
    affected_components=["UserService", "AuthService", "TokenService"]
)
```

### Additional Analysis Models

#### RequirementAnalysis
**Purpose**: Detailed analysis of individual requirements
**Usage**: Analyzes requirement quality and characteristics

```python
analysis = RequirementAnalysis(
    requirement_id="REQ-001",
    content="As a user, I want to authenticate using OAuth2...",
    functionality_keywords={"authentication", "oauth2", "security"},
    acceptance_criteria=["User can login with OAuth2 provider"],
    stakeholder_personas=["End User", "Security Administrator"]
)

# Quality assessment
quality_score = analysis.calculate_quality_score()
```

**Key Methods**:
- `calculate_quality_score()`: Calculates quality based on completeness factors

## Model Relationships

### Hierarchical Relationships

```
SpecAnalysis
├── ConflictReport (multiple)
├── TerminologyIssue (multiple)
├── InterfaceIssue (multiple)
├── ConsolidationOpportunity (multiple)
└── PreventionRecommendation (multiple)

ConsolidationPlan
├── InterfaceChange (multiple)
├── TerminologyChange (multiple)
├── MigrationStep (multiple)
└── ValidationCriterion (multiple)

TraceabilityMap
└── TraceabilityLink (multiple)

DriftReport
└── DriftDetection (multiple)

PreventionControl
├── TriggerCondition (multiple)
├── ValidationRule (multiple)
├── EnforcementAction (multiple)
├── EscalationStep (multiple)
└── MonitoringMetric (multiple)
```

### Process Flow Relationships

1. **Analysis Phase**:
   - `SpecAnalysis` → `OverlapAnalysis` → `ConsolidationOpportunity`
   - `ConflictReport`, `TerminologyIssue`, `InterfaceIssue` identified

2. **Planning Phase**:
   - `ConsolidationOpportunity` → `ConsolidationPlan`
   - `MigrationStep`, `ValidationCriterion` defined

3. **Execution Phase**:
   - `ConsolidationPlan` → `TraceabilityMap` → `TraceabilityLink`
   - `CorrectionWorkflow` manages automated corrections

4. **Monitoring Phase**:
   - `DriftDetection` → `DriftReport`
   - `PreventionControl` triggers based on `TriggerCondition`

## Usage Patterns

### Creating Analysis Models

```python
# Start with spec analysis
spec_analysis = SpecAnalysis(spec_id="my-spec")

# Add identified issues
conflict = ConflictReport(
    conflicting_specs=["spec-a", "spec-b"],
    conflict_type="interface_mismatch",
    severity=OverlapSeverity.HIGH
)
spec_analysis.conflicting_requirements.append(conflict)

# Validate and serialize
if spec_analysis.validate():
    json_data = spec_analysis.to_json()
```

### Building Consolidation Plans

```python
# Create consolidation plan from analysis
plan = ConsolidationPlan(
    target_specs=analysis.overlapping_specs,
    unified_spec_name="consolidated-spec"
)

# Add migration steps
step = MigrationStep(
    step_id="step-1",
    description="Merge authentication requirements",
    estimated_effort=8
)
plan.migration_steps.append(step)

# Calculate metrics
duration = plan.get_estimated_duration_days()
```

### Implementing Prevention Controls

```python
# Define trigger condition
condition = TriggerCondition(
    condition_type="threshold",
    condition_expression="overlap > 0.5",
    parameters={"metric": "overlap", "threshold": 0.5, "operator": ">"}
)

# Create prevention control
control = PreventionControl(
    control_type=PreventionType.GOVERNANCE,
    trigger_conditions=[condition],
    name="Overlap Prevention"
)

# Check activation
context = {"overlap": 0.7}
if control.is_triggered(context):
    # Execute enforcement actions
    for action in control.enforcement_actions:
        result = action.execute(context)
```

### Tracking Traceability

```python
# Create traceability links
link = TraceabilityLink(
    original_spec="old-spec",
    original_requirement_id="REQ-001",
    consolidated_spec="new-spec",
    consolidated_requirement_id="NEW-REQ-001",
    transformation_type="merged"
)

# Build traceability map
traceability = TraceabilityMap(
    consolidation_id="consolidation-001",
    links=[link]
)

# Track completeness
traceability.validation_status["REQ-001"] = True
completeness = traceability.update_completeness_score()
```

## Serialization and Persistence

All models inherit from `DataModelMixin` which provides:

### JSON Serialization
```python
# Convert to dictionary
data_dict = model.to_dict()

# Convert to JSON string
json_str = model.to_json()

# Create from dictionary
model = ModelClass.from_dict(data_dict)
```

### Validation
```python
# Validate model instance
is_valid = model.validate()
```

### Special Handling
- **DateTime fields**: Automatically converted to/from ISO format
- **Enum fields**: Serialized as string values
- **Set fields**: Converted to/from lists
- **Path fields**: Converted to/from strings

## Utility Functions

### Model Registry
```python
# Get model class by name
model_class = get_model_class("SpecAnalysis")

# Create instance by name
instance = create_model_instance("SpecAnalysis", spec_id="test")

# Validate all models
results = validate_all_models()
```

## Best Practices

### Model Creation
1. Always validate models after creation
2. Use appropriate enums for type safety
3. Provide meaningful IDs and descriptions
4. Set confidence scores for analysis results

### Relationship Management
1. Use composition over inheritance
2. Maintain bidirectional references where needed
3. Update related models when changes occur
4. Validate relationship consistency

### Serialization
1. Use `to_dict()` for internal processing
2. Use `to_json()` for external APIs
3. Handle datetime and enum serialization properly
4. Validate deserialized models

### Performance
1. Use lazy loading for large collections
2. Cache calculated values where appropriate
3. Batch operations for multiple models
4. Use appropriate data structures for lookups

## Error Handling

### Validation Errors
- Models return `False` from `validate()` on validation failure
- Check logs for specific validation error messages
- Required fields must not be None or empty strings

### Serialization Errors
- Handle JSON serialization errors gracefully
- Provide fallback values for complex types
- Log serialization errors for debugging

### Relationship Errors
- Validate foreign key relationships
- Handle missing related objects gracefully
- Maintain referential integrity during updates

This documentation provides a comprehensive guide to understanding and using the data models in the Spec Reconciliation System. The models are designed to be flexible, extensible, and maintainable while providing strong type safety and validation capabilities.