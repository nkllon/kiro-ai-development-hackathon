# CLI Domain Architecture

**Total Classes**: 201

## Section 1

```mermaid
classDiagram
    class ACLCommands {
        +acl_cat()
        +acl_dryrun()
        +acl_deluser()
        +acl_genpass()
        +acl_getuser()
    }
    class AbstractCommandsParser {
        +_get_pubsub_keys()
        +parse_subcommand()
    }
    class ApiClient {
        +__init__()
        +get_info()
    }
    class ApiClientMethods {
        +__init__()
        +get_info()
    }
    class AssistantsClient {
        +__init__()
    }
    class AsyncBasicKeyCommands {
        +__delitem__()
        +__contains__()
        +__getitem__()
        +__setitem__()
    }
    class AsyncClient {
        +__init__()
        +_init_transport()
        +_init_proxy_transport()
        +_transport_for_url()
    }
    class AsyncClusterDataAccessCommands {
    }
```

## Section 2

```mermaid
classDiagram
    class AsyncClusterManagementCommands {
    }
    class AsyncClusterMultiKeyCommands {
    }
    class AsyncCommandsParser {
        +__init__()
    }
    class AsyncCoreCommands {
    }
    class AsyncDataAccessCommands {
    }
    class AsyncLibraryNotFoundError {
    }
    class AsyncManagementCommands {
    }
    class AsyncModuleCommands {
    }
    AsyncClusterManagementCommands --|> AsyncManagementCommands
    AsyncCoreCommands --|> AsyncDataAccessCommands
    AsyncCoreCommands --|> AsyncManagementCommands
    AsyncCoreCommands --|> AsyncModuleCommands
```

## Section 3

```mermaid
classDiagram
    class AsyncOpenAITextEmbedEmbeddingClient {
        +__init__()
        +_permute()
        +_batch()
        +_unbatch()
        +_kwargs_post_request()
    }
    class AsyncRedisClusterCommands {
    }
    class AsyncRedisModuleCommands {
        +ft()
    }
    class AsyncScriptCommands {
        +register_script()
    }
    class AsyncSearchCommands {
    }
    class AsyncSentinelCommands {
    }
    class AzureMLEndpointClient {
        +__init__()
        +call()
    }
    class BFCommands {
        +create()
        +add()
        +madd()
        +insert()
        +exists()
    }
    AsyncRedisClusterCommands --|> AsyncScriptCommands
    AsyncRedisClusterCommands --|> AsyncRedisModuleCommands
```

## Section 4

```mermaid
classDiagram
    class BaseClient {
        +__init__()
        +is_closed()
        +trust_env()
        +_enforce_trailing_slash()
        +_get_proxy_map()
    }
    class BasicKeyCommands {
        +append()
        +bitcount()
        +bitfield()
        +bitfield_ro()
        +bitop()
    }
    class BattleReadyChromeCommander {
        +__init__()
        +register_agent_capabilities()
        +execute_applescript()
        +get_current_page_info()
        +navigate_to_target()
    }
    class BeastDagCli {
        +__init__()
        +get_info()
    }
    class BusClient {
        +__init__()
        +get_info()
    }
    class BusClientCore {
        +__init__()
        +get_info()
    }
    class BusClientCoreCore {
        +__init__()
        +get_info()
    }
    class CFCommands {
        +create()
        +add()
        +addnx()
        +insert()
        +insertnx()
    }
```

## Section 5

```mermaid
classDiagram
    class CLICommand {
    }
    class CLIENT {
    }
    class CLIExampleRunner {
        +__init__()
        +run_command()
        +create_sample_spec()
        +cleanup_sample_files()
    }
    class CLIGeneratorCore {
        +__init__()
        +get_module_info()
        +get_capabilities()
        +get_health_status()
        +graceful_degradation()
    }
    class CLIGeneratorEngine {
        +__init__()
        +get_module_info()
        +get_capabilities()
        +get_health_status()
        +graceful_degradation()
    }
    class CLIGeneratorServices {
        +__init__()
        +register_module()
        +get_interface_metadata()
        +health_check()
        +get_health_status()
    }
    class CLIProcessing {
        +__init__()
        +process_input()
        +process_json_input()
        +process_text_input()
        +process_binary_input()
    }
    class CLIResult {
    }
```

## Section 6

