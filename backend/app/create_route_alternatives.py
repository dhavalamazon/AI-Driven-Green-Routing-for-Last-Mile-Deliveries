import random
from utils import haversine_distance

def create_route_alternatives(stops):
    """Create optimized route alternatives using proper TSP techniques"""
    routes = []
    
    # Route 1: Nearest neighbor (greedy)
    routes.append(nearest_neighbor_route(stops))
    
    # Route 2: 2-opt improvement on nearest neighbor
    nn_route = nearest_neighbor_route(stops)
    routes.append(two_opt_improve(nn_route))
    
    # Route 3: Convex hull + insertion
    routes.append(convex_hull_route(stops))
    
    # Route 4: Farthest insertion
    routes.append(farthest_insertion_route(stops))
    
    # Route 5: Nearest insertion
    routes.append(nearest_insertion_route(stops))
    
    # Route 6: Highway bypass (Electronic City to Hebbal avoiding city)
    routes.append(create_highway_bypass(stops))
    
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

def two_opt_improve(route):
    """Improve route using 2-opt swaps"""
    best_route = route.copy()
    best_distance = calculate_total_distance(best_route)
    improved = True
    
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1: continue
                new_route = route.copy()
                new_route[i:j] = route[i:j][::-1]
                new_distance = calculate_total_distance(new_route)
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    route = new_route
                    improved = True
    return best_route

def calculate_total_distance(route):
    """Calculate total distance of a route"""
    if len(route) < 2:
        return 0
    return sum(haversine_distance(route[i], route[i+1]) for i in range(len(route)-1))

def convex_hull_route(stops):
    """Create route using convex hull approach"""
    if len(stops) <= 3:
        return stops
    
    # Find convex hull points
    hull = convex_hull(stops)
    interior = [s for s in stops if s not in hull]
    
    # Insert interior points optimally
    route = hull.copy()
    for point in interior:
        best_pos = 0
        best_increase = float('inf')
        for i in range(len(route)):
            # Calculate increase in distance if inserted at position i
            if i == len(route) - 1:
                increase = (haversine_distance(route[i], point) + 
                           haversine_distance(point, route[0]) - 
                           haversine_distance(route[i], route[0]))
            else:
                increase = (haversine_distance(route[i], point) + 
                           haversine_distance(point, route[i+1]) - 
                           haversine_distance(route[i], route[i+1]))
            if increase < best_increase:
                best_increase = increase
                best_pos = i + 1
        route.insert(best_pos, point)
    
    return route

def convex_hull(points):
    """Find convex hull using Graham scan"""
    def cross(o, a, b):
        return (a['lat'] - o['lat']) * (b['lon'] - o['lon']) - (a['lon'] - o['lon']) * (b['lat'] - o['lat'])
    
    points = sorted(set([(p['lat'], p['lon']) for p in points]))
    if len(points) <= 1:
        return [{'lat': p[0], 'lon': p[1]} for p in points]
    
    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross({'lat': lower[-2][0], 'lon': lower[-2][1]}, 
                                       {'lat': lower[-1][0], 'lon': lower[-1][1]}, 
                                       {'lat': p[0], 'lon': p[1]}) <= 0:
            lower.pop()
        lower.append(p)
    
    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross({'lat': upper[-2][0], 'lon': upper[-2][1]}, 
                                       {'lat': upper[-1][0], 'lon': upper[-1][1]}, 
                                       {'lat': p[0], 'lon': p[1]}) <= 0:
            upper.pop()
        upper.append(p)
    
    return [{'lat': p[0], 'lon': p[1]} for p in lower[:-1] + upper[:-1]]

def farthest_insertion_route(stops):
    """Farthest insertion TSP heuristic"""
    if len(stops) <= 2:
        return stops
    
    # Start with two farthest points
    max_dist = 0
    start_pair = (0, 1)
    for i in range(len(stops)):
        for j in range(i+1, len(stops)):
            dist = haversine_distance(stops[i], stops[j])
            if dist > max_dist:
                max_dist = dist
                start_pair = (i, j)
    
    route = [stops[start_pair[0]], stops[start_pair[1]]]
    remaining = [s for i, s in enumerate(stops) if i not in start_pair]
    
    while remaining:
        # Find farthest point from current route
        farthest_point = None
        max_min_dist = 0
        for point in remaining:
            min_dist = min(haversine_distance(point, r) for r in route)
            if min_dist > max_min_dist:
                max_min_dist = min_dist
                farthest_point = point
        
        # Insert at best position
        best_pos = 0
        best_increase = float('inf')
        for i in range(len(route)):
            next_i = (i + 1) % len(route)
            increase = (haversine_distance(route[i], farthest_point) + 
                       haversine_distance(farthest_point, route[next_i]) - 
                       haversine_distance(route[i], route[next_i]))
            if increase < best_increase:
                best_increase = increase
                best_pos = i + 1
        
        route.insert(best_pos, farthest_point)
        remaining.remove(farthest_point)
    
    return route

def nearest_insertion_route(stops):
    """Nearest insertion TSP heuristic"""
    if len(stops) <= 2:
        return stops
    
    # Start with first point
    route = [stops[0]]
    remaining = stops[1:]
    
    while remaining:
        # Find nearest point to current route
        nearest_point = None
        min_dist = float('inf')
        for point in remaining:
            dist = min(haversine_distance(point, r) for r in route)
            if dist < min_dist:
                min_dist = dist
                nearest_point = point
        
        # Insert at best position
        if len(route) == 1:
            route.append(nearest_point)
        else:
            best_pos = 0
            best_increase = float('inf')
            for i in range(len(route)):
                next_i = (i + 1) % len(route)
                increase = (haversine_distance(route[i], nearest_point) + 
                           haversine_distance(nearest_point, route[next_i]) - 
                           haversine_distance(route[i], route[next_i]))
                if increase < best_increase:
                    best_increase = increase
                    best_pos = i + 1
            
            route.insert(best_pos, nearest_point)
        
        remaining.remove(nearest_point)
    
    return route

def create_highway_bypass(stops):
    """Create highway route: Electronic City → Hebbal → others (avoiding city center)"""
    electronic_city = {'lat': 12.8456, 'lon': 77.6603}
    hebbal = {'lat': 13.0358, 'lon': 77.5970}
    
    # Find Electronic City and Hebbal in stops
    ec_stop = None
    hebbal_stop = None
    other_stops = []
    
    for stop in stops:
        if abs(stop['lat'] - electronic_city['lat']) < 0.01:
            ec_stop = stop
        elif abs(stop['lat'] - hebbal['lat']) < 0.01:
            hebbal_stop = stop
        else:
            other_stops.append(stop)
    
    # Create highway route: EC → Hebbal → others
    if ec_stop and hebbal_stop:
        route = [ec_stop, hebbal_stop] + other_stops
        return route
    
    # Fallback to original order if no highway endpoints
    return stops

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