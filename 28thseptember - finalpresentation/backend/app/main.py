from fastapi import FastAPI
from pydantic import BaseModel
from create_route_alternatives import create_route_alternatives
from ai_model import RouteScorer, route_features, load_model_with_scaler
from traffic_service import get_route_traffic_analysis
import torch
import random
import hashlib
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Green Routing API", version="1.0.0")

# Allow requests from your frontend
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load trained model and scaler
print("🚀 Starting AI Green Routing API...")
model, scaler = load_model_with_scaler()

# If model not available, train it
if model is None or scaler is None:
    print("🤖 AI model not found. Training new model...")
    from train_model import train_model
    train_model()
    model, scaler = load_model_with_scaler()
    
    if model is None or scaler is None:
        raise RuntimeError("Failed to train AI model. Check if dataset exists.")
    
    print("✅ AI model trained and loaded successfully!")

class OptimizeRequest(BaseModel):
    stops: list
    vehicle_type: str = "Car"  # Car, Truck, Bus, Motorcycle
    fuel_type: str = "Petrol"  # Electric, Hybrid, Petrol, Diesel
    traffic_conditions: str = "Moderate"  # Free flow, Moderate, Heavy

@app.post("/classify-area")
def classify_area(locations: list):
    """Classify area type for traffic detection - consistent with backend route analysis"""
    if not locations or len(locations) < 2:
        return {"area_type": "mixed", "traffic_multiplier": 1.0}
    
    # Convert to route format
    route = [{'lat': loc['lat'], 'lon': loc['lon']} for loc in locations]
    
    # Calculate total distance
    from utils import haversine_distance
    total_distance = sum([haversine_distance(route[i], route[i+1]) for i in range(len(route)-1)])
    
    # Use same backend classification logic
    route_characteristics = analyze_route_characteristics(route, total_distance)
    area_type = route_characteristics['type']
    
    # Detect city for time-based traffic
    from traffic_service import detect_city
    city_info = detect_city(route[0])
    
    return {
        "area_type": area_type,
        "city": city_info['name'],
        "characteristics": {
            "avg_segment_length": round(route_characteristics['avg_segment_length'], 2),
            "coordinate_spread": round(route_characteristics['coordinate_spread'], 4),
            "turns_per_km": round(route_characteristics['turns_per_km'], 2)
        }
    }

