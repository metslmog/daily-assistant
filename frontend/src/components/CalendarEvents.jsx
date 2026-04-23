import Card from "./Card";

export default function CalendarEvents({ events }) {
  return (
    <Card 
      title="Today's Events" 
      headerColor="bg-amber-500" 
      contentColor="bg-amber-50"
    >
      <ul className="space-y-1.5">
        {events.map((event, idx) => (
          <li key={idx} className="text-black text-base font-medium">
            📅 {event.time} — {event.title}
          </li>
        ))}
      </ul>
    </Card>
  );
}
