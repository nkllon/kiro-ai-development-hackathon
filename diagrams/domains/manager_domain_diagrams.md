# Manager Domain Architecture

**Total Classes**: 132

## Section 1

```mermaid
classDiagram
    class AWSSecretsManagerSettingsSource {
        +__init__()
        +_load_env_vars()
        +__repr__()
    }
    class AlertManager {
        +__init__()
        +add_alert_handler()
        +get_active_alerts()
        +get_alerts_by_severity()
        +get_alert_history()
    }
    class AsyncCallbackManager {
        +is_async()
        +configure()
    }
    class AsyncCallbackManagerForChainGroup {
        +__init__()
        +copy()
        +merge()
    }
    class AsyncCallbackManagerForChainRun {
        +get_sync()
    }
    class AsyncCallbackManagerForLLMRun {
        +get_sync()
    }
    class AsyncCallbackManagerForRetrieverRun {
        +get_sync()
    }
    class AsyncCallbackManagerForToolRun {
        +get_sync()
    }
    AsyncCallbackManagerForChainGroup --|> AsyncCallbackManager
```

## Section 2

```mermaid
classDiagram
    class AsyncContextManager {
    }
    class AsyncContextManagerMixin {
        +__asynccontextmanager__()
    }
    class AsyncEventContextManager {
        +__init__()
    }
    class AsyncParentRunManager {
        +get_child()
    }
    class AsyncRunManager {
        +get_sync()
    }
    class BanditManager {
        +__init__()
        +get_skipped()
        +get_issue_list()
        +populate_baseline()
        +filter_results()
    }
    class BaseCallbackManager {
        +__init__()
        +copy()
        +merge()
        +is_async()
        +add_handler()
    }
    class BaseRunManager {
        +__init__()
        +get_noop_manager()
    }
    AsyncParentRunManager --|> AsyncRunManager
    AsyncRunManager --|> BaseRunManager
```

## Section 3

```mermaid
classDiagram
    class BranchProtectionManager {
        +__init__()
        +create_develop_branch()
        +setup_branch_protection()
        +get_master_protection_config()
        +get_develop_protection_config()
    }
    class BreakTheGlassProtocolManager {
        +__init__()
        +activate_emergency_protocol()
        +get_protocol_status()
    }
    class BrowserSessionManager {
        +__init__()
        +start_playwright()
        +discover_browsers()
        +start_chrome_with_extensions()
        +connect_to_browser()
    }
    class BuildManager {
        +__init__()
        +dump_stats()
        +use_fine_grained_cache()
        +maybe_swap_for_shadow_path()
        +get_stat()
    }
    class CallbackManager {
        +on_llm_start()
        +on_chat_model_start()
        +on_chain_start()
        +on_tool_start()
        +on_retriever_start()
    }
    class CallbackManagerForChainGroup {
        +__init__()
        +copy()
        +merge()
        +on_chain_end()
        +on_chain_error()
    }
    class CallbackManagerForChainRun {
        +on_chain_end()
        +on_chain_error()
        +on_agent_action()
        +on_agent_finish()
    }
    class CallbackManagerForLLMRun {
        +on_llm_new_token()
        +on_llm_end()
        +on_llm_error()
    }
    CallbackManagerForChainGroup --|> CallbackManager
```

## Section 4

```mermaid
classDiagram
    class CallbackManagerForRetrieverRun {
        +on_retriever_end()
        +on_retriever_error()
    }
    class CallbackManagerForToolRun {
        +on_tool_end()
        +on_tool_error()
    }
    class CallbackManagerMixin {
        +on_llm_start()
        +on_chat_model_start()
        +on_retriever_start()
        +on_chain_start()
        +on_tool_start()
    }
    class ChainManagerMixin {
        +on_chain_end()
        +on_chain_error()
        +on_agent_action()
        +on_agent_finish()
    }
    class ClassManager {
        +deferred_scalar_loader()
        +deferred_scalar_loader()
        +__init__()
        +_update_state()
        +_finalize()
    }
    class ContextManagerMixin {
        +__enter__()
        +__exit__()
        +__contextmanager__()
    }
    class DeadlineManager {
        +__init__()
        +get_info()
    }
    class DeadlineManagerCore {
        +__init__()
        +get_info()
    }
```

