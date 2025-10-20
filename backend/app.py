from flask import Flask, jsonify
from flask_cors import CORS
from weather_service import get_weather
from gemini_service import get_gemini_recommendation
from google_maps_service import get_google_directions
from flask import request

app = Flask(__name__)
CORS(app)   # must be called after app is created

@app.route("/api/recommendations")
def get_recommendations():
    home = request.args.get("home")
    work = request.args.get("work")
    if not home:
        home = "700 Van Ness Ave, San Francisco, CA"
    if not work:
        work = "160 Spear St, San Francisco, CA"

    weather = get_weather(home)
    # If weather has error, skip Gemini and return error message for outfit
    if "error" in weather:
        outfit = "Unable to generate outfit suggestion: weather data unavailable."
    else:
        outfit = get_gemini_recommendation(weather)
    transport = get_google_directions(home, work)
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