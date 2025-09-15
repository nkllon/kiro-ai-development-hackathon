# Quality Domain Architecture

**Total Classes**: 38

## Section 1

```mermaid
classDiagram
    class AssessmentCriteria {
    }
    class AssessmentResult {
    }
    class AutomatedQualityGates {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class AutomatedQualityGatesCore {
        +__init__()
        +get_info()
    }
    class AutomatedQualityGatesCoreCore {
        +__init__()
        +get_info()
    }
    class AutomatedQualityGatesCoreCoreUtils {
        +__init__()
        +get_info()
    }
    class AutomatedQualityGatesCoreUtils {
        +__init__()
        +get_info()
    }
    class AutomatedQualityGatesUtils {
        +__init__()
        +get_info()
    }
```

## Section 2

```mermaid
classDiagram
    class CategoryAssessment {
    }
    class CodeQualityAssessmentEngine {
        +__init__()
        +assess_code_quality()
        +validate_code_quality()
        +generate_quality_improvement_plan()
        +_discover_source_files()
    }
    class CodeQualityCore {
        +__init__()
        +get_info()
    }
    class CodeQualityCoreCore {
        +__init__()
        +get_info()
    }
    class CodeQualityEnforcer {
        +__init__()
        +enforce_code_quality()
        +check_ast_parsing()
        +check_import_quality()
        +check_code_structure()
    }
    class CodeQualityExpert {
        +__init__()
        +get_capabilities()
        +validate_confidence()
        +_analyze_python_ast()
        +_analyze_python_lines()
    }
    class CodeQualityIssue {
    }
    class CodeQualityMetric {
    }
```

## Section 3

```mermaid
classDiagram
    class CodeQualityReport {
    }
    class ContentQualityRule {
        +__init__()
        +get_module_info()
        +get_capabilities()
        +get_dependencies()
        +check_health()
    }
    class ContentqualityruleInterface {
        +__init__()
        +get_info()
    }
    class FocusedMilestoneGates {
        +__init__()
        +check_all_gates()
        +check_rdi_compliance_gate()
        +check_size_compliance_gate()
        +check_health_monitoring_gate()
    }
    class ImpactAssessment {
    }
    class JsonEqualityEvaluator {
        +__init__()
        +requires_input()
        +requires_reference()
        +evaluation_name()
        +_parse_json()
    }
    class MilestoneDeliveryGates {
        +__init__()
        +check_all_gates()
        +check_rdi_compliance_gate()
        +check_size_compliance_gate()
        +check_health_monitoring_gate()
    }
    class ModuleAssessment {
    }
```

## Section 4

```mermaid
classDiagram
    class PolygonAggregates {
        +_run()
    }
    class PolygonAggregatesSchema {
    }
    class QualityAssessment {
    }
    class QualityGateConfig {
    }
    class QualityGateResult {
    }
    class QualityGateStatus {
    }
    class QualityGateType {
    }
    class QualityIssue {
    }
```

## Section 5

```mermaid
classDiagram
    class QualityLevel {
    }
    class QualityReport {
    }
    class QualityVisitor {
        +__init__()
        +visit_FunctionDef()
        +visit_ClassDef()
        +_calculate_complexity()
    }
    class RiskAssessmentResult {
    }
    class RiskMitigationAssessment {
    }
    class TechnicalAssessment {
        +__post_init__()
    }
```

## All Classes in Domain

- `AssessmentCriteria`
- `AssessmentResult`
- `AutomatedQualityGates`
- `AutomatedQualityGatesCore`
- `AutomatedQualityGatesCoreCore`
- `AutomatedQualityGatesCoreCoreUtils`
- `AutomatedQualityGatesCoreUtils`
- `AutomatedQualityGatesUtils`
- `CategoryAssessment`
- `CodeQualityAssessmentEngine`
- `CodeQualityCore`
- `CodeQualityCoreCore`
- `CodeQualityEnforcer`
- `CodeQualityExpert`
- `CodeQualityIssue`
- `CodeQualityMetric`
- `CodeQualityReport`
- `ContentQualityRule`
- `ContentqualityruleInterface`
- `FocusedMilestoneGates`
- `ImpactAssessment`
- `JsonEqualityEvaluator`
- `MilestoneDeliveryGates`
- `ModuleAssessment`
- `PolygonAggregates`
- `PolygonAggregatesSchema`
- `QualityAssessment`
- `QualityGateConfig`
- `QualityGateResult`
- `QualityGateStatus`
- `QualityGateType`
- `QualityIssue`
- `QualityLevel`
- `QualityReport`
- `QualityVisitor`
- `RiskAssessmentResult`
- `RiskMitigationAssessment`
- `TechnicalAssessment`
