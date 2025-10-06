# Task Domain Architecture

**Total Classes**: 100

## Section 1

```mermaid
classDiagram
    class AgentExecution {
    }
    class AgentTask {
    }
    class AssertsExecutionResults {
        +assert_result()
        +assert_list()
        +assert_row()
        +assert_unordered_result()
        +sql_execution_asserter()
    }
    class AsyncIOTaskInfo {
        +__init__()
        +has_pending_cancellation()
    }
    class CheckpointTask {
    }
    class DAGAnalysis {
    }
    class DagModels {
        +__init__()
        +get_info()
    }
    class DebuggingEngineMethodsExecutiontrace {
        +__init__()
        +get_info()
    }
```

## Section 2

```mermaid
classDiagram
    class DefaultExecutionContext {
        +_init_ddl()
        +_init_compiled()
        +_init_statement()
        +_init_default()
        +_get_cache_stats()
    }
    class DiscoveredAgent {
    }
    class EnhancedAgentOrchestrator {
        +__init__()
        +discover_rdi_test_files()
        +test_file_execution_status()
        +apply_repair_pattern()
        +_repair_syntax_issues()
    }
    class EventSourcedAggregate {
        +__init__()
        +version()
        +is_new()
        +get_uncommitted_events()
        +mark_events_as_committed()
    }
    class ExecutionAnalyzer {
        +__init__()
        +verify()
    }
    class ExecutionConfig {
    }
    class ExecutionContext {
        +_init_ddl()
        +_init_compiled()
        +_init_statement()
        +_init_default()
        +_exec_default()
    }
    class ExecutionEngine {
        +__init__()
        +get_info()
    }
    DefaultExecutionContext --|> ExecutionContext
```

## Section 3

```mermaid
classDiagram
    class ExecutionError {
    }
    class ExecutionMode {
    }
    class ExecutionPlan {
    }
    class ExecutionResult {
    }
    class ExecutionStatus {
    }
    class ExecutionStrategy {
        +__init__()
        +get_info()
    }
    class ExecutiontraceInterface {
        +__init__()
        +get_info()
    }
    class FunctionExecutionResult {
        +to_json()
    }
```

## Section 4

```mermaid
classDiagram
    class HackathonTask {
    }
    class LaunchExecutionCore {
        +__init__()
        +get_info()
    }
    class LaunchExecutionCoreCore {
        +__init__()
        +get_info()
    }
    class LaunchExecutionCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class LaunchExecutionCoreProcessing {
        +__init__()
        +get_info()
    }
    class LaunchExecutionProcessing {
        +__init__()
        +get_info()
    }
    class LaunchExecutionSystem {
        +__init__()
        +execute_competitive_launch()
        +monitor_competitive_response()
        +adapt_strategy()
        +generate_success_metrics()
    }
    class MSExecutionContext {
        +_opt_encode()
        +pre_exec()
        +post_exec()
        +get_lastrowid()
        +handle_dbapi_exception()
    }
```

## Section 5

```mermaid
classDiagram
    class MSExecutionContext_aioodbc {
        +create_server_side_cursor()
    }
    class MSExecutionContext_pyodbc {
        +pre_exec()
        +post_exec()
    }
    class MySQLExecutionContext {
        +post_exec()
        +create_server_side_cursor()
        +fire_sequence()
    }
    class MySQLExecutionContext_mariadbconnector {
        +create_server_side_cursor()
        +create_default_cursor()
        +post_exec()
        +get_lastrowid()
    }
    class MySQLExecutionContext_mysqlconnector {
        +create_server_side_cursor()
        +create_default_cursor()
    }
    class MySQLExecutionContext_mysqldb {
    }
    class MySQLExecutionContext_pyodbc {
        +get_lastrowid()
    }
    class OracleExecutionContext {
        +fire_sequence()
        +pre_exec()
    }
    MSExecutionContext_aioodbc --|> MSExecutionContext_pyodbc
    MySQLExecutionContext_mariadbconnector --|> MySQLExecutionContext
    MySQLExecutionContext_mysqlconnector --|> MySQLExecutionContext
    MySQLExecutionContext_mysqldb --|> MySQLExecutionContext
    MySQLExecutionContext_pyodbc --|> MySQLExecutionContext
```

## Section 6