```mermaid
classDiagram
    class CLISafetyLinter {
        +__init__()
        +validate_command()
        +_check_quote_balance()
        +_check_escaping()
        +_is_properly_escaped()
    }
    class CMSCommands {
        +initbydim()
        +initbyprob()
        +incrby()
        +query()
        +merge()
    }
    class Cli {
        +__init__()
        +get_info()
    }
    class CliApp {
        +_run_cli_cmd()
        +run()
        +run_subcommand()
    }
    class CliAppBaseSettings {
    }
    class CliCommands {
        +__init__()
        +get_info()
    }
    class CliCore {
        +__init__()
        +get_info()
    }
    class CliCoreCore {
        +__init__()
        +get_info()
    }
```

## Section 7

```mermaid
classDiagram
    class CliDetectionResult {
        +__init__()
        +__dict__()
        +to_json()
    }
    class CliMain {
        +__init__()
        +get_info()
    }
    class CliMainMethods {
        +__init__()
        +get_info()
    }
    class CliMutuallyExclusiveGroup {
    }
    class CliRunner {
        +__init__()
        +get_default_prog_name()
        +make_env()
        +isolation()
        +invoke()
    }
    class CliSettingsSource {
        +__init__()
        +__call__()
        +__call__()
        +__call__()
        +__call__()
    }
    class ClickException {
        +__init__()
        +format_message()
        +__str__()
        +show()
    }
    class ClickHouseDsn {
    }
```

## Section 8

```mermaid
classDiagram
    class ClickTool {
        +_selector_effective()
        +_run()
    }
    class ClickToolInput {
    }
    class Clickhouse {
        +__init__()
        +_schema()
        +embeddings()
        +escape_str()
        +_build_insert_sql()
    }
    class ClickhouseSettings {
        +__getitem__()
    }
    class ClickupAPIWrapper {
        +get_access_code_url()
        +get_access_token()
        +validate_environment()
        +attempt_parse_teams()
        +get_headers()
    }
    class ClickupAction {
        +_run()
    }
    class ClickupToolkit {
        +from_clickup_api_wrapper()
        +get_tools()
    }
    class Client {
        +__init__()
        +get_info()
    }
```

## Section 9

```mermaid
classDiagram
    class ClientCertificate {
    }
    class ClientConnectionError {
    }
    class ClientConnectionResetError {
    }
    class ClientConnectorCertificateError {
        +__init__()
        +certificate_error()
        +host()
        +port()
        +ssl()
    }
    class ClientConnectorDNSError {
    }
    class ClientConnectorError {
        +__init__()
        +os_error()
        +host()
        +port()
        +ssl()
    }
    class ClientConnectorSSLError {
    }
    class ClientCore {
        +__init__()
        +get_info()
    }
    ClientConnectionResetError --|> ClientConnectionError
    ClientConnectorDNSError --|> ClientConnectorError
```

## Section 10

```mermaid
classDiagram
    class ClientCoreCore {
        +__init__()
        +get_info()
    }
    class ClientError {
    }
    class ClientHttpProxyError {
    }
    class ClientOSError {
    }
    class ClientPayloadError {
    }
    class ClientProxyConnectionError {
    }
    class ClientRequest {
        +__init__()
        +__reset_writer()
        +_get_content_length()
        +skip_auto_headers()
        +_writer()
    }
    class ClientResponse {
        +__init__()
        +__reset_writer()
        +_writer()
        +_writer()
        +cookies()
    }
    ClientPayloadError --|> ClientError
```

## Section 11

```mermaid
classDiagram
    class ClientResponseError {
        +__init__()
        +__str__()
        +__repr__()
        +code()
        +code()
    }
    class ClientSSLError {
    }
    class ClientSession {
        +__init__()
        +__init_subclass__()
        +__del__()
        +_build_url()
        +ws_connect()
    }
    class ClientState {
    }
    class ClientTimeout {
    }
    class ClientType {
    }
    class ClientWSTimeout {
    }
    class ClientWebSocketResponse {
        +__init__()
        +_cancel_heartbeat()
        +_cancel_pong_response_cb()
        +_reset_heartbeat()
        +_send_heartbeat()
    }
```

## Section 12

