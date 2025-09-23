# RCA Domain Architecture

**Total Classes**: 82

## Section 1

```mermaid
classDiagram
    class ArthurCallbackHandler {
        +__init__()
        +from_credentials()
        +on_llm_start()
        +on_llm_end()
        +on_chain_start()
    }
    class AsyncFinalIteratorCallbackHandler {
        +append_to_last_tokens()
        +check_if_answer_reached()
        +__init__()
    }
    class AsyncIteratorCallbackHandler {
        +always_verbose()
        +__init__()
    }
    class ErrorCategory {
    }
    class EvaluatorCallbackHandler {
        +__init__()
        +_evaluate_in_project()
        +_select_eval_results()
        +_log_evaluation_feedback()
        +_persist_run()
    }
    class FiddlerCallbackHandler {
        +__init__()
        +custom_features()
        +_publish_events()
        +on_llm_start()
        +on_llm_end()
    }
    class LLMonitorCallbackHandler {
        +__init__()
        +on_llm_start()
        +on_chat_model_start()
        +on_llm_end()
        +on_tool_start()
    }
    class LetterCase {
    }
    AsyncFinalIteratorCallbackHandler --|> AsyncIteratorCallbackHandler
```

## Section 2

```mermaid
classDiagram
    class LoaderCallableStatus {
    }
    class NetRCAuth {
        +__init__()
        +auth_flow()
        +_build_auth_header()
    }
    class ProgressBarCallback {
        +__init__()
        +increment()
        +_print_bar()
        +on_chain_error()
        +on_chain_end()
    }
    class PromptLayerCallbackHandler {
        +__init__()
        +on_chat_model_start()
        +on_llm_start()
        +on_llm_end()
        +_convert_message_to_dict()
    }
    class RCAAnalyzer {
        +__init__()
        +analyze_issue()
        +_identify_root_causes()
        +_identify_contributing_factors()
        +_generate_recommendations()
    }
    class RCACategory {
    }
    class RCAEngine {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class RCAErrorHandler {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
```

## Section 3

```mermaid
classDiagram
    class RCAPatternAnalyzer {
        +__init__()
        +_setup_analyzer_logging()
        +analyze_failure_pattern()
        +_analyze_logging_deficiencies()
        +_analyze_profiling_deficiencies()
    }
    class RCAPerformanceMonitor {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class RCAReportGenerator {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class RCAResult {
    }
    class RCASeverity {
    }
    class RCAStatus {
    }
    class RCATimeoutHandler {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class RcaAnalyzerCore {
        +__init__()
        +get_info()
    }
```

## Section 4

```mermaid
classDiagram
    class RcaAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class RcaEngineCore {
        +__init__()
        +get_info()
    }
    class RcaEngineCoreCore {
        +__init__()
        +get_info()
    }
    class RcaEngineServices {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesCore {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesCoreCore {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesServices {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesServicesCore {
        +__init__()
        +get_info()
    }
```

## Section 5

```mermaid
classDiagram
    class RcaEngineServicesServicesUtils {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesServicesValidation {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesUtils {
        +__init__()
        +get_info()
    }
    class RcaEngineServicesValidation {
        +__init__()
        +get_info()
    }
    class RcaEngineUtils {
        +__init__()
        +get_info()
    }
    class RcaEngineValidation {
        +__init__()
        +get_info()
    }
    class RcaIntegrationCore {
        +__init__()
        +get_info()
    }
    class RcaIntegrationCoreCore {
        +__init__()
        +get_info()
    }
```

## Section 6

```mermaid
classDiagram
    class RcaIntegrationModels {
        +__init__()
        +get_info()
    }
    class RcaIntegrationProcessing {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServices {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesCore {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesCoreCore {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesProcessing {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesServices {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesServicesCore {
        +__init__()
        +get_info()
    }
```

## Section 7

```mermaid
classDiagram
    class RcaIntegrationServicesServicesProcessing {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesServicesValidation {
        +__init__()
        +get_info()
    }
    class RcaIntegrationServicesValidation {
        +__init__()
        +get_info()
    }
    class RcaIntegrationValidation {
        +__init__()
        +get_info()
    }
    class RcaPatternAnalyzerCore {
        +__init__()
        +get_info()
    }
    class RcaPatternAnalyzerCoreCore {
        +__init__()
        +get_info()
    }
    class RcaPatternAnalyzerCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class RcaPatternAnalyzerCoreProcessing {
        +__init__()
        +get_info()
    }
```

## Section 8

```mermaid
classDiagram
    class RcaPatternAnalyzerProcessing {
        +__init__()
        +get_info()
    }
    class RcaReportGeneratorCore {
        +__init__()
        +get_info()
    }
    class RcaReportGeneratorCoreCore {
        +__init__()
        +get_info()
    }
    class RcaReportGeneratorCoreCoreUtils {
        +__init__()
        +get_info()
    }
    class RcaReportGeneratorCoreUtils {
        +__init__()
        +get_info()
    }
    class RcaReportGeneratorUtils {
        +__init__()
        +get_info()
    }
    class RegisterCallableInfo {
    }
    class RootCause {
    }
```

## Section 9

