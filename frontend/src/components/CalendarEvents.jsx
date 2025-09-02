export default function CalendarEvents({ events }) {
  return (
    <div className="bg-gradient-to-br from-purple-100 to-purple-200 shadow-lg rounded-2xl p-6 border border-purple-200 hover:shadow-2xl transition-all">
      <h2 className="text-xl font-bold mb-2 text-purple-600">Today's Events</h2>
      <ul className="space-y-1">
        {events.map((event, idx) => (
          <li key={idx} className="text-purple-700 text-lg font-medium">
            {event.time} — {event.title}
          </li>
        ))}
      </ul>
    </div>
  );
}
