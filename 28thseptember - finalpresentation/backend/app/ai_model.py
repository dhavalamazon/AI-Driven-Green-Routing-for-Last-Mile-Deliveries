import torch
import torch.nn as nn
from utils import haversine_distance

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