```mermaid
classDiagram
    class ClusterCommands {
        +cluster()
        +readwrite()
        +readonly()
    }
    class ClusterCommandsProtocol {
    }
    class ClusterDataAccessCommands {
        +stralgo()
        +scan_iter()
    }
    class ClusterManagementCommands {
        +slaveof()
        +replicaof()
        +swapdb()
        +cluster_myid()
        +cluster_addslots()
    }
    class ClusterMultiKeyCommands {
        +_partition_keys_by_slot()
        +_partition_pairs_by_slot()
        +_execute_pipeline_by_slot()
        +_reorder_keys_by_command()
        +mget_nonatomic()
    }
    class Command {
    }
    class CommandCenter {
        +__init__()
        +get_info()
    }
    class CommandCenterCore {
        +__init__()
        +get_info()
    }
    ClusterMultiKeyCommands --|> ClusterCommandsProtocol
```

## Section 13

```mermaid
classDiagram
    class CommandCenterCoreCore {
        +__init__()
        +get_info()
    }
    class CommandCenterServices {
        +__init__()
        +get_info()
    }
    class CommandCollection {
        +__init__()
        +add_source()
        +get_command()
        +list_commands()
    }
    class CommandInfo {
        +__init__()
    }
    class CommandLineParser {
        +join()
        +split()
    }
    class Commands {
        +__init__()
        +get_info()
    }
    class CommandsParser {
        +__init__()
        +initialize()
        +get_keys()
        +_get_moveable_keys()
    }
    class CommandsProtocol {
        +execute_command()
    }
```

## Section 14

```mermaid
classDiagram
    class CompetitiveCommandCenter {
        +__init__()
        +execute_competitive_strategy()
        +respond_to_competitive_threat()
        +optimize_platform_allocation()
        +_deploy_multi_platform()
    }
    class CoreCommands {
    }
    class CronClient {
        +__init__()
    }
    class DaemonClientCore {
        +__init__()
        +get_info()
    }
    class DaemonClientCoreCore {
        +__init__()
        +get_info()
    }
    class DaemonClientCoreCoreProcessing {
        +__init__()
        +get_info()
    }
    class DaemonClientCoreProcessing {
        +__init__()
        +get_info()
    }
    class DaemonClientProcessing {
        +__init__()
        +get_info()
    }
```

## Section 15

```mermaid
classDiagram
    class DagCli {
        +__init__()
        +get_info()
    }
    class DagCliCore {
        +__init__()
        +get_info()
    }
    class DataAccessCommands {
    }
    class EmergencyCLIFix {
        +__init__()
        +validate_command()
        +sanitize_command()
        +safe_execute()
    }
    class ExeclineLexer {
        +analyse_text()
    }
    class FunctionCommands {
        +function_load()
        +function_delete()
        +function_flush()
        +function_list()
        +_fcall()
    }
    class GeoCommands {
        +geoadd()
        +geodist()
        +geohash()
        +geopos()
        +georadius()
    }
    class GoogleApiClient {
        +__post_init__()
        +validate_channel_or_videoIds_is_set()
        +_load_credentials()
    }
    DataAccessCommands --|> GeoCommands
```

## Section 16

```mermaid
classDiagram
    class HTTPClientError {
    }
    class HashCommands {
        +hdel()
        +hexists()
        +hget()
        +hgetall()
        +hgetdel()
    }
    class HttpClient {
        +__init__()
    }
    class HyperlogCommands {
        +pfadd()
        +pfcount()
        +pfmerge()
    }
    class IPCClient {
        +__init__()
        +__enter__()
        +__exit__()
    }
    class ISortCommand {
        +initialize_options()
        +finalize_options()
        +distribution_files()
        +run()
    }
    class InteractiveNegotiationCLI {
        +__init__()
        +start_negotiation_session()
        +_present_situation()
        +_conduct_interactive_negotiation()
        +_handle_information_request()
    }
    class InvalidUrlClientError {
    }
```

## Section 17

```mermaid
classDiagram
    class InvalidUrlRedirectClientError {
    }
    class JSONCommands {
        +arrappend()
        +arrindex()
        +arrinsert()
        +arrlen()
        +arrpop()
    }
    class LakeFSClient {
        +__init__()
        +ls_objects()
        +is_presign_supported()
    }
    class LangGraphClient {
        +__init__()
    }
    class ListCommands {
        +blpop()
        +brpop()
        +brpoplpush()
        +blmpop()
        +lmpop()
    }
    class MDCLinter {
        +__init__()
        +log_violation()
        +log_warning()
        +validate_yaml_frontmatter()
        +validate_markdown_content()
    }
    class ManagementCommands {
        +auth()
        +bgrewriteaof()
        +bgsave()
        +role()
        +client_kill()
    }
    class ModuleCommands {
        +module_load()
        +module_loadex()
        +module_unload()
        +module_list()
        +command_info()
    }
```

