"""Gemini AI service using REST API instead of gRPC SDK"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def list_gemini_models():
    """List available Gemini models for debugging"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "No API key available"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            print(f"🔍 Available Gemini models: {models}")
            return models
        else:
            print(f"❌ Failed to list models: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def get_gemini_recommendation_rest(weather):
    """
    Get outfit recommendation using Gemini REST API (no gRPC/SSL issues)
    """
    # Defensive: check for required keys
    if not weather or "conditions" not in weather or "temp" not in weather:
        return "Unable to generate outfit suggestion: weather data unavailable."
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Unable to generate outfit suggestion: Gemini API key not configured."
    
    try:
        print(f"🤖 Generating AI outfit for {weather['temp']}°F, {weather['conditions']}")
        
        # Use Gemini REST API directly (no gRPC!) - using stable model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
        Given the current weather conditions: {weather["conditions"]} with a temperature of {weather["temp"]}°F,
        suggest an appropriate outfit.
        
        Respond in this exact format:
        👕 Top: [specific clothing item]
        👖 Bottoms: [specific clothing item]  
        👟 Shoes: [specific footwear]
        🧥 Extra: [additional items if needed for weather]
        
        Consider the temperature and weather conditions to give practical, stylish advice.
        """
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                content = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Gemini AI outfit generated successfully")
                return content.strip()
            else:
                print(f"❌ Gemini API: No candidates in response")
                return "Unable to generate outfit suggestion: API response incomplete."
        else:
            print(f"❌ Gemini API error: {response.status_code} - {response.text}")
            return f"Unable to generate outfit suggestion: API error {response.status_code}."
            
    except Exception as e:
        print(f"❌ Gemini REST API error: {e}")
        return f"Unable to generate outfit suggestion: {str(e)}"