@app.post("/get-traffic-level")
def get_traffic_level(data: dict):
    """Get traffic level based on locations, time, and area type"""
    locations = data.get('locations', [])
    hour = data.get('hour', 12)
    
    if not locations:
        return {"traffic_level": "Moderate"}
    
    # Use backend traffic detection
    from traffic_service import detect_city, get_time_traffic_multiplier
    
    route = [{'lat': loc['lat'], 'lon': loc['lon']} for loc in locations]
    city_info = detect_city(route[0])
    
    # Get time-based multiplier
    time_multiplier = get_time_traffic_multiplier(hour, city_info['name'])
    
    # Convert multiplier to traffic level
    if time_multiplier >= 1.5:
        traffic_level = "Heavy"
    elif time_multiplier >= 1.1:
        traffic_level = "Moderate"
    else:
        traffic_level = "Free flow"
    
    return {
        "traffic_level": traffic_level,
        "city": city_info['name'],
        "time_multiplier": time_multiplier
    }

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # Remove deterministic seeding to allow route variation
    
    # Generate dramatically different route alternatives
    candidates = create_route_alternatives(req.stops)
    
    # Find the route with lowest adjusted score for these specific parameters
    best_route = None
    best_score = float("inf")
    best_distance = 0
    best_co2 = 0
    
    # Track shortest route for comparison
    shortest_route = None
    shortest_distance = float("inf")
    shortest_co2 = 0
    shortest_route_mapping = []
    
    print(f"\n🔍 Evaluating {len(candidates)} route alternatives...")
    
    for i, route in enumerate(candidates):
        # Calculate distance using road-aware routing
        from utils import calculate_route_distance
        distance = calculate_route_distance(route)
        
        # Create route mapping for debugging
        route_indices = []
        for stop in route:
            for j, original_stop in enumerate(req.stops):
                if stop['lat'] == original_stop['lat'] and stop['lon'] == original_stop['lon']:
                    route_indices.append(j + 1)
                    break
        
        print(f"Route {i+1}: {' → '.join(map(str, route_indices))} | Distance: {distance:.2f}km")
        
        # Use AI model for CO2 prediction
        if model and scaler:
            # Derive missing features from user inputs and route analysis
            route_analysis = analyze_route_characteristics(route, distance)
            
            # Derive speed based on traffic conditions and route type
            speed = derive_speed(req.traffic_conditions, route_analysis['type'])
            
            # Derive engine size based on vehicle type
            engine_size = derive_engine_size(req.vehicle_type)
            
            # Encode categorical variables for AI model
            vehicle_encoded = encode_vehicle_type(req.vehicle_type)
            fuel_encoded = encode_fuel_type(req.fuel_type)
            traffic_encoded = encode_traffic_conditions(req.traffic_conditions)
            
            # Prepare enhanced features for AI model
            speed_squared = speed ** 2
            engine_vehicle = engine_size * vehicle_encoded
            speed_traffic = speed * traffic_encoded
            
            features = [speed, engine_size, traffic_encoded, vehicle_encoded, fuel_encoded, 
                       speed_squared, engine_vehicle, speed_traffic]
            
            # Scale features and predict using AI model
            import torch
            import numpy as np
            features_scaled = scaler.transform([features])
            features_tensor = torch.FloatTensor(features_scaled)
            
            with torch.no_grad():
                model.eval()
                ai_prediction = model(features_tensor).item()
            
            # AI predicts grams per unit, scale by distance
            raw_co2_grams = ai_prediction * (distance / 10)  # Scale prediction by distance
            
            # Apply realistic corrections based on vehicle type, fuel, etc.
            co2_score = apply_realistic_corrections(raw_co2_grams, req.vehicle_type, req.fuel_type, engine_size, speed, distance)
            
            print(f"  AI Features: Speed={speed:.1f}km/h, Engine={engine_size:.1f}L, Traffic={traffic_encoded}, Vehicle={vehicle_encoded}, Fuel={fuel_encoded}")
            print(f"  AI Prediction: {ai_prediction:.2f}g → Raw: {raw_co2_grams:.0f}g → Corrected: {co2_score:.2f}kg for {distance:.2f}km")
        else:
            raise RuntimeError("AI model failed to load - this should not happen after auto-training")
        
        print(f"  CO2: {co2_score:.2f}kg (AI prediction for {req.vehicle_type}/{req.fuel_type} in {req.traffic_conditions} traffic)")
        
        # Apply vehicle-specific route penalties
        route_characteristics = analyze_route_characteristics(route, distance)
        vehicle_penalty = calculate_vehicle_route_penalty(req.vehicle_type, route_characteristics, req.traffic_conditions)
        adjusted_score = co2_score * (1 + vehicle_penalty)
        
        # Track shortest route
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_route = route
            shortest_co2 = co2_score
            shortest_route_mapping = route_indices.copy()
        
        if adjusted_score < best_score:
            print(f"  ⭐ NEW BEST: Route {i+1} with {adjusted_score:.2f}kg CO2")
            best_score = adjusted_score
            best_route = route
            best_distance = distance
            best_co2 = co2_score
    
    # Debug: Show selected route
    selected_indices = []
    for stop in best_route:
        for i, original_stop in enumerate(req.stops):
            if stop['lat'] == original_stop['lat'] and stop['lon'] == original_stop['lon']:
                selected_indices.append(i + 1)
                break
    print(f"\n✅ Selected: {' → '.join(map(str, selected_indices))} | {best_distance:.2f}km | {best_co2:.2f}kg CO2\n")
    
    # Get default values for response
    default_engines = {'Car': 2.0, 'Truck': 4.5, 'Bus': 5.0, 'Motorcycle': 1.5}
    default_speeds = {'Free flow': 70, 'Moderate': 45, 'Heavy': 25}
    
    # Create mapping of optimized route to original input indices
    route_mapping = []
    for stop in best_route:
        for i, original_stop in enumerate(req.stops):
            if stop['lat'] == original_stop['lat'] and stop['lon'] == original_stop['lon']:
                route_mapping.append(i + 1)  # 1-based indexing
                break
    
    # Generate road waypoints for map visualization
    from utils import generate_road_waypoints
    route_waypoints = []
    for i in range(len(best_route) - 1):
        segment_waypoints = generate_road_waypoints(best_route[i], best_route[i + 1])
        if i == 0:
            route_waypoints.extend(segment_waypoints)
        else:
            route_waypoints.extend(segment_waypoints[1:])  # Skip duplicate start point
    
    return {
        "best_route": best_route, 
        "route_waypoints": route_waypoints,  # For map visualization
        "route_mapping": route_mapping,
        "predicted_co2": round(best_co2, 2),
        "total_distance": round(best_distance, 2),
        "shortest_route_comparison": {
            "route_mapping": shortest_route_mapping,
            "distance": round(shortest_distance, 2),
            "co2": round(shortest_co2, 2),
            "co2_savings": round(shortest_co2 - best_co2, 2),
            "distance_difference": round(best_distance - shortest_distance, 2)
        },
        "input_features": {
            "vehicle_type": req.vehicle_type,
            "fuel_type": req.fuel_type,
            "traffic_conditions": req.traffic_conditions,
            "derived_engine_size": default_engines.get(req.vehicle_type, 2.0),
            "derived_speed": default_speeds.get(req.traffic_conditions, 45)
        }
    }

