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
    <Card 
      title="Commute" 
      headerColor="bg-green-500" 
      contentColor="bg-green-50"
    >
      {commute.driving && !commute.driving.error && (
        <p className="text-black text-sm font-medium mb-2">
          <span className="font-semibold">🚗 Driving:</span> {commute.driving.duration}
          {commute.driving.distance && <span className="text-gray-700 text-xs"> ({commute.driving.distance})</span>}
        </p>
      )}
      
      {commute.driving && commute.driving.error && (
        <p className="text-black text-sm font-medium mb-2">
          <span className="font-semibold">🚗 Driving:</span> <span className="text-gray-600">Route unavailable</span>
        </p>
      )}
      {commute.walking && (
        <p className="text-black text-sm font-medium mb-2">
          <span className="font-semibold">🚶 Walking:</span> {commute.walking.duration}
          {commute.walking.distance && <span className="text-gray-700 text-xs"> ({commute.walking.distance})</span>}
        </p>
      )}
      {commute.transit && (
        <div>
          <p className="text-black text-sm font-medium mb-2">🚌 Public Transit:</p>
          {Array.isArray(commute.transit) && commute.transit.length > 0 ? (
            <ul className="ml-3 mt-1 space-y-1.5">
              {sortedTransit.map((option, idx) => (
                <li key={idx} className="text-black text-sm">
                  <span className="font-medium">{option.duration}</span>
                  {option.lines && option.lines.length > 0 && (
                    <div className="text-xs text-gray-700 mt-1">
                      {option.lines.map((line, lidx) => (
                        <span key={lidx}>
                          <span className="font-semibold">{line.name}</span> from <span className="italic">{line.departure_stop}</span> at <span>{line.departure_time}</span>
                          {lidx < option.lines.length - 1 && <span> → </span>}
                        </span>
                      ))}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="ml-3 text-gray-700 text-sm">No route found</p>
          )}
        </div>
      )}
    </Card>
  );
}

