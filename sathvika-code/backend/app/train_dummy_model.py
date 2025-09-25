import torch
from ai_model import RouteScorer, route_features
import random

# Generate synthetic dataset
N = 5000
stops_data = [
    [{'lat': random.uniform(37.74,37.79),'lon': random.uniform(-122.43,-122.40)} for _ in range(5)]
    for _ in range(N)
]
traffic_levels = [random.uniform(0,1) for _ in range(N)]
vehicle_types = [random.choice([0,1]) for _ in range(N)]  # 0=ICE,1=EV

# Create labels using simple formula
labels = []
for i in range(N):
    dist = sum([((stops_data[i][j]['lat']-stops_data[i][j+1]['lat'])**2 + 
                 (stops_data[i][j]['lon']-stops_data[i][j+1]['lon'])**2)**0.5 
                 for j in range(len(stops_data[i])-1)])
    vehicle_factor = 1.5 if vehicle_types[i]==0 else 1.0
    labels.append(dist * (1 + traffic_levels[i]*0.5) * vehicle_factor)

X = []
for i in range(N):
    route = stops_data[i]
    X.append([sum([((route[j]['lat']-route[j+1]['lat'])**2 + (route[j]['lon']-route[j+1]['lon'])**2)**0.5 for j in range(len(route)-1)]),
              len(route),
              traffic_levels[i],
              vehicle_types[i],
              30  # avg_speed placeholder
             ])
    
X_train = torch.tensor(X, dtype=torch.float32)
y_train = torch.tensor(labels, dtype=torch.float32).view(-1,1)

# Train model
model = RouteScorer()
criterion = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(50):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    if epoch % 10 == 0:
        print(f"Epoch {epoch} Loss: {loss.item()}")

torch.save(model.state_dict(), "route_scorer.pt")
print("Model saved as route_scorer.pt")
