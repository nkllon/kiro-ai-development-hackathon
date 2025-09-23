# Engine Domain Architecture

**Total Classes**: 59

## Section 1

```mermaid
classDiagram
    class AIErrorUnderstandingEngine {
        +__init__()
        +analyze_error_with_ai()
        +classify_error_category()
        +assess_complexity_level()
        +determine_fix_strategy()
    }
    class AppEngineAdapter {
        +__init__()
        +init_poolmanager()
    }
    class AppEngineMROHack {
        +__init__()
    }
    class AsyncEngine {
        +__init__()
        +_proxied()
        +_regenerate_proxy_for_target()
        +connect()
        +execution_options()
    }
    class CompetitiveIntelligenceEngine {
        +__init__()
        +monitor_competitors()
        +analyze_market_trends()
        +generate_differentiation_strategy()
        +calculate_competitive_advantage()
    }
    class ConcurrentProcessingEngine {
        +__init__()
        +_setup_logging()
        +_initialize_execution_pools()
        +_start_worker_threads()
        +_worker_loop()
    }
    class ConsensusEngine {
        +__init__()
        +get_resolution_methods()
    }
    class CreateEnginePlugin {
        +__init__()
        +update_url()
        +handle_dialect_kwargs()
        +handle_pool_kwargs()
        +engine_created()
    }
    AppEngineAdapter --|> AppEngineMROHack
```

## Section 2

```mermaid
classDiagram
    class DataEnrichmentEngine {
        +__init__()
        +load_session_data()
        +load_telemetry_data()
        +analyze_navigation_patterns()
        +analyze_form_completion_patterns()
    }
    class DebuggingEngine {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethods {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethodsDebuggingengine {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethodsDebuginfo {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethodsDebuglevel {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethodsDiagnosticresult {
        +__init__()
        +get_info()
    }
    class DecisionEngine {
        +__init__()
        +was_selected()
        +was_ignored()
        +make_decision()
        +decision_for()
    }
```

## Section 3

```mermaid
classDiagram
    class DuplicateConsolidationEngine {
        +__init__()
        +load_analysis_results()
        +backup_file()
        +consolidate_versioned_files()
        +consolidate_same_directory()
    }
    class Engine {
        +__init__()
        +_lru_size_alert()
        +engine()
        +clear_compiled_cache()
        +update_execution_options()
    }
    class FieldModificationEngine {
        +__init__()
        +request_field_modification()
        +_validate_safety_and_sync()
        +_apply_code_changes()
        +_run_tests()
    }
    class FutureEngineMixin {
    }
    class InsecureAppEngineAdapter {
        +__init__()
    }
    class InspectionEngine {
        +__init__()
        +reload_module()
        +expr_type()
        +object_type()
        +collect_attrs()
    }
    class IntelligenceEngine {
        +__init__()
        +get_info()
    }
    class IntelligenceEngineCore {
        +__init__()
        +get_info()
    }
```

## Section 4

```mermaid
classDiagram
    class IntelligenceEngineServices {
        +__init__()
        +get_info()
    }
    class InterfaceConsolidationEngine {
        +__init__()
        +get_info()
    }
    class MatchingEngine {
        +__init__()
        +embeddings()
        +_validate_google_libraries_installation()
        +add_texts()
        +_upload_to_gcs()
    }
    class MockEngineStrategy {
    }
    class ModelDrivenIntelligenceEngine {
        +__init__()
        +get_info()
    }
    class ModelDrivenIntelligenceEngineCore {
        +__init__()
        +get_info()
    }
    class ModelDrivenIntelligenceEngineProcessing {
        +__init__()
        +get_info()
    }
    class ModelDrivenIntelligenceEngineUtils {
        +__init__()
        +get_info()
    }
```

## Section 5

```mermaid
classDiagram
    class OptionEngine {
        +update_execution_options()
    }
    class OptionEngineMixin {
        +__init__()
        +update_execution_options()
    }
    class QueryEngine {
        +__init__()
        +get_info()
    }
    class QueryEngineCore {
        +__init__()
        +get_info()
    }
    class QueryEngineCoreCore {
        +__init__()
        +get_info()
    }
    class QueryEngineProcessing {
        +__init__()
        +get_info()
    }
    class QueryEngineServices {
        +__init__()
        +get_info()
    }
    class QueryEngineServicesCore {
        +__init__()
        +get_info()
    }
    OptionEngine --|> OptionEngineMixin
```

