# Agent Domain Architecture

**Total Classes**: 78

## Section 1

```mermaid
classDiagram
    class Agent {
    }
    class AgentAction {
        +__init__()
        +is_lc_serializable()
        +get_lc_namespace()
        +messages()
    }
    class AgentActionMessageLog {
    }
    class AgentCapabilities {
    }
    class AgentCapability {
    }
    class AgentCommunicator {
        +__init__()
        +start_listening()
        +send_message()
        +stop_listening()
    }
    class AgentCoordinator {
    }
    class AgentDiscoveryHandler {
        +__init__()
        +get_supported_types()
        +validate_message()
    }
    AgentActionMessageLog --|> AgentAction
```

## Section 2

```mermaid
classDiagram
    class AgentExecutor {
        +from_agent_and_tools()
        +validate_tools()
        +validate_runnable_agent()
        +_action_agent()
        +save()
    }
    class AgentExecutorIterator {
        +__init__()
        +inputs()
        +inputs()
        +agent_executor()
        +agent_executor()
    }
    class AgentFinish {
        +__init__()
        +is_lc_serializable()
        +get_lc_namespace()
        +messages()
    }
    class AgentManager {
        +__init__()
        +get_info()
    }
    class AgentMetrics {
    }
    class AgentOrchestrator {
        +__init__()
        +register_agent()
        +get_available_agent()
        +assign_task_to_agent()
        +release_agent()
    }
    class AgentOutputParser {
        +parse()
    }
    class AgentPool {
        +__post_init__()
    }
```

## Section 3

```mermaid
classDiagram
    class AgentResponseHandler {
        +__init__()
        +get_supported_types()
    }
    class AgentResult {
    }
    class AgentScratchPadChatPromptTemplate {
        +is_lc_serializable()
        +_construct_agent_scratchpad()
        +_merge_partial_and_user_variables()
    }
    class AgentState {
    }
    class AgentStatePydantic {
    }
    class AgentStateWithStructuredResponse {
    }
    class AgentStateWithStructuredResponsePydantic {
    }
    class AgentStatus {
    }
    AgentStateWithStructuredResponse --|> AgentState
    AgentStateWithStructuredResponsePydantic --|> AgentStatePydantic
```

## Section 4

```mermaid
classDiagram
    class AgentStep {
        +messages()
    }
    class AgentTokenBufferMemory {
        +buffer()
        +memory_variables()
        +load_memory_variables()
        +save_context()
    }
    class AgentTrajectoryEvaluator {
        +requires_input()
        +_evaluate_agent_trajectory()
        +evaluate_agent_trajectory()
    }
    class AgentType {
    }
    class BaseMultiActionAgent {
        +return_values()
        +get_allowed_tools()
        +plan()
        +input_keys()
        +return_stopped_response()
    }
    class BaseSingleActionAgent {
        +return_values()
        +get_allowed_tools()
        +plan()
        +input_keys()
        +return_stopped_response()
    }
    class BillingAgentState {
    }
    class BillingAnalysisAgents {
        +__init__()
        +_create_billing_workflow()
        +_data_collector_agent()
        +_cost_analyzer_agent()
        +_anomaly_detector_agent()
    }
```

## Section 5

```mermaid
classDiagram
    class ChatAgent {
        +observation_prefix()
        +llm_prefix()
        +_construct_scratchpad()
        +_get_default_output_parser()
        +_validate_tools()
    }
    class CodeQualityMentorAgent {
        +__init__()
        +get_specializations()
        +get_max_concurrent_tasks()
    }
    class ConversationalAgent {
        +_get_default_output_parser()
        +_agent_type()
        +observation_prefix()
        +llm_prefix()
        +create_prompt()
    }
    class ConversationalChatAgent {
        +_get_default_output_parser()
        +_agent_type()
        +observation_prefix()
        +llm_prefix()
        +_validate_tools()
    }
    class CostOptimizationAgent {
        +__init__()
        +get_specializations()
        +get_max_concurrent_tasks()
    }
    class DeploymentSpecialistAgent {
        +__init__()
        +get_specializations()
        +get_max_concurrent_tasks()
    }
    class GhostbustersExpertAgent {
        +__init__()
        +get_capabilities()
        +validate_confidence()
        +supports_capability()
        +get_agent_info()
    }
    class JSONAgentOutputParser {
        +parse()
        +_type()
    }
```

## Section 6

```mermaid
classDiagram
    class LLMSingleActionAgent {
        +input_keys()
        +dict()
        +plan()
        +tool_run_logging_kwargs()
    }
    class MultiActionAgentOutputParser {
        +parse()
    }
    class MultiAgentCollaborationModel {
        +__init__()
        +get_info()
    }
    class MultiAgentCollaborationModelCore {
        +__init__()
        +get_info()
    }
    class MultiAgentCollaborationModelModels {
        +__init__()
        +get_info()
    }
    class OpenAIAgentsTracingProcessor {
        +__init__()
    }
    class OpenAIFunctionsAgent {
        +get_allowed_tools()
        +validate_prompt()
        +input_keys()
        +functions()
        +plan()
    }
    class OpenAIFunctionsAgentOutputParser {
        +_type()
        +_parse_ai_message()
        +parse_result()
        +parse()
    }
```

## Section 7