def apply_realistic_corrections(raw_co2_grams, vehicle_type, fuel_type, engine_size, speed, distance):
    """Apply realistic physics-based corrections to AI predictions"""
    
    # Base emissions factors (g CO2/km) for different vehicle types
    base_emissions = {
        'Car': 140,         # Typical car: ~140g CO2/km
        'Motorcycle': 85,   # Smaller, lighter: ~85g CO2/km
        'Truck': 350,       # Heavy truck: ~350g CO2/km
        'Bus': 500          # Large bus: ~500g CO2/km
    }
    
    # Fuel type efficiency multipliers
    fuel_factors = {
        'Electric': 0.2,    # Very low emissions (electricity generation)
        'Hybrid': 0.6,      # Moderate emissions
        'Petrol': 1.0,      # Baseline
        'Diesel': 1.15      # Slightly higher but more efficient
    }
    
    # Calculate realistic CO2 based on vehicle type and fuel
    base_co2_per_km = base_emissions.get(vehicle_type, 150)
    fuel_multiplier = fuel_factors.get(fuel_type, 1.0)
    
    # Engine size factor (larger engines = more fuel consumption)
    engine_factor = 0.7 + (engine_size * 0.15)  # Scale with engine size
    
    # Speed efficiency curve (most efficient around 50-60 km/h)
    if speed < 20:
        speed_factor = 1.4  # Very inefficient at very low speeds
    elif speed < 40:
        speed_factor = 1.2  # Inefficient in stop-and-go traffic
    elif speed <= 70:
        speed_factor = 1.0  # Optimal efficiency range
    elif speed <= 90:
        speed_factor = 1.1  # Slightly less efficient
    else:
        speed_factor = 1.3  # Much less efficient at high speeds
    
    # Calculate realistic CO2 emissions in grams
    co2_per_km = base_co2_per_km * fuel_multiplier * engine_factor * speed_factor
    total_co2_grams = co2_per_km * distance
    
    # Convert to kg and return
    return total_co2_grams / 1000

def analyze_route_characteristics(route, total_distance):
    """Generic route analysis that works for any city worldwide"""
    if len(route) < 2:
        return {'type': 'unknown', 'segments': [], 'density': 0}
    
    from utils import road_aware_distance, haversine_distance
    import math
    
    # Calculate segment characteristics
    segments = []
    total_turns = 0
    
    for i in range(len(route) - 1):
        segment_distance = haversine_distance(route[i], route[i+1])
        segments.append(segment_distance)
        
        # Calculate turn angles (simplified)
        if i > 0:
            # Rough turn detection based on coordinate changes
            prev_lat_diff = route[i]['lat'] - route[i-1]['lat']
            prev_lon_diff = route[i]['lon'] - route[i-1]['lon']
            curr_lat_diff = route[i+1]['lat'] - route[i]['lat']
            curr_lon_diff = route[i+1]['lon'] - route[i]['lon']
            
            # If direction changes significantly, it's a turn
            if abs(prev_lat_diff - curr_lat_diff) > 0.01 or abs(prev_lon_diff - curr_lon_diff) > 0.01:
                total_turns += 1
    
    # Calculate metrics
    avg_segment_length = sum(segments) / len(segments) if segments else 0
    max_segment_length = max(segments) if segments else 0
    coordinate_spread = calculate_coordinate_spread(route)
    turns_per_km = total_turns / total_distance if total_distance > 0 else 0
    
    # Determine route type based on characteristics
    route_type = classify_route_type(avg_segment_length, max_segment_length, 
                                   coordinate_spread, turns_per_km, total_distance)
    
    return {
        'type': route_type,
        'avg_segment_length': avg_segment_length,
        'max_segment_length': max_segment_length,
        'coordinate_spread': coordinate_spread,
        'turns_per_km': turns_per_km,
        'total_segments': len(segments)
    }