## Section 18

```mermaid
classDiagram
    class NeuralDBClientVectorStore {
        +__init__()
        +similarity_search()
        +insert()
        +remove_documents()
    }
    class NodeCommands {
        +__init__()
        +append()
        +write()
        +read()
    }
    class NonHttpUrlClientError {
    }
    class NonHttpUrlRedirectClientError {
    }
    class NucliaDB {
        +__init__()
        +is_local()
        +kb_url()
        +add_texts()
        +delete()
    }
    class NucliaLoader {
        +__init__()
        +load()
    }
    class NucliaTextTransformer {
        +__init__()
        +transform_documents()
    }
    class NucliaUnderstandingAPI {
        +__init__()
        +_run()
        +_pushText()
        +_pushFile()
        +_pushField()
    }
    NonHttpUrlRedirectClientError --|> NonHttpUrlClientError
```

## Section 19

```mermaid
classDiagram
    class PahoClientMode {
    }
    class ParentCommand {
        +__init__()
    }
    class PathwayVectorClient {
        +__init__()
        +add_texts()
        +from_texts()
        +similarity_search()
        +similarity_search_with_score()
    }
    class PipelineCommand {
        +__init__()
        +__repr__()
    }
    class PubSubCommands {
        +publish()
        +spublish()
        +pubsub_channels()
        +pubsub_shardchannels()
        +pubsub_numpat()
    }
    class RedirectClientError {
    }
    class RedisClusterCommands {
    }
    class RedisModuleCommands {
        +json()
        +ft()
        +ts()
        +bf()
        +cf()
    }
    RedisClusterCommands --|> PubSubCommands
    RedisClusterCommands --|> RedisModuleCommands
```

## Section 20

```mermaid
classDiagram
    class RunsClient {
        +__init__()
        +stream()
        +stream()
        +stream()
        +join_stream()
    }
    class SafeCLIExecutor {
        +__init__()
        +_setup_logging()
        +validate_command()
        +sanitize_command()
        +check_cli_availability()
    }
    class ScriptCommands {
        +_eval()
        +eval()
        +eval_ro()
        +_evalsha()
        +evalsha()
    }
    class SearchCommands {
        +_parse_results()
        +_parse_info()
        +_parse_search()
        +_parse_aggregate()
        +_parse_profile()
    }
    class SentinelCommands {
        +sentinel()
        +sentinel_get_master_addr_by_name()
        +sentinel_master()
        +sentinel_masters()
        +sentinel_monitor()
    }
    class SetCommands {
        +sadd()
        +scard()
        +sdiff()
        +sdiffstore()
        +sinter()
    }
    class ShellCommandFix {
        +__init__()
        +validate_command()
        +sanitize_command()
        +safe_execute()
    }
    class SortedSetCommands {
        +zadd()
        +zcard()
        +zcount()
        +zdiff()
        +zdiffstore()
    }
```

## Section 21

```mermaid
classDiagram
    class StoreClient {
        +__init__()
    }
    class StreamCommands {
        +xack()
        +xackdel()
        +xadd()
        +xautoclaim()
        +xclaim()
    }
    class StubgenCliParseSuite {
        +test_walk_packages()
    }
    class SyncAssistantsClient {
        +__init__()
        +get()
        +get_graph()
        +get_schemas()
        +get_subgraphs()
    }
    class SyncCronClient {
        +__init__()
        +create_for_thread()
        +create()
        +delete()
        +search()
    }
    class SyncHttpClient {
        +__init__()
        +get()
        +post()
        +put()
        +patch()
    }
    class SyncLangGraphClient {
        +__init__()
        +__enter__()
        +__exit__()
        +close()
    }
    class SyncRunsClient {
        +__init__()
        +stream()
        +stream()
        +stream()
        +create()
    }
```

## Section 22

```mermaid
classDiagram
    class SyncStoreClient {
        +__init__()
        +put_item()
        +get_item()
        +delete_item()
        +search_items()
    }
    class SyncThreadsClient {
        +__init__()
        +get()
        +create()
        +update()
        +delete()
    }
    class TDigestCommands {
        +create()
        +reset()
        +add()
        +merge()
        +min()
    }
    class TOPKCommands {
        +reserve()
        +add()
        +incrby()
        +query()
        +count()
    }
    class ThreadsClient {
        +__init__()
    }
    class TimeSeriesCommands {
        +create()
        +alter()
        +add()
        +madd()
        +incrby()
    }
    class TinyAsyncGradientEmbeddingClient {
        +__init__()
    }
    class TinyAsyncOpenAIInfinityEmbeddingClient {
        +__init__()
        +_permute()
        +_batch()
        +_unbatch()
        +_kwargs_post_request()
    }
```

