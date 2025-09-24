import os, requests

def get_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = "San Francisco"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": round(data["main"]["temp"]),
            "conditions": data["weather"][0]["description"].capitalize()
        }
    return {"error": "Unable to fetch weather data"}