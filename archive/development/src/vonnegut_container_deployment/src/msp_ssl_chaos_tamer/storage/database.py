"""
Certificate database operations for MSP SSL Chaos Tamer

Provides SQLite database schema and operations with proper indexing,
performance optimization, and data integrity for certificate inventory.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from contextlib import contextmanager
from dataclasses import asdict

from ..core.interfaces import ReflectiveModule
from ..core.models import Certificate, Client, MSP, CertificateStatus


class CertificateDatabase(ReflectiveModule):
    """
    SQLite database for certificate inventory management
    
    Provides high-performance certificate storage with proper indexing,
    data integrity constraints, and optimized queries for MSP operations.
    """
    
    def __init__(self, db_path: str = "certificates.db"):
        super().__init__()
        self.db_path = db_path
        self.logger = logging.getLogger("msp_ssl.database")
        
        # Initialize database
        self._initialize_database()
        self.logger.info(f"Certificate database initialized: {db_path}")
    
    def _initialize_database(self) -> None:
        """Initialize database schema with tables and indexes"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create certificates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    ca_provider TEXT NOT NULL,
                    issue_date TEXT,
                    expiration_date TEXT,
                    certificate_chain TEXT,  -- JSON array
                    private_key_fingerprint TEXT,
                    status TEXT NOT NULL,
                    renewal_policy TEXT,  -- JSON object
                    emergency_contacts TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Create clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    msp_id TEXT NOT NULL,
                    domains TEXT,  -- JSON array
                    preferred_ca TEXT NOT NULL,
                    billing_contact TEXT,
                    technical_contact TEXT,
                    emergency_contact TEXT,
                    certificate_policies TEXT,  -- JSON array
                    portal_access_enabled INTEGER NOT NULL DEFAULT 1,
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (msp_id) REFERENCES msps (id)
                )
            """)
            
            # Create MSPs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS msps (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    ca_credentials TEXT,  -- JSON object (encrypted references)
                    clients TEXT,  -- JSON array of client IDs
                    default_policies TEXT,  -- JSON array
                    integration_settings TEXT,  -- JSON object
                    branding_config TEXT,  -- JSON object
                    contact_info TEXT,  -- JSON object
                    metadata TEXT,  -- JSON object
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create performance indexes
            self._create_indexes(cursor)
            
            # Create views for common queries
            self._create_views(cursor)
            
            conn.commit()
    
    def _create_indexes(self, cursor: sqlite3.Cursor) -> None:
        """Create database indexes for performance optimization"""
        
        # Certificate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_domain ON certificates (domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_client_id ON certificates (client_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_ca_provider ON certificates (ca_provider)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_status ON certificates (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_expiration ON certificates (expiration_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_created ON certificates (created_at)")
        
        # Client indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_msp_id ON clients (msp_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients (name)")
        
        # MSP indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_msps_name ON msps (name)")
        
        # Composite indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cert_client_status ON certificates (client_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cert_expiration_status ON certificates (expiration_date, status)")
    
    def _create_views(self, cursor: sqlite3.Cursor) -> None:
        """Create database views for common queries"""
        
        # Certificate summary view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS certificate_summary AS
            SELECT 
                c.id,
                c.domain,
                c.client_id,
                cl.name as client_name,
                cl.msp_id,
                m.name as msp_name,
                c.ca_provider,
                c.status,
                c.expiration_date,
                c.created_at,
                c.updated_at
            FROM certificates c
            JOIN clients cl ON c.client_id = cl.id
            JOIN msps m ON cl.msp_id = m.id
        """)
        
        # Expiring certificates view
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS expiring_certificates AS
            SELECT *
            FROM certificate_summary
            WHERE expiration_date IS NOT NULL
            AND julianday(expiration_date) <= julianday('now', '+30 days')
            AND status NOT IN ('expired', 'revoked')
            ORDER BY expiration_date ASC
        """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _serialize_json_field(self, value: Any) -> Optional[str]:
        """Serialize value to JSON string for database storage"""
        if value is None:
            return None
        return json.dumps(value)
    
    def _deserialize_json_field(self, value: Optional[str]) -> Any:
        """Deserialize JSON string from database"""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None
    
    # Certificate operations
    def create_certificate(self, certificate: Certificate) -> bool:
        """
        Create a new certificate record
        
        Args:
            certificate: Certificate object to store
            
        Returns:
            bool: True if creation successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO certificates (
                        id, domain, client_id, ca_provider, issue_date, expiration_date,
                        certificate_chain, private_key_fingerprint, status, renewal_policy,
                        emergency_contacts, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    certificate.id,
                    certificate.domain,
                    certificate.client_id,
                    certificate.ca_provider,
                    certificate.issue_date.isoformat() if certificate.issue_date else None,
                    certificate.expiration_date.isoformat() if certificate.expiration_date else None,
                    self._serialize_json_field(certificate.certificate_chain),
                    certificate.private_key_fingerprint,
                    certificate.status.value,
                    self._serialize_json_field(certificate.renewal_policy),
                    self._serialize_json_field(certificate.emergency_contacts),
                    self._serialize_json_field(certificate.metadata),
                    certificate.created_at.isoformat(),
                    certificate.updated_at.isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Created certificate record: {certificate.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create certificate {certificate.id}: {e}")
            return False
    
    def get_certificate(self, certificate_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve certificate by ID
        
        Args:
            certificate_id: Certificate ID to retrieve
            
        Returns:
            Dict containing certificate data, None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM certificates WHERE id = ?", (certificate_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_certificate_dict(row)
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve certificate {certificate_id}: {e}")
            return None
    
    def update_certificate(self, certificate: Certificate) -> bool:
        """
        Update existing certificate record
        
        Args:
            certificate: Certificate object with updated data
            
        Returns:
            bool: True if update successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE certificates SET
                        domain = ?, client_id = ?, ca_provider = ?, issue_date = ?,
                        expiration_date = ?, certificate_chain = ?, private_key_fingerprint = ?,
                        status = ?, renewal_policy = ?, emergency_contacts = ?,
                        metadata = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    certificate.domain,
                    certificate.client_id,
                    certificate.ca_provider,
                    certificate.issue_date.isoformat() if certificate.issue_date else None,
                    certificate.expiration_date.isoformat() if certificate.expiration_date else None,
                    self._serialize_json_field(certificate.certificate_chain),
                    certificate.private_key_fingerprint,
                    certificate.status.value,
                    self._serialize_json_field(certificate.renewal_policy),
                    self._serialize_json_field(certificate.emergency_contacts),
                    self._serialize_json_field(certificate.metadata),
                    datetime.utcnow().isoformat(),
                    certificate.id
                ))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated certificate record: {certificate.id}")
                    return True
                else:
                    self.logger.warning(f"Certificate not found for update: {certificate.id}")
                    return False
                
        except Exception as e:
            self.logger.error(f"Failed to update certificate {certificate.id}: {e}")
            return False
    
    def delete_certificate(self, certificate_id: str) -> bool:
        """
        Delete certificate record
        
        Args:
            certificate_id: Certificate ID to delete
            
        Returns:
            bool: True if deletion successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM certificates WHERE id = ?", (certificate_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted certificate record: {certificate_id}")
                    return True
                else:
                    self.logger.warning(f"Certificate not found for deletion: {certificate_id}")
                    return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete certificate {certificate_id}: {e}")
            return False
    
    def get_client_certificates(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get all certificates for a client
        
        Args:
            client_id: Client ID
            
        Returns:
            List of certificate dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM certificates WHERE client_id = ? ORDER BY expiration_date ASC",
                    (client_id,)
                )
                
                rows = cursor.fetchall()
                return [self._row_to_certificate_dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve certificates for client {client_id}: {e}")
            return []
    
    def get_expiring_certificates(self, days_threshold: int = 30) -> List[Dict[str, Any]]:
        """
        Get certificates expiring within threshold
        
        Args:
            days_threshold: Days before expiration to include
            
        Returns:
            List of expiring certificate dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM certificate_summary
                    WHERE expiration_date IS NOT NULL
                    AND julianday(expiration_date) <= julianday('now', '+' || ? || ' days')
                    AND status NOT IN ('expired', 'revoked')
                    ORDER BY expiration_date ASC
                """, (days_threshold,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve expiring certificates: {e}")
            return []
    
    def get_certificates_by_status(self, status: CertificateStatus) -> List[Dict[str, Any]]:
        """
        Get certificates by status
        
        Args:
            status: Certificate status to filter by
            
        Returns:
            List of certificate dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM certificates WHERE status = ? ORDER BY updated_at DESC",
                    (status.value,)
                )
                
                rows = cursor.fetchall()
                return [self._row_to_certificate_dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve certificates by status {status}: {e}")
            return []
    
    def _row_to_certificate_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to certificate dictionary"""
        return {
            "id": row["id"],
            "domain": row["domain"],
            "client_id": row["client_id"],
            "ca_provider": row["ca_provider"],
            "issue_date": row["issue_date"],
            "expiration_date": row["expiration_date"],
            "certificate_chain": self._deserialize_json_field(row["certificate_chain"]),
            "private_key_fingerprint": row["private_key_fingerprint"],
            "status": row["status"],
            "renewal_policy": self._deserialize_json_field(row["renewal_policy"]),
            "emergency_contacts": self._deserialize_json_field(row["emergency_contacts"]),
            "metadata": self._deserialize_json_field(row["metadata"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # Client operations
    def create_client(self, client: Client) -> bool:
        """Create a new client record"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO clients (
                        id, name, msp_id, domains, preferred_ca, billing_contact,
                        technical_contact, emergency_contact, certificate_policies,
                        portal_access_enabled, metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    client.id,
                    client.name,
                    client.msp_id,
                    self._serialize_json_field(client.domains),
                    client.preferred_ca,
                    client.billing_contact,
                    client.technical_contact,
                    client.emergency_contact,
                    self._serialize_json_field(client.certificate_policies),
                    1 if client.portal_access_enabled else 0,
                    self._serialize_json_field(client.metadata),
                    client.created_at.isoformat(),
                    client.updated_at.isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Created client record: {client.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create client {client.id}: {e}")
            return False
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve client by ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return self._row_to_client_dict(row)
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve client {client_id}: {e}")
            return None
    
    def _row_to_client_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to client dictionary"""
        return {
            "id": row["id"],
            "name": row["name"],
            "msp_id": row["msp_id"],
            "domains": self._deserialize_json_field(row["domains"]) or [],
            "preferred_ca": row["preferred_ca"],
            "billing_contact": row["billing_contact"],
            "technical_contact": row["technical_contact"],
            "emergency_contact": row["emergency_contact"],
            "certificate_policies": self._deserialize_json_field(row["certificate_policies"]) or [],
            "portal_access_enabled": bool(row["portal_access_enabled"]),
            "metadata": self._deserialize_json_field(row["metadata"]) or {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # MSP operations
    def create_msp(self, msp: MSP) -> bool:
        """Create a new MSP record"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO msps (
                        id, name, ca_credentials, clients, default_policies,
                        integration_settings, branding_config, contact_info,
                        metadata, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msp.id,
                    msp.name,
                    self._serialize_json_field(list(msp.ca_credentials.keys())),  # Only store keys
                    self._serialize_json_field(msp.clients),
                    self._serialize_json_field(msp.default_policies),
                    self._serialize_json_field(msp.integration_settings),
                    self._serialize_json_field(msp.branding_config),
                    self._serialize_json_field(msp.contact_info),
                    self._serialize_json_field(msp.metadata),
                    msp.created_at.isoformat(),
                    msp.updated_at.isoformat()
                ))
                
                conn.commit()
                self.logger.info(f"Created MSP record: {msp.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create MSP {msp.id}: {e}")
            return False
    
    # Database maintenance
    def vacuum_database(self) -> bool:
        """Optimize database by running VACUUM"""
        try:
            with self._get_connection() as conn:
                conn.execute("VACUUM")
                self.logger.info("Database vacuum completed")
                return True
        except Exception as e:
            self.logger.error(f"Database vacuum failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table counts
                cursor.execute("SELECT COUNT(*) FROM certificates")
                cert_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM clients")
                client_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM msps")
                msp_count = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                
                db_size = page_count * page_size
                
                return {
                    "certificates": cert_count,
                    "clients": client_count,
                    "msps": msp_count,
                    "database_size_bytes": db_size,
                    "database_path": self.db_path
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get database module information"""
        return {
            "module_name": "certificate_database",
            "module_type": "storage",
            "version": "1.0.0",
            "description": "SQLite database for certificate inventory management"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get database capabilities"""
        return [
            {"name": "certificate_storage", "enabled": True},
            {"name": "client_management", "enabled": True},
            {"name": "msp_management", "enabled": True},
            {"name": "performance_indexing", "enabled": True},
            {"name": "data_integrity", "enabled": True}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            stats = self.get_database_stats()
            
            # Test database connectivity
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                
            return {
                "status": "healthy",
                "database_accessible": True,
                "statistics": stats,
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "database_accessible": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for database"""
        try:
            health = self.get_health_status()
            
            if health["status"] != "healthy":
                return {
                    "degradation_applied": True,
                    "fallback_mode": "read_only",
                    "message": "Database in read-only mode due to connectivity issues"
                }
            
            return {
                "degradation_applied": False,
                "fallback_mode": None,
                "message": "Database operating normally"
            }
            
        except Exception as e:
            return {
                "degradation_applied": True,
                "fallback_mode": "offline",
                "message": f"Database offline: {e}"
            }