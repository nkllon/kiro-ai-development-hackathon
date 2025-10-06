# Analysis Domain Architecture

**Total Classes**: 139

## Section 1

```mermaid
classDiagram
    class ASTAnalysisResult {
    }
    class ASTAnalysisRule {
    }
    class AccurateInterfaceAnalyzer {
        +__init__()
        +get_info()
    }
    class ActualBillingAnalyzer {
        +__init__()
        +get_project_info()
        +get_actual_usage()
        +get_cost_estimates()
        +get_high_cost_services()
    }
    class AdjacencyClusterAnalyzer {
        +__init__()
        +add_vector()
        +analyze_adjacency()
        +_calculate_adjacency_matrix()
        +_calculate_vector_similarity()
    }
    class AnalysisConfiguration {
    }
    class AnalysisContext {
        +__post_init__()
    }
    class AnalysisError {
    }
```

## Section 2

```mermaid
classDiagram
    class AnalysisResult {
        +__post_init__()
    }
    class AnalysisState {
        +__init__()
    }
    class AnalysisStatus {
    }
    class AnalysisStrategy {
    }
    class Analyzer {
        +__init__()
        +get_info()
    }
    class AnalyzerCore {
        +__init__()
        +get_info()
    }
    class AnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class ArchitectureAnalysis {
    }
```

## Section 3

```mermaid
classDiagram
    class AsPattern {
        +__init__()
        +accept()
    }
    class AzureAiServicesImageAnalysisTool {
        +validate_environment()
        +_image_analysis()
        +_format_image_analysis_result()
        +_run()
    }
    class AzureCogsImageAnalysisTool {
        +validate_environment()
        +_image_analysis()
        +_format_image_analysis_result()
        +_run()
    }
    class BaseAnalysisVisitor {
        +visit_goto()
        +visit_register_op()
        +visit_assign()
        +visit_assign_multi()
        +visit_set_mem()
    }
    class BasePattern {
        +__new__()
        +__repr__()
        +_submatch()
        +optimize()
        +match()
    }
    class BypassPattern {
    }
    class ClassPattern {
        +__init__()
        +accept()
    }
    class ClusterAnalysis {
        +to_dict()
    }
```

## Section 4

```mermaid
classDiagram
    class CognitiveComplexityAnalyzer {
        +__init__()
        +analyze()
        +_calculate_cognitive_complexity()
        +_analyze_function_cognitive_complexity()
        +_analyze_class_cognitive_complexity()
    }
    class CollaborationPattern {
    }
    class ComparativeAnalysisEngine {
        +__init__()
        +get_info()
    }
    class ComparativeAnalysisEngineCore {
        +__init__()
        +get_info()
    }
    class ComparativeAnalysisEngineServices {
        +__init__()
        +get_info()
    }
    class ComparativeAnalysisResult {
    }
    class ComplexityAnalyzer {
        +analyze()
    }
    class ComprehensiveAnalysisResult {
    }
    CognitiveComplexityAnalyzer --|> ComplexityAnalyzer
```

## Section 5

```mermaid
classDiagram
    class ComprehensiveErrorAnalyzer {
        +__init__()
        +analyze_all_errors()
        +_parse_import_error()
        +_parse_syntax_error()
        +apply_systematic_fixes()
    }
    class ContentAnalyzer {
        +__init__()
        +get_info()
    }
    class ContentAnalyzerCore {
        +__init__()
        +get_info()
    }
    class ContentAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class ContrastAnalyzer {
        +__init__()
        +get_info()
    }
    class ContrastAnalyzerCore {
        +__init__()
        +get_info()
    }
    class ContrastAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class CredentialPattern {
    }
```

## Section 6

