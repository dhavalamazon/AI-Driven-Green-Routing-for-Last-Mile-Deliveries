import random
from utils import haversine_distance

def nearest_neighbor_route(stops):
    unvisited = stops.copy()
    route = [unvisited.pop(0)]
    while unvisited:
        last = route[-1]
        next_stop = min(unvisited, key=lambda s: haversine_distance(last, s))
        route.append(next_stop)
        unvisited.remove(next_stop)
    return route

def random_routes(stops, n_routes=5):
    routes = []
    for _ in range(n_routes):
        r = stops.copy()
        random.shuffle(r)
        routes.append(r)
    return routes
