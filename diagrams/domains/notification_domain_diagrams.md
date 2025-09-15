# Notification Domain Architecture

**Total Classes**: 155

## Section 1

```mermaid
classDiagram
    class AIMessage {
        +__init__()
        +lc_attributes()
        +_backwards_compat_tool_calls()
        +pretty_repr()
    }
    class AIMessageChunk {
        +lc_attributes()
        +init_tool_calls()
        +__add__()
    }
    class AIMessagePromptTemplate {
    }
    class AstraDBChatMessageHistory {
        +__init__()
        +messages()
        +messages()
        +add_messages()
        +clear()
    }
    class AsyncMessageStreamWrapper {
        +__init__()
        +text_stream()
        +response()
        +request_id()
        +current_message_snapshot()
    }
    class AsyncMessagesStreamManagerWrapper {
        +__init__()
    }
    class AsyncPushNotificationsParser {
        +set_pubsub_push_handler()
        +set_invalidation_push_handler()
    }
    class BadHttpMessage {
        +__init__()
    }
    AIMessageChunk --|> AIMessage
```

## Section 2

```mermaid
classDiagram
    class BaseChatMessageHistory {
        +add_user_message()
        +add_ai_message()
        +add_message()
        +add_messages()
        +clear()
    }
    class BaseMessage {
        +__init__()
        +is_lc_serializable()
        +get_lc_namespace()
        +text()
        +__add__()
    }
    class BaseMessageChunk {
        +__add__()
    }
    class BaseMessageConverter {
        +from_sql_model()
        +to_sql_model()
        +get_sql_model_class()
    }
    class BaseMessageHandler {
        +__init__()
        +get_supported_types()
        +can_handle()
        +validate_message()
        +get_stats()
    }
    class BaseMessageLike {
        +type()
    }
    class BaseMessagePromptTemplate {
        +is_lc_serializable()
        +get_lc_namespace()
        +format_messages()
        +input_variables()
        +pretty_repr()
    }
    class BaseStringMessagePromptTemplate {
        +from_template()
        +from_template_file()
        +format()
        +format_messages()
        +input_variables()
    }
    BaseMessageChunk --|> BaseMessage
    BaseStringMessagePromptTemplate --|> BaseMessagePromptTemplate
```

## Section 3

```mermaid
classDiagram
    class CassandraChatMessageHistory {
        +__init__()
        +messages()
        +add_message()
        +clear()
    }
    class ChatMessage {
    }
    class ChatMessageChunk {
        +__add__()
    }
    class ChatMessagePromptTemplate {
        +format()
    }
    class ConsoleMessage {
        +type()
        +text()
        +args()
        +location()
        +page()
    }
    class CosmosDBChatMessageHistory {
        +__init__()
        +prepare_cosmos()
        +__enter__()
        +__exit__()
        +load_messages()
    }
    class CreateDraftMessageSchema {
    }
    class DefaultMessageConverter {
        +__init__()
        +from_sql_model()
        +to_sql_model()
        +get_sql_model_class()
    }
    ChatMessageChunk --|> ChatMessage
```

## Section 4

```mermaid
classDiagram
    class DynamoDBChatMessageHistory {
        +__init__()
        +messages()
        +messages()
        +add_messages()
        +clear()
    }
    class ElasticsearchChatMessageHistory {
        +__init__()
        +get_user_agent()
        +connect_to_elasticsearch()
        +messages()
        +messages()
    }
    class EndOfMessage {
        +__init__()
    }
    class ErrorMessage {
        +format()
        +with_additional_msg()
    }
    class FakeMessagesListChatModel {
        +_generate()
        +_llm_type()
    }
    class FewShotChatMessagePromptTemplate {
        +is_lc_serializable()
        +format_messages()
        +format()
        +pretty_repr()
    }
    class FileChatMessageHistory {
        +__init__()
        +messages()
        +add_message()
        +clear()
    }
    class FirestoreChatMessageHistory {
        +__init__()
        +prepare_firestore()
        +load_messages()
        +add_message()
        +upsert_messages()
    }
```

## Section 5

