import math
from datetime import datetime
from utils import haversine_distance



# Removed unused functions - now using tier-based detection

# Removed - now using tier-based detection in get_traffic_for_route

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



def calculate_speed_from_traffic(traffic_level, speed_factor=1.0):
    """Calculate realistic speed based on traffic conditions"""
    
    # Base speeds (km/h)
    free_flow_speed = 60 * speed_factor
    heavy_traffic_speed = 20 * speed_factor
    
    # Linear interpolation based on traffic level
    speed = free_flow_speed - (traffic_level * (free_flow_speed - heavy_traffic_speed))
    
    return max(speed, 10)  # Minimum 10 km/h