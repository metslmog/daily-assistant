import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv

def get_travel_summary(api_key, origin, destination, departure_time=None):
    """
    Provides a concise summary of travel times and public transport schedules.

    Args:
        api_key (str): Your Google Maps API key.
        origin (str): The starting location.
        destination (str): The ending location.
        departure_time (datetime, optional): The time of departure.

    Returns:
        dict: A dictionary with travel time summaries for different modes.
    """
    gmaps = googlemaps.Client(key=api_key)
    now = departure_time or datetime.now()
    summary = {}

    modes = ['driving', 'transit', 'walking']
    for mode in modes:
        try:
            directions_result = gmaps.directions(
                origin,
                destination,
                mode=mode,
                departure_time=now,
                alternatives=True
            )

            if directions_result:
                leg = directions_result[0]['legs'][0]
                duration_text = leg['duration']['text']

                if mode == 'driving':
                    summary['driving'] = {'duration': duration_text}
                
                elif mode == 'walking':
                    summary['walking'] = {'duration': duration_text}
                
                elif mode == 'transit':
                    # Collect multiple transit options if available
                    transit_options = []
                    for route in directions_result:
                        leg = route['legs'][0]
                        option = {'duration': leg['duration']['text'], 'lines': []}
                        for step in leg['steps']:
                            if step.get('travel_mode') == 'TRANSIT':
                                line = step['transit_details']['line']
                                option['lines'].append({
                                    'name': line.get('short_name') or line.get('name'),
                                    'departure_time': step['transit_details']['departure_time']['text'],
                                    'departure_stop': step['transit_details']['departure_stop']['name']
                                })
                        transit_options.append(option)
                    # Store all options; first one is usually the recommended
                    summary['transit'] = transit_options
        except Exception as e:
            # Handle cases where a route for a specific mode isn't found
            # e.g., no public transit available
            summary[mode] = {'error': 'No route found'}
            continue

    return summary

def get_google_directions():
    load_dotenv()
    MY_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    if not MY_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in .env file")
    START_DEST = '601 Van Ness Ave, San Francisco, CA'
    END_DEST = '160 Spear St, San Francisco, CA'

    travel_summary = get_travel_summary(MY_API_KEY, START_DEST, END_DEST)
    return travel_summary