// src/pages/Dashboard.jsx
import WeatherCard from "../components/WeatherCard";
import OutfitSuggestion from "../components/OutfitSuggestion";
import CommuteInfo from "../components/CommuteInfo";
import CalendarEvents from "../components/CalendarEvents";

import { useEffect, useState } from "react";
import { fetchRecommendations } from "../services/api";


export default function Dashboard() {
    const [home, setHome] = useState(null);
    const [work, setWork] = useState(null);
    const [data, setData] = useState(null);
    useEffect(() => {
        const storedHome = localStorage.getItem("home");
        const storedWork = localStorage.getItem("work");
        if (storedHome) setHome(storedHome);
        if (storedWork) setWork(storedWork);
        fetchRecommendations(storedHome, storedWork)
            .then(setData)
            .catch(console.error);
    }, []);

    // Placeholder sample data
    //const weather = { temp: 72, conditions: "Sunny" };
    //const outfit = "T-shirt, jeans, sneakers";
    //const commute = { mode: "Bus", departure: "8:15 AM" };
    //const events = [
    //    { time: "9:00 AM", title: "Team meeting" },
    //    { time: "1:00 PM", title: "Project review" },
    //];

    if (!data) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-400 via-fuchsia-200 to-pink-200">
                <span className="text-xl text-gray-700">Loading...</span>
            </div>
        );
    }

    // Map backend transport/departure_time to commute prop
    const commute = {
        mode: data.transport,
        departure: data.departure_time,
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-300 via-fuchsia-200 to-pink-100 py-8">
            <div className="p-8 font-sans w-full h-full mx-auto rounded-3xl">
                <h1 className="text-4xl font-extrabold mb-8 w-full block text-white drop-shadow-lg">Good Morning!</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                    <div className="flex flex-col gap-8">
                        <WeatherCard weather={data.weather} />
                        <CommuteInfo commute={data.transport} />
                    </div>
                    <div className="flex flex-col gap-8">
                        <OutfitSuggestion outfit={data.outfit} />
                        <CalendarEvents events={data.calendar} />
                    </div>
                </div>
            </div>
        </div>
    );
}
