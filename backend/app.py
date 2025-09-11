from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # must be called after app is created

@app.route("/api/recommendations")
def get_recommendations():
    return jsonify({
        "weather":  { "temp": 72, "conditions": "Sunny" },
        "outfit": "T-shirt and jeans",
        "transport": { "mode": "Bus", "departure": "8:15 AM" },
        "calendar": [
            { "time": "9:00 AM", "title": "Team meeting" },
            { "time": "1:00 PM", "title": "Project review" }
        ]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001)