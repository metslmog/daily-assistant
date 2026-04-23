"""
Action system for handling action proposals and approvals
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Any
from database_models import action_model


class ActionSystem:
    """System for managing action proposals and executions"""
    
    def __init__(self):
        self.action_handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        
        def handle_reminder(details: Dict) -> Dict[str, Any]:
            """Handle reminder creation"""
            # For now, just simulate the reminder creation
            # In a real implementation, this could integrate with calendar APIs
            message = details.get('message', 'Reminder set')
            return {
                "success": True,
                "message": f"✅ {message}",
                "details": details
            }
        
        def handle_preference_update(details: Dict) -> Dict[str, Any]:
            """Handle updating user preferences"""
            session_id = details.get('session_id')
            preference_key = details.get('key')
            preference_value = details.get('value')
            
            if not all([session_id, preference_key, preference_value]):
                return {
                    "success": False,
                    "message": "❌ Missing required parameters for preference update",
                    "details": details
                }
            
            # Update preference in database
            from database_models import user_preferences_model
            success = user_preferences_model.set_preference(session_id, preference_key, preference_value)
            
            if success:
                return {
                    "success": True,
                    "message": f"✅ Updated {preference_key} preference",
                    "details": details
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Failed to update {preference_key} preference",
                    "details": details
                }
        
        def handle_notification(details: Dict) -> Dict[str, Any]:
            """Handle sending notifications"""
            # For now, just simulate notification
            # In a real implementation, this could send push notifications
            message = details.get('message', 'Notification sent')
            return {
                "success": True,
                "message": f"🔔 {message}",
                "details": details
            }
        
        # Register handlers
        self.action_handlers['reminder'] = handle_reminder
        self.action_handlers['preference_update'] = handle_preference_update
        self.action_handlers['notification'] = handle_notification
    
    def create_action_proposal(self, session_id: str, action_type: str, 
                             description: str, reasoning: str = None, 
                             details: Dict = None) -> str:
        """Create a new action proposal"""
        
        action_id = str(uuid.uuid4())
        
        success = action_model.create_action(
            action_id=action_id,
            session_id=session_id,
            action_type=action_type,
            description=description,
            reasoning=reasoning,
            details=details or {}
        )
        
        if success:
            print(f"✅ Created action proposal: {action_id} - {description}")
            return action_id
        else:
            print(f"❌ Failed to create action proposal: {description}")
            return None
    
    def approve_action(self, action_id: str, approved: bool) -> Dict[str, Any]:
        """Approve or deny an action"""
        
        if approved:
            return self._execute_action(action_id)
        else:
            # Mark as denied
            action_model.update_action_status(action_id, 'denied')
            
            return {
                "success": True,
                "message": "Action declined",
                "action_id": action_id
            }
    
    def _execute_action(self, action_id: str) -> Dict[str, Any]:
        """Execute an approved action"""
        
        try:
            # Get action details from database
            conn = action_model.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT action_type, description, details
                FROM actions
                WHERE id = ?
            """, (action_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {
                    "success": False,
                    "message": "Action not found",
                    "action_id": action_id
                }
            
            action_type = row['action_type']
            description = row['description']
            details = json.loads(row['details']) if row['details'] else {}
            
            # Get handler for this action type
            handler = self.action_handlers.get(action_type)
            if not handler:
                return {
                    "success": False,
                    "message": f"No handler for action type: {action_type}",
                    "action_id": action_id
                }
            
            # Execute the action
            print(f"🚀 Executing action: {action_id} - {description}")
            result = handler(details)
            
            # Update action status
            new_status = 'executed' if result['success'] else 'failed'
            action_model.update_action_status(action_id, new_status)
            
            return {
                "success": result['success'],
                "message": result['message'],
                "action_id": action_id,
                "details": result.get('details', {})
            }
            
        except Exception as e:
            print(f"❌ Error executing action {action_id}: {e}")
            action_model.update_action_status(action_id, 'failed')
            
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}",
                "action_id": action_id
            }
    
    def get_pending_actions(self, session_id: str) -> List[Dict]:
        """Get all pending actions for a session"""
        return action_model.get_pending_actions(session_id)
    
    def register_action_handler(self, action_type: str, handler_function):
        """Register a new action handler"""
        self.action_handlers[action_type] = handler_function
        print(f"✅ Registered action handler: {action_type}")


# Global action system instance
action_system = ActionSystem()