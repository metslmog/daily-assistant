import os
import requests
import logging
import googlemaps

def get_coordinates(address):
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return {"error": "Google Maps API key not set in environment variables"}
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print("Geocoding failed for address:", address)
        return 37.2664, 122.0296  # Default coordinates if geocoding fails

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