def calculate_coordinate_spread(route):
    """Calculate how spread out the coordinates are (density indicator)"""
    if len(route) < 2:
        return 0
    
    lats = [stop['lat'] for stop in route]
    lons = [stop['lon'] for stop in route]
    
    lat_range = max(lats) - min(lats)
    lon_range = max(lons) - min(lons)
    
    # Combined spread (larger = more spread out = less dense)
    return (lat_range + lon_range) / len(route)

def classify_route_type(avg_segment, max_segment, spread, turns_per_km, total_distance):
    """Classify route type based on characteristics"""
    
    # Highway characteristics: Long segments, low turn rate, high spread
    if (max_segment > 15 and turns_per_km < 0.5 and total_distance > 20):
        return 'highway'
    
    # Dense urban: Short segments, high turn rate, low spread
    elif (avg_segment < 3 and turns_per_km > 2 and spread < 0.02):
        return 'dense_urban'
    
    # Suburban: Medium segments, moderate turns
    elif (avg_segment < 8 and turns_per_km < 2 and spread < 0.05):
        return 'suburban'
    
    # Rural: Long segments, low density
    elif (avg_segment > 5 and spread > 0.05):
        return 'rural'
    
    # Default
    else:
        return 'mixed'

def derive_speed(traffic_conditions, route_type):
    """Derive realistic speed based on traffic and route type"""
    base_speeds = {
        'Free flow': {'highway': 80, 'suburban': 50, 'dense_urban': 40, 'rural': 60, 'mixed': 50},
        'Moderate': {'highway': 65, 'suburban': 35, 'dense_urban': 25, 'rural': 45, 'mixed': 35},
        'Heavy': {'highway': 45, 'suburban': 20, 'dense_urban': 15, 'rural': 35, 'mixed': 25}
    }
    return base_speeds.get(traffic_conditions, {}).get(route_type, 35)

def derive_engine_size(vehicle_type):
    """Derive typical engine size based on vehicle type"""
    engine_sizes = {
        'Car': 2.0,
        'Motorcycle': 0.8,
        'Truck': 4.5,
        'Bus': 6.0
    }
    return engine_sizes.get(vehicle_type, 2.0)

def encode_vehicle_type(vehicle_type):
    """Encode vehicle type for AI model (matches training data)"""
    mapping = {'Car': 0, 'Truck': 1, 'Bus': 2, 'Motorcycle': 3}
    return mapping.get(vehicle_type, 0)

def encode_fuel_type(fuel_type):
    """Encode fuel type for AI model (matches training data)"""
    mapping = {'Electric': 0, 'Hybrid': 1, 'Petrol': 2, 'Diesel': 3}
    return mapping.get(fuel_type, 2)

def encode_traffic_conditions(traffic_conditions):
    """Encode traffic conditions for AI model (matches training data)"""
    mapping = {'Free flow': 0, 'Moderate': 1, 'Heavy': 2}
    return mapping.get(traffic_conditions, 1)

def calculate_vehicle_route_penalty(vehicle_type, route_characteristics, traffic_conditions):
    """Calculate vehicle-specific penalties for route characteristics"""
    penalty = 0.0
    
    # Truck penalties for dense urban routes
    if vehicle_type == 'Truck':
        # Heavy penalty for dense urban routes (many turns, short segments)
        if route_characteristics['type'] == 'dense_urban':
            penalty += 0.25  # 25% CO2 penalty
        
        # Penalty for high turn frequency (trucks hate stop-and-go)
        if route_characteristics['turns_per_km'] > 1.5:
            penalty += 0.15  # 15% penalty for frequent turns
            
        # Extra penalty in heavy traffic
        if traffic_conditions == 'Heavy':
            penalty += 0.20  # 20% penalty for heavy traffic
            
        # Penalty for short segments (indicates city driving)
        if route_characteristics['avg_segment_length'] < 3:
            penalty += 0.10  # 10% penalty for short segments
    
    # Car penalties (less severe)
    elif vehicle_type == 'Car':
        # Cars are more efficient in city driving, small penalty for very long routes
        if route_characteristics['type'] == 'highway' and route_characteristics['avg_segment_length'] > 15:
            penalty += 0.05  # Small penalty for very long highway segments
    
    return penalty