```mermaid
classDiagram
    class CriticalPathAnalysis {
    }
    class CriticalPathAnalyzer {
        +__init__()
        +analyze_critical_paths()
        +identify_bottlenecks()
        +calculate_completion_percentage()
        +estimate_remaining_work()
    }
    class CriticalPathAnalyzerCore {
        +__init__()
        +get_info()
    }
    class CriticalPathAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class CuriousPageAnalyzer {
        +__init__()
        +analyze_page()
        +_heuristically_detect_page_type()
        +_find_status_indicators()
        +_find_navigation_elements()
    }
    class CyclomaticComplexityAnalyzer {
        +__init__()
        +analyze()
        +_calculate_cyclomatic_complexity()
        +_analyze_function_complexity()
        +_analyze_class_complexity()
    }
    class DeepErrorAnalysis {
    }
    class DeepErrorAnalyzer {
        +__init__()
        +perform_deep_analysis()
        +_parse_deep_import_error()
        +_parse_deep_syntax_error()
        +_parse_deep_attribute_error()
    }
```

## Section 7

```mermaid
classDiagram
    class DimensionAnalyzer {
        +__init__()
        +count_dimensions()
        +find_orphaned_dimensions()
        +analyze_dimension_relationships()
        +get_dimension_usage_timeline()
    }
    class E2BDataAnalysisTool {
        +__init__()
        +close()
        +uploaded_files_description()
        +_run()
        +run_command()
    }
    class E2BDataAnalysisToolArguments {
    }
    class EcosystemAnalysisResult {
    }
    class EnumCallAnalyzer {
        +__init__()
        +process_enum_call()
        +check_enum_call()
        +build_enum_call_typeinfo()
        +parse_enum_call_args()
    }
    class ErrorAnalysis {
    }
    class ErrorPattern {
    }
    class FailureAnalysis {
    }
```

## Section 8

```mermaid
classDiagram
    class GeminiGCPBillingAnalyzer {
        +__init__()
        +get_1password_credential()
        +setup_credentials()
        +get_project_info()
        +load_billing_data()
    }
    class GitAnalyzer {
        +__init__()
        +get_commits_ahead_of_main()
        +analyze_file_changes()
        +map_changes_to_tasks()
        +analyze()
    }
    class GitIgnorePattern {
        +__init__()
        +_deprecated()
        +pattern_to_regex()
    }
    class GitWildMatchPattern {
        +pattern_to_regex()
        +_translate_segment_glob()
        +escape()
    }
    class GitWildMatchPatternError {
    }
    class HeuristicPattern {
        +__post_init__()
    }
    class HubrisPattern {
    }
    class ImpactAnalysis {
    }
    GitIgnorePattern --|> GitWildMatchPattern
```

## Section 9

```mermaid
classDiagram
    class IndirectVerificationAnalyzer {
        +__init__()
        +analyze_execution_characteristics()
    }
    class IntegratedRequirementsAnalyzer {
        +__init__()
        +get_info()
    }
    class IntegrationPattern {
    }
    class KnownPatternFinder {
        +__init__()
        +_parse_known_pattern()
        +find()
    }
    class LayerAnalysis {
    }
    class LeafPattern {
        +__init__()
        +match()
        +_submatch()
    }
    class LearningPattern {
    }
    class MappingPattern {
        +__init__()
        +accept()
    }
```

## Section 10

```mermaid
classDiagram
    class MetaEcosystemAnalysis {
        +to_dict()
    }
    class ModelAnalysis {
    }
    class ModuleAnalysis {
    }
    class ModuleSizeAnalyzer {
        +__init__()
        +analyze_module()
        +_calculate_priority()
    }
    class MultiDimensionalAnalysis {
    }
    class MultiDimensionalContextAnalyzer {
        +__init__()
        +_build_knowledge_base()
        +_extract_general_techniques()
        +_extract_site_specific_techniques()
        +_extract_page_specific_techniques()
    }
    class MultiDimensionalSessionAnalyzer {
        +__init__()
        +analyze_session_context()
        +_analyze_technical_complexity()
        +_analyze_risk_level()
        +_analyze_uncertainty_level()
    }
    class MultiPerspectiveAnalysis {
    }
```

## Section 11

