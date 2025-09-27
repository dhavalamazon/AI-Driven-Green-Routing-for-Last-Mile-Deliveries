import math
from datetime import datetime
from utils import haversine_distance

def get_traffic_for_route(route_points, time_of_day=None):
    """Get realistic traffic conditions based on coordinates and time"""
    
    # Detect city based on coordinates
    city_info = detect_city(route_points[0])
    
    # Get city-specific traffic centers
    traffic_centers = city_info['centers']
    
    # Current time if not specified
    if time_of_day is None:
        current_hour = datetime.now().hour
    else:
        current_hour = time_of_day
    
    traffic_levels = []
    
    for point in route_points:
        # Calculate distance from city-specific traffic centers
        center_distances = [haversine_distance(point, center) for center in traffic_centers]
        
        # Base traffic by location
        base_traffic = calculate_location_traffic_generic(point, center_distances, city_info['density'])
        
        # Time-based traffic multiplier (city-specific)
        time_multiplier = get_time_traffic_multiplier(current_hour, city_info['name'])
        
        # Final traffic level (0.0 = free flow, 1.0 = heavy traffic)
        final_traffic = min(base_traffic * time_multiplier, 1.0)
        traffic_levels.append(final_traffic)
    
    # Return average traffic for the route
    return sum(traffic_levels) / len(traffic_levels)

def detect_city(point):
    """Detect which Indian city based on coordinates"""
    
    cities = {
        'bangalore': {
            'bounds': {'lat_min': 12.7, 'lat_max': 13.2, 'lon_min': 77.3, 'lon_max': 77.9},
            'centers': [
                {'lat': 12.9716, 'lon': 77.5946},  # MG Road
                {'lat': 12.8456, 'lon': 77.6603},  # Electronic City
                {'lat': 12.9500, 'lon': 77.7000}   # Marathahalli
            ],
            'density': 0.8,
            'name': 'bangalore'
        },
        'delhi': {
            'bounds': {'lat_min': 28.4, 'lat_max': 28.9, 'lon_min': 76.8, 'lon_max': 77.5},
            'centers': [
                {'lat': 28.6139, 'lon': 77.2090},  # Connaught Place
                {'lat': 28.5355, 'lon': 77.3910},  # Noida
                {'lat': 28.4595, 'lon': 77.0266}   # Gurgaon
            ],
            'density': 0.9,
            'name': 'delhi'
        },
        'mumbai': {
            'bounds': {'lat_min': 18.9, 'lat_max': 19.3, 'lon_min': 72.7, 'lon_max': 73.1},
            'centers': [
                {'lat': 19.0760, 'lon': 72.8777},  # Mumbai Central
                {'lat': 19.0330, 'lon': 72.8697},  # Worli
                {'lat': 19.1136, 'lon': 72.8697}   # Bandra
            ],
            'density': 0.95,
            'name': 'mumbai'
        },
        'hyderabad': {
            'bounds': {'lat_min': 17.2, 'lat_max': 17.6, 'lon_min': 78.2, 'lon_max': 78.7},
            'centers': [
                {'lat': 17.3850, 'lon': 78.4867},  # Charminar/Old City
                {'lat': 17.4399, 'lon': 78.3489},  # HITEC City
                {'lat': 17.4065, 'lon': 78.4772}   # Banjara Hills
            ],
            'density': 0.85,
            'name': 'hyderabad'
        },
        'pune': {
            'bounds': {'lat_min': 18.4, 'lat_max': 18.7, 'lon_min': 73.7, 'lon_max': 74.0},
            'centers': [
                {'lat': 18.5204, 'lon': 73.8567},  # Pune Central
                {'lat': 18.5593, 'lon': 73.7785},  # Hinjewadi IT Park
                {'lat': 18.6298, 'lon': 73.7997}   # Pimpri-Chinchwad
            ],
            'density': 0.75,
            'name': 'pune'
        },
        'chennai': {
            'bounds': {'lat_min': 12.8, 'lat_max': 13.3, 'lon_min': 80.1, 'lon_max': 80.4},
            'centers': [
                {'lat': 13.0827, 'lon': 80.2707},  # T. Nagar
                {'lat': 12.9716, 'lon': 80.2341},  # Anna Salai
                {'lat': 12.8230, 'lon': 80.0444}   # Tambaram
            ],
            'density': 0.8,
            'name': 'chennai'
        },
        'kolkata': {
            'bounds': {'lat_min': 22.4, 'lat_max': 22.8, 'lon_min': 88.2, 'lon_max': 88.5},
            'centers': [
                {'lat': 22.5726, 'lon': 88.3639},  # Park Street
                {'lat': 22.5958, 'lon': 88.2636},  # Salt Lake
                {'lat': 22.4707, 'lon': 88.3616}   # Jadavpur
            ],
            'density': 0.85,
            'name': 'kolkata'
        }
    }
    
    # Check which city the point belongs to
    for city_name, city_data in cities.items():
        bounds = city_data['bounds']
        if (bounds['lat_min'] <= point['lat'] <= bounds['lat_max'] and 
            bounds['lon_min'] <= point['lon'] <= bounds['lon_max']):
            return city_data
    
    # Default to generic Indian city if not recognized
    return {
        'centers': [point],  # Use the point itself as center
        'density': 0.6,
        'name': 'generic'
    }

