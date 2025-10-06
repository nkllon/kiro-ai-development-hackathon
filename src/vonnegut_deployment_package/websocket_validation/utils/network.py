"""
Network utilities for WebSocket validation framework.
"""

import asyncio
import ssl
import time
from typing import Dict, Optional, Tuple, Any
import aiohttp
import websockets
from urllib.parse import urlparse

from ..models import EndpointResult, HandshakeResult
from ..config import ValidationConfig
from .logging import get_logger
from .errors import create_network_error, create_timeout_error


async def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    verify_ssl: bool = True
) -> EndpointResult:
    """
    Make an HTTP request and return detailed results.
    
    Args:
        url: Request URL
        method: HTTP method
        headers: Optional request headers
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        EndpointResult: Detailed request results
    """
    logger = get_logger(__name__)
    start_time = time.time()
    
    # Prepare headers
    request_headers = {
        "User-Agent": "WebSocket-Validation-Framework/1.0.0",
        **(headers or {})
    }
    
    try:
        # Configure SSL context
        ssl_context = None
        if not verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create timeout configuration
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        
        async with aiohttp.ClientSession(
            timeout=timeout_config,
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            
            async with session.request(
                method=method,
                url=url,
                headers=request_headers
            ) as response:
                
                response_time = time.time() - start_time
                response_body = await response.text()
                
                # Convert headers to dict
                response_headers = dict(response.headers)
                
                result = EndpointResult(
                    url=url,
                    method=method,
                    status_code=response.status,
                    headers=response_headers,
                    response_time=response_time,
                    response_body=response_body
                )
                
                logger.info(f"HTTP {method} {url} -> {response.status} ({response_time:.2f}s)")
                return result
                
    except asyncio.TimeoutError as e:
        response_time = time.time() - start_time
        logger.error(f"Request timeout for {method} {url} after {response_time:.2f}s")
        
        return EndpointResult(
            url=url,
            method=method,
            status_code=0,
            response_time=response_time,
            error_message=f"Request timeout after {timeout}s"
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"Request failed for {method} {url}: {e}")
        
        return EndpointResult(
            url=url,
            method=method,
            status_code=0,
            response_time=response_time,
            error_message=str(e)
        )


async def test_websocket_connection(
    url: str,
    timeout: float = 10.0,
    verify_ssl: bool = True,
    extra_headers: Optional[Dict[str, str]] = None
) -> HandshakeResult:
    """
    Test WebSocket connection and handshake.
    
    Args:
        url: WebSocket URL
        timeout: Connection timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        extra_headers: Optional extra headers for handshake
        
    Returns:
        HandshakeResult: WebSocket handshake results
    """
    logger = get_logger(__name__)
    start_time = time.time()
    
    try:
        # Prepare headers
        headers = {
            "User-Agent": "WebSocket-Validation-Framework/1.0.0",
            **(extra_headers or {})
        }
        
        # Configure SSL context
        ssl_context = None
        if not verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Attempt WebSocket connection
        async with websockets.connect(
            url,
            extra_headers=headers,
            ssl=ssl_context,
            open_timeout=timeout,
            close_timeout=5.0
        ) as websocket:
            
            response_time = time.time() - start_time
            
            # Extract handshake information
            handshake_result = HandshakeResult(
                endpoint_url=url,
                handshake_success=True,
                upgrade_header="websocket",
                connection_header="upgrade",
                websocket_accept=websocket.response_headers.get("Sec-WebSocket-Accept"),
                websocket_protocol=websocket.response_headers.get("Sec-WebSocket-Protocol"),
                response_time=response_time
            )
            
            logger.info(f"WebSocket connection successful: {url} ({response_time:.2f}s)")
            return handshake_result
            
    except websockets.exceptions.InvalidStatusCode as e:
        response_time = time.time() - start_time
        logger.error(f"WebSocket handshake failed for {url}: HTTP {e.status_code}")
        
        return HandshakeResult(
            endpoint_url=url,
            handshake_success=False,
            error_message=f"HTTP {e.status_code}: {e}",
            response_time=response_time
        )
        
    except websockets.exceptions.InvalidHandshake as e:
        response_time = time.time() - start_time
        logger.error(f"WebSocket handshake invalid for {url}: {e}")
        
        return HandshakeResult(
            endpoint_url=url,
            handshake_success=False,
            error_message=f"Invalid handshake: {e}",
            response_time=response_time
        )
        
    except asyncio.TimeoutError:
        response_time = time.time() - start_time
        logger.error(f"WebSocket connection timeout for {url} after {response_time:.2f}s")
        
        return HandshakeResult(
            endpoint_url=url,
            handshake_success=False,
            error_message=f"Connection timeout after {timeout}s",
            response_time=response_time
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        logger.error(f"WebSocket connection failed for {url}: {e}")
        
        return HandshakeResult(
            endpoint_url=url,
            handshake_success=False,
            error_message=str(e),
            response_time=response_time
        )


async def test_websocket_upgrade_request(
    url: str,
    timeout: float = 30.0,
    verify_ssl: bool = True
) -> EndpointResult:
    """
    Test WebSocket upgrade request using HTTP.
    
    This tests the initial HTTP request that should be upgraded to WebSocket.
    
    Args:
        url: WebSocket URL (will be converted to HTTP for upgrade test)
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        EndpointResult: HTTP upgrade request results
    """
    logger = get_logger(__name__)
    
    # Convert WebSocket URL to HTTP URL
    parsed = urlparse(url)
    if parsed.scheme == "wss":
        http_url = url.replace("wss://", "https://")
    elif parsed.scheme == "ws":
        http_url = url.replace("ws://", "http://")
    else:
        http_url = url
    
    # WebSocket upgrade headers
    upgrade_headers = {
        "Connection": "Upgrade",
        "Upgrade": "websocket",
        "Sec-WebSocket-Version": "13",
        "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",  # Standard test key
        "User-Agent": "WebSocket-Validation-Framework/1.0.0"
    }
    
    result = await make_request(
        url=http_url,
        method="GET",
        headers=upgrade_headers,
        timeout=timeout,
        verify_ssl=verify_ssl
    )
    
    # Check if this looks like a WebSocket upgrade response
    if result.status_code == 101:
        upgrade_header = result.headers.get("upgrade", "").lower()
        connection_header = result.headers.get("connection", "").lower()
        
        result.websocket_upgrade_success = (
            upgrade_header == "websocket" and
            "upgrade" in connection_header
        )
        
        if result.websocket_upgrade_success:
            result.websocket_protocol = result.headers.get("sec-websocket-protocol")
            logger.info(f"WebSocket upgrade successful for {http_url}")
        else:
            logger.warning(f"WebSocket upgrade headers incorrect for {http_url}")
    else:
        logger.info(f"WebSocket upgrade not supported for {http_url} (HTTP {result.status_code})")
    
    return result


def parse_websocket_url(url: str) -> Tuple[str, str, int, str]:
    """
    Parse WebSocket URL into components.
    
    Args:
        url: WebSocket URL to parse
        
    Returns:
        Tuple of (scheme, host, port, path)
    """
    parsed = urlparse(url)
    
    scheme = parsed.scheme or "ws"
    host = parsed.hostname or "localhost"
    
    # Determine default port based on scheme
    if parsed.port:
        port = parsed.port
    elif scheme == "wss":
        port = 443
    elif scheme == "ws":
        port = 80
    else:
        port = 80
    
    path = parsed.path or "/"
    
    return scheme, host, port, path


def is_websocket_url(url: str) -> bool:
    """
    Check if URL is a WebSocket URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is WebSocket, False otherwise
    """
    parsed = urlparse(url)
    return parsed.scheme in ["ws", "wss"]


def convert_to_websocket_url(http_url: str) -> str:
    """
    Convert HTTP URL to WebSocket URL.
    
    Args:
        http_url: HTTP URL to convert
        
    Returns:
        WebSocket URL
    """
    if http_url.startswith("https://"):
        return http_url.replace("https://", "wss://")
    elif http_url.startswith("http://"):
        return http_url.replace("http://", "ws://")
    else:
        return http_url


def convert_to_http_url(websocket_url: str) -> str:
    """
    Convert WebSocket URL to HTTP URL.
    
    Args:
        websocket_url: WebSocket URL to convert
        
    Returns:
        HTTP URL
    """
    if websocket_url.startswith("wss://"):
        return websocket_url.replace("wss://", "https://")
    elif websocket_url.startswith("ws://"):
        return websocket_url.replace("ws://", "http://")
    else:
        return websocket_url