## Section 5

```mermaid
classDiagram
    class DeadlineManagerCoreCore {
        +__init__()
        +get_info()
    }
    class DeploymentManager {
        +__init__()
        +get_info()
    }
    class DispatchExtensionManager {
        +map()
        +map_method()
    }
    class DriverManager {
        +__init__()
        +_default_on_load_failure()
        +make_test_instance()
        +_init_plugins()
        +__call__()
    }
    class EmergencyProtocolManager {
        +__init__()
        +activate_emergency_protocols()
        +_prepare_human_intervention_interface()
        +_emergency_fallback()
        +get_protocol_status()
    }
    class EnabledExtensionManager {
        +__init__()
        +_load_one_plugin()
    }
    class EnhancedObservabilityManager {
        +__init__()
        +get_info()
    }
    class EnhancedObservabilityManagerCore {
        +__init__()
        +get_info()
    }
    DispatchExtensionManager --|> EnabledExtensionManager
```

## Section 6

```mermaid
classDiagram
    class EnhancedObservabilityManagerServices {
        +__init__()
        +get_info()
    }
    class EventContextManager {
        +__init__()
        +__enter__()
        +__exit__()
    }
    class EventContextManagerImpl {
        +__init__()
        +future()
    }
    class ExtensionManager {
        +__init__()
        +make_test_instance()
        +_init_attributes()
        +_init_plugins()
        +_extensions_by_name()
    }
    class FindersManager {
        +__init__()
        +find()
    }
    class FineGrainedBuildManager {
        +__init__()
        +update()
        +trigger()
        +flush_cache()
        +update_one()
    }
    class FontManager {
        +__init__()
        +_get_nix_font_path()
        +_create_nix()
        +_get_mac_font_path()
        +_create_mac()
    }
    class GCPStateManager {
        +__init__()
        +load_state()
        +save_state()
        +create_session()
        +start_step()
    }
```

## Section 7

```mermaid
classDiagram
    class GitBranchManager {
        +__init__()
        +get_info()
    }
    class GitWorkflowManager {
        +__init__()
        +load_snapshots()
        +save_snapshots()
        +run_git()
        +create_snapshot()
    }
    class GoogleSecretManagerMapping {
        +__init__()
        +_gcp_project_path()
        +_secret_names()
        +_secret_version_path()
        +__getitem__()
    }
    class GoogleSecretManagerSettingsSource {
        +__init__()
        +_load_env_vars()
        +__repr__()
    }
    class GracefulDegradationManager {
        +__init__()
        +get_info()
    }
    class HackathonDeadlineManager {
        +__init__()
        +add_task()
        +update_task_status()
        +calculate_critical_path()
        +get_deadline_status()
    }
    class HookManager {
        +__init__()
        +_init_attributes()
        +__getitem__()
    }
    class InMemoryRecordManager {
        +__init__()
        +create_schema()
        +get_time()
        +update()
        +exists()
    }
```

## Section 8

```mermaid
classDiagram
    class InstrumentationManager {
        +__init__()
        +manage()
        +unregister()
        +manager_getter()
        +instrument_attribute()
    }
    class IntelligentCacheManager {
        +__init__()
        +_setup_logging()
        +_initialize_prediction_model()
        +start_cleanup_thread()
        +stop_cleanup_thread()
    }
    class IsLastStepManager {
        +get()
    }
    class LLMManagerMixin {
        +on_llm_new_token()
        +on_llm_end()
        +on_llm_error()
    }
    class MCPManager {
        +__init__()
        +check_mcp_servers()
        +install_mcp_servers()
        +create_mcp_config()
        +create_mcp_directory()
    }
    class MailboxLoggerManager {
        +__init__()
        +start()
        +stop()
        +get_status()
        +__enter__()
    }
    class Manager {
        +__init__()
        +get_info()
    }
    class ManagerCore {
        +__init__()
        +get_info()
    }
```

## Section 9