def calculate_location_traffic_generic(point, center_distances, city_density):
    """Calculate base traffic level for any Indian city"""
    
    min_distance = min(center_distances)
    
    # Traffic based on distance from nearest center
    if min_distance < 2.0:
        return city_density  # Very high density near centers
    elif min_distance < 5.0:
        return city_density * 0.7  # High density
    elif min_distance < 10.0:
        return city_density * 0.5  # Medium density
    elif min_distance < 20.0:
        return city_density * 0.3  # Low density
    else:
        return 0.2  # Rural/highway areas

def get_time_traffic_multiplier(hour, city_name='generic'):
    """Get traffic multiplier based on time of day and city"""
    
    # City-specific rush hour patterns
    if city_name == 'mumbai':
        # Mumbai has more intense and longer rush hours
        if 7 <= hour <= 12:     # Extended morning rush
            return 1.7
        elif 17 <= hour <= 22:  # Extended evening rush
            return 1.8
        elif 12 <= hour <= 14:  # Lunch time
            return 1.3
        elif 23 <= hour or hour <= 6:  # Night time
            return 0.4
        else:
            return 1.1
    elif city_name == 'delhi':
        # Delhi has severe pollution and traffic issues
        if 8 <= hour <= 11:     # Morning rush
            return 1.6
        elif 17 <= hour <= 21:  # Evening rush
            return 1.7
        elif 12 <= hour <= 14:  # Lunch time
            return 1.2
        elif 22 <= hour or hour <= 6:  # Night time
            return 0.4
        else:
            return 1.0
    elif city_name == 'hyderabad':
        # Hyderabad IT hub with tech traffic patterns
        if 8 <= hour <= 11:     # Morning rush
            return 1.5
        elif 18 <= hour <= 21:  # Evening rush (IT timings)
            return 1.6
        elif 12 <= hour <= 14:  # Lunch time
            return 1.1
        elif 22 <= hour or hour <= 7:  # Night time
            return 0.5
        else:
            return 1.0
    elif city_name == 'pune':
        # Pune IT/automotive hub
        if 8 <= hour <= 10:     # Morning rush
            return 1.4
        elif 17 <= hour <= 20:  # Evening rush
            return 1.5
        elif 12 <= hour <= 14:  # Lunch time
            return 1.1
        elif 22 <= hour or hour <= 7:  # Night time
            return 0.6
        else:
            return 1.0
    elif city_name == 'chennai':
        # Chennai with hot climate affecting traffic
        if 7 <= hour <= 10:     # Morning rush (early due to heat)
            return 1.5
        elif 17 <= hour <= 20:  # Evening rush
            return 1.6
        elif 12 <= hour <= 14:  # Lunch time (hot afternoon)
            return 1.3
        elif 22 <= hour or hour <= 6:  # Night time
            return 0.4
        else:
            return 1.0
    elif city_name == 'kolkata':
        # Kolkata with traditional traffic patterns
        if 8 <= hour <= 11:     # Morning rush
            return 1.4
        elif 17 <= hour <= 20:  # Evening rush
            return 1.5
        elif 12 <= hour <= 14:  # Lunch time
            return 1.2
        elif 22 <= hour or hour <= 7:  # Night time
            return 0.5
        else:
            return 1.0
    else:
        # Default Indian city pattern (Bangalore-like)
        if 7 <= hour <= 11:     # Morning rush
            return 1.5
        elif 11 <= hour <= 17:  # Moderate traffic
            return 1.1
        elif 17 <= hour <= 21:  # Evening rush
            return 1.6
        elif 12 <= hour <= 14:  # Lunch time
            return 1.2
        elif 22 <= hour or hour <= 6:  # Night time
            return 0.5
        else:
            return 1.0

def classify_road_type(route_segment):
    """Determine road type based on route characteristics"""
    
    distance = haversine_distance(route_segment[0], route_segment[1])
    
    # Long segments likely highways
    if distance > 5.0:
        return "Highway"
    # Medium segments likely main roads
    elif distance > 1.0:
        return "City"
    # Short segments likely local roads
    else:
        return "Rural"

def get_route_traffic_analysis(route):
    """Analyze entire route for traffic patterns"""
    
    total_traffic = get_traffic_for_route(route)
    
    # Classify overall route type
    total_distance = sum([haversine_distance(route[i], route[i+1]) 
                         for i in range(len(route)-1)])
    
    if total_distance > 15:
        route_type = "Highway"
        speed_factor = 1.2  # Higher speeds on highways
    elif total_distance > 8:
        route_type = "Mixed"
        speed_factor = 1.0
    else:
        route_type = "City"
        speed_factor = 0.8  # Lower speeds in city
    
    return {
        'traffic_level': total_traffic,
        'route_type': route_type,
        'speed_factor': speed_factor,
        'estimated_speed': calculate_speed_from_traffic(total_traffic, speed_factor)
    }

def calculate_speed_from_traffic(traffic_level, speed_factor=1.0):
    """Calculate realistic speed based on traffic conditions"""
    
    # Base speeds (km/h)
    free_flow_speed = 60 * speed_factor
    heavy_traffic_speed = 20 * speed_factor
    
    # Linear interpolation based on traffic level
    speed = free_flow_speed - (traffic_level * (free_flow_speed - heavy_traffic_speed))
    
    return max(speed, 10)  # Minimum 10 km/h