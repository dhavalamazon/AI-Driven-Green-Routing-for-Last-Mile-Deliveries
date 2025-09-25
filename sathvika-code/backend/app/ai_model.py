import torch
import torch.nn as nn
from utils import haversine_distance

class RouteScorer(nn.Module):
    def __init__(self):
        super(RouteScorer, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(5, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        return self.net(x)

def route_features(route, vehicle_type, traffic_level=0.5, avg_speed=30):
    total_distance = sum([haversine_distance(route[i], route[i+1]) for i in range(len(route)-1)])
    num_stops = len(route)
    vehicle_flag = 1 if vehicle_type == "EV" else 0
    return [total_distance, num_stops, traffic_level, vehicle_flag, avg_speed]