```mermaid
classDiagram
    class FunctionMessage {
    }
    class FunctionMessageChunk {
        +__add__()
    }
    class GmailGetMessage {
        +_run()
    }
    class GmailSendMessage {
        +_prepare_message()
        +_run()
    }
    class HumanMessage {
        +__init__()
    }
    class HumanMessageChunk {
    }
    class HumanMessagePromptTemplate {
    }
    class IMessageChatLoader {
        +__init__()
        +_parse_attributed_body()
        +_get_session_query()
        +_load_single_chat_session()
        +lazy_load()
    }
    FunctionMessageChunk --|> FunctionMessage
    HumanMessageChunk --|> HumanMessage
```

## Section 6

```mermaid
classDiagram
    class InMemoryChatMessageHistory {
        +add_message()
        +clear()
    }
    class KafkaChatMessageHistory {
        +__init__()
        +add_messages()
        +__read_messages()
        +messages_from_beginning()
        +messages_from_latest()
    }
    class LegacyMessageType {
    }
    class MQTTMessage {
        +__init__()
        +__eq__()
        +__ne__()
        +topic()
        +topic()
    }
    class MQTTMessageInfo {
        +__init__()
        +__str__()
        +__iter__()
        +__next__()
        +next()
    }
    class Message {
        +__init__()
        +__str__()
    }
    class MessageBuilder {
        +__init__()
        +filter_errors()
        +add_errors()
        +disable_type_names()
        +are_type_names_disabled()
    }
    class MessageCompatibilityError {
    }
```

## Section 7

```mermaid
classDiagram
    class MessageCompatibilityLayer {
        +__init__()
        +register_unknown_type_handler()
        +register_custom_type()
        +process_message()
        +_is_unknown_type()
    }
    class MessageConversionError {
    }
    class MessageConverter {
        +__init__()
        +convert_to_current()
        +_convert_from_version()
        +_convert_from_v1_0()
        +_convert_from_v1_1()
    }
    class MessageDict {
    }
    class MessageEntry {
    }
    class MessageFilter {
    }
    class MessageGraph {
        +__init__()
    }
    class MessageHandler {
        +get_supported_types()
    }
```

## Section 8

```mermaid
classDiagram
    class MessageHandlerResult {
    }
    class MessageHandlersCore {
        +__init__()
        +get_info()
    }
    class MessageHandlersCoreCore {
        +__init__()
        +get_info()
    }
    class MessageHandlersCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class MessageHandlersCoreProcessing {
        +__init__()
        +get_info()
    }
    class MessageHandlersHandlers {
        +__init__()
        +get_info()
    }
    class MessageHandlersHandlersCore {
        +__init__()
        +get_info()
    }
    class MessageHandlersHandlersHandlersCore {
        +__init__()
        +get_info()
    }
```

## Section 9

```mermaid
classDiagram
    class MessageHandlersProcessing {
        +__init__()
        +get_info()
    }
    class MessageHistory {
        +__init__()
        +get_info()
    }
    class MessageHistoryManager {
        +__init__()
        +_load_status_data()
        +_write_status_file()
        +_file_in_time_range()
        +_read_log_file()
    }
    class MessageHistoryServices {
        +__init__()
        +get_info()
    }
    class MessageHistoryServicesCore {
        +__init__()
        +get_info()
    }
    class MessageHistoryServicesServices {
        +__init__()
        +get_info()
    }
    class MessageHistoryServicesServicesCore {
        +__init__()
        +get_info()
    }
    class MessageModels {
        +__init__()
        +get_info()
    }
```

## Section 10

```mermaid
classDiagram
    class MessageModelsCore {
        +__init__()
        +get_info()
    }
    class MessageModelsCoreCore {
        +__init__()
        +get_info()
    }
    class MessageRouter {
        +__init__()
        +register_handler()
        +register_fallback_handler()
        +_convert_legacy_message()
        +get_supported_types()
    }
    class MessageRouterCore {
        +__init__()
        +get_info()
    }
    class MessageRouterCoreCore {
        +__init__()
        +get_info()
    }
    class MessageState {
    }
    class MessageStatus {
    }
    class MessageStreamWrapper {
        +__init__()
        +response()
        +request_id()
        +text_stream()
        +__next__()
    }
```

## Section 11

