"""
Main agent orchestrator for handling conversations and tool usage
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Try to import OpenAI, but make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

from conversation_manager import conversation_manager
from tool_registry import tool_registry
from database_models import user_preferences_model


class AgentOrchestrator:
    """Main agent that orchestrates conversations and tool usage"""
    
    def __init__(self):
        self.openai_client = None
        self._init_openai_client()
        self.system_prompt = self._build_system_prompt()
    
    def _init_openai_client(self):
        """Initialize OpenAI client if API key and library are available"""
        if not OPENAI_AVAILABLE:
            print("⚠️ OpenAI library not installed - using fallback responses only")
            self.openai_client = None
            return
            
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e} - using fallback responses")
                self.openai_client = None
        else:
            print("⚠️ No OpenAI API key found - using fallback responses")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent"""
        return """You are a helpful daily assistant that helps users with their morning routine and daily planning.

Your capabilities include:
- Providing current weather information for any location
- Giving travel directions and commute time estimates (driving, transit, walking)
- Suggesting appropriate outfits based on weather conditions
- Answering questions about daily planning and recommendations

Key guidelines:
1. Be conversational, friendly, and helpful
2. Use the available tools when users ask for specific information
3. If users ask about weather, commute, or outfit advice, use the appropriate tools
4. When suggesting actions (like setting reminders), always ask for permission first
5. Keep responses concise but informative
6. If you can't help with something specific, explain what you can help with instead

When using tools:
- Always use tools when users ask for weather, commute, or outfit information
- Explain what you're doing: "Let me check the current weather for you..."
- Present tool results in a clear, user-friendly way
- If a tool fails, explain the issue and offer alternatives

Remember: You're here to make the user's morning routine and daily planning easier and more informed."""
    
    def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process a user message and return agent response"""
        
        print(f"🔄 Processing message for session {session_id}: {user_message[:100]}...")
        
        # Add user message to conversation
        conversation_manager.add_message(session_id, 'user', user_message)
        
        # Get conversation context
        context = conversation_manager.get_context_for_agent(session_id)
        
        # Process with AI if available, otherwise use fallback
        if self.openai_client:
            response = self._process_with_openai(session_id, user_message, context)
        else:
            response = self._process_with_fallback(session_id, user_message)
        
        # Add agent response to conversation
        conversation_manager.add_message(
            session_id, 
            'agent', 
            response['message'],
            metadata={'actions': response.get('suggested_actions', [])}
        )
        
        return response
    
    def _process_with_openai(self, session_id: str, user_message: str, context: str) -> Dict[str, Any]:
        """Process message using OpenAI with function calling"""
        
        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context if available
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            # Add recent conversation history
            history = conversation_manager.get_conversation_history(session_id, limit=6)
            for msg in history[-6:]:  # Last 6 messages for context
                if msg['type'] == 'user':
                    messages.append({"role": "user", "content": msg['content']})
                elif msg['type'] == 'agent':
                    messages.append({"role": "assistant", "content": msg['content']})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get available tools
            functions = tool_registry.get_openai_functions()
            
            # Call OpenAI
            print("🤖 Calling OpenAI API...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.function_call:
                return self._handle_function_call(session_id, message, user_message)
            else:
                # Direct response without tools
                return {
                    "message": message.content,
                    "suggested_actions": [],
                    "tool_calls": []
                }
                
        except Exception as e:
            print(f"❌ Error with OpenAI: {e}")
            return self._process_with_fallback(session_id, user_message)
    
    def _handle_function_call(self, session_id: str, message, original_user_message: str) -> Dict[str, Any]:
        """Handle OpenAI function call"""
        
        function_name = message.function_call.name
        function_args = json.loads(message.function_call.arguments)
        
        print(f"🔧 Executing tool: {function_name} with args: {function_args}")
        
        # Execute the tool
        tool_result = tool_registry.execute_tool(function_name, **function_args)
        
        if tool_result['success']:
            # Format the response based on the tool and result
            formatted_response = self._format_tool_response(function_name, tool_result['result'], function_args)
            
            return {
                "message": formatted_response,
                "suggested_actions": self._generate_suggested_actions(function_name, tool_result['result']),
                "tool_calls": [{
                    "tool": function_name,
                    "args": function_args,
                    "result": tool_result['result']
                }]
            }
        else:
            # Tool execution failed
            error_message = f"I encountered an issue getting that information: {tool_result['error']}. Let me know if you'd like me to try something else!"
            
            return {
                "message": error_message,
                "suggested_actions": [],
                "tool_calls": []
            }
    
    def _format_tool_response(self, tool_name: str, result: Any, args: Dict) -> str:
        """Format tool results for user-friendly display"""
        
        if tool_name == "get_current_weather":
            if isinstance(result, dict) and 'temp' in result:
                response = f"The current weather"
                if 'address' in args:
                    response += f" in {args['address']}"
                response += f" is {result['temp']}°F with {result['conditions']}."
                
                if 'humidity' in result:
                    response += f" Humidity is {result['humidity']}%"
                if 'feels_like' in result:
                    response += f" and it feels like {result['feels_like']}°F."
                
                return response
            else:
                return f"I couldn't get the weather information right now. {result}"
        
        elif tool_name == "get_travel_directions":
            if isinstance(result, dict):
                response = "Here are your travel options:\n\n"
                
                if 'driving' in result and 'duration' in result['driving']:
                    response += f"🚗 **Driving:** {result['driving']['duration']}"
                    if 'distance' in result['driving']:
                        response += f" ({result['driving']['distance']})"
                    response += "\n\n"
                
                if 'transit' in result and result['transit']:
                    transit_option = result['transit'][0] if result['transit'] else {}
                    if 'duration' in transit_option:
                        response += f"🚌 **Public Transit:** {transit_option['duration']}"
                        if 'lines' in transit_option and transit_option['lines']:
                            lines = [line.get('name', 'Transit') for line in transit_option['lines']]
                            response += f" (via {', '.join(lines)})"
                        response += "\n\n"
                
                if 'walking' in result and 'duration' in result['walking']:
                    response += f"🚶 **Walking:** {result['walking']['duration']}"
                    if 'distance' in result['walking']:
                        response += f" ({result['walking']['distance']})"
                
                return response
            else:
                return f"I couldn't get travel directions right now. {result}"
        
        elif tool_name == "suggest_outfit":
            return f"Here's what I'd suggest wearing:\n\n{result}"
        
        elif tool_name == "get_weather_and_outfit":
            if isinstance(result, dict):
                response = ""
                if 'weather' in result:
                    weather = result['weather']
                    response += f"**Weather:** {weather.get('temp', 'N/A')}°F, {weather.get('conditions', 'N/A')}\n\n"
                
                if 'outfit' in result:
                    response += f"**Outfit Suggestion:**\n{result['outfit']}"
                
                return response
            else:
                return f"Here's the information I found: {result}"
        
        # Default formatting
        return str(result)
    
    def _generate_suggested_actions(self, tool_name: str, result: Any) -> List[Dict]:
        """Generate suggested actions based on tool results"""
        actions = []
        
        if tool_name == "get_current_weather" and isinstance(result, dict):
            temp = result.get('temp', 70)
            conditions = result.get('conditions', '').lower()
            
            # Suggest actions based on weather
            if 'rain' in conditions:
                actions.append({
                    'id': f'umbrella_reminder_{datetime.now().timestamp()}',
                    'description': 'Add umbrella reminder',
                    'reasoning': 'Rain is expected today',
                    'action_type': 'reminder'
                })
            
            if temp > 80:
                actions.append({
                    'id': f'hydration_reminder_{datetime.now().timestamp()}',
                    'description': 'Set hydration reminder for hot weather',
                    'reasoning': f'Temperature is {temp}°F - stay hydrated!',
                    'action_type': 'reminder'
                })
            elif temp < 40:
                actions.append({
                    'id': f'warmup_reminder_{datetime.now().timestamp()}',
                    'description': 'Reminder to dress warmly',
                    'reasoning': f'It\'s quite cold at {temp}°F',
                    'action_type': 'reminder'
                })
        
        elif tool_name == "get_travel_directions" and isinstance(result, dict):
            driving_time = result.get('driving', {}).get('duration', '')
            
            # Suggest early departure for long commutes
            if any(word in driving_time.lower() for word in ['hour', 'hours']) or any(num in driving_time for num in ['45', '50', '60']):
                actions.append({
                    'id': f'early_departure_{datetime.now().timestamp()}',
                    'description': 'Set reminder to leave 15 minutes early',
                    'reasoning': f'Your commute is {driving_time} - consider leaving early',
                    'action_type': 'reminder'
                })
        
        return actions
    
    def _process_with_fallback(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Fallback processing when OpenAI is not available"""
        
        user_message_lower = user_message.lower()
        
        # Simple keyword-based responses
        if any(word in user_message_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            # Try to extract location or use default
            location = self._extract_location(user_message) or "your location"
            
            # Use weather tool
            try:
                result = tool_registry.execute_tool('get_current_weather', address=location)
                if result['success']:
                    formatted_response = self._format_tool_response('get_current_weather', result['result'], {'address': location})
                    return {
                        "message": formatted_response,
                        "suggested_actions": self._generate_suggested_actions('get_current_weather', result['result']),
                        "tool_calls": [{'tool': 'get_current_weather', 'result': result['result']}]
                    }
            except Exception as e:
                print(f"Weather tool error: {e}")
        
        elif any(word in user_message_lower for word in ['commute', 'travel', 'directions', 'drive']):
            return {
                "message": "I can help you with travel directions! I'll need your home and work addresses to get accurate commute information. You can set these in the settings panel.",
                "suggested_actions": [],
                "tool_calls": []
            }
        
        elif any(word in user_message_lower for word in ['outfit', 'wear', 'clothes']):
            return {
                "message": "I'd love to help suggest an outfit! Let me check the current weather to give you the best recommendation.",
                "suggested_actions": [],
                "tool_calls": []
            }
        
        elif any(word in user_message_lower for word in ['hello', 'hi', 'hey']):
            return {
                "message": "Hello! I'm your daily assistant. I can help you with weather information, commute directions, outfit suggestions, and daily planning. What would you like to know?",
                "suggested_actions": [],
                "tool_calls": []
            }
        
        # Default response
        return {
            "message": "I'm here to help with your daily routine! I can check the weather, provide commute information, suggest outfits, and help with daily planning. What would you like to know about?",
            "suggested_actions": [],
            "tool_calls": []
        }
    
    def _extract_location(self, message: str) -> Optional[str]:
        """Simple location extraction from user message"""
        # Very basic location extraction - could be improved with NLP
        words = message.lower().split()
        location_indicators = ['in', 'at', 'for']
        
        for i, word in enumerate(words):
            if word in location_indicators and i + 1 < len(words):
                # Return the next few words as potential location
                return ' '.join(words[i+1:i+4])
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "status": "ready",
            "openai_library_installed": OPENAI_AVAILABLE,
            "openai_client_ready": self.openai_client is not None,
            "tools_available": len(tool_registry.get_all_tools()),
            "active_sessions": len(conversation_manager.active_sessions)
        }


# Global agent orchestrator instance
agent_orchestrator = AgentOrchestrator()