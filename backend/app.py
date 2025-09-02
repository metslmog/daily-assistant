# backend/app.py
from flask import Flask, jsonify
from routes.weather import get_weather
from routes.calendar import get_calendar_events
from routes.transit import get_transit_info
from routes.gemini import get_gemini_recommendation

app = Flask(__name__)

@app.route("/api/recommendations", methods=["GET"])
def recommendations():
    weather = get_weather()
    calendar_events = get_calendar_events()
    transit = get_transit_info(calendar_events)
    
    ai_suggestion = get_gemini_recommendation(weather, calendar_events, transit)
    
    return jsonify(ai_suggestion)

if __name__ == "__main__":
    app.run(debug=True)