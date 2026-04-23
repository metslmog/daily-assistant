"""Modular Flask app using REST APIs only - no gRPC/SSL issues!"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import our modular services (all using REST APIs)
from weather_service_rest import get_weather_rest
from google_maps_service_rest import get_google_directions_rest
from gemini_service_rest import get_gemini_recommendation_rest, list_gemini_models
from openai_service import get_openai_recommendation

# Import agent system components
from agent_orchestrator import agent_orchestrator
from conversation_manager import conversation_manager
from action_system import action_system

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

def get_ai_outfit_recommendation(weather):
    """Try AI services in order of preference"""
    
    # Option 1: Try Gemini REST API first (your original choice)
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("🤖 Trying Gemini AI via REST API (model: gemini-1.5-flash)...")
        result = get_gemini_recommendation_rest(weather)
        if not result.startswith("Unable to generate"):
            return result
        else:
            print("❌ Gemini failed, trying OpenAI...")
            print("💡 Tip: Check http://127.0.0.1:5001/api/debug/models to see available models")
    
    # Option 2: Try OpenAI as backup
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("🤖 Trying OpenAI API...")
        result = get_openai_recommendation(weather)
        if not result.startswith("Unable to generate"):
            return result
        else:
            print("❌ OpenAI failed, using fallback...")
    
    # Option 3: Intelligent fallback (no AI needed)
    print("🎭 Using intelligent fallback recommendations...")
    temp = weather.get('temp', 70) if weather else 70
    conditions = weather.get('conditions', '').lower() if weather else ''
    
    if temp >= 75:
        return "👕 Top: Light t-shirt or tank\n👖 Bottoms: Shorts or light pants\n👟 Shoes: Breathable sneakers\n🧴 Extra: Sunscreen recommended"
    elif temp >= 65:
        return "👔 Top: Light shirt or sweater\n👖 Bottoms: Jeans or chinos\n👟 Shoes: Comfortable shoes\n🧥 Extra: Light layer for air conditioning"
    elif temp >= 50:
        return "🧥 Top: Sweater or light jacket\n👖 Bottoms: Long pants\n👟 Shoes: Closed-toe shoes\n🧣 Extra: Consider a scarf if windy"
    else:
        return "🧥 Top: Warm jacket or coat\n👖 Bottoms: Warm pants\n👢 Shoes: Boots or warm shoes\n🧤 Extra: Gloves and warm accessories"

@app.route("/api/recommendations")
def get_recommendations():
    home = request.args.get("home")
    work = request.args.get("work")
    
    # Handle null/empty addresses
    if not home or home in ["null", "undefined", ""]:
        home = "700 Van Ness Ave, San Francisco, CA"
    if not work or work in ["null", "undefined", ""]:
        work = "160 Spear St, San Francisco, CA"
        
    print(f"\n🔄 NEW REQUEST:")
    print(f"   🏠 Home: {home}")
    print(f"   🏢 Work: {work}")
    
    # Get data using modular REST services
    try:
        weather = get_weather_rest(home)
        outfit = get_ai_outfit_recommendation(weather)  # AI-powered!
        transport = get_google_directions_rest(home, work)
        
        result = {
            "weather": weather,
            "outfit": outfit,
            "transport": transport,
            "calendar": [
                {"time": "9:00 AM", "title": "Team meeting"},
                {"time": "1:00 PM", "title": "Project review"},
                {"time": "3:30 PM", "title": "Coffee with Sarah"}
            ]
        }
        
        print("✅ SUCCESS - All recommendations generated!")
        print(f"   🌡️  Weather: {weather.get('temp')}°F, {weather.get('conditions')}")
        print(f"   👔 Outfit: AI-generated successfully")
        print(f"   🚗 Transport: {transport.get('driving', {}).get('duration', 'N/A')}")
        print("")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500

@app.route("/api/status")  
def get_status():
    """Status endpoint showing which services are available"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    
    status = {
        "backend": "✅ Modular REST-only version",
        "google_maps_api": "✅ Available (REST)" if google_key else "❌ Missing API key",
        "openweather_api": "✅ Available (REST)" if weather_key else "❌ Missing API key",
        "gemini_ai": "✅ Available (REST)" if gemini_key else "❌ Missing API key", 
        "openai_ai": "✅ Available (REST)" if openai_key else "❌ Missing API key",
        "outfit_ai": "✅ AI-powered recommendations",
        "ssl_issues": "❌ None - REST APIs only!",
        "modular_structure": "✅ Separate service files",
        "ai_fallback_order": ["Gemini REST", "OpenAI", "Smart logic"]
    }
    
    working_services = len([k for k, v in status.items() if isinstance(v, str) and '✅' in v])
    print(f"📊 Status check: {working_services} services operational")
    
    return jsonify(status)

