// src/pages/Dashboard.jsx
import WeatherCard from "../components/WeatherCard";
import OutfitSuggestion from "../components/OutfitSuggestion";
import CommuteInfo from "../components/CommuteInfo";
import CalendarEvents from "../components/CalendarEvents";

export default function Dashboard() {
    // Placeholder sample data
    const weather = { temp: 72, conditions: "Sunny" };
    const outfit = "T-shirt, jeans, sneakers";
    const commute = { mode: "Bus", departure: "8:15 AM" };
    const events = [
        { time: "9:00 AM", title: "Team meeting" },
        { time: "1:00 PM", title: "Project review" },
    ];

    return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 via-fuchsia-200 to-pink-200 py-8">
            <div className="p-8 font-sans w-full max-w-3xl mx-auto rounded-3xl">
                <h1 className="text-4xl font-extrabold mb-8 w-full block text-white drop-shadow-lg">Good Morning!</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <WeatherCard weather={weather} />
                    <OutfitSuggestion outfit={outfit} />
                    <CommuteInfo commute={commute} />
                    <CalendarEvents events={events} />
                </div>
            </div>
        </div>
    );
}