```mermaid
classDiagram
    class MultiStakeholderAnalysis {
    }
    class NamedTupleAnalyzer {
        +__init__()
        +analyze_namedtuple_classdef()
        +check_namedtuple_classdef()
        +check_namedtuple()
        +store_namedtuple_info()
    }
    class NavigationAnalyzer {
        +__init__()
        +investigate()
        +_identify_interaction_patterns()
    }
    class NegatedPattern {
        +__init__()
        +match()
        +match_seq()
        +generate_matches()
    }
    class NewTypeAnalyzer {
        +__init__()
        +process_newtype_declaration()
        +analyze_newtype_declaration()
        +check_newtype_args()
        +build_newtype_typeinfo()
    }
    class NodePattern {
        +__init__()
        +_submatch()
    }
    class OfficeHoursPattern {
    }
    class OrPattern {
        +__init__()
        +accept()
    }
```

## Section 12

```mermaid
classDiagram
    class OutlierAnalysis {
        +to_dict()
    }
    class OverlapAnalysis {
    }
    class PageAnalysis {
    }
    class PageStructureAnalyzer {
        +__init__()
        +investigate()
        +_analyze_url_pattern()
        +_analyze_title()
        +_count_form_elements()
    }
    class Pattern {
        +accept()
    }
    class PatternAnalysisResult {
    }
    class PatternChecker {
        +__init__()
        +accept()
        +visit_as_pattern()
        +visit_or_pattern()
        +visit_value_pattern()
    }
    class PatternError {
    }
```

## Section 13

```mermaid
classDiagram
    class PatternReport {
    }
    class PatternType {
    }
    class PatternVisitor {
        +visit_as_pattern()
        +visit_or_pattern()
        +visit_value_pattern()
        +visit_singleton_pattern()
        +visit_sequence_pattern()
    }
    class PerformanceAnalyzer {
        +__init__()
        +analyze_performance()
    }
    class PlanningExhaustionAnalyzer {
        +__init__()
        +calculate_planning_effectiveness()
        +generate_planning_cycle()
        +detect_diminishing_returns()
        +run_planning_exhaustion_analysis()
    }
    class PreventionPattern {
    }
    class ProfilingAnalysis {
    }
    class RDIRMAnalysisSystemInterface {
        +__init__()
        +validate_rdi_compliance()
        +analyze_requirements_traceability()
        +validate_design_compliance()
        +generate_quality_metrics()
    }
```

## Section 14

```mermaid
classDiagram
    class RdiRmAnalysisSystemCore {
        +__init__()
        +get_info()
    }
    class RdiRmAnalysisSystemCoreCore {
        +__init__()
        +get_info()
    }
    class RdiRmdddAnalysis {
        +__init__()
        +get_info()
    }
    class RegexPattern {
        +__init__()
        +__eq__()
        +match_file()
        +pattern_to_regex()
    }
    class RepositoryAnalysis {
    }
    class RequirementAnalysis {
    }
    class RequirementsAnalyzer {
        +__init__()
        +get_info()
    }
    class RoundTripHairballAnalyzer {
        +__init__()
        +analyze_expected_vs_actual()
        +_analyze_source_files()
        +_analyze_extracted_models()
        +_analyze_generated_files()
    }
```

## Section 15

```mermaid
classDiagram
    class RuntimePlanningAnalyzer {
        +__init__()
        +analyze_risk_landscape()
        +find_planning_gaps()
        +suggest_next_actions()
        +get_planning_context()
    }
    class SPAAnalysis {
        +to_dict()
    }
    class SelectorPattern {
        +__init__()
        +get_name()
        +match()
    }
    class SemanticAnalyzer {
        +__init__()
        +type()
        +is_stub_file()
        +is_typeshed_stub_file()
        +final_iteration()
    }
    class SemanticAnalyzerCoreInterface {
        +lookup_qualified()
        +lookup_fully_qualified()
        +lookup_fully_qualified_or_none()
        +fail()
        +note()
    }
    class SemanticAnalyzerInterface {
        +lookup()
        +named_type()
        +named_type_or_none()
        +accept()
        +anal_type()
    }
    class SemanticAnalyzerPluginInterface {
        +named_type()
        +builtin_type()
        +named_type_or_none()
        +basic_new_typeinfo()
        +parse_bool()
    }
    class SemanticAnalyzerPreAnalysis {
        +visit_file()
        +visit_func_def()
        +visit_class_def()
        +visit_import_from()
        +visit_import_all()
    }
    SemanticAnalyzer --|> SemanticAnalyzerInterface
    SemanticAnalyzer --|> SemanticAnalyzerPluginInterface
    SemanticAnalyzerInterface --|> SemanticAnalyzerCoreInterface
```

