import math

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