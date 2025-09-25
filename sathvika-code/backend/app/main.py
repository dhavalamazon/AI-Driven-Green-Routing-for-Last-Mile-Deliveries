from fastapi import FastAPI
from pydantic import BaseModel
from route_gen import nearest_neighbor_route, random_routes
from ai_model import RouteScorer, route_features
import torch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Allow requests from your frontend
origins = [
    "http://localhost:5173",  # Vite dev server
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
    candidates = random_routes(req.stops, n_routes=5) + [nearest_neighbor_route(req.stops)]
    best_route = None
    best_score = float("inf")
    
    for r in candidates:
        feats = torch.tensor(route_features(r, req.vehicle_type, req.traffic_level), dtype=torch.float32)
        score = model(feats).item()
        if score < best_score:
            best_score = score
            best_route = r
    
    return {"best_route": best_route, "predicted_co2": best_score}