```mermaid
classDiagram
    class RootCauseType {
    }
    class RunCollectorCallbackHandler {
        +__init__()
        +_persist_run()
    }
    class SageMakerCallbackHandler {
        +__init__()
        +_reset()
        +on_llm_start()
        +on_llm_new_token()
        +on_llm_end()
    }
    class SystemicRCAAnalyzer {
        +__init__()
        +analyze_syntax_error_patterns()
        +analyze_automated_modification_patterns()
        +analyze_compliance_monitoring_failures()
        +identify_root_causes()
    }
    class TestRCAIntegrationEngine {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class TestRCAReportData {
    }
    class TestRCASummaryData {
    }
    class TestingRCAFrameworkInterface {
        +__init__()
        +execute_comprehensive_rca()
        +trigger_automated_resolution()
        +execute_integrated_testing()
        +monitor_system_health()
    }
```

## Section 10

```mermaid
classDiagram
    class TestingRcaFrameworkCore {
        +__init__()
        +get_info()
    }
    class TestingRcaFrameworkCoreCore {
        +__init__()
        +get_info()
    }
    class TestingRcaFrameworkCoreCoreValidation {
        +__init__()
        +get_info()
    }
    class TestingRcaFrameworkCoreValidation {
        +__init__()
        +get_info()
    }
    class TestingRcaFrameworkValidation {
        +__init__()
        +get_info()
    }
    class UnifiedTestingRcaFrameworkCompatibility {
        +__init__()
        +get_info()
    }
    class _HybridComparatorCallableType {
        +__call__()
    }
    class _HybridExprCallableType {
        +__call__()
    }
```

## Section 11

```mermaid
classDiagram
    class _InstallLoaderCallableProto {
        +__call__()
    }
    class _LoaderCallable {
        +__call__()
    }
```

## All Classes in Domain

- `ArthurCallbackHandler`
- `AsyncFinalIteratorCallbackHandler`
- `AsyncIteratorCallbackHandler`
- `ErrorCategory`
- `EvaluatorCallbackHandler`
- `FiddlerCallbackHandler`
- `LLMonitorCallbackHandler`
- `LetterCase`
- `LoaderCallableStatus`
- `NetRCAuth`
- `ProgressBarCallback`
- `PromptLayerCallbackHandler`
- `RCAAnalyzer`
- `RCACategory`
- `RCAEngine`
- `RCAErrorHandler`
- `RCAPatternAnalyzer`
- `RCAPerformanceMonitor`
- `RCAReportGenerator`
- `RCAResult`
- `RCASeverity`
- `RCAStatus`
- `RCATimeoutHandler`
- `RcaAnalyzerCore`
- `RcaAnalyzerCoreCore`
- `RcaEngineCore`
- `RcaEngineCoreCore`
- `RcaEngineServices`
- `RcaEngineServicesCore`
- `RcaEngineServicesCoreCore`
- `RcaEngineServicesServices`
- `RcaEngineServicesServicesCore`
- `RcaEngineServicesServicesUtils`
- `RcaEngineServicesServicesValidation`
- `RcaEngineServicesUtils`
- `RcaEngineServicesValidation`
- `RcaEngineUtils`
- `RcaEngineValidation`
- `RcaIntegrationCore`
- `RcaIntegrationCoreCore`
- `RcaIntegrationModels`
- `RcaIntegrationProcessing`
- `RcaIntegrationServices`
- `RcaIntegrationServicesCore`
- `RcaIntegrationServicesCoreCore`
- `RcaIntegrationServicesProcessing`
- `RcaIntegrationServicesServices`
- `RcaIntegrationServicesServicesCore`
- `RcaIntegrationServicesServicesProcessing`
- `RcaIntegrationServicesServicesValidation`
- `RcaIntegrationServicesValidation`
- `RcaIntegrationValidation`
- `RcaPatternAnalyzerCore`
- `RcaPatternAnalyzerCoreCore`
- `RcaPatternAnalyzerCoreCoreProcessing`
- `RcaPatternAnalyzerCoreProcessing`
- `RcaPatternAnalyzerProcessing`
- `RcaReportGeneratorCore`
- `RcaReportGeneratorCoreCore`
- `RcaReportGeneratorCoreCoreUtils`
- `RcaReportGeneratorCoreUtils`
- `RcaReportGeneratorUtils`
- `RegisterCallableInfo`
- `RootCause`
- `RootCauseType`
- `RunCollectorCallbackHandler`
- `SageMakerCallbackHandler`
- `SystemicRCAAnalyzer`
- `TestRCAIntegrationEngine`
- `TestRCAReportData`
- `TestRCASummaryData`
- `TestingRCAFrameworkInterface`
- `TestingRcaFrameworkCore`
- `TestingRcaFrameworkCoreCore`
- `TestingRcaFrameworkCoreCoreValidation`
- `TestingRcaFrameworkCoreValidation`
- `TestingRcaFrameworkValidation`
- `UnifiedTestingRcaFrameworkCompatibility`
- `_HybridComparatorCallableType`
- `_HybridExprCallableType`
- `_InstallLoaderCallableProto`
- `_LoaderCallable`
