import Card from "./Card";

export default function WeatherCard({ weather }) {
  return (
    <Card 
      title="Weather" 
      headerColor="bg-blue-500" 
      contentColor="bg-blue-50"
    >
      <p className="text-black text-sm font-medium">{weather.temp}°F — {weather.conditions}</p>
    </Card>
  );
}