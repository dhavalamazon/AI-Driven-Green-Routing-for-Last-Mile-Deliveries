import random
from utils import haversine_distance

def create_route_alternatives(stops):
    """Create dramatically different route alternatives"""
    routes = []
    
    # Route 1: Shortest path (nearest neighbor)
    routes.append(nearest_neighbor_route(stops))
    
    # Route 2: Outer loop (longer but potentially more efficient)
    outer_route = create_outer_loop(stops)
    routes.append(outer_route)
    
    # Route 3: Inner zigzag (shorter but more turns)
    zigzag_route = create_zigzag_route(stops)
    routes.append(zigzag_route)
    
    # Route 4: Reverse order
    reverse_route = stops[::-1]
    routes.append(reverse_route)
    
    # Route 5-10: Random variations
    for _ in range(6):
        route = stops.copy()
        random.shuffle(route)
        routes.append(route)
    
    return routes

def nearest_neighbor_route(stops):
    """Standard nearest neighbor algorithm"""
    if len(stops) <= 1:
        return stops
    
    unvisited = stops.copy()
    route = [unvisited.pop(0)]
    
    while unvisited:
        last = route[-1]
        next_stop = min(unvisited, key=lambda s: haversine_distance(last, s))
        route.append(next_stop)
        unvisited.remove(next_stop)
    
    return route

def create_outer_loop(stops):
    """Create a route that goes around the perimeter first"""
    # Sort by distance from center
    center_lat = sum(s['lat'] for s in stops) / len(stops)
    center_lon = sum(s['lon'] for s in stops) / len(stops)
    center = {'lat': center_lat, 'lon': center_lon}
    
    # Sort by distance from center (outer stops first)
    sorted_stops = sorted(stops, key=lambda s: haversine_distance(center, s), reverse=True)
    return sorted_stops

def create_zigzag_route(stops):
    """Create a zigzag pattern"""
    # Sort by latitude, then alternate
    sorted_stops = sorted(stops, key=lambda s: s['lat'])
    zigzag = []
    
    for i, stop in enumerate(sorted_stops):
        if i % 2 == 0:
            zigzag.append(stop)
        else:
            zigzag.insert(0, stop)
    
    return zigzag

# Test the alternatives
if __name__ == "__main__":
    test_stops = [
        {'lat':37.7749,'lon':-122.4194},
        {'lat':37.7849,'lon':-122.4094},
        {'lat':37.7649,'lon':-122.4294},
        {'lat':37.7849,'lon':-122.4394},
        {'lat':37.7549,'lon':-122.4094},
        {'lat':37.7949,'lon':-122.4194},
        {'lat':37.7649,'lon':-122.4094},
        {'lat':37.7349,'lon':-122.4394}
    ]
    
    routes = create_route_alternatives(test_stops)
    
    print("Route alternatives:")
    for i, route in enumerate(routes[:4]):  # Show first 4
        total_dist = sum([haversine_distance(route[j], route[j+1]) for j in range(len(route)-1)])
        print(f"Route {i+1}: {total_dist:.2f}km")