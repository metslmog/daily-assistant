"""OpenAI service for outfit recommendations (uses REST API, no gRPC)"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_openai_recommendation(weather):
    """
    Get outfit recommendation using OpenAI API (REST-based, no SSL issues)
    """
    # Defensive: check for required keys
    if not weather or "conditions" not in weather or "temp" not in weather:
        return "Unable to generate outfit suggestion: weather data unavailable."
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Unable to generate outfit suggestion: OpenAI API key not configured."
    
    try:
        print(f"🤖 Generating OpenAI outfit for {weather['temp']}°F, {weather['conditions']}")
        
        url = "https://api.openai.com/v1/chat/completions"
        
        prompt = f"""Given the current weather conditions: {weather["conditions"]} with a temperature of {weather["temp"]}°F, suggest an appropriate outfit.

Respond in this exact format:
👕 Top: [specific clothing item]
👖 Bottoms: [specific clothing item]  
👟 Shoes: [specific footwear]
🧥 Extra: [additional items if needed for weather]

Consider the temperature and weather conditions to give practical, stylish advice."""
        
        payload = {
            "model": "gpt-4o-mini",  # Cost-effective model
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"✅ OpenAI outfit generated successfully")
                return content.strip()
            else:
                print(f"❌ OpenAI API: No choices in response")
                return "Unable to generate outfit suggestion: API response incomplete."
        else:
            print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
            return f"Unable to generate outfit suggestion: API error {response.status_code}."
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return f"Unable to generate outfit suggestion: {str(e)}"