```mermaid
classDiagram
    class OpenAIMultiFunctionsAgent {
        +get_allowed_tools()
        +validate_prompt()
        +input_keys()
        +functions()
        +plan()
    }
    class OpenAIToolsAgentOutputParser {
        +_type()
        +parse_result()
        +parse()
    }
    class OrchestrationEngine {
        +__init__()
        +get_info()
    }
    class OrchestrationEngineServices {
        +__init__()
        +get_info()
    }
    class OrchestrationResult {
        +get_summary()
    }
    class ParallelAgent {
    }
    class ReActDocstoreAgent {
        +_get_default_output_parser()
        +_agent_type()
        +create_prompt()
        +_validate_tools()
        +observation_prefix()
    }
    class RunnableAgent {
        +return_values()
        +input_keys()
        +plan()
    }
```

## Section 8

```mermaid
classDiagram
    class RunnableMultiActionAgent {
        +return_values()
        +input_keys()
        +plan()
    }
    class SelfAskWithSearchAgent {
        +_get_default_output_parser()
        +_agent_type()
        +create_prompt()
        +_validate_tools()
        +observation_prefix()
    }
    class SimpleBeastAgent {
        +__init__()
        +_get_primary_responsibility()
        +get_health_indicators()
        +get_module_status()
        +is_healthy()
    }
    class SimplifiedMultiAgentModel {
        +__init__()
        +get_module_status()
        +_get_primary_responsibility()
        +is_healthy()
        +get_health_indicators()
    }
    class StructuredChatAgent {
        +observation_prefix()
        +llm_prefix()
        +_construct_scratchpad()
        +_validate_tools()
        +_get_default_output_parser()
    }
    class ToolAgentAction {
    }
    class ToolOrchestrationEngine {
        +__init__()
        +get_module_status()
        +is_healthy()
        +get_health_indicators()
        +_get_primary_responsibility()
    }
    class ToolOrchestrationEngineCore {
        +__init__()
        +get_info()
    }
```

## Section 9

```mermaid
classDiagram
    class ToolOrchestrationEngineCoreCore {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServices {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesCore {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesCoreCore {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesServices {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesServicesCore {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesServicesUtils {
        +__init__()
        +get_info()
    }
    class ToolOrchestrationEngineServicesUtils {
        +__init__()
        +get_info()
    }
```

## Section 10

```mermaid
classDiagram
    class ToolOrchestrationEngineUtils {
        +__init__()
        +get_info()
    }
    class ToolsAgentOutputParser {
        +_type()
        +parse_result()
        +parse()
    }
    class UserAgentBuilder {
        +__init__()
        +build()
        +include_extras()
        +include_implementation()
        +include_system()
    }
    class XMLAgent {
        +input_keys()
        +get_default_prompt()
        +get_default_output_parser()
        +plan()
    }
    class XMLAgentOutputParser {
        +parse()
        +get_format_instructions()
        +_type()
    }
    class ZeroShotAgent {
        +_get_default_output_parser()
        +_agent_type()
        +observation_prefix()
        +llm_prefix()
        +create_prompt()
    }
```

## All Classes in Domain

- `Agent`
- `AgentAction`
- `AgentActionMessageLog`
- `AgentCapabilities`
- `AgentCapability`
- `AgentCommunicator`
- `AgentCoordinator`
- `AgentDiscoveryHandler`
- `AgentExecutor`
- `AgentExecutorIterator`
- `AgentFinish`
- `AgentManager`
- `AgentMetrics`
- `AgentOrchestrator`
- `AgentOutputParser`
- `AgentPool`
- `AgentResponseHandler`
- `AgentResult`
- `AgentScratchPadChatPromptTemplate`
- `AgentState`
- `AgentStatePydantic`
- `AgentStateWithStructuredResponse`
- `AgentStateWithStructuredResponsePydantic`
- `AgentStatus`
- `AgentStep`
- `AgentTokenBufferMemory`
- `AgentTrajectoryEvaluator`
- `AgentType`
- `BaseMultiActionAgent`
- `BaseSingleActionAgent`
- `BillingAgentState`
- `BillingAnalysisAgents`
- `ChatAgent`
- `CodeQualityMentorAgent`
- `ConversationalAgent`
- `ConversationalChatAgent`
- `CostOptimizationAgent`
- `DeploymentSpecialistAgent`
- `GhostbustersExpertAgent`
- `JSONAgentOutputParser`
- `LLMSingleActionAgent`
- `MultiActionAgentOutputParser`
- `MultiAgentCollaborationModel`
- `MultiAgentCollaborationModelCore`
- `MultiAgentCollaborationModelModels`
- `OpenAIAgentsTracingProcessor`
- `OpenAIFunctionsAgent`
- `OpenAIFunctionsAgentOutputParser`
- `OpenAIMultiFunctionsAgent`
- `OpenAIToolsAgentOutputParser`
- `OrchestrationEngine`
- `OrchestrationEngineServices`
- `OrchestrationResult`
- `ParallelAgent`
- `ReActDocstoreAgent`
- `RunnableAgent`
- `RunnableMultiActionAgent`
- `SelfAskWithSearchAgent`
- `SimpleBeastAgent`
- `SimplifiedMultiAgentModel`
- `StructuredChatAgent`
- `ToolAgentAction`
- `ToolOrchestrationEngine`
- `ToolOrchestrationEngineCore`
- `ToolOrchestrationEngineCoreCore`
- `ToolOrchestrationEngineServices`
- `ToolOrchestrationEngineServicesCore`
- `ToolOrchestrationEngineServicesCoreCore`
- `ToolOrchestrationEngineServicesServices`
- `ToolOrchestrationEngineServicesServicesCore`
- `ToolOrchestrationEngineServicesServicesUtils`
- `ToolOrchestrationEngineServicesUtils`
- `ToolOrchestrationEngineUtils`
- `ToolsAgentOutputParser`
- `UserAgentBuilder`
- `XMLAgent`
- `XMLAgentOutputParser`
- `ZeroShotAgent`
