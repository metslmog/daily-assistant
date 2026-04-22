import os
import requests
import logging
import googlemaps
import ssl
from dotenv import load_dotenv

# Try to configure SSL certificates if certifi is available
try:
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass  # certifi not available, use system defaults

def get_coordinates(address):
    # Handle null/empty addresses
    if not address or address == "null" or address == "undefined":
        print("Geocoding failed for address: null - using default coordinates")
        return 37.7749, -122.4194  # San Francisco coordinates
        
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Google Maps API key not set - using default coordinates")
        return 37.7749, -122.4194  # San Francisco coordinates
        
    try:
        gmaps = googlemaps.Client(key=api_key)
        print(f"Attempting to geocode: {address}")
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            print(f"Geocoding successful: {location['lat']}, {location['lng']}")
            return location['lat'], location['lng']
        else:
            print("Geocoding failed for address:", address)
            return 37.7749, -122.4194  # Default coordinates if geocoding fails
    except ssl.SSLError as e:
        print(f"SSL error during geocoding for {address}: {e}")
        return 37.7749, -122.4194  # Default coordinates on SSL error
    except googlemaps.exceptions.ApiError as e:
        print(f"Google Maps API error for {address}: {e}")
        return 37.7749, -122.4194  # Default coordinates on API error
    except Exception as e:
        print(f"General geocoding error for address {address}: {e}")
        return 37.7749, -122.4194  # Default coordinates on error

def get_weather(address):
    lat, lon = get_coordinates(address)

    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeather API key not set in environment variables"}
    url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "imperial"
    }

    try:
        response = requests.get(url, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data["main"]["temp"],
                "conditions": data["weather"][0]["description"].capitalize()
            }
        else:
            return {"error": "Unable to fetch weather data"}
    except Exception as e:
        return {"error": f"Exception occurred: {e}"}