## Section 6

```mermaid
classDiagram
    class QueryEngineServicesCoreCore {
        +__init__()
        +get_info()
    }
    class QueryEngineServicesProcessing {
        +__init__()
        +get_info()
    }
    class QueryEngineServicesServices {
        +__init__()
        +get_info()
    }
    class QueryEngineServicesServicesCore {
        +__init__()
        +get_info()
    }
    class QueryEngineServicesServicesProcessing {
        +__init__()
        +get_info()
    }
    class RecoveryEngine {
        +__init__()
        +get_supported_delusion_types()
        +can_handle_delusion()
    }
    class RepositoryRefactoringEngine {
        +__init__()
        +_load_domain_patterns()
        +analyze_repository()
        +_analyze_file()
        +_classify_domain()
    }
    class ResourceAllocationEngine {
        +optimize_allocation()
        +allocate_for_response()
    }
```

## Section 7

```mermaid
classDiagram
    class SemanticDiffEngine {
        +__init__()
        +diff_spores()
    }
    class SuggestionEngine {
        +__init__()
        +suggest()
        +suggest_callsites()
        +restore_after()
        +with_export_types()
    }
    class SuperiorityEngine {
        +__init__()
        +get_info()
    }
    class SuperiorityEngineCore {
        +__init__()
        +get_info()
    }
    class SuperiorityEngineServices {
        +__init__()
        +get_info()
    }
    class TypeEngine {
        +evaluates_none()
        +copy()
        +copy_value()
        +literal_processor()
        +bind_processor()
    }
    class TypeEngineMixin {
    }
    class VolcEngineMaasBase {
        +validate_environment()
        +_default_params()
    }
```

## Section 8

```mermaid
classDiagram
    class VolcEngineMaasChat {
        +_llm_type()
        +is_lc_serializable()
        +_identifying_params()
        +_convert_prompt_msg_params()
        +_stream()
    }
    class VolcEngineMaasLLM {
        +_llm_type()
        +_convert_prompt_msg_params()
        +_call()
        +_stream()
    }
    class _AppEnginePoolManager {
        +__init__()
        +connection_from_url()
        +clear()
    }
```

## All Classes in Domain

- `AIErrorUnderstandingEngine`
- `AppEngineAdapter`
- `AppEngineMROHack`
- `AsyncEngine`
- `CompetitiveIntelligenceEngine`
- `ConcurrentProcessingEngine`
- `ConsensusEngine`
- `CreateEnginePlugin`
- `DataEnrichmentEngine`
- `DebuggingEngine`
- `DebuggingEngineMethods`
- `DebuggingEngineMethodsDebuggingengine`
- `DebuggingEngineMethodsDebuginfo`
- `DebuggingEngineMethodsDebuglevel`
- `DebuggingEngineMethodsDiagnosticresult`
- `DecisionEngine`
- `DuplicateConsolidationEngine`
- `Engine`
- `FieldModificationEngine`
- `FutureEngineMixin`
- `InsecureAppEngineAdapter`
- `InspectionEngine`
- `IntelligenceEngine`
- `IntelligenceEngineCore`
- `IntelligenceEngineServices`
- `InterfaceConsolidationEngine`
- `MatchingEngine`
- `MockEngineStrategy`
- `ModelDrivenIntelligenceEngine`
- `ModelDrivenIntelligenceEngineCore`
- `ModelDrivenIntelligenceEngineProcessing`
- `ModelDrivenIntelligenceEngineUtils`
- `OptionEngine`
- `OptionEngineMixin`
- `QueryEngine`
- `QueryEngineCore`
- `QueryEngineCoreCore`
- `QueryEngineProcessing`
- `QueryEngineServices`
- `QueryEngineServicesCore`
- `QueryEngineServicesCoreCore`
- `QueryEngineServicesProcessing`
- `QueryEngineServicesServices`
- `QueryEngineServicesServicesCore`
- `QueryEngineServicesServicesProcessing`
- `RecoveryEngine`
- `RepositoryRefactoringEngine`
- `ResourceAllocationEngine`
- `SemanticDiffEngine`
- `SuggestionEngine`
- `SuperiorityEngine`
- `SuperiorityEngineCore`
- `SuperiorityEngineServices`
- `TypeEngine`
- `TypeEngineMixin`
- `VolcEngineMaasBase`
- `VolcEngineMaasChat`
- `VolcEngineMaasLLM`
- `_AppEnginePoolManager`
