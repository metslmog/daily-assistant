// src/pages/Dashboard.jsx


import WeatherCard from "../components/WeatherCard";
import OutfitSuggestion from "../components/OutfitSuggestion";
import CommuteInfo from "../components/CommuteInfo";
import CalendarEvents from "../components/CalendarEvents";
import Settings from "./Settings";
import { useLocation, useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import { Cog6ToothIcon } from '@heroicons/react/24/outline';

import { useEffect, useState } from "react";
import { fetchRecommendations } from "../services/api";


export default function Dashboard() {
    const [home, setHome] = useState(null);
    const [work, setWork] = useState(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [loadingStatus, setLoadingStatus] = useState("Connecting to backend...");
    const location = useLocation();
    const navigate = useNavigate();
    const showSettings = location.pathname === "/settings";
    
    useEffect(() => {
        const storedHome = localStorage.getItem("home");
        const storedWork = localStorage.getItem("work");
        if (storedHome) setHome(storedHome);
        if (storedWork) setWork(storedWork);
        
        setLoadingStatus("Fetching your daily recommendations...");
        
        fetchRecommendations(storedHome, storedWork)
            .then((result) => {
                setData(result);
                setLoading(false);
                setLoadingStatus("Complete!");
            })
            .catch((err) => {
                console.error("API Error:", err);
                setError(`Failed to load recommendations: ${err.message}`);
                setLoading(false);
            });
    }, []);

    // Placeholder sample data
    //const weather = { temp: 72, conditions: "Sunny" };
    //const outfit = "T-shirt, jeans, sneakers";
    //const commute = { mode: "Bus", departure: "8:15 AM" };
    //const events = [
    //    { time: "9:00 AM", title: "Team meeting" },
    //    { time: "1:00 PM", title: "Project review" },
    //];

    if (loading) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-400 via-fuchsia-200 to-pink-200">
                <div className="bg-white/80 backdrop-blur-sm rounded-lg p-8 shadow-lg">
                    <div className="flex items-center space-x-3">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        <span className="text-xl text-gray-700">{loadingStatus}</span>
                    </div>
                    <div className="mt-4 text-sm text-gray-500">
                        This may take a moment while we gather your data...
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-red-400 via-pink-200 to-orange-200">
                <div className="bg-white/90 backdrop-blur-sm rounded-lg p-8 shadow-lg max-w-md">
                    <div className="text-center">
                        <div className="text-6xl mb-4">⚠️</div>
                        <h2 className="text-xl font-bold text-gray-800 mb-2">Oops! Something went wrong</h2>
                        <p className="text-gray-600 mb-4">{error}</p>
                        <button 
                            onClick={() => window.location.reload()} 
                            className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                        >
                            Try Again
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-400 via-fuchsia-200 to-pink-200">
                <span className="text-xl text-gray-700">No data received</span>
            </div>
        );
    }

    // Map backend transport/departure_time to commute prop
    const commute = {
        mode: data.transport,
        departure: data.departure_time,
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-300 via-fuchsia-200 to-pink-100 py-8 relative">
            <div className="flex items-center justify-between px-8 mb-8">
                <h1 className="text-4xl font-extrabold text-white drop-shadow-lg">Good Morning!</h1>
                <Link to="/settings" className="z-10 ml-4" title="Settings">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="purple" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>
                </Link>
            </div>
            <div className="p-8 font-sans w-full h-full mx-auto rounded-3xl">
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
            {/* Settings drawer popup */}
            {showSettings && (
                <div className="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-2xl z-50 transition-transform duration-300" style={{ transform: "translateX(0)" }}>
                    <button
                        className="absolute top-4 right-4 text-gray-500 hover:text-blue-600 text-2xl"
                        onClick={() => navigate("/")}
                        title="Close"
                    >
                        &times;
                    </button>
                    <Settings />
                </div>
            )}
        </div>
    );
}