## Section 23

```mermaid
classDiagram
    class UnifiedClient {
        +__init__()
        +get_info()
    }
    class UnifiedClientCore {
        +__init__()
        +get_info()
    }
    class UnifiedClientCoreCore {
        +__init__()
        +get_info()
    }
    class UnixClientConnectorError {
        +__init__()
        +path()
        +__str__()
    }
    class UseClientDefault {
    }
    class VectorSetCommands {
        +vadd()
        +vsim()
        +vdim()
        +vcard()
        +vrem()
    }
    class _BaseCommand {
    }
    class _CliExplicitFlag {
    }
```

## Section 24

```mermaid
classDiagram
    class _CliImplicitFlag {
    }
    class _CliInternalArgParser {
        +__init__()
        +error()
    }
    class _CliPositionalArg {
    }
    class _CliSubCommand {
    }
    class _CliUnknownArgs {
    }
    class _DatabricksClientBase {
        +request()
        +_get()
        +_post()
        +post()
        +llm()
    }
    class _DatabricksClusterDriverProxyClient {
        +set_api_url()
        +post()
    }
    class _DatabricksServingEndpointClient {
        +__init__()
        +llm()
        +set_api_url()
        +post()
    }
    _DatabricksClusterDriverProxyClient --|> _DatabricksClientBase
    _DatabricksServingEndpointClient --|> _DatabricksClientBase
```

## Section 25

```mermaid
classDiagram
    class _MemcachedClient {
        +get()
        +set()
    }
    class _MinimaxEndpointClient {
        +set_api_url()
        +post()
    }
    class _MoonshotClient {
        +completion()
    }
    class _MultiCommand {
    }
    class _SolarClient {
        +completion()
    }
    class _SparkLLMClient {
        +__init__()
        +_create_url()
        +run()
        +arun()
        +on_error()
    }
    class _VectorStoreClient {
        +__init__()
        +query()
        +get_vectorstore_statistics()
        +get_input_files()
    }
    class build_clib {
        +initialize_options()
        +finalize_options()
        +have_f_sources()
        +have_cxx_sources()
        +run()
    }
```

## Section 26

```mermaid
classDiagram
    class install_clib {
        +initialize_options()
        +finalize_options()
        +run()
        +get_outputs()
    }
```

## All Classes in Domain

