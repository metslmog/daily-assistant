import googlemaps
from datetime import datetime
import os
import ssl
import urllib3
from dotenv import load_dotenv

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try to configure SSL certificates if certifi is available
try:
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass  # certifi not available, use system defaults

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
    # Create SSL context that doesn't verify certificates (for development only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    gmaps = googlemaps.Client(key=api_key)
    now = departure_time or datetime.now()
    summary = {}

    modes = ['driving', 'transit', 'walking']
    for mode in modes:
        try:
            print(f"Getting {mode} directions from {origin} to {destination}")
            directions_result = gmaps.directions(
                origin,
                destination,
                mode=mode,
                departure_time=now,
                alternatives=True
            )
            print(f"Successfully got {mode} directions")

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
        except ssl.SSLError as e:
            print(f"SSL Error for {mode}: {e}")
            summary[mode] = {'error': 'SSL certificate issue - using fallback'}
            continue
        except googlemaps.exceptions.ApiError as e:
            print(f"Google Maps API Error for {mode}: {e}")
            summary[mode] = {'error': f'API Error: {str(e)}'}
            continue  
        except Exception as e:
            # Handle cases where a route for a specific mode isn't found
            print(f"General error for {mode}: {e}")
            summary[mode] = {'error': 'No route found'}
            continue

    return summary

def get_google_directions(home, work):
    load_dotenv()
    MY_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    if not MY_API_KEY:
        return {
            "error": "Google Maps API key not configured. Please add GOOGLE_MAPS_API_KEY to .env file",
            "driving": {"error": "API key missing"},
            "transit": [{"error": "API key missing"}],
            "walking": {"error": "API key missing"}
        }

    # Validate addresses
    if not home or home == "null":
        home = "700 Van Ness Ave, San Francisco, CA"
    if not work or work == "null":  
        work = "160 Spear St, San Francisco, CA"

    try:
        travel_summary = get_travel_summary(MY_API_KEY, home, work)
        return travel_summary
    except Exception as e:
        return {
            "error": f"Failed to get directions: {str(e)}",
            "driving": {"error": "Service unavailable"},
            "transit": [{"error": "Service unavailable"}], 
            "walking": {"error": "Service unavailable"}
        }