```mermaid
classDiagram
    class MessageType {
    }
    class MessageTypeDemo {
        +__init__()
        +_create_callbacks()
        +_handle_simple_message()
        +_handle_prompt_request()
        +_handle_prompt_response()
    }
    class MessageTypeTranslator {
        +__init__()
        +translate_to_current()
        +translate_to_legacy()
    }
    class MessageVersion {
    }
    class MessageVersionDetector {
        +__init__()
        +detect_version()
        +is_compatible_version()
    }
    class MessagesPlaceholder {
        +__init__()
        +format_messages()
        +input_variables()
        +pretty_repr()
    }
    class MessagesState {
    }
    class MessagesStreamManagerWrapper {
        +__init__()
        +__enter__()
        +__exit__()
    }
```

## Section 12

```mermaid
classDiagram
    class MomentoChatMessageHistory {
        +__init__()
        +from_client_params()
        +messages()
        +add_message()
        +clear()
    }
    class MongoDBChatMessageHistory {
        +__init__()
        +messages()
        +add_message()
        +clear()
    }
    class Neo4jChatMessageHistory {
        +__init__()
        +messages()
        +messages()
        +add_message()
        +clear()
    }
    class NotificationManager {
        +__init__()
        +get_info()
    }
    class NotificationManagerMethods {
        +__init__()
        +get_info()
    }
    class NotificationManagerMethodsNotificationconfig {
        +__init__()
        +get_info()
    }
    class NotificationManagerMethodsNotificationmanager {
        +__init__()
        +get_info()
    }
    class NotificationMessage {
        +__init__()
        +get_module_info()
        +get_capabilities()
        +get_dependencies()
        +check_health()
    }
```

## Section 13

```mermaid
classDiagram
    class NotificationModels {
        +__init__()
        +get_info()
    }
    class NotificationModelsNotificationmessage {
        +__init__()
        +get_info()
    }
    class NotificationModelsNotificationmessageNotificationmessage {
        +__init__()
        +get_info()
    }
    class NotificationModelsNotificationsettings {
        +__init__()
        +get_info()
    }
    class NotificationNotificationmessage {
        +__init__()
        +get_info()
    }
    class NotificationNotificationmessageNotificationmessage {
        +__init__()
        +get_info()
    }
    class NotificationNotificationmessageNotificationmessageNotificationmessage {
        +__init__()
        +get_info()
    }
    class NotificationNotificationsettings {
        +__init__()
        +get_info()
    }
```

## Section 14

```mermaid
classDiagram
    class NotificationSettings {
        +__init__()
        +_get_default_settings()
        +get_module_info()
        +get_capabilities()
        +get_dependencies()
    }
    class NotificationconfigInterface {
        +__init__()
        +get_info()
    }
    class NotificationmanagerInterface {
        +__init__()
        +get_info()
    }
    class NotificationmessageInterface {
        +__init__()
        +get_info()
    }
    class NotificationsettingsInterface {
        +__init__()
        +get_info()
    }
    class O365CreateDraftMessage {
        +_run()
    }
    class O365SendMessage {
        +_run()
    }
    class OutlookMessageLoader {
        +__init__()
        +lazy_load()
    }
```

## Section 15

```mermaid
classDiagram
    class ParsedMessageParams {
    }
    class ParsedMessagePayload {
    }
    class PostgresChatMessageHistory {
        +__init__()
        +_create_table_if_not_exists()
        +messages()
        +add_message()
        +clear()
    }
    class PushNotificationsParser {
        +handle_pubsub_push_response()
        +handle_push_response()
        +set_pubsub_push_handler()
        +set_invalidation_push_handler()
    }
    class QueuedMessage {
    }
    class RawRequestMessage {
    }
    class RawResponseMessage {
    }
    class RedisChatMessageHistory {
        +__init__()
        +key()
        +messages()
        +messages()
        +add_message()
    }
```

## Section 16

```mermaid
classDiagram
    class RemoveMessage {
        +__init__()
    }
    class RemoveUIMessage {
    }
    class RocksetChatMessageHistory {
        +_wait_until()
        +_query()
        +_create_collection()
        +_collection_exists()
        +_collection_is_ready()
    }
    class RunnableWithMessageHistory {
        +__init__()
        +config_specs()
        +get_input_schema()
        +OutputType()
        +get_output_schema()
    }
    class SQLChatMessageHistory {
        +Session()
        +__init__()
        +_create_table_if_not_exists()
        +messages()
        +get_messages()
    }
    class ScheduleMessageSchema {
    }
    class SendMessageSchema {
    }
    class SimpleMessage {
    }
```

