# Daily Assistant

A full-stack productivity dashboard that combines weather, commute, outfit suggestions, and calendar events—all in one place.

## Features

- **Weather**: Get current weather for your home address.
- **Commute**: See driving, walking, and public transit options between home and work, powered by Google Maps.
- **Outfit Suggestion**: AI-generated outfit recommendations based on the weather (using Google Gemini).
- **Calendar**: Displays your daily events.
- **Settings Drawer**: Update your home and work addresses in a right-side popup.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, React Router, Heroicons
- **Backend**: Flask, Flask-CORS, Google Maps API, OpenWeatherMap API, Google Gemini API
- **AI**: Outfit suggestions via Gemini
- **Environment**: Python 3, Node.js

## Getting Started

### Backend Setup

1. **Install dependencies:**
	```sh
	cd backend
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	```

2. **Environment variables:**
	- Create a `.env` file in `backend/` with:
	  ```
	  GOOGLE_MAPS_API_KEY=your_google_maps_api_key
	  OPENWEATHER_API_KEY=your_openweather_api_key
	  GEMINI_API_KEY=your_gemini_api_key
	  ```

3. **Run the backend:**
	```sh
	python app.py
	```
	The backend runs on `http://localhost:5001`.

### Frontend Setup

1. **Install dependencies:**
	```sh
	cd frontend
	npm install
	```

2. **Run the frontend:**
	```sh
	npm run dev
	```
	The frontend runs on `http://localhost:5173` (default Vite port).

## Usage

- Open the frontend in your browser.
- Click the settings icon (gear) to open the settings drawer and set your home/work addresses.
- The dashboard will show weather, commute options, outfit suggestions, and calendar events.

## API Endpoints

- `GET /api/recommendations?home=...&work=...`
  - Returns weather, outfit, commute, and calendar data.

## Customization

- **Calendar events**: Edit in `backend/app.py`.
- **Outfit prompt**: Edit in `backend/gemini_service.py`.
- **Styling**: Tailwind classes in frontend components.

## License

MIT