```mermaid
classDiagram
    class ManagerCoreCore {
        +__init__()
        +get_info()
    }
    class ManagerProcessing {
        +__init__()
        +get_info()
    }
    class ManagerServices {
        +__init__()
        +get_info()
    }
    class ManagerServicesCore {
        +__init__()
        +get_info()
    }
    class ManagerServicesCoreCore {
        +__init__()
        +get_info()
    }
    class ManagerServicesProcessing {
        +__init__()
        +get_info()
    }
    class ManagerServicesServices {
        +__init__()
        +get_info()
    }
    class ManagerServicesServicesCore {
        +__init__()
        +get_info()
    }
```

## Section 10

```mermaid
classDiagram
    class ManagerServicesServicesProcessing {
        +__init__()
        +get_info()
    }
    class MongoDocumentManager {
        +__init__()
        +create_schema()
        +update()
        +get_time()
        +exists()
    }
    class NameDispatchExtensionManager {
        +__init__()
        +_init_plugins()
        +map()
        +map_method()
    }
    class NamedExtensionManager {
        +__init__()
        +make_test_instance()
        +_init_attributes()
        +_init_plugins()
        +_load_one_plugin()
    }
    class NodesManager {
        +__init__()
        +get_node()
        +set_nodes()
        +update_moved_exception()
        +_update_moved_slots()
    }
    class OnePasswordAPIKeyManager {
        +__init__()
        +_is_api_key_item()
        +_extract_aws_account_id()
        +_organize_credentials()
        +_discover_all_apis()
    }
    class OperationalDashboardManager {
        +__init__()
        +get_info()
    }
    class OperationalDashboardManagerModels {
        +__init__()
        +get_info()
    }
```

## Section 11

```mermaid
classDiagram
    class OperationalDashboardManagerServices {
        +__init__()
        +get_info()
    }
    class OperatorSafetyManager {
        +__init__()
        +initialize_safety_systems()
        +shutdown_safety_systems()
        +get_safety_status()
        +is_operation_safe()
    }
    class OptionManager {
        +__init__()
        +register_plugins()
        +add_option()
        +extend_default_ignore()
        +extend_default_select()
    }
    class ParentRunManager {
        +get_child()
    }
    class PhaseManagerModule {
        +determine_phase_priority()
        +calculate_phase_weights()
    }
    class PlanningMemoryManager {
        +__init__()
        +start_planning_session()
        +add_planning_dimension()
        +add_planning_insight()
        +update_planning_depth()
    }
    class PlaywrightContextManager {
        +__init__()
        +__enter__()
        +start()
        +__exit__()
    }
    class PoolManager {
        +__init__()
        +__enter__()
        +__exit__()
        +_new_pool()
        +clear()
    }
```

## Section 12

```mermaid
classDiagram
    class PrometheusConfigManager {
        +__init__()
        +_load_config()
        +_get_bool_env()
        +_validate_config()
        +get_config()
    }
    class PromptModeManager {
        +__init__()
        +start_prompt_conversation()
        +handle_user_response()
        +_handle_ghostbusters_request()
        +_handle_proceed_request()
    }
    class ProxyManager {
        +__init__()
        +connection_from_host()
        +_set_proxy_headers()
        +urlopen()
    }
    class PubSubManager {
        +__init__()
        +register_handler()
        +get_health_status()
    }
    class RMDDDIntegrationManager {
        +__init__()
        +_setup_logging()
        +_initialize_default_services()
        +check_service_health()
        +_make_health_check_request()
    }
    class RecordManager {
        +__init__()
        +create_schema()
        +get_time()
        +update()
        +exists()
    }
    class RecoveryManager {
        +__init__()
        +add_recovery_callback()
        +get_recovery_history()
        +get_active_recoveries()
        +get_recovery_summary()
    }
    class RemainingStepsManager {
        +get()
    }
```

## Section 13

