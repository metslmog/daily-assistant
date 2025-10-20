import Card from "./Card";

export default function WeatherCard({ weather }) {
  return (
    <Card>
        <h2 className="text-xl font-bold mb-2 text-red-600">Weather</h2>
        <p className="text-red-500 text-lg font-medium">{weather.temp}°F — {weather.conditions}</p>
    </Card>
  );
}