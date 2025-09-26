import math
import requests
import time

def haversine_distance(a, b):
    # a, b: dict with 'lat' and 'lon'
    lat1, lon1 = a['lat'], a['lon']
    lat2, lon2 = b['lat'], b['lon']
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a_calc = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a_calc))
    return R * c

def get_real_route(a, b):
    """Get actual road route using free OSRM service"""
    try:
        # OSRM free service - no API key needed
        url = f"http://router.project-osrm.org/route/v1/driving/{a['lon']},{a['lat']};{b['lon']},{b['lat']}"
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['routes']:
                route = data['routes'][0]
                # Distance in meters, convert to km
                distance_km = route['distance'] / 1000
                # Get actual road coordinates
                coordinates = route['geometry']['coordinates']
                # Convert to lat/lon format
                waypoints = [{'lat': coord[1], 'lon': coord[0]} for coord in coordinates]
                
                print(f"Real routing: {distance_km:.2f}km via actual roads ({len(waypoints)} waypoints)")
                return distance_km, waypoints
        
        # Fallback
        straight_distance = haversine_distance(a, b)
        fallback_distance = straight_distance * 1.3
        print(f"Routing fallback: {fallback_distance:.2f}km (estimated)")
        return fallback_distance, [a, b]
            
    except Exception as e:
        print(f"Routing error: {e}, using fallback")
        straight_distance = haversine_distance(a, b)
        return straight_distance * 1.3, [a, b]

def road_aware_distance(a, b):
    """Get road distance (wrapper for compatibility)"""
    distance, _ = get_real_route(a, b)
    return distance

def calculate_route_distance(route):
    """Calculate total route distance using road-aware calculations"""
    total_distance = 0
    
    for i in range(len(route) - 1):
        segment_distance = road_aware_distance(route[i], route[i + 1])
        total_distance += segment_distance
    
    return total_distance

def generate_road_waypoints(a, b):
    """Get actual road waypoints using real routing service"""
    _, waypoints = get_real_route(a, b)
    return waypoints