from fastapi import FastAPI
from pydantic import BaseModel
from create_route_alternatives import create_route_alternatives
from ai_model import RouteScorer, load_model_with_scaler

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
    shortest_adjusted_score = 0
    
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
            print(f"  AI Prediction: {ai_prediction:.2f}g/unit → Scaled: {raw_co2_grams:.0f}g → AI+Physics: {co2_score:.2f}kg for {distance:.2f}km")
            print(f"  🤖 AI Base: {(raw_co2_grams/distance):.1f}g/km → Physics Corrected: {(co2_score*1000/distance):.1f}g/km")
        else:
            raise RuntimeError("AI model failed to load - this should not happen after auto-training")
        
        print(f"  CO2: {co2_score:.2f}kg (AI prediction for {req.vehicle_type}/{req.fuel_type} in {req.traffic_conditions} traffic)")
        
        # Apply vehicle-specific route penalties
        route_characteristics = analyze_route_characteristics(route, distance)
        vehicle_penalty = calculate_vehicle_route_penalty(req.vehicle_type, route_characteristics, req.traffic_conditions)
        adjusted_score = co2_score * (1 + vehicle_penalty)
        
        print(f"  📊 Route: {route_characteristics['type']}, Turns/km: {route_characteristics['turns_per_km']:.1f}, Avg segment: {route_characteristics['avg_segment_length']:.1f}km")
        print(f"  ⚖️  Penalty: {vehicle_penalty:.1%} → Adjusted: {adjusted_score:.2f}kg CO2")
        
        # Track shortest route
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_route = route
            shortest_co2 = co2_score
            shortest_route_mapping = route_indices.copy()
            shortest_adjusted_score = adjusted_score  # Track adjusted score too
        
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
    print(f"\n✅ Selected GREENEST: {' → '.join(map(str, selected_indices))} | {best_distance:.2f}km | {best_co2:.2f}kg base → {best_score:.2f}kg adjusted")
    print(f"📍 SHORTEST was: {' → '.join(map(str, shortest_route_mapping))} | {shortest_distance:.2f}km | {shortest_co2:.2f}kg base → {shortest_adjusted_score:.2f}kg adjusted")
    
    if best_distance != shortest_distance:
        adjusted_savings = shortest_adjusted_score - best_score
        extra_distance = best_distance - shortest_distance
        print(f"🌱 GREEN CHOICE: +{extra_distance:.1f}km distance but -{adjusted_savings:.2f}kg CO2 savings (after penalties)!\n")
    else:
        print(f"ℹ️ Same route chosen for both shortest and greenest\n")
    
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
        "predicted_co2": round(best_score, 2),  # Send adjusted CO2 as main value
        "total_distance": round(best_distance, 2),
        "shortest_route_comparison": {
            "route_mapping": shortest_route_mapping,
            "distance": round(shortest_distance, 2),
            "co2": round(shortest_adjusted_score, 2),  # Send adjusted CO2 for shortest route
            "co2_savings": round(shortest_adjusted_score - best_score, 2),  # Use adjusted values for savings
            "distance_difference": round(best_distance - shortest_distance, 2),
            "shortest_adjusted_co2": round(shortest_adjusted_score, 2),
            "greenest_adjusted_co2": round(best_score, 2),
            "adjusted_co2_savings": round(shortest_adjusted_score - best_score, 2),
            "is_different_route": best_distance != shortest_distance,
            "green_choice_message": f"+{round(best_distance - shortest_distance, 1)}km distance but -{round(shortest_adjusted_score - best_score, 2)}kg CO2 savings!" if best_distance != shortest_distance else None
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
    
    # START WITH AI PREDICTION as the base - TRUST THE AI MORE
    ai_base_per_km = raw_co2_grams / distance if distance > 0 else raw_co2_grams
    
    # Fuel type efficiency multipliers (apply to AI prediction)
    fuel_factors = {
        'Electric': 0.4,    # AI learned patterns, moderate electric adjustment
        'Hybrid': 0.8,      # AI learned patterns, moderate hybrid adjustment
        'Petrol': 1.0,      # Baseline - trust AI prediction completely
        'Diesel': 1.05      # AI learned patterns, very slight diesel adjustment
    }
    
    # Speed efficiency curve (apply to AI prediction) - MORE AGGRESSIVE
    if speed < 20:
        speed_factor = 1.8  # Heavy penalty for stop-and-go
    elif speed < 40:
        speed_factor = 1.4  # Significant penalty for city traffic
    elif speed <= 70:
        speed_factor = 1.0  # AI learned optimal range, trust it
    elif speed <= 90:
        speed_factor = 1.1  # Slight highway inefficiency
    else:
        speed_factor = 1.3  # High-speed inefficiency
    
    # Engine size factor (apply to AI prediction) - MORE SENSITIVE
    engine_factor = 0.8 + (engine_size * 0.1)  # More engine size impact
    
    # Apply corrections to AI prediction
    fuel_multiplier = fuel_factors.get(fuel_type, 1.0)
    corrected_co2_per_km = ai_base_per_km * fuel_multiplier * engine_factor * speed_factor
    total_co2_grams = corrected_co2_per_km * distance
    
    # REMOVE ARTIFICIAL BOUNDS - Trust AI + corrections
    # Only apply very loose safety bounds
    min_co2_per_km = 20   # Very low minimum
    max_co2_per_km = 1200 # Very high maximum
    
    final_co2_per_km = max(min_co2_per_km, min(max_co2_per_km, corrected_co2_per_km))
    final_total_co2_grams = final_co2_per_km * distance
    
    # Convert to kg and apply Indian calibration multiplier
    # Indian average: 121.3g CO2/km, our model predicts ~40g CO2/km
    # Calibration factor: 3.0x to match Indian driving conditions
    indian_calibration_factor = 3.0
    
    return (final_total_co2_grams / 1000) * indian_calibration_factor

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
        'total_segments': len(segments),
        'total_distance': total_distance
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
        'Free flow': {'highway': 85, 'suburban': 55, 'dense_urban': 45, 'rural': 65, 'mixed': 55},
        'Moderate': {'highway': 70, 'suburban': 40, 'dense_urban': 30, 'rural': 50, 'mixed': 40},
        'Heavy': {'highway': 50, 'suburban': 25, 'dense_urban': 18, 'rural': 40, 'mixed': 30}
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
    
    # TRAFFIC-DEPENDENT PENALTIES - Only apply route penalties in heavy traffic
    if traffic_conditions == 'Heavy':
        # In heavy traffic, route type matters A LOT
        route_type = route_characteristics.get('type', 'mixed')
        if route_type == 'rural':
            penalty += 0.50  # Rural routes suffer in heavy traffic (stop-and-go)
        elif route_type == 'mixed':
            penalty += 0.45  # Mixed routes are inefficient in traffic
        elif route_type == 'suburban':
            penalty += 0.35  # Suburban routes have traffic lights
        elif route_type == 'dense_urban':
            penalty += 0.60  # Dense urban is worst in heavy traffic
        elif route_type == 'highway':
            penalty += 0.10  # Highways maintain flow even in traffic
        
        # Turn frequency penalties (only matter in heavy traffic)
        turns_per_km = route_characteristics.get('turns_per_km', 0)
        if turns_per_km > 0.5:
            penalty += 0.25  # High turn frequency penalty
        elif turns_per_km > 0.2:
            penalty += 0.15  # Moderate turn penalty
        
        # Segment length penalties (only matter in heavy traffic)
        avg_segment = route_characteristics.get('avg_segment_length', 0)
        if avg_segment < 5:  # Short segments = city driving with lights
            penalty += 0.20
        elif avg_segment < 8:  # Medium segments
            penalty += 0.10
            
    elif traffic_conditions == 'Moderate':
        # In moderate traffic, route type matters less
        route_type = route_characteristics.get('type', 'mixed')
        if route_type == 'dense_urban':
            penalty += 0.15  # Only dense urban gets penalty
        elif route_type == 'rural':
            penalty += 0.10  # Small penalty for rural
            
    # In 'Free flow' traffic, NO route penalties - shortest = greenest
    
    # Base traffic penalties (apply regardless of route)
    if traffic_conditions == 'Heavy':
        penalty += 0.20  # Base heavy traffic penalty
    elif traffic_conditions == 'Moderate':
        penalty += 0.05  # Small base moderate traffic penalty
    
    # Vehicle-specific multipliers
    if vehicle_type == 'Truck':
        penalty *= 1.3  # Trucks suffer more from all penalties
    elif vehicle_type == 'Bus':
        penalty *= 1.1  # Buses suffer slightly more
    
    return penalty
