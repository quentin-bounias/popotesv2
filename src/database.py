# src/database.py
import sqlite3
import hashlib
import os
from typing import Dict, Optional
import streamlit as st

class UserDatabase:
    def __init__(self, db_path='data/users.db'):
        """
        Initialize SQLite database for user management
        
        Args:
        - db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    name TEXT,
                    profile_picture BLOB,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id INTEGER,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')
            
            cursor.execute('''
    CREATE TABLE IF NOT EXISTS wine_tastings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        wine_id INTEGER,
        dress_rating REAL,
        dress_notes TEXT,
        nose_rating REAL,
        nose_notes TEXT,
        taste_rating REAL,
        taste_notes TEXT,
        overall_rating REAL,
        overall_notes TEXT,
        tasted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        UNIQUE(user_id, wine_id)  # Ensures each user can rate a wine only once
    )
''')
            conn.commit()
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """
        Generate a secure password hash
        
        Args:
        - password: User's plain text password
        - salt: Optional salt (generated if not provided)
        
        Returns:
        - Tuple of (salt, password_hash)
        """
        if salt is None:
            salt = os.urandom(32).hex()
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000
        ).hex()
        
        return salt, password_hash
    
    def register_user(self, email: str, password: str, name: str = None) -> bool:
        """
        Register a new user
        
        Args:
        - email: User's email
        - password: User's password
        - name: Optional user name
        
        Returns:
        - Boolean indicating registration success
        """
        try:
            salt, password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (email, password_hash, salt, name) VALUES (?, ?, ?, ?)',
                    (email, password_hash, salt, name)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error("Email already exists. Please use a different email.")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user and generate a long-lived session
        
        Args:
        - email: User's email
        - password: User's password
        
        Returns:
        - User details if authentication successful, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password_hash, salt, name FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if not user:
                st.error("User not found")
                return None
            
            user_id, stored_hash, salt, name = user
            
            # Verify password
            _, input_hash = self._hash_password(password, salt)
            
            if input_hash != stored_hash:
                st.error("Incorrect password")
                return None
            
            # Generate long-lived session token
            session_token = os.urandom(32).hex()
            # Set session to expire in 30 days
            expires_at = st.experimental_get_query_params().get('expires_at', os.path.getatime() + 30 * 24 * 60 * 60)
            
            cursor.execute(
                'INSERT INTO user_sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)',
                (user_id, session_token, expires_at)
            )
            conn.commit()
            
            return {
                'id': user_id,
                'email': email,
                'name': name,
                'session_token': session_token
            }
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate an existing session
        
        Args:
        - session_token: User's session token
        
        Returns:
        - User details if session is valid, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.email, u.name 
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            user = cursor.fetchone()
            
            return user
    
    def update_user_profile(self, user_id: int, name: str = None, profile_picture: bytes = None):
        """
        Update user profile information
        
        Args:
        - user_id: User's unique identifier
        - name: Optional new name
        - profile_picture: Optional profile picture as bytes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Prepare update statement based on provided parameters
            update_fields = []
            params = []
            
            if name:
                update_fields.append("name = ?")
                params.append(name)
            
            if profile_picture:
                update_fields.append("profile_picture = ?")
                params.append(profile_picture)
            
            params.append(user_id)
            
            if update_fields:
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
    
    def record_wine_tasting(self, user_id: int, wine_id: int, rating: int, notes: str = None):
        """
        Record a wine tasting entry
        
        Args:
        - user_id: User's unique identifier
        - wine_id: Wine's unique identifier
        - rating: User's rating for the wine
        - notes: Optional tasting notes
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO wine_tastings (user_id, wine_id, rating, notes) VALUES (?, ?, ?, ?)',
                (user_id, wine_id, rating, notes)
            )
            conn.commit()
    
    def get_user_wine_tastings(self, user_id: int):
        """
        Retrieve a user's wine tasting history
        
        Args:
        - user_id: User's unique identifier
        
        Returns:
        - List of wine tasting entries
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT w.wine_name, t.rating, t.notes, t.tasted_at
                FROM wine_tastings t
                JOIN wines w ON t.wine_id = w.id
                WHERE t.user_id = ?
                ORDER BY t.tasted_at DESC
            ''', (user_id,))
            return cursor.fetchall()