"""
Tool registry for exposing existing services as agent tools
"""

import json
from typing import Dict, List, Any, Callable
from weather_service_rest import get_weather_rest
from google_maps_service_rest import get_google_directions_rest
from gemini_service_rest import get_gemini_recommendation_rest
from openai_service import get_openai_recommendation


class AgentTool:
    """Represents a tool that the agent can use"""
    
    def __init__(self, name: str, description: str, parameters: Dict, 
                 function: Callable, examples: List[str] = None):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.function = function
        self.examples = examples or []
    
    def to_openai_function(self) -> Dict:
        """Convert tool to OpenAI function calling format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        try:
            result = self.function(**kwargs)
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            print(f"Error executing tool {self.name}: {e}")
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }


class ToolRegistry:
    """Registry for managing agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, AgentTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools from existing services"""
        
        # Weather tool
        self.register_tool(AgentTool(
            name="get_current_weather",
            description="Get current weather conditions for a specific location",
            parameters={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The address or location to get weather for (e.g., 'San Francisco, CA', '123 Main St, New York')"
                    }
                },
                "required": ["address"]
            },
            function=get_weather_rest,
            examples=[
                "What's the weather like at home?",
                "Check the current weather in San Francisco",
                "Is it raining at 123 Main Street?"
            ]
        ))
        
        # Directions tool
        self.register_tool(AgentTool(
            name="get_travel_directions",
            description="Get travel directions and time estimates between two locations for driving, transit, and walking",
            parameters={
                "type": "object", 
                "properties": {
                    "home": {
                        "type": "string",
                        "description": "Starting location/home address"
                    },
                    "work": {
                        "type": "string",
                        "description": "Destination location/work address"
                    }
                },
                "required": ["home", "work"]
            },
            function=get_google_directions_rest,
            examples=[
                "How long is my commute today?",
                "What's the best way to get to work?", 
                "Should I drive or take transit?",
                "How long will it take to walk to the office?"
            ]
        ))
        
        # Outfit recommendation tool (using both AI services)
        def get_outfit_recommendation(weather_data: Dict = None, temperature: float = None, 
                                    conditions: str = None, **kwargs) -> str:
            """Get AI-powered outfit recommendation"""
            
            # Create weather dict if individual params provided
            if weather_data is None and (temperature is not None or conditions is not None):
                weather_data = {}
                if temperature is not None:
                    weather_data['temp'] = temperature
                if conditions is not None:
                    weather_data['conditions'] = conditions
            
            if weather_data is None:
                return "Please provide weather information (temperature and/or conditions) for outfit recommendations"
            
            # Try Gemini first, then OpenAI
            try:
                result = get_gemini_recommendation_rest(weather_data)
                if not result.startswith("Unable to generate"):
                    return result
            except Exception as e:
                print(f"Gemini failed: {e}")
            
            try:
                result = get_openai_recommendation(weather_data)
                if not result.startswith("Unable to generate"):
                    return result
            except Exception as e:
                print(f"OpenAI failed: {e}")
            
            # Fallback
            temp = weather_data.get('temp', 70)
            if temp >= 75:
                return "👕 Top: Light t-shirt\n👖 Bottoms: Shorts\n👟 Shoes: Breathable sneakers"
            elif temp >= 65:
                return "👔 Top: Light shirt\n👖 Bottoms: Jeans\n👟 Shoes: Casual shoes"
            else:
                return "🧥 Top: Warm jacket\n👖 Bottoms: Warm pants\n👢 Shoes: Boots"
        
        self.register_tool(AgentTool(
            name="suggest_outfit",
            description="Generate AI-powered outfit suggestions based on weather conditions",
            parameters={
                "type": "object",
                "properties": {
                    "weather_data": {
                        "type": "object",
                        "description": "Weather information object with temp and conditions",
                        "properties": {
                            "temp": {"type": "number", "description": "Temperature in Fahrenheit"},
                            "conditions": {"type": "string", "description": "Weather conditions (e.g., 'sunny', 'rainy', 'cloudy')"}
                        }
                    },
                    "temperature": {
                        "type": "number", 
                        "description": "Temperature in Fahrenheit (alternative to weather_data)"
                    },
                    "conditions": {
                        "type": "string",
                        "description": "Weather conditions (alternative to weather_data)"
                    }
                }
            },
            function=get_outfit_recommendation,
            examples=[
                "What should I wear today?",
                "Suggest an outfit for 65 degrees and sunny",
                "What outfit would work for rainy weather?"
            ]
        ))
        
        # Combined weather and outfit tool for convenience
        def get_weather_and_outfit(address: str) -> Dict[str, Any]:
            """Get weather and outfit recommendation for a location"""
            weather = get_weather_rest(address)
            outfit = get_outfit_recommendation(weather_data=weather)
            return {
                "weather": weather,
                "outfit": outfit,
                "location": address
            }
        
        self.register_tool(AgentTool(
            name="get_weather_and_outfit",
            description="Get current weather and AI-powered outfit suggestion for a location",
            parameters={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "The location to get weather and outfit advice for"
                    }
                },
                "required": ["address"]
            },
            function=get_weather_and_outfit,
            examples=[
                "What should I wear for the weather at home?",
                "Check the weather and suggest an outfit for downtown",
                "Weather and outfit advice for my current location"
            ]
        ))
    
    def register_tool(self, tool: AgentTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> AgentTool:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, AgentTool]:
        """Get all registered tools"""
        return self.tools.copy()
    
    def get_openai_functions(self) -> List[Dict]:
        """Get all tools in OpenAI function calling format"""
        return [tool.to_openai_function() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "result": None,
                "error": f"Tool '{tool_name}' not found"
            }
        
        return tool.execute(**kwargs)
    
    def get_tool_suggestions(self, user_message: str) -> List[str]:
        """Get suggested tools based on user message content"""
        user_message_lower = user_message.lower()
        suggestions = []
        
        # Simple keyword matching for tool suggestions
        weather_keywords = ['weather', 'temperature', 'rain', 'sunny', 'cold', 'hot', 'forecast']
        commute_keywords = ['commute', 'travel', 'directions', 'drive', 'transit', 'walk', 'traffic']
        outfit_keywords = ['wear', 'outfit', 'clothes', 'dress', 'clothing', 'attire']
        
        if any(keyword in user_message_lower for keyword in weather_keywords):
            suggestions.append('get_current_weather')
            if any(keyword in user_message_lower for keyword in outfit_keywords):
                suggestions.append('get_weather_and_outfit')
        
        if any(keyword in user_message_lower for keyword in commute_keywords):
            suggestions.append('get_travel_directions')
        
        if any(keyword in user_message_lower for keyword in outfit_keywords):
            if 'get_weather_and_outfit' not in suggestions:
                suggestions.append('suggest_outfit')
        
        return suggestions


# Global tool registry instance
tool_registry = ToolRegistry()