from fastapi import FastAPI
from pydantic import BaseModel
from create_route_alternatives import create_route_alternatives
from ai_model import RouteScorer, route_features
import torch
import random
import hashlib
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Allow requests from your frontend
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Next.js dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # frontend URL
    allow_credentials=True,
    allow_methods=["*"],       # allow all HTTP methods
    allow_headers=["*"],
)
model = RouteScorer()
model.load_state_dict(torch.load("route_scorer.pt", weights_only=True))
model.eval()

class OptimizeRequest(BaseModel):
    stops: list
    vehicle_type: str = "ICE"
    traffic_level: float = 0.5

@app.post("/optimize")
def optimize(req: OptimizeRequest):
    # Create deterministic seed from ALL parameters for consistent results
    input_str = f"{req.stops}{req.vehicle_type}{req.traffic_level}"
    seed = int(hashlib.md5(input_str.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Generate dramatically different route alternatives
    candidates = create_route_alternatives(req.stops)
    
    # Find the route with lowest adjusted score for these specific parameters
    best_route = None
    best_score = float("inf")
    best_distance = 0
    best_co2 = 0
    
    for route in candidates:
        feats = route_features(route, req.vehicle_type, req.traffic_level)
        feats_tensor = torch.tensor(feats, dtype=torch.float32)
        co2_score = model(feats_tensor).item()
        distance = feats[0]
        
        # Simulate different route types: some routes are "highway-style" (longer but efficient in low traffic)
        # vs "city-street" routes (shorter but inefficient in high traffic)
        route_efficiency_factor = 1.0
        
        # Simulate realistic traffic behavior
        if distance > 15:  # Longer routes = "highway/bypass style"
            if req.traffic_level > 0.7:
                # In HIGH traffic: longer routes AVOID congested city streets
                route_efficiency_factor = 0.7   # 30% MORE efficient (avoid traffic jams)
            else:
                # In LOW traffic: longer routes are wasteful
                route_efficiency_factor = 1.1   # 10% less efficient
        else:  # Shorter routes = "direct city street style"
            if req.traffic_level > 0.7:
                # In HIGH traffic: short routes get stuck in congestion
                route_efficiency_factor = 1.4   # 40% LESS efficient (stuck in traffic)
            else:
                # In LOW traffic: short routes are optimal
                route_efficiency_factor = 0.9   # 10% more efficient
        
        # Apply route efficiency to CO2 score
        adjusted_score = co2_score * route_efficiency_factor
        
        # Vehicle type differences
        if req.vehicle_type == "EV":
            # EVs benefit more from avoiding stop-and-go traffic
            if distance > 15 and req.traffic_level > 0.7:
                adjusted_score *= 0.85  # EVs get extra benefit from highway routes in traffic
        else:
            # ICE vehicles suffer more in stop-and-go traffic
            if distance < 15 and req.traffic_level > 0.7:
                adjusted_score *= 1.15  # ICE gets extra penalty for short routes in high traffic
        
        if adjusted_score < best_score:
            best_score = adjusted_score
            best_route = route
            best_distance = distance
            best_co2 = co2_score
    
    return {
        "best_route": best_route, 
        "predicted_co2": round(best_co2, 2),  # Return actual CO2, not adjusted score
        "total_distance": round(best_distance, 2)
    }
