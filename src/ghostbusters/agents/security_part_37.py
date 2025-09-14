from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def _init_security_patterns(self):
    """Initialize security vulnerability patterns"""
    self.sql_injection_patterns = ['execute\\s*\\(\\s*["\\\'].*\\+.*["\\\']', 'query\\s*\\(\\s*["\\\'].*\\+.*["\\\']', 'SELECT\\s+.*\\+.*FROM', 'INSERT\\s+.*\\+.*VALUES', 'UPDATE\\s+.*SET.*\\+', 'DELETE\\s+.*WHERE.*\\+']
    self.xss_patterns = ['innerHTML\\s*=\\s*.*\\+', 'document\\.write\\s*\\(', 'eval\\s*\\(', 'setTimeout\\s*\\(\\s*["\\\'].*\\+', 'setInterval\\s*\\(\\s*["\\\'].*\\+']
    self.command_injection_patterns = ['os\\.system\\s*\\(\\s*.*\\+', 'subprocess\\.\\w+\\s*\\(\\s*.*\\+', 'exec\\s*\\(\\s*.*\\+', 'shell_exec\\s*\\(\\s*.*\\+']
    self.secret_patterns = [('password\\s*=\\s*["\\\'][^"\\\']{8,}["\\\']', 'hardcoded_password'), ('api_key\\s*=\\s*["\\\'][^"\\\']{16,}["\\\']', 'hardcoded_api_key'), ('secret\\s*=\\s*["\\\'][^"\\\']{16,}["\\\']', 'hardcoded_secret'), ('token\\s*=\\s*["\\\'][^"\\\']{20,}["\\\']', 'hardcoded_token'), ('private_key\\s*=\\s*["\\\']-----BEGIN', 'hardcoded_private_key')]
    self.crypto_patterns = [('md5\\s*\\(', 'weak_hash_md5'), ('sha1\\s*\\(', 'weak_hash_sha1'), ('DES\\s*\\(', 'weak_cipher_des'), ('RC4\\s*\\(', 'weak_cipher_rc4'), ('random\\(\\)', 'weak_random')]
    self.path_traversal_patterns = ['\\.\\./.*\\.\\.', '\\.\\.\\\\.*\\.\\.', 'file:///', '/etc/passwd', '/etc/shadow']
