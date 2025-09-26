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
    
    print(f"\n🔍 Evaluating {len(candidates)} route alternatives...")
    
    for i, route in enumerate(candidates):
        # Calculate distance first
        from utils import haversine_distance
        distance = sum([haversine_distance(route[j], route[j+1]) for j in range(len(route)-1)])
        
        # Create route mapping for debugging
        route_indices = []
        for stop in route:
            for j, original_stop in enumerate(req.stops):
                if stop['lat'] == original_stop['lat'] and stop['lon'] == original_stop['lon']:
                    route_indices.append(j + 1)
                    break
        
        print(f"Route {i+1}: {' → '.join(map(str, route_indices))} | Distance: {distance:.2f}km")
        
        # Use distance as primary factor for CO2 calculation
        # CO2 is roughly proportional to distance
        base_co2_per_km = {
            'Car': 0.15,      # 150g CO2/km
            'Motorcycle': 0.10, # 100g CO2/km  
            'Truck': 0.40,    # 400g CO2/km
            'Bus': 0.55       # 550g CO2/km
        }
        
        fuel_multipliers = {
            'Electric': 0.3,
            'Hybrid': 0.7, 
            'Petrol': 1.0,
            'Diesel': 1.1
        }
        
        # Calculate CO2 based on distance and vehicle characteristics
        co2_per_km = base_co2_per_km.get(req.vehicle_type, 0.15)
        fuel_factor = fuel_multipliers.get(req.fuel_type, 1.0)
        
        # Traffic impact on efficiency
        traffic_multipliers = {
            'Free flow': 0.9,   # More efficient at highway speeds
            'Moderate': 1.0,    # Baseline
            'Heavy': 1.3        # Stop-and-go increases consumption
        }
        
        traffic_factor = traffic_multipliers.get(req.traffic_conditions, 1.0)
        
        # Generic route analysis (works for any city worldwide)
        route_analysis = analyze_route_characteristics(route, distance)
        congestion_penalty = 1.0
        
        # Apply efficiency factors based on route type
        if route_analysis['type'] == 'highway' and req.vehicle_type in ['Truck', 'Bus']:
            congestion_penalty *= 0.2  # Highway efficiency for large vehicles
        elif route_analysis['type'] == 'dense_urban' and req.traffic_conditions == 'Heavy':
            congestion_penalty *= 2.2  # Dense city congestion penalty
        elif route_analysis['type'] == 'suburban' and req.traffic_conditions == 'Heavy':
            congestion_penalty *= 1.6  # Moderate suburban congestion
        elif route_analysis['type'] == 'rural' and req.vehicle_type in ['Truck', 'Bus']:
            congestion_penalty *= 0.8  # Rural roads good for large vehicles
        
        co2_score = distance * co2_per_km * fuel_factor * traffic_factor * congestion_penalty
        
        print(f"  CO2: {co2_score:.2f}kg ({co2_per_km:.2f}/km × {fuel_factor} fuel × {traffic_factor} traffic × {congestion_penalty:.2f} route)")
        
        # Use CO2 score directly (distance-based)
        adjusted_score = co2_score
        
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
    
    return {
        "best_route": best_route, 
        "route_mapping": route_mapping,
        "predicted_co2": round(best_co2, 2),
        "total_distance": round(best_distance, 2),
        "input_features": {
            "vehicle_type": req.vehicle_type,
            "fuel_type": req.fuel_type,
            "traffic_conditions": req.traffic_conditions,
            "derived_engine_size": default_engines.get(req.vehicle_type, 2.0),
            "derived_speed": default_speeds.get(req.traffic_conditions, 45)
        }
    }

def apply_realistic_corrections(raw_co2, vehicle_type, fuel_type, engine_size, speed):
    """Apply realistic physics-based corrections to AI predictions"""
    corrected_co2 = raw_co2
    
    # Vehicle size multipliers (larger vehicles = more emissions)
    vehicle_multipliers = {
        'Car': 1.0,
        'Motorcycle': 0.6,  # Smaller, lighter
        'Truck': 2.5,       # Much larger, heavier
        'Bus': 3.0          # Largest, heaviest
    }
    
    # Fuel type efficiency factors
    fuel_factors = {
        'Electric': 0.3,    # Very low emissions
        'Hybrid': 0.7,      # Moderate emissions
        'Petrol': 1.0,      # Baseline
        'Diesel': 1.1       # Slightly higher
    }
    
    # Apply corrections
    corrected_co2 *= vehicle_multipliers.get(vehicle_type, 1.0)
    corrected_co2 *= fuel_factors.get(fuel_type, 1.0)
    
    # Engine size factor (larger engines = more fuel)
    corrected_co2 *= (0.8 + (engine_size * 0.1))  # Scale with engine size
    
    # Speed efficiency (very low or very high speeds are less efficient)
    if speed < 30 or speed > 80:
        corrected_co2 *= 1.2  # 20% penalty for inefficient speeds
    
    # Ensure minimum realistic values (kg CO2 for ~14km delivery route)
    min_co2 = {
        'Car': 2.0,        # ~140g/km × 14km = 2kg
        'Motorcycle': 1.5,  # ~100g/km × 14km = 1.4kg  
        'Truck': 6.0,       # ~400g/km × 14km = 5.6kg
        'Bus': 8.0          # ~550g/km × 14km = 7.7kg
    }
    
    return max(corrected_co2, min_co2.get(vehicle_type, 2.0))

def analyze_route_characteristics(route, total_distance):
    """Generic route analysis that works for any city worldwide"""
    if len(route) < 2:
        return {'type': 'unknown', 'segments': [], 'density': 0}
    
    from utils import haversine_distance
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