## Section 17

```mermaid
classDiagram
    class SimpleMessageHandler {
        +__init__()
        +get_supported_types()
    }
    class SingleStoreDBChatMessageHistory {
        +__init__()
        +_sanitize_input()
        +_get_connection()
        +_create_table_if_not_exists()
        +messages()
    }
    class SlackGetMessage {
        +_run()
    }
    class SlackGetMessageSchema {
    }
    class SlackScheduleMessage {
        +_run()
    }
    class SlackSendMessage {
        +_run()
    }
    class StandardMessageRouter {
        +__init__()
        +_setup_standard_handlers()
        +track_sent_message()
        +_trim_history()
        +update_capabilities()
    }
    class StreamMessagesHandler {
        +__init__()
        +_emit()
        +_find_and_emit_messages()
        +tap_output_aiter()
        +tap_output_iter()
    }
```

## Section 18

```mermaid
classDiagram
    class StreamlitChatMessageHistory {
        +__init__()
        +messages()
        +messages()
        +add_message()
        +clear()
    }
    class SystemMessage {
        +__init__()
    }
    class SystemMessageChunk {
    }
    class SystemMessagePromptTemplate {
    }
    class TestMessageSorting {
        +test_simple_sorting()
        +test_long_form_sorting()
        +test_mypy_error_prefix()
        +test_new_file_at_the_end()
    }
    class TiDBChatMessageHistory {
        +__init__()
        +_create_table_if_not_exists()
        +_load_messages_to_cache()
        +messages()
        +add_message()
    }
    class ToolMessage {
        +coerce_args()
        +__init__()
    }
    class ToolMessageChunk {
        +__add__()
    }
    SystemMessageChunk --|> SystemMessage
    ToolMessageChunk --|> ToolMessage
```

## Section 19

```mermaid
classDiagram
    class UIMessage {
    }
    class UpstashRedisChatMessageHistory {
        +__init__()
        +key()
        +messages()
        +add_message()
        +clear()
    }
    class WSMessage {
        +json()
    }
    class WSMessageTypeError {
    }
    class XataChatMessageHistory {
        +__init__()
        +_create_table_if_not_exists()
        +add_message()
        +messages()
        +clear()
    }
    class ZepChatMessageHistory {
        +__init__()
        +messages()
        +zep_messages()
        +zep_summary()
        +_get_memory()
    }
    class ZepCloudChatMessageHistory {
        +__init__()
        +messages()
        +zep_messages()
        +zep_summary()
        +zep_facts()
    }
    class _KdtMessage {
    }
```

## Section 20

```mermaid
classDiagram
    class _StringImageMessagePromptTemplate {
        +from_template()
        +from_template_file()
        +format_messages()
        +input_variables()
        +format()
    }
    class retry_if_exception_message {
        +__init__()
    }
    class retry_if_not_exception_message {
        +__init__()
        +__call__()
    }
    retry_if_not_exception_message --|> retry_if_exception_message
```

## All Classes in Domain