```mermaid
classDiagram
    class RetrieverManagerMixin {
        +on_retriever_error()
        +on_retriever_end()
    }
    class RollbackManager {
        +__init__()
        +create_backup()
        +list_backups()
        +rollback_to_backup()
    }
    class RunManager {
        +on_text()
        +on_retry()
    }
    class RunManagerMixin {
        +on_text()
        +on_retry()
        +on_custom_event()
    }
    class SOCKSProxyManager {
        +__init__()
    }
    class SQLRecordManager {
        +__init__()
        +create_schema()
        +_make_session()
        +get_time()
        +update()
    }
    class SporeManager {
        +__init__()
        +_load_existing_spores()
        +_calculate_checksum()
        +_get_spore_paths()
        +save_spore()
    }
    class SporeManagerCore {
        +__init__()
        +get_info()
    }
```

## Section 14

```mermaid
classDiagram
    class SporeManagerCoreCore {
        +__init__()
        +get_info()
    }
    class SporeManagerModels {
        +__init__()
        +get_info()
    }
    class SporeManagerServices {
        +__init__()
        +get_info()
    }
    class SporeManagerServicesCore {
        +__init__()
        +get_info()
    }
    class SporeManagerServicesCoreCore {
        +__init__()
        +get_info()
    }
    class SporeManagerServicesServices {
        +__init__()
        +get_info()
    }
    class SporeManagerServicesServicesCore {
        +__init__()
        +get_info()
    }
    class StyleGuideManager {
        +__init__()
        +populate_style_guides_with()
        +_style_guide_for()
        +processing_file()
        +handle_error()
    }
```

## Section 15

```mermaid
classDiagram
    class SyncContextManager {
        +__enter__()
        +__exit__()
        +close()
    }
    class SyncManager {
        +__init__()
        +get_info()
    }
    class SyncManagerQueuedsyncoperation {
        +__init__()
        +get_info()
    }
    class SyncManagerQueuedsyncoperationQueuedsyncoperation {
        +__init__()
        +get_info()
    }
    class TestExtensionManager {
        +__init__()
        +_load_plugins()
    }
    class TieredMemoryManager {
        +__init__()
        +add_short_term_memory()
        +get_short_term_memory()
        +queue_for_qualification()
        +qualify_memory()
    }
    class TokenManager {
        +__init__()
        +__del__()
        +start()
        +stop()
        +acquire_token()
    }
    class TokenManagerConfig {
        +__init__()
        +get_expiration_refresh_ratio()
        +get_lower_refresh_bound_millis()
        +get_token_request_execution_timeout_in_ms()
        +get_retry_policy()
    }
```

## Section 16

```mermaid
classDiagram
    class ToolManagerMixin {
        +on_tool_end()
        +on_tool_error()
    }
    class UserContextManager {
        +__init__()
        +__enter__()
        +__exit__()
    }
    class _AsyncExperimentManager {
        +__init__()
        +_reset_example_attachments()
        +_get_example_with_readers()
        +_copy()
    }
    class _AsyncSessionContextManager {
        +__init__()
    }
    class _BaseRequestContextManager {
        +__init__()
        +send()
        +throw()
        +close()
        +__await__()
    }
    class _BlockingAsyncContextManager {
        +__init__()
        +__enter__()
        +__exit__()
    }
    class _DNSResolverManager {
        +__new__()
        +_init()
        +get_resolver()
        +release_resolver()
    }
    class _ExperimentManager {
        +__init__()
        +_reset_example_attachment_readers()
        +examples()
        +dataset_id()
        +evaluation_results()
    }
```

## Section 17

```mermaid
classDiagram
    class _ExperimentManagerMixin {
        +__init__()
        +experiment_name()
        +_get_experiment()
        +_get_experiment_metadata()
        +_create_experiment()
    }
    class _ManagerFactory {
        +__call__()
    }
    class _SerializeManager {
        +__init__()
        +__call__()
    }
    class _SessionRequestContextManager {
        +__init__()
    }
```

## All Classes in Domain

