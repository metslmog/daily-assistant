import Card from "./Card";

export default function CalendarEvents({ events }) {
  return (
    <Card>
        <h2 className="text-xl font-bold mb-2 text-purple-600">Today's Events</h2>
        <ul className="space-y-1">
          {events.map((event, idx) => (
            <li key={idx} className="text-purple-700 text-lg font-medium">
              {event.time} — {event.title}
            </li>
          ))}
        </ul>
    </Card>
  );
}
