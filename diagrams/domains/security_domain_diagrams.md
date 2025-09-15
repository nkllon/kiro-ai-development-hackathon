# Security Domain Architecture

**Total Classes**: 73

## Section 1

```mermaid
classDiagram
    class AsyncReAuthConnectionListener {
    }
    class Auth {
        +__init__()
        +get_info()
    }
    class AuthBase {
        +__call__()
    }
    class AuthContext {
    }
    class AuthCredentials {
    }
    class AuthHandler {
        +__init__()
        +__call__()
        +__repr__()
        +_make_uniform()
        +_key_from_url()
    }
    class AuthModels {
        +__init__()
        +get_info()
    }
    class AuthModelsMethods {
        +__init__()
        +get_info()
    }
    AuthHandler --|> AuthBase
```

## Section 2

```mermaid
classDiagram
    class AuthModelsMethodsAuthconfig {
        +__init__()
        +get_info()
    }
    class AuthModelsMethodsAuthcredentials {
        +__init__()
        +get_info()
    }
    class AuthModelsMethodsAuthresult {
        +__init__()
        +get_info()
    }
    class AuthModelsMethodsAuthsession {
        +__init__()
        +get_info()
    }
    class AuthParameter {
    }
    class AuthServiceCore {
        +__init__()
        +get_info()
    }
    class AuthServiceServices {
        +__init__()
        +get_info()
    }
    class AuthServiceServicesCore {
        +__init__()
        +get_info()
    }
```

## Section 3

```mermaid
classDiagram
    class AuthServiceServicesCoreCore {
        +__init__()
        +get_info()
    }
    class AuthServiceServicesServices {
        +__init__()
        +get_info()
    }
    class AuthServiceServicesServicesCore {
        +__init__()
        +get_info()
    }
    class AuthSessionManager {
        +__init__()
        +get_info()
    }
    class AuthconfigInterface {
        +__init__()
        +get_info()
    }
    class AuthcredentialsInterface {
        +__init__()
        +get_info()
    }
    class AuthenticationError {
    }
    class AuthenticationWrongNumberOfArgsError {
    }
```

## Section 4

```mermaid
classDiagram
    class AuthorizationError {
    }
    class AuthorizationRequest {
    }
    class AuthorizationResponse {
    }
    class AuthorizationStatus {
    }
    class AuthresultInterface {
        +__init__()
        +get_info()
    }
    class AuthsessionInterface {
        +__init__()
        +get_info()
    }
    class BaseAuthContext {
    }
    class BasicAuth {
        +__init__()
        +auth_flow()
        +_build_auth_header()
    }
```

## Section 5

```mermaid
classDiagram
    class DigestAuth {
        +__init__()
        +auth_flow()
        +_parse_challenge()
        +_build_auth_header()
        +_get_client_nonce()
    }
    class DigestAuthChallenge {
    }
    class DigestAuthMiddleware {
        +__init__()
        +_in_protection_space()
        +_authenticate()
    }
    class FunctionAuth {
        +__init__()
        +auth_flow()
    }
    class GCPAuthorizationHandshake {
        +__init__()
        +step_1_request_authorization()
        +step_2_enterprise_admin_review()
        +step_3_verify_authorization()
        +step_4_link_project_with_authorization()
    }
    class GuessAuth {
        +__init__()
        +_handle_basic_auth_401()
        +_handle_digest_auth_401()
        +handle_401()
        +__call__()
    }
    class GuessProxyAuth {
        +__init__()
        +_handle_basic_auth_407()
        +_handle_digest_auth_407()
        +handle_407()
        +__call__()
    }
    class HTTPBasicAuth {
        +__init__()
        +__eq__()
        +__ne__()
        +__call__()
    }
    GuessProxyAuth --|> GuessAuth
```

## Section 6

```mermaid
classDiagram
    class HTTPDigestAuth {
        +__init__()
        +init_per_thread_state()
        +build_digest_header()
        +handle_redirect()
        +handle_401()
    }
    class HTTPNetworkAuthenticationRequired {
    }
    class HTTPNonAuthoritativeInformation {
    }
    class HTTPProxyAuth {
        +__call__()
    }
    class HTTPProxyAuthenticationRequired {
    }
    class HTTPProxyDigestAuth {
        +__init__()
        +stale_rejects()
        +stale_rejects()
        +init_per_thread_state()
        +handle_407()
    }
    class HTTPUnauthorized {
    }
    class JiraOauth2 {
    }
```

## Section 7