```mermaid
classDiagram
    class OracleExecutionContextAsync_oracledb {
        +create_default_cursor()
        +create_server_side_cursor()
    }
    class OracleExecutionContext_cx_oracle {
        +_generate_out_parameter_vars()
        +_generate_cursor_outputtype_handler()
        +_get_cx_oracle_type_handler()
        +pre_exec()
        +post_exec()
    }
    class OracleExecutionContext_oracledb {
    }
    class PDCATask {
    }
    class PGExecutionContext {
        +fire_sequence()
        +get_insert_default()
    }
    class PGExecutionContext_psycopg2 {
        +post_exec()
        +_log_notices()
    }
    class ParallelExecutionCoordinator {
        +__init__()
        +_build_agent_command()
        +_calculate_parallel_efficiency()
        +_calculate_timeline_reduction()
        +_calculate_task_complexity()
    }
    class ParallelExecutionResult {
    }
    OracleExecutionContextAsync_oracledb --|> OracleExecutionContext_oracledb
```

## Section 7

```mermaid
classDiagram
    class Phase5LaunchExecutionDemo {
        +__init__()
        +run_complete_demo()
        +_demo_launch_execution_system()
        +_demo_production_deployment()
        +_demo_competitive_monitoring()
    }
    class PluginExecutionFailed {
        +__init__()
        +__str__()
    }
    class PregelExecutableTask {
    }
    class PregelTask {
    }
    class PregelTaskWrites {
    }
    class RdiDagIntegration {
        +__init__()
        +get_info()
    }
    class ReActTextWorldAgent {
        +create_prompt()
        +_validate_tools()
    }
    class RecoveryExecution {
    }
```

## Section 8

```mermaid
classDiagram
    class RefactoringTask {
    }
    class ResponseExecution {
    }
    class SQLiteExecutionContext {
        +_preserve_raw_colnames()
        +_translate_colname()
    }
    class SQLiteExecutionContext_aiosqlite {
        +create_server_side_cursor()
    }
    class SpecTask {
    }
    class Task {
    }
    class TaskComplexity {
    }
    class TaskDAGAnalyzer {
        +__init__()
        +load_tasks_from_spec()
        +_parse_tasks_markdown()
        +_extract_dependencies()
        +_resolve_parent_dependencies()
    }
    SQLiteExecutionContext_aiosqlite --|> SQLiteExecutionContext
```

## Section 9

```mermaid
classDiagram
    class TaskDAGRM {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class TaskDagRmCore {
        +__init__()
        +get_info()
    }
    class TaskDagRmCoreCore {
        +__init__()
        +get_info()
    }
    class TaskDagRmCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class TaskDagRmCoreProcessing {
        +__init__()
        +get_info()
    }
    class TaskDagRmProcessing {
        +__init__()
        +get_info()
    }
    class TaskDetectionResult {
    }
    class TaskDetector {
        +__init__()
        +detect_tasks_from_specs()
        +_extract_tasks_from_spec()
        +_parse_task_line()
        +_extract_task_id_and_name()
    }
```

## Section 10

```mermaid
classDiagram
    class TaskDetectorCore {
        +__init__()
        +get_info()
    }
    class TaskDetectorCoreCore {
        +__init__()
        +get_info()
    }
    class TaskDetectorCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class TaskDetectorCoreProcessing {
        +__init__()
        +get_info()
    }
    class TaskDetectorProcessing {
        +__init__()
        +get_info()
    }
    class TaskExecutionEngine {
        +__init__()
        +_initialize_tasks()
        +_initialize_agents()
        +get_ready_tasks()
        +_dependencies_met()
    }
    class TaskGroup {
        +__init__()
        +_spawn()
        +start_soon()
    }
    class TaskInfo {
        +__init__()
        +__eq__()
        +__hash__()
        +__repr__()
        +has_pending_cancellation()
    }
```

## Section 11

```mermaid
classDiagram
    class TaskMapping {
    }
    class TaskNode {
    }
    class TaskNotFound {
    }
    class TaskPayload {
    }
    class TaskPriority {
    }
    class TaskProgressColumn {
        +__init__()
        +render_speed()
        +render()
    }
    class TaskResultPayload {
    }
    class TaskScheduler {
        +__init__()
        +create_task()
        +_add_to_queue()
        +get_next_task()
        +assign_task()
    }
```

## Section 12

