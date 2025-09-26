import pandas as pd
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from ai_model import RouteScorer
import joblib

def prepare_data():
    """Load and prepare the vehicle emission dataset"""
    print("Loading vehicle emission dataset...")
    
    # Load the dataset
    df = pd.read_csv('../../vehicle_emission_dataset.csv')
    print(f"Loaded {len(df)} records")
    
    # Create mappings for categorical variables
    vehicle_map = {'Car': 0, 'Truck': 1, 'Bus': 2, 'Motorcycle': 3}
    fuel_map = {'Electric': 0, 'Hybrid': 1, 'Petrol': 2, 'Diesel': 3}
    road_map = {'City': 0, 'Highway': 1, 'Rural': 2}
    traffic_map = {'Free flow': 0, 'Moderate': 1, 'Heavy': 2}
    
    # Map categorical variables to numeric
    df['Vehicle_Encoded'] = df['Vehicle Type'].map(vehicle_map)
    df['Fuel_Encoded'] = df['Fuel Type'].map(fuel_map)
    df['Road_Encoded'] = df['Road Type'].map(road_map)
    df['Traffic_Encoded'] = df['Traffic Conditions'].map(traffic_map)
    
    # Select features that match our routing context
    features = [
        'Speed',           # Average speed (km/h)
        'Engine Size',     # Engine size (L)
        'Traffic_Encoded', # Traffic conditions (0-2)
        'Vehicle_Encoded', # Vehicle type (0-3)
        'Fuel_Encoded'     # Fuel type (0-3)
    ]
    
    X = df[features].values
    y = df['CO2 Emissions'].values
    
    # Handle missing values
    X = np.nan_to_num(X)
    y = np.nan_to_num(y)
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    return X, y

def train_model():
    """Train the neural network on emission data"""
    print("=== Training AI Model on Real Emission Data ===")
    
    # Prepare data
    X, y = prepare_data()
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features for better training
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train_scaled)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    X_test_tensor = torch.FloatTensor(X_test_scaled)
    y_test_tensor = torch.FloatTensor(y_test).unsqueeze(1)
    
    # Initialize model
    model = RouteScorer()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print("Training neural network...")
    
    # Training loop
    epochs = 1000
    best_test_loss = float('inf')
    
    for epoch in range(epochs):
        # Training
        model.train()
        optimizer.zero_grad()
        
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        
        # Validation every 100 epochs
        if (epoch + 1) % 100 == 0:
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test_tensor)
                test_loss = criterion(test_outputs, y_test_tensor)
                
                if test_loss < best_test_loss:
                    best_test_loss = test_loss
                
                print(f'Epoch [{epoch+1}/{epochs}] - Train Loss: {loss.item():.4f}, Test Loss: {test_loss.item():.4f}')
    
    # Save trained model and scaler
    torch.save(model.state_dict(), 'route_scorer.pt')
    joblib.dump(scaler, 'feature_scaler.pkl')
    
    print(f"✅ Model training completed!")
    print(f"✅ Best test loss: {best_test_loss:.4f}")
    print(f"✅ Model saved as 'route_scorer.pt'")
    print(f"✅ Scaler saved as 'feature_scaler.pkl'")
    
    # Test with sample predictions
    test_predictions(model, scaler)

def test_predictions(model, scaler):
    """Test the model with sample vehicle scenarios"""
    print("\n=== Testing Model Predictions ===")
    
    model.eval()
    
    test_cases = [
        # [Speed, Engine_Size, Traffic(0-2), Vehicle(0-3), Fuel(0-3)]
        [60.0, 2.0, 0, 0, 0],  # Car, Electric, Free flow, 60km/h
        [30.0, 2.0, 2, 0, 2],  # Car, Petrol, Heavy traffic, 30km/h
        [80.0, 4.0, 1, 1, 3],  # Truck, Diesel, Moderate traffic, 80km/h
        [25.0, 6.0, 2, 2, 0],  # Bus, Electric, Heavy traffic, 25km/h
    ]
    
    labels = [
        "Electric Car (Free Flow)",
        "Petrol Car (Heavy Traffic)",
        "Diesel Truck (Moderate Traffic)",
        "Electric Bus (Heavy Traffic)"
    ]
    
    with torch.no_grad():
        for i, (case, label) in enumerate(zip(test_cases, labels)):
            # Scale input
            case_scaled = scaler.transform([case])
            case_tensor = torch.FloatTensor(case_scaled)
            
            # Predict
            prediction = model(case_tensor).item()
            
            print(f"{label}: {prediction:.2f} kg CO2")

if __name__ == "__main__":
    train_model()