- `AWSSecretsManagerSettingsSource`
- `AlertManager`
- `AsyncCallbackManager`
- `AsyncCallbackManagerForChainGroup`
- `AsyncCallbackManagerForChainRun`
- `AsyncCallbackManagerForLLMRun`
- `AsyncCallbackManagerForRetrieverRun`
- `AsyncCallbackManagerForToolRun`
- `AsyncContextManager`
- `AsyncContextManagerMixin`
- `AsyncEventContextManager`
- `AsyncParentRunManager`
- `AsyncRunManager`
- `BanditManager`
- `BaseCallbackManager`
- `BaseRunManager`
- `BranchProtectionManager`
- `BreakTheGlassProtocolManager`
- `BrowserSessionManager`
- `BuildManager`
- `CallbackManager`
- `CallbackManagerForChainGroup`
- `CallbackManagerForChainRun`
- `CallbackManagerForLLMRun`
- `CallbackManagerForRetrieverRun`
- `CallbackManagerForToolRun`
- `CallbackManagerMixin`
- `ChainManagerMixin`
- `ClassManager`
- `ContextManagerMixin`
- `DeadlineManager`
- `DeadlineManagerCore`
- `DeadlineManagerCoreCore`
- `DeploymentManager`
- `DispatchExtensionManager`
- `DriverManager`
- `EmergencyProtocolManager`
- `EnabledExtensionManager`
- `EnhancedObservabilityManager`
- `EnhancedObservabilityManagerCore`
- `EnhancedObservabilityManagerServices`
- `EventContextManager`
- `EventContextManagerImpl`
- `ExtensionManager`
- `FindersManager`
- `FineGrainedBuildManager`
- `FontManager`
- `GCPStateManager`
- `GitBranchManager`
- `GitWorkflowManager`
- `GoogleSecretManagerMapping`
- `GoogleSecretManagerSettingsSource`
- `GracefulDegradationManager`
- `HackathonDeadlineManager`
- `HookManager`
- `InMemoryRecordManager`
- `InstrumentationManager`
- `IntelligentCacheManager`
- `IsLastStepManager`
- `LLMManagerMixin`
- `MCPManager`
- `MailboxLoggerManager`
- `Manager`
- `ManagerCore`
- `ManagerCoreCore`
- `ManagerProcessing`
- `ManagerServices`
- `ManagerServicesCore`
- `ManagerServicesCoreCore`
- `ManagerServicesProcessing`
- `ManagerServicesServices`
- `ManagerServicesServicesCore`
- `ManagerServicesServicesProcessing`
- `MongoDocumentManager`
- `NameDispatchExtensionManager`
- `NamedExtensionManager`
- `NodesManager`
- `OnePasswordAPIKeyManager`
- `OperationalDashboardManager`
- `OperationalDashboardManagerModels`
- `OperationalDashboardManagerServices`
- `OperatorSafetyManager`
- `OptionManager`
- `ParentRunManager`
- `PhaseManagerModule`
- `PlanningMemoryManager`
- `PlaywrightContextManager`
- `PoolManager`
- `PrometheusConfigManager`
- `PromptModeManager`
- `ProxyManager`
- `PubSubManager`
- `RMDDDIntegrationManager`
- `RecordManager`
- `RecoveryManager`
- `RemainingStepsManager`
- `RetrieverManagerMixin`
- `RollbackManager`
- `RunManager`
- `RunManagerMixin`
- `SOCKSProxyManager`
- `SQLRecordManager`
- `SporeManager`
- `SporeManagerCore`
- `SporeManagerCoreCore`
- `SporeManagerModels`
- `SporeManagerServices`
- `SporeManagerServicesCore`
- `SporeManagerServicesCoreCore`
- `SporeManagerServicesServices`
- `SporeManagerServicesServicesCore`
- `StyleGuideManager`
- `SyncContextManager`
- `SyncManager`
- `SyncManagerQueuedsyncoperation`
- `SyncManagerQueuedsyncoperationQueuedsyncoperation`
- `TestExtensionManager`
- `TieredMemoryManager`
- `TokenManager`
- `TokenManagerConfig`
- `ToolManagerMixin`
- `UserContextManager`
- `_AsyncExperimentManager`
- `_AsyncSessionContextManager`
- `_BaseRequestContextManager`
- `_BlockingAsyncContextManager`
- `_DNSResolverManager`
- `_ExperimentManager`
- `_ExperimentManagerMixin`
- `_ManagerFactory`
- `_SerializeManager`
- `_SessionRequestContextManager`
