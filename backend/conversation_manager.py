"""
Conversation management for the daily assistant agent
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from database_models import conversation_model, user_preferences_model, session_model

class ConversationManager:
    """Manages conversation state, context, and memory"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
    
    def start_session(self, session_id: str) -> Dict:
        """Initialize a new conversation session"""
        print(f"Starting conversation session: {session_id}")
        
        # Create session in database
        session_model.create_session(session_id)
        
        # Load user preferences
        preferences = user_preferences_model.get_all_preferences(session_id)
        
        # Initialize session state
        session_state = {
            'session_id': session_id,
            'started_at': datetime.now().isoformat(),
            'preferences': preferences,
            'context': {},
            'last_activity': datetime.now(),
        }
        
        self.active_sessions[session_id] = session_state
        return session_state
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session state, creating if it doesn't exist"""
        if session_id not in self.active_sessions:
            self.start_session(session_id)
        
        # Update last activity
        session_model.update_session_activity(session_id)
        self.active_sessions[session_id]['last_activity'] = datetime.now()
        
        return self.active_sessions[session_id]
    
    def add_message(self, session_id: str, message_type: str, content: str, 
                   metadata: Dict = None) -> str:
        """Add a message to the conversation"""
        message_id = str(uuid.uuid4())
        
        # Store in database
        conversation_model.add_message(
            session_id=session_id,
            message_id=message_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Update session
        self.get_session(session_id)
        
        return message_id
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for display"""
        messages = conversation_model.get_conversation_history(session_id, limit)
        
        # Format for frontend
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                'id': msg['id'],
                'type': msg['type'],
                'content': msg['content'],
                'timestamp': msg['timestamp']
            }
            
            # Add actions if present in metadata
            if msg['metadata'].get('actions'):
                formatted_msg['actions'] = msg['metadata']['actions']
                
            formatted_messages.append(formatted_msg)
        
        return formatted_messages
    
    def get_context_for_agent(self, session_id: str) -> str:
        """Get conversation context formatted for the AI agent"""
        session = self.get_session(session_id)
        if not session:
            return ""
        
        # Get recent conversation history
        recent_context = conversation_model.get_recent_context(session_id, max_messages=10)
        
        # Build context string
        context_parts = []
        
        # Add user preferences if available
        if session['preferences']:
            prefs_str = []
            for key, value in session['preferences'].items():
                prefs_str.append(f"{key}: {value}")
            if prefs_str:
                context_parts.append(f"User preferences: {', '.join(prefs_str)}")
        
        # Add recent conversation
        if recent_context:
            context_parts.append(f"Recent conversation:\n{recent_context}")
        
        return "\n\n".join(context_parts)
    
    def update_user_preference(self, session_id: str, key: str, value: Any) -> bool:
        """Update a user preference"""
        success = user_preferences_model.set_preference(session_id, key, value)
        
        # Update session cache
        if success and session_id in self.active_sessions:
            self.active_sessions[session_id]['preferences'][key] = value
        
        return success
    
    def get_user_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        session = self.get_session(session_id)
        return session['preferences'].get(key, default)
    
    def set_context(self, session_id: str, key: str, value: Any):
        """Set temporary context data for the session"""
        session = self.get_session(session_id)
        session['context'][key] = value
    
    def get_context(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get temporary context data from the session"""
        session = self.get_session(session_id)
        return session['context'].get(key, default)
    
    def clear_old_sessions(self, max_age_hours: int = 24):
        """Clear sessions older than max_age_hours"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if session['last_activity'].timestamp() < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            print(f"Cleaning up old session: {session_id}")
            del self.active_sessions[session_id]


# Global conversation manager instance
conversation_manager = ConversationManager()