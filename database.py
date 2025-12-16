"""Database models and operations for the knowledge portal."""
import sqlite3
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from utils.config_loader import ConfigLoader


class Database:
    """Manage SQLite database for metadata, users, and documents."""
    
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.db_path = config.get('app.database_path', './data/knowledge_portal.db')
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'viewer',
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_date TIMESTAMP,
                chunk_count INTEGER,
                status TEXT DEFAULT 'pending',
                uploaded_by TEXT,
                department TEXT,
                permissions TEXT DEFAULT '{}'
            )
        ''')
        
        # Add department columns if they don't exist (migrations)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN department TEXT')
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute('ALTER TABLE documents ADD COLUMN department TEXT')
        except sqlite3.OperationalError:
            pass
        
        # Chunks table (for tracking individual chunks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_id INTEGER,
                text TEXT,
                vector_id INTEGER,
                start_pos INTEGER,
                end_pos INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # Search history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                query TEXT,
                results_count INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_hash = self._hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, department)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_hash, 'admin', 'IT')) # Default admin dept
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # User management
    def create_user(self, username: str, password: str, role: str = 'viewer', department: str = None) -> bool:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self._hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, department)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, role, department))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return user info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        password_hash = self._hash_password(password)
        
        cursor.execute('''
            SELECT id, username, role, department FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (result[0],))
            conn.commit()
            
            user = {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'department': result[3]
            }
            conn.close()
            return user
        
        conn.close()
        return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role, department FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[2],
                'department': result[3]
            }
        return None
    
    # Document management
    def add_document(self, file_name: str, file_path: str, file_hash: str,
                    file_size: int, file_type: str, chunk_count: int,
                    uploaded_by: str, permissions: Dict = None, department: str = None) -> int:
        """Add a document to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        permissions_json = json.dumps(permissions or {})
        
        cursor.execute('''
            INSERT INTO documents 
            (file_name, file_path, file_hash, file_size, file_type, 
             chunk_count, uploaded_by, permissions, processed_date, status, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'processed', ?)
        ''', (file_name, file_path, file_hash, file_size, file_type,
              chunk_count, uploaded_by, permissions_json, department))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def get_document_by_hash(self, file_hash: str) -> Optional[Dict]:
        """Get document by file hash."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE file_hash = ?', (file_hash,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [col[0] for col in cursor.description]
            doc = dict(zip(columns, row))
            doc['permissions'] = json.loads(doc.get('permissions') or '{}')
            return doc
        return None
    
    def get_all_documents(self, user_role: str = None, user_department: str = None) -> List[Dict]:
        """Get all documents (filtered by role and department)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Use Row factory for creating dicts easily using column names
        cursor = conn.cursor()
        
        query = 'SELECT * FROM documents'
        params = []
        
        # Filter logic:
        # If Admin: Show all.
        # If User: Show only docs where doc.department == user.department OR doc.department IS NULL
        
        if user_role != 'admin' and user_department:
            query += ' WHERE department = ?'
            params.append(user_department)
            
        query += ' ORDER BY upload_date DESC'
            
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            doc = dict(row)
            doc['permissions'] = json.loads(doc.get('permissions') or '{}')
            documents.append(doc)
        
        return documents
    
    def delete_document(self, file_hash: str) -> bool:
        """Delete a document from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents WHERE file_hash = ?', (file_hash,))
        cursor.execute('DELETE FROM chunks WHERE document_id IN (SELECT id FROM documents WHERE file_hash = ?)', (file_hash,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    # Search history
    def log_search(self, user_id: int, query: str, results_count: int):
        """Log a search query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_history (user_id, query, results_count)
            VALUES (?, ?, ?)
        ''', (user_id, query, results_count))
        conn.commit()
        conn.close()