```mermaid
classDiagram
    class JiraOauth2Token {
    }
    class LangSmithAuthError {
    }
    class LayerupSecurity {
        +validate_layerup_sdk()
        +_llm_type()
        +_call()
    }
    class ManagedPassioLifeAuth {
        +__init__()
        +headers()
        +is_valid_now()
        +_http_get()
        +refresh_access_token()
    }
    class NullAuthStrategy {
        +__repr__()
        +__call__()
    }
    class OCIAuthType {
    }
    class ReAuthConnectionListener {
        +listen()
    }
    class RegisterReAuthForAsyncClusterNodes {
        +__init__()
        +listen()
    }
```

## Section 8

```mermaid
classDiagram
    class RegisterReAuthForPooledConnections {
        +__init__()
        +listen()
        +_re_auth()
        +_raise_on_error()
    }
    class RegisterReAuthForPubSub {
        +__init__()
        +listen()
        +_re_auth()
        +_raise_on_error()
    }
    class RegisterReAuthForSingleConnection {
        +__init__()
        +listen()
        +_re_auth()
        +_raise_on_error()
    }
    class RivaAuthMixin {
        +auth()
        +_validate_url()
    }
    class Security {
        +__init__()
        +get_info()
    }
    class SecurityAuditResult {
    }
    class SecurityCore {
        +__init__()
        +get_info()
    }
    class SecurityCoreCore {
        +__init__()
        +get_info()
    }
```

## Section 9

```mermaid
classDiagram
    class SecurityDetails {
    }
    class SecurityError {
    }
    class SecurityExpert {
        +__init__()
        +_init_security_patterns()
        +get_capabilities()
        +validate_confidence()
        +_check_sql_injection()
    }
    class SecurityFinding {
    }
    class SecurityIssue {
    }
    class SecurityLevel {
    }
    class SecurityManager {
        +__init__()
        +get_info()
    }
    class SecurityWarning {
    }
```

## Section 10

```mermaid
classDiagram
    class _DigestAuthChallenge {
    }
```

## All Classes in Domain

- `AsyncReAuthConnectionListener`
- `Auth`
- `AuthBase`
- `AuthContext`
- `AuthCredentials`
- `AuthHandler`
- `AuthModels`
- `AuthModelsMethods`
- `AuthModelsMethodsAuthconfig`
- `AuthModelsMethodsAuthcredentials`
- `AuthModelsMethodsAuthresult`
- `AuthModelsMethodsAuthsession`
- `AuthParameter`
- `AuthServiceCore`
- `AuthServiceServices`
- `AuthServiceServicesCore`
- `AuthServiceServicesCoreCore`
- `AuthServiceServicesServices`
- `AuthServiceServicesServicesCore`
- `AuthSessionManager`
- `AuthconfigInterface`
- `AuthcredentialsInterface`
- `AuthenticationError`
- `AuthenticationWrongNumberOfArgsError`
- `AuthorizationError`
- `AuthorizationRequest`
- `AuthorizationResponse`
- `AuthorizationStatus`
- `AuthresultInterface`
- `AuthsessionInterface`
- `BaseAuthContext`
- `BasicAuth`
- `DigestAuth`
- `DigestAuthChallenge`
- `DigestAuthMiddleware`
- `FunctionAuth`
- `GCPAuthorizationHandshake`
- `GuessAuth`
- `GuessProxyAuth`
- `HTTPBasicAuth`
- `HTTPDigestAuth`
- `HTTPNetworkAuthenticationRequired`
- `HTTPNonAuthoritativeInformation`
- `HTTPProxyAuth`
- `HTTPProxyAuthenticationRequired`
- `HTTPProxyDigestAuth`
- `HTTPUnauthorized`
- `JiraOauth2`
- `JiraOauth2Token`
- `LangSmithAuthError`
- `LayerupSecurity`
- `ManagedPassioLifeAuth`
- `NullAuthStrategy`
- `OCIAuthType`
- `ReAuthConnectionListener`
- `RegisterReAuthForAsyncClusterNodes`
- `RegisterReAuthForPooledConnections`
- `RegisterReAuthForPubSub`
- `RegisterReAuthForSingleConnection`
- `RivaAuthMixin`
- `Security`
- `SecurityAuditResult`
- `SecurityCore`
- `SecurityCoreCore`
- `SecurityDetails`
- `SecurityError`
- `SecurityExpert`
- `SecurityFinding`
- `SecurityIssue`
- `SecurityLevel`
- `SecurityManager`
- `SecurityWarning`
- `_DigestAuthChallenge`
