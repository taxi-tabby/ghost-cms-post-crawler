import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import os

class URLDatabase:
    """A class for managing URL entries in a SQLite database."""
    
    def __init__(self, db_path: str = "urls.db"):
        """Initialize the database connection and create table if it doesn't exist.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_table_exists()
    
    def _get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Create and return a database connection and cursor.
        
        Returns:
            Tuple of (connection, cursor)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
        cursor = conn.cursor()
        return conn, cursor
    
    def _ensure_table_exists(self) -> None:
        """Create the table if it doesn't already exist."""
        conn, cursor = self._get_connection()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    uripath TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(domain, uripath)
                )
            """)
            
            # Create index on domain column for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_domain ON urls(domain)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def create(self, domain: str, uripath: str) -> int:
        """Create a new URL entry.
        
        Args:
            domain: The domain name
            uripath: The URI path
            
        Returns:
            The ID of the newly created entry
            
        Raises:
            sqlite3.IntegrityError: If the domain+uripath combination already exists
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "INSERT INTO urls (domain, uripath) VALUES (?, ?)",
                (domain, uripath)
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def read(self, url_id: int = None) -> List[Dict[str, Any]]:
        """Read URL entries from the database.
        
        Args:
            url_id: If provided, retrieve only the entry with this ID
            
        Returns:
            A list of dictionaries representing URL entries
        """
        conn, cursor = self._get_connection()
        try:
            if url_id is not None:
                cursor.execute("SELECT * FROM urls WHERE id = ?", (url_id,))
            else:
                cursor.execute("SELECT * FROM urls")
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def read_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Read URL entries for a specific domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            A list of dictionaries representing URL entries
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute("SELECT * FROM urls WHERE domain = ?", (domain,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
            
    def read_by_domain_and_path(self, domain: str, uripath: str) -> Optional[Dict[str, Any]]:
        """Read a URL entry for a specific domain and path combination.
        
        Args:
            domain: The domain to filter by
            uripath: The URI path to filter by
            
        Returns:
            A dictionary representing the URL entry if found, or None if not found
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute(
                "SELECT * FROM urls WHERE domain = ? AND uripath = ?", 
                (domain, uripath)
            )
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()
            
    
    def update(self, url_id: int, domain: str = None, uripath: str = None) -> bool:
        """Update a URL entry.
        
        Args:
            url_id: The ID of the entry to update
            domain: The new domain name (if None, won't be updated)
            uripath: The new URI path (if None, won't be updated)
            
        Returns:
            True if a row was updated, False otherwise
            
        Raises:
            sqlite3.IntegrityError: If the update would violate the unique constraint
        """
        if domain is None and uripath is None:
            return False
        
        conn, cursor = self._get_connection()
        try:
            update_parts = []
            params = []
            
            if domain is not None:
                update_parts.append("domain = ?")
                params.append(domain)
            
            if uripath is not None:
                update_parts.append("uripath = ?")
                params.append(uripath)
                
            params.append(url_id)
            
            query = f"UPDATE urls SET {', '.join(update_parts)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete(self, url_id: int) -> bool:
        """Delete a URL entry.
        
        Args:
            url_id: The ID of the entry to delete
            
        Returns:
            True if a row was deleted, False otherwise
        """
        conn, cursor = self._get_connection()
        try:
            cursor.execute("DELETE FROM urls WHERE id = ?", (url_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for URL entries matching a query.
        
        Args:
            query: The search query
            
        Returns:
            A list of dictionaries representing matching URL entries
        """
        conn, cursor = self._get_connection()
        try:
            pattern = f"%{query}%"
            cursor.execute(
                "SELECT * FROM urls WHERE domain LIKE ? OR uripath LIKE ?",
                (pattern, pattern)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

