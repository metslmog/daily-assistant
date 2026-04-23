"""
Database models for conversation management and user preferences
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = "daily_assistant.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                message_type TEXT NOT NULL, -- 'user', 'agent', 'system', 'error'
                content TEXT NOT NULL,
                metadata TEXT, -- JSON string for additional data
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, message_id)
            )
        """)
        
        # Actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                description TEXT NOT NULL,
                reasoning TEXT,
                details TEXT, -- JSON string for action details
                status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'denied', 'executed'
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, preference_key)
            )
        """)
        
        # Session metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT -- JSON string for session data
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn


class ConversationModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_message(self, session_id: str, message_id: str, message_type: str, 
                   content: str, metadata: Dict = None) -> bool:
        """Add a message to the conversation history"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (session_id, message_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, message_id, message_type, content, metadata_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT message_id, message_type, content, metadata, timestamp
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
                messages.append({
                    'id': row['message_id'],
                    'type': row['message_type'],
                    'content': row['content'],
                    'metadata': metadata,
                    'timestamp': row['timestamp']
                })
            
            conn.close()
            return messages
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def get_recent_context(self, session_id: str, max_messages: int = 10) -> str:
        """Get recent conversation context as a formatted string"""
        messages = self.get_conversation_history(session_id, max_messages)
        
        context_lines = []
        for msg in messages[-max_messages:]:
            if msg['type'] == 'user':
                context_lines.append(f"User: {msg['content']}")
            elif msg['type'] == 'agent':
                context_lines.append(f"Assistant: {msg['content']}")
        
        return "\n".join(context_lines)


class ActionModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_action(self, action_id: str, session_id: str, action_type: str,
                     description: str, reasoning: str = None, details: Dict = None) -> bool:
        """Create a new action proposal"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            cursor.execute("""
                INSERT INTO actions 
                (id, session_id, action_type, description, reasoning, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (action_id, session_id, action_type, description, reasoning, details_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating action: {e}")
            return False
    
    def update_action_status(self, action_id: str, status: str) -> bool:
        """Update the status of an action"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE actions 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, action_id))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating action status: {e}")
            return False
    
    def get_pending_actions(self, session_id: str) -> List[Dict]:
        """Get all pending actions for a session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, action_type, description, reasoning, details, created_at
                FROM actions 
                WHERE session_id = ? AND status = 'pending'
                ORDER BY created_at DESC
            """, (session_id,))
            
            actions = []
            for row in cursor.fetchall():
                details = json.loads(row['details']) if row['details'] else {}
                actions.append({
                    'id': row['id'],
                    'action_type': row['action_type'],
                    'description': row['description'],
                    'reasoning': row['reasoning'],
                    'details': details,
                    'created_at': row['created_at']
                })
            
            conn.close()
            return actions
        except Exception as e:
            print(f"Error getting pending actions: {e}")
            return []


class UserPreferencesModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def set_preference(self, session_id: str, key: str, value: Any) -> bool:
        """Set a user preference"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Convert value to JSON string for storage
            value_str = json.dumps(value) if not isinstance(value, str) else value
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences 
                (session_id, preference_key, preference_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (session_id, key, value_str))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting preference: {e}")
            return False
    
    def get_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT preference_value 
                FROM user_preferences 
                WHERE session_id = ? AND preference_key = ?
            """, (session_id, key))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    # Try to parse as JSON, fall back to string
                    return json.loads(row['preference_value'])
                except json.JSONDecodeError:
                    return row['preference_value']
            
            return default
        except Exception as e:
            print(f"Error getting preference: {e}")
            return default
    
    def get_all_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get all preferences for a session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT preference_key, preference_value 
                FROM user_preferences 
                WHERE session_id = ?
            """, (session_id,))
            
            preferences = {}
            for row in cursor.fetchall():
                try:
                    value = json.loads(row['preference_value'])
                except json.JSONDecodeError:
                    value = row['preference_value']
                preferences[row['preference_key']] = value
            
            conn.close()
            return preferences
        except Exception as e:
            print(f"Error getting all preferences: {e}")
            return {}


class SessionModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_session(self, session_id: str, metadata: Dict = None) -> bool:
        """Create a new session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, metadata, last_activity)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (session_id, metadata_json))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp for a session"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions 
                SET last_activity = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
            
            # Create session if it doesn't exist
            if cursor.rowcount == 0:
                self.create_session(session_id)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return False


# Global database instance
db_manager = DatabaseManager()
conversation_model = ConversationModel(db_manager)
action_model = ActionModel(db_manager)
user_preferences_model = UserPreferencesModel(db_manager)
session_model = SessionModel(db_manager)