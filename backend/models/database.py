#!/usr/bin/env python3
"""
Database Manager - Handles interaction logging and data persistence
Uses SQLite for offline operation and data storage
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../data/farm_advisor.db')
        
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def create_tables(self):
        """Create necessary database tables"""
        with self.get_connection() as conn:
            # Interactions table for logging Q&A
            conn.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    input_method TEXT DEFAULT 'text',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    user_feedback INTEGER,
                    response_time_ms INTEGER
                )
            ''')
            
            conn.commit()
            logger.info("Database tables created/verified successfully")
    
    def log_interaction(self, question: str, answer: str, input_method: str = 'text', 
                       language: str = 'en', session_id: str = None, 
                       response_time_ms: int = None) -> int:
        """Log a user interaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO interactions 
                    (question, answer, language, input_method, session_id, response_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (question, answer, language, input_method, session_id, response_time_ms))
                
                interaction_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"Logged interaction: {question[:50]}... -> {answer[:50]}...")
                return interaction_id
                
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
            return -1
    
    def get_interaction_history(self, limit: int = 50, session_id: str = None) -> List[Dict]:
        """Get recent interaction history"""
        try:
            with self.get_connection() as conn:
                if session_id:
                    cursor = conn.execute('''
                        SELECT question, answer, language, input_method, timestamp
                        FROM interactions 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (session_id, limit))
                else:
                    cursor = conn.execute('''
                        SELECT question, answer, language, input_method, timestamp
                        FROM interactions 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                interactions = []
                for row in cursor.fetchall():
                    interactions.append({
                        'question': row['question'],
                        'answer': row['answer'],
                        'language': row['language'],
                        'input_method': row['input_method'],
                        'timestamp': row['timestamp']
                    })
                
                return interactions
                
        except Exception as e:
            logger.error(f"Error fetching interaction history: {str(e)}")
            return []