```mermaid
classDiagram
    class TaskState {
        +__init__()
    }
    class TaskStatus {
    }
    class ThreadTask {
    }
    class ToolExecutionRequest {
    }
    class ToolExecutionResult {
    }
    class UnboundExecutionError {
    }
    class _AsyncioTaskStatus {
        +__init__()
        +started()
    }
    class _BlockingPortalTaskStatus {
        +__init__()
        +started()
    }
    _BlockingPortalTaskStatus --|> TaskStatus
```

## Section 13

```mermaid
classDiagram
    class _CoreKnownExecutionOptions {
    }
    class _IgnoredTaskStatus {
        +started()
    }
    class _OrmKnownExecutionOptions {
    }
    class _PGExecutionContext_common_psycopg {
        +create_server_side_cursor()
    }
    _OrmKnownExecutionOptions --|> _CoreKnownExecutionOptions
```

## All Classes in Domain

- `AgentExecution`
- `AgentTask`
- `AssertsExecutionResults`
- `AsyncIOTaskInfo`
- `CheckpointTask`
- `DAGAnalysis`
- `DagModels`
- `DebuggingEngineMethodsExecutiontrace`
- `DefaultExecutionContext`
- `DiscoveredAgent`
- `EnhancedAgentOrchestrator`
- `EventSourcedAggregate`
- `ExecutionAnalyzer`
- `ExecutionConfig`
- `ExecutionContext`
- `ExecutionEngine`
- `ExecutionError`
- `ExecutionMode`
- `ExecutionPlan`
- `ExecutionResult`
- `ExecutionStatus`
- `ExecutionStrategy`
- `ExecutiontraceInterface`
- `FunctionExecutionResult`
- `HackathonTask`
- `LaunchExecutionCore`
- `LaunchExecutionCoreCore`
- `LaunchExecutionCoreCoreProcessing`
- `LaunchExecutionCoreProcessing`
- `LaunchExecutionProcessing`
- `LaunchExecutionSystem`
- `MSExecutionContext`
- `MSExecutionContext_aioodbc`
- `MSExecutionContext_pyodbc`
- `MySQLExecutionContext`
- `MySQLExecutionContext_mariadbconnector`
- `MySQLExecutionContext_mysqlconnector`
- `MySQLExecutionContext_mysqldb`
- `MySQLExecutionContext_pyodbc`
- `OracleExecutionContext`
- `OracleExecutionContextAsync_oracledb`
- `OracleExecutionContext_cx_oracle`
- `OracleExecutionContext_oracledb`
- `PDCATask`
- `PGExecutionContext`
- `PGExecutionContext_psycopg2`
- `ParallelExecutionCoordinator`
- `ParallelExecutionResult`
- `Phase5LaunchExecutionDemo`
- `PluginExecutionFailed`
- `PregelExecutableTask`
- `PregelTask`
- `PregelTaskWrites`
- `RdiDagIntegration`
- `ReActTextWorldAgent`
- `RecoveryExecution`
- `RefactoringTask`
- `ResponseExecution`
- `SQLiteExecutionContext`
- `SQLiteExecutionContext_aiosqlite`
- `SpecTask`
- `Task`
- `TaskComplexity`
- `TaskDAGAnalyzer`
- `TaskDAGRM`
- `TaskDagRmCore`
- `TaskDagRmCoreCore`
- `TaskDagRmCoreCoreProcessing`
- `TaskDagRmCoreProcessing`
- `TaskDagRmProcessing`
- `TaskDetectionResult`
- `TaskDetector`
- `TaskDetectorCore`
- `TaskDetectorCoreCore`
- `TaskDetectorCoreCoreProcessing`
- `TaskDetectorCoreProcessing`
- `TaskDetectorProcessing`
- `TaskExecutionEngine`
- `TaskGroup`
- `TaskInfo`
- `TaskMapping`
- `TaskNode`
- `TaskNotFound`
- `TaskPayload`
- `TaskPriority`
- `TaskProgressColumn`
- `TaskResultPayload`
- `TaskScheduler`
- `TaskState`
- `TaskStatus`
- `ThreadTask`
- `ToolExecutionRequest`
- `ToolExecutionResult`
- `UnboundExecutionError`
- `_AsyncioTaskStatus`
- `_BlockingPortalTaskStatus`
- `_CoreKnownExecutionOptions`
- `_IgnoredTaskStatus`
- `_OrmKnownExecutionOptions`
- `_PGExecutionContext_common_psycopg`
