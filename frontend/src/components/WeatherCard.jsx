export default function WeatherCard({ weather }) {
  return (
    <div className="bg-gradient-to-br from-red-100 to-red-200 shadow-lg rounded-2xl p-6 border border-red-200 hover:shadow-2xl transition-all">
      <h2 className="text-xl font-bold mb-2 text-red-600">Weather</h2>
      <p className="text-red-500 text-lg font-medium">{weather.temp}°F — {weather.conditions}</p>
    </div>
  );
}