- `ACLCommands`
- `AbstractCommandsParser`
- `ApiClient`
- `ApiClientMethods`
- `AssistantsClient`
- `AsyncBasicKeyCommands`
- `AsyncClient`
- `AsyncClusterDataAccessCommands`
- `AsyncClusterManagementCommands`
- `AsyncClusterMultiKeyCommands`
- `AsyncCommandsParser`
- `AsyncCoreCommands`
- `AsyncDataAccessCommands`
- `AsyncLibraryNotFoundError`
- `AsyncManagementCommands`
- `AsyncModuleCommands`
- `AsyncOpenAITextEmbedEmbeddingClient`
- `AsyncRedisClusterCommands`
- `AsyncRedisModuleCommands`
- `AsyncScriptCommands`
- `AsyncSearchCommands`
- `AsyncSentinelCommands`
- `AzureMLEndpointClient`
- `BFCommands`
- `BaseClient`
- `BasicKeyCommands`
- `BattleReadyChromeCommander`
- `BeastDagCli`
- `BusClient`
- `BusClientCore`
- `BusClientCoreCore`
- `CFCommands`
- `CLICommand`
- `CLIENT`
- `CLIExampleRunner`
- `CLIGeneratorCore`
- `CLIGeneratorEngine`
- `CLIGeneratorServices`
- `CLIProcessing`
- `CLIResult`
- `CLISafetyLinter`
- `CMSCommands`
- `Cli`
- `CliApp`
- `CliAppBaseSettings`
- `CliCommands`
- `CliCore`
- `CliCoreCore`
- `CliDetectionResult`
- `CliMain`
- `CliMainMethods`
- `CliMutuallyExclusiveGroup`
- `CliRunner`
- `CliSettingsSource`
- `ClickException`
- `ClickHouseDsn`
- `ClickTool`
- `ClickToolInput`
- `Clickhouse`
- `ClickhouseSettings`
- `ClickupAPIWrapper`
- `ClickupAction`
- `ClickupToolkit`
- `Client`
- `ClientCertificate`
- `ClientConnectionError`
- `ClientConnectionResetError`
- `ClientConnectorCertificateError`
- `ClientConnectorDNSError`
- `ClientConnectorError`
- `ClientConnectorSSLError`
- `ClientCore`
- `ClientCoreCore`
- `ClientError`
- `ClientHttpProxyError`
- `ClientOSError`
- `ClientPayloadError`
- `ClientProxyConnectionError`
- `ClientRequest`
- `ClientResponse`
- `ClientResponseError`
- `ClientSSLError`
- `ClientSession`
- `ClientState`
- `ClientTimeout`
- `ClientType`
- `ClientWSTimeout`
- `ClientWebSocketResponse`
- `ClusterCommands`
- `ClusterCommandsProtocol`
- `ClusterDataAccessCommands`
- `ClusterManagementCommands`
- `ClusterMultiKeyCommands`
- `Command`
- `CommandCenter`
- `CommandCenterCore`
- `CommandCenterCoreCore`
- `CommandCenterServices`
- `CommandCollection`
- `CommandInfo`
- `CommandLineParser`
- `Commands`
- `CommandsParser`
- `CommandsProtocol`
- `CompetitiveCommandCenter`
- `CoreCommands`
- `CronClient`
- `DaemonClientCore`
- `DaemonClientCoreCore`
- `DaemonClientCoreCoreProcessing`
- `DaemonClientCoreProcessing`
- `DaemonClientProcessing`
- `DagCli`
- `DagCliCore`
- `DataAccessCommands`
- `EmergencyCLIFix`
- `ExeclineLexer`
- `FunctionCommands`
- `GeoCommands`
- `GoogleApiClient`
- `HTTPClientError`
- `HashCommands`
- `HttpClient`
- `HyperlogCommands`
- `IPCClient`
- `ISortCommand`
- `InteractiveNegotiationCLI`
- `InvalidUrlClientError`
- `InvalidUrlRedirectClientError`
- `JSONCommands`
- `LakeFSClient`
- `LangGraphClient`
- `ListCommands`
- `MDCLinter`
- `ManagementCommands`
- `ModuleCommands`
- `NeuralDBClientVectorStore`
- `NodeCommands`
- `NonHttpUrlClientError`
- `NonHttpUrlRedirectClientError`
- `NucliaDB`
- `NucliaLoader`
- `NucliaTextTransformer`
- `NucliaUnderstandingAPI`
- `PahoClientMode`
- `ParentCommand`
- `PathwayVectorClient`
- `PipelineCommand`
- `PubSubCommands`
- `RedirectClientError`
- `RedisClusterCommands`
- `RedisModuleCommands`
- `RunsClient`
- `SafeCLIExecutor`
- `ScriptCommands`
- `SearchCommands`
- `SentinelCommands`
- `SetCommands`
- `ShellCommandFix`
- `SortedSetCommands`
- `StoreClient`
- `StreamCommands`
- `StubgenCliParseSuite`
- `SyncAssistantsClient`
- `SyncCronClient`
- `SyncHttpClient`
- `SyncLangGraphClient`
- `SyncRunsClient`
- `SyncStoreClient`
- `SyncThreadsClient`
- `TDigestCommands`
- `TOPKCommands`
- `ThreadsClient`
- `TimeSeriesCommands`
- `TinyAsyncGradientEmbeddingClient`
- `TinyAsyncOpenAIInfinityEmbeddingClient`
- `UnifiedClient`
- `UnifiedClientCore`
- `UnifiedClientCoreCore`
- `UnixClientConnectorError`
- `UseClientDefault`
- `VectorSetCommands`
- `_BaseCommand`
- `_CliExplicitFlag`
- `_CliImplicitFlag`
- `_CliInternalArgParser`
- `_CliPositionalArg`
- `_CliSubCommand`
- `_CliUnknownArgs`
- `_DatabricksClientBase`
- `_DatabricksClusterDriverProxyClient`
- `_DatabricksServingEndpointClient`
- `_MemcachedClient`
- `_MinimaxEndpointClient`
- `_MoonshotClient`
- `_MultiCommand`
- `_SolarClient`
- `_SparkLLMClient`
- `_VectorStoreClient`
- `build_clib`
- `install_clib`
