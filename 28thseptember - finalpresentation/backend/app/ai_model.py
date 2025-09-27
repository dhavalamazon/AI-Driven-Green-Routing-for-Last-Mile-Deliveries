import torch
import torch.nn as nn
from utils import haversine_distance
from traffic_service import get_route_traffic_analysis
import joblib
import numpy as np

class RouteScorer(nn.Module):
    def __init__(self, input_size=8):
        super(RouteScorer, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, x):
        return self.net(x)

def route_features(route, vehicle_type, traffic_level=0.5):
    """Extract features for CO2 prediction using real traffic analysis"""
    
    # Get realistic traffic analysis based on coordinates
    traffic_analysis = get_route_traffic_analysis(route)
    
    # Use calculated speed from traffic analysis
    avg_speed = traffic_analysis['estimated_speed']
    actual_traffic_level = traffic_analysis['traffic_level']
    
    # Vehicle and fuel type mappings (from training data)
    if vehicle_type == "EV":
        vehicle_encoded = 0  # Car
        fuel_encoded = 0     # Electric
        engine_size = 2.0    # Typical EV
    else:  # ICE
        vehicle_encoded = 0  # Car
        fuel_encoded = 2     # Petrol
        engine_size = 2.5    # Typical ICE engine
    
    # Convert traffic level to categorical (0-2 scale) using real analysis
    if actual_traffic_level < 0.33:
        traffic_encoded = 0  # Free flow
    elif actual_traffic_level < 0.67:
        traffic_encoded = 1  # Moderate
    else:
        traffic_encoded = 2  # Heavy
    
    # Features: [Speed, Engine Size, Traffic, Vehicle Type, Fuel Type]
    features = [avg_speed, engine_size, traffic_encoded, vehicle_encoded, fuel_encoded]
    
    return features, traffic_analysis

def load_model_with_scaler():
    """Load trained model and scaler"""
    model = RouteScorer()
    try:
        model.load_state_dict(torch.load("route_scorer.pt", weights_only=True))
        scaler = joblib.load('feature_scaler.pkl')
        model.eval()
        print("✅ Loaded trained model and scaler")
        return model, scaler
    except FileNotFoundError:
        print("⚠️  Trained model not found. Please run: python train_model.py")
        return model, None
