// Sort transit options by duration (ascending)
import Card from "./Card";

export default function CommuteInfo({ commute }) {
  if (!commute) return null;

  // Sort transit options by duration (ascending)
  const sortedTransit =
    commute.transit && Array.isArray(commute.transit)
      ? [...commute.transit].sort((a, b) => {
        // Try to parse durations as minutes, fallback to string compare
        const parseDuration = (str) => {
          // e.g., "15 mins", "1 hr 5 mins"
          if (!str) return Infinity;
          const hrMatch = str.match(/(\d+)\s*hr/);
          const minMatch = str.match(/(\d+)\s*min/);
          let mins = 0;
          if (hrMatch) mins += parseInt(hrMatch[1], 10) * 60;
          if (minMatch) mins += parseInt(minMatch[1], 10);
          return mins;
        };
        return parseDuration(a.duration) - parseDuration(b.duration);
      })
      : [];

  return (
    <Card>
      <h2 className="text-xl font-bold mb-4 text-green-600">Commute</h2>
      {commute.driving && (
        <p className="text-green-700 text-lg font-medium">
          <span className="font-semibold">Driving:</span> {commute.driving.duration}
        </p>
      )}
      {commute.walking && (
        <p className="text-green-700 text-lg font-medium">
          <span className="font-semibold">Walking:</span> {commute.walking.duration}
        </p>
      )}
      {commute.transit && (
        <p>
          <span className="text-green-700 text-lg font-medium">Public Transit:</span>
          {Array.isArray(commute.transit) && commute.transit.length > 0 ? (
            <ul className="ml-4 mt-1 space-y-1">
              {sortedTransit.map((option, idx) => (
                <li key={idx}>
                  <span className="font-medium">{option.duration} | </span>
                  {option.lines && option.lines.length > 0 && (
                    <span>
                      {option.lines.map((line, lidx) => (
                        <span key={lidx}>
                          <span className="font-semibold">{line.name}</span> from <span className="italic">{line.departure_stop}</span> at <span>{line.departure_time}</span>
                          {lidx < option.lines.length - 1 && <span> &rarr; </span>}
                        </span>
                      ))}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="ml-4 text-green-700">No route found</p>
          )}
        </p>
      )}
    </Card>
  );
}