## Section 16

```mermaid
classDiagram
    class SequencePattern {
        +__init__()
        +accept()
    }
    class SessionRecoveryAnalyzer {
        +__init__()
        +analyze_page_similarity()
        +_check_exact_url_match()
        +_check_visual_similarity()
        +_check_url_similarity()
    }
    class SingletonPattern {
        +__init__()
        +accept()
    }
    class SpecialPseudoPattern {
        +__init__()
        +get_name()
        +match()
    }
    class StarredPattern {
        +__init__()
        +accept()
    }
    class StateMutationAnalyzer {
        +__init__()
        +analyze_state_mutations()
    }
    class SuperiorityAnalysis {
    }
    class ThirdWaveErrorAnalyzer {
        +__init__()
        +analyze_remaining_errors()
        +_parse_error_detail()
        +_create_error_patterns()
        +_get_suggested_fix()
    }
```

## Section 17

```mermaid
classDiagram
    class TimingAnalysis {
    }
    class TypeAnalyzerPluginInterface {
        +fail()
        +named_type()
        +analyze_type()
        +analyze_callable_args()
    }
    class TypeArgumentAnalyzer {
        +__init__()
        +visit_mypy_file()
        +visit_func()
        +visit_class_def()
        +visit_block()
    }
    class TypedDictAnalyzer {
        +__init__()
        +analyze_typeddict_classdef()
        +add_keys_and_types_from_base()
        +_parse_typeddict_base()
        +analyze_base_args()
    }
    class URLPattern {
        +__init__()
        +matches()
        +priority()
        +__hash__()
        +__lt__()
    }
    class UnifiedRdiRmAnalysisSystemCompatibility {
        +__init__()
        +get_info()
    }
    class UniversalAnalysisRule {
    }
    class UserBehaviorPattern {
    }
```

## Section 18

```mermaid
classDiagram
    class ValuePattern {
        +__init__()
        +accept()
    }
    class WildcardPattern {
        +__init__()
        +optimize()
        +match()
        +match_seq()
        +generate_matches()
    }
    class _pattern_symbols {
    }
```

## All Classes in Domain

