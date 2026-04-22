"""Google Maps service using REST API only (no gRPC client)"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_coordinates_rest(address):
    """Get coordinates using Google Maps Geocoding REST API"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ Google Maps API key not set - using default coordinates")
        return 37.7749, -122.4194  # San Francisco coordinates
        
    # Handle null/empty addresses
    if not address or address in ["null", "undefined", ""]:
        print("❌ Invalid address - using default coordinates")
        return 37.7749, -122.4194
        
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": api_key
        }
        
        print(f"🗺️  Geocoding via REST: {address}")
        response = requests.get(url, params=params, timeout=10, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                location = data['results'][0]['geometry']['location']
                lat, lng = location['lat'], location['lng']
                print(f"✅ Geocoding successful: {lat}, {lng}")
                return lat, lng
            else:
                print(f"❌ No geocoding results for: {address}")
                return 37.7749, -122.4194
        else:
            print(f"❌ Geocoding API error: {response.status_code}")
            return 37.7749, -122.4194
            
    except Exception as e:
        print(f"❌ Geocoding exception: {e}")
        return 37.7749, -122.4194

def get_directions_rest(origin, destination):
    """Get directions for all modes using Google Maps Directions REST API"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("❌ Google Maps API key not set - using fallback directions")
        return {
            "driving": {"duration": "25-35 minutes", "distance": "~15 miles"},
            "transit": [{"duration": "45-60 minutes", "lines": [{"name": "Public Transit", "departure_time": "Every 10-15 min"}]}],
            "walking": {"duration": "2+ hours", "distance": "8+ miles"}
        }
    
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    summary = {}
    
    # Get directions for each mode like the original implementation
    modes = ['driving', 'transit', 'walking']
    for mode in modes:
        try:
            params = {
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "key": api_key,
                "alternatives": "true"
            }
            
            # Add departure time for transit
            if mode == 'transit':
                from datetime import datetime
                import time
                departure_time = int(time.mktime(datetime.now().timetuple()))
                params['departure_time'] = departure_time
            
            print(f"🚗🚌🚶 Getting {mode} directions: {origin} → {destination}")
            response = requests.get(base_url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('routes'):
                    leg = data['routes'][0]['legs'][0]
                    duration_text = leg['duration']['text']
                    
                    if mode == 'driving':
                        summary['driving'] = {
                            'duration': duration_text,
                            'distance': leg['distance']['text']
                        }
                        print(f"✅ Driving: {duration_text}, {leg['distance']['text']}")
                    
                    elif mode == 'walking':
                        summary['walking'] = {
                            'duration': duration_text,
                            'distance': leg['distance']['text']
                        }
                        print(f"✅ Walking: {duration_text}, {leg['distance']['text']}")
                    
                    elif mode == 'transit':
                        # Collect multiple transit options like the original
                        transit_options = []
                        for route in data['routes']:
                            leg = route['legs'][0]
                            option = {'duration': leg['duration']['text'], 'lines': []}
                            
                            # Extract transit line information
                            for step in leg['steps']:
                                if step.get('travel_mode') == 'TRANSIT':
                                    transit_details = step.get('transit_details', {})
                                    line = transit_details.get('line', {})
                                    option['lines'].append({
                                        'name': line.get('short_name') or line.get('name') or 'Transit',
                                        'departure_time': transit_details.get('departure_time', {}).get('text', 'N/A'),
                                        'departure_stop': transit_details.get('departure_stop', {}).get('name', 'N/A')
                                    })
                            
                            transit_options.append(option)
                        
                        summary['transit'] = transit_options
                        print(f"✅ Transit: {len(transit_options)} option(s), first: {transit_options[0]['duration'] if transit_options else 'N/A'}")
                else:
                    print(f"❌ No {mode} routes found")
                    summary[mode] = {'error': 'No route found'}
            else:
                print(f"❌ {mode.title()} API error: {response.status_code}")
                summary[mode] = {'error': f'API Error: {response.status_code}'}
                
        except Exception as e:
            print(f"❌ {mode.title()} exception: {e}")
            summary[mode] = {'error': 'No route found'}
    
    # Provide fallbacks for any missing modes
    if 'driving' not in summary:
        summary['driving'] = {"duration": "25-35 minutes", "distance": "~15 miles"}
    if 'transit' not in summary:
        summary['transit'] = [{"duration": "45-60 minutes", "lines": [{"name": "Public Transit", "departure_time": "Every 10-15 min"}]}]
    if 'walking' not in summary:
        summary['walking'] = {"duration": "2+ hours", "distance": "8+ miles"}
            
    return summary

def get_google_directions_rest(home, work):
    """Main function to get directions between home and work"""
    # Validate addresses
    if not home or home in ["null", "undefined", ""]:
        home = "700 Van Ness Ave, San Francisco, CA"
    if not work or work in ["null", "undefined", ""]:  
        work = "160 Spear St, San Francisco, CA"

    return get_directions_rest(home, work)