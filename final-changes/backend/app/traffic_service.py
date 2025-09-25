import math
from datetime import datetime
from utils import haversine_distance

def get_traffic_for_route(route_points, time_of_day=None):
    """Get realistic traffic conditions based on coordinates and time"""
    
    # San Francisco key areas with different traffic patterns
    downtown_sf = {'lat': 37.7749, 'lon': -122.4194}
    financial_district = {'lat': 37.7949, 'lon': -122.4094}
    highway_101 = {'lat': 37.7849, 'lon': -122.4394}
    
    # Current time if not specified
    if time_of_day is None:
        current_hour = datetime.now().hour
    else:
        current_hour = time_of_day
    
    traffic_levels = []
    
    for point in route_points:
        # Calculate distance from high-traffic areas
        dist_downtown = haversine_distance(point, downtown_sf)
        dist_financial = haversine_distance(point, financial_district)
        
        # Base traffic by location
        base_traffic = calculate_location_traffic(point, dist_downtown, dist_financial)
        
        # Time-based traffic multiplier
        time_multiplier = get_time_traffic_multiplier(current_hour)
        
        # Final traffic level (0.0 = free flow, 1.0 = heavy traffic)
        final_traffic = min(base_traffic * time_multiplier, 1.0)
        traffic_levels.append(final_traffic)
    
    # Return average traffic for the route
    return sum(traffic_levels) / len(traffic_levels)

def calculate_location_traffic(point, dist_downtown, dist_financial):
    """Calculate base traffic level based on location"""
    
    # Downtown core (high density)
    if dist_downtown < 1.0:
        return 0.8
    # Financial district
    elif dist_financial < 1.0:
        return 0.7
    # Urban areas
    elif dist_downtown < 3.0:
        return 0.6
    # Suburban areas
    elif dist_downtown < 8.0:
        return 0.4
    # Rural/highway areas
    else:
        return 0.2

def get_time_traffic_multiplier(hour):
    """Get traffic multiplier based on time of day"""
    
    # Rush hour patterns
    if 7 <= hour <= 9:      # Morning rush
        return 1.4
    elif 17 <= hour <= 19:  # Evening rush
        return 1.5
    elif 12 <= hour <= 14:  # Lunch time
        return 1.1
    elif 22 <= hour or hour <= 5:  # Night time
        return 0.6
    else:                   # Regular hours
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