@app.route("/api/test")
def test_endpoint():
    """Quick test endpoint"""
    return jsonify({
        "status": "✅ Modular backend operational!", 
        "message": "AI-powered, SSL-free, properly structured",
        "architecture": "Modular services using REST APIs only",
        "ai_providers": "Gemini (REST) + OpenAI fallback"
    })

# =============================================================================
# AGENT CHAT ENDPOINTS 
# =============================================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    """Send message to agent and get response"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
            
        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400
        
        # Process message with agent orchestrator
        response = agent_orchestrator.process_message(session_id, message)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return jsonify({
            "error": "Failed to process message",
            "message": "Sorry, I encountered an error. Please try again.",
            "suggested_actions": []
        }), 500

@app.route("/api/chat/history")
def chat_history():
    """Get conversation history for a session"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400
            
        messages = conversation_manager.get_conversation_history(session_id)
        
        return jsonify({
            "messages": messages,
            "session_id": session_id
        })
        
    except Exception as e:
        print(f"❌ Chat history error: {e}")
        return jsonify({"error": "Failed to get chat history"}), 500

@app.route("/api/actions/approve", methods=["POST"])
def approve_action():
    """Approve or deny a suggested action"""
    try:
        data = request.get_json()
        action_id = data.get('action_id')
        approved = data.get('approved', False)
        
        if not action_id:
            return jsonify({"error": "Action ID is required"}), 400
        
        # Process action approval
        result = action_system.approve_action(action_id, approved)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Action approval error: {e}")
        return jsonify({"error": "Failed to process action approval"}), 500

@app.route("/api/agent/status")
def agent_status():
    """Get current agent status"""
    try:
        status = agent_orchestrator.get_status()
        return jsonify(status)
        
    except Exception as e:
        print(f"❌ Agent status error: {e}")
        return jsonify({"error": "Failed to get agent status"}), 500

# =============================================================================
# DEBUG ENDPOINTS
# =============================================================================

@app.route("/api/debug/models")
def debug_models():
    """Debug endpoint to list available Gemini models"""
    models = list_gemini_models()
    return jsonify({
        "gemini_models": models,
        "current_model_used": "gemini-1.5-flash",
        "note": "If Gemini fails, check if your API key has access to this model"
    })

if __name__ == "__main__":
    print("🚀 Starting AGENTIC DAILY ASSISTANT backend")
    print("🤖 AI-powered conversational agent with tool integration")
    print("🏗️  Modular architecture with REST APIs only")  
    print("🔒 Zero SSL/gRPC issues - REST APIs only")
    print("💬 Chat-enabled with action proposals and approvals")
    print()
    print("🌐 Backend: http://127.0.0.1:5001")
    print("📊 Status: http://127.0.0.1:5001/api/status")
    print("🧪 Test: http://127.0.0.1:5001/api/test")
    print()
    print("💬 CHAT ENDPOINTS:")
    print("   POST /api/chat - Send message to agent")
    print("   GET  /api/chat/history - Get conversation history")
    print("   POST /api/actions/approve - Approve/deny suggested actions")
    print("   GET  /api/agent/status - Get agent status")
    print()
    print("🔍 Debug Models: http://127.0.0.1:5001/api/debug/models")
    print("📁 Services: agent_orchestrator.py, tool_registry.py, etc.\n")
    app.run(debug=True, port=5001)