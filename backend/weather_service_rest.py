"""Weather service using REST APIs only"""

import os
import requests
from dotenv import load_dotenv
from google_maps_service_rest import get_coordinates_rest

load_dotenv()

def get_weather_rest(address):
    """Get weather using REST APIs for both geocoding and weather data"""
    try:
        # Get coordinates using REST API
        lat, lng = get_coordinates_rest(address)
        
        # Get weather data
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            print("❌ OpenWeather API key not set - using mock weather")
            return {
                "temp": 68.0,
                "conditions": "Partly Cloudy",
                "humidity": 50,
                "feels_like": 68.0
            }

        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": api_key,
            "units": "imperial"
        }

        print(f"🌤️  Getting weather for coordinates: {lat}, {lng}")
        response = requests.get(url, params=params, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            weather = {
                "temp": round(data["main"]["temp"], 1),
                "conditions": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "feels_like": round(data["main"]["feels_like"], 1)
            }
            print(f"✅ Weather retrieved: {weather['temp']}°F, {weather['conditions']}")
            return weather
        else:
            print(f"❌ OpenWeather API error: {response.status_code}")
            return {
                "temp": 68.0,
                "conditions": "Unable to fetch weather",
                "humidity": 50,
                "feels_like": 68.0
            }
    except Exception as e:
        print(f"❌ Weather service error: {e}")
        return {
            "temp": 68.0,
            "conditions": "Weather service unavailable",
            "humidity": 50,
            "feels_like": 68.0
        }