- `AIMessage`
- `AIMessageChunk`
- `AIMessagePromptTemplate`
- `AstraDBChatMessageHistory`
- `AsyncMessageStreamWrapper`
- `AsyncMessagesStreamManagerWrapper`
- `AsyncPushNotificationsParser`
- `BadHttpMessage`
- `BaseChatMessageHistory`
- `BaseMessage`
- `BaseMessageChunk`
- `BaseMessageConverter`
- `BaseMessageHandler`
- `BaseMessageLike`
- `BaseMessagePromptTemplate`
- `BaseStringMessagePromptTemplate`
- `CassandraChatMessageHistory`
- `ChatMessage`
- `ChatMessageChunk`
- `ChatMessagePromptTemplate`
- `ConsoleMessage`
- `CosmosDBChatMessageHistory`
- `CreateDraftMessageSchema`
- `DefaultMessageConverter`
- `DynamoDBChatMessageHistory`
- `ElasticsearchChatMessageHistory`
- `EndOfMessage`
- `ErrorMessage`
- `FakeMessagesListChatModel`
- `FewShotChatMessagePromptTemplate`
- `FileChatMessageHistory`
- `FirestoreChatMessageHistory`
- `FunctionMessage`
- `FunctionMessageChunk`
- `GmailGetMessage`
- `GmailSendMessage`
- `HumanMessage`
- `HumanMessageChunk`
- `HumanMessagePromptTemplate`
- `IMessageChatLoader`
- `InMemoryChatMessageHistory`
- `KafkaChatMessageHistory`
- `LegacyMessageType`
- `MQTTMessage`
- `MQTTMessageInfo`
- `Message`
- `MessageBuilder`
- `MessageCompatibilityError`
- `MessageCompatibilityLayer`
- `MessageConversionError`
- `MessageConverter`
- `MessageDict`
- `MessageEntry`
- `MessageFilter`
- `MessageGraph`
- `MessageHandler`
- `MessageHandlerResult`
- `MessageHandlersCore`
- `MessageHandlersCoreCore`
- `MessageHandlersCoreCoreProcessing`
- `MessageHandlersCoreProcessing`
- `MessageHandlersHandlers`
- `MessageHandlersHandlersCore`
- `MessageHandlersHandlersHandlersCore`
- `MessageHandlersProcessing`
- `MessageHistory`
- `MessageHistoryManager`
- `MessageHistoryServices`
- `MessageHistoryServicesCore`
- `MessageHistoryServicesServices`
- `MessageHistoryServicesServicesCore`
- `MessageModels`
- `MessageModelsCore`
- `MessageModelsCoreCore`
- `MessageRouter`
- `MessageRouterCore`
- `MessageRouterCoreCore`
- `MessageState`
- `MessageStatus`
- `MessageStreamWrapper`
- `MessageType`
- `MessageTypeDemo`
- `MessageTypeTranslator`
- `MessageVersion`
- `MessageVersionDetector`
- `MessagesPlaceholder`
- `MessagesState`
- `MessagesStreamManagerWrapper`
- `MomentoChatMessageHistory`
- `MongoDBChatMessageHistory`
- `Neo4jChatMessageHistory`
- `NotificationManager`
- `NotificationManagerMethods`
- `NotificationManagerMethodsNotificationconfig`
- `NotificationManagerMethodsNotificationmanager`
- `NotificationMessage`
- `NotificationModels`
- `NotificationModelsNotificationmessage`
- `NotificationModelsNotificationmessageNotificationmessage`
- `NotificationModelsNotificationsettings`
- `NotificationNotificationmessage`
- `NotificationNotificationmessageNotificationmessage`
- `NotificationNotificationmessageNotificationmessageNotificationmessage`
- `NotificationNotificationsettings`
- `NotificationSettings`
- `NotificationconfigInterface`
- `NotificationmanagerInterface`
- `NotificationmessageInterface`
- `NotificationsettingsInterface`
- `O365CreateDraftMessage`
- `O365SendMessage`
- `OutlookMessageLoader`
- `ParsedMessageParams`
- `ParsedMessagePayload`
- `PostgresChatMessageHistory`
- `PushNotificationsParser`
- `QueuedMessage`
- `RawRequestMessage`
- `RawResponseMessage`
- `RedisChatMessageHistory`
- `RemoveMessage`
- `RemoveUIMessage`
- `RocksetChatMessageHistory`
- `RunnableWithMessageHistory`
- `SQLChatMessageHistory`
- `ScheduleMessageSchema`
- `SendMessageSchema`
- `SimpleMessage`
- `SimpleMessageHandler`
- `SingleStoreDBChatMessageHistory`
- `SlackGetMessage`
- `SlackGetMessageSchema`
- `SlackScheduleMessage`
- `SlackSendMessage`
- `StandardMessageRouter`
- `StreamMessagesHandler`
- `StreamlitChatMessageHistory`
- `SystemMessage`
- `SystemMessageChunk`
- `SystemMessagePromptTemplate`
- `TestMessageSorting`
- `TiDBChatMessageHistory`
- `ToolMessage`
- `ToolMessageChunk`
- `UIMessage`
- `UpstashRedisChatMessageHistory`
- `WSMessage`
- `WSMessageTypeError`
- `XataChatMessageHistory`
- `ZepChatMessageHistory`
- `ZepCloudChatMessageHistory`
- `_KdtMessage`
- `_StringImageMessagePromptTemplate`
- `retry_if_exception_message`
- `retry_if_not_exception_message`
