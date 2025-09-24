from flask import Flask, jsonify
from flask_cors import CORS
from weather_service import get_weather
from gemini_service import get_gemini_recommendation
from google_maps_service import get_google_directions

app = Flask(__name__)
CORS(app)   # must be called after app is created

@app.route("/api/recommendations")
def get_recommendations():
    weather = get_weather()
    outfit = get_gemini_recommendation(weather)
    transport = get_google_directions()
    return jsonify({
        "weather":  weather,
        "outfit": outfit,
        "transport": transport,
        "calendar": [
            { "time": "9:00 AM", "title": "Team meeting" },
            { "time": "1:00 PM", "title": "Project review" }
        ]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)