- `ASTAnalysisResult`
- `ASTAnalysisRule`
- `AccurateInterfaceAnalyzer`
- `ActualBillingAnalyzer`
- `AdjacencyClusterAnalyzer`
- `AnalysisConfiguration`
- `AnalysisContext`
- `AnalysisError`
- `AnalysisResult`
- `AnalysisState`
- `AnalysisStatus`
- `AnalysisStrategy`
- `Analyzer`
- `AnalyzerCore`
- `AnalyzerCoreCore`
- `ArchitectureAnalysis`
- `AsPattern`
- `AzureAiServicesImageAnalysisTool`
- `AzureCogsImageAnalysisTool`
- `BaseAnalysisVisitor`
- `BasePattern`
- `BypassPattern`
- `ClassPattern`
- `ClusterAnalysis`
- `CognitiveComplexityAnalyzer`
- `CollaborationPattern`
- `ComparativeAnalysisEngine`
- `ComparativeAnalysisEngineCore`
- `ComparativeAnalysisEngineServices`
- `ComparativeAnalysisResult`
- `ComplexityAnalyzer`
- `ComprehensiveAnalysisResult`
- `ComprehensiveErrorAnalyzer`
- `ContentAnalyzer`
- `ContentAnalyzerCore`
- `ContentAnalyzerCoreCore`
- `ContrastAnalyzer`
- `ContrastAnalyzerCore`
- `ContrastAnalyzerCoreCore`
- `CredentialPattern`
- `CriticalPathAnalysis`
- `CriticalPathAnalyzer`
- `CriticalPathAnalyzerCore`
- `CriticalPathAnalyzerCoreCore`
- `CuriousPageAnalyzer`
- `CyclomaticComplexityAnalyzer`
- `DeepErrorAnalysis`
- `DeepErrorAnalyzer`
- `DimensionAnalyzer`
- `E2BDataAnalysisTool`
- `E2BDataAnalysisToolArguments`
- `EcosystemAnalysisResult`
- `EnumCallAnalyzer`
- `ErrorAnalysis`
- `ErrorPattern`
- `FailureAnalysis`
- `GeminiGCPBillingAnalyzer`
- `GitAnalyzer`
- `GitIgnorePattern`
- `GitWildMatchPattern`
- `GitWildMatchPatternError`
- `HeuristicPattern`
- `HubrisPattern`
- `ImpactAnalysis`
- `IndirectVerificationAnalyzer`
- `IntegratedRequirementsAnalyzer`
- `IntegrationPattern`
- `KnownPatternFinder`
- `LayerAnalysis`
- `LeafPattern`
- `LearningPattern`
- `MappingPattern`
- `MetaEcosystemAnalysis`
- `ModelAnalysis`
- `ModuleAnalysis`
- `ModuleSizeAnalyzer`
- `MultiDimensionalAnalysis`
- `MultiDimensionalContextAnalyzer`
- `MultiDimensionalSessionAnalyzer`
- `MultiPerspectiveAnalysis`
- `MultiStakeholderAnalysis`
- `NamedTupleAnalyzer`
- `NavigationAnalyzer`
- `NegatedPattern`
- `NewTypeAnalyzer`
- `NodePattern`
- `OfficeHoursPattern`
- `OrPattern`
- `OutlierAnalysis`
- `OverlapAnalysis`
- `PageAnalysis`
- `PageStructureAnalyzer`
- `Pattern`
- `PatternAnalysisResult`
- `PatternChecker`
- `PatternError`
- `PatternReport`
- `PatternType`
- `PatternVisitor`
- `PerformanceAnalyzer`
- `PlanningExhaustionAnalyzer`
- `PreventionPattern`
- `ProfilingAnalysis`
- `RDIRMAnalysisSystemInterface`
- `RdiRmAnalysisSystemCore`
- `RdiRmAnalysisSystemCoreCore`
- `RdiRmdddAnalysis`
- `RegexPattern`
- `RepositoryAnalysis`
- `RequirementAnalysis`
- `RequirementsAnalyzer`
- `RoundTripHairballAnalyzer`
- `RuntimePlanningAnalyzer`
- `SPAAnalysis`
- `SelectorPattern`
- `SemanticAnalyzer`
- `SemanticAnalyzerCoreInterface`
- `SemanticAnalyzerInterface`
- `SemanticAnalyzerPluginInterface`
- `SemanticAnalyzerPreAnalysis`
- `SequencePattern`
- `SessionRecoveryAnalyzer`
- `SingletonPattern`
- `SpecialPseudoPattern`
- `StarredPattern`
- `StateMutationAnalyzer`
- `SuperiorityAnalysis`
- `ThirdWaveErrorAnalyzer`
- `TimingAnalysis`
- `TypeAnalyzerPluginInterface`
- `TypeArgumentAnalyzer`
- `TypedDictAnalyzer`
- `URLPattern`
- `UnifiedRdiRmAnalysisSystemCompatibility`
- `UniversalAnalysisRule`
- `UserBehaviorPattern`
- `ValuePattern`
- `WildcardPattern`
- `_pattern_symbols`
